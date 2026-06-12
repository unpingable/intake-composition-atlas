# Synthesis

## The invariant

Populations are exposed to inferences and decisions composed **outside their
effective contestation surface**. The grid atlas asks who controls the transformer
you cannot vote on. This atlas asks who acts on the join you cannot see.

Narrow federal intake surfaces — a benefit portal, a single form — are each
individually unremarkable. The structural risk is *composition*: when the field
classes collected at one surface are matched, shared, and fed into decision
surfaces, they compose into a broader identity-and-decision graph. Abstraction
does not eliminate the chokepoint. It relocates it into the composition layer,
where there is rarely notice and almost never an appeal that targets the composed
result.

## Why edge typing is the whole project

Privacy advocacy already describes these risks in prose, and is often right. But
prose blends three claim classes without marking the seams:

- a flow **exists** (a SORN or privacy policy says X goes to Y),
- a flow is **permitted** (an EO authorizes the join; no evidence it executes),
- a flow is **possible** (composition makes it derivable).

Conflating these is what makes a scary diagram dismissable. This atlas refuses the
blur: every edge carries one claim type and a receipt. See
[METHODOLOGY.md](METHODOLOGY.md). The deliverable is the typed graph; the prose
exists to explain the types.

The default view shows `documented` edges only. Toggling on `authorized`, then
`inferred`, visibly inflates the graph. **The delta between those views is the
finding** — what is proven, what is permitted, what is possible — earned edge by
edge, or it does not render.

## Why administration-agnostic

The current portals are *cases*, not the thesis. Composition risk is a structural
property of benefit-portal architecture plus anti-silo policy. It predates this
administration: federal computer-matching of income data goes back to the 1980s —
which is *why* the Privacy Act's Computer Matching Agreement regime exists at all.
The schema must absorb a 1980s IRS/SSA income-verification match, a 2014
healthcare.gov data hub, and a 2026 portal with equal ease. v1 includes at least
one historical case to prove it. A typed graph of public filings is watchdog work
in the EPIC/POGO tradition; a vibes graph titled with a president's name is a
different and lesser genre.

## What this is NOT

- **Not a claim that any specific unlawful flow exists.** Absence of a documented
  edge is recorded as absence, not asserted as concealment.
- **Not administration-specific.** The schema indexes a structural property of
  intake plus anti-silo policy; cases from any era are admissible.
- **Not a privacy essay.** The deliverable is a typed graph with receipts; the
  prose exists to explain the types.
- **Not exhaustive.** Edges ship when receipted, not when suspected.
- **Not surveillance, and not a how-to.** It indexes what is *already disclosed*
  in public filings but deliberately illegible because it is scattered across
  hundreds of SORNs, PIAs, CMAs, and ICRs.

## Open questions

- Where do `external_consumer` edges (insurers, brokers, landlords) become
  admissible without sliding into speculation? v1 ships the node type with
  zero/near-zero edges and lets the empty region speak.
- Does the historical case belong in the same graph as current portals, or in a
  sibling view? (Resolved for v1: same schema, tagged by `status: historical`.)
- A written companion at launch — the documented-only default view is the
  screenshot it wants — is a launch decision, not a build task.
