"""Convert a Vedic reading report.md into a mobile-friendly PDF.

Pipeline: Markdown → styled HTML (inline CJK CSS) → Chrome headless --print-to-pdf.
"""

from __future__ import annotations

import base64
import re
import subprocess
import tempfile
from pathlib import Path

import markdown

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
@font-face {{
  font-family: 'Songti SC';
  src: local('Songti SC Regular'), local('STSong'), local('Songti SC');
}}
@font-face {{
  font-family: 'PingFang SC';
  src: local('PingFang SC Regular'), local('.PingFang SC'), local('PingFang SC');
}}

@page {{
  size: 148mm 210mm;
  margin: 16mm 15mm 18mm 15mm;
}}

:root {{
  --serif: 'Songti SC', 'Noto Serif CJK SC', Georgia, 'Times New Roman', serif;
  --sans: 'PingFang SC', 'Hiragino Sans GB', 'Noto Sans CJK SC',
          -apple-system, 'Helvetica Neue', sans-serif;
  --mono: 'SF Mono', 'Menlo', 'IBM Plex Mono', 'Consolas', monospace;

  --bg: #F5F1EB;
  --bg-card: #FFFFFF;
  --text: #1F1D1A;
  --text-sec: #5C5650;
  --accent: #96734E;
  --accent-light: rgba(150,115,78,0.10);
  --steel: #7A8490;
  --divider: #DDD7CE;
  --stripe: rgba(150,115,78,0.035);
  --tag-bg: rgba(150,115,78,0.08);
  --tag-text: #7A5E3E;
  --highlight-bg: rgba(150,115,78,0.05);
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: var(--sans);
  background: var(--bg);
  color: var(--text);
  font-size: 10.5pt;
  line-height: 2;
  -webkit-font-smoothing: antialiased;
  padding: 0;
}}

.page {{
  max-width: 100%;
  margin: 0 auto;
}}

/* === Typography: "the larger, the lighter" === */

.md-content h1 {{
  font-family: var(--serif);
  font-size: 20pt;
  font-weight: 400;
  text-align: center;
  margin-bottom: 18pt;
  padding-bottom: 14pt;
  border-bottom: 1pt solid var(--divider);
  letter-spacing: 0.06em;
  line-height: 1.5;
}}
.md-content h2 {{
  font-family: var(--serif);
  font-size: 15pt;
  font-weight: 500;
  margin-top: 24pt;
  margin-bottom: 10pt;
  padding-bottom: 6pt;
  border-bottom: 0.5pt solid var(--divider);
  color: var(--accent);
  break-after: avoid;
  letter-spacing: 0.04em;
  line-height: 1.5;
}}
.md-content h3 {{
  font-family: var(--serif);
  font-size: 12.5pt;
  font-weight: 600;
  margin-top: 18pt;
  margin-bottom: 6pt;
  letter-spacing: 0.02em;
  break-after: avoid;
  line-height: 1.6;
}}
.md-content h4 {{
  font-family: var(--sans);
  font-size: 11pt;
  font-weight: 600;
  margin-top: 14pt;
  margin-bottom: 4pt;
  line-height: 1.6;
}}

/* === Body text === */

.md-content p {{
  margin-bottom: 9pt;
  font-size: 10.5pt;
  line-height: 2;
}}
.md-content ul, .md-content ol {{
  margin-bottom: 9pt;
  padding-left: 18pt;
  font-size: 10.5pt;
  line-height: 2;
}}
.md-content li {{
  margin-bottom: 3pt;
}}

/* === Tables === */

.md-content table {{
  width: 100%;
  border-collapse: collapse;
  font-family: var(--sans);
  font-size: 9.5pt;
  margin: 12pt 0 14pt;
  background: var(--bg-card);
  border-radius: 4pt;
  overflow: hidden;
  font-variant-numeric: tabular-nums;
  line-height: 1.6;
}}
.md-content th {{
  font-family: var(--mono);
  text-align: left;
  font-size: 7.5pt;
  color: var(--steel);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  padding: 10pt 10pt 8pt;
  border-bottom: 1pt solid var(--divider);
  font-weight: 500;
}}
.md-content td {{
  padding: 9pt 10pt;
  border-bottom: 0.5pt solid var(--divider);
  vertical-align: top;
  word-break: break-word;
}}
.md-content tr:last-child td {{ border-bottom: none; }}
.md-content tr:nth-child(even) td {{ background: var(--stripe); }}

/* === Code blocks: monospace meta, wrap for PDF === */

.md-content code {{
  font-family: var(--mono);
  font-size: 8pt;
  background: var(--tag-bg);
  padding: 1pt 4pt;
  border-radius: 2pt;
  color: var(--tag-text);
  word-break: break-all;
  letter-spacing: 0.02em;
}}
.md-content pre {{
  background: var(--bg-card);
  padding: 12pt 14pt;
  border-radius: 4pt;
  font-size: 8pt;
  margin: 10pt 0 12pt;
  border: 0.5pt solid var(--divider);
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-all;
  overflow: hidden;
  line-height: 1.7;
}}
.md-content pre code {{
  background: none;
  padding: 0;
  font-size: 8pt;
  word-break: break-all;
}}

/* === Blockquotes === */

.md-content blockquote {{
  background: var(--highlight-bg);
  border-left: 2.5pt solid var(--accent);
  padding: 11pt 14pt;
  border-radius: 0 4pt 4pt 0;
  margin: 12pt 0;
  line-height: 1.9;
}}
.md-content blockquote p {{
  font-family: var(--serif);
  font-size: 10pt;
  font-style: italic;
  color: var(--text-sec);
  margin-bottom: 4pt;
}}
.md-content blockquote p:last-child {{
  margin-bottom: 0;
}}

/* === Horizontal rules === */

.md-content hr {{
  border: none;
  border-top: 0.5pt solid var(--divider);
  margin: 20pt 0;
}}

/* === Emphasis === */

.md-content strong {{
  color: var(--text);
  font-weight: 600;
}}

/* === Inline data references (← markers) === */

.md-content p code,
.md-content li code {{
  font-size: 7pt;
  opacity: 0.55;
  font-weight: 400;
}}
</style>
</head>
<body>
<div class="page">
<div class="md-content">
{content}
</div>
</div>
</body>
</html>
"""


def _embed_images(html: str, base_dir: Path) -> str:
    """Replace local image src paths with base64 data URIs.

    Chrome headless resolves relative paths from the *temp* HTML location,
    not the original report directory.  Embedding inline side-steps that.
    """
    def _replace_src(m: re.Match) -> str:
        src = m.group(2)
        # Skip external URLs and already-inline data URIs
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)

        img_path = (base_dir / src).resolve()
        if not img_path.exists():
            return m.group(0)  # leave untouched — will show broken-image marker

        raw = img_path.read_bytes()
        b64 = base64.b64encode(raw).decode("ascii")

        # Map extension → MIME
        ext = img_path.suffix.lower()
        mime_map = {
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mime = mime_map.get(ext, "image/svg+xml")
        # Preserve everything, only replace the src value
        return f'{m.group(1)}data:{mime};base64,{b64}{m.group(3)}'

    return re.sub(r'(<img[^>]+src=")([^"]+)(")', _replace_src, html)


def md_to_html(md_path: Path) -> str:
    """Convert a Markdown file to a styled HTML string with embedded images."""
    md_text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "smarty"],
        output_format="html",
    )
    html_body = _embed_images(html_body, md_path.parent)
    return HTML_TEMPLATE.format(content=html_body)


def html_to_pdf(html_path: Path, pdf_path: Path) -> Path:
    """Use Chrome headless to convert an HTML file to PDF."""
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        str(html_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=30)
    return pdf_path


def export_pdf(md_path: str | Path) -> Path:
    """Full pipeline: report.md → report.pdf in the same directory."""
    md_path = Path(md_path)
    if not md_path.exists():
        raise FileNotFoundError(f"Report not found: {md_path}")

    html_str = md_to_html(md_path)
    pdf_path = md_path.with_suffix(".pdf")

    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
        f.write(html_str)
        tmp_html = Path(f.name)

    try:
        html_to_pdf(tmp_html, pdf_path)
    finally:
        tmp_html.unlink(missing_ok=True)

    return pdf_path


def pdf_cli() -> None:
    """Entry point for vedic-pdf command."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="vedic-pdf",
        description="Convert a Vedic reading report.md to a mobile-friendly PDF.",
    )
    parser.add_argument("report", type=Path, help="Path to report.md")
    parser.add_argument("-o", "--output", type=Path, help="Output PDF path (default: same dir as report)")

    args = parser.parse_args()

    if not args.report.exists():
        print(f"Error: {args.report} not found", file=sys.stderr)
        sys.exit(1)

    if args.output:
        html_str = md_to_html(args.report)
        with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
            f.write(html_str)
            tmp_html = Path(f.name)
        try:
            html_to_pdf(tmp_html, args.output)
        finally:
            tmp_html.unlink(missing_ok=True)
        pdf_path = args.output
    else:
        pdf_path = export_pdf(args.report)

    print(f"[pdf] {pdf_path}", file=sys.stderr)
