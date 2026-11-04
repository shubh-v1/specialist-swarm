---
name: compliance-matrix-export
description: BTS-Synthetic compliance-matrix appendix builder. Use when an RFP response is nearly done and the requirements blackboard must be turned into a compliance matrix appendix for the proposal document, with a coverage summary and a huddle conflict log. Trigger on any request to produce a compliance matrix, requirements traceability appendix, or capability matrix, or to export the blackboard.
---

# Compliance Matrix Export

Most RFPs require a compliance matrix anyway. The blackboard already holds it. This skill turns `blackboard.json` and `huddle-log.json` into appendix content for the .docx.

Precondition: resolution gate from the rfp-requirements-blackboard skill reads PASS. If it does not, stop and report which check failed. Do not export a partial matrix.

## Appendix A — Compliance matrix

One table, one row per requirement, in RFP order. Columns:

| Req ID | Requirement (RFP wording, shortened only if over 40 words) | Response | Status | Evidence / reference | Owner |

- **Response**: the `position` field, plain language, customer-facing. No internal margin, no negotiation notes.
- **Status** shown as: Compliant (covered), Partially compliant (partial), Non-compliant with alternative (gap), Not applicable (n/a).
- Colour: green, amber, red, grey. Always also print the word; do not rely on colour alone.
- Header row repeats on every page. Landscape orientation for the appendix section.
- Group rows under RFP section headings.

## Appendix B — Coverage summary

A short table at the top of Appendix A:

```
Total requirements: N
Compliant: X (x%)   Partial: Y   Non-compliant with alternative: Z   N/A: W
Mandatory requirements not fully compliant: <list of IDs>
```

Compute from the blackboard. Do not type the numbers by hand; count them.

## Appendix C — Exceptions and clarifications

One row per `partial` and `gap` row: ID, what we cannot meet as written, our alternative, and the clarification question for the customer if we have one. This section is customer-facing.

## Appendix D — Internal: huddle conflict log (INTERNAL ONLY)

From `huddle-log.json`: ID, issue, resolution, who decided, residual risk. Mark the page "Internal — remove before sending". Put it last so it can be deleted in one step. Never merge it into customer-facing sections.

## Checks before finishing

1. Row count in Appendix A == `blackboard.json` row count == RFP requirement count.
2. No row shows Status blank.
3. No `confidence`, `huddle_flags` or margin figure leaks into Appendix A or C.
4. Every Compliant row has an evidence reference.
5. The coverage numbers match a recount.

## Output

Also save `compliance-matrix.csv` (same columns as Appendix A) so the customer or a reviewer can filter it. Report: file names, row counts, and any row you had to flag.

## Rules of conduct

- Never upgrade a status to look better. A gap stays a gap.
- Never include internal-only data in a customer-facing appendix.
- If the RFP supplies its own matrix template (for example the "Capability Matrix" attachment), mirror its columns and order, and add ours only as extra columns.
