# C.O.D.E. Fitout Management (`code_fitout`)

**Source release candidate v0.4.0 — fresh ERPNext / Frappe v16 installation.** Independent, version-controlled Frappe app for Egyptian apartment fitout, resident/visiting supervision, staged work acceptance, project site stores and mixed owner/personal/company funding.

**Testing status:** All Python/JSON source parses and local static/SQL tests pass. **No real ERPNext v16 bench/MariaDB end-to-end installation or workflow test has been performed here.** Validate on a fresh **test site** before using real payments, stock or signed acceptance records. Not a statutory accounting or code-certification system.

## Installation and source guides

- [Proxmox / ERPNext v16 clean install](docs/INSTALL.md)
- [What is implemented / not implemented](docs/SCOPE.md)
- [Arabic daily use](docs/USER_GUIDE_AR.md)
- [Required acceptance tests](docs/TESTING.md)
- [Legal, privacy and accounting safeguards](docs/SECURITY_AND_ACCOUNTING.md)
- [Publish and upgrade via GitHub](docs/GITHUB_PUBLISH.md)

## Included features

| Area | Implementation |
|---|---|
| Apartment / owner | ERPNext `Project` + `Customer`, custom property fields |
| Contractors and suppliers | ERPNext `Supplier`, 36 seeded specialties, multiple specialties per supplier, InstaPay recipient details |
| Contracts & quantities | `CF Work Order`, `CF BOQ` / `CF BOQ Line`, planned vs actual reports |
| Certified costs | `CF Cost Record`: materials, labor, project, supplier and work category |
| Contractor payments | `CF Payment` / `CF Payment Allocation`: part-payments, InstaPay, payer, funding source, advances |
| Owner/personal funds | `CF Owner Movement`: held receipts, refunds, recoverables, same-owner project transfers |
| Resident / visiting supervision | `CF Supervisor`, `CF Supervisor Assignment`, `CF Site Visit` daily logs/visits |
| Supervision revenue | `CF Supervision Agreement` with optional native Sales Invoice link |
| Trade acceptance templates | **122 editable stages** across **36 work categories**; three inspection checks per stage |
| Handover minutes | `CF Stage Handover` with checklist, tests, defects, photos, reinspection, signed print format; `CF Trade Handover` consolidating accepted stages with final signed print format |
| Project stores | `CF Site Store` linked to a project: company-owned ERPNext Warehouse or separate owner-owned operational store |
| Owner material quantities | `CF Owner Material Movement` / `CF Owner Material Line`: receipt, consumption, supplier return, same-owner transfer, adjustments, stock balance checks |
| Reports | **9 Script Reports** covering contractor, project, owner funds, payment, BOQ, commitments, supervision, accepted stages and owner-material quantities |
| Controls | Frappe roles/Submit/Cancel, server-side controllers, project/record locking, evidence requirements |

**No separate Server Scripts are needed**. Business logic is in app source. All documents can be updated through future GitHub releases and `bench migrate`.

## Daily operating sequence

1. Create your ERPNext **Company** (EGP), **Customer** (owner), **Project** (apartment), **Supplier**, work orders and BOQ.
2. Assign a **Resident** or **Visits** supervisor using `CF Supervisor Assignment` and record visits in `CF Site Visit`.
3. Create a `CF Site Store` for each project. For company stock use native ERPNext Warehouse, Purchase Receipts and Stock Entries. For owner-owned materials use the **operational** material ledger (no GL postings).
4. Record `CF Cost Record` on approved completed works. Accept each building/finishing stage using `CF Stage Handover`; print, sign and scan its minutes. At the end of each trade/area prepare `CF Trade Handover`.
5. Record owner funds with `CF Owner Movement` and supplier payments/allocations with `CF Payment` after actual settlement. Submit, don't backfill dummy payments.
6. Open financial, progress, supervision and material balances in the nine reports.

## Core caveats

- **Owner-owned material is not company inventory.** Use the owner-material ledger only; do not create stock/GL postings for a legal owner without accountant-reviewed transactions.
- Cross-project owner materials can move automatically **only between projects of the same owner** and with signed transfer/receipt evidence. Company-owned stock transfers use ERPNext native Stock Entry/Material Transfer.
- Handover acceptance criteria are **illustrative editable checklists**. Engineer-approved design, specifications, specialist tests and applicable law supersede them; no numeric code tolerances are invented.
- A printed PDF contains signature lines, but only a signed original/scan is proof. Digital checkboxes are not electronic signatures.
- Owner/contractor accounts, legal tax, VAT, escrow and payroll are not automatically posted to ERPNext General Ledger. Native accounting needs proper reconciliation.
- No automatic external InstaPay transfer, vendor portal, biometric attendance, full batch/serial/lot stock valuation or owner-specific row-level portal is implemented.

## Main routes after installation

- `/app/cf-work-order`, `/app/cf-boq`, `/app/cf-cost-record`, `/app/cf-payment`
- `/app/cf-owner-movement`, `/app/cf-supervision-agreement`
- `/app/cf-supervisor`, `/app/cf-supervisor-assignment`, `/app/cf-site-visit`
- `/app/cf-stage-template`, `/app/cf-stage-handover`, `/app/cf-trade-handover`
- `/app/cf-site-store`, `/app/cf-owner-material-movement`
- `/app/query-report/CF%20Handover%20Progress`
- `/app/query-report/CF%20Owner%20Material%20Balance`

See the nine report definitions under `code_fitout/code_fitout/report/`. The Frappe v16 Apps-screen entry is included; dock/sidebar arrangement may differ by installed v16 patch.

**License:** MIT. Independently developed and not supported or endorsed by ERPNext/Frappe.
