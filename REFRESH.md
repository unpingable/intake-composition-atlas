# Refresh

Portals change fast; filings change slowly. Receipts carry a `retrieved` date and
the linter warns when one ages past its window.

## Staleness windows

| Receipt kind | Window | Rationale |
|---|---|---|
| `observed_artifact` | 90 days | Live portal observables (analytics tags, vendor JS, DNS/CT) drift quickly |
| everything else | 365 days | Federal Register documents, CMAs, SORNs, PIAs, ICRs are durable |

The linter raises `RECEIPT_STALE` (a **warning**, never a build failure) when a
receipt's `retrieved` date exceeds its window. Staleness is surfaced, not buried.

## Source of truth

- `cases/*.yaml` + `receipts/*.yaml` are **canonical**.
- `docs/data/*.json` is **derived** by `tools/build.py`. If it disagrees with the
  YAML, it is wrong — rebuild and commit.

## Refresh procedure

1. Re-fetch the public surface(s) for a case (public pages/APIs/filings only).
2. Re-snapshot to archive.org; update `archived` and `retrieved` on the receipt.
3. If the underlying document changed in substance, edit `basis` and revisit any
   edges that cite it — a changed routine-use clause can change an edge's claim type.
4. `python tools/lint.py` → `python tools/build.py` → commit YAML + rebuilt JSON.

## Doctrine constraints (non-negotiable)

1. **Automation cannot widen claims the evidence doesn't support.** A freshness
   stamp that isn't refreshed is worse than no stamp.
2. **Refusal must remain visible.** A failing check surfaces on the next edit path,
   not buried.
3. **Proposal-only by default.** Automation prepares diffs; humans ratify. CI never
   auto-commits content (see `.github/workflows/ci.yml`).
4. **YAML is source-of-truth.** Generated JSON is a subordinate rendering.

`snapshot.py` (archive.org integration + automated freshness sweep) is a Phase 5
deliverable, not yet built.

**Archive retry policy (lookup-first, not save-first).** Some receipts carry an empty
`archived:` with a "save attempted, no snapshot returned yet (retry)" note — Save Page Now
queued the capture but the snapshot was not yet indexed. Do **not** re-trigger saves in a
loop (that just adds noise and risks throttling). To retry: query the CDX / availability API
for the original URL first; wire the snapshot if one now exists; only trigger a fresh Save
Page Now if none exists after a reasonable delay. Retries are currency cleanup, never a
claim/layout change.

## Currency is not claim (sweep invariant)

When the freshness sweep is built, it operates on a **currency axis** that is orthogonal to
the claim axis. A stale or dead source downgrades an edge's *currency* (`current → stale →
unreachable`); it never changes the edge's *claim type*. A sweep may autonomously append an
observation receipt only for a **hash-identical** re-fetch; any drift, dead link, or
candidate new edge emits a review packet and stops. Acceptance of a packet is operator-
signed and graph-scoped (`edge_ids` / `receipt_ids`). The acceptance horizon maps onto the
staleness windows above and is invalidated by a methodology-version change. Full statement:
[METHODOLOGY.md](METHODOLOGY.md) § "Sweep and currency protocol." Governor schemas live in
the governor lane; the atlas is a consumer.
