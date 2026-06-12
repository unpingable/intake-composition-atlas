# Cases

One YAML file per case in [`cases/`](cases/). A case is a subgraph: nodes + edges +
an `inference_layer`. Receipts are filed separately in [`receipts/`](receipts/) and
shared across edges.

| Case | Status | Nodes | Edges (doc / auth / inf) | Notes |
|---|---|---|---|---|
| [trump-accounts](cases/trump-accounts.yaml) | active | 14 | 8 / 3 / 1 | TrumpAccounts.gov / Form 4547 → Treasury TAP system of records. Carries the `signed_is_not_witnessed` worked example (`e-share-disburse`). |

## Planned (not yet built)

- **trump-rx** — TrumpRx.gov; medication+ZIP → condition-proxy inference edges.
- **trump-card** — TrumpCard.gov / I-140G; DHS/USCIS sponsor graph.
- **trump-ira** — TrumpIRA.gov; mostly `authorized` (a portal promised, not yet operating).
- **historical** — IRS/SSA income-verification matching *or* the ACA Federal Data
  Services Hub. Proves the schema is administration-agnostic (status: `historical`).
- **policy-layer** — Information-Silos EO + 2026 Fraud-Task-Force EO; an instrument-
  centric case whose `authorizes` edges land on the others.

See [METHODOLOGY.md](METHODOLOGY.md) for how edges are typed and receipted, and
[SYNTHESIS.md](SYNTHESIS.md) for the thesis and scope.
