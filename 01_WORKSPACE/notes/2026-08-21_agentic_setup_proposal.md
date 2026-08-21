# Agentic setup plan for LUNARVOID — review draft

**Date:** 2026-08-21
**Status:** SUPERSEDED — the opencode-native agentic setup was built
and committed (see `.opencode/` agents/commands/skills + commit
"Agentic setup: 5-role agent team..."). The valuable parts of THIS
proposal were adopted on 2026-08-21: verification-matrix wiring,
T5 reproduction stop-trigger, skeptic role (from research_agent_demo),
headless pipeline (admin/orchestrator/, manual-only), findings log,
candidate registry. NOT adopted: PDS MCP wrapper (would bypass the
manifest/SHA-256 audit trail), GitHub MCP (push stays parked on
amrahman90/luna). The `lunarvoid-lltb1-build` skill content from
~/.hermes/ was ported into `.opencode/skills/lunarvoid-conventions/`
(single source of truth). Kept for the record.
**Goal:** set up a complete agentic workflow so a fresh agent
opening this repo can pick up where we left off, run the
verification scripts, regenerate the deliverables, and push
forward to Paper 2 — with minimal back-and-forth.

---

## TL;DR (decisions you need to make before I do anything)

These are the only questions blocking a complete setup. The rest
of this document is the proposal; below is the compact list.

1. **Where should the agentic setup live?** Three options:
   - (A) Inside this repo as `.agent/` (committed to `master`)
   - (B) Outside, in `~/lunarvoid/agent/` (per AGENTS.md's
     "raw/derived separation")
   - (C) Inside this repo as `.agent/` but in a separate branch
     (so `master` stays "what the paper submits")
2. **Which MCPs (if any) should I add?** Three candidates below:
   - Filesystem MCP (probably not needed — I have native `read_file`
     and `write_file` tools)
   - GitHub MCP (if you want push/PR flow to come back online)
   - NASA PDS / LROC search API MCP (for the lunar inference,
     Paper 2)
3. **Skill-rotation policy?** When a skill gets out of date, do I:
   - (A) Patch in place
   - (B) Bump version + read CHANGELOG
   - (C) Both
4. **Anything else you want to bundle** (sub-issue tracker, a
   pre-commit hook that runs the verification scripts, a CI
   stub, etc.)?

---

## 1. Skills already in place — audit

From `~/.hermes/skills/`:

| Skill | Status | Notes |
|---|---|---|
| `software-development/lunarvoid-lltb1-build` | v1 (last patched for v0.4) | Operational know-how for the LLTB-1 build. Covers env, pipeline, all 8 bugs-found-and-fixed. This is the project's "main" skill. |
| `delegate-coding-agent` | bundled | For spawning subagents. |
| `autonomous-ai-agents` | bundled | For orchestrating multi-agent workflows. |
| `creative/*` (ascii-visuals, baoyu-infographic, etc.) | bundled | Not relevant for this research project. |
| `data-science/jupyter-live-kernel` | bundled | Useful for the data-exploration loop once we move to Paper 2 inference. |
| `mlops/*` (llama-cpp, vllm, etc.) | bundled | Premature; v5 plan is "inference" but using physical-priors models, not LLMs. |

What's missing from the skills inventory for a research project:

- **research/arxiv** — exists, useful for finding related work.
- **research/blogwatcher** — exists, useful for monitoring the
  ESSA / Robinson / Wagner preprint activity (the close competitors
  v5 plan §1 names).
- **research/llm-wiki** — exists, useful for building the project's
  own interlinked KB. Probably not needed for v0.x.
- A new **research/lunarvoid-context-pack** skill (built today
  essentially as this document + the existing skill).

So the skill coverage is reasonable. The main recommendation is
**one new skill: `research/lunarvoid-runbook`** that consolidates
"what to do when an agent opens this repo cold" into one place.

---

## 2. MCPs (Model Context Protocol servers)

You mentioned "any new MCP needed". My honest answer:

**Most of what an agent needs is already covered by native Hermes
tools** (`read_file`, `write_file`, `patch`, `terminal`,
`search_files`, `session_search`, `execute_code` for Python, etc.).
MCPs add value only when the native tool surface is too thin or
too slow for a specific need.

### 2.1 MCPs I'd recommend adding (with justification)

| MCP | Why | Source / cost |
|---|---|---|
| **GitHub MCP** | If you want to take the GitHub push off the parking lot, the GitHub MCP gives me tools for `create_or_update_file`, `push_files`, `create_pull_request` etc. so I can commit and push directly. Without it, push needs `gh` CLI auth, which is what failed last time (your identity had no write access to `amrahman90/luna`). | Public MCP server; no cost. Auth via PAT or GitHub App. |
| **NASA PDS search MCP** (would need to be built or wrapped) | For Paper 2 (lunar inference), the agent needs to query PDS for NAC CDRs by product ID, query the Lunar Pit Atlas for new entries, and read PDS3+4 metadata. A wrapper around the PDS Search API + the LROC RDR index would let the agent do this without a custom script for every site. | ~50 LOC wrapper; no cost (PDS is public). Alternatively, just curl PDS directly via `terminal` — same speed, less infra. |
| **arXiv MCP / search** | Most projects don't need this; an `arxiv` skill with curl + jq is sufficient. The `research/arxiv` skill is already bundled. | Not recommended. |

### 2.2 MCPs I'd NOT recommend

| MCP | Why not |
|---|---|
| Filesystem MCP | Native `read_file`/`write_file`/`search_files` are faster and more restricted by AGENTS.md (never read `00_SOURCE_ORIGINALS/`, only write under `01_WORKSPACE/`). |
| Calendar MCP | Project work doesn't gate on dates. |
| Slack/Discord MCP | You're working CLI-only, no messaging channel integration. |
| Postgres / SQLite MCP | `~/lunarvoid/data/lltb1/*.npz` is the project's "DB"; NumPy on those arrays is what the agent needs. No SQL anywhere. |

---

## 3. The new skill I'd write: `research/lunarvoid-runbook`

Draft outline (not yet written to `~/.hermes/skills/`):

```yaml
---
name: research/lunarvoid-runbook
description: Cold-start runbook for the LUNARVOID lunar lava-tube inference project. Read this FIRST when an agent opens the repo with no in-conversation context. Lists the freshest head commit, the 3-5 things every session must do, the documentation files to always keep in sync, and the cheap proxies for the hard problems (e.g., slope mask is the precision lift; per-claim inference is the v5 path).
---
```

Sections in the runbook:

1. **What just landed** (one paragraph: the v0.x version, the
   committed hash, the headline numbers — auto-generated at skill
   write time from a small script that reads the latest
   `CHANGELOG.md` entry and `sag_summary.json` files)
2. **What every session must read first** (3 files in priority
   order: `admin/CHANGELOG.md` → `data/MANIFEST.md` → the v0.x
   release note for the current version)
3. **What every session must do at exit** (3 files to update:
   `admin/CHANGELOG.md`, `notes/<date>_session<N>_summary.md`,
   the relevant v0.x release note if numbers changed)
4. **The 12 things you can cheap-shot without re-reading the
   paper plan** (12 pointers: where the LLTB-1 v0.4 numbers live,
   where the 8 covered-pit DTMs are, where the GRAIL evidence is,
   what the slope-mask default is, what the `--tune-slope` cap is,
   etc.)
5. **The 5 things that should escalate to you** (cost-boundary
   triggers T1-T4 from the roadmap, plus a new T5: "agent can't
   reproduce a v0.x number within ±5%")
6. **Verification matrix** (which script to run for which
   version: `verify_v02_f32dir_and_filter.py`,
   `verify_v03_slope_mask.py`, `verify_v04_tune_slope.py`)
7. **Skill graph** (what `lunarvoid-lltb1-build` covers vs what
   the runbook covers; cross-link)
8. **One-paragraph current understanding** (the v5 plan's
   per-claim inference framing, the base-rate problem, the
   honesty rules around FP/10⁴ km² — auto-generated from
   `admin/CHANGELOG.md`)

The skill would be loaded automatically when an agent opens
`~/Ahnaf_Shafin/research_project/Lunar_LavaTube/` (Hermes 1.x
offers the `skill_view-on-cwd-match` matcher; I'd add a
`/.agent/AGENT_HINT` file or a project-level `.harness.yml` to
opt in).

---

## 4. Where to put the agentic setup

Three options, all defensible. My recommendation depends on
your answer to Q1.

| Option | Pros | Cons |
|---|---|---|
| **A.** `.agent/` inside this repo, on `master` | Same repo, same `git log`, atomic with the code. Anyone who clones gets it. | Bloats the repo with workflow artefacts. Some of them (like prompts) may contain personal info. |
| **B.** `~/lunarvoid/agent/` outside the repo (per AGENTS.md rule) | Clean separation. Easy to wipe and restart. No personal-info concern. | A fresh agent opening the repo won't find it unless explicitly told. |
| **C.** `.agent/` in a separate branch `agent-setup` | `master` stays "what the paper submits"; the agent setup is a separate concern. Future papers don't have to mention it. | One branch to merge when committing agent improvements. Adds workflow friction. |

My recommendation: **(A) with a `CHANGELOG.md` discipline**. Keep
AGENTS.md the source of truth, put the agent setup in `.agent/`,
document every change there in a single `CHANGELOG_AGENT.md`,
never commit any prompts that reference personal info.

---

## 5. What I propose to do, in order

1. (10 min) Create `01_WORKSPACE/notes/2026-08-21_agentic_setup_proposal.md`
   (already done — this file)
2. (5 min, after your decision on Q1) Create the `.agent/` skeleton
   with `AGENT_HINT`, `CHANGELOG_AGENT.md`, the new skill symlink
3. (15 min) Write the `research/lunarvoid-runbook` skill (skill_view
   + skill_manage create), with the 8 sections above
4. (10 min, after your decision on Q2) If you want MCPs: scaffold
   the MCP server entries in `~/.hermes/config.yaml`. I have no
   way to install MCPs from here (they need to be on your local
   MCP registry), but I can show you the entries to add.
5. (15 min) Wire the verification scripts into a pre-commit hook
   for `code/` changes (or a Makefile target, whichever you
   prefer) — so every commit runs the v0.x verifications and
   the diff surface includes only "passing" changes
6. (5 min) Update AGENTS.md with a "what's in `.agent/`" footer
   so any agent reading AGENTS.md learns the layout
7. (5 min) Commit

**Total time:** ~1 hour of session time. **Cost:** $0.

## 6. Open questions for you (compactly)

1. **Where** does the agent setup live? (A) in-repo `.agent/` /
   (B) `~/lunarvoid/agent/` / (C) separate branch.
2. **MCPs** — do you want GitHub MCP (for pushes), NASA PDS MCP
   (for lunar inference), neither, or both? Or do you want me to
   leave the question open and decide when those flows come up?
3. **Skill-rotation policy** — when a skill gets out of date, do I
   (A) patch in place, (B) bump version + read CHANGELOG, or (C) both?
4. Anything else you want bundled — a sub-issue tracker in the
   repo? a CI stub (e.g., GitHub Actions yaml that runs the v0.x
   verifications on push)? a Makefile target for the smoke test?

---

## 7. What I will NOT do

- I will NOT install any MCP server. Hermes' MCP model means the
  MCP is owned by your local config; I can edit the YAML but
  the binary has to come from your registry.
- I will NOT push to GitHub. The push is parked.
- I will NOT modify AGENTS.md. Only you change AGENTS.md per
  the rules it specifies itself.
- I will NOT modify `00_SOURCE_ORIGINALS/`. Read-only per project
  rules.
- I will NOT touch the v0.4 deliverable numbers or the committed
  hashes.
