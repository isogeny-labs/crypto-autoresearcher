"""Keep the frozen 2026-11-08 syntax repairs replayable in CI."""

import unittest

from tools.check_legacy_parse_corrections_20261108 import main


class LegacyParseCorrectionTests(unittest.TestCase):
    def test_replay(self) -> None:
        main()
