"""Unchanged A20 collection and corrected A21 formal producer dependencies."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/prime_field_a21_execution_20261107'))
from deps21 import NATIVE_CAPABILITY as DIRECT_CAPABILITY
from deps20 import core,solver,NATIVE_CAPABILITY,public_base,check_base,checker,check_source,commitment,known_checks,public_verify,check_pairs
import custody20 as acquisition,custody21 as prior
import direct21,check21
