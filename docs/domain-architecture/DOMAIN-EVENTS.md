# Domain Events

The loop has no cross-context integration events; both models live in-process. The ledger row is the published language between review and decision:

| Field | Meaning |
|---|---|
| `number` | attempt ordinal |
| `scores` | per-dimension 0-10 review scores |
| `tactic` | revision strategy in force |
| `prompt` | full prompt text used |
| `revision` | what the revision added |

`events/` stays empty for now; when the loop integrates with an external generation API, its payload spec lands here as YAML, spec-first.
