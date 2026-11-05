from __future__ import annotations

import json
import os
import secrets
from pathlib import Path
from urllib.parse import urlparse

import httpx
import typer

from research_kb.auth import token_digest
from research_kb.config import Settings
from research_kb.ingest import bundle, import_bundle, refresh, writer_lock
from research_kb.library import Library

app = typer.Typer(
    no_args_is_help=True, help="Shared research library. Agents retrieve; operator CLI imports and indexes."
)
token_app = typer.Typer(no_args_is_help=True)
app.add_typer(token_app, name="token")


def emit(value):
    typer.echo(json.dumps(value, indent=2, default=str))


def library(ctx):
    return Library(ctx.obj)


@app.callback()
def main(ctx: typer.Context, home: Path | None = None, config: Path | None = None):
    kwargs = {}
    if home is not None:
        kwargs["home"] = home
    if config is not None:
        kwargs["config"] = config
    ctx.obj = Settings(**kwargs)


@app.command("refresh")
def refresh_command(ctx: typer.Context, build_index: bool = False):
    lib = library(ctx)
    result = refresh(lib)
    emit(result)
    if build_index and lib.settings.qdrant_url:
        with writer_lock(lib.settings.home):
            emit(lib.index())
    if result["failed"] or result["missing_roots"]:
        raise typer.Exit(1)


@app.command("index")
def index_command(ctx: typer.Context):
    lib = library(ctx)
    with writer_lock(lib.settings.home):
        emit(lib.index())


@app.command()
def status(ctx: typer.Context):
    emit(library(ctx).status())


@app.command()
def recent(ctx: typer.Context, limit: int = 10, repo: str | None = None):
    """Newest ingested sources, useful for seeing findings that just landed."""
    emit(library(ctx).recent(limit, repo))


@app.command()
def search(
    ctx: typer.Context,
    query: str,
    repo: str | None = None,
    source_type: str | None = None,
    top_k: int = 6,
    mode: str = "lexical",
):
    emit(library(ctx).search(query, top_k, repo, source_type, mode))


@app.command()
def brief(
    ctx: typer.Context,
    query: str,
    repo: str | None = None,
    source_type: str | None = None,
    top_k: int = 6,
    mode: str = "lexical",
    max_chars: int = 14000,
):
    """Print a citation-bearing context pack for a batch or non-MCP model.

    Delphi and shell wrappers use this; it is the same retriever the MCP tools
    serve, not a second search path.
    """
    typer.echo(library(ctx).brief(query, top_k, repo, source_type, mode, max_chars))


@app.command()
def theorems(ctx: typer.Context, query: str, repo: str | None = None, environment: str | None = None):
    emit(library(ctx).catalog.search_theorems(query, repo=repo, environment=environment))


@app.command("bundle")
def bundle_command(ctx: typer.Context, output: Path):
    emit(bundle(ctx.obj, output))


@app.command("import-bundle")
def import_command(ctx: typer.Context, filename: Path, build_index: bool = False):
    lib = library(ctx)
    emit(import_bundle(lib, filename))
    if build_index and lib.settings.qdrant_url:
        with writer_lock(lib.settings.home):
            emit(lib.index())


@app.command("sync-s3")
def sync_s3(ctx: typer.Context, bucket: str, prefix: str = "inbox/", build_index: bool = False):
    """Operator-only import from a private S3 prefix; uses the host's IAM role."""
    import boto3

    lib = library(ctx)
    client = boto3.client("s3")
    inbox = lib.settings.home / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    for page in client.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            if not obj["Key"].endswith(".tar.gz"):
                continue
            from research_kb.catalog import digest

            key = digest(obj["Key"] + obj["ETag"])
            marker = inbox / (key + ".done")
            if marker.exists():
                continue
            if obj["Size"] > lib.settings.max_bundle_bytes:
                raise ValueError("S3 bundle exceeds configured limit")
            target = inbox / (key + ".tar.gz")
            client.download_file(bucket, obj["Key"], str(target))
            emit(import_bundle(lib, target))
            marker.write_text(obj["Key"])
    if build_index and lib.settings.qdrant_url:
        with writer_lock(lib.settings.home):
            emit(lib.index())


@app.command("export-lean")
def export_lean(
    ctx: typer.Context, project: Path, modules: list[str], output: Path = typer.Option(..., "--output")
):
    """Read a compiled Lean environment. Does not label source scans as verified."""
    from research_kb.lean import environment_info, export_environment
    from research_kb.catalog import digest

    project = project.resolve()
    env = environment_info(project / "Placeholder.lean", project)
    rows = export_environment(project, modules)
    sources = {}
    for file in project.rglob("*.lean"):
        if ".lake" not in file.parts:
            sources[file.relative_to(project).as_posix()] = digest(file.read_bytes())
    result = {
        "schema": 1,
        "environment": env["digest"],
        "pins": env["pins"],
        "sources": sources,
        "declarations": rows,
    }
    output.write_text(json.dumps(result, indent=2))
    emit({"output": str(output), "declarations": len(rows), "environment": env["digest"]})


@app.command("backup")
def backup(ctx: typer.Context, output: Path):
    library(ctx).catalog.backup(output)
    emit({"catalog_backup": str(output), "originals": "also back up objects/ and the active index metadata"})


@app.command("audit-lean")
def audit_lean(ctx: typer.Context, project: Path, modules: list[str]):
    """Compile and audit registered Lean projects; unavailable through MCP/HTTP."""
    from research_kb.lean import audit_project

    result = audit_project(library(ctx), project, modules)
    emit(result)
    if result["failed_axiom_checks"]:
        raise typer.Exit(1)


@app.command("mcp")
def mcp(ctx: typer.Context):
    from research_kb.server import build_mcp

    build_mcp(library(ctx)).run(transport="stdio", show_banner=False)


@app.command("update-sources")
def update_sources(ctx: typer.Context):
    """Fast-forward each registered git checkout; never merges or overwrites local work."""
    from research_kb.ingest import update_sources as update

    results = update(library(ctx))
    emit(results)
    if any(item.get("ok") is False for item in results):
        raise typer.Exit(1)


@app.command("watch")
def watch_command(
    ctx: typer.Context,
    interval: float = typer.Option(60.0, "--interval", help="Seconds between source checks."),
    once: bool = typer.Option(False, "--once", help="Check and refresh once, then exit."),
    pull: bool = typer.Option(False, "--pull", help="Fast-forward registered git checkouts each cycle."),
    max_cycles: int | None = typer.Option(None, "--max-cycles", hidden=True),
):
    """Refresh the catalog when a registered source changes.

    Run this under launchd/systemd/cron when agents should see new findings
    without an operator remembering to run ``refresh``.
    """
    from research_kb.watch import watch

    watch(library(ctx), interval=interval, once=once, max_cycles=max_cycles, pull=pull)


@app.command("install-client")
def install_client_command(
    ctx: typer.Context,
    client: list[str] = typer.Option(..., "--client", "-c", help="claude | codex | opencode | delphi | all"),
    transport: str = typer.Option("stdio", help="stdio | http"),
    url: str | None = typer.Option(
        None, "--url", help="Base URL for HTTP transport, e.g. https://kb.example.com"
    ),
    command: str | None = typer.Option(None, "--command", help="Path to the research-kb executable."),
):
    """Register this KB in local agent clients. Idempotent, with backups."""
    from research_kb import clients as client_installer

    if transport not in {"stdio", "http"}:
        raise typer.BadParameter("transport must be stdio or http")
    names = list(client_installer.CLIENT_NAMES) if "all" in client else client
    names = [part for name in names for part in name.split(",") if part]
    unknown = sorted(set(names) - set(client_installer.CLIENT_NAMES))
    if unknown:
        raise typer.BadParameter(f"unknown clients: {', '.join(unknown)}")
    executable = command or client_installer.default_command()
    kwargs = {
        "transport": transport,
        "command": executable,
        "state_home": ctx.obj.home.expanduser().resolve(),
        "config": ctx.obj.config.expanduser().resolve(),
        "url": url,
    }
    for name in names:
        emit(client_installer.install(name, **kwargs))


@app.command("serve")
def serve(ctx: typer.Context, host: str | None = None, port: int | None = None):
    import uvicorn
    from research_kb.server import http_app

    settings = ctx.obj
    uvicorn.run(
        http_app(library(ctx)), host=host or settings.host, port=port or settings.port, access_log=False
    )


def remote_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" and not (
        parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    ):
        raise ValueError("remote credentials require HTTPS (HTTP is allowed only for loopback testing)")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("remote URL must not contain credentials, query parameters or fragments")
    return url.rstrip("/")


@app.command("remote-search")
def remote_search(url: str, query: str, repo: str | None = None):
    """Fallback for cloud runtimes without custom MCP; token comes from the environment."""
    endpoint = remote_url(url)
    token = os.environ.get("RESEARCH_KB_TOKEN")
    if not token:
        raise ValueError("set RESEARCH_KB_TOKEN in the cloud session's secret configuration")
    params = {"q": query}
    if repo:
        params["repo"] = repo
    with httpx.Client(timeout=30, follow_redirects=False) as client:
        result = client.get(
            endpoint + "/v1/search", params=params, headers={"Authorization": "Bearer " + token}
        )
        result.raise_for_status()
        emit(result.json())


@app.command("connect")
def connect(url: str):
    """Bridge stdio-only clients to the authenticated remote MCP endpoint."""
    from fastmcp import FastMCP, Client
    from fastmcp.client.transports import StreamableHttpTransport

    endpoint = remote_url(url)
    token = os.environ.get("RESEARCH_KB_TOKEN")
    if not token:
        raise ValueError("set RESEARCH_KB_TOKEN")
    transport = StreamableHttpTransport(endpoint + "/mcp", headers={"Authorization": "Bearer " + token})
    FastMCP.as_proxy(Client(transport), name="Research KB Remote").run(transport="stdio", show_banner=False)


@token_app.command("create")
def create_token(
    ctx: typer.Context,
    client: str = typer.Option(..., "--client"),
    output: Path = typer.Option(..., "--output"),
):
    """Write a new client secret to a mode-0600 file; store only its hash on the server."""
    if not client or len(client) > 80 or not all(c.isalnum() or c in "-_" for c in client):
        raise ValueError("client must be a short identifier")
    settings = ctx.obj
    auth_file = settings.auth_file or settings.home / "auth.json"
    secret = secrets.token_urlsafe(32)
    output.parent.mkdir(parents=True, exist_ok=True)
    with writer_lock(settings.home):
        registry = (
            json.loads(auth_file.read_text()) if auth_file.exists() else {"schema_version": 1, "tokens": {}}
        )
        registry["tokens"][client] = token_digest(secret)
        # Refuse to overwrite a caller's file, including an existing secret.
        fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as handle:
            handle.write(secret + "\n")
        auth_file.parent.mkdir(parents=True, exist_ok=True)
        temp = auth_file.with_suffix(".tmp")
        fd = os.open(temp, os.O_CREAT | os.O_TRUNC | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as handle:
            json.dump(registry, handle, indent=2)
        os.chmod(temp, 0o600)
        os.replace(temp, auth_file)
    emit({"client": client, "auth_file": str(auth_file), "token_file": str(output)})


@token_app.command("revoke")
def revoke_token(ctx: typer.Context, client: str = typer.Option(..., "--client")):
    auth_file = ctx.obj.auth_file or ctx.obj.home / "auth.json"
    with writer_lock(ctx.obj.home):
        raw = json.loads(auth_file.read_text())
        raw["tokens"].pop(client, None)
        temp = auth_file.with_suffix(".tmp")
        temp.write_text(json.dumps(raw, indent=2))
        temp.chmod(0o600)
        os.replace(temp, auth_file)
    emit({"revoked": client})
