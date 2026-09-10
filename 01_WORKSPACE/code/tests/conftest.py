"""Shared fixtures for the LUNARVOID pytest suite (task C4).

Design constraints (from the dispatch + AGENTS.md + conventions skill):

- **Venv-independent path resolution.** The repo root, the code dir and
  the data root are derived from *this file's location* and the
  ``LUNARVOID_DATA`` environment variable — never from a hardcoded
  username. The interpreter used for child processes is ``sys.executable``
  (the suite is meant to run under ``~/lunarvoid/venv/bin/python`` but
  works under any venv that has the freeze installed).
- **Local-only artifacts auto-skip.** Raw/derived rasters live only under
  ``~/lunarvoid/data`` (conventions §1). Tests that need them resolve
  paths through the ``data_root`` fixture and call ``pytest.skip()``
  with a reason when the file is absent, so the same suite runs green
  in CI where only the git-tracked repo exists. Setting
  ``LUNARVOID_DATA=/tmp/some-empty-dir`` hides the data without
  touching it (used by the C11 skip-verification).
- **No network.** An autouse fixture denies socket creation inside the
  test process. Child subprocesses (smoke_test.py, sag_detect.py) are
  unaffected — they are local binaries/numpy code that never network.
  Set ``LUNARVOID_ALLOW_NET=1`` to escape-hatch while debugging.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

# --- venv-independent path resolution -------------------------------------

TESTS_DIR = Path(__file__).resolve().parent
CODE_DIR = TESTS_DIR.parent            # 01_WORKSPACE/code
WS_DIR = CODE_DIR.parent               # 01_WORKSPACE
REPO_ROOT = WS_DIR.parent              # Lunar_LavaTube repo root

# Raw + derived rasters live ONLY under the data root (conventions §1).
# LUNARVOID_DATA overrides for the acceptance check "run with the data
# dir hidden" — no renaming/deleting of the real tree.
DATA_ROOT = Path(
    os.environ.get("LUNARVOID_DATA", str(Path.home() / "lunarvoid" / "data"))
)

# The suite must run under the project venv (numpy/rasterio/whitebox).
# Resolve the interpreter running us instead of hardcoding a path.
VENV_PYTHON = Path(sys.executable)

# Make pipeline modules importable exactly as production code expects.
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))


# --- process runner ---------------------------------------------------------

class VenvRun:
    """Run child Python processes with the project conventions applied.

    - same interpreter as the suite (the project venv),
    - ``PYTHONPATH`` starts with the code dir (the C9 shared-``_crs``
      refactor means bare-script invocations of sag_detect.py need
      ``01_WORKSPACE/code`` importable),
    - ``MPLBACKEND=Agg`` (headless plots),
    - cwd = repo root.
    """

    def __init__(self, python: Path):
        self.python = python

    def __call__(self, args: list[str], timeout: float = 1200,
                 cwd: Path | None = None) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = os.pathsep.join(
            [str(CODE_DIR)] + ([existing] if existing else [])
        )
        env.setdefault("MPLBACKEND", "Agg")
        return subprocess.run(
            [str(self.python), *[str(a) for a in args]],
            capture_output=True, text=True,
            cwd=str(cwd or REPO_ROOT), timeout=timeout, env=env,
        )


# --- fixtures ---------------------------------------------------------------

@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def code_dir() -> Path:
    return CODE_DIR


@pytest.fixture(scope="session")
def data_root() -> Path:
    """Root of raw/derived raster storage (env-overridable; conventions §1)."""
    return DATA_ROOT


@pytest.fixture(scope="session")
def venv_python() -> Path:
    return VENV_PYTHON


@pytest.fixture(scope="session")
def venv_run() -> Callable:
    return VenvRun(VENV_PYTHON)


@pytest.fixture(scope="session")
def smoke_run(venv_run, tmp_path_factory) -> dict:
    """Run code/smoke_test.py ONCE per session; cache stdout + summary.

    The known-good anchors asserted here are the §7 canary
    (F1 0.392/0/0.800 per rung, fusion AUC 0.990).
    """
    outdir = tmp_path_factory.mktemp("smoke")
    r = venv_run([CODE_DIR / "smoke_test.py", "--outdir", outdir], timeout=900)
    summary = None
    spath = outdir / "smoke_summary.json"
    if spath.exists():
        summary = json.loads(spath.read_text())
    return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr,
            "summary": summary, "outdir": outdir}


@pytest.fixture(scope="session")
def sag_help(venv_run) -> str:
    """sag_detect.py --help output, cached (imports are ~3 s each)."""
    r = venv_run([CODE_DIR / "wp1_detector" / "sag_detect.py", "--help"],
                 timeout=180)
    assert r.returncode == 0, f"sag_detect --help failed: {r.stderr[-300:]}"
    return r.stdout


@pytest.fixture(scope="session")
def sag_run(venv_run, tmp_path_factory) -> Callable:
    """Cached sag_detect.py CLI runner (the LLTB-1 v0.5 detector path).

    Returns ``run(npz: Path, rungs: list[float], *extra_args,
    min_component: int | None = None) -> dict`` with keys rc/stdout/
    stderr/outdir/summary. Identical invocations are cached per session
    so several ported verifiers can share one detector re-run.
    """
    cache: dict[tuple, dict] = {}

    def _run(npz: Path, rungs, *extra, min_component=None):
        key = (str(npz), tuple(str(r) for r in rungs), tuple(extra),
               min_component)
        if key in cache:
            return cache[key]
        outdir = tmp_path_factory.mktemp("sag")
        args = [CODE_DIR / "wp1_detector" / "sag_detect.py",
                "--npz", npz, "--outdir", outdir,
                "--rungs", *[str(r) for r in rungs]]
        if min_component is not None:
            args += ["--min-component", str(min_component)]
        args += list(extra)
        r = venv_run(args, timeout=1800)
        ssum = outdir / "sag_summary.json"
        res = {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr,
               "outdir": outdir,
               "summary": json.loads(ssum.read_text()) if ssum.exists() else None}
        cache[key] = res
        return res

    return _run


# --- offline enforcement -----------------------------------------------------

@pytest.fixture(autouse=True)
def _block_network():
    """Deny socket creation inside the test process (no-network pin).

    Child subprocesses are NOT affected (they are separate processes);
    none of them legitimately network either. Escape hatch for
    debugging live-UA checks: LUNARVOID_ALLOW_NET=1.
    """
    if os.environ.get("LUNARVOID_ALLOW_NET") == "1":
        yield
        return

    msg = ("network access denied: LUNARVOID tests run offline "
           "(set LUNARVOID_ALLOW_NET=1 to permit)")

    # Must stay a CLASS: stdlib modules subclass socket.socket at import
    # time (e.g. ssl.SSLSocket), and subclassing a plain function raises
    # "TypeError: function() argument 'code' must be code, not str".
    class _BlockedSocket(socket.socket):
        def __init__(self, *_a, **_k):
            raise RuntimeError(msg)

    def _deny(*_a, **_k):
        raise RuntimeError(msg)

    saved = (socket.socket, socket.create_connection, socket.getaddrinfo)
    socket.socket = _BlockedSocket          # type: ignore[assignment]
    socket.create_connection = _deny         # type: ignore[assignment]
    socket.getaddrinfo = _deny               # type: ignore[assignment]
    try:
        yield
    finally:
        (socket.socket, socket.create_connection, socket.getaddrinfo) = saved
