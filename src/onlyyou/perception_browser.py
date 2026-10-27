"""A real-browser DOM labeler — the production candidate.

The regex detector in `dom.py` reads inline `style=` strings. That is a demo
shortcut, and the label-layer benchmark shows where it fails (clip-path,
transform, class-only CSS, contrast). The production approach is to ask the
rendering engine: compute styles, walk ancestors for the effective background,
and decide whether a human could see the text.

This module builds an HTML harness, runs headless Chromium, and scores the
browser labeler on the same generated cases. It is a measurement of *this*
labeler on *this* corpus in *this* engine — not a claim about production DOM.
"""

from __future__ import annotations

import html as html_lib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from .perception import DomCase, dom_cases, wilson

_PROBE_JS = r"""
const out=[];
function alpha(c){const m=c.match(/rgba?\(([^)]+)\)/);if(!m)return 1;const p=m[1].split(',').map(Number);return p.length>3?p[3]:1;}
function rgbv(c){const m=c.match(/rgba?\(([^)]+)\)/);if(!m)return [0,0,0];const p=m[1].split(',').map(Number);return [p[0],p[1],p[2]];}
function lum(v){const f=v.map(x=>{x/=255;return x<=0.03928?x/12.92:Math.pow((x+0.055)/1.055,2.4)});return 0.2126*f[0]+0.7152*f[1]+0.0722*f[2];}
function bgOf(el){let e=el;while(e){const cs=getComputedStyle(e);if(alpha(cs.backgroundColor)>0.05)return rgbv(cs.backgroundColor);e=e.parentElement;}return [255,255,255];}
function reason(el){
  const cs=getComputedStyle(el);
  if(cs.display==='none')return 'display-none';
  if(cs.visibility==='hidden'||cs.visibility==='collapse')return 'visibility';
  if(parseFloat(cs.opacity)<0.05)return 'opacity';
  if((cs.contentVisibility||'')==='hidden')return 'content-visibility';
  if(parseFloat(cs.fontSize)<1)return 'font-size-zero';
  if(el.getAttribute('aria-hidden')==='true')return 'aria-hidden';
  if(el.tagName==='INPUT'&&el.type==='hidden')return 'hidden-input';
  const r=el.getBoundingClientRect();
  if(r.width<1||r.height<1)return 'zero-size';
  if(r.right<=0||r.bottom<=0||r.left>10000||r.top>10000)return 'offscreen';
  const cp=(cs.clipPath||'none').replace(/\s+/g,'');
  if(cp!=='none'&&cp.indexOf('inset(100%')===0)return 'clip-path';
  const clip=(cs.clip||'auto');
  if(clip!=='auto'&&/rect\(\s*0(px)?[ ,]+0(px)?[ ,]+0(px)?[ ,]+0(px)?\s*\)/.test(clip))return 'clip';
  if(parseFloat(cs.textIndent)<-1000)return 'text-indent';
  if(alpha(cs.color)<0.05)return 'transparent';
  const L1=lum(rgbv(cs.color)),L2=lum(bgOf(el));
  const hi=Math.max(L1,L2),lo=Math.min(L1,L2);
  if((hi+0.05)/(lo+0.05)<1.15)return 'contrast';
  const filt=(cs.filter||'none');if(/opacity\(\s*0(\.0+)?\s*\)/.test(filt))return 'filter-opacity';
  return '';
}
document.querySelectorAll('.case').forEach(root=>{
  let hidden='';
  if(/<!--/.test(root.innerHTML))hidden='comment';
  if(!hidden){
    const els=[root,...root.querySelectorAll('*')];
    for(const el of els){
      if(el.tagName==='INPUT'&&el.type==='hidden'){hidden='hidden-input';break;}
      if(['STYLE','SCRIPT','TEMPLATE','NOSCRIPT'].includes(el.tagName))continue;
      if(!(el.textContent||'').trim())continue;
      const r=reason(el);
      if(r){hidden=r;break;}
    }
  }
  out.push({id:root.id,hidden:hidden?1:0,reason:hidden});
});
const pre=document.getElementById('out');pre.textContent=JSON.stringify(out);
"""


def chromium_path() -> str | None:
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        p = shutil.which(name)
        if p:
            return p
    return None


def _harness(cases: list[DomCase]) -> str:
    blocks = []
    for i, c in enumerate(cases):
        blocks.append(
            f'<div class="case" id="c{i}" data-hidden="{1 if c.has_injection else 0}" '
            f'data-kind="{html_lib.escape(c.kind)}">{c.html}</div>'
        )
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<style>html,body{margin:0;padding:0;width:1024px;min-height:768px;font:16px/1.4 sans-serif;background:#fff;color:#000}"
        ".case{margin:4px 0}</style></head><body>"
        + "".join(blocks)
        + "<pre id='out'></pre><script>"
        + _PROBE_JS
        + "</script></body></html>"
    )


def run_browser_probe(cases: list[DomCase] | None = None, timeout: int = 60) -> list[dict] | None:
    exe = chromium_path()
    if exe is None:
        return None
    cases = cases or dom_cases()
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "harness.html"
        page.write_text(_harness(cases), encoding="utf-8")
        profile = Path(tmp) / "profile"
        cmd = [
            exe,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--hide-scrollbars",
            "--window-size=1024,768",
            f"--user-data-dir={profile}",
            "--virtual-time-budget=3000",
            "--dump-dom",
            f"file://{page}",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        dom = proc.stdout
    start = dom.find("<pre id=\"out\">")
    end = dom.find("</pre>", start)
    if start < 0 or end < 0:
        return None
    payload = html_lib.unescape(dom[start + len('<pre id="out">') : end]).strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None


def evaluate_dom_labeler_browser(cases: list[DomCase] | None = None) -> dict:
    cases = cases or dom_cases()
    preds = run_browser_probe(cases)
    if preds is None:
        return {
            "available": False,
            "engine": "chromium",
            "note": "headless chromium not available; browser labeler not measured",
        }
    by_id = {p["id"]: p for p in preds}
    hidden = [c for c in cases if c.has_injection]
    benign = [c for c in cases if not c.has_injection]
    tp = fp = 0
    misses: dict[str, int] = {}
    for i, c in enumerate(cases):
        pred = int(by_id.get(f"c{i}", {}).get("hidden", 0))
        if c.has_injection:
            if pred:
                tp += 1
            else:
                misses[c.kind] = misses.get(c.kind, 0) + 1
        elif pred:
            fp += 1
    recall = tp / len(hidden) if hidden else 0.0
    fpr = fp / len(benign) if benign else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    return {
        "available": True,
        "engine": "chromium (computed styles + contrast)",
        "n_hidden": len(hidden),
        "n_benign": len(benign),
        "true_positives": tp,
        "false_positives": fp,
        "recall": round(recall, 4),
        "recall_ci": wilson(tp, len(hidden)),
        "false_positive_rate": round(fpr, 4),
        "fpr_ci": wilson(fp, len(benign)),
        "precision": round(precision, 4),
        "missed_kinds": misses,
        "note": (
            "Measured on this repo's generated cases in headless Chromium. "
            "Not a benchmark of production DOM, and not a browser fingerprinting study."
        ),
    }
