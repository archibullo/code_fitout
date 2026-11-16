# Changelog

## 0.4.1 — Setup lifecycle reliability (2026-11-16)

- Added automatic, idempotent Supplier Group initialization when ERPNext setup wizard finishes, a company is created, or the root Supplier Group is updated.
- Kept `after_install` and `after_migrate` repair hooks. Existing Supplier Groups and edited inspection templates are not overwritten.
- Added the read-only `code_fitout.setup.install.setup_status` diagnostic and regression tests.
- Preserved the working Frappe v16 Apps-screen route from the latest GitHub `main` branch.
- Verified by offline unit tests; fresh-site integration testing is still required.


## 0.4.0 — Supervision, staged handovers and site stores (2026-11-15)

- Added resident or visiting supervisors, per-project assignments, site visit logs and coverage reporting.
- Added 122 editable stage templates for 36 trades, stage-by-stage inspections, hold points and printable signed handover minutes.
- Added final trade handover documentation, stage ordering and cancellation protections.
- Added per-project site stores with native ERPNext Warehouse links for company stock.
- Added separate owner-owned material quantity ledger for receipts, consumption, returns and same-owner project transfers.
- Added owner material balance and handover progress reports; now nine Script Reports.
- Expanded structure checks and staging acceptance checklists.
- **Not yet installed, runtime-tested, or financially certified on a live Frappe/ERPNext v16 environment.**

## 0.2.0 — Clean ERPNext v16 release candidate (2026-11-15)

- Removed legacy hand-built DocType migration paths and old-data references; installation is for a new ERPNext v16 site.
- Added `CF Work Order` and an approved-contract ceiling check on linked certified costs.
- Added `CF Site Visit` for supervision, issues, follow-up and site photos.
- Added six Project metadata fields, retained shared Supplier specialization and InstaPay payee fields.
- Added owner-held inter-project transfers restricted to two Projects belonging to the same Customer, with target-funds cancellation guard.
- Added `CF Contract Commitments` as the sixth report and transfer detail to owner balance reporting.
- Added v16 Apps-screen hook, removed deprecated app-level `workspace_sidebar` files; module navigation falls back to Frappe's generated sidebar.
- Improved BOQ handling of fractional quantities; validated supervision agreement against Project Customer.
- Expanded source tests, installation/acceptance docs and non-accounting scope disclosures.

**Not yet integration-tested on a running ERPNext v16/MariaDB instance.** Do not represent this as production-audited accounting software.

## 0.1.0 — Initial prototype

- Project/Supplier integration, BOQ, operational costs/payments, owner movements, supervision agreement, five Script Reports.
- Source-level validation and optional Workflow scaffolding.

## 0.4.0 — Stage acceptance, final minutes, stores and material transfers (release candidate)

- 122 trade acceptance stages covering all 36 work categories, editable with bilingual labels.
- Handover inspections, approved-stage sequencing, mandatory checklist/test evidence, reinspection and cancellation locks.
- Bilingual per-stage and final trade handover print formats with signed-scan evidence.
- Resident or visiting supervisor assignment supported in inspection records.
- Project site stores integrating native ERPNext Warehouse for company stock.
- Independent owner-owned materials quantity ledger with receipts, consumption, returns, same-owner cross-project transfers, adjustments and locking against negatives.
- Added acceptance progress and owner-material balances (nine Script Reports total) and expanded staging checks.

**Release is not yet validated on a live Frappe v16 bench and should first be installed on a test site.**
