# Upgrade from v0.4.0 to v0.4.1

This patch fixes master-data initialization timing on newly installed ERPNext v16 sites. The three Supplier Groups are created after the company/root group appears, and missing groups are repaired by `bench migrate`.

## Apply source changes to GitHub

If using the **hotfix-only** ZIP, overlay its contents at the repository root, preserving directories and committing the changes. If using the complete source ZIP, replace the repository tree with the extracted contents and commit. Do not put the ZIP itself in the repository as the application source.

**Changes:**
- `code_fitout/hooks.py`
- `code_fitout/setup/install.py`
- `code_fitout/__init__.py`
- `pyproject.toml`
- `README.md`
- `CHANGELOG.md`
- `docs/SETUP_RECOVERY.md` (new)
- `docs/UPGRADE_0.4.1.md` (new)
- `tests/test_setup_lifecycle.py` (new)

The current working Apps-screen route is preserved. No old data is migrated or deleted.

## Update installed app

Run commands below as the `frappe` Linux user in the container. Inspect `git status` first and do not overwrite local modifications.

```bash
cd /opt/frappe-bench/apps/code_fitout
git status --short
git pull --ff-only upstream main
cd /opt/frappe-bench
bench --site site1.local migrate
bench --site site1.local clear-cache
bench restart
bench --site site1.local list-apps
bench --site site1.local execute code_fitout.setup.install.setup_status
```

Expected: `code_fitout 0.4.1`, all three supplier group flags true, 36 work categories, 122 stage templates, two print formats, InstaPay true.

## Verify in ERPNext

Open existing Supplier `TEST HVAC Contractor`. Select `Fitout Contractors`, save and reopen. Select two work categories using `Specializations (C.O.D.E. Fitout)` and save/reopen. Neither company accounts nor previous payments are changed by this patch.

## Testing limits

The package underwent offline unit/source tests, not a Frappe database integration test. The hook timing must be tested on a fresh test site once the patch has been applied.
