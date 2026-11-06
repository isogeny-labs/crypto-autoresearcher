"""Reuse pinned A13/A12 arithmetic; no fresh generation at import time."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'research/prime_field_a13_execution_20261106'))
from baseline import solver, check_source, check_solver, core
from baseline import batch_query, batch_check
import known_solver

Meter = solver.Meter
