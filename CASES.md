# Cases

One YAML file per case in [`cases/`](cases/). A case is a subgraph: nodes + edges +
an `inference_layer`. Receipts are filed separately in [`receipts/`](receipts/) and
shared across edges.

| Case | Status | Nodes | Edges (doc / auth / inf) | Notes |
|---|---|---|---|---|
| [trump-accounts](cases/trump-accounts.yaml) | active | 13 | 9 / 3 / 1 | TrumpAccounts.gov / Form 4547 → Treasury TAP system of records. New intake surface, documented collection, inferred household composition. Carries the `signed_is_not_witnessed` worked example (`e-share-disburse`). |
| [difsla-ssi-irs-match](cases/difsla-ssi-irs-match.yaml) | recurring | 7 | 5 / 1 / 0 | IRS/SSA DIFSLA Match #1016. The canonical computer match — first real `matches_against` + `cma` receipt, and the first **documented** join (not inferred). Carries genuine contestation safeguards (verify-before-adverse-action, CMPPA). |

Each case renders as its own explainer at `graph/?case=<case_id>`; the splash lists them.

## Roadmap (prioritized)

Sequence chosen to **mature the edge grammar** — collection → matching → hub composition —
not by topical interest. The next two cases instantiate `matches_against` and the `cma`
receipt kind, which v1 (TrumpAccounts) declares in the vocabulary but never exercises with a
real *documented* join. Each will extend `edge_types` (e.g. `routes_via`, `matches_against`,
`returns_verification`, `supports_decision`, `creates_contestation_path`) as the forcing case
arrives — named here, added with the case, not before.

**1. IRS/SSA DIFSLA — SSI unearned-income match** — ✅ **BUILT** (`difsla-ssi-irs-match`).
The canonical computer match; first real `matches_against` + `cma`, first *documented* join, with
genuine contestation safeguards. (Note: the 4.13:1 benefit/cost figure cited in early research is
not yet wired as a node — the CMA PDF is 403 to automated fetch; the FY2023 ~$74.5M figure is in
the `r-difsla-cma` basis. Add the cost-benefit detail in a later pass if the source becomes
fetchable.) See the case table above.

**2. ACA Marketplace / Federal Data Services Hub** — modern multi-source eligibility routing.
> "How a Marketplace application becomes a federal data match."
Application fields route through the Hub to verify SSN, citizenship/lawful presence, household
income, family size against IRS/SSA/DHS/state sources → eligibility → APTC/CSR/QHP/Medicaid.
**Load-bearing caveat:** the Hub is a routing *conduit*, not a PII store — model as
routes/processes/transmits, never "stores" (CMS FDSH PIA). Mark expired DHS/state agreements
`historical` or `needs_current_receipt`.
Receipts: CMS FDSH PIA; IRS/CMS CMA 2024-08 / HHS 2404 (income/family-size FTI); SSA/CMS CMA
2025-12 / HHS 2601 / SSA 1097; FR 2026-02472 (SSA matching notice w/ safeguards);
HealthCare.gov "How We Use Your Data". Historical-only: 2023 DHS/CMS exchange, 2023 SBAE CMA.

**Then** (additional muscles, roughly in order):
3. **HUD Enterprise Income Verification** — strongest wage/income match (NDNH + SSA).
4. **FAFSA / IRS Direct Data Exchange** — consent as the intake hinge; tax data → aid eligibility.
5. **E-Verify** — public/private membrane; employer intake → DHS/SSA match → work authorization.
6. **SAVE** — state/local benefit/license action riding on federal status verification.
7. **Treasury Do Not Pay** — anti-fraud decision infrastructure ("denial gets cheaper").

**Deprioritized:** TrumpRx / TrumpCard / TrumpIRA — too inference-heavy until better source
records exist. The atlas must prove *documented composition* next, not "this could get creepy"
(everything can; that's not a receipt, that's Tuesday).

**Posture for matching cases:** documented-composition specimens, not scandal frames. Always
render the verify-before-adverse-action safeguard where the records show one — the contrast
(TrumpAccounts = new surface + inferred risk; DIFSLA/ACA = disclosed machinery + documented
join) is what makes this "here is the general machinery" rather than "one weird Trump thing."

See [METHODOLOGY.md](METHODOLOGY.md) for how edges are typed and receipted, and
[SYNTHESIS.md](SYNTHESIS.md) for the thesis and scope.
