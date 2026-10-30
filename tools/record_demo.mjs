import fs from 'fs';
import { execFileSync } from 'child_process';

// Records the 60 s cut from the live demo at 1920x1080 via Chromium DevTools Protocol.
// Setup: python3 -m onlyyou.cli web --port 8022; python3 -m http.server 8090 --directory docs/assets/record;
//        python3 -m http.server 8091 --directory docs
//        chromium --headless=new --remote-debugging-port=9333 --window-size=1920,1080 about:blank
//        OUT=/tmp/rec-frames node tools/record_demo.mjs
const OUT = process.env.OUT || '/tmp/rec-frames';
const DRY = process.env.DRY === '1';
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));

const targets = await (await fetch('http://127.0.0.1:9333/json/list')).json();
const page = targets.find(t => t.type === 'page' && t.url !== 'about:blank') || targets.find(t => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
let seq = 0; const pending = new Map(); const frames = []; const events = []; const t0ref = {t:0};
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Page.screencastFrame') {
    const file = `${OUT}/${String(frames.length).padStart(5, '0')}.jpg`;
    fs.writeFileSync(file, Buffer.from(m.params.data, 'base64'));
    frames.push({ file, t: Date.now() });
    cdp('Page.screencastFrameAck', { sessionId: m.params.sessionId }).catch(() => {});
  }
};
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
const cdp = (method, params = {}) => new Promise((res, rej) => {
  const id = ++seq; pending.set(id, m => m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result));
  ws.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (expression, awaitPromise = false) => {
  const r = await cdp('Runtime.evaluate', { expression, returnByValue: true, awaitPromise });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + ' ' + (r.exceptionDetails.exception?.description || ''));
  return r.result.value;
};
await cdp('Page.enable'); await cdp('Runtime.enable');
await cdp('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });

const CURSOR = `(() => {
  if (window.__recCursor) return;
  const s = document.createElement('style');
  s.textContent = '*{cursor:none!important}';
  document.documentElement.appendChild(s);
  const d = document.createElement('div');
  d.id = '__recCursor';
  d.innerHTML = '<svg width="30" height="30" viewBox="0 0 30 30"><path d="M3 2 L3 23 L9 17.5 L13 27 L17.6 25 L13.6 15.5 L21.5 14.6 Z" fill="#fff" stroke="#111" stroke-width="2.2" stroke-linejoin="round"/></svg>';
  d.style.cssText = 'position:fixed;left:0;top:0;width:30px;height:30px;z-index:2147483647;pointer-events:none;filter:drop-shadow(0 2px 3px rgba(0,0,0,.55));transition:none';
  document.documentElement.appendChild(d);
  window.__recCursor = d; window.__cursorPos = {x: 960, y: 540};
  window.__setCursor = (x, y, down) => { window.__cursorPos = {x,y}; d.style.transform = 'translate('+x+'px,'+y+'px) scale('+(down?0.86:1)+')'; };
  window.__pulse = (x,y) => {
    const p = document.createElement('div');
    p.style.cssText = 'position:fixed;left:'+(x-18)+'px;top:'+(y-18)+'px;width:36px;height:36px;border:2px solid rgba(255,255,255,.75);border-radius:50%;z-index:2147483646;pointer-events:none;animation:recPulse .35s ease-out forwards';
    document.documentElement.appendChild(p);
    setTimeout(()=>p.remove(), 380);
  };
  const k = document.createElement('style'); k.textContent = '@keyframes recPulse{from{transform:scale(.4);opacity:.9}to{transform:scale(1.6);opacity:0}}'; document.documentElement.appendChild(k);
  window.__setCursor(960,540);
})()`;

async function inject() { await evaluate(CURSOR); }
async function navigate(url) {
  await cdp('Page.navigate', { url });
  for (let i=0;i<80;i++) {
    await sleep(100);
    try { if (await evaluate('document.readyState') === 'complete') break; } catch {}
  }
  await sleep(350);
  await inject();
  await evaluate('window.scrollTo(0,0)');
}
async function moveTo(x, y, ms = 700) {
  const p = await evaluate('window.__cursorPos');
  const sx = p?.x ?? 960, sy = p?.y ?? 540;
  const n = Math.max(8, Math.round(ms / 16));
  for (let i=1;i<=n;i++) {
    const u = i/n, e = u<.5 ? 4*u*u*u : 1-Math.pow(-2*u+2,3)/2;
    const jx = Math.sin(u*Math.PI*3.1)*1.2*(1-u);
    const jy = Math.cos(u*Math.PI*2.7)*1.1*(1-u);
    const x2 = sx+(x-sx)*e+jx, y2 = sy+(y-sy)*e+jy;
    await cdp('Input.dispatchMouseEvent', { type:'mouseMoved', x:x2, y:y2, buttons:0 });
    await evaluate(`window.__setCursor(${x2},${y2},false)`);
    await sleep(ms/n);
  }
}
async function clickText(txt, wait=1200, nth=0) {
  const r = await evaluate(`(() => {
    const all=[...document.querySelectorAll('button,a,[role=button],li')].filter(e=>e.offsetParent!==null && e.textContent.trim().includes(${JSON.stringify(txt)}));
    const e=all[${nth}]; if(!e) return null; const b=e.getBoundingClientRect(); return {x:b.x+b.width/2,y:b.y+b.height/2,t:e.textContent.trim().slice(0,100)};
  })()`);
  if (!r) throw new Error('not found: '+txt);
  console.log('click', JSON.stringify(r));
  await moveTo(r.x, r.y, 650);
  await sleep(180);
  await cdp('Input.dispatchMouseEvent', { type:'mousePressed', x:r.x, y:r.y, button:'left', buttons:1, clickCount:1 });
  await evaluate(`window.__setCursor(${r.x},${r.y},true); window.__pulse(${r.x},${r.y})`);
  await sleep(90);
  await cdp('Input.dispatchMouseEvent', { type:'mouseReleased', x:r.x, y:r.y, button:'left', buttons:0, clickCount:1 });
  await evaluate(`window.__setCursor(${r.x},${r.y},false)`);
  await sleep(wait);
  return r;
}
async function still(name) {
  const s = await cdp('Page.captureScreenshot', { format:'png' });
  fs.writeFileSync(`/tmp/${name}.png`, Buffer.from(s.data, 'base64'));
}

// reset while app is not visible
try { await fetch('http://127.0.0.1:8022/api/reset', { method:'POST', headers:{'Content-Type':'application/json'}, body:'{}' }); } catch (e) { console.error('reset failed', e.message); }

await navigate('http://127.0.0.1:8090/intro.html');
await still('rec-intro');
await cdp('Page.startScreencast', { format:'jpeg', quality:90, maxWidth:1920, maxHeight:1080, everyNthFrame:1 });
const t0 = Date.now(); t0ref.t = t0;
const at = async (sec) => { const d = sec*1000 - (Date.now()-t0); if (d>0) await sleep(d); };
const mark = (name) => { events.push({name, t: Date.now()-t0}); console.log('mark', name, ((Date.now()-t0)/1000).toFixed(2)); };
await at(0.2); mark('intro'); await moveTo(1180,700,900);
await at(2.2); await moveTo(1000,600,800);
await at(3.0); mark('quote'); await navigate('http://127.0.0.1:8090/quote.html'); await moveTo(1050,680,1200);
await at(7.0); mark('app'); await navigate('http://127.0.0.1:8022/?fakecam=1'); await sleep(700); await moveTo(980,620,700);
await at(8.2); mark('grant'); await clickText('grant a mandate', 1800); await moveTo(1700,500,900);
await at(13.2); mark('pay'); await clickText('owner pays invoice', 3200); await moveTo(1700,300,850);
await at(20.2); mark('attack'); await clickText('attacker invoice', 3600); await moveTo(1700,245,850);
await at(30.2); mark('poster'); await clickText('poster tries to unlock', 1400); await moveTo(500,300,700);
await at(36.2); mark('frontier'); await navigate('http://127.0.0.1:8090/frontier.html'); await moveTo(1350,700,1400); await at(41.0); await moveTo(1500,520,1800);
await at(45.2); mark('verify'); await navigate('http://127.0.0.1:8091/verify.html?auto=cross'); await sleep(900); await moveTo(960,500,900); await at(47.0); await moveTo(960,360,1200);
await at(52.2); mark('close'); await navigate('http://127.0.0.1:8090/close.html'); await moveTo(1100,700,1500); await at(56.0); await moveTo(1300,600,1200);
await at(DRY ? 16.0 : 61.0); mark('end');
await cdp('Page.stopScreencast');
const end = Date.now();
fs.writeFileSync(`${OUT}/manifest.json`, JSON.stringify({start:t0, end, frames:frames.map(f=>({file:f.file,t:f.t-t0})), events}, null, 1));
console.log('frames', frames.length, 'elapsed', ((end-t0)/1000).toFixed(2), 'out', OUT);
ws.close();
