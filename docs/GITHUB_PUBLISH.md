# Publish clean v0.2.0 to GitHub

1. Download and extract `code_fitout-v0.2.0-clean-install-source.zip` to a **new local folder**. Verify that `pyproject.toml`, `code_fitout/hooks.py`, `docs/INSTALL.md`, `LICENSE`, and `code_fitout/code_fitout/doctype` are immediately inside its root.
2. Create a repository named **`code_fitout`** on GitHub, preferably private until the code has passed integration acceptance on your Proxmox test site. Do not push passwords, owner data, receipt images, `site_config.json`, site backups or payment identifiers.
3. From the extracted repo root (on any development computer with Git installed):

```bash
git init
git branch -M main
git add .
git commit -m "Initial clean ERPNext v16 fitout app v0.2.0 RC"
git remote add origin git@github.com:YOUR_USERNAME/code_fitout.git
git push -u origin main
```

4. On the new bench follow `docs/INSTALL.md`. A private repository requires a read-only SSH deploy key accessible to the bench installation user, or temporary authorized developer credentials; never place GitHub PATs in a public terminal transcript.
5. Once installation, full `docs/TESTING.md` and backup restore pass, tag and push a released version:

```bash
git tag -a v0.2.0 -m "C.O.D.E. Fitout 0.2.0"
git push origin v0.2.0
```

6. Future changes should be committed on a branch, tested on a restored/staging site, then version-bumped in `pyproject.toml` and `code_fitout/__init__.py`, tagged after review. Use `bench migrate`, not ad-hoc Server Scripts on production, to apply schema/report upgrades.

CI in `.github/workflows/static-checks.yml` runs static Python and SQL smoke tests only. It does not prove Frappe/ERPNext DB compatibility.
