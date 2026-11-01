from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from tools.galbraith_book_catalog import (
    Block,
    ErrataParser,
    detect_object,
    normalize_text,
    parse_errata,
)
from collections import Counter


class GalbraithBookCatalogUnitTests(unittest.TestCase):
    def block(self, text: str, *, font: str = "CMBX10") -> Block:
        return Block(
            ordinal=0,
            page=44,
            page_block=2,
            text=text,
            lines=(text,),
            first_span_text=text.split(" ", 1)[0],
            first_font=font,
            fonts=(font,),
            bbox=(0.0, 0.0, 1.0, 1.0),
            context="chapter-02",
        )

    def test_ligature_normalization_and_numbered_detection(self) -> None:
        block = self.block("Deﬁnition 2.1.15. A reduction is ...")
        found = detect_object(block, Counter())
        self.assertIsNotNone(found)
        self.assertEqual(found.kind, "Definition")
        self.assertEqual(found.label, "2.1.15")
        self.assertEqual(normalize_text("aﬃne ﬁeld"), "affine field")

    def test_cross_reference_in_roman_font_is_not_an_object(self) -> None:
        block = self.block("Lemma 21.4.9.", font="CMR10")
        self.assertIsNone(detect_object(block, Counter()))

    def test_algorithm_and_unnumbered_theorem(self) -> None:
        algorithm = detect_object(self.block("Algorithm 16 The rho algorithm"), Counter())
        self.assertEqual((algorithm.kind, algorithm.label), ("Algorithm", "16"))
        theorem = detect_object(self.block("Theorem. Let the notation be as above"), Counter())
        self.assertEqual(theorem.kind, "Theorem")
        self.assertIsNone(theorem.label)
        self.assertEqual(theorem.synthetic_label, "p44-1")
        notation = detect_object(self.block("Notation for algorithms and complexity"), Counter())
        self.assertEqual((notation.kind, notation.synthetic_label), ("Notation", "p44-1"))

    def test_errata_parser_ignores_review_lists(self) -> None:
        html = """
        <h2>Reviews</h2><ul><li>Not errata</li></ul>
        <b>Errata</b><ul>
          <li>Section 5.3, Theorem 5.3.8: The theorem is false.
          <li>Section 9.5, Exercise 9.5.8: The claim is incorrectly stated.
        </ul><b>Full Extended Text</b><ul><li>Not errata either</li></ul>
        """
        parser = ErrataParser()
        parser.feed(html)
        self.assertEqual(len(parser.items), 2)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "errata.html"
            path.write_text(html, encoding="utf-8")
            rows = parse_errata(path)
        self.assertEqual(rows[0]["labels"], [{"kind": "Theorem", "label": "5.3.8"}])
        self.assertEqual(rows[0]["section"], "5.3")
        self.assertEqual(rows[0]["severity"], "substantive")


@unittest.skipUnless(importlib.util.find_spec("fitz") or importlib.util.find_spec("pymupdf"),
                     "optional PyMuPDF not installed")
class GalbraithBookCatalogPdfSmokeTests(unittest.TestCase):
    def test_pymupdf_can_make_a_fixture(self) -> None:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.pdf"
            document = fitz.open()
            page = document.new_page()
            page.insert_text((72, 72), "Lemma 1.1.1.", fontname="hebo")
            page.insert_text((150, 72), " A fixture statement.")
            document.save(path)
            self.assertGreater(path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
