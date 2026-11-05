"""UNVALIDATED private per-solve refuter binding for the counted engine fork."""
import copy
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from .transform import ROOT, verify_baselines

ENGINE_PATH = Path(__file__).with_name('engine_counted.py')
SIDECAR = 'refuter_diagnostics'


def _private_engine(mode):
    if mode not in ('baseline', 'active_support'):
        raise ValueError('unknown refuter mode')
    verify_baselines()
    spec = importlib.util.spec_from_file_location('private_transform_counted_engine', ENGINE_PATH)
    engine = importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)
    path = ROOT/'research/prime_sat_active_support_implementation_20261030/active_refute.py'
    spec = importlib.util.spec_from_file_location('private_transform_refuter', path)
    refuter = importlib.util.module_from_spec(spec); spec.loader.exec_module(refuter)
    shared = engine.legacy
    if Path(shared.__file__).resolve() != ROOT/'research/prime_sat_followup_20261029/encoding.py':
        raise ImportError('unexpected encoding module')
    identities = {name: id(value) for name, value in vars(shared).items()}
    sidecar = {'mode': mode, 'calls': [], 'units': 'separate support/validation events; not arithmetic total'}
    def bound_refute(ring, generators, degree_cap, row_cap=4096):
        diagnostic = {'call_index': len(sidecar['calls'])}; sidecar['calls'].append(diagnostic)
        try:
            return refuter.checked_refute(mode, ring, generators, degree_cap, row_cap, diagnostics=diagnostic)
        except BaseException as error:
            diagnostic.update(exception_type=type(error).__name__, exception_message=str(error))
            raise
    private = dict(vars(shared)); private['refute'] = bound_refute
    engine.legacy = SimpleNamespace(**private)
    def check_shared():
        if identities != {name: id(value) for name, value in vars(shared).items()}:
            raise AssertionError('shared encoding namespace changed')
    check_shared()
    return engine, sidecar, check_shared


def solve(ring, polys, domain, projected_bits, limits, strategy, prefix_depths,
          checkpoint=None, *, refuter_mode, attempt=None, solver_factory=None):
    engine, sidecar, check_shared = _private_engine(refuter_mode)
    def enrich(answer):
        return {**answer, SIDECAR: copy.deepcopy(sidecar)}
    def save(answer):
        check_shared()
        value = enrich(answer)
        if attempt:
            attempt.checkpoint(value, event='bridge_checkpoint', refuter_diagnostics=copy.deepcopy(sidecar))
        if checkpoint:
            checkpoint(value)
    primary = None
    try:
        answer = engine.solve(ring, polys, domain, projected_bits, limits, strategy,
                              prefix_depths, save, attempt=attempt, solver_factory=solver_factory)
        return enrich(answer)
    except BaseException as error:
        primary = error
        if attempt:
            attempt.failure(error, 'counted_bridge')
        try:
            error.refuter_diagnostics = copy.deepcopy(sidecar)
            if hasattr(error, 'partial_transcript') and error.partial_transcript is not None:
                error.partial_transcript = enrich(error.partial_transcript)
                if attempt:
                    attempt.checkpoint(error.partial_transcript, event='bridge_failed')
        except BaseException as secondary:
            if attempt:
                attempt.secondary(secondary, 'bridge_failure_checkpoint')
        raise
    finally:
        try:
            check_shared()
        except BaseException as error:
            if primary is None:
                raise
            if attempt:
                attempt.secondary(error, 'shared_namespace_guard')
