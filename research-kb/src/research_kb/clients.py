"""Install the Research KB MCP server into local agent clients.

The server itself is one stdio/HTTP MCP process; this module only writes the
small client-specific config block that tells an agent how to start or reach
it. Every writer is idempotent, backs the original file up before the first
change, and preserves unrelated entries.

Delphi has no MCP client. It gets a pair of shell wrappers instead: the first
prints a retrieval-augmented context pack, the second sends that pack to
``delphi ask``. That keeps Delphi on the same corpus and the same citations
without inventing a private retrieval path.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any

CLIENT_NAMES = ("claude", "codex", "opencode", "delphi")
SERVER_NAME = "research-kb"


class ClientConfigError(RuntimeError):
    """Raised when a client config cannot be parsed or updated safely."""


# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------


def client_home() -> Path:
    """Root used to locate client configs.

    ``RESEARCH_KB_CLIENT_HOME`` exists so tests and dry runs never touch a real
    user's agent configuration.
    """
    override = os.environ.get("RESEARCH_KB_CLIENT_HOME")
    return Path(override).expanduser() if override else Path.home()


def client_path(client: str) -> Path:
    """Resolve a client's config path.

    ``RESEARCH_KB_CLIENT_HOME`` pins *all* paths under one root, including the
    ones that normally follow ``CODEX_HOME`` or ``XDG_CONFIG_HOME``. That is
    what lets a setup dry run and the tests avoid touching a real agent config.
    """
    override = os.environ.get("RESEARCH_KB_CLIENT_HOME")
    home = Path(override).expanduser() if override else Path.home()
    if client == "claude":
        return home / ".claude.json"
    if client == "codex":
        if override:
            return home / ".codex" / "config.toml"
        codex_home = os.environ.get("CODEX_HOME")
        return (Path(codex_home).expanduser() if codex_home else home / ".codex") / "config.toml"
    if client == "opencode":
        if override:
            root = home / ".config" / "opencode"
        else:
            root = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config")).expanduser() / "opencode"
        # OpenCode accepts both. Write the file that already exists so we do
        # not silently shadow a real config with a new, minimal one.
        if (root / "opencode.json").exists():
            return root / "opencode.json"
        if (root / "opencode.jsonc").exists():
            return root / "opencode.jsonc"
        return root / "opencode.json"
    if client == "delphi":
        # A directory, not a file: two wrappers are written here.
        return home / ".local" / "bin"
    raise ClientConfigError(f"unknown client {client!r}; choose from {', '.join(CLIENT_NAMES)}")


# --------------------------------------------------------------------------
# Atomic writes and backups
# --------------------------------------------------------------------------


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    backup = path.with_name(path.name + ".bak-research-kb")
    if not backup.exists():
        shutil.copy2(path, backup)
    return backup


def _atomic_write(path: Path, text: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=str(path.parent), prefix="." + path.name + ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        if mode is not None:
            os.chmod(name, mode)
        elif path.exists():
            os.chmod(name, path.stat().st_mode & 0o777)
        os.replace(name, path)
    except BaseException:
        try:
            os.unlink(name)
        except OSError:
            pass
        raise


# --------------------------------------------------------------------------
# JSON / JSONC
# --------------------------------------------------------------------------


def strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments without touching string contents.

    OpenCode accepts JSONC. We read it, but write plain JSON back: comments in a
    machine-managed block are not worth a second parser dependency, and the
    backup keeps the original.
    """
    out: list[str] = []
    i = 0
    in_string = False
    escaped = False
    while i < len(text):
        char = text[i]
        if in_string:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
            continue
        if char == '"':
            in_string = True
            out.append(char)
            i += 1
            continue
        if char == "/" and i + 1 < len(text):
            if text[i + 1] == "/":
                while i < len(text) and text[i] != "\n":
                    i += 1
                continue
            if text[i + 1] == "*":
                end = text.find("*/", i + 2)
                if end == -1:
                    raise ClientConfigError("unterminated block comment in JSONC config")
                i = end + 2
                continue
        out.append(char)
        i += 1
    return "".join(out)


def load_json_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(strip_jsonc(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, ClientConfigError) as exc:
        raise ClientConfigError(f"cannot parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ClientConfigError(f"{path} must contain a JSON object")
    return value


def _json_entry(transport: str, command: str, state_home: Path, config: Path, url: str | None) -> dict:
    if transport == "http":
        if not url:
            raise ClientConfigError("HTTP transport requires a URL")
        return {
            "type": "http",
            "url": url.rstrip("/") + "/mcp",
            "headers": {"Authorization": "Bearer ${RESEARCH_KB_TOKEN}"},
        }
    return {
        "type": "stdio",
        "command": command,
        "args": ["mcp"],
        "env": {
            "RESEARCH_KB_HOME": str(state_home),
            "RESEARCH_KB_CONFIG": str(config),
        },
    }


def install_claude(*, transport: str, command: str, state_home: Path, config: Path, url: str | None) -> dict:
    path = client_path("claude")
    data = load_json_config(path)
    servers = data.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise ClientConfigError(f"{path}: mcpServers must be an object")
    servers[SERVER_NAME] = _json_entry(transport, command, state_home, config, url)
    backup = _backup(path)
    _atomic_write(path, json.dumps(data, indent=2) + "\n")
    return {"client": "claude", "path": str(path), "backup": str(backup) if backup else None}


# --------------------------------------------------------------------------
# Codex (TOML)
# --------------------------------------------------------------------------


def _toml_string(value: str) -> str:
    # JSON string escaping is a subset of TOML basic-string escaping.
    return json.dumps(value)


def _drop_server_block(text: str, name: str) -> str:
    """Remove ``[mcp_servers.NAME]`` and all of its child tables."""
    lines = text.splitlines(keepends=True)
    kept: list[str] = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("["):
            try:
                header = tomllib.loads(stripped + "\n__header_probe__ = true\n")
            except tomllib.TOMLDecodeError:
                pass
            else:
                servers = header.get("mcp_servers")
                skipping = isinstance(servers, dict) and name in servers
        if not skipping:
            kept.append(line)
    # Collapse the blank lines the removal can leave behind.
    result = "".join(kept)
    while "\n\n\n" in result:
        result = result.replace("\n\n\n", "\n\n")
    return result.rstrip() + "\n" if result.strip() else ""


def install_codex(*, transport: str, command: str, state_home: Path, config: Path, url: str | None) -> dict:
    path = client_path("codex")
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    try:
        original = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ClientConfigError(f"cannot parse {path}: {exc}") from exc
    text = _drop_server_block(text, SERVER_NAME)
    if transport == "http":
        if not url:
            raise ClientConfigError("HTTP transport requires a URL")
        block = (
            f"[mcp_servers.{SERVER_NAME}]\n"
            f"url = {_toml_string(url.rstrip('/') + '/mcp')}\n"
            f'bearer_token_env_var = "RESEARCH_KB_TOKEN"\n'
        )
    else:
        block = (
            f"[mcp_servers.{SERVER_NAME}]\n"
            f"command = {_toml_string(command)}\n"
            f'args = ["mcp"]\n'
            f"\n[mcp_servers.{SERVER_NAME}.env]\n"
            f"RESEARCH_KB_HOME = {_toml_string(str(state_home))}\n"
            f"RESEARCH_KB_CONFIG = {_toml_string(str(config))}\n"
        )
    candidate = (text + "\n" if text.strip() else "") + block
    try:
        updated = tomllib.loads(candidate)
    except tomllib.TOMLDecodeError as exc:
        raise ClientConfigError(f"cannot safely update {path}: {exc}") from exc

    def unrelated(data):
        result = dict(data)
        servers = result.pop("mcp_servers", {})
        if not isinstance(servers, dict):
            raise ClientConfigError(f"{path}: mcp_servers must be a table")
        retained = {key: value for key, value in servers.items() if key != SERVER_NAME}
        if retained:
            result["mcp_servers"] = retained
        return result

    # Table-looking lines inside multiline strings must never cause unrelated
    # user settings to be removed by the text-preserving block replacement.
    if unrelated(original) != unrelated(updated):
        raise ClientConfigError(f"cannot safely preserve unrelated settings in {path}")
    backup = _backup(path)
    _atomic_write(path, candidate)
    return {"client": "codex", "path": str(path), "backup": str(backup) if backup else None}


# --------------------------------------------------------------------------
# OpenCode (JSON/JSONC)
# --------------------------------------------------------------------------


def install_opencode(
    *, transport: str, command: str, state_home: Path, config: Path, url: str | None
) -> dict:
    path = client_path("opencode")
    data = load_json_config(path)
    mcp = data.setdefault("mcp", {})
    if not isinstance(mcp, dict):
        raise ClientConfigError(f"{path}: mcp must be an object")
    if transport == "http":
        if not url:
            raise ClientConfigError("HTTP transport requires a URL")
        mcp[SERVER_NAME] = {
            "type": "remote",
            "url": url.rstrip("/") + "/mcp",
            "enabled": True,
            "headers": {"Authorization": "Bearer ${RESEARCH_KB_TOKEN}"},
        }
    else:
        mcp[SERVER_NAME] = {
            "type": "local",
            "enabled": True,
            "command": [command, "mcp"],
            "environment": {
                "RESEARCH_KB_HOME": str(state_home),
                "RESEARCH_KB_CONFIG": str(config),
            },
        }
    backup = _backup(path)
    _atomic_write(path, json.dumps(data, indent=2) + "\n")
    return {"client": "opencode", "path": str(path), "backup": str(backup) if backup else None}


# --------------------------------------------------------------------------
# Delphi (no MCP: context-pack wrappers)
# --------------------------------------------------------------------------


def _wrapper(path: Path, content: str) -> None:
    _backup(path)
    _atomic_write(path, content, mode=0o755)


def install_delphi(*, command: str, state_home: Path, config: Path, **_ignored) -> dict:
    directory = client_path("delphi")
    brief = directory / "delphi-kb"
    ask = directory / "delphi-kb-ask"
    common = (
        "#!/bin/sh\n"
        "# Generated by research-kb install-client. Delphi has no MCP client;\n"
        "# this wrapper gives it the same corpus through the read-only CLI.\n"
        "set -eu\n"
        f"export RESEARCH_KB_HOME={shlex.quote(str(state_home))}\n"
        f"export RESEARCH_KB_CONFIG={shlex.quote(str(config))}\n"
        f"RESEARCH_KB={shlex.quote(command)}\n"
    )
    _wrapper(
        brief,
        common
        + 'query=${1:?usage: delphi-kb "research question" [--repo NAME]}\n'
        + "shift || true\n"
        + 'exec "$RESEARCH_KB" brief "$query" "$@"\n',
    )
    _wrapper(
        ask,
        common
        + 'query=${1:?usage: delphi-kb-ask "research question" [extra delphi ask flags]}\n'
        + "shift || true\n"
        + "if ! command -v delphi >/dev/null 2>&1; then\n"
        + '  echo "delphi is not on PATH; printing the context pack instead" >&2\n'
        + '  exec "$RESEARCH_KB" brief "$query"\n'
        + "fi\n"
        + 'prompt=$("$RESEARCH_KB" brief "$query")\n'
        + 'exec delphi ask -prompt "$prompt" "$@"\n',
    )
    return {"client": "delphi", "paths": [str(brief), str(ask)], "backup": None}


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def default_command() -> str:
    """The installed ``research-kb`` executable for the running environment."""
    sibling = Path(sys.executable).with_name("research-kb")
    if sibling.exists():
        return str(sibling)
    found = shutil.which("research-kb")
    if found:
        return found
    raise ClientConfigError("cannot find the research-kb executable; pass --command /path/to/research-kb")


def install(client: str, **kwargs) -> dict:
    if client == "claude":
        return install_claude(**kwargs)
    if client == "codex":
        return install_codex(**kwargs)
    if client == "opencode":
        return install_opencode(**kwargs)
    if client == "delphi":
        return install_delphi(**kwargs)
    raise ClientConfigError(f"unknown client {client!r}")
