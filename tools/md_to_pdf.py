"""Minimal Markdown → PDF for the judge-facing report (no external deps).

Uses headless Chromium to print a styled A4 HTML page. Supports the subset this
repo's docs use: headings, paragraphs, bold, inline code, links, bullet lists,
blockquotes, horizontal rules and pipe tables.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def inline(text: str, base_dir: Path | None = None) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    def img(m: re.Match) -> str:
        alt, src = m.group(1), m.group(2)
        if base_dir and not src.startswith(("http://", "https://", "data:")):
            path = (base_dir / src).resolve()
            if path.exists():
                import base64

                mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
                data = base64.b64encode(path.read_bytes()).decode()
                return f'<img alt="{alt}" src="data:{mime};base64,{data}"/>'
        return f'<img alt="{alt}" src="{src}"/>'

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def convert(md: str, base_dir: Path | None = None) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    in_list = False
    list_tag = "ul"
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Continuation line of the previous list item (markdown hard-wrap).
        if in_list and line[:1].isspace() and stripped and out and out[-1].startswith("<li>"):
            out[-1] = out[-1][: -len("</li>")] + " " + inline(stripped, base_dir) + "</li>"
            i += 1
            continue

        if not stripped:
            if in_list:
                out.append(f"</{list_tag}>")
                in_list = False
            i += 1
            continue

        if stripped == "---":
            out.append("<hr/>")
            i += 1
            continue

        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if m:
            if in_list:
                out.append(f"</{list_tag}>")
                in_list = False
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2), base_dir)}</h{level}>")
            i += 1
            continue

        if stripped.startswith(">"):
            if in_list:
                out.append(f"</{list_tag}>")
                in_list = False
            out.append(f"<blockquote>{inline(stripped[1:].strip(), base_dir)}</blockquote>")
            i += 1
            continue

        if stripped.startswith("|"):
            if in_list:
                out.append(f"</{list_tag}>")
                in_list = False
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            body = [c for c in cells if not all(re.fullmatch(r":?-{2,}:?", x or "-") for x in c)]
            out.append("<table>")
            for r_idx, row in enumerate(body):
                tag = "th" if r_idx == 0 else "td"
                out.append("<tr>" + "".join(f"<{tag}>{inline(c, base_dir)}</{tag}>" for c in row) + "</tr>")
            out.append("</table>")
            continue

        if stripped.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
                list_tag = "ul"
            out.append(f"<li>{inline(stripped[2:], base_dir)}</li>")
            i += 1
            continue

        m_ol = re.match(r"^\d+\.\s+(.*)$", stripped)
        if m_ol:
            if not in_list:
                out.append("<ol>")
                in_list = True
                list_tag = "ol"
            out.append(f"<li>{inline(m_ol.group(1), base_dir)}</li>")
            i += 1
            continue

        if in_list:
            out.append(f"</{list_tag}>")
            in_list = False
        # Join hard-wrapped markdown lines into one paragraph.
        para = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (
                not nxt
                or nxt == "---"
                or nxt.startswith(("#", ">", "|", "- "))
                or re.match(r"^\d+\.\s", nxt)
            ):
                break
            para.append(nxt)
            i += 1
        out.append(f"<p>{inline(' '.join(para), base_dir)}</p>")

    if in_list:
        out.append(f"</{list_tag}>")
    return "\n".join(out)



CSS_SLIDES = """
@page { size: 13.333in 7.5in; margin: 0; }
body { font-family: "Adwaita Sans", "Helvetica Neue", Arial, sans-serif;
       font-size: 19pt; line-height: 1.32; color: #111; padding: 16mm 18mm; }
h1 { font-size: 46pt; margin: 22mm 0 4mm; letter-spacing: -0.5pt; }
h1 + p { font-size: 22pt; color: #444; }
h2 { font-size: 30pt; margin: 0 0 6mm; page-break-before: always; }
h3 { font-size: 21pt; margin: 4mm 0 2mm; }
p { margin: 0 0 4mm; }
li { margin: 0 0 2.4mm; }
code { font-family: "Adwaita Mono", ui-monospace, monospace; font-size: 0.85em;
       background: #f2f2f2; padding: 0 1.2mm; border-radius: 1mm; }
blockquote { margin: 4mm 0; padding: 3mm 4mm; border-left: 3pt solid #999;
             background: #fafafa; font-style: italic; }
table { width: 100%; border-collapse: collapse; font-size: 0.8em; margin: 3mm 0; }
th, td { border: 1px solid #ddd; padding: 1.6mm 2.4mm; text-align: left; }
th { background: #f2f2f2; }
a { color: #0b57d0; text-decoration: none; }
img { display: block; max-width: 100%; max-height: 72mm; margin: 3mm 0; border-radius: 2mm; }
hr { border: none; border-top: 1px solid #ddd; margin: 4mm 0; }
"""

CSS = """
@page { size: A4; margin: 11mm 12mm; }
body { font-family: "Adwaita Sans", "Helvetica Neue", Arial, sans-serif;
       font-size: 9.2pt; line-height: 1.27; color: #111; }
h1 { font-size: 16pt; margin: 0 0 3mm; letter-spacing: -0.2pt; }
h2 { font-size: 11.5pt; margin: 4.5mm 0 1.6mm; border-bottom: 1px solid #ddd; padding-bottom: 1mm; }
h3 { font-size: 11pt; margin: 4mm 0 1.5mm; }
p { margin: 0 0 2.1mm; }
code { font-family: "Adwaita Mono", ui-monospace, monospace; font-size: 8.8pt;
       background: #f3f3f3; padding: 0.3mm 1mm; border-radius: 1mm; }
blockquote { margin: 2mm 0 3mm; padding: 2mm 3mm; border-left: 2pt solid #999;
             background: #fafafa; font-style: italic; }
table { width: 100%; border-collapse: collapse; margin: 1.5mm 0 3mm; font-size: 8.3pt; }
th, td { border: 1px solid #ddd; padding: 0.9mm 1.6mm; text-align: left; vertical-align: top; }
th { background: #f2f2f2; }
ul { margin: 0 0 3mm 0; padding-left: 5mm; }
li { margin: 0 0 1mm; }
hr { border: none; border-top: 1px solid #ddd; margin: 5mm 0; }
a { color: #0b57d0; text-decoration: none; }
"""


def find_chromium() -> str:
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        p = shutil.which(name)
        if p:
            return p
    raise SystemExit("chromium not found")


def build_pdf(md_path: Path, pdf_path: Path, slides: bool = False) -> int:
    body = convert(md_path.read_text(encoding="utf-8"), base_dir=md_path.parent)
    css = CSS_SLIDES if slides else CSS
    page = f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "report.html"
        html_path.write_text(page, encoding="utf-8")
        cmd = [
            find_chromium(),
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            f"--user-data-dir={Path(tmp) / 'profile'}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            "file://" + str(html_path),
        ]
        subprocess.run(cmd, capture_output=True, timeout=90)
    return 0 if pdf_path.exists() else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="markdown -> PDF via headless chromium")
    ap.add_argument("md")
    ap.add_argument("pdf")
    ap.add_argument("--slides", action="store_true", help="landscape 16:9 slide deck")
    args = ap.parse_args()
    md_path, pdf_path = Path(args.md), Path(args.pdf)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    rc = build_pdf(md_path, pdf_path, slides=args.slides)
    info = ""
    if pdf_path.exists() and shutil.which("pdfinfo"):
        out = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout
        pages = [l for l in out.splitlines() if l.startswith("Pages:")]
        info = pages[0] if pages else ""
    print(f"rc={rc} {pdf_path} {info}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
