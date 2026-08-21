#!/usr/bin/env python3
"""LUNARVOID manual orchestrator — headless dispatch of recurring tasks.

Reads tasks.yaml (same directory) and runs each task via
`opencode run --agent <agent> "<prompt>"`, capturing output to
orchestrator/logs/<date>_<id>.log. Manual dispatch only (no cron
wired by design; add one yourself only after reading README notes).

Usage:
    python pipeline.py                # run every task
    python pipeline.py --only <id>    # run one task
    python pipeline.py --list         # list task ids and agents

Deliberate limitations (safety rails):
    - No git commits/pushes from here. Ever.
    - Tasks are expected to be read/append-only (see tasks.yaml).
    - No parallelism: tasks run sequentially, one opencode session
      each, so interactive opencode sessions aren't raced.
"""
import argparse
import datetime
import pathlib
import subprocess
import sys

import yaml  # uv pip install pyyaml (into the venv) if missing

ROOT = pathlib.Path(__file__).resolve().parents[3]  # repo root
HERE = pathlib.Path(__file__).resolve().parent
LOG_DIR = HERE / "logs"
TASKS_FILE = HERE / "tasks.yaml"


def run_task(task_id: str, agent: str, prompt: str) -> int:
    stamp = datetime.date.today().isoformat()
    log_path = LOG_DIR / f"{stamp}_{task_id}.log"
    LOG_DIR.mkdir(exist_ok=True)
    cmd = ["opencode", "run", "--agent", agent, prompt]
    print(f"[{task_id}] dispatching to agent '{agent}' -> {log_path}")
    with log_path.open("w") as log:
        log.write(f"# {stamp} {task_id} (agent={agent})\n# cmd: {' '.join(cmd[:4])}...\n\n")
        log.flush()
        proc = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    status = "OK" if proc.returncode == 0 else f"EXIT {proc.returncode}"
    print(f"[{task_id}] {status}")
    return proc.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="run only the task with this id")
    ap.add_argument("--list", action="store_true", help="list tasks")
    args = ap.parse_args()

    tasks = yaml.safe_load(TASKS_FILE.read_text())
    if args.list:
        for t in tasks:
            print(f"{t['id']:24s} -> {t['agent']}")
        return 0

    rc_total = 0
    for t in tasks:
        if args.only and t["id"] != args.only:
            continue
        rc_total |= run_task(t["id"], t["agent"], t["prompt"].strip())
    return rc_total


if __name__ == "__main__":
    sys.exit(main())
