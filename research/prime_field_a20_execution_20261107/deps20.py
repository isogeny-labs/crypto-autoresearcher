"""Pinned A19 scientific imports; no experiment at import time."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/prime_field_a19_execution_20261107'))
from deps19 import core,solver,NATIVE_CAPABILITY,public_base,check_base,checker,check_source,known_checks,commitment,public_verify,check_pairs
from deps19 import native_case as prior_case
import custody19 as prior
import collection19,check_collection19,branch19,pool19,cancel19,information19,check_algebra19
