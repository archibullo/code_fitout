# ERPNext v16 staging acceptance tests — MUST RUN BEFORE LIVE DATA

These **cannot be replaced by static CI tests**. Use a fresh test site and dummy Company/Customer/Project/Suppliers; capture outputs, screenshots, and the installed `bench version`. Retain a verified backup/restore point.

## Installation & navigation

- [ ] Run `bench --site SITE install-app code_fitout` and `bench --site SITE migrate` without errors; `bench --site SITE list-apps` lists code_fitout.
- [ ] 36 seeded work categories, Supplier groups, InstaPay Mode of Payment, Project detail fields, Supplier specialties & payee fields exist.
- [ ] Open all main standalone DocTypes, the public workspace, and **all nine reports**. If Apps icon/dock isn't visible on that v16 patch, use direct routes and document the discrepancy (not a reason to change accounting schema).
- [ ] CF Fitout Editor cannot submit; CF Fitout Approver can submit/cancel; CF Fitout Viewer cannot create/edit. Owners/contractors get no broad app role.

## Contracts, BOQ, site progress

- [ ] Create BOQ with fractional quantity e.g. 0.125 and rate 1000 = 125.00; Submit and check budget report.
- [ ] Create Work Order 1,200 EGP, Project A, Supplier A, optional signed document; Submit. Create approved cost 1,000 linked to it. Trying another 300 on same order should **fail** unless an additional authorized contract is recorded or the order had explicit overrun flag.
- [ ] Work Order cannot be cancelled with submitted linked costs. A cost cannot point to a different project or supplier's Work Order, nor to draft Work Order.
- [ ] Site Visit records observations, photo, follow-up, Project Task link; reject linking Task from a different Project.
- [ ] Supervision Agreement only links the Project's Customer; fee calculation matches fixed/percentage; any linked Sales Invoice belongs to same Customer.

## Cost, payment, owner funds

- [ ] Submit Cost 1,000 EGP under Project A, Supplier A; Draft costs excluded from reports. Submitted costs cannot be edited.
- [ ] Submit verified payment 700 EGP allocated to that cost; Contractor Balances: approved 1,000, paid 700, outstanding 300. Payment without allocation is an advance tied to a Project.
- [ ] Payment 400 against same cost fails; 300 passes. Duplicate reference for same supplier+method fails. Cost cancellation fails while submitted payments remain.
- [ ] Payment with mismatched Supplier or Project fails; payment funded personally / from owner's held funds with blank Project fails. One owner-paid-directly payment cannot cover costs of two different owners.
- [ ] Owner funds receipt 1,000, owner-funded payment 800 succeeds, further payment 300 fails. Refund 100 succeeds, refund another 200 fails; cancelling original receipt while money was spent fails.
- [ ] Personal payment 500 EGP increases recoverable 500; direct reimbursement 200 leaves recoverable 300; over-reimbursement 400 fails.
- [ ] Transfer 100 EGP held funds from Project A to Project B for SAME Customer. Source owner balance reduces 100; target rises 100. Transfer across different Customer fails; cancelling a transfer after target spent it must fail.
- [ ] Simultaneous submits by two users against same cost or held funds should never allow a combined overpayment. Review retry/deadlock outcomes and logs.
- [ ] Cancelled payments, costs, owner movements are excluded from reports. Test amendment corrections and no invalid negative balances.
- [ ] Audit that **no standard ERPNext GL, bank account or Payment Entry** is created solely by submitting CF operational documents.

## Reporting, backups, and release gate

- [ ] All nine Script Reports execute on Frappe v16 with realistic records and return accurate totals: contractor across projects, project statement, owner balance incl transfers, payment register, BOQ budget, contract commitments.
- [ ] Verify `Payment Register` shows allocated rows and unallocated advance once, without double counting.
- [ ] Test private attachments, role permissions, and a normal user who has no Company bookkeeping role.
- [ ] Produce off-LXC backup; successfully restore to another test environment.
- [ ] Confirm GitHub tag, installed app version and tested Frappe/ERPNext v16 patch versions before releasing for live use.

Static checks from the source root:

```bash
python -m compileall -q code_fitout
python -m unittest discover -s tests -v
```

Only after **all** necessary acceptance checks pass should you treat the operational records as reliable for day-to-day business use. Independent accounting/tax requirements remain outside app scope.

## Mandatory staged handover tests (v0.4)

- [ ] 122 active stage templates across all 36 work categories are installed; checklist content editable before any submitted acceptance, template changes affecting accepted work blocked.
- [ ] Create a project, Supplier and (optional) submitted resident/visit Supervisor Assignment; stage checklist auto-populates from selection and Arabic/English headings display.
- [ ] For an electrical circuit zone, inspect stage 2 before stage 1: Accepted Submit must fail. Accept stage 1 with required inspections, attachments and signed scan, then stage 2 succeeds.
- [ ] A mandatory Fail or missing mandatory test photo fails Accepted Submit. Reject an inspection with documented deficiencies; create linked Reinspection after repair.
- [ ] Duplicate Accepted stage for same project + trade + zone is blocked. Approved stage cannot be cancelled while later accepted stage or submitted final trade minutes depend on it.
- [ ] Generate/print `CF Stage Handover Minutes` and `CF Final Trade Handover` (browser and PDF). Signatures, Arabic text, check rows, statuses and dates must all render legibly.
- [ ] Final trade handover cannot submit until *all active* stage templates for that trade and zone are Accepted; signed scan required.

## Mandatory warehouse and material movements tests (v0.4)

- [ ] Create two Projects for the same owner and a third Project for a different owner. Create an owner-owned store for each and company-owned ERP Warehouses for a company Project.
- [ ] Owner goods: receipt 50 units to site A; consumption 20 => 30 on hand; transfer 15 to site B with signed receipt => A=15, B=15; return 5 from A => A=10.
- [ ] Consumption 11 from site A fails; receipt minus quantity or duplicate item lines fail; changing site ownership with posted movements fails.
- [ ] Transfer from owner A's site to another owner's site fails. Transfers require receiver acknowledgment and signed proof; returns/adjustments require reason/proof.
- [ ] Try cancelling receipt of 50 after consumption and transfer: must fail when it would create negative balances. Cancel transfers in reverse sequence and re-check on-hand quantities.
- [ ] Two concurrent deductions that individually pass but together exceed stock cannot both submit; test with two users on real MariaDB.
- [ ] Company-owned project: use standard ERPNext `Stock Entry -> Material Transfer` between two project warehouses; check Stock Ledger and Bin quantities. Purchase Return/supplier credit must be handled by ERPNext's standard purchase return path.
- [ ] Confirm owner operational movements **do not affect** ERPNext stock ledger, balance sheet, warehouse valuation or payment entries.
- [ ] Physical count reconciliation, backdating, VAT treatment, lot/serial tracking and accounting valuation must be approved and tested separately if required.
