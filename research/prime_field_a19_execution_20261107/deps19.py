"""Pinned scientific imports; importing performs no experiment."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/prime_field_a18_execution_20261107'))
from deps18 import core,solver,NATIVE_CAPABILITY,public_base,check_base,checker,check_source,old_check
from deps18 import collection16,partial_solver,check_partial,known_checks,public_verify,commitment
from deps16 import pair_build,check_pairs,TargetCache,native_case
from shared import check_solver
import custody18 as prior
