import json
import stat
import tomllib

import pytest

from research_kb import clients


@pytest.fixture
def isolated_clients(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_KB_CLIENT_HOME", str(tmp_path / "home"))
    monkeypatch.delenv("CODEX_HOME", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "home" / ".config"))
    return tmp_path / "home"


def install(client, **overrides):
    values = {
        "transport": "stdio",
        "command": "/opt/kb/bin/research-kb",
        "state_home": overrides.pop("state_home", clients.client_home() / ".local/share/research-kb"),
        "config": overrides.pop("config", clients.client_home() / ".config/research-kb/sources.toml"),
        "url": None,
    }
    values.update(overrides)
    return clients.install(client, **values)


def test_claude_preserves_other_servers_and_is_idempotent(isolated_clients):
    path = clients.client_path("claude")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"mcpServers": {"other": {"command": "other"}}, "theme": "dark"}))

    first = install("claude")
    second = install("claude")

    assert first["backup"] and second["backup"] == first["backup"]
    data = json.loads(path.read_text())
    assert data["theme"] == "dark"
    assert data["mcpServers"]["other"] == {"command": "other"}
    entry = data["mcpServers"]["research-kb"]
    assert entry["command"] == "/opt/kb/bin/research-kb"
    assert entry["args"] == ["mcp"]
    assert entry["env"]["RESEARCH_KB_HOME"].endswith(".local/share/research-kb")


def test_claude_http_uses_runtime_token(isolated_clients):
    install("claude", transport="http", url="https://kb.example.com/")
    data = json.loads(clients.client_path("claude").read_text())
    entry = data["mcpServers"]["research-kb"]
    assert entry["type"] == "http"
    assert entry["url"] == "https://kb.example.com/mcp"
    assert entry["headers"]["Authorization"] == "Bearer ${RESEARCH_KB_TOKEN}"


def test_codex_replaces_only_its_own_tables(isolated_clients):
    path = clients.client_path("codex")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        'model = "gpt-5"\n\n'
        "[mcp_servers.other]\n"
        'command = "other"\n\n'
        "[mcp_servers.research-kb]\n"
        'command = "/stale"\n'
        'args = ["mcp"]\n\n'
        "[mcp_servers.research-kb.env]\n"
        'RESEARCH_KB_HOME = "/stale/home"\n\n'
        "[profiles.fast]\n"
        'model = "gpt-5-mini"\n'
    )

    install("codex")
    install("codex")

    parsed = tomllib.loads(path.read_text())
    assert parsed["model"] == "gpt-5"
    assert parsed["profiles"]["fast"]["model"] == "gpt-5-mini"
    assert parsed["mcp_servers"]["other"]["command"] == "other"
    entry = parsed["mcp_servers"]["research-kb"]
    assert entry["command"] == "/opt/kb/bin/research-kb"
    assert entry["args"] == ["mcp"]
    assert entry["env"]["RESEARCH_KB_HOME"].endswith(".local/share/research-kb")


def test_codex_http_uses_bearer_env(isolated_clients):
    install("codex", transport="http", url="https://kb.example.com")
    parsed = tomllib.loads(clients.client_path("codex").read_text())
    entry = parsed["mcp_servers"]["research-kb"]
    assert entry["url"] == "https://kb.example.com/mcp"
    assert entry["bearer_token_env_var"] == "RESEARCH_KB_TOKEN"


def test_codex_handles_quoted_headers_and_preserves_commented_tables(isolated_clients):
    path = clients.client_path("codex")
    path.parent.mkdir(parents=True, exist_ok=True)
    original = (
        'model = "custom"\n'
        '[mcp_servers."research-kb"] # existing server\ncommand = "/old"\n'
        '[mcp_servers."research-kb".env] # existing environment\nOLD = "old"\n'
        '[mcp_servers.other] # preserve this server\ncommand = "keep"\n'
        '[profiles.fast] # preserve this profile\nmodel = "fast"\n'
    )
    path.write_text(original)
    install("codex")
    first = path.read_text()
    install("codex")
    assert path.read_text() == first
    parsed = tomllib.loads(first)
    assert parsed["mcp_servers"]["other"] == {"command": "keep"}
    assert parsed["profiles"]["fast"] == {"model": "fast"}
    assert parsed["model"] == "custom"
    assert parsed["mcp_servers"]["research-kb"]["command"] == "/opt/kb/bin/research-kb"
    assert path.with_name(path.name + ".bak-research-kb").read_text() == original


def test_codex_refuses_invalid_toml_without_writing(isolated_clients):
    path = clients.client_path("codex")
    path.parent.mkdir(parents=True, exist_ok=True)
    original = 'model = "unterminated\n'
    path.write_text(original)
    with pytest.raises(clients.ClientConfigError):
        install("codex")
    assert path.read_text() == original


def test_codex_refuses_to_change_table_like_text_in_multiline_strings(isolated_clients):
    path = clients.client_path("codex")
    path.parent.mkdir(parents=True, exist_ok=True)
    original = 'banner = """\n[mcp_servers.research-kb]\nkeep me\n[other]\nalso keep me\n"""\n'
    path.write_text(original)
    with pytest.raises(clients.ClientConfigError):
        install("codex")
    assert path.read_text() == original


def test_opencode_accepts_jsonc_and_preserves_comments_elsewhere(isolated_clients):
    path = clients.client_path("opencode")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '{\n  // existing note\n  "theme": "dark",\n'
        '  "mcp": {"other": {"type": "local", "command": ["other"]}}\n}\n'
    )

    install("opencode")

    data = json.loads(path.read_text())
    assert data["theme"] == "dark"
    assert data["mcp"]["other"]["command"] == ["other"]
    entry = data["mcp"]["research-kb"]
    assert entry["type"] == "local"
    assert entry["command"] == ["/opt/kb/bin/research-kb", "mcp"]
    assert entry["environment"]["RESEARCH_KB_HOME"].endswith(".local/share/research-kb")


def test_delphi_wrappers_are_executable_and_use_the_same_command(isolated_clients):
    result = install("delphi")
    brief, ask = (clients.client_path("delphi") / name for name in ("delphi-kb", "delphi-kb-ask"))
    assert result["paths"] == [str(brief), str(ask)]
    for path in (brief, ask):
        assert path.is_file()
        assert stat.S_IMODE(path.stat().st_mode) & 0o111
        assert "/opt/kb/bin/research-kb" in path.read_text()
    assert 'exec "$RESEARCH_KB" brief "$query"' in brief.read_text()
    assert "delphi ask -prompt" in ask.read_text()


def test_unknown_client_refuses(isolated_clients):
    with pytest.raises(clients.ClientConfigError):
        install("cursor")


def test_client_home_override_ignores_codex_and_xdg(isolated_clients, monkeypatch):
    monkeypatch.setenv("CODEX_HOME", "/tmp/real-codex")
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/real-xdg")
    assert clients.client_path("codex") == isolated_clients / ".codex" / "config.toml"
    assert clients.client_path("opencode") == isolated_clients / ".config" / "opencode" / "opencode.json"


def test_opencode_prefers_the_existing_jsonc_file(isolated_clients):
    path = isolated_clients / ".config" / "opencode" / "opencode.jsonc"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"theme": "dark"}\n')
    assert clients.client_path("opencode") == path
    install("opencode")
    assert json.loads(path.read_text())["mcp"]["research-kb"]["type"] == "local"
