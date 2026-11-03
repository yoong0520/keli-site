/* KELI 관리자 서버 (Cloudflare Worker)
   하는 일 세 가지
   1) 아이디·비밀번호 로그인  — 직원은 GitHub 토큰 없이 아이디·비밀번호로 관리자 화면에 들어온다
   2) 큰 파일 창고(R2)        — 첨부파일을 100MB 제한 없이 올리고(여러 조각으로 나눠 올림) 사이트에서 바로 연다
   3) GitHub 대리 호출        — 글 저장(커밋)·배포 상태는 사무국이 한 번 넣어 둔 GitHub 토큰(비밀 변수)으로 서버가 대신 처리한다

   설정(Cloudflare 대시보드 → Workers → 이 워커 → Settings)
   - Bindings: R2 bucket  변수 이름 FILES  → 버킷 keli-files      (큰 파일 창고. R2 는 결제 수단 등록이 필요하지만 무료 한도(10GB) 안이면 0원)
               KV namespace 변수 이름 KV → keli-auth            (R2 를 아직 못 쓸 때 사용자 목록만 여기에 둔다. 둘 중 하나는 있어야 함)
   - Variables & Secrets (Secret):
       GITHUB_TOKEN     저장소(yoong0520/keli-site) Contents·Actions 읽고 쓰기 권한의 Fine-grained 토큰
       SESSION_SECRET   아무 긴 무작위 문자열(로그인 유지용 서명 열쇠)
       SETUP_KEY        첫 관리자 계정을 만들 때 한 번만 쓰는 비밀 문자열
   - Variables (Plain text):
       REPO             yoong0520/keli-site
       ALLOW_ORIGINS    https://keli-aied.org,https://www.keli-aied.org   (쉼표로 여러 개)
   사용자 목록은 R2 안의 _auth/users.json 에 저장된다(비밀번호는 PBKDF2-SHA256 10만 회 해시 · Cloudflare 한도).
*/

const ENC = new TextEncoder();
const SESSION_DAYS = 30;
const PART_MIN = 5 * 1024 * 1024;        // R2 multipart 최소 조각(마지막 조각 제외)
const LOCK_AFTER = 5, LOCK_MINUTES = 15;   // 로그인 5회 실패 → 15분 잠금

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin') || '';
    const cors = corsHeaders(origin, env);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    try {
      let res;
      if (url.pathname.startsWith('/api/')) res = await api(request, env, url);
      else if (url.pathname.startsWith('/gh/')) res = await ghProxy(request, env, url);
      else if (url.pathname.startsWith('/files/')) res = await files(request, env, url, ctx);
      else res = json({ ok: true, service: 'KELI admin server', setup: !(await loadUsers(env)).length }, 200);
      for (const [k, v] of Object.entries(cors)) res.headers.set(k, v);
      return res;
    } catch (e) {
      const res = json({ error: e.message || String(e) }, e.status || 500);
      for (const [k, v] of Object.entries(cors)) res.headers.set(k, v);
      return res;
    }
  },
};

// ---------------------------------------------------------------- 공통
function json(obj, status = 200, extra = {}) {
  return new Response(JSON.stringify(obj), { status, headers: Object.assign({ 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }, extra) });
}
function err(message, status) { const e = new Error(message); e.status = status; return e; }
function corsHeaders(origin, env) {
  const allow = (env.ALLOW_ORIGINS || '').split(',').map((s) => s.trim()).filter(Boolean);
  const ok = origin && (allow.length === 0 || allow.includes(origin) || /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin));
  return {
    'Access-Control-Allow-Origin': ok ? origin : (allow[0] || '*'),
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Authorization,Content-Type,Accept,X-GitHub-Api-Version,X-Part-Number,X-Upload-Id',
    'Access-Control-Expose-Headers': 'ETag,Content-Length',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}
async function readJson(request) { try { return await request.json(); } catch (e) { throw err('본문이 JSON 이 아닙니다', 400); } }
function b64url(bytes) { return btoa(String.fromCharCode(...new Uint8Array(bytes))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); }
function b64urlDecode(s) { s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '='; return Uint8Array.from(atob(s), (c) => c.charCodeAt(0)); }
function randomHex(n) { const a = new Uint8Array(n); crypto.getRandomValues(a); return [...a].map((b) => b.toString(16).padStart(2, '0')).join(''); }

// ---------------------------------------------------------------- 비밀번호 · 세션
async function hashPassword(password, saltHex) {
  const salt = saltHex ? b64urlDecode(saltHex) : crypto.getRandomValues(new Uint8Array(16));
  const key = await crypto.subtle.importKey('raw', ENC.encode(password), 'PBKDF2', false, ['deriveBits']);
  const bits = await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations: 100000 }, key, 256);
  return { salt: b64url(salt), hash: b64url(bits) };
}
async function verifyPassword(password, rec) { const h = await hashPassword(password, rec.salt); return h.hash === rec.hash; }
async function hmac(secret, data) {
  const key = await crypto.subtle.importKey('raw', ENC.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return b64url(await crypto.subtle.sign('HMAC', key, ENC.encode(data)));
}
async function makeSession(env, user) {
  const payload = b64url(ENC.encode(JSON.stringify({ u: user.username, r: user.role, n: user.name, exp: Date.now() + SESSION_DAYS * 86400000, v: user.pv || 0 })));
  return payload + '.' + (await hmac(env.SESSION_SECRET, payload));
}
async function readSession(request, env) {
  const h = request.headers.get('Authorization') || '';
  const tok = h.startsWith('Bearer ') ? h.slice(7).trim() : '';
  if (!tok || tok.indexOf('.') < 0) return null;
  const [payload, sig] = tok.split('.');
  if ((await hmac(env.SESSION_SECRET, payload)) !== sig) return null;
  let data; try { data = JSON.parse(new TextDecoder().decode(b64urlDecode(payload))); } catch (e) { return null; }
  if (!data.exp || data.exp < Date.now()) return null;
  const users = await loadUsers(env);
  const u = users.find((x) => x.username === data.u);
  if (!u || (u.pv || 0) !== (data.v || 0)) return null;   // 비밀번호를 바꾸면 예전 로그인은 모두 끊긴다
  return { username: u.username, name: u.name, role: u.role };
}
async function requireUser(request, env) { const s = await readSession(request, env); if (!s) throw err('로그인이 필요합니다', 401); return s; }

// ---------------------------------------------------------------- 사용자 저장(R2 _auth/users.json, R2 가 없으면 KV)
async function storeGet(env, key) {
  if (env.FILES) { const o = await env.FILES.get(key); return o ? await o.text() : null; }
  if (env.KV) return await env.KV.get(key);
  throw err('서버에 저장소 바인딩(FILES 또는 KV)이 없습니다. Cloudflare 설정을 확인하세요', 500);
}
async function storePut(env, key, text) {
  if (env.FILES) return env.FILES.put(key, text, { httpMetadata: { contentType: 'application/json' } });
  if (env.KV) return env.KV.put(key, text);
  throw err('서버에 저장소 바인딩(FILES 또는 KV)이 없습니다', 500);
}
async function loadUsers(env) { const t = await storeGet(env, '_auth/users.json'); if (!t) return []; try { return (JSON.parse(t).users) || []; } catch (e) { return []; } }
async function saveUsers(env, users) { await storePut(env, '_auth/users.json', JSON.stringify({ users }, null, 2)); }
async function lockState(env, username) { const t = await storeGet(env, '_auth/lock/' + username + '.json'); if (!t) return { fails: 0, until: 0 }; try { return JSON.parse(t); } catch (e) { return { fails: 0, until: 0 }; } }
async function lockSave(env, username, st) { await storePut(env, '_auth/lock/' + username + '.json', JSON.stringify(st)); }
function cleanUsername(u) { u = String(u || '').trim().toLowerCase(); if (!/^[a-z0-9._-]{2,32}$/.test(u)) throw err('아이디는 영문·숫자·점·밑줄·하이픈 2~32자입니다', 400); return u; }
function checkPassword(p) { if (typeof p !== 'string' || p.length < 8) throw err('비밀번호는 8자 이상이어야 합니다', 400); }
function publicUser(u) { return { username: u.username, name: u.name, role: u.role, created: u.created }; }

// ---------------------------------------------------------------- /api/*
async function api(request, env, url) {
  const p = url.pathname.replace(/^\/api/, '');
  const m = request.method;
  if (p === '/ping' && m === 'GET') return json({ ok: true, setup: !(await loadUsers(env)).length, repo: env.REPO || '', files: !!env.FILES });

  if (p === '/setup' && m === 'POST') {   // 첫 관리자 만들기(사용자가 하나도 없을 때, SETUP_KEY 필요)
    const b = await readJson(request);
    if (!env.SETUP_KEY || b.setup_key !== env.SETUP_KEY) throw err('설정 열쇠(SETUP_KEY)가 맞지 않습니다', 403);
    if ((await loadUsers(env)).length) throw err('이미 관리자가 있습니다. 로그인한 뒤 "사용자" 메뉴에서 추가하세요', 409);
    const username = cleanUsername(b.username); checkPassword(b.password);
    const h = await hashPassword(b.password);
    const user = { username, name: String(b.name || username).trim().slice(0, 40), role: 'admin', salt: h.salt, hash: h.hash, pv: 0, created: new Date().toISOString() };
    await saveUsers(env, [user]);
    return json({ ok: true, token: await makeSession(env, user), user: publicUser(user) });
  }

  if (p === '/login' && m === 'POST') {
    const b = await readJson(request);
    const username = String(b.username || '').trim().toLowerCase(), password = String(b.password || '');
    const users = await loadUsers(env); const u = users.find((x) => x.username === username);
    const st = u ? await lockState(env, username) : { fails: 0, until: 0 };
    if (st.until && st.until > Date.now()) throw err('로그인을 여러 번 실패해 ' + Math.ceil((st.until - Date.now()) / 60000) + '분 동안 잠겼습니다', 429);
    if (!u || !(await verifyPassword(password, u))) {
      if (u) { st.fails = (st.until && st.until < Date.now()) ? 1 : (st.fails || 0) + 1; st.until = st.fails >= LOCK_AFTER ? Date.now() + LOCK_MINUTES * 60000 : 0; await lockSave(env, username, st); }
      throw err('아이디 또는 비밀번호가 맞지 않습니다', 401);
    }
    if (st.fails) await lockSave(env, username, { fails: 0, until: 0 });
    return json({ ok: true, token: await makeSession(env, u), user: publicUser(u) });
  }

  const me = await requireUser(request, env);
  if (p === '/me' && m === 'GET') return json({ ok: true, user: me });
  if (p === '/me/password' && m === 'POST') {
    const b = await readJson(request); const users = await loadUsers(env); const u = users.find((x) => x.username === me.username);
    if (!(await verifyPassword(String(b.old || ''), u))) throw err('현재 비밀번호가 맞지 않습니다', 403);
    checkPassword(b.password); const h = await hashPassword(b.password); u.salt = h.salt; u.hash = h.hash; u.pv = (u.pv || 0) + 1; await saveUsers(env, users);
    return json({ ok: true, token: await makeSession(env, u) });
  }
  if (p === '/users' && m === 'GET') { if (me.role !== 'admin') throw err('관리자만 볼 수 있습니다', 403); return json({ ok: true, users: (await loadUsers(env)).map(publicUser) }); }
  if (p === '/users' && m === 'POST') {
    if (me.role !== 'admin') throw err('관리자만 추가할 수 있습니다', 403);
    const b = await readJson(request); const users = await loadUsers(env); const username = cleanUsername(b.username); checkPassword(b.password);
    if (users.find((x) => x.username === username)) throw err('이미 있는 아이디입니다', 409);
    const h = await hashPassword(b.password);
    users.push({ username, name: String(b.name || username).trim().slice(0, 40), role: b.role === 'admin' ? 'admin' : 'editor', salt: h.salt, hash: h.hash, pv: 0, created: new Date().toISOString() });
    await saveUsers(env, users); return json({ ok: true, users: users.map(publicUser) });
  }
  let mm = p.match(/^\/users\/([a-z0-9._-]+)\/password$/);
  if (mm && m === 'POST') {
    if (me.role !== 'admin') throw err('관리자만 바꿀 수 있습니다', 403);
    const b = await readJson(request); const users = await loadUsers(env); const u = users.find((x) => x.username === mm[1]); if (!u) throw err('없는 사용자입니다', 404);
    checkPassword(b.password); const h = await hashPassword(b.password); u.salt = h.salt; u.hash = h.hash; u.pv = (u.pv || 0) + 1; await saveUsers(env, users); await lockSave(env, u.username, { fails: 0, until: 0 });
    return json({ ok: true });
  }
  mm = p.match(/^\/users\/([a-z0-9._-]+)$/);
  if (mm && m === 'DELETE') {
    if (me.role !== 'admin') throw err('관리자만 지울 수 있습니다', 403);
    let users = await loadUsers(env); if (mm[1] === me.username) throw err('자기 계정은 지울 수 없습니다', 400);
    if (!users.find((x) => x.username === mm[1])) throw err('없는 사용자입니다', 404);
    users = users.filter((x) => x.username !== mm[1]); await saveUsers(env, users); return json({ ok: true, users: users.map(publicUser) });
  }
  throw err('없는 요청입니다: ' + m + ' ' + p, 404);
}

// ---------------------------------------------------------------- /gh/* : GitHub API 대리 호출(허용 경로만)
async function ghProxy(request, env, url) {
  await requireUser(request, env);
  if (!env.GITHUB_TOKEN) throw err('서버에 GITHUB_TOKEN 비밀 변수가 없습니다', 500);
  const repo = env.REPO || '';
  const path = url.pathname.slice(3) + url.search;   // '/gh' 뒤
  const bare = url.pathname.slice(3);
  const m = request.method;
  const R = repo.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&');
  const allowed = [
    [new RegExp('^/user$'), ['GET']],
    [new RegExp('^/repos/' + R + '$'), ['GET']],
    [new RegExp('^/repos/' + R + '/contents/.+'), ['GET', 'PUT']],
    [new RegExp('^/repos/' + R + '/actions/runs$'), ['GET']],
    [new RegExp('^/repos/' + R + '/actions/workflows/[^/]+/dispatches$'), ['POST']],
    [new RegExp('^/repos/' + R + '/commits$'), ['GET']],
  ];
  if (!repo || !allowed.some(([re, ms]) => re.test(bare) && ms.includes(m))) throw err('허용되지 않은 GitHub 요청입니다: ' + m + ' ' + bare, 403);
  const headers = { 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + env.GITHUB_TOKEN, 'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'KELI-admin-worker' };
  let body;
  if (m === 'PUT' || m === 'POST') { headers['Content-Type'] = 'application/json'; body = await request.text(); }
  if (m === 'GET' && bare === '/user') {   // 로그인 사용자 이름을 GitHub 계정 대신 돌려준다
    const s = await readSession(request, env); return json({ login: s.username, name: s.name, role: s.role });
  }
  const r = await fetch('https://api.github.com' + path, { method: m, headers, body });
  const text = await r.text();
  const empty = r.status === 204 || r.status === 205 || r.status === 304;
  return new Response(empty ? null : text, { status: r.status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' } });
}

// ---------------------------------------------------------------- /files/* : R2 파일 창고
function fileKey(url) {
  const key = decodeURIComponent(url.pathname.slice('/files/'.length));
  if (!key || key.startsWith('_auth/') || key.includes('..')) throw err('잘못된 파일 경로입니다', 400);
  return key;
}
function guessType(key) {
  const ext = (key.split('.').pop() || '').toLowerCase();
  return { pdf: 'application/pdf', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', webp: 'image/webp', svg: 'image/svg+xml', mp4: 'video/mp4', mov: 'video/quicktime', webm: 'video/webm', mp3: 'audio/mpeg', zip: 'application/zip', hwp: 'application/x-hwp', hwpx: 'application/hwp+zip', doc: 'application/msword', docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', ppt: 'application/vnd.ms-powerpoint', pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation', xls: 'application/vnd.ms-excel', xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', txt: 'text/plain; charset=utf-8', html: 'text/html; charset=utf-8', json: 'application/json' }[ext] || 'application/octet-stream';
}
async function files(request, env, url, ctx) {
  const m = request.method;
  if (!env.FILES) throw err('파일 창고(R2 버킷 FILES)가 아직 연결되지 않았습니다. 첨부는 GitHub(100MB 한도)로 올라갑니다', 501);
  // 조각 올리기(multipart): 100MB 요청 제한을 넘는 파일을 위해 브라우저가 50MB씩 나눠 보낸다
  if (url.pathname === '/files/mpu/create' && m === 'POST') {
    await requireUser(request, env); const b = await readJson(request); const key = String(b.key || ''); if (!key || key.startsWith('_auth/') || key.includes('..')) throw err('잘못된 파일 경로입니다', 400);
    const mpu = await env.FILES.createMultipartUpload(key, { httpMetadata: { contentType: b.contentType || guessType(key) } });
    return json({ ok: true, key: mpu.key, uploadId: mpu.uploadId });
  }
  if (url.pathname === '/files/mpu/part' && m === 'PUT') {
    await requireUser(request, env); const key = url.searchParams.get('key'), uploadId = url.searchParams.get('uploadId'), n = Number(url.searchParams.get('part')); if (!key || !uploadId || !n) throw err('key·uploadId·part 가 필요합니다', 400);
    const mpu = env.FILES.resumeMultipartUpload(key, uploadId); const part = await mpu.uploadPart(n, request.body);
    return json({ ok: true, partNumber: part.partNumber, etag: part.etag });
  }
  if (url.pathname === '/files/mpu/complete' && m === 'POST') {
    await requireUser(request, env); const b = await readJson(request); const mpu = env.FILES.resumeMultipartUpload(b.key, b.uploadId);
    const obj = await mpu.complete(b.parts); return json({ ok: true, key: obj.key, size: obj.size, url: '/files/' + obj.key.split('/').map(encodeURIComponent).join('/') });
  }
  if (url.pathname === '/files/mpu/abort' && m === 'POST') { await requireUser(request, env); const b = await readJson(request); await env.FILES.resumeMultipartUpload(b.key, b.uploadId).abort(); return json({ ok: true }); }
  if (url.pathname === '/files/list' && m === 'GET') {
    await requireUser(request, env); const prefix = url.searchParams.get('prefix') || ''; const l = await env.FILES.list({ prefix, limit: 500 });
    return json({ ok: true, files: l.objects.filter((o) => !o.key.startsWith('_auth/')).map((o) => ({ key: o.key, size: o.size, uploaded: o.uploaded })) });
  }
  const key = fileKey(url);
  if (m === 'PUT') {   // 한 번에 올리기(100MB 이하)
    await requireUser(request, env);
    const obj = await env.FILES.put(key, request.body, { httpMetadata: { contentType: request.headers.get('Content-Type') || guessType(key) } });
    return json({ ok: true, key: obj.key, size: obj.size, url: '/files/' + key.split('/').map(encodeURIComponent).join('/') });
  }
  if (m === 'DELETE') { await requireUser(request, env); await env.FILES.delete(key); return json({ ok: true }); }
  if (m === 'GET' || m === 'HEAD') {   // 누구나 읽기(사이트 첨부)
    const range = request.headers.get('Range');
    const obj = await env.FILES.get(key, range ? { range: request.headers } : undefined);
    if (!obj) return json({ error: '파일이 없습니다' }, 404);
    const h = new Headers(); obj.writeHttpMetadata(h); h.set('ETag', obj.httpEtag); h.set('Accept-Ranges', 'bytes'); h.set('Cache-Control', 'public, max-age=3600');
    if (!h.get('Content-Type') || h.get('Content-Type') === 'application/octet-stream') h.set('Content-Type', guessType(key));
    const name = key.split('/').pop(); h.set('Content-Disposition', 'inline; filename*=UTF-8\'\'' + encodeURIComponent(name));
    if (range && obj.range) { h.set('Content-Range', 'bytes ' + obj.range.offset + '-' + (obj.range.offset + obj.range.length - 1) + '/' + obj.size); return new Response(m === 'HEAD' ? null : obj.body, { status: 206, headers: h }); }
    return new Response(m === 'HEAD' ? null : obj.body, { status: 200, headers: h });
  }
  throw err('없는 요청입니다', 404);
}
