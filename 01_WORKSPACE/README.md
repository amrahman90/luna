# 01_WORKSPACE — All New & Future Work

Every document, script, index, and deliverable created from 2026-08-19
onward lives somewhere inside this folder. The project root and
`00_SOURCE_ORIGINALS/` never receive new files.

| Subfolder  | Contents                                                         |
|------------|------------------------------------------------------------------|
| `plans/`   | New plan versions (v6+), roadmaps, gate reports, pivots          |
| `notes/`   | Working notes, prior-art matrix, literature reading notes        |
| `code/`    | Scripts and pipelines (WP0 scope-map, depression primitive, etc.)|
| `data/`    | Dataset indexes, download manifests, licence audit records      |
| `papers/`  | Paper drafts, figures, submission packages                       |
| `admin/`   | Budget logs, infrastructure records, meeting notes               |
| `luna-web/`| Public portal (git submodule → `Ahnaf181419/luna-web@main`).     |
|            | React 19 + Vite 8 SPA, auto-deploys to GH Pages. Edits inside    |
|            | the submodule are committed to luna-web's own repo; parent-side |
|            | pushes do not trigger deploys.                                  |

Conventions:
- Prefix working files with ISO date: `YYYY-MM-DD_<topic>.<ext>`.
- Markdown (`.md`) is the default format for new documents.
- A new plan version must state in its header which version it supersedes
  (current authoritative: `00_SOURCE_ORIGINALS/LUNARVOID_Master_Plan_v5_Full_Synthesis.txt`).
- Raw data downloads never live here long-term — record what, where, and
  licence status in `data/`, keep the bytes on the analysis machine.

Submodule workflow (`luna-web/`):
- Clone with submodules: `git clone --recurse-submodules <repo>`. If you
  already cloned without that flag, run `git submodule update --init --recursive`.
- Portal edits are committed inside `01_WORKSPACE/luna-web/` and pushed to
  `Ahnaf181419/luna-web` (the submodule's remote) to trigger GH Pages
  deploys. Pushing to the parent does **not** deploy.
- After committing inside the submodule, record the new pointer in the
  parent: `git add 01_WORKSPACE/luna-web && git commit -m "bump luna-web"`.
- Or do it one-shot from the parent root: `git submodule update --remote`.
