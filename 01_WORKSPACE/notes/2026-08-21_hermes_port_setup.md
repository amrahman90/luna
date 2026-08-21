# Hermes port of the LUNARVOID agentic workflow — setup record

**Date:** 2026-08-21
**Status:** INSTALLED (Hermes-side files outside git; one repo-side
skill edit + this note are uncommitted drafts pending user OK)

## What was installed

| Piece | Location | Purpose |
|---|---|---|
| Mutual-exclusion lock | `~/lunarvoid/bin/lunarvoid_lock.sh` | One orchestrator on the roadmap at a time (opencode vs Hermes). Heartbeat-TTL design (6 h default, `LUNARVOID_LOCK_TTL`); subcommands acquire/release/force/status; owners `opencode`/`hermes`. All four paths tested: fresh acquire, same-owner refresh, cross-owner refusal (exit 1), TTL steal of a dead heartbeat. |
| Hermes skill | `~/.hermes/skills/lunarvoid-orchestrator/SKILL.md` | Hermes-side orchestrator role: loads the repo's canonical conventions+protocol skills by path (single source of truth — never forked), acquires the lock, resumes from roadmap+CHANGELOG on disk, delegates via Hermes subagents to the repo's `.opencode/agent/*.md` role prompts, obeys the same review chain / stop conditions / claim discipline / no-push rule. |
| Hermes config | `~/.hermes/config.yaml` → `skills.external_dirs` | Added the repo's `.opencode/skills/` so Hermes natively discovers `lunarvoid-conventions` and `lunarvoid-protocol` alongside its own skills. Backup: `~/.hermes/config.yaml.bak.20260821_224305`. YAML validated post-edit. |
| Protocol skill edit | `.opencode/skills/lunarvoid-protocol/SKILL.md` | New step 0 "LOCK (mutual exclusion)" in the task lifecycle (both frameworks follow the same protocol file). |

## Not ported (deliberate)

- **MCP servers (arxiv/zotero)**: Hermes config has no MCP-server
  block found; arXiv/Zotero access for Hermes is left for a later
  session (Hermes has its own `research/arxiv` skill bundle anyway).
- **Permission enforcement**: opencode's per-agent edit-denies are not
  replicated (no native equivalent found). Mitigation = role-prompt
  write-scopes + lock + review chain; `00_SOURCE_ORIGINALS/` stays
  protected by opencode.json for opencode sessions only.

## How to run

In Hermes: open a session, say "load lunarvoid-orchestrator" (or it
triggers on LUNARVOID work). It will read the repo skills, take the
lock, and continue the roadmap. Meanwhile opencode sessions must
observe the same lock (protocol skill step 0).

## Rollback

1. `rm -rf ~/.hermes/skills/lunarvoid-orchestrator`
2. `cp ~/.hermes/config.yaml.bak.20260821_224305 ~/.hermes/config.yaml`
3. Revert the protocol-skill LOCK step; delete this note.

## Safety notes

- Hermes default model is MiniMax-M3 (config.yaml) — different model
  from opencode sessions, which is fine for the model-diversity goal
  (skeptic second opinion).
- `subagent_auto_approve: false` in Hermes delegation: delegated role
  runs may prompt for approval — expected, do not auto-accept writes
  outside role scopes.
- Concurrent execution remains forbidden even with the lock working:
  the lock is the guard, the discipline is the rule.
