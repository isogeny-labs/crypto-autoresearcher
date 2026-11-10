"""Pinned A14 scalar/query machinery; imports do not generate scientific inputs."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'research/prime_field_a14_execution_20261106'))
from shared import core, Meter, batch_query, check_source
from guards import NATIVE_CAPABILITY, require_fields
from query_index import QueryIndex, require
from check_query import Oracle
