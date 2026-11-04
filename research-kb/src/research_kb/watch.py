"""Keep a local catalog close to the live source checkouts.

The MCP server is deliberately read-only. Freshness belongs to an operator
process: this loop notices that a registered source changed, takes the same
writer lock as a manual ``refresh``, and rebuilds only what content hashing says
changed. A connected agent sees the new revision on its next call.

The signature is cheap on purpose -- git HEAD plus file count, total size and
the newest mtime -- so a five-repository corpus can be polled every minute
without re-reading every byte. Content hashing remains the authority inside
``refresh``; the signature only decides whether it is worth starting.
"""

from __future__ import annotations

import json
import signal
import time

from research_kb.ingest import git_commit, refresh, source_files, update_sources


def _signature_for(source) -> tuple:
    if not source.root.is_dir():
        return (source.name, None, 0, 0, 0)
    count = 0
    total = 0
    newest = 0
    for path, _relative in source_files(source):
        try:
            stat = path.stat()
        except OSError:
            continue
        count += 1
        total += stat.st_size
        newest = max(newest, stat.st_mtime_ns)
    return (source.name, git_commit(source.root), count, total, newest)


def signature(library) -> tuple:
    """A cheap, order-stable fingerprint of every registered source."""
    return tuple(_signature_for(source) for source in library.settings.sources())


def _emit(payload: dict) -> None:
    print(json.dumps(payload, sort_keys=True), flush=True)


def watch(
    library, interval: float = 60.0, once: bool = False, max_cycles: int | None = None, pull: bool = False
) -> list[dict]:
    """Poll registered sources and refresh the catalog when they move.

    ``once`` performs one check-and-refresh and returns. ``max_cycles`` bounds
    a test or a cron-style run; nothing else stops the loop except a signal.
    ``pull`` fast-forwards git checkouts first, so a push from another machine
    becomes visible without a manual operator step.
    """
    if interval < 5:
        raise ValueError("interval must be at least 5 seconds")
    stop = False

    def _stop(_signum, _frame):
        nonlocal stop
        stop = True

    previous = signal.signal(signal.SIGTERM, _stop)
    events: list[dict] = []
    cycles = 0
    stored = library.catalog.get_state("source_signature")
    last = tuple(tuple(item) for item in json.loads(stored)) if stored else None
    try:
        while not stop:
            cycles += 1
            started = time.time()
            pulled = None
            if pull:
                pulled = update_sources(library)
            current = signature(library)
            status = library.catalog.status()
            due = last is None or current != last or not status.get("ready")
            event = {"cycle": cycles, "changed": due, "signature": current}
            if pulled is not None:
                event["pulled"] = [
                    {"repo": item["repo"], "ok": item.get("ok"), "skipped": item.get("skipped")}
                    for item in pulled
                ]
            if due:
                try:
                    report = refresh(library)
                    event.update(
                        {
                            "indexed": report["indexed"],
                            "failed": report["failed"],
                            "missing_roots": report["missing_roots"],
                            "errors": report["errors"][:10],
                        }
                    )
                    last = signature(library)
                    library.catalog.set_state("source_signature", json.dumps(last))
                except Exception as exc:
                    # Another operator may hold the writer lock, or one source
                    # may be temporarily unreadable. Keep the watcher alive and
                    # retry on the next cycle.
                    event["error"] = str(exc)
            event["seconds"] = round(time.time() - started, 3)
            _emit(event)
            events.append(event)
            if once or (max_cycles is not None and cycles >= max_cycles):
                break
            deadline = time.time() + interval
            while not stop and time.time() < deadline:
                time.sleep(min(1.0, max(0.0, deadline - time.time())))
    finally:
        signal.signal(signal.SIGTERM, previous)
    return events
