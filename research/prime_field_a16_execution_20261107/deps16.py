"""Pinned A14/A15 components; importing performs no fresh native generation."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/prime_field_a15_execution_20261107'))
from deps15 import core,Meter,batch_query,check_source,NATIVE_CAPABILITY,require_fields
from pairbuild15 import build as pair_build
from check15 import check_pairs,commitment
import custody15 as prior
import mixed_collection as old_collection
import check_mixed as old_check
import public_base,check_base,affine_branch,native_case,partial_solver,check_partial
import information,check_information
from target_cache import TargetCache
from baseline import checker,solver,costs
import known_checks
