# Taxonomy

Cross-cutting vocabulary for the graph. The authoritative machine-readable source
is [schema.yaml](schema.yaml); this document is the human-facing gloss.

## Claim types (the spine)

`documented` · `authorized` · `inferred` · `speculative`. Definitions and the
receipts each requires are in [METHODOLOGY.md](METHODOLOGY.md). One per edge.

## Node types

| Type | What it is |
|---|---|
| `portal` | Public-facing intake surface (a `.gov` site) |
| `instrument` | Legal basis — EO, statute, regulation, OMB memo |
| `form` | Collection instrument; carries an OMB control number where applicable |
| `field_class` | **Coarse** category of data collected — child SSN, medication+ZIP, sponsor identity, behavioral telemetry. Field *classes*, never individual fields, never values |
| `system_of_record` | Privacy Act SORN-backed system (cite SORN number) |
| `agency` | Federal agency (IRS, Treasury, DHS, USCIS, HHS, SSA, …) |
| `operator` | Private contractor/vendor — identity proofing, cloud, analytics, payments |
| `decision_surface` | Downstream use — eligibility, fraud scoring, enforcement prioritization, adjudication, pricing, targeting |
| `external_consumer` | Non-federal recipient — states, law enforcement, insurers, data brokers. v1: node type present, edges near-zero by design |

## Edge types

| Type | Direction | Notes |
|---|---|---|
| `collects` | portal/form → field_class | what a surface gathers |
| `authorizes` | instrument → portal \| edge | an instrument permits a thing (may target an edge) |
| `feeds` | portal/form → system_of_record | intake lands in a system |
| `operates` | operator → portal \| system_of_record | who runs the surface |
| `shares_with` | system/agency → agency \| external_consumer | **CMA gold lives here**; contestation required |
| `matches_against` | system ↔ system | Computer Matching Agreements; contestation required |
| `enables_inference` | field_class set → derived attribute | always `claim: inferred`, always with derivation |
| `consumed_by` | system/graph → decision_surface | contestation required |

## Receipt kinds

`cma`, `sorn`, `pia`, `omb_icr`, `contract_award`, `fedramp`, `observed_artifact`,
`press_or_agency_statement` (documented-eligible); `eo`, `statute` (authorize a
flow, do not witness it — see `signed_is_not_witnessed`).

## Case status

`active` · `emerging` · `resolved` · `recurring` · `historical`. The `historical`
tag carries the administration-agnostic proof: same schema, different era.

## Contestation vocabulary

Per sharing/consuming edge: `notice` (how a subject would learn of the edge) and
`appeal` (what process targets the composed result). Common honest value:
`none_identified`.
