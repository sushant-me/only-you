#!/usr/bin/env python3
"""Build a designed, paginated PDF handbook from docs/handbook.md.

Source of truth is Markdown so the author can edit it. Pages are separated by
`<!-- PAGE -->`; every content page starts with one `# heading`. The script adds
the cover, a table of contents with real page numbers, running headers and
footers, and checks for overflow before printing with headless Chromium.

    python3 tools/handbook.py
    python3 tools/handbook.py --check-only     # report overflowing pages

Style tokens live in CSS below; edit them freely.
"""

from __future__ import annotations

import argparse
import base64
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "handbook.md"
OUTPUT = ROOT / "docs" / "handbook.pdf"

TITLE = "ONLY YOU"
SUBTITLE = "The handbook: what it is, what it proves, and how to change every part of it."
LINKS = [
    ("Repo", "https://github.com/sushant-me/only-you"),
    ("Playground", "https://sushant-me.github.io/only-you/playground.html"),
    ("Verifier", "https://sushant-me.github.io/only-you/verify.html"),
]
MODELS = ["Muse Spark", "Muse Wonder", "Muse Voice Transcribe", "SAM 3.1", "Muse Image"]

PAGE_KEY = {
    "Why this project exists": ("25% → 0%", "the confused-deputy corpus with the full gate"),
    "The authority model": ("0% / 0%", "attacks executed / false refusals at the full gate"),
    "The Meta stack": ("4 models", "one authority layer; each model has a committed artifact"),
    "What the evidence proves (1)": ("18/18", "receipts verified on the hard corpus; 99 live calls"),
    "What the evidence proves (2)": ("50% → 0%", "frontier DeepSeek: 50% → 0%; human FAR 0/12 capped"),
    "The demo, beat by beat": ("179 s", "a four-second contrast opens the film"),
    "The presentation kit": ("1 · 2 · 10", "brief pages · report pages · deck slides"),
    "Run it": ("make judge", "172 tests, 67-check audit and a live smoke in ~25 s"),
    "Verify it": ("VERIFIED", "CROSS-MODEL: both chains and both mandates, in the browser"),
    "How to change the numbers": ("67/67", "audit checks that catch documentation drift"),
    "How to change the documents and media": ("regenerates", "every asset here has a source and a build command"),
    "How this handbook is built": ("18 pages", "fixed A4 pages, overflow-checked before printing"),
    "Submission runbook": ("4 Nov", "9:00 PM ET / 5 Nov, 7:45 AM NPT"),
    "Limitations and roadmap": ("17 rows", "of published failure modes, each with a status and a next step"),
    "Judge Q&A": ("10 answers", "the questions a sceptical judge will actually ask"),
    "Appendix": ("1 command", "make judge reproduces the whole evidence path"),
}

PAGE_META = {
    "Why this project exists": ("README.md · docs/brief.md", "make brief", "docs/brief.pdf"),
    "The authority model": ("src/onlyyou/provenance.py · policy.py · mandates.py · receipts.py", "make test", "results-real-doc/"),
    "The Meta stack": ("src/onlyyou/model.py · scene_muse.py · sam.py · voice_muse.py", "make sam-check · asr-check", "results-sam/ · results/voice-asr.json"),
    "What the evidence proves (1)": ("results-real-doc/benchmark.json", "make bench-meta", "results-real-verify/benchmark.json"),
    "What the evidence proves (2)": ("results-cross-model/ · results/voice-study-human.json", "make cross-model · voice-study", "results/latency.json"),
    "The demo, beat by beat": ("docs/narration-script.md · demo-3min.mp4", "make voice · audit", "docs/demo-3min.mp4 (179 s)"),
    "The presentation kit": ("docs/brief.md · report.md · pitch-event.md", "make brief report pitch thumb", "docs/*.pdf"),
    "Run it": ("Makefile · tools/", "make judge · preflight", "AUDIT.md · results/"),
    "Verify it": ("tools/verify_audit.py · docs/verify.html", "make cross-model", "results-cross-model/cross-model-audit.json"),
    "How to change the numbers": ("this table → canonical artifacts", "python3 tools/audit.py", "AUDIT.md (67/67)"),
    "How to change the documents and media": ("docs/*.md · docs/assets/", "make brief report pitch handbook thumb", "docs/handbook.pdf"),
    "How this handbook is built": ("docs/handbook.md · tools/handbook.py", "make handbook", "docs/handbook.pdf"),
    "Submission runbook": ("SUBMIT-NOW.md · FORM-ANSWERS.md", "make preflight", "docs/submission-final.md"),
    "Limitations and roadmap": ("docs/limitations.md · judge-qa.md", "make test", "docs/limitations.md"),
    "Judge Q&A": ("docs/judge-qa.md", "make report", "docs/report.pdf"),
    "Appendix": ("repo map · this page", "make judge", "git log --oneline"),
}


CSS = r"""
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; }
body { font-family: -apple-system, "Segoe UI", Roboto, "Liberation Sans", Arial, sans-serif;
       color: #141a26; font-size: 9.75pt; line-height: 1.44; }
.page { position: relative; width: 210mm; height: 297mm; padding: 17mm 16mm 16mm;
        overflow: hidden; page-break-after: always; break-after: page; background: #fff;
        display: flex; flex-direction: column; }
.content { flex: 1 1 auto; min-height: 0; }
.page:last-child { page-break-after: auto; break-after: auto; }
.header { display: flex; justify-content: space-between; align-items: baseline;
          border-bottom: 1.2pt solid #e3e7ef; padding-bottom: 2.2mm; margin-bottom: 4mm;
          font-size: 7.4pt; letter-spacing: .08em; text-transform: uppercase; color: #8a93a5; }
.header b { color: #141a26; letter-spacing: .12em; }
.footer { position: absolute; left: 16mm; right: 16mm; bottom: 8mm; display: flex;
          justify-content: space-between; font-size: 7.4pt; color: #9aa2b1;
          border-top: .6pt solid #eef1f6; padding-top: 2mm; }
h1 { font-size: 23pt; line-height: 1.08; letter-spacing: -.02em; margin: 1mm 0 2.5mm; color: #0d1220; }
h2 { font-size: 13pt; margin: 4.5mm 0 1.8mm; color: #0d1220; letter-spacing: -.01em; }
h3 { font-size: 10.4pt; margin: 3.2mm 0 1.2mm; color: #2b3447; text-transform: uppercase; letter-spacing: .07em; }
p { margin: 0 0 2.4mm; }
.lede { font-size: 11.2pt; color: #3a4459; line-height: 1.5; }
a { color: #1d4fd8; text-decoration: none; }
code { font-family: "JetBrains Mono", "SFMono-Regular", Menlo, Consolas, monospace; font-size: 8.4pt;
       background: #f1f4fa; padding: .4mm 1.2mm; border-radius: 1mm; color: #17202f; }
pre { font-family: "JetBrains Mono", "SFMono-Regular", Menlo, Consolas, monospace; font-size: 7.9pt;
      line-height: 1.4; background: #0e1420; color: #e6ebf5; padding: 3mm 3.5mm; border-radius: 2mm;
      margin: 1.5mm 0 3mm; white-space: pre-wrap; }
pre code { background: none; color: inherit; padding: 0; font-size: inherit; }
ul, ol { margin: 0 0 2.6mm 5mm; padding: 0; }
li { margin: 0 0 1.1mm; }
table { width: 100%; border-collapse: collapse; margin: 1.4mm 0 3mm; font-size: 8.5pt; }
th { background: #0e1420; color: #fff; text-align: left; padding: 1.6mm 2mm; font-weight: 600; }
td { padding: 1.5mm 2mm; border-bottom: .5pt solid #e5e9f1; vertical-align: top; }
tr:nth-child(even) td { background: #f8f9fc; }
blockquote { margin: 2mm 0 3mm; padding: 2mm 3mm; border-left: 2.2pt solid #ff2d55;
             background: #fff5f7; color: #3a2430; font-size: 9.2pt; }
hr { border: 0; border-top: .6pt solid #e3e7ef; margin: 3mm 0; }
img { max-width: 100%; border-radius: 2mm; border: .6pt solid #e3e7ef; }
.cover { background: radial-gradient(120% 90% at 80% 0%, #1b2747 0%, #0a0d15 58%, #07090f 100%);
         color: #fff; padding: 26mm 20mm; display: flex; flex-direction: column; }
.cover .kicker { font-size: 8.6pt; letter-spacing: .3em; text-transform: uppercase; color: #8b96ab; }
.cover h1 { color: #fff; font-size: 62pt; letter-spacing: -.04em; margin: 8mm 0 3mm; }
.cover .sub { font-size: 17pt; line-height: 1.35; color: #dfe5f0; max-width: 150mm; }
.cover .thesis { margin-top: auto; font-size: 11.5pt; color: #9fb0cc; }
.cover .chips { display: flex; gap: 2mm; flex-wrap: wrap; margin: 8mm 0 4mm; }
.cover .chip { border: .7pt solid #3b4a68; color: #cfd9ea; padding: 1.5mm 3mm; border-radius: 6mm; font-size: 8.2pt; }
.cover .links { font-size: 9pt; color: #9fb0cc; line-height: 1.7; }
.cover .version { margin-top: 6mm; font-size: 8pt; color: #6f7d96; }
.cover .rule { width: 26mm; height: 1.4mm; background: #ff2d55; margin: 4mm 0 6mm; }
.toc h1 { font-size: 21pt; }
.toc table { font-size: 9.4pt; margin-top: 4mm; }
.toc td { border-bottom: .5pt dotted #cfd6e4; padding: 1.6mm 1mm; background: none !important; }
.toc td.num { text-align: right; width: 12mm; color: #6a7487; font-variant-numeric: tabular-nums; }
.toc .note { margin-top: 7mm; }
.tocgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; margin-top: 8mm; }
.tocgrid > div { background: #f6f8fc; border-radius: 2mm; padding: 4mm 4.5mm; }
.tocgrid h3 { margin: 0 0 2mm; font-size: 8.4pt; }
.tocgrid ul { margin: 0 0 0 4mm; font-size: 8.6pt; }
.tocgrid li { margin-bottom: 1.4mm; }
.small { font-size: 8.6pt; color: #5c667b; }
.keystrip { margin-top: 3.4mm; border-left: 3.2pt solid #ff2d55; background: #f6f8fc;
            padding: 2mm 3mm; display: flex; gap: 4mm; align-items: baseline; }
.keystrip .num { font-size: 15pt; font-weight: 800; letter-spacing: -.02em; color: #0d1220; white-space: nowrap; }
.keystrip .what { font-size: 8.8pt; color: #5c667b; line-height: 1.35; }
.pagemeta { margin-top: auto; border-top: .6pt solid #e3e7ef; padding-top: 2.4mm;
            display: grid; grid-template-columns: 1.2fr 1fr 1.2fr; gap: 3mm; font-size: 7.3pt; color: #6a7487; }
.pagemeta b { display: block; font-size: 6.6pt; letter-spacing: .12em; color: #9aa2b1; margin-bottom: .8mm; }
.pagemeta span { line-height: 1.45; }
.tag { display: inline-block; font-size: 7.6pt; letter-spacing: .06em; text-transform: uppercase;
       background: #eef2fb; color: #2b4a9c; padding: .6mm 1.8mm; border-radius: 4mm; }
"""


def md_inline(text: str, base: Path) -> str:
    text = html.escape(text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: image(m, base), text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def image(match: re.Match, base: Path) -> str:
    alt, src = match.group(1), match.group(2)
    if src.startswith(("http://", "https://", "data:")):
        return f'<img alt="{alt}" src="{src}"/>'
    path = (base / src).resolve()
    if not path.exists():
        return f'<span class="small">[missing image: {html.escape(src)}]</span>'
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode()
    caption = f'<div class="small" style="margin-top:1mm">{html.escape(alt)}</div>' if alt else ""
    return f'<img alt="{html.escape(alt)}" src="data:{mime};base64,{data}"/>{caption}'


def render_page(markdown: str, base: Path) -> tuple[str, str]:
    lines = markdown.splitlines()
    body: list[str] = []
    title = ""
    i = 0
    in_list: str | None = None
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if in_list and line[:1].isspace() and stripped and body and body[-1].startswith("<li>"):
            body[-1] = body[-1][:-5] + " " + md_inline(stripped, base) + "</li>"
            i += 1
            continue
        if not stripped:
            if in_list:
                body.append(f"</{in_list}>")
                in_list = None
            i += 1
            continue
        if stripped.startswith("```"):
            if in_list:
                body.append(f"</{in_list}>")
                in_list = None
            lang = stripped[3:].strip()
            code: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            body.append(f'<pre><code class="language-{lang}">{html.escape(chr(10).join(code))}</code></pre>')
            continue
        if stripped == "---":
            body.append("<hr/>")
            i += 1
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if m:
            if in_list:
                body.append(f"</{in_list}>")
                in_list = None
            level = len(m.group(1))
            content = md_inline(m.group(2), base)
            if level == 1 and not title:
                title = re.sub(r"<[^>]+>", "", content)
            body.append(f"<h{level}>{content}</h{level}>")
            i += 1
            continue
        if stripped.startswith("|"):
            if in_list:
                body.append(f"</{in_list}>")
                in_list = None
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            body.append("<table>")
            for r_idx, row in enumerate(cells):
                if all(re.fullmatch(r":?-{2,}:?", c or "-") for c in row):
                    continue
                tag = "th" if r_idx == 0 else "td"
                body.append("<tr>" + "".join(f"<{tag}>{md_inline(c, base)}</{tag}>" for c in row) + "</tr>")
            body.append("</table>")
            continue
        if stripped.startswith(">"):
            if in_list:
                body.append(f"</{in_list}>")
                in_list = None
            quote = [stripped[1:].strip()]
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            body.append("<blockquote>" + "<br/>".join(md_inline(q, base) for q in quote if q) + "</blockquote>")
            continue
        if stripped.startswith("- "):
            if in_list != "ul":
                if in_list:
                    body.append(f"</{in_list}>")
                body.append("<ul>")
                in_list = "ul"
            body.append(f"<li>{md_inline(stripped[2:], base)}</li>")
            i += 1
            continue
        m_ol = re.match(r"^\d+\.\s+(.*)$", stripped)
        if m_ol:
            if in_list != "ol":
                if in_list:
                    body.append(f"</{in_list}>")
                body.append("<ol>")
                in_list = "ol"
            body.append(f"<li>{md_inline(m_ol.group(1), base)}</li>")
            i += 1
            continue
        if in_list:
            body.append(f"</{in_list}>")
            in_list = None
        para = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,3}\s|[-*]\s|\d+\.\s|>|\||```|---$)", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        body.append("<p>" + " ".join(md_inline(p, base) for p in para) + "</p>")
    if in_list:
        body.append(f"</{in_list}>")
    return title, "\n".join(body)


def git_version() -> tuple[str, str]:
    try:
        commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, check=True).stdout.strip()
        date = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%cs"],
                              capture_output=True, text=True, check=True).stdout.strip()
        return commit, date
    except Exception:
        return "working-tree", "unknown"


def build(check_only: bool = False) -> int:
    raw = SOURCE.read_text()
    pages = [p.strip() for p in raw.split("<!-- PAGE -->") if p.strip()]
    rendered = [render_page(p, SOURCE.parent) for p in pages]
    commit, date = git_version()
    total = 2 + len(rendered)
    toc_rows = "".join(
        f'<tr><td>{html.escape(title)}</td><td class="num">{idx + 3}</td></tr>'
        for idx, (title, _) in enumerate(rendered)
    )
    cover = f"""
<section class="page cover">
  <div class="kicker">Meta Global AI Developer Hackathon 2026 · Indie track</div>
  <h1>{TITLE}</h1>
  <div class="rule"></div>
  <div class="sub">{html.escape(SUBTITLE)}</div>
  <div class="chips">{''.join(f'<span class="chip">{m}</span>' for m in MODELS)}</div>
  <div class="thesis">Capability is solved. Authority isn’t.</div>
  <div class="links">{' · '.join(f'<a href="{url}" style="color:#9fb0cc">{name}</a>' for name, url in LINKS)}</div>
  <div class="version">v{date} · {commit} · 172 tests · audit 67/67</div>
</section>"""
    toc = f"""
<section class="page toc">
  <div class="header"><span>ONLY YOU · handbook</span><b>contents</b></div>
  <h1>Contents</h1>
  <p class="lede">Read pages 3–7 for the pitch, architecture and evidence; 8–13 for the demo, run/verify and change maps;
  14–18 for the build, submission, limits and appendix.</p>
  <table>{toc_rows}</table>
  <div class="note small">Source of this document: <code>docs/handbook.md</code>. Layout and style:
  <code>tools/handbook.py</code>. Rebuild: <code>make handbook</code>. Every number here has a canonical
  artifact listed on page 12, so changing one starts there.</div>
  <div class="tocgrid">
    <div><h3>Status at build</h3><ul>
      <li><b>172 tests</b> · audit <b>67/67</b> · CI green (tests + Docker)</li>
      <li><b>179 s</b> film · 1-page brief · 2-page report · 10-slide deck</li>
      <li><b>Four Meta models</b>, each with a committed artifact</li>
      <li><b>Frontier DeepSeek:</b> 50% undefended → <b>0%</b> gated, 18/18 receipts</li>
      <li>Frontier DeepSeek: <b>50% → 0%</b>, 18/18 receipts</li>
      <li>Human voice study: owner 3/3 · <b>0/12 FAR</b> at capped 0.10 (pilot + held-out)</li>
    </ul></div>
    <div><h3>How to use this book</h3><ul>
      <li>Every page ends with <b>EDIT · BUILD · PROOF</b>: the file, the command, the artifact.</li>
      <li>Tables are the checkable evidence; prose is the why.</li>
      <li>Change a number by changing its canonical artifact (page 12), never prose first.</li>
      <li>This PDF refuses to build if any fixed page overflows.</li>
    </ul></div>
  </div>
  <div class="footer"><span>v{date} · {commit}</span><span>2 / {total}</span></div>
</section>"""
    body = [cover, toc]
    for idx, (title, page_body) in enumerate(rendered):
        num = idx + 3
        edit, build, proof = PAGE_META.get(title, ("docs/handbook.md", "make handbook", "docs/handbook.pdf"))
        num, what = PAGE_KEY.get(title, ("", ""))
        key_block = (
            f'<div class="keystrip"><span class="num">{html.escape(num)}</span>'
            f'<span class="what">{html.escape(what)}</span></div>' if num else ""
        )
        meta_block = (
            '<div class="pagemeta">'
            f'<span><b>EDIT</b>{html.escape(edit)}</span>'
            f'<span><b>BUILD</b>{html.escape(build)}</span>'
            f'<span><b>PROOF</b>{html.escape(proof)}</span>'
            '</div>'
        )
        body.append(
            f"""<section class="page">
  <div class="header"><span>ONLY YOU · handbook</span><b>{html.escape(title)}</b></div>
  <div class="content">{page_body}</div>
  {key_block}
  {meta_block}
  <div class="footer"><span>v{date} · {commit}</span><span>{num} / {total}</span></div>
</section>"""
        )
    script = """
<script>
window.addEventListener('load', () => {
  const bad = [...document.querySelectorAll('.page:not(.cover)')].map((p, i) => {
    const c = p.querySelector('.content');
    const over = Math.max(p.scrollHeight - p.clientHeight, c ? c.scrollHeight - c.clientHeight : 0);
    return {n: i + 2, over};
  }).filter(x => x.over > 2).map(x => x.n + ':' + x.over);
  document.title = bad.length ? 'OVERFLOW:' + bad.join(',') : 'OK:' + document.querySelectorAll('.page').length;
});
</script>"""
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>building</title>
<style>{CSS}</style></head><body>
{''.join(body)}
{script}
</body></html>"""
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, dir="/tmp") as fh:
        fh.write(doc)
        tmp = Path(fh.name)
    try:
        dom = subprocess.run(
            ["chromium", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
             "--virtual-time-budget=3000", "--dump-dom", tmp.as_uri()],
            capture_output=True, text=True, check=False,
        ).stdout
        m = re.search(r"<title>([^<]+)</title>", dom)
        status = m.group(1) if m else "?"
        print(f"layout: {status}")
        if check_only:
            return 0 if status.startswith("OK") else 1
        if not status.startswith("OK"):
            print("refusing to print: fix the overflowing pages first", file=sys.stderr)
            return 1
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["chromium", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
             "--no-pdf-header-footer", f"--print-to-pdf={OUTPUT}", tmp.as_uri()],
            check=True, capture_output=True,
        )
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
        return 0
    finally:
        tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    raise SystemExit(build(args.check_only))
