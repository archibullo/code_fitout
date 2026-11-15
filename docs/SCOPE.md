# Function and design audit — v0.4.0 clean install

This inventory describes **implemented source** versus features intentionally **not implemented**. It is not proof that the app has been installed successfully on a running Frappe v16 site.

| Requirement | Source implementation / boundary |
|---|---|
| Owner with one or many apartments | ERPNext Customer linked to one Project per apartment; Project fields for address/building/unit/floor/budget/scope |
| One contractor across many sites | One standard Supplier; all costs/payments reference it; multi-specialty supplier selector |
| Contractor agreement and balance | CF Work Order: initial amount, amendments agreed *before Submit*, retention percent for information, signed document; CF Contract Commitments report |
| Material and labour costs | CF Cost Record (Materials, Labor, Subcontracted Services, Site Expenses, etc.), optional BOQ and Work Order |
| BOQ and budget comparison | CF BOQ/Line with quantities, rates and CF BOQ Budget report |
| Cash/InstaPay/bank transfer | ERPNext Mode of Payment; InstaPay seeded. Payee identifiers on Supplier; source bank is an **informational** field |
| Mixed payments by owner, by individual or company | CF Payment with Paid By, Funding Source, reference and optional proof |
| Supplier advances and partial payments | CF Payment/Allocation; allocated and unallocated amounts, submitted payment validations |
| Single transfer for several costs | Multiple allocation rows, potentially several projects. Owner-held/personal funded payments are limited to **one project per operational payment** to keep owner ledgers correct; split a real cross-project transfer into per-project CF records with reconciliation notes |
| Owner paid supplier directly | CF Payment, Owner Paid Directly. Not counted as cash received/paid by C.O.D.E. |
| Owner money temporarily held by individual | CF Owner Movement; held balance checked on submit |
| Reimbursements of user's personal outlays | CF Owner Movement; recoverable computed separately and checked on submit |
| Reallocate held funds between apartments of same owner | CF Owner Movement Transfer Held Funds to Another Project, source and target balances checked; different owners rejected |
| Site staffing | CF Supervisor (optional User/Supplier) and CF Supervisor Assignment per apartment with Resident or Visits mode, date range, planned frequency, compensation reference and duties |
| Site supervision | Submitted CF Site Visit daily logs / scheduled visits / emergency visits with assigned supervisor, photos, findings, follow-up, Task |
| Supervisor coverage | CF Supervision Coverage report of reported days/visits and informational per-visit fee estimate; does not create payroll or financial payments |
| Supervision fee | CF Supervision Agreement Fixed/Percentage; Sales Invoice linked manually; legal revenue handled by ERPNext accounting |
| Reports | Contractor Balances, Project Statement, Owner Balance, Payment Register, BOQ Budget, Contract Commitments, Supervision Coverage |
| Access and history | App roles, Submit/Cancel, document audit trail; no owner portal and no site-by-site permission partition yet |
| GitHub upgrades | Python controllers/JSON doctypes/reports/custom fields all versioned; bench migrate applies updates |

## Important limits before using real money

1. **The app is an operational project ledger**, not GL / statutory accounting. No automatic invoices, VAT, Egyptian tax calculations, withholding certificates, or bank reconciliation.
2. Retention percentage is a **contractual reference only**; deduction/release schedule is not implemented. To reserve retention, leave part of an approved cost unpaid and document the terms manually until a controlled retention module is added.
3. Post-submission contractual variations: submit a **separate supplemental CF Work Order** referencing the original contract in notes, rather than editing a submitted Work Order. A dedicated variation-order UI and retention release are next-phase features.
4. There is no direct InstaPay API transfer or Android SMS reader. Captures payment method, payee, proof and reference only.
5. No row-level client portal or role-restricted confidential bank field access per customer. Use trusted staff users only; do not grant app role access to owners or contractors.
6. A real transfer covering **multiple owners** must be split into per-owner/per-project operational records. Duplicate-transfer rules are deliberately strict; see the user guide.
7. Company stock uses ERPNext Stock/Items/Purchase Orders; owner-owned material quantities use the separate operational site-store ledger. App does not automatically convert operational costs to ERPNext Stock Ledger or General Ledger.
8. Resident attendance is *reported* through daily site logs, not biometric/verified attendance. Planned visits are not automatically scheduled. Fees are operational estimates, not payroll/GL costs.
9. Site visits estimate percent complete independently of BOQ physical quantities; automated weighted milestone progress and client-facing project dashboards remain follow-up features.
10. All cost, bank and budget values in this app are EGP. Multi-currency would require dedicated FX logic.
11. Workflows with branded Approve/Verify labels are **opt-in**, while native Submit/Cancel works immediately.
12. No old-data import: this release is intentionally scoped to a **fresh bench**.

A separate sandbox acceptance test is required for actual Frappe 16 patch/OS/DB behavior, including file upload permissions, row locking, cancellation/amendment and v16 module/dock display.

## Acceptance, handover and project stores (v0.4)

| Requirement | Implementation / boundary |
|---|---|
| Standard construction finishing stages | 122 predefined stage templates covering all 36 seeded work categories; customized by trade and sequence; *not a substitute for a consultant/authority-approved code or approved technical specifications*. |
| Every-stage signed minutes | `CF Stage Handover` with results, technical measurements, photos/tests, inspector and contractor/owner representatives, rejected findings, reinspection and signed scan; printable `CF Stage Handover Minutes`. |
| Final trade/package handover | `CF Trade Handover` validates the full accepted stage set for a trade/project/area, snapshots their reference numbers, and prints `CF Final Trade Handover` with signatures. |
| Stage precedence and cancellation | Next-stage acceptance is blocked unless all earlier active stages for that zone are accepted; cancelling an earlier accepted stage is blocked if later accepted stages or final handover depend on it. |
| Multiple resident/visiting supervisors | `CF Supervisor` + submitted `CF Supervisor Assignment`; `CF Stage Handover` can reference assigned supervisor, which must match project/date. |
| Company-owned site warehouses | `CF Site Store` optionally creates/links a standard ERPNext Warehouse under the company root; use native Stock Entry, Stock Balance, Purchase Receipt and supplier returns for real stock/GL handling. |
| Owner-owned site stores | Separate operational quantities via `CF Owner Material Movement` + `CF Owner Material Line` (Receipt, Consumption, Return, Transfer, +/- adjustment). Signed evidence required for receipts/returns/transfers/adjustments; balances guarded against negatives. |
| Leftover materials transfer | Company-owned: ERPNext Material Transfer between project warehouses; owner-owned: `CF Owner Material Movement` Transfer allowed between stores belonging to the same Customer only, with receiving confirmation and signed proof. |
| Real stock audit boundary | Operational owner materials are *not* in ERPNext Stock Ledger or General Ledger. Batch/serial/expiry, valuation, owner-to-owner sales, stock booking and tax treatment require separate approved processes. |

**Implementation notes:** Stage tests are consultant-configurable, not definitive safety certificates. Generated HTML print formats still require browser/PDF rendering acceptance on installed v16. Native ERPNext quality inspection handles inbound stock items, not these building-work handover stages. Acceptance, warehouse transfer concurrency and final print output need live staging tests.
