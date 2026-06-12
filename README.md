# Intake Composition Atlas

**A typed, receipt-backed map of how narrow federal intake surfaces compose into a
broader identity and decision graph — with every edge labeled by what kind of
claim it is.**

This is not a theory of surveillance. It is not a privacy essay. It is a queryable
graph where every edge carries exactly one **claim type** and at least one
**receipt** pointing at a public record. An edge that cannot cite its basis does
not ship.

Sibling to the [Grid Dependency Atlas](https://github.com/unpingable/grid-dependency-atlas).
Same thesis, new substrate: populations exposed to inferences and decisions
composed **outside their effective contestation surface**. The grid atlas asks who
controls the transformer you cannot vote on; this atlas asks who acts on the join
you cannot see.

## Live site

_(GitHub Pages — published from `docs/`.)_

## Claim types

The spine of the project. Every edge is exactly one:

| Claim type | Asserts | Required receipt |
|---|---|---|
| `documented` | the flow/collection **exists** | SORN, CMA, PIA, OMB ICR, contract award, FedRAMP, privacy policy, observed page artifact — with URL + retrieval date |
| `authorized` | a legal instrument **permits** it; no evidence it occurs | EO, statute, routine-use clause — citation to the authorizing text |
| `inferred` | composition makes it **derivable** | a derivation: which parent edges compose to yield it |
| `speculative` | plausible under incentive analysis only | marked, excluded from the default view, capped per case |

The default view shows `documented` edges only. Toggling on `authorized`, then
`inferred`, visibly inflates the graph. **That delta is the finding** — what is
proven, what is permitted, what is possible.

Key rule: **`signed_is_not_witnessed`** — an EO authorizing data sharing is an
`authorized` edge, never `documented`. See [METHODOLOGY.md](METHODOLOGY.md).

## Structure

```
schema.yaml          # graph schema: nodes, edges, claim types, receipts
METHODOLOGY.md       # claim types, signed_is_not_witnessed, linter rules, source corpus
SYNTHESIS.md         # the invariant, why edge typing, what this is NOT
TAXONOMY.md          # node/edge/receipt vocabulary
PROVENANCE.md        # human-directed / AI-assisted disclosure
REFRESH.md           # staleness windows + refresh procedure
CASES.md             # case index
cases/               # one YAML per case: nodes + edges + inference_layer
receipts/            # one YAML per receipt (shared across edges)
fixtures/            # synthetic pass case + failure fixtures the linter must catch
tools/
  lint.py            # doctrine linter — built first; the reason this is a graph not a corkboard
  build.py           # cases + receipts -> docs/data/*.json (refuses on lint error)
  test_lint.py       # asserts the linter catches each violation for the RIGHT rule
docs/                # GitHub Pages site (cytoscape.js graph, claim-type filter)
```

## Develop

```bash
pip install -r tools/requirements.txt
python tools/test_lint.py     # linter self-test against fixtures
python tools/lint.py          # validate cases + receipts
python tools/build.py         # emit docs/data/graph.json
python -m http.server -d docs # serve the site locally
```

## Doctrine, in one breath

No edge without a receipt. Signed is not witnessed. Inferred edges show their
derivation. No PII, ever. No access beyond public surfaces. Absence is recorded as
absence, not asserted as concealment. The schema is administration-agnostic — the
portals are cases, not the thesis.

Apache 2.0.
