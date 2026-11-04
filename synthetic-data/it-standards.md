# IT Provisioning Standards — BTS-Synthetic

**Owner:** IT Operations (it-ops@bts-synthetic.example)
**Version:** 2026.3 (effective 2026-09-01)
**Synthetic data — for the Hire-to-Onboard scenario**

---

## 1. Laptop matrix by role

| Role family | Standard laptop | Alternative (no approval) | Non-standard (needs approval) |
| --- | --- | --- | --- |
| Engineering — Software / Data / ML (L4–L7) | MacBook Pro 14" M4 Pro, 48 GB, 1 TB | Dell XPS 15 (Ubuntu 24.04 LTS), 64 GB | MacBook Pro 16" M4 Max, 64 GB+ |
| Engineering — Junior (L1–L3) | MacBook Pro 14" M4, 24 GB, 512 GB | Dell XPS 13 (Ubuntu) | Any Pro/Max upgrade |
| Engineering Management (M1+) | MacBook Pro 14" M4 Pro, 24 GB | MacBook Air 15" | — |
| Analytics / BI | MacBook Pro 14" M4, 24 GB | Lenovo ThinkPad X1 (Windows 11) | — |
| Sales / Consulting | MacBook Air 13" M4, 16 GB | Lenovo ThinkPad X1 (Windows 11) | — |
| Corporate (HR, Finance, Legal) | Lenovo ThinkPad X1 (Windows 11) | MacBook Air 13" | — |

**Non-standard approval:** requires a written business justification from the hiring manager **and** approval from the department Director. Rationale "large local workloads" is normally redirected to a cloud dev box (see §4) unless the workload cannot leave the device.

**Keyboard layouts:** all EU-shipped laptops available in US-International, German (QWERTZ), UK, French (AZERTY), Nordic. Must be specified at order time.

## 2. Lead times (from order placed to device at desk/home)

| Device | Germany / EU | US | UK |
| --- | --- | --- | --- |
| Standard laptop (in stock) | 5 business days | 3 business days | 5 business days |
| Alternative laptop | 8 business days | 5 business days | 8 business days |
| Non-standard laptop | **15 business days** (incl. approval) | 10 business days | 15 business days |
| Accessibility equipment (ergonomic keyboard, vertical mouse, etc.) | 7 business days | 5 business days | 7 business days |
| Office monitor (hot desk) | 3 business days | 3 business days | 3 business days |

Device must be **imaged and enrolled in MDM 2 business days before start**. Order cut-off = start date − (lead time + 2 business days).

## 3. Accounts — baseline (every employee)

| System | Provisioned by | Lead time | Notes |
| --- | --- | --- | --- |
| Microsoft Entra ID (SSO identity) | IT Ops | 1 business day | Created from HRIS once offer accepted **and** background check received or waived |
| Microsoft 365 (Outlook, Teams, OneDrive) | IT Ops | Same day as Entra | — |
| Slack | IT Ops | Same day as Entra | Auto-join #general, #announcements, office channel (#munich, #austin, …) |
| Workday (HRIS self-service) | HR Ops | 1 business day | — |
| 1Password (Business) | IT Ops | Same day as Entra | — |
| Okta Verify / MFA | New hire on day 1 | — | Hardware key (YubiKey 5C) shipped with laptop for Engineering |
| Security awareness training (KnowBe4) | Auto-assigned | — | Must be completed in week 1 |

## 4. Accounts — Engineering add-ons

| System | Access level on day 1 | Upgrade path | Approver |
| --- | --- | --- | --- |
| GitHub Enterprise (org `bts-synthetic`) | Member; team repos write | Admin on request | Engineering Manager |
| Azure — dev / staging subscriptions | Contributor | — | Engineering Manager |
| Azure — **production** subscriptions | **None** on day 1 | Read-only after week 4; write via PIM (just-in-time) after probation | Director + Security |
| Databricks workspace | User (dev workspace) | Prod workspace after week 4 | Engineering Manager |
| Confluent Cloud (Kafka) | Developer (non-prod) | — | Engineering Manager |
| Datadog | Standard user | — | Auto |
| PagerDuty | Not added | Added when on-call starts (min. week 6) | Engineering Manager |
| Jira / Confluence | Standard user | — | Auto |
| Cloud dev box (Azure VM, 32 vCPU / 128 GB, Ubuntu) | On request | — | Engineering Manager — lead time 2 business days |

Data team specifics: `data-platform` and `ingest-streaming` GitHub teams; Confluent `ingest-dev` environment; Databricks `dp-dev` workspace.

## 5. Gating rules

1. **No accounts are created** until the background check is received or HR records a formal waiver/conditional start (see offer-policy.md §5).
2. Production access is never granted before week 4, regardless of manager request.
3. Personal phones accessing company email must be enrolled in Intune MDM.
4. Equipment ships to the home address on file unless the new hire opts for office pickup.

## 6. Day-1 IT checklist (template)

- [ ] Laptop imaged, MDM-enrolled, shipped/at desk
- [ ] YubiKey shipped (Engineering)
- [ ] Entra ID + M365 + Slack live; temporary password sent to personal email
- [ ] Role-based add-ons provisioned (§4)
- [ ] Accessibility equipment delivered
- [ ] Hot-desk monitor booked for office days
- [ ] IT orientation session booked (Day 1, 10:00 local, 45 min)
