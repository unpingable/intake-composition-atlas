#!/usr/bin/env python3
"""Intake Composition Atlas — doctrine linter.

Validates case + receipt YAML against schema.yaml and the project's hard rules.
Every rule here is the machine-checkable form of a doctrine statement in
METHODOLOGY.md. The linter is the reason this project is a typed graph and not a
corkboard: an edge that cannot cite its basis does not ship.

Usage:
    python tools/lint.py                      # lint cases/ + receipts/
    python tools/lint.py --root fixtures/pass # lint a fixture dir
    python tools/lint.py --root fixtures/fail/no-receipt.yaml --expect EDGE_NO_RECEIPT

Exit code 0 iff there are no errors. Warnings never fail the build.
With --expect RULE, exit 0 iff at least one error with that rule code was raised
(used by test_lint.py to assert failure fixtures fail for the *right* reason).
"""
import argparse
import datetime as _dt
import glob
import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("error: PyYAML required (pip install -r tools/requirements.txt)\n")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# --- vocabulary mirrored from schema.yaml (kept in sync; schema is the prose source) ---
NODE_TYPES = {
    "portal", "instrument", "form", "field_class", "system_of_record",
    "agency", "operator", "decision_surface", "external_consumer",
}
EDGE_TYPES = {
    "collects", "authorizes", "feeds", "operates", "shares_with",
    "matches_against", "enables_inference", "consumed_by",
}
CLAIM_TYPES = {"documented", "authorized", "inferred", "speculative"}
# Receipt kinds that can support a `documented` flow edge. A statute proves only
# its own text, never that a flow occurs — so it is NOT in this set.
DOCUMENTED_KINDS = {
    "cma", "sorn", "pia", "omb_icr", "contract_award", "fedramp",
    "observed_artifact", "press_or_agency_statement",
}
# An edge basis drawn ONLY from these kinds asserts permission, not occurrence.
AUTHORIZED_ONLY_KINDS = {"eo", "statute"}
ALL_RECEIPT_KINDS = DOCUMENTED_KINDS | AUTHORIZED_ONLY_KINDS
CONTESTATION_REQUIRED_ON = {"shares_with", "matches_against", "consumed_by"}
SPECULATIVE_MAX_PER_CASE = 2
STALENESS_DAYS = {"observed_artifact": 90, "_default": 365}

# Today is injected (Date.now equivalent), defaults to schema's current date for
# determinism in CI; overridable via --today.
DEFAULT_TODAY = "2026-06-12"


class Report:
    def __init__(self):
        self.errors = []    # (rule_code, location, message)
        self.warnings = []  # (rule_code, location, message)

    def error(self, code, loc, msg):
        self.errors.append((code, loc, msg))

    def warn(self, code, loc, msg):
        self.warnings.append((code, loc, msg))

    def print(self):
        for code, loc, msg in self.warnings:
            print(f"  warn  [{code}] {loc}: {msg}")
        for code, loc, msg in self.errors:
            print(f"  ERROR [{code}] {loc}: {msg}")
        n_e, n_w = len(self.errors), len(self.warnings)
        print(f"\n{n_e} error(s), {n_w} warning(s).")
        return n_e == 0


def _load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(fh)


def load_receipts(root):
    """Return {id: receipt}. Receipts live in receipts/ unless root is a fixture."""
    receipts = {}
    search = []
    if os.path.isdir(os.path.join(root, "receipts")):
        search += glob.glob(os.path.join(root, "receipts", "*.yaml"))
    # fixtures embed receipts inline in the case file; handled in load_cases.
    for path in sorted(search):
        rec = _load_yaml(path)
        if isinstance(rec, dict) and "id" in rec:
            receipts[rec["id"]] = rec
    return receipts


def load_cases(root):
    """Return list of (path, case_dict). `root` may be a dir or a single file."""
    cases = []
    if os.path.isfile(root):
        cases.append((root, _load_yaml(root)))
        return cases
    case_dir = os.path.join(root, "cases") if os.path.isdir(os.path.join(root, "cases")) else root
    for path in sorted(glob.glob(os.path.join(case_dir, "*.yaml"))):
        cases.append((path, _load_yaml(path)))
    return cases


def parse_date(s):
    if isinstance(s, _dt.date):
        return s
    return _dt.date.fromisoformat(str(s))


def lint(root, today, report):
    today = parse_date(today)
    receipts = load_receipts(root)
    cases = load_cases(root)

    for path, case in cases:
        loc0 = os.path.basename(path)
        if not isinstance(case, dict):
            report.error("CASE_MALFORMED", loc0, "case file is not a mapping")
            continue

        # Receipts may be filed centrally (receipts/) or inline (fixtures).
        local_receipts = dict(receipts)
        for rec in case.get("receipts_inline", []) or []:
            if isinstance(rec, dict) and "id" in rec:
                local_receipts[rec["id"]] = rec

        nodes = case.get("nodes", []) or []
        node_ids = set()
        for n in nodes:
            nid = n.get("id")
            if not nid:
                report.error("NODE_NO_ID", loc0, f"node missing id: {n}")
                continue
            if n.get("type") not in NODE_TYPES:
                report.error("NODE_BAD_TYPE", f"{loc0}:{nid}",
                             f"unknown node type {n.get('type')!r}")
            node_ids.add(nid)

        edges = list(case.get("edges", []) or []) + list(case.get("inference_layer", []) or [])
        edge_ids = {e.get("id") for e in edges if isinstance(e, dict)}
        spec_count = 0

        # Validate each receipt referenced — and freshness.
        for rid, rec in local_receipts.items():
            rloc = f"{loc0}:{rid}"
            if rec.get("kind") not in ALL_RECEIPT_KINDS:
                report.error("RECEIPT_BAD_KIND", rloc, f"unknown receipt kind {rec.get('kind')!r}")
            if not rec.get("retrieved"):
                report.error("RECEIPT_NO_DATE", rloc, "receipt missing `retrieved` date")
            else:
                try:
                    age = (today - parse_date(rec["retrieved"])).days
                    limit = STALENESS_DAYS.get(rec.get("kind"), STALENESS_DAYS["_default"])
                    if age > limit:
                        report.warn("RECEIPT_STALE", rloc,
                                    f"retrieved {age}d ago (> {limit}d window for {rec.get('kind')})")
                except ValueError:
                    report.error("RECEIPT_BAD_DATE", rloc, f"unparseable date {rec['retrieved']!r}")

        for e in edges:
            eid = e.get("id", "<no-id>")
            eloc = f"{loc0}:{eid}"
            etype = e.get("type")
            claim = e.get("claim")

            if etype not in EDGE_TYPES:
                report.error("EDGE_BAD_TYPE", eloc, f"unknown edge type {etype!r}")
            if claim not in CLAIM_TYPES:
                report.error("EDGE_BAD_CLAIM", eloc, f"unknown claim {claim!r}")

            # Referential integrity. `authorizes` edges may point to an edge id.
            for end in ("from", "to"):
                ref = e.get(end)
                ok = ref in node_ids or (etype == "authorizes" and ref in edge_ids)
                if not ok:
                    report.error("EDGE_DANGLING_REF", eloc,
                                 f"`{end}` -> {ref!r} resolves to no node{' or edge' if etype=='authorizes' else ''}")

            # RULE: no edge without a receipt; receipts must resolve.
            recs = e.get("receipts") or []
            if not recs:
                report.error("EDGE_NO_RECEIPT", eloc, "edge has no receipts (>=1 required)")
            for rid in recs:
                if rid not in local_receipts:
                    report.error("EDGE_RECEIPT_UNRESOLVED", eloc, f"receipt {rid!r} not found")

            kinds = {local_receipts[r]["kind"] for r in recs if r in local_receipts}

            # RULE signed_is_not_witnessed: a `documented` edge needs >=1 receipt of a
            # documented-eligible kind. An edge whose basis is ONLY eo/statute is a
            # permission, not an observation — force downgrade to `authorized`.
            if claim == "documented":
                if kinds and not (kinds & DOCUMENTED_KINDS):
                    report.error("DOCUMENTED_NEEDS_WITNESS", eloc,
                                 f"claim=documented but receipts are only {sorted(kinds)} "
                                 f"(EO/statute authorize a flow, they do not witness it). "
                                 f"Downgrade to claim: authorized.")

            # RULE inferred: derivation non-empty, parents exist, depth-1 (no inferred parent).
            if claim == "inferred":
                deriv = e.get("derivation") or []
                if not deriv:
                    report.error("INFERRED_NO_DERIVATION", eloc,
                                 "claim=inferred requires non-empty derivation (parent edge ids)")
                for pid in deriv:
                    parent = next((x for x in edges if x.get("id") == pid), None)
                    if parent is None:
                        report.error("INFERRED_PARENT_MISSING", eloc,
                                     f"derivation parent {pid!r} not found in case")
                    elif parent.get("claim") == "inferred":
                        report.error("INFERRED_TOWER", eloc,
                                     f"derivation parent {pid!r} is itself inferred "
                                     f"(no inference-on-inference; depth-1 cap)")
            elif etype == "enables_inference":
                report.error("ENABLES_INFERENCE_CLAIM", eloc,
                             "enables_inference edges must have claim: inferred")

            # RULE speculative cap.
            if claim == "speculative":
                spec_count += 1

            # RULE contestation block on sharing/consuming edges.
            if etype in CONTESTATION_REQUIRED_ON:
                c = e.get("contestation")
                if not isinstance(c, dict) or "notice" not in c or "appeal" not in c:
                    report.error("CONTESTATION_MISSING", eloc,
                                 f"{etype} edge requires contestation block with notice + appeal")

        if spec_count > SPECULATIVE_MAX_PER_CASE:
            report.error("SPECULATIVE_OVER_CAP", loc0,
                         f"{spec_count} speculative edges (max {SPECULATIVE_MAX_PER_CASE} per case)")

    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description="Intake Composition Atlas doctrine linter")
    ap.add_argument("--root", default=REPO,
                    help="repo root, a directory of cases, or a single case file")
    ap.add_argument("--today", default=DEFAULT_TODAY, help="date for staleness checks (YYYY-MM-DD)")
    ap.add_argument("--expect", default=None,
                    help="assert at least one error with this rule code (for failure fixtures)")
    args = ap.parse_args(argv)

    report = Report()
    lint(args.root, args.today, report)
    ok = report.print()

    if args.expect:
        codes = {c for c, _, _ in report.errors}
        if args.expect in codes:
            print(f"OK: expected failure rule {args.expect} was raised.")
            return 0
        print(f"FAIL: expected failure rule {args.expect} NOT raised. Got: {sorted(codes)}")
        return 1

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
