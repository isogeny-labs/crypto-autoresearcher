"""Fixed F27 full-row native replay and malformed-stream rejection."""

import copy
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

from native_squareclass_stream import verify_native, write_stream


HERE = Path(__file__).parent


class NativeSquareclassStreamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-native-squareclass-")
        cls.candidate = Path(cls.scratch.name) / "candidate_unit"
        cls.checker = Path(cls.scratch.name) / "independent_squareclass_native"
        for source, target in ((HERE / "candidate_unit.rs", cls.candidate),
                               (HERE / "independent_squareclass_native.rs", cls.checker)):
            subprocess.run(["rustc", "--edition=2021", "-O", str(source),
                            "-o", str(target)], check=True, capture_output=True)
        cls.checker_sha = hashlib.sha256(cls.checker.read_bytes()).hexdigest()
        cls.units = []
        for form in ([1, 0, 1, 1, 0], [1, 1, 1, 0, 1],
                     [2, 4, 22, 4, 2]):
            raw = subprocess.check_output([
                str(cls.candidate), "3", "3", ",".join(map(str, form)),
                "27", "819", "3276", "1000", "1000", "819"])
            unit = json.loads(raw)
            binding = {"schema": "pext.candidate-binding/v1",
                       "experiment": "EXP-PEXT-bf8f96",
                       "cohort": "f27-software-fixture", "class_index": 0,
                       "T_index": 0, "model": {"fixture": True}, "target": None,
                       "field": unit["field"], "quotient_form": form,
                       "input_sha256": "a"*64, "manifest_sha256": "b"*64,
                       "join_plan_sha256": "c"*64, "structure_offset": 0,
                       "structure_end_exclusive": 819, "structures_per_T": 819}
            cls.units.append((raw, unit, binding))

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def _stream(self, raw, binding):
        sink = io.BytesIO()
        receipt = write_stream(raw, binding, hashlib.sha256(raw).hexdigest(), sink)
        return sink.getvalue(), receipt

    def _native(self, stream):
        return subprocess.run([str(self.checker)], input=stream,
                              capture_output=True, check=False)

    def test_all_fixed_f27_exceptional_rows(self):
        expected = [(279, "1:1:1,3:3:278"), (1, "1:1:1"),
                    (592, "2:2:2,2:3:8,3:3:582")]
        for (raw, unit, binding), (count, pairs) in zip(self.units, expected):
            with self.subTest(form=binding["quotient_form"]):
                receipt = verify_native(raw, binding, hashlib.sha256(raw).hexdigest(),
                                        self.checker, self.checker_sha)
                self.assertEqual((receipt["rows"], receipt["native_summary"]),
                                 (count, f"OK rows={count} rank_pairs={pairs}"))
                self.assertEqual(len(unit["rows"]), count)
                self.assertEqual(receipt["candidate_raw_sha256"],
                                 hashlib.sha256(raw).hexdigest())

    def test_producer_rows_and_external_binding_cannot_change(self):
        raw, unit, binding = self.units[0]
        for edit in ("genus", "rank", "constant", "matrix", "ordinal"):
            with self.subTest(edit=edit):
                changed = copy.deepcopy(unit)
                if edit == "genus":
                    changed["rows"][0][4] += 1
                elif edit == "rank":
                    changed["rows"][0][2] = 2
                elif edit == "constant":
                    changed["exceptional_squareclasses"][0][1] = True
                elif edit == "matrix":
                    changed["rows"][0][1][0] ^= 1
                else:
                    changed["rows"][1][0] = changed["rows"][0][0]
                altered = json.dumps(changed).encode()
                if edit in ("ordinal", "matrix"):
                    with self.assertRaisesRegex(ValueError,
                                                "strictly increasing|independent ordinal"):
                        self._stream(altered, binding)
                else:
                    with self.assertRaisesRegex(ValueError, "native squareclass replay refused"):
                        verify_native(altered, binding,
                                      hashlib.sha256(altered).hexdigest(),
                                      self.checker, self.checker_sha)
        bad_binding = copy.deepcopy(binding)
        bad_binding["quotient_form"][0] ^= 1
        with self.assertRaisesRegex(ValueError, "external field/form"):
            self._stream(raw, bad_binding)
        bad_binding = copy.deepcopy(binding)
        bad_binding["structures_per_T"] = 818
        with self.assertRaisesRegex(ValueError, "external field/form"):
            self._stream(raw, bad_binding)
        with self.assertRaisesRegex(ValueError, "sealed raw candidate digest"):
            write_stream(raw, binding, "0"*64, io.BytesIO())
        with self.assertRaisesRegex(ValueError, "differs from published hash"):
            verify_native(raw, binding, hashlib.sha256(raw).hexdigest(),
                          self.checker, "0"*64)

    def test_native_truncation_trailing_and_reducible_modulus(self):
        raw, _, binding = self.units[1]
        stream, _ = self._stream(raw, binding)
        for altered in (stream[:-1], stream + b"x"):
            with self.subTest(length=len(altered)):
                result = self._native(altered)
                self.assertEqual(result.returncode, 2)
        # Magic(8), p(2), n(1), then four u16 modulus coefficients.
        reducible = bytearray(stream)
        reducible[11:19] = struct.pack("<4H", 0, 0, 0, 1)
        result = self._native(reducible)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"reducible field modulus", result.stderr)
        # Explicit row-count cannot be silently truncated to a sample.
        wrong_count = bytearray(stream)
        count_offset = 8 + 2 + 1 + 4*2 + 5*2 + 8
        wrong_count[count_offset:count_offset+4] = struct.pack("<I", 2)
        self.assertEqual(self._native(wrong_count).returncode, 2)

    def test_published_n5_one_row_arithmetic_fixture(self):
        from candidate_binding import CandidateBinder
        from candidate_stage import join_path
        from check_quotient_certificate import Field
        from check_structure_certificate import transform
        from independent_component_geometry import assess
        from independent_transversal import IndependentTransversal

        binder = CandidateBinder("q3-n5", plan_path=join_path("q3-n5"))
        binding = binder.bind(0, 0)
        field = Field(binding["field"])
        matrix = IndependentTransversal(binding["field"]).matrix(0)
        moved = transform(field, binding["quotient_form"], matrix)
        forms = [moved]
        for _ in range(field.n - 1):
            forms.append([field.power(value, field.p) for value in forms[-1]])
        geometry = assess(binding["field"], forms)
        unit = {"schema": "pext.checked-candidate-unit/v1",
                "field": binding["field"], "form": binding["quotient_form"],
                "structures": binding["structures_per_T"], "exceptional": 1,
                "generic": binding["structures_per_T"] - 1,
                "rows": [[0, matrix, geometry["geometric_rank"],
                          geometry["branch_points"],
                          geometry["geometric_component_genus"]]],
                "exceptional_squareclasses": [[geometry["arithmetic_rank"],
                    geometry["arithmetic_rank"] > geometry["geometric_rank"]]]}
        raw = json.dumps(unit).encode()
        receipt = verify_native(raw, binding, hashlib.sha256(raw).hexdigest(),
                                self.checker, self.checker_sha)
        self.assertEqual(receipt["rows"], 1)
        self.assertEqual(receipt["binary_sha256"], self.checker_sha)


if __name__ == "__main__":
    unittest.main(verbosity=2)
