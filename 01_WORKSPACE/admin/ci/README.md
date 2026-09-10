# Staged CI workflow (task E4) — NOT ACTIVE

`ci.yml` = GitHub Actions: on push/PR to master -> checkout -> Python 3.12 ->
pinned freeze install (incl. the pulearn `--no-deps` quirk, see the install
step comments) -> smoke test -> `pytest 01_WORKSPACE/code/tests/ -q`.
Local-data tests (real-data E2E, analog npz verifiers) auto-skip with
reasons; no secrets; PyPI is the only network use; free-tier minutes only.

To activate (requires a user-approved exception to the AGENTS.md
root-clean rule — the repo root has no `.github/` today):

    mkdir -p .github/workflows
    cp 01_WORKSPACE/admin/ci/ci.yml .github/workflows/ci.yml
    # or symlink: ln -s ../../01_WORKSPACE/admin/ci/ci.yml .github/workflows/ci.yml

Delete the copy (or the symlink) to deactivate. No cost trigger is
involved — this is Tier-0 ($0) per the budget discipline.
