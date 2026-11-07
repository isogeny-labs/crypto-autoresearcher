"""Pinned known-base components; imports do not generate native curves or targets."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/prime_field_a16_execution_20261107'))
from deps16 import core,Meter,solver,check_source,NATIVE_CAPABILITY,require_fields,commitment
from deps16 import public_base,check_base,native_case,partial_solver,check_partial,known_checks
from deps16 import checker,pair_build,check_pairs,TargetCache,old_check
import collection16,branch16,checks16,custody16
from shared import known_solver
from driver14 import public_verify
