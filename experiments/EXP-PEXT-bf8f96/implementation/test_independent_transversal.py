"""Full fixed F27 and four cohort-field ordinal alignment checks."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from independent_transversal import IndependentTransversal


BASE = Path(__file__).parent
INPUTS = BASE.parent / "inputs/classes-20261102"


class IndependentTransversalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="pext-transversal-")
        cls.directory = Path(cls.scratch.name)
        cls.join = cls.directory / "join"
        subprocess.run(["rustc", "--edition=2021", str(BASE / "join_certificate.rs"),
                        "-o", str(cls.join)], check=True, capture_output=True)
        cls.fixture = json.loads(subprocess.check_output([cls.join, "f27-char3"]))
        rust_source = '''#[path="%s"] mod quotient_core;
use quotient_core::Context;
fn main() {
 let args:Vec<String>=std::env::args().collect();
 let q:u32=args[1].parse().unwrap();let n:u32=args[2].parse().unwrap();
 let ctx=Context::new(q,n,q.pow(n)).unwrap();
 for raw in &args[3..] {
  let ordinal:u64=raw.parse().unwrap();
  ctx.visit_structures_range(ordinal,ordinal+1,1,|matrix| {
   let e=ctx.encoding();println!("{},{},{},{}",e[matrix[0] as usize],e[matrix[1] as usize],e[matrix[2] as usize],e[matrix[3] as usize]);Ok(())
  }).unwrap();
 }
}
''' % (BASE / "quotient_core.rs")
        cls.ordinal = cls.directory / "ordinal"
        subprocess.run(["rustc", "--edition=2021", "-", "-o", str(cls.ordinal)],
                       input=rust_source, text=True, check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def test_every_fixed_f27_ordinal(self):
        transversal = IndependentTransversal(self.fixture["field"])
        self.assertEqual(transversal.count, 819)
        self.assertEqual([transversal.matrix(i) for i in range(819)],
                         [row["matrix"] for row in self.fixture["rows"][:819]])
        with self.assertRaisesRegex(ValueError, "ordinal out of range"):
            transversal.matrix(819)

    def test_all_cohort_field_counts_and_sampled_ordinals(self):
        for name in ("q5-n3", "q7-n3", "q11-n3", "q3-n5"):
            with self.subTest(cohort=name):
                field = json.loads((INPUTS / f"{name}.json").read_bytes())["field"]
                transversal = IndependentTransversal(field)
                ordinals = (0, transversal.count // 2, transversal.count - 1)
                rows = subprocess.check_output(
                    [self.ordinal, str(field["prime"]), str(field["degree"]),
                     *map(str, ordinals)], text=True).splitlines()
                actual = [[int(part) for part in row.split(",")] for row in rows]
                self.assertEqual(actual, [transversal.matrix(i) for i in ordinals])


if __name__ == "__main__":
    unittest.main(verbosity=2)
