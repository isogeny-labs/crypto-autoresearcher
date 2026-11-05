import json

from research_kb.config import Settings
from research_kb.ingest import refresh
from research_kb.library import Library
from research_kb.watch import watch


def test_brief_is_citation_bearing_markdown(populated):
    lib, _a, _b = populated
    text = lib.brief("Semaev decomposition", top_k=3)
    assert text.startswith("## Research KB context")
    assert "Query: Semaev decomposition" in text
    assert "`source:" in text
    assert "git_commit" in text or "path:" in text
    assert "relevance-ranked, not verified" in text


def test_status_reports_last_refresh(populated):
    lib, _a, _b = populated
    status = lib.status()
    assert status["ready"] is True
    assert status["last_refresh"].endswith("Z")


def test_watch_refreshes_an_uninitialized_catalog_once(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "note.md").write_text("# Note\n\nA finding worth indexing with enough prose to chunk.\n")
    config = tmp_path / "sources.toml"
    config.write_text(f'[[sources]]\nname="source"\nroot={json.dumps(str(source))}\n')
    library = Library(Settings(home=tmp_path / "state", config=config))

    events = watch(library, interval=5, once=True)

    assert len(events) == 1
    assert events[0]["changed"] is True
    assert events[0]["indexed"] == 1
    assert library.status()["ready"] is True


def test_watch_skips_after_seeding_the_signature(populated):
    lib, _a, _b = populated
    first = watch(lib, interval=5, once=True)
    assert first[0]["changed"] is True
    second = watch(lib, interval=5, once=True)
    assert second[0]["changed"] is False


def test_recent_lists_ingested_documents(populated):
    lib, _a, _b = populated
    result = lib.recent(limit=10)
    assert result["sources"]
    assert result["sources"][0]["source_id"].startswith(("source:", "paper:"))
    assert result["sources"][0]["added_at"].endswith("Z")
    assert result["revision"]


def test_recent_can_filter_by_repo(populated):
    lib, _a, _b = populated
    result = lib.recent(limit=10, repo="cryptanalysis")
    assert result["sources"]
    assert all("cryptanalysis" in row["repo"].split(",") for row in result["sources"])


def test_watch_pull_reports_non_git_sources(populated):
    lib, _a, _b = populated
    events = watch(lib, interval=5, once=True, pull=True)
    assert {item["repo"] for item in events[0]["pulled"]} == {"crypto", "cryptanalysis"}
    assert all(item.get("skipped") == "not a git checkout" for item in events[0]["pulled"])


def test_second_refresh_reuses_versions_and_keeps_them_searchable(populated):
    lib, _a, _b = populated
    before = lib.status()
    report = refresh(lib)
    after = lib.status()
    assert report["indexed"] >= before["active_documents"]
    assert report["failed"] == 0
    assert after["active_documents"] == before["active_documents"]
    assert after["documents"] == before["documents"]
    assert lib.search("Semaev decomposition", top_k=1)["results"]


def test_watch_does_not_acknowledge_changes_after_ingestion(tmp_path, monkeypatch):
    import importlib

    watcher = importlib.import_module("research_kb.watch")
    source = tmp_path / "source"
    source.mkdir()
    (source / "note.md").write_text("# Initial\n\nThe first document has enough prose to index.\n")
    config = tmp_path / "sources.toml"
    config.write_text(f'[[sources]]\nname="source"\nroot={json.dumps(str(source))}\n')
    library = Library(Settings(home=tmp_path / "state", config=config))
    actual_refresh = watcher.refresh

    def refresh_then_edit(lib):
        report = actual_refresh(lib)
        (source / "late.md").write_text("# Late arrival\n\nLatearrivalquartz must be indexed next cycle.\n")
        return report

    monkeypatch.setattr(watcher, "refresh", refresh_then_edit)
    watch(library, interval=5, once=True)
    monkeypatch.setattr(watcher, "refresh", actual_refresh)
    following = watch(library, interval=5, once=True)
    assert following[0]["changed"] is True
    assert library.search("Latearrivalquartz", top_k=1)["results"]


def test_watch_does_not_reuse_a_legacy_postscan_signature(populated):
    from research_kb.watch import signature

    lib, _a, _b = populated
    lib.catalog.set_state("source_signature", json.dumps(signature(lib)))
    assert watch(lib, interval=5, once=True)[0]["changed"] is True
