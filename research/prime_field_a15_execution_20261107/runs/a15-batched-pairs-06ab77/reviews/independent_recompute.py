#!/usr/bin/env python3
"""Read-only A15 raw-row recomputation; no producer modules are imported."""

import collections
import gzip
import hashlib
import itertools
import json
import sys
from pathlib import Path

NONCE = "51c186646fe2347a240150f010034e38"
RUN = Path(__file__).resolve().parents[1]
STUDY = RUN.parents[1]


def lines(path):
    with gzip.open(path, "rt") as stream:
        for line in stream:
            yield json.loads(line)


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def point_add(left, right, prime, a):
    if left is None:
        return right
    if right is None:
        return left
    x, y = left
    u, v = right
    if x == u and (y + v) % prime == 0:
        return None
    slope = ((3 * x * x + a) * pow(2 * y, -1, prime) if x == u
             else (v - y) * pow(u - x, -1, prime)) % prime
    next_x = (slope * slope - x - u) % prime
    return next_x, (slope * (x - next_x) - y) % prime


def check_sample(input_row, record):
    fixture = input_row["fixture"]
    prime, a, b, order = (int(fixture[k]) for k in ("p", "a", "b", "r"))
    points = input_row["geometry"]["points"]
    def on_curve(point):
        x, y = point
        return (y * y - x * x * x - a * x - b) % prime == 0
    assert all(on_curve(p) for p in points)
    assert on_curve(record["point"])
    checked = 0
    for row in record["rows"]:
        result = None
        coeff = [0] * len(points)
        assert len(row["triple"]) == len(row["signs"]) == 3
        for index, sign in zip(row["triple"], row["signs"]):
            assert 0 <= index < len(points) and sign in (-1, 1)
            x, y = points[index]
            result = point_add(result, (x, y if sign == 1 else (-y) % prime), prime, a)
            coeff[index] = (coeff[index] + sign) % order
        assert result == tuple(record["point"])
        assert coeff == row["coefficients"]
        checked += 1
    return checked


def oracle_for_queries(source):
    """Enumerate every distinct-index signed triple, retaining queried sums only."""
    prime = int(source["fixture"]["p"])
    a = int(source["fixture"]["a"])
    points = source["geometry"]["points"]
    queried = {tuple(q["point"]) for q in source["queries"]}
    hits = collections.defaultdict(set)
    count = 0
    for triple in itertools.combinations(range(len(points)), 3):
        for signs in itertools.product((-1, 1), repeat=3):
            result = None
            for index, sign in zip(triple, signs):
                x, y = points[index]
                result = point_add(result, (x, y if sign == 1 else (-y) % prime), prime, a)
            if result in queried:
                hits[result].add((triple, signs))
            count += 1
    return hits, count


def main():
    metrics = json.loads((RUN / "metrics.json").read_text())
    rows = {(row["table"], row["method"]): row for row in metrics["rows"]}
    tables = sorted(p.name for p in (RUN / "raw").iterdir() if p.is_dir())
    assert len(tables) == 16 and len(rows) == 32
    all_counters = collections.Counter()
    total_queries = total_builds = total_checks = all_rows_checked = oracle_triples = 0
    hit_queries = miss_queries = 0
    sample_table = tables[int(hashlib.sha256((NONCE + "/table").encode()).hexdigest(), 16) % len(tables)]
    sample_query = None
    sample_input = None
    for table in tables:
        source = json.loads((STUDY / f"{table}.input.json").read_text())
        expected = source["queries"]
        oracle, triples = oracle_for_queries(source)
        oracle_triples += triples
        built, completed = {}, {}
        seen = collections.defaultdict(dict)
        query_rows = collections.Counter()
        for output in lines(RUN / "raw" / table / "outputs.jsonl.gz"):
            kind, method = output["kind"], output.get("method")
            if kind == "built":
                assert method not in built
                built[method] = output
                total_builds += 1
            elif kind == "method_complete":
                assert method not in completed
                completed[method] = output
            elif kind == "query":
                index = output["query_index"]
                assert 0 <= index < len(expected) and index not in seen[method]
                record = output["record"]
                digest = canonical_hash(record)
                assert digest == expected[index]["expected_record_sha256"]
                assert record["point"] == expected[index]["point"]
                if method == "scalar":
                    all_rows_checked += check_sample(source, record)
                    if record["rows"]:
                        hit_queries += 1
                    else:
                        miss_queries += 1
                    observed = [(tuple(row["triple"]), tuple(row["signs"])) for row in record["rows"]]
                    assert len(observed) == len(set(observed))
                    assert set(observed) == oracle[tuple(record["point"])]
                seen[method][index] = digest
                query_rows[method] += len(record["rows"])
                if table == sample_table and method == "scalar":
                    if sample_query is None:
                        sample_query = int(hashlib.sha256((NONCE + "/query").encode()).hexdigest(), 16) % len(expected)
                    if index == sample_query:
                        sample_input, sample_record = source, record
                total_queries += 1
            else:
                raise AssertionError(f"unknown output kind {kind}")
        assert set(built) == set(completed) == set(seen) == {"scalar", "batched"}
        assert built["scalar"]["pairs_sha256"] == built["batched"]["pairs_sha256"]
        assert seen["scalar"] == seen["batched"]
        assert set(seen["scalar"]) == set(range(len(expected)))
        for method in ("scalar", "batched"):
            row = rows[(table, method)]
            assert row["queries"] == row["verified_queries"] == len(expected)
            assert row["rows"] == completed[method]["rows"]
            assert row["rows"] == query_rows[method]
            assert row["build"]["pairs_sha256"] == built[method]["pairs_sha256"]
            assert completed[method]["queries"] == len(expected)
        checked_pairs = set()
        checked_queries = collections.defaultdict(set)
        oracle_count = None
        for check in lines(RUN / "raw" / table / "checks.jsonl.gz"):
            if check["kind"] == "pair_check":
                assert check["verification"]["checked"] is True
                assert check["verification"]["pairs_sha256"] == built[check["method"]]["pairs_sha256"]
                checked_pairs.add(check["method"])
            elif check["kind"] == "query_check":
                method, index = check["method"], check["query_index"]
                assert check["verification"]["checked"] is True
                assert check["verification"]["record_sha256"] == seen[method][index]
                checked_queries[method].add(index)
            elif check["kind"] == "complete_oracle_construction":
                oracle_count = check["signed_triple_records"]
            else:
                raise AssertionError(f"unknown check kind {check['kind']}")
            total_checks += 1
        assert oracle_count == triples
        assert checked_pairs == {"scalar", "batched"}
        assert all(checked_queries[m] == set(range(len(expected))) for m in checked_pairs)
        for event in lines(RUN / "raw" / table / "events.jsonl.gz"):
            if event["kind"] == "affine_phase":
                assert event["phase"]["wall_valid"] is False
                all_counters.update(event["phase"]["counters"])
    assert total_builds == 32 and total_queries == 17920
    assert all_counters == collections.Counter(metrics["physical_counters"])
    assert sample_input is not None
    uniform_rows = len(sample_record["rows"])
    hit_query = sample_query
    if uniform_rows == 0:
        # The uniform nonce draw was a miss. The next hit in cyclic query order
        # is fixed by that draw, so the arithmetic spot-check is reproducible.
        candidates = []
        for output in lines(RUN / "raw" / sample_table / "outputs.jsonl.gz"):
            if output["kind"] == "query" and output["method"] == "scalar" and output["record"]["rows"]:
                index = output["query_index"]
                distance = (index - sample_query) % len(sample_input["queries"])
                candidates.append((distance, index, output["record"]))
        assert candidates
        _, hit_query, sample_record = min(candidates, key=lambda x: x[0])
    sample_rows = check_sample(sample_input, sample_record)
    assert sample_rows > 0
    mutated = json.loads(json.dumps(sample_record))
    mutated["rows"][0]["signs"][0] *= -1
    try:
        check_sample(sample_input, mutated)
    except AssertionError:
        mutation_rejected = True
    else:
        raise AssertionError("changed-sign control escaped independent checker")
    print(json.dumps({"nonce": NONCE, "tables": len(tables), "builds": total_builds,
                      "queries": total_queries, "checks": total_checks,
                      "all_output_hashes_match_inputs": True,
                      "scalar_batched_records_match": True,
                      "phase_counters_match_metrics": True,
                      "all_reported_rows_checked_by_independent_group_law": all_rows_checked,
                      "all_query_relation_sets_match_independent_oracle": True,
                      "independent_oracle_signed_triples": oracle_triples,
                      "scalar_hit_queries": hit_queries, "scalar_miss_queries": miss_queries,
                      "changed_sign_control_rejected": mutation_rejected,
                      "sample_table": sample_table, "uniform_sample_query": sample_query,
                      "uniform_sample_rows": uniform_rows, "cyclic_next_hit_query": hit_query,
                      "sample_rows_checked_by_independent_group_law": sample_rows,
                      "physical_counters": dict(sorted(all_counters.items()))}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
