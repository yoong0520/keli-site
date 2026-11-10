// 워커를 Cloudflare 없이 Node 에서 끝까지 돌려 보는 검사 (가짜 R2 · 가짜 GitHub)
// 사용: node worker/test_worker.mjs            → 단위 검사
//       node worker/test_worker.mjs serve 8787 → 관리자 화면 검사용 로컬 서버(워커를 HTTP 로 감쌈)
import worker from './keli-admin.js';
import http from 'node:http';
import { DatabaseSync } from 'node:sqlite';

async function bodyBytes(b) { if (b == null) return new Uint8Array(); if (typeof b === 'string') return new TextEncoder().encode(b); if (b instanceof Uint8Array) return b; return new Uint8Array(await new Response(b).arrayBuffer()); }
export class FakeR2 {
  constructor() { this.objs = new Map(); this.mpus = new Map(); }
  async put(key, body, opts) { const bytes = await bodyBytes(body); this.objs.set(key, { bytes, ct: opts && opts.httpMetadata && opts.httpMetadata.contentType }); return { key, size: bytes.length }; }
  async get(key, opts) {
    const o = this.objs.get(key); if (!o) return null; let bytes = o.bytes, range = null;
    if (opts && opts.range) { const h = opts.range.get ? opts.range.get('Range') : ''; const m = /bytes=(\d+)-(\d*)/.exec(h || ''); if (m) { const s = Number(m[1]), e = m[2] ? Number(m[2]) : bytes.length - 1; bytes = bytes.slice(s, e + 1); range = { offset: s, length: bytes.length }; } }
    return { key, size: o.bytes.length, body: bytes, httpEtag: '"e' + o.bytes.length + '"', range, text: async () => new TextDecoder().decode(o.bytes), writeHttpMetadata(h) { if (o.ct) h.set('Content-Type', o.ct); } };
  }
  async delete(key) { this.objs.delete(key); }
  async list({ prefix }) { return { objects: [...this.objs.keys()].filter((k) => k.startsWith(prefix || '')).map((k) => ({ key: k, size: this.objs.get(k).bytes.length, uploaded: new Date() })) }; }
  async createMultipartUpload(key, opts) { const id = 'u' + Math.random().toString(36).slice(2); this.mpus.set(id, { key, parts: new Map(), ct: opts && opts.httpMetadata && opts.httpMetadata.contentType }); return { key, uploadId: id }; }
  resumeMultipartUpload(key, uploadId) {
    const self = this; const u = this.mpus.get(uploadId); if (!u || u.key !== key) throw new Error('no such upload');
    return { async uploadPart(n, body) { const bytes = await bodyBytes(body); u.parts.set(n, bytes); return { partNumber: n, etag: '"p' + n + '-' + bytes.length + '"' }; },
      async complete(parts) { const ordered = parts.sort((a, b) => a.partNumber - b.partNumber).map((p) => u.parts.get(p.partNumber)); const total = ordered.reduce((s, b) => s + b.length, 0); const out = new Uint8Array(total); let o = 0; for (const b of ordered) { out.set(b, o); o += b.length; } self.objs.set(key, { bytes: out, ct: u.ct }); self.mpus.delete(uploadId); return { key, size: total }; },
      async abort() { self.mpus.delete(uploadId); } };
  }
}
export class FakeD1 {   // Cloudflare D1 흉내: Node 내장 SQLite 로 진짜 SQL 을 돌린다
  constructor() { this.db = new DatabaseSync(':memory:'); }
  prepare(sql) {
    const db = this.db; const st = { _sql: sql, _args: [], bind(...a) { st._args = a.map((v) => (v === undefined ? null : v)); return st; },
      async run() { const r = db.prepare(sql).run(...st._args); return { success: true, results: [], meta: { changes: r.changes, last_row_id: Number(r.lastInsertRowid) } }; },
      async all() { return { success: true, results: db.prepare(sql).all(...st._args) }; },
      async first(col) { const row = db.prepare(sql).get(...st._args); return col ? (row ? row[col] : null) : (row || null); } };
    return st;
  }
  async batch(stmts) { const out = []; for (const s of stmts) out.push(/^\s*(SELECT|WITH)/i.test(s._sql) ? await s.all() : await s.run()); return out; }
}
class FakeKV { constructor() { this.m = new Map(); } async get(k) { return this.m.has(k) ? this.m.get(k) : null; } async put(k, v) { this.m.set(k, String(v)); } }
export const aiCalls = [];
export const env = { FILES: new FakeR2(), KV: new FakeKV(), DB: new FakeD1(), GITHUB_TOKEN: 'ghp_test', SESSION_SECRET: 'secret-for-tests', SETUP_KEY: 'setup-123', REPO: 'yoong0520/keli-site', ALLOW_ORIGINS: 'https://keli-aied.org', SITE_URL: 'https://keli-aied.org/',
  AI: { async run(model, opts) { aiCalls.push({ model, opts }); const sys = opts.messages[0].content; const q = opts.messages[opts.messages.length - 1].content; return { response: (sys.startsWith('You are Iru-mi') ? 'EN answer about: ' : '이음이 답: ') + q + ' / facts=' + (sys.match(/^\[\d+\]/gm) || []).length }; } } };
export const ghLog = [];
export const mailLog = []; let mailMode = 'ok';
export const ghStore = {};   // 가짜 저장소 파일: path → {sha, text}
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, init) => {
  if (String(url) === 'https://keli-aied.org/assets/kb.json') { const fs = await import('node:fs'); return new Response(fs.readFileSync(new URL('../assets/kb.json', import.meta.url)), { status: 200, headers: { 'content-type': 'application/json' } }); }
  if (String(url).startsWith('https://formsubmit.co/ajax/')) { mailLog.push({ url: String(url), headers: init.headers, body: JSON.parse(init.body) }); return new Response(JSON.stringify(mailMode === 'ok' ? { success: 'true', message: 'The form was submitted successfully.' } : { success: 'false', message: 'This form needs Activation.' }), { status: 200, headers: { 'Content-Type': 'application/json' } }); }
  if (!String(url).startsWith('https://api.github.com')) return realFetch(url, init);
  const u = new URL(url); const path = u.pathname; const m = (init && init.method) || 'GET';
  ghLog.push([m, path, (init && init.headers && init.headers.Authorization) || '']);
  const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { 'content-type': 'application/json' } });
  if (path === '/repos/yoong0520/keli-site') return J({ permissions: { push: true } });
  if (path.startsWith('/repos/yoong0520/keli-site/contents/')) {
    const fp = decodeURIComponent(path.split('/contents/')[1]);
    if (m === 'GET') return ghStore[fp] ? J({ sha: ghStore[fp].sha, content: Buffer.from(ghStore[fp].text).toString('base64'), download_url: 'x' }) : J({ message: 'Not Found' }, 404);
    const b = JSON.parse(init.body); if (ghStore[fp] && ghStore[fp].sha !== b.sha) return J({ message: 'sha mismatch' }, 409);
    ghStore[fp] = { sha: 's' + ghLog.length, text: Buffer.from(b.content, 'base64').toString() }; return J({ content: { sha: ghStore[fp].sha }, commit: { message: b.message } });
  }
  if (path === '/repos/yoong0520/keli-site/actions/runs') return J({ workflow_runs: [{ status: 'completed', conclusion: 'success', created_at: '2026-11-03T05:00:00Z', html_url: 'x' }] });
  if (path.endsWith('/dispatches')) return new Response(null, { status: 204 });
  if (path === '/repos/yoong0520/keli-site/commits') return J([{ sha: 'a', html_url: 'x', author: { login: 'bot' }, commit: { message: 'm', author: { name: 'n', date: '2026-11-03T05:00:00Z' } } }]);
  return J({ message: 'unhandled' }, 500);
};

export function call(method, path, { body, token, headers, raw } = {}) {
  const h = Object.assign({ Origin: 'https://keli-aied.org' }, headers || {});
  if (token) h.Authorization = 'Bearer ' + token;
  let b; if (raw != null) b = raw; else if (body != null) { b = JSON.stringify(body); h['Content-Type'] = 'application/json'; }
  return worker.fetch(new Request('https://keli-admin.example.workers.dev' + path, { method, headers: h, body: b }), env, { waitUntil() {} });
}
async function j(r) { const t = await r.text(); try { return JSON.parse(t); } catch (e) { return { _text: t }; } }
function assert(c, msg) { if (!c) { console.error('FAIL:', msg); process.exit(1); } }

if (process.argv[2] === 'serve') {
  const port = Number(process.argv[3] || 8787);
  http.createServer(async (req, res) => {
    const chunks = []; for await (const c of req) chunks.push(c); const buf = Buffer.concat(chunks);
    const headers = new Headers(); for (const [k, v] of Object.entries(req.headers)) if (v != null) headers.set(k, Array.isArray(v) ? v.join(',') : v);
    const r = await worker.fetch(new Request('http://127.0.0.1:' + port + req.url, { method: req.method, headers, body: ['GET', 'HEAD'].includes(req.method) ? undefined : buf }), env, { waitUntil() {} });
    res.writeHead(r.status, Object.fromEntries(r.headers)); res.end(Buffer.from(await r.arrayBuffer()));
  }).listen(port, '127.0.0.1', () => console.log('worker test server on', port));
} else {
  // ---- 1) 상태 · 첫 관리자
  let r = await call('GET', '/api/ping'); let d = await j(r); assert(r.status === 200 && d.setup === true, 'ping setup');
  r = await call('OPTIONS', '/api/login'); assert(r.status === 204 && r.headers.get('Access-Control-Allow-Origin') === 'https://keli-aied.org', 'cors preflight');
  r = await call('POST', '/api/setup', { body: { setup_key: 'wrong', username: 'keli', password: 'password123' } }); assert(r.status === 403, 'setup wrong key');
  r = await call('POST', '/api/setup', { body: { setup_key: 'setup-123', username: 'KELI', password: 'password123', name: 'KELI 사무국' } }); d = await j(r); assert(r.status === 200 && d.token && d.user.username === 'keli' && d.user.role === 'admin', 'setup ok ' + JSON.stringify(d));
  const admin = d.token;
  r = await call('POST', '/api/setup', { body: { setup_key: 'setup-123', username: 'x', password: 'password123' } }); assert(r.status === 409, 'setup twice blocked');
  // ---- 2) 로그인 · 잠금
  r = await call('POST', '/api/login', { body: { username: 'keli', password: 'nope' } }); assert(r.status === 401, 'bad login');
  r = await call('POST', '/api/login', { body: { username: 'keli', password: 'password123' } }); d = await j(r); assert(r.status === 200 && d.token, 'login ok'); const tok = d.token;
  r = await call('GET', '/api/me', { token: tok }); d = await j(r); assert(d.user.name === 'KELI 사무국', 'me');
  r = await call('GET', '/api/me', { token: tok + 'x' }); assert(r.status === 401, 'tampered token rejected');
  for (let i = 0; i < 5; i++) await call('POST', '/api/login', { body: { username: 'keli', password: 'nope' + i } });
  r = await call('POST', '/api/login', { body: { username: 'keli', password: 'password123' } }); assert(r.status === 429, 'locked after 5 failures');
  await env.FILES.put('_auth/lock/keli.json', JSON.stringify({ fails: 0, until: 0 }));
  // ---- 3) 사용자 관리
  r = await call('POST', '/api/users', { token: tok, body: { username: 'staff1', password: 'staffpass1', name: '직원 1', role: 'editor' } }); d = await j(r); assert(r.status === 200 && d.users.length === 2, 'add user');
  r = await call('POST', '/api/login', { body: { username: 'staff1', password: 'staffpass1' } }); d = await j(r); const staff = d.token; assert(d.user.role === 'editor', 'staff login');
  r = await call('POST', '/api/users', { token: staff, body: { username: 'x2', password: 'password123' } }); assert(r.status === 403, 'editor cannot add users');
  r = await call('POST', '/api/me/password', { token: staff, body: { old: 'staffpass1', password: 'newstaffpass' } }); d = await j(r); assert(r.status === 200 && d.token, 'change own password');
  r = await call('GET', '/api/me', { token: staff }); assert(r.status === 401, 'old session dead after password change');
  r = await call('POST', '/api/users/staff1/password', { token: tok, body: { password: 'resetpass99' } }); assert(r.status === 200, 'admin resets password');
  r = await call('POST', '/api/login', { body: { username: 'staff1', password: 'resetpass99' } }); d = await j(r); assert(r.status === 200, 'login with reset password'); const staff2 = d.token;
  // ---- 4) GitHub 대리 호출
  r = await call('GET', '/gh/user', { token: staff2 }); d = await j(r); assert(d.login === 'staff1', 'gh user = login user');
  r = await call('GET', '/gh/repos/yoong0520/keli-site', { token: staff2 }); d = await j(r); assert(d.permissions.push === true, 'gh repo');
  r = await call('PUT', '/gh/repos/yoong0520/keli-site/contents/content/notices.json', { token: staff2, body: { message: 'm', content: Buffer.from('{"items":[]}').toString('base64'), branch: 'main' } }); d = await j(r); assert(r.status === 200 && d.content.sha, 'gh put contents');
  assert(ghLog[ghLog.length - 1][2] === 'Bearer ghp_test', 'server token used, not user');
  r = await call('GET', '/gh/repos/yoong0520/keli-site/actions/runs?per_page=1&branch=main', { token: staff2 }); d = await j(r); assert(d.workflow_runs, 'gh runs with query');
  r = await call('POST', '/gh/repos/yoong0520/keli-site/actions/workflows/pages.yml/dispatches', { token: staff2, body: { ref: 'main' } }); assert(r.status === 204, 'gh dispatch');
  r = await call('DELETE', '/gh/repos/yoong0520/keli-site/contents/x', { token: staff2 }); assert(r.status === 403, 'gh delete blocked');
  r = await call('GET', '/gh/repos/other/repo/contents/x', { token: staff2 }); assert(r.status === 403, 'gh other repo blocked');
  r = await call('GET', '/gh/repos/yoong0520/keli-site/contents/x'); assert(r.status === 401, 'gh needs login');
  // ---- 5) 파일: 한 번에 올리기 · 읽기 · 범위 · 지우기
  r = await call('PUT', '/files/content/files/2026/11/a%20b.pdf', { token: staff2, raw: '%PDF-1.4 hello', headers: { 'Content-Type': 'application/pdf' } }); d = await j(r); assert(r.status === 200 && d.url === '/files/content/files/2026/11/a%20b.pdf', 'put file ' + JSON.stringify(d));
  r = await call('GET', '/files/content/files/2026/11/a%20b.pdf'); assert(r.status === 200 && r.headers.get('Content-Type') === 'application/pdf' && (await r.text()) === '%PDF-1.4 hello', 'get file public');
  r = await call('GET', '/files/content/files/2026/11/a%20b.pdf', { headers: { Range: 'bytes=0-3' } }); assert(r.status === 206 && (await r.text()) === '%PDF', 'range');
  r = await call('PUT', '/files/x.pdf', { raw: 'x' }); assert(r.status === 401, 'put needs login');
  r = await call('GET', '/files/_auth/users.json'); assert(r.status === 400, 'auth file not readable');
  r = await call('GET', '/files/list?prefix=content/', { token: staff2 }); d = await j(r); assert(d.files.length === 1, 'list');
  // ---- 6) 조각 올리기(multipart)
  r = await call('POST', '/files/mpu/create', { token: staff2, body: { key: 'content/files/2026/11/big.mp4' } }); d = await j(r); const up = d; assert(up.uploadId, 'mpu create');
  const parts = [];
  for (let n = 1; n <= 3; n++) { r = await call('PUT', '/files/mpu/part?key=' + encodeURIComponent(up.key) + '&uploadId=' + up.uploadId + '&part=' + n, { token: staff2, raw: new Uint8Array(1000).fill(n) }); d = await j(r); assert(d.etag, 'part ' + n); parts.push({ partNumber: d.partNumber, etag: d.etag }); }
  r = await call('POST', '/files/mpu/complete', { token: staff2, body: { key: up.key, uploadId: up.uploadId, parts } }); d = await j(r); assert(d.size === 3000 && d.url === '/files/content/files/2026/11/big.mp4', 'mpu complete ' + JSON.stringify(d));
  r = await call('GET', '/files/content/files/2026/11/big.mp4'); const bytes = new Uint8Array(await r.arrayBuffer()); assert(bytes.length === 3000 && bytes[0] === 1 && bytes[2999] === 3 && r.headers.get('Content-Type') === 'video/mp4', 'mpu assembled');
  r = await call('DELETE', '/files/content/files/2026/11/big.mp4', { token: staff2 }); assert(r.status === 200, 'delete');
  r = await call('GET', '/files/content/files/2026/11/big.mp4'); assert(r.status === 404, 'deleted');
  r = await call('DELETE', '/api/users/staff1', { token: tok }); d = await j(r); assert(d.users.length === 1, 'delete user');
  r = await call('GET', '/api/me', { token: staff2 }); assert(r.status === 401, 'deleted user session dead');
  // ---- 7) 챗봇
  r = await call('POST', '/api/chat', { body: { lang: 'ko', messages: [{ role: 'user', content: '도입은 어떻게 하나요?' }] } }); d = await j(r); assert(r.status === 200 && d.answer.indexOf('이음이 답') === 0 && d.engine === 'workers-ai', 'chat ko ' + JSON.stringify(d));
  assert(/facts=\d+/.test(d.answer) && Number(d.answer.match(/facts=(\d+)/)[1]) >= 3, 'facts given to model');
  assert(d.sources.length >= 1 && d.sources.some((x) => /join/.test(x.url)), 'join source ' + JSON.stringify(d.sources));
  r = await call('POST', '/api/chat', { body: { lang: 'en', messages: [{ role: 'user', content: 'What is KELI?' }] } }); d = await j(r); assert(d.answer.indexOf('EN answer') === 0, 'chat en');
  r = await call('POST', '/api/chat', { body: { lang: 'ko', messages: [] } }); assert(r.status === 400, 'empty question');
  const aiBackup = env.AI; env.AI = null;
  r = await call('POST', '/api/chat', { body: { lang: 'ko', messages: [{ role: 'user', content: '수학 튜터' }] } }); d = await j(r); assert(d.engine === 'search' && /HAI-MathTutor/.test(d.answer), 'search fallback ' + d.answer.slice(0, 80)); env.AI = aiBackup;
  for (let i = 0; i < 20; i++) await call('POST', '/api/chat', { body: { lang: 'ko', messages: [{ role: 'user', content: 'x' + i }] }, headers: { 'CF-Connecting-IP': '9.9.9.9' } });
  r = await call('POST', '/api/chat', { body: { lang: 'ko', messages: [{ role: 'user', content: 'once more' }] }, headers: { 'CF-Connecting-IP': '9.9.9.9' } }); assert(r.status === 429, 'rate limit');
  r = await call('OPTIONS', '/api/chat'); assert(r.status === 204, 'chat preflight');
  // ---- 8) 방문 통계
  const UA = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36', 'CF-Connecting-IP': '1.2.3.4' };
  const MOB = { 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1', 'CF-Connecting-IP': '5.6.7.8' };
  r = await call('POST', '/api/hit', { raw: JSON.stringify({ t: 'pv', p: '/index.html', ti: 'KELI 플랫폼', r: 'https://www.google.com/', l: 'ko' }), headers: UA }); assert(r.status === 204, 'hit ok');
  await call('POST', '/api/hit', { raw: JSON.stringify({ t: 'pv', p: '/services.html', ti: 'Marketplace', r: 'https://keli-aied.org/', l: 'ko' }), headers: UA });
  await call('POST', '/api/hit', { raw: JSON.stringify({ t: 'pv', p: '/services.html?x=1#top', ti: 'Marketplace', r: 'https://m.search.naver.com/search', src: 'newsletter', med: 'email', cmp: 'nov', l: 'ko' }), headers: MOB });
  await call('POST', '/api/hit', { raw: JSON.stringify({ t: 'click', p: '/archive-o122.html', x: 'https://keli-aied.org/content/files/a.pdf' }), headers: MOB });
  await call('POST', '/api/hit', { raw: JSON.stringify({ t: 'pv', p: '/admin.html' }), headers: UA });                       // 관리자 화면은 집계 안 함
  await call('POST', '/api/hit', { raw: JSON.stringify({ t: 'pv', p: '/' }), headers: { 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1)' } });   // 봇 제외
  await call('POST', '/api/hit', { raw: JSON.stringify({ t: 'pv', p: '/' }), headers: Object.assign({}, UA, { Origin: 'https://evil.example' }) });     // 다른 사이트 제외
  r = await call('GET', '/api/stats?days=7'); assert(r.status === 401, 'stats needs login');
  r = await call('GET', '/api/stats?days=7', { token: tok }); d = await j(r);
  assert(d.enabled === true && d.total.pv === 3 && d.total.uv === 2, 'stats totals ' + JSON.stringify(d.total));
  assert(d.pages[0].path === '/services.html' && d.pages[0].pv === 2 && d.pages.some((x) => x.path === '/'), 'pages ' + JSON.stringify(d.pages));
  assert(d.refs.some((x) => x.ref === 'google.com') && d.refs.some((x) => x.ref === 'm.search.naver.com') && d.refs.some((x) => x.ref === '' && x.n === 1), 'refs ' + JSON.stringify(d.refs));
  assert(d.utm.length === 1 && d.utm[0].src === 'newsletter', 'utm');
  assert(d.dev.some((x) => x.dev === 'mobile' && x.n === 1) && d.dev.some((x) => x.dev === 'desktop' && x.n === 2), 'devices ' + JSON.stringify(d.dev));
  assert(d.clicks.length === 1 && /a\.pdf$/.test(d.clicks[0].tgt), 'clicks');
  assert(d.daily.length === 1 && d.daily[0].pv === 3 && d.today.pv === 3, 'daily/today');
  const dbBackup = env.DB; env.DB = null;
  r = await call('POST', '/api/hit', { raw: '{}', headers: UA }); assert(r.status === 204, 'hit without DB is a no-op');
  r = await call('GET', '/api/stats', { token: tok }); d = await j(r); assert(d.enabled === false, 'stats without DB'); env.DB = dbBackup;
  // ---- 9) 문의 양식 · 문의함 · 메일 전달
  const INQ = { type: 'univ', org: '강원대학교', name: '김교수', email: 'Prof@Kangwon.ac.kr', tel: '033-000-0000', services: ['HAI-LRS', 'HAI-Check'], course: '선형대수학', body: '2027-1학기 도입을 검토하고 있습니다.', page: '/join.html', lang: 'ko' };
  r = await call('POST', '/api/contact', { raw: JSON.stringify(INQ), headers: Object.assign({}, UA, { Origin: 'https://keli-aied.org' }) }); d = await j(r);
  assert(r.status === 200 && d.ok && /^KELI-\d{6}-001$/.test(d.ref) && d.mailed === true, 'contact ok ' + JSON.stringify(d));
  assert(mailLog.length === 1 && mailLog[0].url === 'https://formsubmit.co/ajax/contact%40keliedu.org', 'mail relayed to office ' + JSON.stringify(mailLog[0] && mailLog[0].url));
  assert(mailLog[0].headers.Origin === 'https://keli-aied.org' && /join\.html$/.test(mailLog[0].headers.Referer), 'relay carries site origin');
  assert(mailLog[0].body._replyto === 'prof@kangwon.ac.kr' && mailLog[0].body._subject.indexOf(d.ref) > 0 && mailLog[0].body['관심서비스'] === 'HAI-LRS, HAI-Check' && mailLog[0].body._template === 'table', 'mail fields ' + JSON.stringify(mailLog[0].body));
  assert(mailLog[0].body._autoresponse.indexOf(d.ref) > 0, 'autoresponse carries ref');
  r = await call('POST', '/api/contact', { raw: JSON.stringify(Object.assign({}, INQ, { email: 'bad' })), headers: UA }); assert(r.status === 400, 'bad email rejected');
  r = await call('POST', '/api/contact', { raw: JSON.stringify(Object.assign({}, INQ, { hp: 'x' })), headers: UA }); d = await j(r); assert(r.status === 200 && /-000$/.test(d.ref) && mailLog.length === 1, 'honeypot swallowed');
  r = await call('POST', '/api/contact', { raw: JSON.stringify(INQ), headers: Object.assign({}, UA, { Origin: 'https://evil.example' }) }); assert(r.status === 403, 'foreign origin rejected');
  mailMode = 'fail';
  r = await call('POST', '/api/contact', { raw: JSON.stringify(Object.assign({}, INQ, { org: '제주대학교' })), headers: UA }); d = await j(r);
  assert(r.status === 200 && d.ok && d.mailed === false && /-002$/.test(d.ref), 'kept even when mail relay fails ' + JSON.stringify(d));
  mailMode = 'ok';
  r = await call('GET', '/api/inquiries'); assert(r.status === 401, 'inbox needs login');
  r = await call('GET', '/api/inquiries', { token: tok }); d = await j(r);
  assert(d.enabled && d.items.length === 2 && d.counts.new === 2 && d.items[0].org === '제주대학교' && d.items[0].mailed === 0 && d.items[1].mailed === 1, 'inbox list ' + JSON.stringify(d.counts));
  const failedId = d.items[0].id, okId = d.items[1].id;
  r = await call('POST', '/api/inquiries/' + failedId + '/mail', { token: tok }); assert(r.status === 200, 'resend ok'); assert(mailLog.length === 3, 'resend relayed');
  r = await call('POST', '/api/inquiries/' + okId, { token: tok, body: { status: 'done', note: '11/12 답장 보냄' } }); assert(r.status === 200, 'status update');
  r = await call('GET', '/api/inquiries?status=done', { token: tok }); d = await j(r); assert(d.items.length === 1 && d.items[0].note === '11/12 답장 보냄' && d.items[0].updated_by === 'keli', 'filter by status ' + JSON.stringify(d.items.map((x) => x.status)));
  r = await call('GET', '/api/inquiries', { token: tok }); d = await j(r); assert(d.items.find((x) => x.id === failedId).mailed === 1, 'resend marked mailed');
  r = await call('POST', '/api/inquiries/' + failedId + '/delete'); assert(r.status === 401, 'delete needs login');
  r = await call('POST', '/api/inquiries/' + failedId + '/delete', { token: tok }); assert(r.status === 200, 'delete ok');
  r = await call('POST', '/api/inquiries/' + failedId + '/delete', { token: tok }); assert(r.status === 404, 'delete twice 404');
  r = await call('GET', '/api/inquiries', { token: tok }); d = await j(r); assert(d.items.length === 1 && !d.items.find((x) => x.id === failedId), 'deleted gone');
  r = await call('POST', '/api/contact', { raw: JSON.stringify(Object.assign({}, INQ, { org: '강원대학교' })), headers: Object.assign({}, UA, { 'CF-Connecting-IP': '7.7.7.7' }) }); d = await j(r); assert(/-003$/.test(d.ref), 'ref not reused after delete ' + d.ref);
  for (let i = 0; i < 5; i++) await call('POST', '/api/contact', { raw: JSON.stringify(INQ), headers: { 'User-Agent': UA['User-Agent'], 'CF-Connecting-IP': '9.9.9.9' } });
  r = await call('POST', '/api/contact', { raw: JSON.stringify(INQ), headers: { 'User-Agent': UA['User-Agent'], 'CF-Connecting-IP': '9.9.9.9' } }); assert(r.status === 429, 'contact rate limit');
  env.DB = null;
  r = await call('POST', '/api/contact', { raw: JSON.stringify(INQ), headers: { 'User-Agent': UA['User-Agent'], 'CF-Connecting-IP': '8.8.8.8' } }); d = await j(r); assert(r.status === 200 && d.ok && /^KELI-\d{6}-[0-9A-F]{4}$/.test(d.ref), 'contact without DB still mails ' + JSON.stringify(d));
  env.DB = dbBackup;
  console.log('worker tests OK');
}
