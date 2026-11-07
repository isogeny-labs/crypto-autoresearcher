"""Import the immutable A20 scientific implementation, without running it."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/prime_field_a20_execution_20261107'))
from deps20 import core,solver,commitment,known_checks,check_source,public_verify
from deps19 import partial_solver,check_solver
import cancel19,check_algebra19,check_formal20,custody20 as prior

NATIVE_CAPABILITY=object()
