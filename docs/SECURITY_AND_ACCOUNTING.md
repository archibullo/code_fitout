# Financial accounting, privacy and security boundaries

- All `CF ...` transactions are **operational evidence**, not journal entries in ERPNext General Ledger. Submit **does not** move money. The real payment must already have happened; retain a receipt/photo/reference.
- `Owner Paid Directly` never touches your personal/company cash balance. `Owner Funds Already Received` reduces that project's held-funds balance. `Personal Funds - Recoverable` increases that project's personal recoverable amount. `C.O.D.E. Operating Funds` is a source label, not an automatic Payment Entry.
- Owner advances received, refunds, personal reimbursements and same-owner inter-project held-fund transfers are `CF Owner Movement` entries. The owner-fund report includes only Submitted entries and Submitted payments. Refunds, transfers and reimbursements must not be entered as additional contractor payments.
- Submitted cost/payment/owner movements are immutable in standard UI. Use Cancel/Amend as authorized, and keep PDF/bank proof. The Python controllers reject cost cancellation where submitted payments remain, and prevent obvious over-allocations / negative owner-held funds. **Race behavior and all cancellation sequences must still be proved on a real MariaDB/Frappe 16 staging site.**
- `CF Work Order` is an operational contract record, not ERPNext Purchase Order or company liability. `retention_percent` is descriptive. If C.O.D.E. legally acts as principal contractor, enter appropriate real Purchase Invoices, Payment Entries, Sales Invoices and taxes natively (with accountant approval), and reconcile links.
- No owner-facing account portal exists. The Viewer/Editor/Approver roles can view multiple owners' operational records. Keep access limited to trusted staff. Don't issue login to contractors or apartment owners using those roles. Configure Frappe File private attachment settings and review Supplier payee field access before onboarding staff.
- The existing network's HTTPS and VPN access policies should be maintained. Do not expose an administrator interface publicly solely because of this app. Make regular database+attachments backups and independent Proxmox LXC restore points.
- This release intentionally **does not require enabling Server Scripts**, reducing unnecessary permissions on the new bench.
- For simultaneous transactions, submitted payments lock involved cost and project records; owner movements lock their source and target project. Test on the exact installed MariaDB and Frappe patch version. Operational ledger tests cannot substitute for an accounting review.

## Construction acceptance and material custody

- Handover checklists are editable site acceptance aids, not statutory certifications. Engineer-approved drawings, material submittals, relevant codes and applicable specialist test certificates control the actual pass/fail criteria.
- Submitted accepted stages and final handovers are immutable in the normal UI, with paper signatures/scans as evidence. A checkbox on its own is not a cryptographic signature. Ensure files are private and accessible only to authorized project staff.
- Owner-supplied goods are **not assets of C.O.D.E.** merely because they are in your custody. `CF Owner Material Movement` is an operational item-quantity ledger and does not create stock valuation, tax deductions or GL entries.
- Company-owned site stock uses native ERPNext Warehouse and Stock Entry, which may have accounting effects. Do not also mirror those quantities as owner-owned material movements.
- Material movements across different owner identities are blocked in the owner ledger. Real ownership transfers require written approval, reconciled valuation and separate return/receipt documentation.
- Backdated movements and physical stocktake are not represented as a full certified inventory audit; reconcile actual counts at go-live and regularly thereafter.
