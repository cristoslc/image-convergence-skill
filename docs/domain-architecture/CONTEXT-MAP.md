# Context Map

Single bounded context, **convergence loop**, with two conforming inner models:

- **Review model** (image -> per-dimension scores) — upstream of the decision model.
- **Decision model** (ledger -> next action) — the engine's rule; the prose skill mirrors it.

Integration happens at the ledger: the review writing scores into attempt rows, the decision model reading them. One shared ledger shape (see `DOMAIN-EVENTS.md`), so no anticorruption layer is needed inside the repo.
