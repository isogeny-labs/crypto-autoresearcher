"""Pinned A17 scientific components; imports perform no native generation."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/prime_field_a17_execution_20261107'))
from deps17 import core,solver,NATIVE_CAPABILITY,public_base,check_base,checker,check_source,old_check
from deps17 import collection16,checks16,partial_solver,check_partial,known_checks,public_verify,commitment
import custody17 as prior
