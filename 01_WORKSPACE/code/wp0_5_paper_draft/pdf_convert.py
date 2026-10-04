#!/usr/bin/env python3
"""
pdf_convert.py — Convert two LUNARVOID markdown deliverables into clean PDFs
via weasyprint (HTML/CSS -> PDF). No pandoc, no LaTeX.

Inputs
------
01_WORKSPACE/papers/project_overview_v1.md       -> 01_WORKSPACE/admin/outreach/project_overview_v1.pdf
01_WORKSPACE/papers/wp0_5_paper_draft_v1.md      -> 01_WORKSPACE/papers/wp0_5_paper_draft_v1.pdf

Strategy
--------
1. Read markdown.
2. Use the Python `markdown` library (GFM: tables + fenced code) to convert
   MD -> HTML.
4. Render the HTML to PDF with the bundled weasyprint (HTML/CSS print engine).
5. Inline `$...$` LaTeX math stays as plain text — weasyprint does not render
   LaTeX, and that is the agreed behaviour for this pass (fixed in the
   downstream journal-submission LaTeX pass).

The CSS is the academic-letter template from the task brief; no external
font/asset deps.

Run from repo root:
    python3 01_WORKSPACE/code/wp0_5_paper_draft/pdf_convert.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import markdown
from weasyprint import HTML, CSS

# --- Resolve paths relative to repo root (parent of 01_WORKSPACE/) -------
REPO_ROOT = Path(__file__).resolve().parents[3]  # .../Lunar_LavaTube
WS = REPO_ROOT / "01_WORKSPACE"


# --- CSS template (per task brief; no redesign) ---------------------------
CSS_TEXT = """
@page {
  size: A4;
  margin: 25mm 25mm 30mm 25mm;
  @bottom-center {
    content: counter(page) " of " counter(pages);
    font-family: 'DejaVu Serif', serif;
    font-size: 9pt;
    color: #666;
  }
}
@page :first {
  @bottom-center { content: ""; }
}
body {
  font-family: 'DejaVu Serif', 'Liberation Serif', serif;
  font-size: 10.5pt;
  line-height: 1.4;
  color: #1a1a1a;
  max-width: 100%;
}
h1 {
  font-size: 18pt;
  font-weight: bold;
  margin-top: 0;
  margin-bottom: 0.5em;
  text-align: center;
  border-bottom: 2px solid #333;
  padding-bottom: 0.3em;
}
h2 {
  font-size: 13pt;
  font-weight: bold;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  border-bottom: 1px solid #999;
  padding-bottom: 0.2em;
}
h3 {
  font-size: 11.5pt;
  font-weight: bold;
  font-style: italic;
  margin-top: 1.2em;
  margin-bottom: 0.3em;
}
p {
  text-align: justify;
  margin: 0 0 0.6em 0;
}
table {
  border-collapse: collapse;
  margin: 1em auto;
  font-size: 9.5pt;
}
th {
  background: #f0f0f0;
  border: 1px solid #999;
  padding: 4px 6px;
  text-align: center;
  font-weight: bold;
}
td {
  border: 1px solid #ccc;
  padding: 3px 6px;
  vertical-align: top;
}
code {
  font-family: 'DejaVu Sans Mono', monospace;
  font-size: 9pt;
  background: #f5f5f5;
  padding: 1px 3px;
  border-radius: 2px;
}
pre {
  background: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 8px;
  font-size: 9pt;
  overflow-x: auto;
}
blockquote {
  border-left: 3px solid #ccc;
  margin: 0.5em 0;
  padding-left: 1em;
  color: #444;
  font-style: italic;
}
"""


def md_to_html(md_path: Path) -> str:
    """Convert a markdown file to a complete HTML5 document with inline CSS."""
    text = md_path.read_text(encoding="utf-8")
    # GFM tables + fenced code. 'sane_lists' keeps numbered lists sane under
    # deep nesting in the paper draft.
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="html5",
    )
    title = md_path.stem.replace("_", " ")
    html = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        f"  <meta charset=\"utf-8\"/>\n"
        f"  <title>{title}</title>\n"
        f"  <style>{CSS_TEXT}</style>\n"
        "</head>\n"
        "<body>\n"
        f"{body}\n"
        "</body>\n"
        "</html>\n"
    )
    return html


def render_pdf(md_path: Path, pdf_path: Path) -> None:
    html = md_to_html(md_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html, base_url=str(md_path.parent)).write_pdf(str(pdf_path))


# --- Jobs ---------------------------------------------------------------
JOBS = [
    (
        WS / "papers" / "project_overview_v1.md",
        WS / "admin" / "outreach" / "project_overview_v1.pdf",
    ),
    (
        WS / "papers" / "wp0_5_paper_draft_v1.md",
        WS / "papers" / "wp0_5_paper_draft_v1.pdf",
    ),
]


def main() -> int:
    for md_path, pdf_path in JOBS:
        if not md_path.exists():
            print(f"[FAIL] missing source: {md_path}", file=sys.stderr)
            return 1
        print(f"[INFO] {md_path.name} -> {pdf_path.relative_to(WS)}")
        render_pdf(md_path, pdf_path)
        size_kb = pdf_path.stat().st_size / 1024
        print(f"[OK]   {pdf_path}  ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())