# Clean installation — Proxmox Easy Script + ERPNext v16

This guide assumes you are discarding the earlier experimental ERPNext site's data and creating a **new LXC/bench/site**. **Do not run destructive commands against a host or other ERPNext instance.** The existing `erp.home.code-eg.com` ERPNext deployment is unrelated and must remain untouched.

## A. Before installing this app

1. Install ERPNext **v16** with your chosen, trustworthy Proxmox helper script in its own LXC, and verify Frappe/ERPNext versions. Verify the helper's actual container OS, Python and bench layout; do not assume `/opt/frappe-bench` or the bench account is always `frappe`.
2. Complete the ERPNext setup wizard: Company = real activity name, Country = Egypt, Currency = EGP, Fiscal Year = your real fiscal year. If you use C.O.D.E., use it consistently in company setup.
3. Keep `fitout.home.code-eg.com` as the *reverse proxy address* through your existing NPMplus host. It is **not necessarily the Frappe internal site name**. Test access and HTTPS via your existing internal network / VPN; do not open unnecessary public ports.
4. Check official Frappe v16 requirements: **Python 3.14, Node.js 24, MariaDB 11.8** (see https://docs.frappe.io/framework/user/en/installation). The Proxmox helper must provide the proper runtime and database versions.
5. Save a Proxmox LXC backup/snapshot and an ERPNext database+files backup before installing or upgrading, even on the new bench. Test restoring a backup as part of staging.

Identify the actual bench and site from inside the **ERPNext LXC** (not the Proxmox host):

```bash
whoami
find /opt /home -maxdepth 4 -path '*/sites/apps.txt' -print 2>/dev/null
# Change this to the bench directory found above:
cd /opt/frappe-bench
bench version
ls -1 sites
bench --site YOUR_REAL_SITE list-apps
```

Confirm that `frappe` and `erpnext` both show v16. `YOUR_REAL_SITE` is a folder within `sites/` (excluding `assets`), not automatically the public FQDN. If the site is already running, get the exact name from its actual configuration; do not copy passwords or secrets into tickets/chats.

## B. Upload source to GitHub

Extract the downloaded ZIP and create a GitHub repository named `code_fitout`, **with `pyproject.toml` at the repository root**. Follow [GITHUB_PUBLISH.md](GITHUB_PUBLISH.md). Tag your first verified release `v0.4.0` after acceptance tests; don't substitute nonexistent tags.

## C. First installation

Run as the **unprivileged bench-owning Linux user**, not `root`:

```bash
cd /opt/frappe-bench  # replace with your actual bench path
bench --site YOUR_REAL_SITE backup --with-files --compress
bench get-app https://github.com/YOUR_USERNAME/code_fitout.git
bench --site YOUR_REAL_SITE install-app code_fitout
bench --site YOUR_REAL_SITE migrate
bench build --app code_fitout
bench --site YOUR_REAL_SITE clear-cache
bench restart
bench --site YOUR_REAL_SITE list-apps
```

If GitHub repo is **private**, `bench get-app` needs configured Git SSH authentication / a read-only deploy key; use the documented SSH URL rather than hardcoding a personal token in command history. If the installation fails, preserve logs and backup and do not wipe/reinstall the site blindly.

**The Python controllers work without activating Frappe Server Scripts**. Leave Server Scripts disabled on a new site unless another trusted app needs them.

## D. First-use checklist

- [ ] `CF Work Category` has 36 specialties, and the supplier groups (Fitout Contractors, Material Suppliers, Site Services) exist.
- [ ] `Mode of Payment` includes InstaPay. Cash/Wire Transfer can be used from the default ERPNext records.
- [ ] `Project` contains the CF property details; `Supplier` has multiple specializations and InstaPay payee fields.
- [ ] Open `CF Work Order`, `CF Cost Record`, `CF Payment`, `CF Owner Movement`, `CF BOQ`, `CF Supervisor`, `CF Supervisor Assignment`, `CF Site Visit`, `CF Stage Template`, `CF Stage Handover`, `CF Trade Handover`, `CF Site Store`, `CF Owner Material Movement` and all nine reports. Workspace dock placement may vary by v16 patch version; the Apps entry and direct routes are fallbacks.
- [ ] Grant user roles: `CF Fitout Editor` for drafts, `CF Fitout Approver` for native Submit/Cancel, `CF Fitout Viewer` for read-only. Keep contractors and owners off these broad roles; there is no row-level owner portal yet.
- [ ] Perform every transaction acceptance test in [TESTING.md](TESTING.md) before entering client balances.

## E. Workflows — optional

Native Submit/Cancel and Python validations work immediately. For explicit `Approve / Verify / Post` actions, source-controlled workflow presets may be provisioned on a test site:

```bash
bench --site YOUR_REAL_SITE execute code_fitout.setup.workflows.configure
```

This creates **inactive** presets. Review their exact states/role permissions and activate **one workflow at a time**, then re-test submission. Do not assume the previous experimental site's Workflows are present in this fresh installation.

## F. App-only upgrades later

```bash
cd /opt/frappe-bench
bench --site YOUR_REAL_SITE backup --with-files --compress
cd apps/code_fitout
git fetch --tags
git checkout v0.4.1  # placeholder: ONLY when a real tested release exists
cd ../..
bench --site YOUR_REAL_SITE migrate
bench build --app code_fitout
bench --site YOUR_REAL_SITE clear-cache
bench restart
```

Do not modify the app's standard DocType schema directly on production. Change source, test, commit and tag new releases. Avoid upgrading ERPNext core and the app simultaneously. Restoring a proven snapshot/backup is your rollback, not `uninstall-app` on valuable data.

## G. New: setup acceptance templates and project stores

`after_install` seeds 36 trade categories plus 122 stage templates automatically and provisions two HTML/Jinja Print Formats (`CF Stage Handover Minutes`, `CF Final Trade Handover`). It never overwrites edits to existing seeded templates. Inspect `CF Stage Template` *before* live usage and approve stages, acceptance criteria, applicable regulations, measurements and test methods for each actual project's specifications.

For each apartment: first create `Project` with its owner (`Customer`) and company. Then create `CF Site Store`:

- **Company-Owned ERP Stock:** Save a store, choose **Create / Link ERPNext Warehouse**, then use normal ERPNext Warehouse/Stock Entry/Material Transfer/Purchase Receipt/Return operations. DO NOT also enter movements in the owner-only ledger.
- **Owner-Owned Operational Stock:** Save an owner-owned store, add ERPNext stock Items as the catalog of material descriptions, and use `CF Owner Material Movement` to record receipts/consumption/returns/transfers. This does **not** affect ERPNext Stock Ledger/GL. Do not link a native Warehouse.

For accepting trades: create a submitted `CF Supervisor Assignment` (if assigned); open `CF Stage Handover`, select stage and project/room, fill checklist and test evidence, print and sign, attach signed scan, and Submit `Accepted` (or record `Rejected` with corrections). When all stages for that trade and room are submitted Accepted, create `CF Trade Handover`, attach final signed minutes and Submit.

**Before live transactions, perform inventory/handover acceptance tests in docs/TESTING.md and confirm browser PDF render quality.**
