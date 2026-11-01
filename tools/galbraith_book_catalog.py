#!/usr/bin/env python3
"""Build a proof-aware catalog of Galbraith's MPKC v2 PDF.

The source is a typeset book, not a machine-readable theorem database.  This
tool deliberately separates three facts which are easy to conflate:

* a bold labelled object was detected in the PDF;
* the book prints something that looks like a proof (or a proof reference);
* a statement has been translated and checked by Lean.

Only the first two are derived here.  Every catalog row starts with
``lean_status = "not_formalized"``.  A separate, reviewed overlay binds Lean
theorems to source-row hashes; this extractor never emits axioms, ``sorry``, or
machine-verification claims.

The full JSONL output contains lossy PDF text and belongs in the artifact
store.  ``--index-dir`` writes compact, copyright-conscious Markdown indexes
containing labels, pages, hashes, and status only.

PyMuPDF is optional for the repository as a whole and required only when this
tool is run::

    python3 tools/galbraith_book_catalog.py \
      --pdf /path/to/main.pdf \
      --errata-html /path/to/crypto-book.html \
      --catalog /tmp/object-catalog.jsonl \
      --summary inputs/GALBRAITH-MPKC-2018/catalog-summary.json \
      --errata-output inputs/GALBRAITH-MPKC-2018/official-errata.json \
      --index-dir inputs/GALBRAITH-MPKC-2018/catalog-index
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from typing import Any, Iterable


SCHEMA = "crypto.autoresearch.book_object_catalog.v1"
SUMMARY_SCHEMA = "crypto.autoresearch.book_object_catalog_summary.v1"
SOURCE_ID = "book:galbraith-mpkc-v2-2018"
EXPECTED_PDF_SHA256 = "ca75ee62b96daa0d46faaa2d4dc28205683455ad3a2a48586b9b39299c25022d"

KINDS = (
    "Definition",
    "Theorem",
    "Lemma",
    "Corollary",
    "Proposition",
    "Conjecture",
    "Heuristic",
    "Remark",
    "Example",
    "Algorithm",
    "Exercise",
    "Notation",
)
THEOREM_KINDS = {"Theorem", "Lemma", "Corollary", "Proposition"}
NUMBERED_LABEL = r"(?:[A-Z]\.)?\d+(?:\.\d+){1,3}"
OBJECT_RE = re.compile(
    rf"^(?P<kind>{'|'.join(KINDS)})\s+"
    rf"(?P<label>{NUMBERED_LABEL})(?:\.|(?=\s|$))"
)
ALGORITHM_RE = re.compile(r"^Algorithm\s+(?P<label>\d+)(?=\s|$)")
UNNUMBERED_RE = re.compile(rf"^(?P<kind>{'|'.join(KINDS)})(?:\.|\s*$)")
ERRATA_LABEL_RE = re.compile(
    rf"\b(?P<kind>Definition|Theorem|Lemma|Corollary|Proposition|Conjecture|"
    rf"Heuristic|Remark|Example|Exercise)\s+(?P<label>{NUMBERED_LABEL})\b",
    re.IGNORECASE,
)
SECTION_RE = re.compile(r"\bSection\s+(?P<section>(?:[A-Z]\.)?\d+(?:\.\d+)*)\b", re.I)
SOLUTION_ENTRY_RE = re.compile(rf"(?m)^\s*(?P<label>\d+(?:\.\d+){{2,3}})(?::|\s+(?=See\b))")

LIGATURES = str.maketrans(
    {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
    }
)


def normalize_text(value: str) -> str:
    """Normalize only extraction artefacts; preserve mathematical symbols."""

    return value.translate(LIGATURES).replace("\u00a0", " ")


def compact_text(value: str) -> str:
    return " ".join(normalize_text(value).split())


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for part in iter(lambda: handle.read(1 << 20), b""):
            digest.update(part)
    return digest.hexdigest()


def _is_bold(font: str) -> bool:
    upper = font.upper()
    return "BOLD" in upper or "CMBX" in upper or upper.endswith("BX")


@dataclass(frozen=True)
class Block:
    ordinal: int
    page: int
    page_block: int
    text: str
    lines: tuple[str, ...]
    first_span_text: str
    first_font: str
    fonts: tuple[str, ...]
    bbox: tuple[float, float, float, float]
    context: str


@dataclass(frozen=True)
class ObjectStart:
    block_ordinal: int
    kind: str
    label: str | None
    synthetic_label: str


class ErrataParser(HTMLParser):
    """Extract list items from the official page's Errata section only."""

    def __init__(self) -> None:
        super().__init__()
        self.in_errata = False
        self.in_item = False
        self.current: list[str] = []
        self.items: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if self.in_errata and tag.lower() == "li":
            # The author's HTML uses old-style ``<li>`` starts without
            # matching end tags.  A following item therefore closes the
            # previous one for our purposes.
            self._finish_item()
            self.in_item = True
            self.current = []

    def handle_endtag(self, tag: str) -> None:
        if self.in_item and tag.lower() == "li":
            self._finish_item()
        elif self.in_errata and tag.lower() == "ul":
            self._finish_item()

    def _finish_item(self) -> None:
        if not self.in_item:
            return
        text = compact_text(" ".join(self.current))
        if text:
            self.items.append(text)
        self.current = []
        self.in_item = False

    def handle_data(self, data: str) -> None:
        text = compact_text(data)
        if text == "Errata":
            self.in_errata = True
            return
        if text == "Full Extended Text":
            self._finish_item()
            self.in_errata = False
            return
        if self.in_item and text:
            self.current.append(text)


def parse_errata(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    parser = ErrataParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    rows = []
    for index, text in enumerate(parser.items, 1):
        labels = [
            {"kind": match["kind"].title(), "label": match["label"]}
            for match in ERRATA_LABEL_RE.finditer(text)
        ]
        section = SECTION_RE.search(text)
        lowered = text.lower()
        severity = (
            "substantive"
            if any(term in lowered for term in ("false", "incorrect", "not true", "problem with"))
            else "correction"
        )
        rows.append(
            {
                "id": f"ERRATA-{index:03d}",
                "text": text,
                "text_sha256": sha256_text(text),
                "labels": labels,
                "section": section["section"] if section else None,
                "severity": severity,
                "resolution": "requires_comparison_with_pinned_2018_pdf",
            }
        )
    return rows


def _pymupdf_module():
    try:
        import pymupdf  # type: ignore

        return pymupdf
    except ImportError:
        try:
            import fitz as pymupdf  # type: ignore

            return pymupdf
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF is required for catalog extraction (pip install pymupdf)"
            ) from exc


def _block_lines(raw: dict[str, Any]) -> tuple[tuple[str, ...], list[dict[str, Any]]]:
    lines: list[str] = []
    spans: list[dict[str, Any]] = []
    for line in raw.get("lines", []):
        line_spans = line.get("spans", [])
        value = "".join(str(span.get("text", "")) for span in line_spans)
        lines.append(normalize_text(value))
        spans.extend(line_spans)
    return tuple(lines), spans


def _context_update(text: str, current: str) -> str:
    match = re.fullmatch(r"Chapter\s+(\d+)", compact_text(text), re.I)
    if match:
        return f"chapter-{int(match[1]):02d}"
    if re.fullmatch(r"Appendix\s+A", compact_text(text), re.I):
        return "appendix-a"
    if re.fullmatch(r"Appendix\s+B", compact_text(text), re.I):
        return "appendix-b"
    return current


def read_blocks(pdf: Path) -> tuple[list[Block], dict[int, str], str]:
    pymupdf = _pymupdf_module()
    blocks: list[Block] = []
    pages: dict[int, str] = {}
    context = "frontmatter"
    with pymupdf.open(pdf) as document:
        if document.is_encrypted:
            raise ValueError("encrypted PDF cannot be cataloged")
        ordinal = 0
        for page_number, page in enumerate(document, 1):
            pages[page_number] = normalize_text(page.get_text("text", sort=True))
            raw_blocks = page.get_text("dict", sort=True).get("blocks", [])
            for page_block, raw in enumerate(raw_blocks):
                if "lines" not in raw:
                    continue
                lines, spans = _block_lines(raw)
                text = "\n".join(lines).strip()
                if not text:
                    continue
                context = _context_update(text, context)
                nonempty = [span for span in spans if str(span.get("text", "")).strip()]
                first = nonempty[0] if nonempty else {"text": "", "font": ""}
                blocks.append(
                    Block(
                        ordinal=ordinal,
                        page=page_number,
                        page_block=page_block,
                        text=normalize_text(text),
                        lines=lines,
                        first_span_text=normalize_text(str(first.get("text", ""))).strip(),
                        first_font=str(first.get("font", "")),
                        fonts=tuple(str(span.get("font", "")) for span in nonempty),
                        bbox=tuple(float(x) for x in raw.get("bbox", (0, 0, 0, 0))),
                        context=context,
                    )
                )
                ordinal += 1
        version = getattr(pymupdf, "VersionBind", None)
        if version is None:
            version_tuple = getattr(pymupdf, "version", ("unknown",))
            version = version_tuple[0] if version_tuple else "unknown"
    return blocks, pages, str(version)


def detect_object(block: Block, unnumbered_counts: Counter[str]) -> ObjectStart | None:
    if not _is_bold(block.first_font):
        return None
    first_line = compact_text(block.lines[0]) if block.lines else compact_text(block.text)
    match = OBJECT_RE.match(first_line)
    if match:
        kind, label = match["kind"], match["label"]
        return ObjectStart(block.ordinal, kind, label, label)
    match = ALGORITHM_RE.match(first_line)
    if match:
        label = match["label"]
        return ObjectStart(block.ordinal, "Algorithm", label, label)
    if first_line == "Notation" or first_line.startswith("Notation for ") or first_line.startswith("Notation in ") or first_line.startswith("Notation used "):
        unnumbered_counts["Notation"] += 1
        synthetic = f"p{block.page}-{unnumbered_counts['Notation']}"
        return ObjectStart(block.ordinal, "Notation", None, synthetic)
    match = UNNUMBERED_RE.match(first_line)
    if not match:
        return None
    kind = match["kind"]
    unnumbered_counts[kind] += 1
    synthetic = f"p{block.page}-{unnumbered_counts[kind]}"
    return ObjectStart(block.ordinal, kind, None, synthetic)


def truth_status(kind: str) -> str:
    if kind in {"Definition", "Notation"}:
        return "definition_unreviewed"
    if kind == "Heuristic":
        return "heuristic_not_theorem"
    if kind == "Conjecture":
        return "conjectural"
    if kind == "Exercise":
        return "exercise_obligation"
    if kind in THEOREM_KINDS:
        return "claimed_result_unreviewed"
    return "expository_unreviewed"


def _proof_status(text: str, complete: bool) -> str:
    lowered = compact_text(text).lower()
    if any(term in lowered for term in ("left as an exercise", "omit the proof", "without proof")):
        return "partial_or_omitted"
    after = re.sub(r"^proof\s*:\s*", "", compact_text(text), flags=re.I)
    if after.lower().startswith(("see ", "this is theorem ", "follows from ")):
        return "citation_only"
    if "(sketch" in lowered or "proof sketch" in lowered:
        return "sketch_complete" if complete else "sketch_unbounded"
    return "present_complete" if complete else "present_unbounded"


def _section_for(kind: str, label: str | None, context: str) -> str | None:
    if label and kind != "Algorithm" and "." in label:
        return label.rsplit(".", 1)[0]
    if context.startswith("chapter-"):
        return str(int(context.split("-")[1]))
    return None


def _errata_maps(errata: list[dict[str, Any]]) -> tuple[dict[tuple[str, str], list[str]], dict[str, list[str]]]:
    exact: dict[tuple[str, str], list[str]] = defaultdict(list)
    section: dict[str, list[str]] = defaultdict(list)
    for item in errata:
        for label in item["labels"]:
            exact[(label["kind"].lower(), label["label"])].append(item["id"])
        if item.get("section"):
            section[item["section"]].append(item["id"])
    return exact, section


def _solution_pages(pages: dict[int, str], starts_at: int = 605) -> dict[str, list[int]]:
    found: dict[str, list[int]] = defaultdict(list)
    for page, text in pages.items():
        if page < starts_at:
            continue
        for match in SOLUTION_ENTRY_RE.finditer(text):
            if page not in found[match["label"]]:
                found[match["label"]].append(page)
    return found


def extract_catalog(pdf: Path, errata: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    digest = file_sha256(pdf)
    if digest != EXPECTED_PDF_SHA256:
        raise ValueError(
            "source PDF hash mismatch: expected "
            f"{EXPECTED_PDF_SHA256}, observed {digest}"
        )
    blocks, pages, pymupdf_version = read_blocks(pdf)
    block_by_ordinal = {block.ordinal: block for block in blocks}
    unnumbered_counts: Counter[str] = Counter()
    starts: list[ObjectStart] = []
    for block in blocks:
        start = detect_object(block, unnumbered_counts)
        if start is not None:
            starts.append(start)

    exact_errata, section_errata = _errata_maps(errata)
    solutions = _solution_pages(pages)
    rows: list[dict[str, Any]] = []
    duplicate_keys: list[str] = []
    seen: set[tuple[str, str]] = set()

    for position, start in enumerate(starts):
        block = block_by_ordinal[start.block_ordinal]
        key = (start.kind, start.synthetic_label)
        if key in seen:
            duplicate_keys.append(f"{start.kind} {start.synthetic_label}")
        seen.add(key)
        next_ordinal = starts[position + 1].block_ordinal if position + 1 < len(starts) else len(blocks)

        proof_text = ""
        proof_pages: list[int] = []
        proof_complete = False
        if start.kind in THEOREM_KINDS:
            proof_started = False
            captured: list[str] = []
            # The next labelled object is a hard boundary.  This may include
            # prose around a long proof, but can never steal the next claim.
            for ordinal in range(start.block_ordinal + 1, next_ordinal):
                candidate = block_by_ordinal[ordinal]
                first = compact_text(candidate.lines[0] if candidate.lines else candidate.text)
                if not proof_started:
                    if not (first.startswith("Proof:") and _is_bold(candidate.first_font)):
                        continue
                    proof_started = True
                captured.append(candidate.text)
                proof_pages.append(candidate.page)
                if "□" in candidate.text:
                    proof_complete = True
                    # A PyMuPDF block can contain narrative after the end box.
                    captured[-1] = candidate.text.split("□", 1)[0].rstrip() + "\n□"
                    break
            if captured:
                proof_text = "\n\n".join(captured)
                book_proof_status = _proof_status(proof_text, proof_complete)
            else:
                book_proof_status = "absent_in_book"
        else:
            book_proof_status = "not_applicable"

        label = start.label
        section = _section_for(start.kind, label, block.context)
        exact = exact_errata.get((start.kind.lower(), label), []) if label else []
        section_flags = section_errata.get(section, []) if section else []
        solution_pages = solutions.get(label or "", []) if start.kind == "Exercise" else []
        statement_text = block.text
        source_key = f"{start.kind} {label or start.synthetic_label}"
        rows.append(
            {
                "schema": SCHEMA,
                "source_id": SOURCE_ID,
                "source_sha256": digest,
                "object_id": f"{SOURCE_ID}:{start.kind.lower()}:{start.synthetic_label}",
                "source_key": source_key,
                "kind": start.kind,
                "label": label,
                "synthetic_label": start.synthetic_label,
                "context": block.context,
                "section": section,
                "pdf_page_start": block.page,
                "pdf_page_end": block.page,
                "statement_extraction": {
                    "method": "first PyMuPDF text block beginning with a bold label",
                    "fidelity": "lossy_unreviewed",
                    "text": statement_text,
                    "sha256": sha256_text(statement_text),
                    "font": block.first_font,
                    "page_block": block.page_block,
                },
                "book_proof": {
                    "status": book_proof_status,
                    "pages": sorted(set(proof_pages)),
                    "text": proof_text or None,
                    "sha256": sha256_text(proof_text) if proof_text else None,
                    "end_box_detected": proof_complete,
                },
                "official_errata": {
                    "exact": exact,
                    "same_section": section_flags,
                    "status": "requires_manual_resolution" if (exact or section_flags) else "none_detected",
                },
                "appendix_b_hint_or_solution": {
                    "detected": bool(solution_pages),
                    "pages": solution_pages,
                    "fidelity": "label_reference_only_unreviewed",
                },
                "truth_status": truth_status(start.kind),
                "lean_status": "not_formalized",
                "semantic_review": "not_started",
            }
        )

    counts = Counter(row["kind"] for row in rows)
    proof_counts = Counter(row["book_proof"]["status"] for row in rows)
    summary = {
        "schema": SUMMARY_SCHEMA,
        "source_id": SOURCE_ID,
        "source_sha256": digest,
        "pdf_pages": len(pages),
        "extractor": {"path": "tools/galbraith_book_catalog.py", "pymupdf": pymupdf_version},
        "objects": len(rows),
        "counts_by_kind": dict(sorted(counts.items())),
        "counts_by_book_proof_status": dict(sorted(proof_counts.items())),
        "official_errata_items": len(errata),
        "objects_with_exact_errata": sum(bool(row["official_errata"]["exact"]) for row in rows),
        "objects_with_section_errata": sum(bool(row["official_errata"]["same_section"]) for row in rows),
        "exercises_with_appendix_b_signal": sum(
            row["kind"] == "Exercise" and row["appendix_b_hint_or_solution"]["detected"]
            for row in rows
        ),
        "lean_status": {"not_formalized": len(rows)},
        "duplicate_kind_labels": duplicate_keys,
        "limitations": [
            "The PDF is untagged; statement extraction is a lossy first-block transcription.",
            "Displayed mathematics, multi-block statements, and reading order require semantic review.",
            "A printed proof, sketch, citation, or solution hint is not a truth or Lean-verification claim.",
            "Official errata numbering sometimes refers to the 2012 edition rather than this v2 PDF.",
            "Unlabelled prose claims are searchable in the ingested PDF but are not catalog rows.",
        ],
    }
    return rows, summary


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            line = json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
            handle.write(line)
            digest.update(line.encode("utf-8"))
    return digest.hexdigest()


def _safe_group(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-") or "unknown"


def write_indexes(directory: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["context"]].append(row)

    expected: set[Path] = set()
    for context, members in sorted(grouped.items()):
        target = directory / f"{_safe_group(context)}.md"
        expected.add(target)
        lines = [
            f"# {context.replace('-', ' ').title()}",
            "",
            "Generated from the hash-pinned PDF. This index records detection and source hashes,",
            "not truth, semantic fidelity, or Lean verification. Full lossy text is in the",
            "artifact-store catalog named by `../catalog-summary.json`.",
            "",
            "| source key | kind | PDF page | book proof | errata | Appendix B | Lean | statement SHA-256 |",
            "|---|---|---:|---|---|---|---|---|",
        ]
        for row in members:
            errata = ", ".join(row["official_errata"]["exact"]) or (
                "section flag" if row["official_errata"]["same_section"] else "none"
            )
            appendix = (
                ",".join(str(page) for page in row["appendix_b_hint_or_solution"]["pages"])
                if row["appendix_b_hint_or_solution"]["detected"]
                else "none"
            )
            statement_hash = row["statement_extraction"]["sha256"]
            lines.append(
                f"| `{row['source_key']}` | {row['kind']} | {row['pdf_page_start']} | "
                f"{row['book_proof']['status']} | {errata} | {appendix} | "
                f"{row['lean_status']} | `{statement_hash}` |"
            )
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Remove only obsolete generated Markdown files in this dedicated output
    # directory.  Refuse to touch any non-Markdown file.
    for path in directory.iterdir():
        if path.name == "README.md" or path in expected:
            continue
        if path.suffix != ".md":
            raise ValueError(f"refusing to remove non-generated file from index directory: {path}")
        path.unlink()

    readme = directory / "README.md"
    readme.write_text(
        "# Galbraith MPKC v2 labelled-object index\n\n"
        f"Source SHA-256: `{summary['source_sha256']}`. Detected objects: "
        f"**{summary['objects']}**. All default to `not_formalized`.\n\n"
        "This is an index over bold, labelled objects and the front-matter notation blocks. "
        "The complete PDF remains available at the hash-pinned official URL; KB publication "
        "is currently blocked by IAM and is not claimed. See `../README.md` for evidence "
        "boundaries and reproduction.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--errata-html", type=Path)
    parser.add_argument("--errata-output", type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--index-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    errata = parse_errata(args.errata_html)
    rows, summary = extract_catalog(args.pdf, errata)
    if args.errata_output:
        args.errata_output.parent.mkdir(parents=True, exist_ok=True)
        errata_document = {
            "schema": "crypto.autoresearch.book_official_errata.v1",
            "source_id": SOURCE_ID,
            "source_url": "https://www.math.auckland.ac.nz/~sgal018/crypto-book/crypto-book.html",
            "items": errata,
        }
        args.errata_output.write_text(
            json.dumps(errata_document, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        summary["official_errata_sha256"] = file_sha256(args.errata_output)
    summary["catalog_sha256"] = write_jsonl(args.catalog, rows)
    summary["catalog_bytes"] = args.catalog.stat().st_size
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_indexes(args.index_dir, rows, summary)
    print(
        f"cataloged {summary['objects']} labelled objects from {summary['pdf_pages']} pages; "
        f"catalog sha256 {summary['catalog_sha256']}"
    )
    if summary["duplicate_kind_labels"]:
        print(
            f"warning: {len(summary['duplicate_kind_labels'])} duplicate kind/labels detected",
            file=__import__("sys").stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
