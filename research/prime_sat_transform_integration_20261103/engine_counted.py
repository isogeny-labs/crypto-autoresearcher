"""UNVALIDATED scoped fork: exception-safe counted partial-prefix search.

The only strategy switch enables theory calls with fewer than n assignments.
All clauses delivered to CaDiCaL exclude either an algebraically refuted LSB
prefix or a projection with an already checked witness. UNKNOWN is not UNSAT.
"""
from collections import Counter, deque
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import sys

from pysat.engines import Propagator
from pysat.solvers import Cadical195

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/prime_sat_followup_20261029"))
import encoding as legacy


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adapter = load("research/prime_sat_prefix_adapter_20261030/adapter.py", "prefix_search_adapter")
STRATEGIES = ("model_only", "partial_prefix", "partial_prefix_aa")
ENCODINGS = ("quartic", "membership", "quadratic", "quadratic_aa")
EVENTS = ("sat_calls", "model_checks", "valid_model_checks", "invalid_model_checks",
          "accepted_models", "assignment_notifications", "fixed_notifications",
          "complete_assignment_notifications", "new_levels", "backtracks",
          "backtrack_scans", "assignments_removed", "decide_calls", "decision_scans",
          "propagate_calls", "has_clause_calls", "external_clauses", "projection_blocks",
          "pc_calls", "pc_unknown", "pc_capped_calls", "pc_attempted_rows",
          "pc_field_inverse_calls", "duplicate_prefix_visits", "pc_budget_skips",
          "partial_attempts", "model_attempts", "partial_refutations", "model_refutations",
          "leaf_fallbacks", "leaf_inverse_calls", "leaf_multiplier_entries",
          "prefix_scans", "max_assignments", "max_attempted_rows", "max_rank",
          "max_accepted_row_degree", "max_certificate_terms", "max_cache_entries")


def _compact(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def environment():
    native = Path(importlib.util.find_spec("pysolvers").origin)
    return {"backend": "Cadical195", "python_sat": importlib.metadata.version("python-sat"),
            "native_sha256": hashlib.sha256(native.read_bytes()).hexdigest(),
            "python": sys.version, "executable": sys.executable}


def model_bits(model, n):
    seen = {}
    for literal in model:
        if type(literal) is not int or literal == 0 or abs(literal) > n:
            raise ValueError("noncanonical native model")
        variable = abs(literal) - 1
        if variable in seen:
            raise ValueError("duplicate variable in native model")
        seen[variable] = int(literal > 0)
    if len(seen) != n:
        raise ValueError("native model is not a complete observed assignment")
    return sum(value << variable for variable, value in seen.items())


class PrefixPropagator(Propagator):
    def __init__(self, ring, polys, projected_bits, limits, strategy, prefix_depths, checkpoint=None):
        super().__init__()
        if strategy not in STRATEGIES or not 0 <= projected_bits <= ring.n:
            raise ValueError("invalid strategy or projection")
        for key in ("degree", "rows", "pc_calls"):
            if type(limits[key]) is not int or limits[key] < 0:
                raise ValueError("invalid PC limit")
        self.ring, self.polys, self.m = ring, polys, projected_bits
        self.limits, self.strategy = dict(limits), strategy
        self.depths = sorted(set(prefix_depths))
        if any(type(d) is not int or not 0 <= d <= ring.n for d in self.depths):
            raise ValueError("invalid prefix schedule")
        self.checkpoint = checkpoint
        self.level, self.assignments = 0, {}
        self.pending, self.learned, self.models, self.attempts = deque(), [], [], []
        self.cache = set()
        self.events = Counter({name: 0 for name in EVENTS})
        self.online = Counter({"coefficient_multiplications": 0, "coefficient_additions": 0})
        self.arithmetic = {name: Counter() for name in
                           ("restriction", "pc", "model_evaluation", "outer_model_evaluation")}
        self.status, self.stop_reason = "censored", "in_progress"
        self.native = None
        self.native_availability = {"availability": "unknown", "reason": "not allocated"}
        self.charge_stack = []
        self.charge_attempts = []
        self.secondary_errors = []

    def _charge(self, phase, function, *args):
        before = dict(self.ring.counts)
        frame = {"phase": phase, "children": Counter()}
        self.charge_stack.append(frame)
        error = None
        try:
            return function(*args)
        except BaseException as caught:
            error = caught
            raise
        finally:
            self.charge_stack.pop()
            try:
                inclusive = legacy.delta(before, self.ring.counts)
                exclusive = {key: inclusive.get(key, 0)-frame["children"].get(key, 0)
                             for key in set(inclusive) | set(frame["children"])}
                if any(value < 0 for value in exclusive.values()):
                    raise ValueError("nonmonotone or overlapping arithmetic counts")
                self.arithmetic.setdefault(phase, Counter()).update(exclusive)
                if self.charge_stack:
                    self.charge_stack[-1]["children"].update(inclusive)
                self.charge_attempts.append({"phase": phase, "status": "raised" if error else "returned",
                    "exception_type": type(error).__name__ if error else None,
                    "exclusive_arithmetic": exclusive})
            except BaseException as accounting_error:
                self.secondary_errors.append({"phase": "arithmetic_finalization", "type": type(accounting_error).__name__,
                                              "message": str(accounting_error)})
                if error is None:
                    raise

    def snapshot(self):
        arithmetic = Counter()
        for counts in self.arithmetic.values():
            arithmetic.update(counts)
        return {"status": self.status, "stop_reason": self.stop_reason,
                "models": list(self.models), "learned": list(self.learned),
                "attempts": list(self.attempts), "strategy": self.strategy,
                "prefix_depths": self.depths, "limits": self.limits,
                "costs": {"search_arithmetic": dict(arithmetic),
                          "search_events": dict(self.events),
                          "online_certificate_check": dict(self.online),
                          "sat_native": self.native,
                          "arithmetic_breakdown": {k: dict(v) for k, v in self.arithmetic.items()}},
                "certificate_bytes": len(_compact(self.learned)),
                "selected_options": {"is_lazy": False, "seed": 0, "lucky": 0,
                                     "phase": "negative", "decision": "lowest_unassigned_negative",
                                     "clause_delivery": "external_callback"},
                "pending_clauses": len(self.pending),
                "charge_attempts": list(self.charge_attempts),
                "secondary_errors": list(self.secondary_errors),
                "native_stat_availability": dict(self.native_availability)}

    def _save(self):
        if self.checkpoint:
            self.checkpoint(self.snapshot())

    def on_assignment(self, lit, fixed=False):
        index, value = abs(lit) - 1, int(lit > 0)
        if not 0 <= index < self.ring.n:
            raise ValueError("unobserved assignment")
        self.events["assignment_notifications"] += 1
        self.events["fixed_notifications"] += int(fixed)
        old = self.assignments.get(index)
        if old and old[0] != value:
            raise ValueError("assignment changed without backtracking")
        was_complete = len(self.assignments) == self.ring.n
        permanent = bool(fixed or (old and old[2]))
        self.assignments[index] = (value, 0 if permanent else self.level, permanent)
        self.events["complete_assignment_notifications"] += int(
            not was_complete and len(self.assignments) == self.ring.n)
        self.events["max_assignments"] = max(self.events["max_assignments"], len(self.assignments))

    def on_new_level(self):
        self.level += 1
        self.events["new_levels"] += 1

    def on_backtrack(self, to):
        if type(to) is not int or to < 0:
            raise ValueError("invalid backtrack level")
        self.events["backtracks"] += 1
        self.events["backtrack_scans"] += len(self.assignments)
        removed = [i for i, (_, level, fixed) in self.assignments.items() if not fixed and level > to]
        for i in removed:
            del self.assignments[i]
        self.events["assignments_removed"] += len(removed)
        self.level = to

    def decide(self):
        self.events["decide_calls"] += 1
        for i in range(self.ring.n):
            self.events["decision_scans"] += 1
            if i not in self.assignments:
                return -(i + 1)
        return 0

    def propagate(self):
        self.events["propagate_calls"] += 1
        return []

    def provide_reason(self, lit):
        raise AssertionError("no literal propagation is used")

    def _prefix(self):
        depth, bits = 0, 0
        while depth in self.assignments:
            self.events["prefix_scans"] += 1
            bits |= self.assignments[depth][0] << depth
            depth += 1
        return depth, bits

    def _residuals(self, depth, bits):
        assigned = {i: (bits >> i) & 1 for i in range(depth)}
        return self._charge("restriction", lambda: [self.ring.restrict(f, assigned) for f in self.polys])

    def _record_proof(self, depth, bits, residuals, certificate, trigger, metadata):
        ok, cost = legacy.certificate_check(self.ring.p, residuals, certificate)
        self.online.update(cost)
        if not ok:
            raise AssertionError("invalid proof; no clause emitted")
        prefix = bits & ((1 << depth) - 1)
        clause = legacy.block(prefix, depth)
        item = {"depth": depth, "prefix": prefix, "clause": clause, "certificate": certificate,
                "trigger": trigger, "assigned_count": len(self.assignments),
                "contiguous_depth": self._prefix()[0], **metadata}
        self.learned.append(item)
        self.pending.append((clause, "proof"))
        terms = sum(len(q) for q in certificate)
        self.events["max_certificate_terms"] = max(self.events["max_certificate_terms"], terms)
        self.events["partial_refutations" if trigger == "partial" else "model_refutations"] += 1
        self._save()

    def _try_prefix(self, depth, bits, trigger):
        key = (depth, bits & ((1 << depth) - 1))
        if key in self.cache:
            self.events["duplicate_prefix_visits"] += 1
            return False
        if self.events["pc_calls"] >= self.limits["pc_calls"]:
            self.events["pc_budget_skips"] += 1
            return False
        self.cache.add(key)
        self.events["max_cache_entries"] = max(self.events["max_cache_entries"], len(self.cache))
        residuals = self._residuals(depth, bits)
        answer = self._charge("pc", legacy.refute, self.ring, residuals,
                              self.limits["degree"], self.limits["rows"])
        self.events["pc_calls"] += 1
        self.events["partial_attempts" if trigger == "partial" else "model_attempts"] += 1
        self.events["pc_attempted_rows"] += answer["attempted_rows"]
        self.events["pc_field_inverse_calls"] += answer["rank"]
        self.events["pc_capped_calls"] += int(answer["resource_capped"])
        self.events["pc_unknown"] += int(answer["status"] == "unknown")
        for output, source in (("max_attempted_rows", "attempted_rows"), ("max_rank", "rank"),
                               ("max_accepted_row_degree", "max_accepted_row_degree")):
            self.events[output] = max(self.events[output], answer[source])
        metadata = {k: answer[k] for k in ("rank", "attempted_rows", "resource_capped",
                                           "max_accepted_row_degree", "max_multiplier_degree")}
        self.attempts.append({"depth": depth, "prefix": key[1], "trigger": trigger,
                              "status": answer["status"], "assigned_count": len(self.assignments),
                              "contiguous_depth": self._prefix()[0], **metadata})
        if answer["status"] == "refuted":
            self._record_proof(depth, bits, residuals, answer["certificate"], trigger, metadata)
            return True
        return False

    def _fallback(self, bits):
        residuals = self._residuals(self.ring.n, bits)
        for index, residual in enumerate(residuals):
            if residual:
                if set(residual) != {0}:
                    raise AssertionError("full restriction was not constant")
                certificate = [{} for _ in residuals]
                certificate[index] = {0: pow(residual[0], -1, self.ring.p)}
                self.events["leaf_fallbacks"] += 1
                self.events["leaf_inverse_calls"] += 1
                self.events["leaf_multiplier_entries"] += 1
                self._record_proof(self.ring.n, bits, residuals, certificate, "leaf_fallback", {})
                return
        raise AssertionError("invalid-model fallback received a root")

    def _reject(self, bits):
        if not self.pending or legacy.clause_true(self.pending[0][0], bits):
            raise AssertionError("rejected model has no genuine excluding clause")
        return False

    def check_model(self, model):
        bits = model_bits(model, self.ring.n)
        self.events["model_checks"] += 1
        values = self._charge("model_evaluation", lambda: [self.ring.eval(f, bits) for f in self.polys])
        if not any(values):
            self.events["valid_model_checks"] += 1
            return True
        self.events["invalid_model_checks"] += 1
        if self.pending:
            return self._reject(bits)
        for depth in self.depths:
            if self._try_prefix(depth, bits, "model"):
                return self._reject(bits)
        self._fallback(bits)
        return self._reject(bits)

    def has_clause(self):
        self.events["has_clause_calls"] += 1
        if self.pending:
            return True
        # A fully assigned trail before check_model is not partial pruning.
        if self.strategy != "model_only" and len(self.assignments) < self.ring.n:
            depth, bits = self._prefix()
            for eligible in self.depths:
                if eligible <= depth and eligible < self.ring.n:
                    if self._try_prefix(eligible, bits, "partial"):
                        return True
        return False

    def add_clause(self):
        if not self.pending:
            raise AssertionError("add_clause called without a pending clause")
        clause, kind = self.pending.popleft()
        self.events["external_clauses"] += 1
        self.events["projection_blocks"] += int(kind == "projection")
        return clause

    def accept(self, bits):
        values = self._charge("outer_model_evaluation", lambda: [self.ring.eval(f, bits) for f in self.polys])
        if any(values):
            raise AssertionError("native solver returned an invalid arithmetic model")
        mask = (1 << self.m) - 1
        if any((old & mask) == (bits & mask) for old in self.models):
            raise AssertionError("duplicate projected model")
        self.models.append(bits)
        self.events["accepted_models"] += 1
        self.pending.append((legacy.block(bits, self.m), "projection"))
        self._save()


def solve(ring, polys, domain, projected_bits, limits, strategy, prefix_depths, checkpoint=None,
          *, attempt=None, solver_factory=None):
    """Same search/clauses; explicit cleanup retains primary exception identity.

    solver_factory is a deterministic failure-control seam, never an oracle.
    Generic callers must supply integer caps; legacy alias is intentionally
    unavailable in this versioned full-chart interface.
    """
    limits = dict(limits)
    for name in ("outer_calls", "native_conflicts_per_call", "native_decisions_per_call"):
        if type(limits[name]) is not int or limits[name] <= 0:
            raise ValueError("positive explicit native/enumeration limit required")
    prop = PrefixPropagator(ring, polys, projected_bits, limits, strategy, prefix_depths, checkpoint)
    sat = None; primary = None; primary_traceback = None; answer = None
    def capture(error, phase):
        nonlocal primary, primary_traceback
        if primary is None:
            primary, primary_traceback = error, error.__traceback__
            if attempt:
                attempt.failure(error, phase)
        else:
            prop.secondary_errors.append({"phase": phase, "type": type(error).__name__, "message": str(error)})
            if attempt:
                attempt.secondary(error, phase)
    def statistics():
        if sat is None:
            return
        try:
            stats = sat.accum_stats()
            if type(stats) is not dict or any(type(v) is not int or v < 0 for v in stats.values()):
                raise ValueError("native statistics schema")
            prop.native = stats
            fields = {key: ({"availability": "available", "value": stats[key]} if key in stats else
                            {"availability": "unknown", "reason": "native accessor omitted metric"})
                      for key in ("conflicts", "decisions", "propagations", "restarts")}
            prop.native_availability = {"availability": "available" if all(v["availability"] == "available" for v in fields.values()) else "partial",
                                        "captured_before_teardown": True, "metrics": fields}
            if attempt:
                attempt.state["native_statistics"] = {**prop.native_availability, "values": dict(stats)}
        except BaseException as error:
            prop.native_availability = {"availability": "unknown", "reason": type(error).__name__+": "+str(error),
                                       "last_observed": prop.native}
            if attempt:
                attempt.state["native_statistics"] = dict(prop.native_availability)
            capture(error, "native_statistics")
    try:
        prop._save()
        sat = (solver_factory or Cadical195)(bootstrap_with=domain + [[i + 1, -(i + 1)] for i in range(ring.n)])
        sat.configure({"seed": 0})
        sat.set_phases([-(i + 1) for i in range(ring.n)])
        sat.connect_propagator(prop)
        for i in range(ring.n):
            sat.observe(i + 1)
        prop.stop_reason = "outer_call_limit"
        for _ in range(limits["outer_calls"]):
            sat.conf_budget(limits["native_conflicts_per_call"])
            sat.dec_budget(limits["native_decisions_per_call"])
            prop.events["sat_calls"] += 1
            result = sat.solve_limited()
            statistics()
            if primary is not None:
                raise primary.with_traceback(primary_traceback)
            if result is False:
                prop.status, prop.stop_reason = "complete", "native_unsat"
                break
            if result is None:
                prop.stop_reason = "native_limit"
                break
            if result is not True:
                raise ValueError("unexpected native result")
            bits = model_bits(sat.get_model(), ring.n)
            if not all(legacy.clause_true(c, bits) for c in domain):
                raise AssertionError("native model violates the declared auxiliary domain")
            prop.accept(bits)
    except BaseException as error:
        # The same error may have been captured by statistics().
        if primary is not error:
            capture(error, "solve")
    finally:
        statistics()  # always while native object is alive
        if sat is not None:
            try:
                sat.delete()
            except BaseException as error:
                capture(error, "teardown")
        try:
            answer = prop.snapshot()
            if primary is not None:
                answer["attempt_error"] = {"type": type(primary).__name__, "message": str(primary)}
                answer["cost_coverage"] = {"complete": False, "reason": "interrupted work; available counters retained"}
            answer["environment"] = environment()
            answer["solver_factory_used"] = solver_factory is not None
            answer["solver_origin"] = "injected_factory_or_wrapper" if solver_factory is not None else "native_Cadical195"
            if checkpoint:
                checkpoint(answer)
            if attempt:
                attempt.checkpoint(answer, event="engine_final")
        except BaseException as error:
            capture(error, "final_checkpoint_or_environment")
    if primary is not None:
        try:
            primary.partial_transcript = answer if answer is not None else prop.snapshot()
            primary.secondary_errors = list(prop.secondary_errors)
        except BaseException as error:
            if attempt:
                attempt.secondary(error, "attach_partial_transcript")
        raise primary.with_traceback(primary_traceback)
    return answer


def run_cell(cell, encoding, strategy, limits, checkpoint=None):
    if encoding not in ENCODINGS:
        raise ValueError("unknown encoding")
    ring, polys, domain = legacy.build(cell, encoding)
    construction = dict(ring.counts)
    answer = solve(ring, polys, domain, 2 * cell["s"], limits, strategy,
                   sorted(set((0, cell["s"], 2 * cell["s"], ring.n))), checkpoint)
    checked = adapter.verify_encoding_search(cell, encoding, answer)
    phases = {name: answer["costs"][name] for name in
              ("search_arithmetic", "search_events", "online_certificate_check", "sat_native")}
    phases.update(construction=construction,
                  offline_verification={k: v for k, v in checked["costs"].items()
                                        if k != "witness_reconstruction_and_check"},
                  reconstruction=checked["costs"]["witness_reconstruction_and_check"])
    result = {name: checked[name] for name in ("declared_status", "projected_models", "cover_complete",
                                               "projected_model_set_complete")}
    result["stop_reason"] = answer["stop_reason"]
    return {"answer": answer, "result": result, "phases": phases,
            "coordinate_pairs": checked["coordinate_pairs"], "witnesses": checked["witnesses"]}
