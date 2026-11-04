---
name: deal-huddle
description: BTS-Synthetic Deal Desk cross-examination round. Use after the first specialist pass on an RFP response to make Pricing, Legal, Technical Fit and Competitive Intel read each other's outputs, raise objections, and fix combinations that are fine alone but bad together (for example big discount plus uncapped liability). Trigger on any request to reconcile specialist outputs, check deal-level consistency, run a huddle, challenge the pricing/legal/technical positions, or log conflicts.
---

# Deal Huddle — Cross-Examination Round

First-pass outputs are each correct in isolation. The deal as a whole may not be. The huddle forces specialists to read each other's work and object before the coordinator assembles anything.

Run it after the first pass on the blackboard, before the resolution gate.

## Step 1 — Circulate

Send every specialist the full blackboard (all rows, all positions). Ask each one for objections only against OTHER lanes. Cap at 5 objections each, ranked by deal impact.

## Step 2 — Objection format

Each specialist replies with a JSON array:

```json
{
  "from": "legal",
  "to": "pricing",
  "req_ids": ["4.1", "3.3"],
  "objection": "Uncapped breach liability alongside a 35% discount leaves no margin to absorb a claim.",
  "severity": "blocker | major | minor",
  "proposed_fix": "Tie any discount above 25% to a liability cap of 12 months of fees, or add a risk premium."
}
```

Rules: cite requirement IDs, state one concrete fix, no vague worries. "No objections" is a valid reply.

## Step 3 — Mandatory cross-checks

The coordinator checks these pairings even if no specialist raised them. Each is a known failure mode.

| Pair | Trap | Typical resolution |
| --- | --- | --- |
| Pricing x Legal | Deep discount + uncapped liability, MFN, or no early-termination fee | Discount conditional on liability cap; price in risk premium; reject MFN or limit its scope |
| Pricing x Competitive | Incumbent or aggressive rival named, so heavy discount may be the wrong lever | Lead with differentiators and TCO; hold the discount band |
| Technical x Legal | Technical marks a partial or gap, Legal contract text still promises it | Legal rewrites the clause to match what Technical can deliver |
| Technical x Pricing | SLA or scale we only partly meet, but price assumes full tier | Re-tier, or exclude the unmet part |
| Technical x Competitive | Win theme claims a capability Technical rated partial | Remove or soften the claim |
| Legal x Competitive | Positioning promises flexibility (audit, subprocessors) Legal will not give | Align the narrative with the legal position |
| Any x Dependencies | Row A's status changed but dependent row B was not revisited | Re-open B |

## Step 4 — Resolve, one round only

For each objection:
1. Send the target specialist the objection and ask for a revised position, or a rebuttal with evidence.
2. Accept the revision, or decide yourself if they still disagree. The coordinator decides; state the reason.
3. Update the blackboard rows. Add the conflict ID to `huddle_flags`.
4. If a fix changes another lane (a new liability cap changes price), loop that one follow-up. Stop after one extra hop. Do not run endless rounds.

Escalate to a human decision (list it in the document) when: severity is blocker AND neither lane can fix it inside policy. Example: customer insists on uncapped liability and insurance will not cover it.

## Step 5 — Conflict log

Write `huddle-log.json` and show it in the deliverable as an appendix.

```json
{
  "id": "H-01",
  "raised_by": "legal",
  "against": "pricing",
  "req_ids": ["4.1", "3.3"],
  "issue": "35% discount with uncapped liability",
  "resolution": "Discount held at 25% unless liability capped at 12 months of fees.",
  "decided_by": "coordinator",
  "rows_changed": ["3.3", "4.1"],
  "residual_risk": "Customer may reject the cap. Needs partner sign-off."
}
```

## Step 6 — Combined-deal check (last step)

After all fixes, read the final positions together and answer in one line each:

- Total discount vs liability exposure: acceptable?
- Any promise in legal text that technical rated partial or gap?
- Any competitive claim not backed by a covered row?
- Any term with no owner approval (partner sign-off needed)?

If any answer is "no", the huddle is not finished.

## Output

```
HUDDLE SUMMARY — <customer>
Objections raised: N (blocker a, major b, minor c)
Resolved: N   Escalated to human: N
Mandatory cross-checks run: 7/7
Combined-deal check: PASS | FAIL (<why>)
```

## Rules of conduct

- Specialists object to positions, not to people. Keep it to evidence.
- Never delete an objection. Log it, even if rejected.
- Narrate the huddle in the event stream. Each objection and each fix must be visible: this is the demo.
