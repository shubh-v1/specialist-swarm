---
name: rfp-requirements-blackboard
description: BTS-Synthetic Deal Desk requirements blackboard. Use at the start of any inbound RFP response to parse the RFP into numbered requirement IDs, assign each an owning specialist, and track status, confidence and evidence in one shared structured table. Also use before final assembly to check that no requirement is unresolved. Trigger on any request to parse an RFP, build a requirements list, check RFP coverage, or confirm nothing was missed.
---

# RFP Requirements Blackboard

The blackboard is the single source of truth for the deal. It is a structured JSON file, `blackboard.json`, built by the coordinator BEFORE any specialist is called. Specialists answer against requirement IDs, not against prose. The coordinator may not produce the final document until every row is resolved.

Why: a real RFP has 80–200 requirements. If outputs are summarised in prose, nothing proves that requirement 4.3.7 ("SOC 2 Type II report within 30 days") was ever answered. Silent drops get bidders disqualified.

## Step 1 — Parse the RFP into atomic requirements

- One row per obligation. Split sentences that hold several ("uncapped liability AND full indemnity" = 2 rows).
- ID = RFP section number, plus a letter when split: `4.1a`, `4.1b`. If the RFP has no numbering, use `S<section>-<n>`.
- Extract every "must", "shall", "will", "required", "non-negotiable", and every response-format instruction (section 7: references, capability matrix, page limits).
- Keep the RFP's own words in `text`. Never paraphrase away a number, date or threshold.
- Include evaluation criteria and weights as context rows with type `info`. They need no answer but feed the huddle.

## Step 2 — Assign ONE owner per row

| Requirement type | Owner |
| --- | --- |
| Discount, price, term, payment, MFN, escalators, TCO | pricing |
| Liability, indemnity, audit, IP, termination, subprocessors, data residency (contract side) | legal |
| Workloads, scale, integrations, platform capability, SLA engineering feasibility | technical_fit |
| Vendor comparison, incumbent, positioning, win themes, references | competitive |
| Response format, deadlines, attachments | coordinator |

If a row needs two specialists, set `owner` to the primary and list the other in `consult`. Ownership never stays empty.

## Step 3 — Row schema

```json
{
  "id": "4.1",
  "section": "Contractual — Liability",
  "text": "Vendor liability for any data breach is uncapped...",
  "type": "mandatory | preferred | info | format",
  "owner": "legal",
  "consult": ["pricing"],
  "status": "open | covered | partial | gap | n/a",
  "confidence": "high | medium | low | null",
  "evidence": "source file + section, or specialist reasoning in one line",
  "position": "our response in one sentence, or null",
  "dependencies": ["3.3"],
  "huddle_flags": []
}
```

All rows start `status: open`, `confidence: null`.

## Status definitions

- **covered** — we meet it as written. Evidence required.
- **partial** — we meet part, or only with a condition. `position` must state exactly what we offer instead.
- **gap** — we cannot meet it. `position` must state the counter-offer or "no-bid on this item".
- **n/a** — requirement does not apply to us. Evidence must say why. The coordinator, not the specialist, approves every n/a.

## Step 4 — Specialist reply contract

Tell each specialist: "Reply as a JSON array keyed by requirement ID. Every ID you own must appear. For each give status, confidence, evidence, position. Do not skip an ID. Say `gap` rather than omit."

Merge replies into `blackboard.json`. Reject and re-ask any reply that:
- omits an owned ID,
- gives `covered` or `partial` with empty evidence,
- gives `high` confidence with no source cited.

## Step 5 — Resolution gate (hard stop)

Before building the .docx, run the checks below. Print the result.

1. Rows with `status: open`: must be 0.
2. Rows with `status: gap` or `partial` and empty `position`: must be 0.
3. Rows with `confidence: low` on a `mandatory` row: each must have a coordinator note or a follow-up sent.
4. Every `huddle_flags` entry has a logged resolution (see deal-huddle skill).
5. Every ID in the RFP appears exactly once in the blackboard (count check: RFP requirement count == rows).

If any check fails: do not generate the document. Send targeted follow-ups, update the board, re-run the gate.

## Step 6 — Output

Gate report:

```
BLACKBOARD GATE — <customer>
Requirements parsed: N   Resolved: N   Open: 0
covered X | partial Y | gap Z | n/a W
Low-confidence mandatory rows: <ids>
Unresolved huddle flags: 0
GATE: PASS | FAIL (<reason>)
```

Then hand the board to the compliance-matrix-export skill for the appendix.

## Rules of conduct

- Never drop a row to make the gate pass.
- Never change a specialist's status silently. Record changes in `huddle_flags` with who changed it and why.
- Never mark `covered` from marketing language. Evidence must point to product-overview, a past win, or a policy document.
