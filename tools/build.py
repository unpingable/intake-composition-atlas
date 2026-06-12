#!/usr/bin/env python3
"""Intake Composition Atlas — build cases + receipts into site JSON.

Reads cases/*.yaml + receipts/*.yaml, validates via lint.py (build refuses on any
lint error), and emits cytoscape.js elements for the graph view:

    docs/data/graph.json        # {nodes: [...], edges: [...]} cytoscape elements
    docs/data/cases/<id>.json   # per-case slice (for future per-case pages)

Doctrine:
  - `speculative` edges are EXCLUDED from default output (kept behind an explicit
    flag in the data so the site can gate them). They never appear in graph.json
    unless --include-speculative is passed.
  - Build is proposal-only: it writes data files, never commits.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import lint as linter  # noqa: E402

try:
    import yaml
except ImportError:
    sys.stderr.write("error: PyYAML required (pip install -r tools/requirements.txt)\n")
    sys.exit(2)


def load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(fh)


# --- cartographic intent ------------------------------------------------------
# Layout encodes WHERE a claim sits in the machine (semantic stage); edge styling
# encodes HOW strong the claim is. Lanes are the left-to-right stages of the flow.
LANES = [
    ("authority",  "Authority"),
    ("intake",     "Intake"),
    ("collection", "Collection"),
    ("data",       "Collected data"),
    ("custody",    "Custody"),
    ("inference",  "Composition / inference"),
    ("decision",   "Decision surface"),
    ("external",   "External power"),
]
LANE_INDEX = {k: i for i, (k, _) in enumerate(LANES)}
TYPE_LANE = {
    "instrument": "authority", "operator": "intake", "portal": "intake",
    "form": "collection", "field_class": "data", "system_of_record": "custody",
    "agency": "custody", "decision_surface": "decision", "external_consumer": "external",
}
# Edge "role" separates DAG plumbing from annotations so they don't compete for the
# same visual grammar. claim (documented/authorized/inferred) is orthogonal.
EDGE_ROLE = {
    "collects": "flow", "hosts": "flow", "feeds": "flow", "operates": "flow",
    "shares_with": "flow", "matches_against": "flow", "consumed_by": "flow",
    "authorizes": "authorization", "enables_inference": "inference",
}


def short_label(n):
    if n.get("short_label"):
        return n["short_label"]
    lab = n.get("label", n["id"]).split("(")[0].split("—")[0].strip()
    words = lab.split()
    return lab if len(lab) <= 26 else " ".join(words[:3]) + "…"


def collect(root):
    receipts = linter.load_receipts(root)
    cases = []
    case_dir = os.path.join(root, "cases")
    for path in sorted(glob.glob(os.path.join(case_dir, "*.yaml"))):
        cases.append(load_yaml(path))
    return receipts, cases


def to_elements(cases, receipts, include_speculative):
    nodes, edges = [], []
    seen_nodes = set()
    node_label = {}      # id -> short label, for annotations
    edge_by_emitted_id = {}  # id -> emitted edge data, for the authorization annotation pass
    for case in cases:
        cid = case.get("case_id")
        for n in case.get("nodes", []) or []:
            if n["id"] in seen_nodes:
                continue
            seen_nodes.add(n["id"])
            lane = n.get("lane") or TYPE_LANE.get(n.get("type"), "data")
            sl = short_label(n)
            node_label[n["id"]] = sl
            nodes.append({"data": {
                "id": n["id"], "type": n.get("type"),
                "label": n.get("label", n["id"]), "short_label": sl,
                "lane": lane, "rank": LANE_INDEX.get(lane, 3),
                "case": cid,
            }})
        all_edges = list(case.get("edges", []) or []) + list(case.get("inference_layer", []) or [])
        case_node_ids = {n["id"] for n in case.get("nodes", []) or []}
        edge_by_id = {e["id"]: e for e in all_edges if isinstance(e, dict) and "id" in e}

        def resolve(ref, which):
            # An `authorizes` edge may target/source an EDGE id (instrument authorizes a
            # specific flow). cytoscape can only draw node->node, so redirect to that
            # edge's endpoint node for rendering; the real relationship is kept in
            # `authorizes_edge` so the panel can show it.
            if ref in case_node_ids:
                return ref, None
            target_edge = edge_by_id.get(ref)
            if target_edge is not None:
                endpoint = target_edge.get("to") if which == "target" else target_edge.get("from")
                return endpoint, ref
            return ref, None  # dangling — linter would already have flagged it

        for e in all_edges:
            if e.get("claim") == "speculative" and not include_speculative:
                continue
            src, src_edge = resolve(e.get("from"), "source")
            tgt, tgt_edge = resolve(e.get("to"), "target")
            data = {
                "id": e["id"], "source": src, "target": tgt,
                "type": e.get("type"), "claim": e.get("claim"), "case": cid,
                "role": EDGE_ROLE.get(e.get("type"), "flow"),
                "receipts": [receipts.get(r, {"id": r}) for r in (e.get("receipts") or [])],
                "derivation": e.get("derivation", []),
            }
            authorizes_edge = src_edge or tgt_edge
            if authorizes_edge:
                data["authorizes_edge"] = authorizes_edge
            if "contestation" in e:
                data["contestation"] = e["contestation"]
            # cytoscape `classes` keys the stylesheet off claim AND role.
            edges.append({"data": data, "classes": f"{e.get('claim', '')} {data['role']}".strip()})
            edge_by_emitted_id[e["id"]] = data

        # Annotation pass: an `authorizes` edge that targets a specific FLOW edge is
        # rendered faintly, but we also stamp `authorized_by` on that flow edge so the
        # panel shows "Authorized by <instrument>" instead of relying on a spaghetti arrow.
        for e in all_edges:
            if e.get("type") == "authorizes":
                tgt_ref = e.get("to")
                if tgt_ref in edge_by_id and tgt_ref in edge_by_emitted_id:
                    src_node = e.get("from")
                    edge_by_emitted_id[tgt_ref]["authorized_by"] = src_node
                    edge_by_emitted_id[tgt_ref]["authorized_by_label"] = node_label.get(src_node, src_node)
    return {"nodes": nodes, "edges": edges}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build site JSON from cases + receipts")
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--out", default=os.path.join(REPO, "docs", "data"))
    ap.add_argument("--include-speculative", action="store_true")
    ap.add_argument("--today", default=linter.DEFAULT_TODAY)
    args = ap.parse_args(argv)

    # Refuse to build on lint errors.
    report = linter.Report()
    linter.lint(args.root, args.today, report)
    if report.errors:
        report.print()
        sys.stderr.write("build refused: fix lint errors first.\n")
        return 1

    receipts, cases = collect(args.root)
    elements = to_elements(cases, receipts, args.include_speculative)
    # Case-level editorial metadata (far-view framing: headline / dek / nut graf).
    # Reader-facing copy leads; the doctrine lives in the receipts drawer.
    elements["cases"] = [{
        "case_id": c.get("case_id"), "title": c.get("title"),
        "headline": c.get("headline"), "dek": c.get("dek"),
        "why": c.get("why"), "summary": c.get("summary"), "status": c.get("status"),
    } for c in cases]

    os.makedirs(args.out, exist_ok=True)
    os.makedirs(os.path.join(args.out, "cases"), exist_ok=True)
    with open(os.path.join(args.out, "graph.json"), "w") as fh:
        json.dump(elements, fh, indent=2, default=str)  # default=str: YAML dates -> ISO strings

    for case in cases:
        cid = case.get("case_id")
        slice_ = to_elements([case], receipts, args.include_speculative)
        with open(os.path.join(args.out, "cases", f"{cid}.json"), "w") as fh:
            json.dump(slice_, fh, indent=2, default=str)

    n_spec = sum(
        1 for c in cases
        for e in (list(c.get("edges", []) or []) + list(c.get("inference_layer", []) or []))
        if e.get("claim") == "speculative"
    )
    print(f"built {len(elements['nodes'])} nodes, {len(elements['edges'])} edges "
          f"from {len(cases)} case(s) -> {args.out}/graph.json")
    if n_spec and not args.include_speculative:
        print(f"note: {n_spec} speculative edge(s) excluded from default output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
