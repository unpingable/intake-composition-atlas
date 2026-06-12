# Methodology

This document defines how edges enter the graph, what evidence each claim type
requires, and which rules the linter (`tools/lint.py`) enforces mechanically. It
is the contract between the doctrine in [SYNTHESIS.md](SYNTHESIS.md) and the data
in `cases/`. If prose and linter disagree, the linter is the operative authority
for what ships; this document explains why each check exists.

## The one thing that makes this not a corkboard

Existing privacy work (EPIC, EFF, POGO, GAO/IG reports) is prose. It is often
right, but it blends three different kinds of claim without marking the seams:
that a flow *exists*, that a flow is *permitted*, and that a flow is *possible*.
This project's entire value is refusing that blur. **Every edge carries exactly
one claim type and at least one receipt.** An edge that cannot cite its basis
does not ship.

## Claim types

| Claim type | Asserts | Required receipt |
|---|---|---|
| `documented` | This flow/collection **exists** (someone disclosed it) | A receipt of a documented-eligible kind: `cma`, `sorn`, `pia`, `omb_icr`, `contract_award`, `fedramp`, `observed_artifact`, `agency_statement` |
| `authorized` | A legal instrument **permits** this flow; no evidence it occurs | `eo`, `statute`, or a SORN routine-use clause — citation to the authorizing text |
| `inferred` | Composition makes this **derivable**; not authorized as such, not observed | A `derivation`: the parent edge IDs whose composition yields it |
| `speculative` | Plausible under incentive analysis only | Marked; excluded from the default view; capped at 2 per case |

### Why `agency_statement` is documented-eligible (and journalism is not)

`agency_statement` is the softest documented-eligible kind, so its boundary is drawn
deliberately. It admits **first-party disclosure by the record custodian** — an agency's own
guidance page, a department press release — which is a statement about the custodian's own
operations, roughly a statement against interest, and a defensible witness that a flow exists.
It does **not** admit third-party journalism: a newspaper reporting that a flow occurs is a
relay, not a witness (cf. *indexed is not read*), and is leads-only — chase its citations to a
primary record. The kind is named `agency_statement`, not `press_or_agency_statement`, precisely
so a future edit cannot quietly let a WSJ article stand as a `documented` basis.

## `signed_is_not_witnessed`

The load-bearing rule. **An executive order authorizing interagency data sharing
is a signing event, not a witnessed flow.** It produces an `authorized` edge,
never a `documented` one. `documented` requires evidence the flow *exists*: a
published Computer Matching Agreement, a SORN routine use *plus* a matching
notice, an observed analytics tag, a contractor award describing the work.

The linter enforces this as `DOCUMENTED_NEEDS_WITNESS`: a `documented` edge whose
receipts are drawn *only* from `eo`/`statute` kinds is an error instructing
downgrade to `authorized`. (A statute is admissible as `documented` only as to its
own text — e.g. "the statute itself says X" — never as proof that a flow happens.)

### Worked example: the disbursement edge in `trump-accounts`

The edge `e-share-disburse` (`shares_with`: the Trump Accounts Program system of
records → U.S. Department of the Treasury) models the data flow behind the $1,000
pilot contribution. The intuitive instinct is `documented` — Treasury obviously
pays the money, so obviously the eligibility records move from IRS to Treasury.

But the only receipt for that flow is `r-ta-statute`: IRC § 6434 *directs* Treasury
to make the payment. No published CMA, SORN routine use, or PIA witnesses the
IRS→Treasury record transfer itself; the proposed rule explicitly declines to
describe how eligibility is verified or shared (recorded in `r-ta-prop-reg` as
absence, not concealment). A statute that authorizes a payment is a signing event,
not a witnessed flow.

So the edge ships as `claim: authorized`. Setting it to `documented` trips the
linter:

```
$ python tools/lint.py   # (with e-share-disburse forced to claim: documented)
  ERROR [DOCUMENTED_NEEDS_WITNESS] trump-accounts.yaml:e-share-disburse:
  claim=documented but receipts are only ['statute'] (EO/statute authorize a flow,
  they do not witness it). Downgrade to claim: authorized.
1 error(s), 0 warning(s).
```

This is the discipline biting on real material: the scariest-sounding edge in the
case is precisely the one with the weakest claim type, and the linter makes that
visible rather than letting it pass as fact. In the default (documented-only) graph
view, this edge is hidden; it appears only when the viewer opts into the
`authorized` layer — which is the honest representation of what is known.

## Inferred edges show their derivation

An `inferred` edge must list the parent edge IDs (`derivation`) whose composition
yields it. Two linter rules guard this:

- `INFERRED_NO_DERIVATION` — an inferred edge with an empty `derivation` is an error.
- `INFERRED_TOWER` — a derivation parent that is *itself* `inferred` is an error.
  No inference built only on inference (depth-1 cap). Inference towers are how a
  speculative graph launders itself into looking documented; the cap forbids it.

`enables_inference` edges must carry `claim: inferred` (`ENABLES_INFERENCE_CLAIM`).

## The contestation block (the standing question, per edge)

Edges of type `shares_with`, `matches_against`, and `consumed_by` must carry a
`contestation` block with two fields:

- `notice` — how, if at all, would a data subject learn this edge exists?
- `appeal` — what process, if any, targets the *composed* result (not the
  underlying official record)?

Most honest answers are `none_identified` and "appeals target the official record,
not the inferred graph." That is precisely the finding, recorded per-edge rather
than asserted in an essay. The linter requires the block (`CONTESTATION_MISSING`);
it does not grade the content — that is a reviewer obligation.

## Linter rule index

| Rule code | Meaning |
|---|---|
| `EDGE_NO_RECEIPT` | edge has zero receipts (≥1 required) |
| `EDGE_RECEIPT_UNRESOLVED` | edge cites a receipt id that does not exist |
| `EDGE_DANGLING_REF` | `from`/`to` resolves to no node (or edge, for `authorizes`) |
| `EDGE_BAD_TYPE` / `EDGE_BAD_CLAIM` | unknown edge type / claim type |
| `NODE_BAD_TYPE` / `NODE_NO_ID` | unknown node type / missing node id |
| `DOCUMENTED_NEEDS_WITNESS` | `documented` edge backed only by EO/statute (`signed_is_not_witnessed`) |
| `INFERRED_NO_DERIVATION` | `inferred` edge with empty derivation |
| `INFERRED_PARENT_MISSING` | derivation cites a parent edge that does not exist |
| `INFERRED_TOWER` | derivation parent is itself inferred (depth-1 cap) |
| `ENABLES_INFERENCE_CLAIM` | `enables_inference` edge not marked `inferred` |
| `SPECULATIVE_OVER_CAP` | more than 2 speculative edges in one case |
| `CONTESTATION_MISSING` | sharing/consuming edge lacks notice + appeal |
| `RECEIPT_NO_DATE` / `RECEIPT_BAD_DATE` | receipt missing/unparseable `retrieved` |
| `RECEIPT_BAD_KIND` | unknown receipt kind |
| `RECEIPT_STALE` (warning) | receipt older than its staleness window |

## Source corpus (where receipts come from)

Worked top-down per case. The good receipts are better than people realize —
the Privacy Act *requires* agencies to publish their join operations.

1. **Computer Matching Agreements (CMA)** — the best source. Published, signed,
   dated documented join operations. Agency CMA pages (SSA, IRS, DHS) + Federal
   Register "matching program" notices.
2. **SORNs** — Federal Register + agency Privacy Act pages. Routine-use clauses
   are the reuse-authorization surface; enumerate them per system of record.
3. **PIAs** — name contractors, data elements, retention, sharing.
4. **OMB/PRA ICRs** — reginfo.gov: every form has a control number, supporting
   statement, and burden estimate.
5. **Executive orders / statutes** — produce `authorized` edges almost exclusively.
6. **Procurement** — USAspending / FPDS: which vendors touch which intake.
7. **FedRAMP marketplace** — hosting/cloud authorization records.
8. **Direct portal observables** — privacy policies, terms, visible analytics/JS,
   identity-proofing integration, DNS/CT. `observed_artifact`. Snapshot to
   archive.org at observation time.
9. **Secondary** (EPIC, KFF, WSJ, GAO, IG) — leads only; chase their citations to
   primary documents.

## Layout metadata is non-evidentiary

The build emits cartographic hints on nodes — `lane`, `rank`, `short_label` — so the
graph renders as a left-to-right composition flow (authority → intake → collection →
data → custody → inference → decision) instead of a force-directed blob. These fields
mean **"draw this here,"** nothing more.

> **Invariant: layout metadata carries no evidentiary weight. Claim strength is carried
> _only_ by claim type, receipts, derivation, and contestation.**

A node's `lane` is not a claim about the node. `rank: 2` does not make something a
"Rank-2 claim"; it is a column index. Position encodes *where a claim sits in the
machine*; line style encodes *how strong the claim is*. The two never trade places. If
a future change lets layout metadata influence what counts as documented/authorized/
inferred, that change is wrong by this invariant — the map would have started becoming
proof.

Corollary: authorization is rendered as a faint annotation on the flow it permits (and
cross-linked in the panel via `authorized_by`), never as a normal data-flow arrow,
because an `authorizes` edge is a permission, not a witnessed flow (`signed_is_not_
witnessed`).

### Story bands (layout rule)

Related flows that have **no documented edge between them** are not one continuous pipe, and
must not be rendered as one. A reader forced to reconcile a legal authorization, a documented
collection, and an inferred linkage along a single horizontal sentence does edge-reconciliation
labor the graph should have done for them.

Rule: **when a visible view contains more than one weakly-connected band of claims, stack the
bands vertically, sharing the same lane (stage) columns — one band per kind of relation, not
one continuous DAG.** Bands, top to bottom:

| Band | Holds | Default |
|---|---|---|
| Legal basis | `instrument` nodes + `authorizes` edges (the `authority` lane) | off |
| Documented path | the documented spine (all non-authority/inference/external lanes) | **on** |
| Possible composition | `enables_inference` + derived nodes (the `inference` lane) | off |
| External power | `external_consumer` + `speculative` | off |

A single visible band renders as the plain horizontal spine (no band scaffolding). Cross-band
relations (an `authorizes` edge from Legal basis down into Documented path; an
`enables_inference` edge from a documented field down into Possible composition) render as faint
cross-band connectors, never as inline spine edges. This keeps **documented plumbing** visually
distinct from **permission** and from **possible consequence** — the same distinction the claim
types make, now made spatially. (Composes with *layout metadata is non-evidentiary*: the band a
node sits in is derived from its lane, which is cartographic, not a claim about the node.)

Status: the layer on/off defaults and lane separation are implemented in the renderer; the
vertical band **stacking** is the next renderer slice (rule recorded here first).

### Deferred candidate (named, not built): atlas view vs evidence view

A future split — a cognition-first "atlas" view and an admissibility-first "evidence"
view sharing one data substrate — is recorded here as a candidate, not a commitment. It
becomes justified when the evidence base spans multiple cases or densities where
"complete" and "legible" become different products. For a single small case it would be
premature. Named per *name early, ratify lazily*; the door is labeled, the second house
is not built.

### Deferred candidate (named, not built): renderer migration to React Flow + ELK

The current graph view is hand-built on cytoscape.js with a `preset` lane layout. Cytoscape
is a graph-theory/network library; it keeps *wanting to be a graph* when what we are
building is a human-readable system map (an explainer with receipts). A future migration to
**React Flow + ELK.js** is recorded as a candidate: React Flow is built for app-like
node/edge diagrams (custom nodes, panels, selection, fit-view), and ELK's layered algorithm
is purpose-built for left-to-right DAGs with orthogonal routing.

Doctrine line: *cytoscape is fine for an admissibility graph; React Flow + ELK is better for
a public, human-readable system map.* Migration becomes justified when (a) the guide/app-UI
ergonomics keep fighting the renderer, or (b) multi-case density arrives. Until then the
build output (`docs/data/graph.json` with cartographic metadata) is renderer-agnostic by
design — any of cytoscape, React Flow, or a static Graphviz pass can consume it — so the
migration is a view swap, not a data change. Not built now; the data contract is the hedge.

## Sweep and currency protocol (invariant stub — named, not built)

The atlas is slated to become a *consumer* of a governor periodic-sweep workflow (its
schemas and lifecycle are designed in the governor / NQ lane, not here). The full
protocol is deferred. But one atlas-local invariant is recorded now because it is
load-bearing and cheap to violate:

> **Claim type and evidentiary currency are separate axes. An automated sweep may update
> currency; it may never change claim meaning.**

Two orthogonal axes:

- **claim** — `documented` | `authorized` | `inferred` | `speculative`
- **currency** — `current` | `stale` | `contested` | `unreachable` | `superseded` | `pending_review`

A dead or moved source does **not** make a `documented` edge "not documented." It makes it
`documented` with currency `stale`/`unreachable` and a `last_verified` date. Moving an edge
*down the currency axis* (current → stale → contested) is an observation. Moving it on the
*claim axis* — documented→authorized, retiring an edge, adding one — is a promotion-class
mutation and is never autonomous.

**The only autonomous write a sweep may commit** is a hash-identical re-fetch of a receipt
source → append an observation receipt, bump `observed` / archive snapshot. Hash-identical
re-verification adds evidence without changing any claim. Everything else emits a review
packet and **stops**: content drift, a dead/moved link, a staleness-horizon breach, and
*especially* any candidate new edge.

Candidate new edges are the dangerous growth path. **Indexed is not read**: a Federal
Register or API hit testifies that a document *exists*, not that it supports an edge. A
candidate-edge packet therefore requires a validation note attesting the document was
actually examined — relay detection is not witness (cf. `signed_is_not_witnessed`).

**Authority is typed.** Validation notes (from a model or a human) are *testimony* —
admissible input carrying `supports` / `objections`. A model validation note is **not**
acceptance. The acceptance receipt is **operator-signed only**. There is no ambient "a model
validated it, therefore accepted" path.

Acceptance is **graph-scoped, not path-scoped**: `case_ids` / `edge_ids` / `receipt_ids`,
with an explicit `not_accepted` list (the anti-footgun — without it, acceptance becomes a
coupon for future crimes). Acceptance is a bounded fuel cell, not a blessing: it has a
horizon mapped onto the staleness windows in [REFRESH.md](REFRESH.md), and is invalidated by
touched receipts, schema-version change, **methodology-version change** (editing *this* file
changes what counts as documented, retroactively re-typing acceptance), and failed
reproduction.

**Self-application.** The public site must surface currency, not hide it — an edge renders
as `documented · current`, `documented · stale (last verified …)`, `inferred · pending
review`, and so on. An atlas whose entire thesis is illegible composed claims cannot present
stale evidence as fresh; that would be a compact self-indictment. (Phase 5 adds currency
state + public rendering *before* any cron is wired.)

## Conduct limits

- **No PII, ever.** Nodes are institutions, systems, document classes, and field
  *types*. Never individuals, never example records, never scraped user data.
- **No access beyond public surfaces.** Public pages, public APIs, public filings
  only. No authentication, no form submission, no probing.
- **Absence is recorded as absence.** A flow with no documented edge is not
  asserted to be concealed; it is simply not yet witnessed.
