# Outreach Playbook

> **Compiled**: 2026-09-27 (lunar-orchestrator)
> **Purpose**: Calendar + playbook for European PhD applications. Target faculty: `target_faculty.md`. Templates: `email_templates.md`.

## Calendar

| Window | Action |
|---|---|
| **2026-09-30 → 2026-10-04** | Send FIRST batch (Tier 1 + Tier 2 = 10 emails from `target_faculty.md`). Stagger by 1-2 emails/day so failures (bounces, replies) don't clobber. |
| **2026-10-12 → 2026-10-18** | First follow-up round (Template 2) for any non-responders. About 2 weeks after initial send. |
| **2026-10-25 → 2026-11-08** | Track responses. Begin preparing `research_statement_v1.md` final. Begin Zotero attaches for any papers the engagement suggests. |
| **2026-11-15 → 2026-11-30** | Application-season direct messages (Template 3) to engaged faculty + any Tier 3 faculty from `target_faculty.md`. |
| **2026-12-01 → 2026-12-15** | Lock outreach. Freeze new cold emails. Begin active application filing. |
| **2026-12-15 → 2027-01-31** | Application deadlines (per program; most European CS/AI: mid-Dec to mid-Jan). |
| **2027-01-15 → 2027-04** | Interview period (some programs Feb/Mar; some Apr/May). |
| **2027-04 → 2027-09** | Decisions + matriculation prep. |

---

## Tracking

Maintain a single line per faculty in `tracking.md` (create it on first send). Format:

```
[Prof. X — affiliation — Sent YYYY-MM-DD — Reply? YYYY-MM-DD — Notes]
```

Example:
```
Emtiyaz Khan  — UCL — Sent 2026-10-01 — Reply 2026-10-08 — 20min call booked
Schölkopf    — MPI  — Sent 2026-10-02 — Reply — redirect to Khan
Gal          — Ox   — Sent 2026-10-03 — no reply — follow-up 2026-10-17
Yang         — ETH  — Sent 2026-10-03 — bounced — verify email — resent
```

Update `tracking.md` whenever you send, get a reply, or follow up.

---

## When to give up

- **3 sends + 2 follow-ups + 2 months of patience + no reply** → move on.
- **Don't reach out to the same person more than 3 times in any cycle.**
- Some faculty will not respond. That's normal faculty behaviour, not a failure on your side.
- **Pivot options**: a different faculty in the same lab, a faculty member of a related lab, or a different country/PhD program structure (e.g., a structured UK PhD with rotation).

## When to escalate

- **Faculty replies with "let's talk"** → schedule the call. Treat 20 minutes as a mini-interview. Prepare:
  - 2-minute project summary (use `papers/project_overview_v1.md`)
  - 2-minute "what I want to do in the PhD" (pick the ONE question from `target_faculty.md`)
  - Specific question about their work
  - Be ready to talk about ONE thing you don't know about their method (shows engagement)
- **Faculty refers you to a colleague** → contact that colleague with a forwarding note ("Prof. X suggested I contact you; the original email with context is below.")
- **Faculty says "apply to the program, we'll review all candidates"** → do that. Send Template 3 as a courtesy.
- **Faculty says "we don't have open positions"** → note it, move on. Re-engage in 1 year if still relevant.

---

## What to attach / link

| Stage | Attach | Link |
|---|---|---|
| Cold email (T1) | PDF of `papers/project_overview_v1.md` | github.com/amrahman90/luna |
| Follow-up (T2) | nothing | link to new artifact (arXiv, Zenodo, new commit) |
| Application-season (T3) | PDF of `papers/research_statement_v1.md` | full repo + portal URL |
| Engaged reply | nothing additional unless asked | "happy to share more if useful" |

---

## Things NOT to say in cold outreach

- **"Would you supervise me?"** — too forward at first contact.
- **"I'm looking for funding"** — premature; comes later in negotiation.
- **"I don't have a PI"** — not relevant to a methodology faculty reader; irrelevant to a planetary science faculty reader; do not flag this.
- **"Please reply"** — passive-aggressive; don't do it.
- **Generic flattery** ("Your work is amazing!") — faculty see this in every cold email; it discredits immediately.
- **Apologies** ("Sorry to bother") — you aren't bothering; you are introducing yourself.

## Things TO say

- **Specific question(s)** about their methodology.
- **What you found + the artifact** (concrete, not philosophical).
- **Why the methodological fit** (concrete connection to their work via the [SPECIFIC PAPER] anchor).
- **That you're not asking for supervision** at first contact — a conversation first.
- **A link to the open repo** (they will look; the 12 tests + 2 papers + portal is the proof).

---

## Pivot contingency

If 6 weeks after first-batch send you have:
- **0 substantive replies** → pivot. Post Workshop preprint to arXiv; widen target list (European CS less competitive, US as fallback, ELLIS PhD school application); apply to NeurIPS/ICML workshops with the methodology as a track.
- **1-3 short replies** → continue with engaged faculty. Convert short replies to 20-min calls. Drop non-responders.
- **1+ explicit "let's talk"** → do it well. Treat as mini-interview. Document each call's signal.
- **Someone says "apply + we'll write a letter"** → yes; coordinate letter timing carefully (give them 3-4 weeks before deadline).

---

## After outreach cycle ends (post-Jan 2027)

- Send a polite "thank you" note to anyone who replied.
- Stay subscribed to any lab mailing lists for future openings.
- Re-engage if you've shipped something new (arXiv preprint, conference paper, open dataset).
- The relationship is the long-game. Even one reply in 10 is enough to start.

---

## Practical details

- **Email signature**: include name, single-line affiliation (e.g., "Independent Researcher, LUNARVOID Program"), personal website URL if you have one, LinkedIn URL.
- **Sending time**: Tuesday-Thursday, 09:00-11:00 in the recipient's timezone. Faculty read email Tuesday morning more than Friday afternoon.
- **Bounced emails**: verify the recipient's CURRENT email via their most recent paper's corresponding-author line, their departmental directory, or Google Scholar.
- **If you have a personal domain**: send from there; Gmail/yahoo/etc. work but a personal domain (e.g., `yourname.dev`) reads as more serious.
- **DO NOT BCC**: cold outreach works on individualised emails; BCCing devalues.
- **DO NOT use Mail-Merge for [SPECIFIC PAPER]**: this anchor must be GENUINE per recipient, not a search-and-replace of one common paper.
