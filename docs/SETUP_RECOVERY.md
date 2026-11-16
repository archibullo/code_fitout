# Automatic initialization / recovery (v0.4.1)

After installing the Frappe/ERPNext app, default records are created by `after_install` if ERPNext already has its master data. If the company or Supplier Group root is created later, the app now seeds missing supplier groups via `Company.after_insert`, `Supplier Group.on_update` (root group only), and `setup_wizard_complete`. Every `bench --site SITE migrate` also performs an idempotent repair.

Existing records are left untouched; only missing `Fitout Contractors`, `Material Suppliers`, and `Site Services` Supplier Groups are inserted as leaf groups under `All Supplier Groups`. The ERPNext root group is never created or renamed by this app.

## Upgrade an existing test site

Run as the Bench owning user, not root, and only after committing the files to the GitHub repository:

```bash
cd /opt/frappe-bench/apps/code_fitout
git status --short
git pull --ff-only upstream main
cd /opt/frappe-bench
bench --site site1.local migrate
bench --site site1.local execute code_fitout.setup.install.setup_status
bench --site site1.local list-apps
```

Expected `supplier_groups` values: all `true`. Expected `work_categories=36`, `stage_templates=122`, and both handover print formats `true`. The diagnostic is read-only and must not be mistaken for an end-to-end functional acceptance test.

## Fresh-site timing tests

1. Install `code_fitout` before setting up any company; ERPNext root Supplier Group absent. The app should install normally without manufacturing a dummy root group.
2. Complete the Setup Wizard or create the company; the missing groups appear automatically when the root becomes available.
3. Run the setup hooks and `migrate` repeatedly; counts remain constant and existing group settings are untouched.
4. Check specialization selection, InstaPay and supplier creation through the UI.
5. Confirm `setup_status` and handover templates. Do **not** run bench update as part of this fix.

Do not force site installation, uninstall the app or delete any real data to repair missing master records.
