"""F27 source-only C5 blinding, sealing and tamper custody checks."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from c5_blind_input import canonical, digest, prepare, verify_public
from check_c5_blind_input import verify_public as check_public
from check_c5_blind_input import verify_unblind


class C5BlindInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-c5-blind-")
        binary = Path(cls.scratch.name) / "candidate_unit"
        subprocess.run(["rustc", "--edition=2021",
                        str(Path(__file__).with_name("candidate_unit.rs")),
                        "-o", str(binary)], check=True, capture_output=True)
        form = [1, 0, 1, 1, 0]
        cls.raw = subprocess.check_output([
            str(binary), "3", "3", ",".join(map(str, form)),
            "27", "819", "3276", "1000", "1000", "819"])
        cls.unit = json.loads(cls.raw)
        cls.binding = {"schema": "pext.candidate-binding/v1",
                       "experiment": "EXP-PEXT-bf8f96", "cohort": "f27-software-fixture",
                       "class_index": 0, "T_index": 0,
                       "model": {"fixture": True}, "target": None,
                       "field": cls.unit["field"], "quotient_form": form,
                       "input_sha256": "a"*64, "manifest_sha256": "b"*64,
                       "join_plan_sha256": "c"*64,
                       "structure_offset": 0, "structure_end_exclusive": 819,
                       "structures_per_T": 819, "status": "preview_only"}
        cls.selected = {"cohort": "f27-software-fixture", "class_index": 0,
                        "T_index": 0, "torsion_count": 1,
                        "descent_status": "unresolved",
                        "candidate_unit_sha256": hashlib.sha256(cls.raw).hexdigest(),
                        "reasons": ["first_in_stratum"],
                        "unit_counterexample": False,
                        "curve_counterexample": False,
                        "counterexample_ordinals": [],
                        "type2_hyperelliptic_ordinals": [cls.unit["rows"][0][0]]}
        cls.public, cls.escrow = prepare(cls.raw, cls.binding, cls.selected,
                                         nonce=b"n"*32)
        cls.answer = {"schema": "pext.c5-independent-answer/v1",
                      "projection_sha256": digest(cls.public),
                      "structures": cls.unit["structures"],
                      "rows": [[row[0], row[1], row[2], classes[0], row[3], row[4], classes[1]]
                               for row, classes in zip(cls.unit["rows"],
                                                       cls.unit["exceptional_squareclasses"])],
                      "generic_intervals": cls.unit["generic_intervals"],
                      "exceptional_count": cls.unit["exceptional"],
                      "generic_count": cls.unit["generic"]}

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def _seal(self, answer):
        data = canonical(answer)
        seal = {"schema": "pext.c5-independent-answer-seal/v1",
                "projection_sha256": digest(self.public),
                "answer_sha256": hashlib.sha256(data).hexdigest(),
                "independent_session_receipt_sha256": "d"*64}
        return seal, data

    def _unblind(self, public, escrow, seal, data, raw, binding, selected):
        return verify_unblind(public, escrow, seal, data, raw, binding, selected,
                              expected_projection_sha256=digest(self.public),
                              expected_seal_sha256=digest(seal))

    def test_projection_hides_answers_and_unblinds_complete_fixture(self):
        encoded = canonical(self.public)
        for forbidden in (b'"rows"', b'"exceptional_squareclasses"',
                          b'"geometric_rank"', b'"arithmetic_rank"',
                          b'"geometric_genus"', b'"descent_status"',
                          b'"generic_intervals"', b'"factor_pattern"'):
            self.assertNotIn(forbidden, encoded)
        self.assertEqual(verify_public(self.public, self.binding)["projection_sha256"],
                         digest(self.public))
        self.assertEqual(check_public(self.public, self.binding,
                         expected_projection_sha256=digest(self.public))["projection_sha256"],
                         digest(self.public))
        seal, data = self._seal(self.answer)
        checked = self._unblind(self.public, self.escrow, seal, data,
                                self.raw, self.binding, self.selected)
        self.assertTrue(checked["valid"])
        self.assertEqual(checked["structures"], 819)
        self.assertEqual((len(self.answer["rows"]), self.answer["generic_count"]),
                         (279, 540))

    def test_changed_identity_raw_and_private_roster_rejected(self):
        bad_binding = copy.deepcopy(self.binding)
        bad_binding["T_index"] = 1
        with self.assertRaisesRegex(ValueError, "projection identity"):
            verify_public(self.public, bad_binding)
        bad_public = copy.deepcopy(self.public)
        bad_public["rows"] = self.unit["rows"]
        with self.assertRaisesRegex(ValueError, "projection identity"):
            check_public(bad_public, self.binding,
                         expected_projection_sha256=digest(self.public))
        with self.assertRaisesRegex(ValueError, "external handoff digest"):
            check_public(self.public, self.binding,
                         expected_projection_sha256="0"*64)
        bad_selected = copy.deepcopy(self.selected)
        bad_selected["descent_status"] = "certified_admissible"
        seal, data = self._seal(self.answer)
        with self.assertRaisesRegex(ValueError, "roster commitment"):
            self._unblind(self.public, self.escrow, seal, data,
                          self.raw, self.binding, bad_selected)
        with self.assertRaisesRegex(ValueError, "producer raw bytes"):
            self._unblind(self.public, self.escrow, seal, data,
                          self.raw+b"\n", self.binding, self.selected)

    def test_seal_and_complete_answer_required_before_unblinding(self):
        seal, data = self._seal(self.answer)
        with self.assertRaisesRegex(ValueError, "not sealed"):
            self._unblind(self.public, self.escrow, seal, data+b" ",
                          self.raw, self.binding, self.selected)
        with self.assertRaisesRegex(ValueError, "external session readback"):
            verify_unblind(self.public, self.escrow, seal, data,
                           self.raw, self.binding, self.selected,
                           expected_projection_sha256=digest(self.public),
                           expected_seal_sha256="0"*64)
        wrong_genus = copy.deepcopy(self.answer)
        wrong_genus["rows"][0][5] += 1
        resealed, wrong_data = self._seal(wrong_genus)
        with self.assertRaisesRegex(ValueError, "differs from sealed producer"):
            self._unblind(self.public, self.escrow, resealed, wrong_data,
                          self.raw, self.binding, self.selected)
        omitted = copy.deepcopy(self.answer)
        omitted["rows"].pop()
        resealed, wrong_data = self._seal(omitted)
        with self.assertRaisesRegex(ValueError, "coverage counters"):
            self._unblind(self.public, self.escrow, resealed, wrong_data,
                          self.raw, self.binding, self.selected)
        duplicate = copy.deepcopy(self.answer)
        duplicate["rows"][1][0] = duplicate["rows"][0][0]
        resealed, wrong_data = self._seal(duplicate)
        with self.assertRaisesRegex(ValueError, "ordinal or complement"):
            self._unblind(self.public, self.escrow, resealed, wrong_data,
                          self.raw, self.binding, self.selected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
