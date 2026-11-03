/* KELI 콘텐츠 스튜디오(관리자) — GitHub 저장소의 content/*.json 과 assets/stats.json 을 브라우저에서 직접 고친다.
   저장 = 커밋. 커밋이 올라가면 GitHub Actions 가 사이트를 다시 만들어 1~2분 뒤 반영된다.
   화면: 왼쪽 메뉴(대시보드 · 홈 화면 · 소식·공지 · 아카이브 · 서비스 · 행사 · 보도·언론 · 영상 · 게시 기록 · 사이트 설정)
         + 목록·편집 2단(소식·아카이브) + 위쪽 배포 상태·게시 버튼. */
(function () {
  'use strict';
  var CFG = window.KELI_ADMIN || { repo: 'yoong0520/keli-site', branch: 'main', site: './', workflow: 'pages.yml' };
  if (location.protocol !== 'file:') CFG.site = new URL('./', location.href).href;   // 주소(도메인)가 바뀌어도 그대로 동작
  var API = 'https://api.github.com';
  // 관리자 서버(Cloudflare Worker)가 있으면: 아이디·비밀번호 로그인 + GitHub 대리 호출 + 큰 파일 창고(R2)
  function apiBase() { var a = ''; try { a = localStorage.getItem('keli_api') || ''; } catch (e) {} return String(CFG.api || a || '').replace(/\/+$/, ''); }
  var SERVER = apiBase(), SERVER_FILES = false;   // SERVER_FILES: 서버에 파일 창고(R2)가 붙어 있는가(ping 으로 확인)
  var qs = function (s, r) { return (r || document).querySelector(s); };
  var qsa = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var token = null, user = null, state = { notices: null, archive: null, hidden: null, stats: null, site: null, cats: null, feeds: {}, sha: {} };
  var dirty = false;   // 편집 중 저장 안 한 변경이 있는가

  // ---------------------------------------------------------------- 공통 UI
  var toastT = null;
  function toast(msg, ms) { var t = qs('#toast'); t.textContent = msg; t.setAttribute('data-show', '1'); clearTimeout(toastT); toastT = setTimeout(function () { t.setAttribute('data-show', '0'); }, ms || 3200); }
  function modal(html, wide) { var m = qs('#modal'), b = qs('#modal-box'); b.className = 'box' + (wide ? ' wide' : ''); b.innerHTML = html; m.setAttribute('data-open', '1'); var f = qs('input,button,textarea', b); if (f) f.focus(); return b; }
  function closeModal() { qs('#modal').setAttribute('data-open', '0'); qs('#modal-box').innerHTML = ''; }
  function confirmBox(title, text, okLabel, danger) {
    return new Promise(function (res) {
      var b = modal('<h3 style="margin:0 0 8px;font-size:22px">' + esc(title) + '</h3><p class="muted" style="margin:0 0 20px">' + esc(text) + '</p><div style="display:flex;gap:8px;justify-content:flex-end"><button class="btn ghost" type="button" data-x="0">취소</button><button class="btn' + (danger ? ' danger' : '') + '" type="button" data-x="1">' + esc(okLabel || '확인') + '</button></div>');
      qsa('[data-x]', b).forEach(function (bt) { bt.addEventListener('click', function () { closeModal(); res(bt.getAttribute('data-x') === '1'); }); });
    });
  }
  qs('#modal').addEventListener('click', function (e) { if (e.target === qs('#modal')) closeModal(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeModal(); });
  window.addEventListener('beforeunload', function (e) { if (dirty) { e.preventDefault(); e.returnValue = ''; } });

  // ---------------------------------------------------------------- 토큰
  function tokKey() { return SERVER ? 'keli_admin_session' : 'keli_admin_token'; }
  function loadToken() { try { return localStorage.getItem(tokKey()) || sessionStorage.getItem(tokKey()); } catch (e) { return null; } }
  function saveToken(t, keep) { try { (keep ? localStorage : sessionStorage).setItem(tokKey(), t); (keep ? sessionStorage : localStorage).removeItem(tokKey()); } catch (e) {} }
  function clearToken() { try { localStorage.removeItem(tokKey()); sessionStorage.removeItem(tokKey()); } catch (e) {} }

  // ---------------------------------------------------------------- GitHub API
  function gh(path, opt) {
    opt = opt || {};
    var h = { 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + token, 'X-GitHub-Api-Version': '2022-11-28' };
    if (opt.body) h['Content-Type'] = 'application/json';
    var base = SERVER ? SERVER + '/gh' : API;
    return fetch(base + path, { method: opt.method || 'GET', headers: h, body: opt.body ? JSON.stringify(opt.body) : undefined, cache: 'no-store' }).then(function (r) {
      if (r.status === 204) return null;
      return r.text().then(function (t) { var j = {}; try { j = t ? JSON.parse(t) : {}; } catch (e) {} if (!r.ok) { var err = new Error(j.message || ('HTTP ' + r.status)); err.status = r.status; throw err; } return j; });
    });
  }
  function encPath(p) { return p.split('/').map(encodeURIComponent).join('/'); }
  function srv(path, opt) {   // 관리자 서버 /api/* · /files/*
    opt = opt || {}; var h = {}; if (token) h['Authorization'] = 'Bearer ' + token; if (opt.body) h['Content-Type'] = 'application/json'; if (opt.headers) for (var k in opt.headers) h[k] = opt.headers[k];
    return fetch(SERVER + path, { method: opt.method || 'GET', headers: h, body: opt.raw != null ? opt.raw : (opt.body ? JSON.stringify(opt.body) : undefined), cache: 'no-store' }).then(function (r) {
      return r.text().then(function (t) { var j = {}; try { j = t ? JSON.parse(t) : {}; } catch (e) {} if (!r.ok) { var err = new Error(j.error || j.message || ('HTTP ' + r.status)); err.status = r.status; throw err; } return j; });
    });
  }
  function b64enc(str) { var bytes = new TextEncoder().encode(str), bin = ''; for (var i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000)); return btoa(bin); }
  function b64dec(b64) { var bin = atob(b64.replace(/\n/g, '')), bytes = new Uint8Array(bin.length); for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i); return new TextDecoder().decode(bytes); }
  function getFile(path) {
    return gh('/repos/' + CFG.repo + '/contents/' + encPath(path) + '?ref=' + CFG.branch).then(function (j) {
      if (j.content) return { sha: j.sha, text: b64dec(j.content) };
      return fetch(j.download_url + (j.download_url.indexOf('?') > -1 ? '&' : '?') + 't=' + Date.now(), { cache: 'no-store' }).then(function (r) { return r.text(); }).then(function (t) { return { sha: j.sha, text: t }; });
    }).catch(function (e) { if (e.status === 404) return { sha: null, text: null }; throw e; });
  }
  function putFile(path, contentB64, message, sha) {
    var body = { message: message, content: contentB64, branch: CFG.branch }; if (sha) body.sha = sha;
    return gh('/repos/' + CFG.repo + '/contents/' + encPath(path), { method: 'PUT', body: body });
  }
  function saveJson(path, obj, message) {
    var text = JSON.stringify(obj, null, 2) + '\n';
    return putFile(path, b64enc(text), message, state.sha[path]).then(function (j) { state.sha[path] = j.content.sha; return j; })
      .catch(function (e) {
        if (e.status === 409 || e.status === 422) { return getFile(path).then(function (f) { state.sha[path] = f.sha; return putFile(path, b64enc(text), message, f.sha); }).then(function (j) { state.sha[path] = j.content.sha; return j; }); }
        throw e;
      });
  }
  function loadJson(path, fallback) { return getFile(path).then(function (f) { state.sha[path] = f.sha; if (!f.text) return fallback; try { return JSON.parse(f.text); } catch (e) { toast(path + ' 파일이 깨져 있어 새로 만듭니다'); return fallback; } }); }
  function readFileB64(file) { return new Promise(function (res, rej) { var r = new FileReader(); r.onload = function () { res(String(r.result).split(',')[1]); }; r.onerror = rej; r.readAsDataURL(file); }); }
  function safeName(n) { return n.normalize('NFC').replace(/[\\\/:*?"<>|#%&+\s]+/g, '_').replace(/_+/g, '_'); }
  function fmtSize(b) { return b > 1048576 ? (b / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(b / 1024)) + ' KB'; }
  var PART = CFG.part || 50 * 1048576, SINGLE = CFG.single || 90 * 1048576;   // 조각 크기 · 한 번에 올리는 한도(Cloudflare 요청 한도 100MB 아래)
  function uploadFile(file, onProgress) {
    var d = new Date(), ym = d.getFullYear() + '/' + String(d.getMonth() + 1).padStart(2, '0');
    var path = 'content/files/' + ym + '/' + Date.now().toString(36) + '_' + safeName(file.name);
    if (!SERVER || !SERVER_FILES) {
      if (file.size > 100 * 1048576) return Promise.reject(new Error('100MB 를 넘는 파일은 올릴 수 없습니다(관리자 서버에 파일 창고를 연결하면 제한이 없어집니다)'));
      return readFileB64(file).then(function (b64) { return putFile(path, b64, '첨부 올림: ' + file.name); }).then(function () { return { name: file.name, url: path, size: fmtSize(file.size) }; });
    }
    var key = path; var ct = file.type || 'application/octet-stream';
    if (file.size <= SINGLE) {
      return srv('/files/' + encPath(key), { method: 'PUT', raw: file, headers: { 'Content-Type': ct } }).then(function (r) { return { name: file.name, url: SERVER + r.url, size: fmtSize(file.size), store: 'r2' }; });
    }
    var parts = [], up = null, total = Math.ceil(file.size / PART);
    return srv('/files/mpu/create', { method: 'POST', body: { key: key, contentType: ct } }).then(function (r) {
      up = r;
      var chain = Promise.resolve();
      for (var i = 0; i < total; i++) (function (n) {
        chain = chain.then(function () {
          var blob = file.slice(n * PART, Math.min(file.size, (n + 1) * PART));
          return srv('/files/mpu/part?key=' + encodeURIComponent(key) + '&uploadId=' + encodeURIComponent(up.uploadId) + '&part=' + (n + 1), { method: 'PUT', raw: blob, headers: { 'Content-Type': 'application/octet-stream' } })
            .then(function (pr) { parts.push({ partNumber: pr.partNumber, etag: pr.etag }); if (onProgress) onProgress(n + 1, total); else toast('올리는 중… ' + (n + 1) + '/' + total + ' 조각 (' + file.name + ')', 4000); });
        });
      })(i);
      return chain;
    }).then(function () { return srv('/files/mpu/complete', { method: 'POST', body: { key: key, uploadId: up.uploadId, parts: parts } }); })
      .then(function (r) { return { name: file.name, url: SERVER + r.url, size: fmtSize(file.size), store: 'r2' }; })
      .catch(function (e) { if (up) srv('/files/mpu/abort', { method: 'POST', body: { key: key, uploadId: up.uploadId } }).catch(function () {}); throw e; });
  }
  function dispatch() { return gh('/repos/' + CFG.repo + '/actions/workflows/' + CFG.workflow + '/dispatches', { method: 'POST', body: { ref: CFG.branch } }); }
  function liveFeed(k) { if (state.feeds[k]) return Promise.resolve(state.feeds[k]); return fetch('assets/' + k + '.live.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : { items: [] }; }).catch(function () { return { items: [] }; }).then(function (j) { state.feeds[k] = j; return j; }); }

  // ---------------------------------------------------------------- 배포 상태
  var pollT = null;
  function deployState(st, text) { var d = qs('#deploy'); d.setAttribute('data-state', st); qs('#deploy-text').innerHTML = text; }
  function checkDeploy(keep) {
    clearTimeout(pollT);
    return gh('/repos/' + CFG.repo + '/actions/runs?per_page=1&branch=' + CFG.branch).then(function (j) {
      var r = (j.workflow_runs || [])[0]; if (!r) { deployState('idle', '배포 기록 없음'); return; }
      var when = new Date(r.created_at).toLocaleString('ko-KR', { hour12: false, month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' });
      if (r.status !== 'completed') { deployState('running', '배포 중 · 1~2분'); pollT = setTimeout(function () { checkDeploy(true); }, 10000); return; }
      if (r.conclusion === 'success') deployState('ok', '반영 완료 · ' + when + (keep ? ' · 방금 저장한 내용이 올라갔습니다' : ''));
      else deployState('fail', '배포 실패 · <a href="' + esc(r.html_url) + '" target="_blank" rel="noopener">기록 보기</a>');
    }).catch(function (e) { deployState('idle', '배포 상태를 읽지 못함(토큰에 Actions 권한 필요)'); });
  }
  function afterSave(msg) { dirty = false; setDirty(false); toast(msg + ' · 1~2분 뒤 사이트에 반영됩니다'); deployState('running', '커밋됨 · 배포 시작'); clearTimeout(pollT); pollT = setTimeout(function () { checkDeploy(true); }, 8000); }
  function setDirty(on) { dirty = on; var s = qs('#edit-status'); if (s) s.innerHTML = on ? '<span class="dirty">● 수정됨 · 저장 안 됨</span>' : '<span class="saved">● 저장됨</span>'; }

  // ---------------------------------------------------------------- 데이터
  function ensure(kind) {
    if (kind === 'notices' && !state.notices) return loadJson('content/notices.json', { items: [] }).then(function (j) { state.notices = j; });
    if (kind === 'archive' && !state.archive) return loadJson('content/archive.json', { items: [] }).then(function (j) { state.archive = j; });
    if (kind === 'hidden' && !state.hidden) return loadJson('content/hidden.json', { events: [], press: [], videos: [], unn: [], services: [] }).then(function (j) { state.hidden = j; ['events', 'press', 'videos', 'unn', 'services'].forEach(function (k) { state.hidden[k] = (state.hidden[k] || []).map(String); }); });
    if (kind === 'stats' && !state.stats) return loadJson('assets/stats.json', { services: null, universities: 23, companies: 31, courses: null, basis: '' }).then(function (j) { state.stats = j; });
    if (kind === 'cats' && !state.cats) return loadJson('content/categories.json', {}).then(function (j) { state.cats = j; if (!(j.notices || []).length) j.notices = CATS_DEFAULT.notices.slice(); if (!(j.archive || []).length) j.archive = CATS_DEFAULT.archive.slice(); });
    if (kind === 'site' && !state.site) return loadJson('content/site.json', { hero: {}, banner: { on: false, text: '', link: '', until: '' } }).then(function (j) { state.site = j; state.site.hero = state.site.hero || {}; state.site.banner = state.site.banner || {}; });
    return Promise.resolve();
  }
  function counts() {
    var map = { notices: state.notices && (state.notices.items || []).length, archive: state.archive && (state.archive.items || []).length };
    ['services', 'events', 'press', 'videos'].forEach(function (k) { var f = state.feeds[k]; if (f) map[k] = (f.items || []).length + (k === 'press' && state.feeds.unn ? (state.feeds.unn.items || []).length : 0); });
    qsa('[data-cnt]').forEach(function (e) { var v = map[e.getAttribute('data-cnt')]; e.textContent = v == null ? '' : v; });
  }
  function today() { var d = new Date(); return d.getFullYear() + '.' + String(d.getMonth() + 1).padStart(2, '0') + '.' + String(d.getDate()).padStart(2, '0'); }
  function toIso(s) { var m = String(s || '').match(/(\d{4})\D+(\d{1,2})\D+(\d{1,2})/); return m ? m[1] + '-' + m[2].padStart(2, '0') + '-' + m[3].padStart(2, '0') : ''; }
  function fromIso(s) { var m = String(s || '').match(/(\d{4})-(\d{2})-(\d{2})/); return m ? m[1] + '.' + m[2] + '.' + m[3] : (s || today()); }
  function newId(p) { return p + Date.now().toString(36); }
  function sortNotices(items) { return items.slice().sort(function (a, b) { if (!!a.pinned !== !!b.pinned) return a.pinned ? -1 : 1; return (b.date || '').localeCompare(a.date || ''); }); }
  function fail(e) { toast('저장 실패: ' + e.message, 6000); }
  function head(eyebrow, title, desc, metaHtml) {
    return '<div class="cms-head"><div><p class="eyebrow">' + esc(eyebrow) + '</p><h2>' + esc(title) + '</h2>' + (desc ? '<p>' + esc(desc) + '</p>' : '') + '</div>' + (metaHtml ? '<div class="meta">' + metaHtml + '</div>' : '') + '</div>';
  }

  // ---------------------------------------------------------------- 라우터
  var view = qs('#view');
  var TITLES = { home: '대시보드', site: '홈 화면', notices: '소식·공지', archive: '아카이브', services: '서비스', events: '행사', press: '보도·언론', videos: '영상', history: '게시 기록', settings: '사이트 설정' };
  function route() {
    var h = (location.hash || '#home').slice(1).split('/'); var v = h[0] || 'home';
    if (dirty && !confirm('저장하지 않은 변경이 있습니다. 그래도 이동할까요?')) { return; }
    dirty = false;
    qsa('.cms-nav a').forEach(function (a) { a.classList.toggle('on', a.getAttribute('data-view') === v); });
    qs('#top-title').textContent = TITLES[v] || '대시보드'; qs('#top-actions').innerHTML = '';
    view.innerHTML = '<p class="muted">불러오는 중…</p>';
    var fn = { home: vHome, site: vSite, notices: vNotices, archive: vArchive, services: vServices, events: vEvents, press: vPress, videos: vVideos, history: vHistory, settings: vSettings }[v] || vHome;
    Promise.resolve(fn(h.slice(1))).then(counts).catch(function (e) { view.innerHTML = '<div class="panel"><p>불러오지 못했습니다: ' + esc(e.message) + '</p><p class="small muted">토큰 권한(Contents: Read and write)과 저장소 이름을 확인해 주세요.</p></div>'; });
  }
  window.addEventListener('hashchange', route);

  // ---------------------------------------------------------------- 대시보드
  function vHome() {
    return Promise.all([ensure('notices'), ensure('archive'), ensure('hidden'), liveFeed('services'), liveFeed('events'), liveFeed('press'), liveFeed('unn'), liveFeed('videos')]).then(function (r) {
      var n = state.notices.items || [], a = state.archive.items || [], H = state.hidden; var svc = r[3], ev = r[4], pr = r[5], un = r[6], vd = r[7];
      var hidden = (H.events.length + H.press.length + H.unn.length + H.videos.length + H.services.length);
      view.innerHTML = head('Hallym University / KELI', '대시보드', '사이트에 올라가는 글과 자동 연동 자료를 한눈에 봅니다.', '<strong>' + esc(CFG.site.replace(/^https?:\/\//, '').replace(/\/$/, '')) + '</strong><br>매일 03:17 자동 수집·배포') +
        '<div class="stat-grid">' +
        '<a class="stat" href="#notices"><span class="k">소식·공지</span><span class="num">' + n.length + '</span><p>게시 ' + n.filter(function (x) { return x.published !== false; }).length + ' · 비공개 ' + n.filter(function (x) { return x.published === false; }).length + ' · 고정 ' + n.filter(function (x) { return x.pinned; }).length + '</p></a>' +
        '<a class="stat" href="#archive"><span class="k">아카이브</span><span class="num">' + a.length + '</span><p>사례 ' + a.filter(function (x) { return x.cat === 'case'; }).length + ' · 동향 ' + a.filter(function (x) { return x.cat === 'trend'; }).length + ' · 매뉴얼 ' + a.filter(function (x) { return x.cat === 'manual'; }).length + '</p></a>' +
        '<a class="stat" href="#services"><span class="k">서비스(포털 연동)</span><span class="num">' + (svc.count || (svc.items || []).length) + '</span><p>운영 중 ' + (svc.live_count || 0) + ' · 준비 중 ' + (svc.coming_count || 0) + ' · ' + esc(svc.fetched_at || '') + '</p></a>' +
        '<a class="stat" href="#events"><span class="k">행사(센터 사이트 연동)</span><span class="num">' + (ev.items || []).length + '</span><p>' + esc(ev.fetched_at || '') + ' 수집</p></a>' +
        '<a class="stat" href="#press"><span class="k">보도·언론 연동</span><span class="num">' + ((pr.items || []).length + (un.items || []).length) + '</span><p>한림대 보도자료 ' + (pr.items || []).length + ' · 한국대학신문 ' + (un.items || []).length + '</p></a>' +
        '<a class="stat" href="#videos"><span class="k">영상(유튜브 연동)</span><span class="num">' + (vd.items || []).length + '</span><p>숨긴 자동 연동 글 ' + hidden + '건</p></a>' +
        '</div>' +
        '<div class="panel" style="margin-top:24px"><div class="ph"><div><h3>빠른 작업</h3><p>자주 하는 일입니다.</p></div></div><div style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn sm" href="#notices/new">새 소식 작성</a><a class="btn ghost sm" href="#archive/new">자료 추가</a><a class="btn ghost sm" href="#site">홈 문구·배너 고치기</a><button class="btn ghost sm" type="button" id="h-dispatch">지금 다시 수집·배포</button></div></div>' +
        '<div class="panel"><div class="ph"><div><h3>이 화면이 하는 일</h3></div></div><p style="margin:0 0 8px">여기서 저장하면 GitHub 저장소의 글 파일(content/*.json)이 바뀌고, 1~2분 뒤 사이트가 자동으로 다시 만들어집니다. 글 본문은 편집기로 쓰거나 HTML 소스를 그대로 붙여 넣을 수 있고 길이 제한이 없습니다. 첨부파일과 이미지는 저장소(content/files/)에 올라갑니다.</p><p class="small muted" style="margin:0">서비스·행사·보도자료·영상은 매일 새벽 자동으로 수집되므로 직접 쓰지 않습니다. 필요 없는 글만 각 메뉴에서 숨기면 됩니다.</p></div>';
      qs('#h-dispatch').addEventListener('click', function () { dispatch().then(function () { afterSave('다시 수집·배포를 시작했습니다'); }).catch(function (e) { toast('실행 실패: ' + e.message + ' (토큰에 Actions: Read and write 권한 필요)', 6000); }); });
    });
  }

  // ---------------------------------------------------------------- 홈 화면: 첫 화면 문구 · 배너 · 숫자
  function vSite() {
    return Promise.all([ensure('site'), ensure('stats'), liveFeed('services'), fetch('assets/stats.live.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; })]).then(function (r) {
      var S = state.site, st = state.stats, svc = r[2], live = r[3], hero = S.hero || {}, bn = S.banner || {};
      var D = { eyebrow: 'K-University AI EdTech and Learning Initiative', title: '대학이 함께 만드는<br>AI 기반 고등교육 혁신 생태계.', lead: '한림대가 개발하고 수업에서 검증한 AI 교육 서비스를 <br class="d">국내외 대학·기관에 제공하고 함께 확산합니다.', cta1_label: '서비스 둘러보기', cta1_href: 'services.html', cta2_label: '도입 문의', cta2_href: 'join.html#inquiry' };
      function val(k) { return hero[k] == null || hero[k] === '' ? '' : hero[k]; }
      view.innerHTML = head('Hallym University / KELI', '홈 화면', '첫 화면 문구, 상단 배너, 숫자 카드를 고칩니다. 비워 두면 기본 문구를 씁니다.') +
        '<form id="site-form" class="cms-editor" novalidate>' +
        '<div class="panel"><div class="ph"><div><h3>첫 화면(히어로)</h3><p>줄바꿈은 &lt;br&gt; 로 넣습니다. 비우면 기본값(회색 안내)이 쓰입니다.</p></div></div><div class="form">' +
        '<div class="grid g2" style="gap:16px"><div class="field" style="grid-column:1/-1"><label for="h-eyebrow">작은 제목</label><input id="h-eyebrow" value="' + esc(val('eyebrow')) + '" placeholder="' + esc(D.eyebrow) + '"></div>' +
        '<div class="field" style="grid-column:1/-1"><label for="h-title">큰 제목</label><input id="h-title" value="' + esc(val('title')) + '" placeholder="' + esc(D.title) + '"></div>' +
        '<div class="field" style="grid-column:1/-1"><label for="h-lead">설명</label><textarea id="h-lead" placeholder="' + esc(D.lead) + '">' + esc(val('lead')) + '</textarea></div>' +
        '<div class="field"><label for="h-c1">첫 번째 버튼 글자</label><input id="h-c1" value="' + esc(val('cta1_label')) + '" placeholder="' + esc(D.cta1_label) + '"></div><div class="field"><label for="h-c1h">첫 번째 버튼 링크</label><input id="h-c1h" value="' + esc(val('cta1_href')) + '" placeholder="' + esc(D.cta1_href) + '"></div>' +
        '<div class="field"><label for="h-c2">두 번째 링크 글자</label><input id="h-c2" value="' + esc(val('cta2_label')) + '" placeholder="' + esc(D.cta2_label) + '"></div><div class="field"><label for="h-c2h">두 번째 링크 주소</label><input id="h-c2h" value="' + esc(val('cta2_href')) + '" placeholder="' + esc(D.cta2_href) + '"></div></div></div></div>' +
        '<div class="panel"><div class="ph"><div><h3>상단 배너(공지 띠)</h3><p>행사·모집처럼 잠깐 알릴 일이 있을 때 홈 맨 위에 파란 띠로 보입니다.</p></div></div><div class="form">' +
        '<label class="chk"><input type="checkbox" id="b-on"' + (bn.on ? ' checked' : '') + '><span>배너 켜기</span></label>' +
        '<div class="grid g2" style="gap:16px"><div class="field" style="grid-column:1/-1"><label for="b-text">문구</label><input id="b-text" value="' + esc(bn.text || '') + '" placeholder="2026 KELI 국제 심포지엄 참가 신청을 받습니다"></div>' +
        '<div class="field"><label for="b-link">링크(선택)</label><input id="b-link" value="' + esc(bn.link || '') + '" placeholder="events.html 또는 https://…"></div>' +
        '<div class="field"><label for="b-until">자동으로 내리는 날(선택)</label><input id="b-until" type="date" value="' + esc(toIso(bn.until || '')) + '"><span class="hint">이 날이 지나면 저절로 사라집니다</span></div></div></div></div>' +
        '<div class="panel"><div class="ph"><div><h3>숫자 카드</h3><p>홈의 세 숫자입니다. 서비스 수와 강좌 수는 비우면 한림 AI 교육 포털 값이 자동으로 들어갑니다.</p></div></div><div class="form"><div class="grid g2" style="gap:16px">' +
        '<div class="field"><label for="s-services">AI 교육 서비스 수</label><input id="s-services" type="number" min="0" value="' + (st.services == null ? '' : esc(st.services)) + '" placeholder="비워 두면 포털 값 자동"><span class="hint">현재 포털 값: <strong>' + esc(svc.count != null ? svc.count : '—') + '</strong> (운영 중 ' + esc(svc.live_count != null ? svc.live_count : '—') + ' · 준비 중 ' + esc(svc.coming_count != null ? svc.coming_count : '—') + ', ' + esc(svc.fetched_at || '') + ' 수집)</span></div>' +
        '<div class="field"><label for="s-courses">AI 결합 강좌 수</label><input id="s-courses" type="number" min="0" value="' + (st.courses == null ? '' : esc(st.courses)) + '" placeholder="비워 두면 포털 값 자동"><span class="hint">현재 포털 값: <strong>' + esc(live.courses != null ? Number(live.courses).toLocaleString('ko-KR') : '—') + '</strong> (' + esc(live.fetched_at || '') + ' 수집)</span></div>' +
        '<div class="field"><label for="s-univ">참여 대학 수</label><input id="s-univ" type="number" min="0" value="' + esc(st.universities) + '"></div>' +
        '<div class="field"><label for="s-comp">참여 에듀테크 기업 수</label><input id="s-comp" type="number" min="0" value="' + esc(st.companies) + '"></div>' +
        '<div class="field" style="grid-column:1/-1"><label for="s-basis">기준 설명(홈 각주)</label><input id="s-basis" value="' + esc(st.basis || '') + '"></div></div></div></div>' +
        '</form>';
      qs('#top-actions').innerHTML = '<span id="edit-status" class="small"><span class="saved">● 저장됨</span></span><button class="btn dark sm" type="button" id="site-save">저장하고 게시</button>';
      qsa('input,textarea', view).forEach(function (i) { i.addEventListener('input', function () { setDirty(true); }); });
      qs('#site-save').addEventListener('click', function () {
        var btn = qs('#site-save'); btn.disabled = true; btn.textContent = '저장 중…';
        S.hero = { eyebrow: qs('#h-eyebrow').value.trim(), title: qs('#h-title').value.trim(), lead: qs('#h-lead').value.trim(), cta1_label: qs('#h-c1').value.trim(), cta1_href: qs('#h-c1h').value.trim(), cta2_label: qs('#h-c2').value.trim(), cta2_href: qs('#h-c2h').value.trim() };
        S.banner = { on: qs('#b-on').checked, text: qs('#b-text').value.trim(), link: qs('#b-link').value.trim(), until: qs('#b-until').value };
        function num(id) { var v = qs(id).value.trim(); return v === '' ? null : Number(v); }
        st.services = num('#s-services'); st.universities = num('#s-univ'); st.companies = num('#s-comp'); st.courses = num('#s-courses'); st.basis = qs('#s-basis').value.trim();
        saveJson('content/site.json', S, '홈 화면 문구·배너 수정').then(function () { return saveJson('assets/stats.json', st, '홈 숫자 수정'); }).then(function () { afterSave('홈 화면을 저장했습니다'); }).catch(fail).then(function () { btn.disabled = false; btn.textContent = '저장하고 게시'; });
      });
    });
  }

  // ---------------------------------------------------------------- 공용: 본문 편집기 · 첨부파일 상자
  var ED_BTNS = [['tpl', '서식 ▾'], ['sep'], ['h3', '소제목'], ['bold', '굵게'], ['italic', '기울임'], ['sep'], ['ul', '• 목록'], ['ol', '1. 목록'], ['quote', '인용'], ['sep'], ['link', '링크'], ['img', '이미지'], ['table', '표'], ['sep'], ['clear', '서식 지우기'], ['html', 'HTML']];
  function editorHtml(id) {
    return '<div class="ed-bar" id="' + id + '-bar">' + ED_BTNS.map(function (b) { return b[0] === 'sep' ? '<span class="sep"></span>' : '<button type="button" data-ed="' + b[0] + '">' + b[1] + '</button>'; }).join('') + '</div>' +
      '<div class="ed" id="' + id + '" contenteditable="true"></div><textarea class="ed-src" id="' + id + '-src" hidden spellcheck="false"></textarea><input type="file" id="' + id + '-img" accept="image/*" hidden>';
  }
  function mountEditor(id, initial) {
    var ed = qs('#' + id), src = qs('#' + id + '-src'), htmlMode = false, listeners = [];
    ed.innerHTML = initial || '';
    function clean(html) { return String(html || '').replace(/<img\b([^>]*?)\ssrc="blob:[^"]*"([^>]*?)\sdata-src="([^"]*)"([^>]*)>/g, '<img$1 src="$3"$2$4>').replace(/<img\b([^>]*?)\sdata-src="([^"]*)"([^>]*?)\ssrc="blob:[^"]*"([^>]*)>/g, '<img$1 src="$2"$3$4>'); }
    function body() { return clean(htmlMode ? src.value.trim() : ed.innerHTML.trim()); }
    function fire() { listeners.forEach(function (f) { f(); }); }
    qsa('[data-ed]', qs('#' + id + '-bar')).forEach(function (b) {
      b.addEventListener('mousedown', function (e) { e.preventDefault(); });
      b.addEventListener('click', function () {
        var c = b.getAttribute('data-ed');
        if (c === 'tpl') { pickTemplate(function (html) { if (htmlMode) { src.value = (src.value.trim() ? src.value + '\n' : '') + html; } else { if (ed.innerHTML.trim() && !confirm('지금 쓴 내용 뒤에 서식을 붙입니다. 계속할까요?')) return; ed.innerHTML = (ed.innerHTML.trim() ? ed.innerHTML + '<p></p>' : '') + html; } fire(); toast('서식을 넣었습니다. {{ }} 안의 글을 바꿔 쓰세요'); }); return; }
        if (c === 'html') { htmlMode = !htmlMode; b.classList.toggle('on', htmlMode); if (htmlMode) { src.value = ed.innerHTML; ed.hidden = true; src.hidden = false; src.focus(); } else { ed.innerHTML = src.value; src.hidden = true; ed.hidden = false; ed.focus(); } return; }
        if (htmlMode) { toast('HTML 모드에서는 소스를 직접 고치세요'); return; }
        ed.focus();
        if (c === 'h3') document.execCommand('formatBlock', false, 'h3');
        else if (c === 'bold') document.execCommand('bold');
        else if (c === 'italic') document.execCommand('italic');
        else if (c === 'ul') document.execCommand('insertUnorderedList');
        else if (c === 'ol') document.execCommand('insertOrderedList');
        else if (c === 'quote') document.execCommand('formatBlock', false, 'blockquote');
        else if (c === 'clear') { document.execCommand('removeFormat'); document.execCommand('formatBlock', false, 'p'); }
        else if (c === 'table') document.execCommand('insertHTML', false, '<table><thead><tr><th>항목</th><th>내용</th></tr></thead><tbody><tr><td>&nbsp;</td><td>&nbsp;</td></tr><tr><td>&nbsp;</td><td>&nbsp;</td></tr></tbody></table><p></p>');
        else if (c === 'link') { var sel = String(window.getSelection && window.getSelection()); var b2 = modal('<h3 style="margin:0 0 12px;font-size:20px">링크</h3><div class="field"><label>주소</label><input id="lk-url" placeholder="https://…"></div><div class="field" style="margin-top:10px"><label>글자</label><input id="lk-txt" value="' + esc(sel) + '"></div><div style="display:flex;gap:8px;justify-content:flex-end;margin-top:16px"><button class="btn ghost" type="button" id="lk-x">취소</button><button class="btn" type="button" id="lk-ok">넣기</button></div>'); var range = window.getSelection().rangeCount ? window.getSelection().getRangeAt(0) : null; qs('#lk-x', b2).addEventListener('click', closeModal); qs('#lk-ok', b2).addEventListener('click', function () { var u = qs('#lk-url', b2).value.trim(), t = qs('#lk-txt', b2).value.trim() || u; closeModal(); if (!u) return; ed.focus(); if (range) { window.getSelection().removeAllRanges(); window.getSelection().addRange(range); } document.execCommand('insertHTML', false, '<a href="' + esc(u) + '"' + (/^https?:/.test(u) ? ' target="_blank" rel="noopener"' : '') + '>' + esc(t) + '</a>'); fire(); }); }
        else if (c === 'img') { qs('#' + id + '-img').click(); }
        fire();
      });
    });
    qs('#' + id + '-img').addEventListener('change', function () { var f = this.files[0]; if (!f) return; var inp = this; var range = window.getSelection().rangeCount ? window.getSelection().getRangeAt(0) : null; toast('이미지 올리는 중…'); uploadFile(f).then(function (r) { ed.focus(); if (range) { window.getSelection().removeAllRanges(); window.getSelection().addRange(range); } var local = ''; try { local = URL.createObjectURL(f); } catch (e3) {} document.execCommand('insertHTML', false, '<figure class="art-fig"><img src="' + esc(local || r.url) + '"' + (local ? ' data-src="' + esc(r.url) + '"' : '') + ' alt="' + esc(f.name.replace(/\.[^.]+$/, '')) + '"><figcaption></figcaption></figure><p></p>'); toast('이미지를 넣었습니다. 사이트에는 게시 후 1~2분 뒤 보입니다'); fire(); }).catch(function (e) { toast('이미지 실패: ' + e.message, 6000); }).then(function () { inp.value = ''; }); });
    ed.addEventListener('input', fire); src.addEventListener('input', fire);
    return { body: body, onInput: function (f) { listeners.push(f); } };
  }
  function pickTemplate(onPick) {
    var T = window.KELI_TEMPLATES || []; var groups = []; T.forEach(function (t) { if (groups.indexOf(t.group) < 0) groups.push(t.group); });
    var bx = modal('<h3 style="margin:0 0 4px;font-size:20px">글 서식 넣기</h3><p class="small muted" style="margin:0 0 14px">KELI 디자인에 맞춘 서식입니다. 넣은 뒤 {{ }} 안의 글만 바꿔 쓰면 됩니다. 제목·날짜·분류는 글 머리글에 자동으로 붙으므로 본문에 다시 쓰지 않습니다.</p>' +
      groups.map(function (g) { return '<p class="small" style="margin:14px 0 6px;font-weight:700;color:var(--muted)">' + esc(g) + '</p><div class="hist">' + T.filter(function (t) { return t.group === g; }).map(function (t) { return '<div class="h"><div><div><strong>' + esc(t.name) + '</strong></div><div class="m">' + esc(t.desc) + '</div></div><button class="btn sm" type="button" data-tpl="' + esc(t.id) + '">넣기</button></div>'; }).join('') + '</div>'; }).join('') +
      '<div style="display:flex;justify-content:flex-end;margin-top:16px"><button class="btn ghost" type="button" id="tpl-x">닫기</button></div>', true);
    qs('#tpl-x', bx).addEventListener('click', closeModal);
    qsa('[data-tpl]', bx).forEach(function (b) { b.addEventListener('click', function () { var t = T.filter(function (x) { return x.id === b.getAttribute('data-tpl'); })[0]; closeModal(); if (t) onPick(t.html); }); });
  }
  function filesHtml(id, hint) { return '<div class="files-box" id="' + id + '"></div><div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:8px"><input type="file" id="' + id + '-in" multiple><span class="small muted">' + (hint || 'PDF·HWP·이미지 등 여러 개 가능. 올리는 즉시 저장소에 들어갑니다' + (SERVER && SERVER_FILES ? '(용량 제한 없음)' : '(파일당 100MB까지)')) + '</span></div>'; }
  function mountFiles(id, files, onChange) {
    files = files || [];
    function render() { qs('#' + id).innerHTML = files.length ? files.map(function (f, i) { return '<div class="f"><span>' + esc(f.name) + (f.size ? ' <span class="muted">(' + esc(f.size) + ')</span>' : '') + '</span><button class="btn ghost xs" type="button" data-rm="' + i + '">빼기</button></div>'; }).join('') : '<span class="small muted">첨부 없음</span>'; qsa('[data-rm]', qs('#' + id)).forEach(function (b) { b.addEventListener('click', function () { files.splice(Number(b.getAttribute('data-rm')), 1); render(); if (onChange) onChange(files); }); }); }
    render();
    qs('#' + id + '-in').addEventListener('change', function () {
      var list = Array.prototype.slice.call(this.files); if (!list.length) return; var inp = this; inp.disabled = true; toast('올리는 중… ' + list.length + '개');
      list.reduce(function (p, f) { return p.then(function () { return uploadFile(f).then(function (r) { files.push(r); render(); if (onChange) onChange(files, f); }); }); }, Promise.resolve()).then(function () { toast('첨부 ' + list.length + '개를 올렸습니다'); }).catch(function (e) { toast('첨부 실패: ' + e.message, 6000); }).then(function () { inp.disabled = false; inp.value = ''; });
    });
    return { files: files, render: render };
  }
  function listPanel(opt) {   // 왼쪽 목록 카드: {title, count, addHref, addLabel, chips:[[key,label]], items:[{id,href,on,off,cat,status,title,date}]}
    var chips = opt.chips ? '<div class="chips">' + opt.chips.map(function (c, i) { return '<button type="button" data-chip="' + esc(c[0]) + '"' + (i === 0 ? ' class="on"' : '') + '>' + esc(c[1]) + '</button>'; }).join('') + '</div>' : '';
    return '<div class="panel cms-list"><div class="lh"><strong>' + esc(opt.title) + '<span class="n">' + opt.count + '</span></strong><a class="btn ghost xs" href="' + esc(opt.addHref) + '">＋</a></div>' +
      '<div class="search"><input type="search" placeholder="' + esc(opt.searchPh || '검색') + '" data-search></div>' + chips +
      '<div class="items" data-items>' + (opt.items.length ? opt.items.map(function (it) { return '<a class="cms-item' + (it.on ? ' on' : '') + (it.off ? ' off' : '') + '" href="' + esc(it.href) + '" data-text="' + esc((it.title + ' ' + (it.cat || '') + ' ' + (it.date || '')).toLowerCase()) + '" data-chip-val="' + esc(it.chip || '') + '"><span class="row1"><span>' + esc(it.cat || '') + '</span><span class="st ' + (it.off ? 'off' : 'pub') + '">' + (it.off ? '비공개' : (it.pinned ? '고정 · 표시' : '표시')) + '</span></span><span class="t">' + esc(it.title) + '</span><span class="d">' + esc(it.date || '') + (it.extra ? ' · ' + esc(it.extra) : '') + '</span></a>'; }).join('') : '<p class="small muted" style="padding:20px">아직 없습니다.</p>') + '</div>' +
      '<a class="add" href="' + esc(opt.addHref) + '">＋ ' + esc(opt.addLabel) + '</a></div>';
  }
  function wireList() {
    var box = qs('.cms-list', view); if (!box) return;
    var s = qs('[data-search]', box), chip = 'all';
    function apply() { var q = (s.value || '').trim().toLowerCase(); qsa('.cms-item', box).forEach(function (a) { var ok = (!q || a.getAttribute('data-text').indexOf(q) > -1) && (chip === 'all' || a.getAttribute('data-chip-val') === chip); a.style.display = ok ? '' : 'none'; }); }
    s.addEventListener('input', apply);
    qsa('[data-chip]', box).forEach(function (b) { b.addEventListener('click', function () { chip = b.getAttribute('data-chip'); qsa('[data-chip]', box).forEach(function (x) { x.classList.toggle('on', x === b); }); apply(); }); });
    var on = qs('.cms-item.on', box); if (on && on.scrollIntoView) { try { on.scrollIntoView({ block: 'nearest' }); } catch (e) {} }
  }

  // ---------------------------------------------------------------- 게시판 분류(content/categories.json): 각 게시판의 "분류 관리"에서 고친다
  var CATS_DEFAULT = { notices: [{ key: 'general', label: '일반' }, { key: 'recruit', label: '모집' }, { key: 'press', label: '보도' }, { key: 'event', label: '행사 안내' }],
    archive: [{ key: 'manual', label: '매뉴얼·소개자료', lead: '' }, { key: 'trend', label: '기술 동향·연구', lead: '' }, { key: 'case', label: '실증 사례집', lead: '' }] };
  function cats(board) { return (state.cats && state.cats[board] && state.cats[board].length) ? state.cats[board] : CATS_DEFAULT[board]; }
  function keyOf(label) { return String(label || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || ('c' + Date.now().toString(36)); }
  function manageCats(board, used, onDone) {   // used: {key: 글 수} — 글이 있는 분류는 지울 수 없음
    var list = cats(board).map(function (c) { return { key: c.key, label: c.label, lead: c.lead || '' }; }); var isArch = board === 'archive';
    function render() {
      var bx = qs('#modal-box');
      bx.innerHTML = '<h3 style="margin:0 0 4px;font-size:20px">' + (isArch ? '아카이브' : '소식·공지') + ' 분류 관리</h3><p class="small muted" style="margin:0 0 14px">이름을 고치면 사이트의 탭·메뉴·페이지 이름이 함께 바뀝니다. 글이 있는 분류는 지울 수 없습니다(먼저 글의 분류를 옮기세요).</p>' +
        '<div class="hist">' + list.map(function (c, i) { var n = used[c.key] || used[c.label] || 0; return '<div class="h" style="grid-template-columns:1fr auto"><div><input data-cl="' + i + '" value="' + esc(c.label) + '" style="width:100%;border:1px solid var(--line);border-radius:8px;padding:7px 10px;font-size:14px" placeholder="분류 이름">' + (isArch ? '<input data-cd="' + i + '" value="' + esc(c.lead) + '" style="width:100%;margin-top:6px;border:1px solid var(--line);border-radius:8px;padding:6px 10px;font-size:13px" placeholder="분류 페이지 머리말(선택)">' : '') + '<div class="m">주소·탭 키: ' + esc(c.key) + ' · 글 ' + n + '건</div></div><span style="display:flex;gap:4px"><button class="btn ghost xs" type="button" data-up="' + i + '"' + (i === 0 ? ' disabled' : '') + '>↑</button><button class="btn ghost xs" type="button" data-dn="' + i + '"' + (i === list.length - 1 ? ' disabled' : '') + '>↓</button><button class="btn ghost xs danger" type="button" data-del="' + i + '"' + (n ? ' disabled title="글이 있는 분류"' : '') + '>삭제</button></span></div>'; }).join('') + '</div>' +
        '<div style="display:flex;gap:8px;margin-top:12px"><input id="cat-new" placeholder="새 분류 이름" style="flex:1;border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:14px"><button class="btn ghost sm" type="button" id="cat-add">추가</button></div>' +
        '<div style="display:flex;gap:8px;justify-content:flex-end;margin-top:18px"><button class="btn ghost" type="button" id="cat-x">취소</button><button class="btn" type="button" id="cat-ok">저장하고 게시</button></div>';
      function sync() { qsa('[data-cl]', bx).forEach(function (i) { list[Number(i.getAttribute('data-cl'))].label = i.value.trim(); }); qsa('[data-cd]', bx).forEach(function (i) { list[Number(i.getAttribute('data-cd'))].lead = i.value.trim(); }); }
      qsa('[data-up]', bx).forEach(function (b) { b.addEventListener('click', function () { sync(); var i = Number(b.getAttribute('data-up')); var t = list[i - 1]; list[i - 1] = list[i]; list[i] = t; render(); }); });
      qsa('[data-dn]', bx).forEach(function (b) { b.addEventListener('click', function () { sync(); var i = Number(b.getAttribute('data-dn')); var t = list[i + 1]; list[i + 1] = list[i]; list[i] = t; render(); }); });
      qsa('[data-del]', bx).forEach(function (b) { b.addEventListener('click', function () { sync(); list.splice(Number(b.getAttribute('data-del')), 1); render(); }); });
      qs('#cat-add', bx).addEventListener('click', function () { sync(); var v = qs('#cat-new', bx).value.trim(); if (!v) return; var k = keyOf(v); while (list.some(function (c) { return c.key === k; })) k += '2'; list.push({ key: k, label: v, lead: '' }); render(); });
      qs('#cat-x', bx).addEventListener('click', closeModal);
      qs('#cat-ok', bx).addEventListener('click', function () {
        sync(); if (list.some(function (c) { return !c.label; })) { toast('이름이 빈 분류가 있습니다'); return; } if (!list.length) { toast('분류는 하나 이상 있어야 합니다'); return; }
        var old = cats(board); var renamed = {}; old.forEach(function (o) { var n = list.filter(function (c) { return c.key === o.key; })[0]; if (n && n.label !== o.label) renamed[o.label] = n.label; });
        var b2 = qs('#cat-ok', bx); b2.disabled = true;
        ensure('cats').then(function () { state.cats[board] = list.map(function (c) { return isArch ? { key: c.key, label: c.label, lead: c.lead } : { key: c.key, label: c.label }; }); return saveJson('content/categories.json', state.cats, (isArch ? '아카이브' : '소식') + ' 분류 수정'); })
          .then(function () {   // 소식 글은 분류를 이름으로 갖고 있어 이름이 바뀌면 글도 같이 고친다
            if (!isArch && Object.keys(renamed).length && state.notices) { var ch = 0; (state.notices.items || []).forEach(function (n) { if (renamed[n.cat]) { n.cat = renamed[n.cat]; ch++; } }); if (ch) return saveJson('content/notices.json', state.notices, '분류 이름 변경에 따라 공지 ' + ch + '건 갱신'); }
          }).then(function () { closeModal(); afterSave('분류를 저장했습니다'); if (onDone) onDone(); }).catch(function (e) { fail(e); b2.disabled = false; });
      });
    }
    modal('<p class="muted">불러오는 중…</p>'); render();
  }

  // ---------------------------------------------------------------- 소식·공지: 목록 + 편집 2단
  var CATS = ['일반', '모집', '보도', '행사 안내'];
  function vNotices(args) {
    return Promise.all([ensure('notices'), ensure('cats')]).then(function () {
      CATS = cats('notices').map(function (c) { return c.label; });
      var items = sortNotices(state.notices.items || []); var cur = null, isNew = false;
      if (args[0] === 'new') isNew = true;
      else if (args[0]) cur = items.filter(function (x) { return x.id === args[0]; })[0];
      if (!cur && !isNew && items.length) { location.replace('#notices/' + items[0].id); return; }
      var list = listPanel({ title: '전체 소식', count: items.length, addHref: '#notices/new', addLabel: '새 소식 작성', searchPh: '소식 검색', chips: [['all', '전체']].concat(CATS.map(function (c) { return [c, c]; })),
        items: items.map(function (n) { return { id: n.id, href: '#notices/' + n.id, on: cur && cur.id === n.id, off: n.published === false, pinned: n.pinned, cat: n.cat, chip: n.cat, title: n.title, date: n.date, extra: n.files && n.files.length ? '첨부 ' + n.files.length : '' }; }) });
      view.innerHTML = head('Hallym University / Website CMS', '소식·공지', '새로운 소식을 작성하고 홈페이지에 보여줄 항목을 선택합니다.', '<button class="btn ghost xs" type="button" id="cats-manage">분류 관리</button><br><span>마지막 저장 <strong>' + esc(items[0] && items[0].updated ? items[0].updated : '—') + '</strong></span>') +
        '<div class="cms-split">' + list + '<div class="panel cms-editor" id="editor"></div></div>';
      wireList();
      qs('#cats-manage').addEventListener('click', function () { var used = {}; items.forEach(function (n) { used[n.cat] = (used[n.cat] || 0) + 1; }); manageCats('notices', used, route); });
      if (isNew || cur) editNotice(cur); else qs('#editor').innerHTML = '<div class="empty">아직 소식이 없습니다. "새 소식 작성"을 눌러 첫 글을 올려 보세요.</div>';
    });
  }
  function editNotice(it) {
    var isNew = !it; it = it || { id: newId('n'), cat: CATS[0] || '일반', title: '', date: today(), summary: '', body: '', link: '', pinned: false, published: true, files: [] };
    var box = qs('#editor'); var draftKey = 'keli_draft_' + it.id; var draft = null; try { draft = JSON.parse(localStorage.getItem(draftKey) || 'null'); } catch (e) {}
    box.innerHTML = '<div class="ph"><div><h3>' + (isNew ? '새 소식' : '소식 편집') + '</h3><p>작성 내용은 저장 후 게시해야 홈페이지에 반영됩니다.</p></div>' + (isNew ? '' : '<button class="danger-link" type="button" id="n-del">🗑 삭제</button>') + '</div>' +
      '<form class="form" id="nf" novalidate>' +
      '<div class="field"><label for="n-title">제목<span class="req">*</span></label><input id="n-title" required value="' + esc(it.title) + '"><span class="msg" id="n-title-msg" style="display:none">제목을 입력해 주세요</span></div>' +
      '<div class="grid g2" style="gap:16px"><div class="field"><label for="n-cat">분류<span class="req">*</span></label><select id="n-cat">' + CATS.concat(CATS.indexOf(it.cat) < 0 && it.cat ? [it.cat] : []).map(function (c) { return '<option' + (c === it.cat ? ' selected' : '') + '>' + esc(c) + '</option>'; }).join('') + '</select></div>' +
      '<div class="field"><label for="n-date">게시일<span class="req">*</span></label><input id="n-date" type="date" value="' + esc(toIso(it.date) || toIso(today())) + '"></div></div>' +
      '<div class="field"><label for="n-summary">요약 <span class="muted" style="font-weight:400">— 목록과 글 머리글에 한 줄로 보입니다(선택)</span></label><textarea id="n-summary" placeholder="한림대학교 KELI 사무국이 …를 소개했습니다.">' + esc(it.summary || '') + '</textarea></div>' +
      '<div class="field"><label>본문 <span class="muted" style="font-weight:400">— 편집기로 쓰거나 "HTML"을 눌러 소스를 붙여 넣으세요. 길이 제한 없음</span></label>' + editorHtml('ed') + '</div>' +
      '<div class="field"><label for="n-link">관련 링크(선택)</label><input id="n-link" value="' + esc(it.link || '') + '" placeholder="events.html 또는 https://…"></div>' +
      '<div class="field"><label>첨부파일</label>' + filesHtml('files') + '</div>' +
      '<div class="status-row"><label class="chk"><input type="checkbox" id="n-pin"' + (it.pinned ? ' checked' : '') + '><span>상단 고정</span></label><label class="chk"><input type="checkbox" id="n-pub"' + (it.published !== false ? ' checked' : '') + '><span>홈페이지에 표시(끄면 비공개로 저장)</span></label></div>' +
      '</form>';
    qs('#top-actions').innerHTML = '<span id="edit-status" class="small"><span class="saved">● ' + (isNew ? '새 글' : '저장됨') + '</span></span><button class="btn ghost sm" type="button" id="n-preview">미리보기</button><button class="btn ghost sm" type="button" id="n-draft">비공개로 저장</button><button class="btn dark sm" type="button" id="n-save">게시하기</button>';
    var initial = it.body || '';
    if (draft && draft.body && draft.body !== it.body) { toast('저장하지 않은 임시 글이 있어 불러왔습니다', 4000); initial = draft.body; if (draft.title) qs('#n-title').value = draft.title; setDirty(true); }
    var editor = mountEditor('ed', initial), fb = mountFiles('files', it.files ? it.files.slice() : [], function () { setDirty(true); }), files = fb.files;
    var draftT = null; function saveDraft() { setDirty(true); clearTimeout(draftT); draftT = setTimeout(function () { try { localStorage.setItem(draftKey, JSON.stringify({ title: qs('#n-title').value, body: editor.body() })); } catch (e) {} }, 600); }
    editor.onInput(saveDraft); qsa('input,select,textarea', box).forEach(function (i) { i.addEventListener('input', function () { setDirty(true); }); });
    qs('#n-title').addEventListener('input', saveDraft);
    qs('#n-preview').addEventListener('click', function () { var fl = files.length ? '<div class="art-files"><strong>첨부파일</strong><ul>' + files.map(function (f) { return '<li>' + esc(f.name) + '</li>'; }).join('') + '</ul></div>' : ''; var sm = qs('#n-summary').value.trim(); modal('<span class="eyebrow">공지사항 · ' + esc(qs('#n-cat').value) + '</span><h2 style="margin:4px 0 4px;font-size:30px">' + esc(qs('#n-title').value || '(제목 없음)') + '</h2>' + (sm ? '<p class="lead" style="text-align:left">' + esc(sm) + '</p>' : '') + '<p class="muted">' + esc(fromIso(qs('#n-date').value)) + ' · KELI 사무국</p><article class="art">' + (editor.body() || '<p class="muted">(본문 없음)</p>') + '</article>' + fl + '<div style="display:flex;justify-content:flex-end;margin-top:16px"><button class="btn ghost" type="button" id="pv-x">닫기</button></div>', true); qs('#pv-x').addEventListener('click', closeModal); });
    function save(publish) {
      var t = qs('#n-title').value.trim(); var msg = qs('#n-title-msg'); if (!t) { msg.style.display = 'block'; qs('#n-title').focus(); return; } msg.style.display = 'none';
      var btn = qs('#n-save'); btn.disabled = true; btn.textContent = '저장 중…';
      it.title = t; it.cat = qs('#n-cat').value; it.date = fromIso(qs('#n-date').value); it.summary = qs('#n-summary').value.trim(); it.link = qs('#n-link').value.trim(); it.body = editor.body(); it.pinned = qs('#n-pin').checked; it.published = publish == null ? qs('#n-pub').checked : publish; it.files = files; it.updated = new Date().toLocaleString('ko-KR', { hour12: false });
      if (isNew) state.notices.items = [it].concat(state.notices.items || []);
      saveJson('content/notices.json', state.notices, (isNew ? '공지 등록: ' : '공지 수정: ') + t + (it.published ? '' : ' (비공개)')).then(function () { try { localStorage.removeItem(draftKey); } catch (e2) {} afterSave(it.published ? '게시했습니다' : '비공개로 저장했습니다'); isNew = false; location.hash = '#notices/' + it.id; route(); }).catch(function (e2) { fail(e2); btn.disabled = false; btn.textContent = '게시하기'; });
    }
    qs('#n-save').addEventListener('click', function () { save(true); });
    qs('#n-draft').addEventListener('click', function () { save(false); });
    qs('#nf').addEventListener('submit', function (e) { e.preventDefault(); save(null); });
    if (!isNew) qs('#n-del').addEventListener('click', function () { confirmBox('이 소식을 삭제할까요?', '"' + it.title + '" 글이 사이트에서 사라집니다. 되돌리려면 게시 기록에서 복구해야 합니다.', '삭제', true).then(function (ok) { if (!ok) return; state.notices.items = state.notices.items.filter(function (x) { return x.id !== it.id; }); saveJson('content/notices.json', state.notices, '공지 삭제: ' + it.title).then(function () { afterSave('삭제했습니다'); location.hash = '#notices'; route(); }).catch(fail); }); });
  }

  // ---------------------------------------------------------------- 아카이브: 목록 + 편집 2단 (외부 주소 / 파일 / 설명 글)
  var ACATS = [['manual', '매뉴얼·소개자료'], ['trend', '기술 동향·연구'], ['case', '실증 사례집']], ATYPES = [['pdf', 'PDF'], ['doc', '문서'], ['link', '링크'], ['video', '영상'], ['image', '이미지']];
  function lbl(list, k) { var m = list.filter(function (x) { return x[0] === k; })[0]; return m ? m[1] : k; }
  function typeOf(name) { return /\.pdf$/i.test(name) ? 'pdf' : /\.(png|jpe?g|gif|webp)$/i.test(name) ? 'image' : /\.(mp4|mov|webm)$/i.test(name) ? 'video' : 'doc'; }
  function archiveOpen(a) { var fs = a.files || []; if (a.body || fs.length > 1 || (fs.length && a.url)) return CFG.site + 'archive-' + a.id + '.html'; return a.url || (fs[0] && fs[0].url) || (CFG.site + 'archive.html'); }
  function vArchive(args) {
    return Promise.all([ensure('archive'), ensure('cats')]).then(function () {
      ACATS = cats('archive').map(function (c) { return [c.key, c.label]; });
      var items = state.archive.items || []; var cur = null, isNew = false;
      if (args[0] === 'new') isNew = true; else if (args[0]) cur = items.filter(function (x) { return x.id === args[0]; })[0];
      if (!cur && !isNew && items.length) { location.replace('#archive/' + items[0].id); return; }
      var list = listPanel({ title: '전체 자료', count: items.length, addHref: '#archive/new', addLabel: '자료 추가', searchPh: '자료 검색', chips: [['all', '전체']].concat(ACATS),
        items: items.map(function (a) { return { id: a.id, href: '#archive/' + a.id, on: cur && cur.id === a.id, off: a.published === false, cat: lbl(ACATS, a.cat) + ' · ' + lbl(ATYPES, a.type), chip: a.cat, title: a.title, date: a.date, extra: (a.org || '') + ((a.files || []).length ? ' · 첨부 ' + a.files.length : '') }; }) });
      view.innerHTML = head('Hallym University / Website CMS', '아카이브', '자료를 올립니다. 다른 사이트 주소를 가져오거나, 파일을 직접 올리거나, 설명 글과 함께 올리면 자료 페이지가 생깁니다.', '<button class="btn ghost xs" type="button" id="cats-manage">분류 관리</button>') +
        '<div class="cms-split">' + list + '<div class="panel cms-editor" id="editor"></div></div>';
      wireList();
      qs('#cats-manage').addEventListener('click', function () { var used = {}; items.forEach(function (a) { used[a.cat] = (used[a.cat] || 0) + 1; }); manageCats('archive', used, route); });
      if (isNew || cur) editArchive(cur); else qs('#editor').innerHTML = '<div class="empty">아직 자료가 없습니다.</div>';
    });
  }
  function editArchive(it) {
    var isNew = !it; it = it || { id: newId('a'), cat: (ACATS[0] || ['case'])[0], type: 'pdf', title: '', org: 'KELI 사무국', date: today(), url: '', body: '', files: [], published: true };
    var box = qs('#editor');
    box.innerHTML = '<div class="ph"><div><h3>' + (isNew ? '자료 추가' : '자료 편집') + '</h3><p>외부 주소, 파일, 설명 가운데 하나는 있어야 합니다.</p></div>' + (isNew ? '' : '<span style="display:flex;gap:12px;align-items:center"><a class="btn ghost xs" href="' + esc(archiveOpen(it)) + '" target="_blank" rel="noopener">열기</a><button class="danger-link" type="button" id="a-del">🗑 삭제</button></span>') + '</div>' +
      '<form class="form" id="af" novalidate>' +
      '<div class="field"><label for="a-title">제목<span class="req">*</span></label><input id="a-title" value="' + esc(it.title) + '"><span class="msg" id="a-title-msg" style="display:none">제목을 입력해 주세요</span></div>' +
      '<div class="grid g2" style="gap:16px">' +
      '<div class="field"><label for="a-cat">분류<span class="req">*</span></label><select id="a-cat">' + ACATS.map(function (c) { return '<option value="' + c[0] + '"' + (c[0] === it.cat ? ' selected' : '') + '>' + c[1] + '</option>'; }).join('') + '</select></div>' +
      '<div class="field"><label for="a-type">유형</label><select id="a-type">' + ATYPES.map(function (c) { return '<option value="' + c[0] + '"' + (c[0] === it.type ? ' selected' : '') + '>' + c[1] + '</option>'; }).join('') + '</select><span class="hint">파일을 올리면 자동으로 맞춰집니다</span></div>' +
      '<div class="field"><label for="a-org">기관·저자</label><input id="a-org" value="' + esc(it.org || '') + '"></div>' +
      '<div class="field"><label for="a-date">날짜</label><input id="a-date" value="' + esc(it.date || '') + '" placeholder="2026.11"></div></div>' +
      '<div class="field"><label for="a-url">방법 1 · 다른 사이트의 주소 가져오기(선택)</label><input id="a-url" value="' + esc(it.url || '') + '" placeholder="https://… (한림 AI 교육 포털, 구글 드라이브, 유튜브 등)"><span class="hint">주소만 넣으면 목록에서 그 주소가 새 창으로 열립니다</span></div>' +
      '<div class="field"><label>방법 2 · 파일 직접 올리기(선택, 여러 개 가능)</label>' + filesHtml('a-files', 'PDF·HWP·PPT·이미지·영상 등. 파일이 하나면 목록에서 바로 열리고, 여러 개면 자료 페이지가 생깁니다' + (SERVER && SERVER_FILES ? '(용량 제한 없음)' : '(파일당 100MB까지)')) + '</div>' +
      '<div class="field"><label>방법 3 · 설명 글(선택)</label>' + editorHtml('a-ed') + '<span class="hint">설명을 쓰면 자료 페이지(제목 · 설명 · 첨부 · 외부 주소)가 만들어집니다</span></div>' +
      '<span class="msg" id="a-need-msg" style="display:none">외부 주소, 파일, 설명 가운데 하나는 있어야 합니다</span>' +
      '<div class="status-row"><label class="chk"><input type="checkbox" id="a-pub"' + (it.published !== false ? ' checked' : '') + '><span>홈페이지에 표시(끄면 비공개로 저장)</span></label></div></form>';
    qs('#top-actions').innerHTML = '<span id="edit-status" class="small"><span class="saved">● ' + (isNew ? '새 자료' : '저장됨') + '</span></span><button class="btn ghost sm" type="button" id="a-draft">비공개로 저장</button><button class="btn dark sm" type="button" id="a-save">게시하기</button>';
    var editor = mountEditor('a-ed', it.body || ''); editor.onInput(function () { setDirty(true); });
    var fb = mountFiles('a-files', it.files ? it.files.slice() : [], function (files, added) { setDirty(true); if (added && files.length === 1) qs('#a-type').value = typeOf(added.name); }), files = fb.files;
    qsa('input,select,textarea', box).forEach(function (i) { i.addEventListener('input', function () { setDirty(true); }); });
    qs('#a-url').addEventListener('change', function () { var u = this.value.trim(); if (!u) return; if (/youtu\.?be|vimeo|\/video/i.test(u)) qs('#a-type').value = 'video'; else if (/\.pdf(\?|$)/i.test(u)) qs('#a-type').value = 'pdf'; else if (!files.length) qs('#a-type').value = 'link'; });
    function save(publish) {
      var t = qs('#a-title').value.trim(), u = qs('#a-url').value.trim(), body = editor.body();
      qs('#a-title-msg').style.display = t ? 'none' : 'block'; var need = !u && !files.length && !body; qs('#a-need-msg').style.display = need ? 'block' : 'none'; if (!t || need) return;
      var btn = qs('#a-save'); btn.disabled = true; btn.textContent = '저장 중…';
      it.title = t; it.cat = qs('#a-cat').value; it.type = qs('#a-type').value; it.org = qs('#a-org').value.trim(); it.date = qs('#a-date').value.trim(); it.url = u; it.body = body; it.files = files; it.published = publish == null ? qs('#a-pub').checked : publish;
      if (isNew) state.archive.items = (state.archive.items || []).concat([it]);
      saveJson('content/archive.json', state.archive, (isNew ? '아카이브 추가: ' : '아카이브 수정: ') + t).then(function () { afterSave(it.published ? '게시했습니다' : '비공개로 저장했습니다'); isNew = false; location.hash = '#archive/' + it.id; route(); }).catch(function (e2) { fail(e2); btn.disabled = false; btn.textContent = '게시하기'; });
    }
    qs('#a-save').addEventListener('click', function () { save(true); }); qs('#a-draft').addEventListener('click', function () { save(false); });
    qs('#af').addEventListener('submit', function (e) { e.preventDefault(); save(null); });
    if (!isNew) qs('#a-del').addEventListener('click', function () { confirmBox('이 자료를 삭제할까요?', '"' + it.title + '" 이(가) 아카이브에서 사라집니다.', '삭제', true).then(function (ok) { if (!ok) return; state.archive.items = (state.archive.items || []).filter(function (x) { return x.id !== it.id; }); saveJson('content/archive.json', state.archive, '아카이브 삭제: ' + it.title).then(function () { afterSave('삭제했습니다'); location.hash = '#archive'; route(); }).catch(fail); }); });
  }

  // ---------------------------------------------------------------- 자동 연동(서비스 · 행사 · 보도·언론 · 영상): 보기/숨기기
  function feedView(opt) {   // {eyebrow,title,desc,sections:[{key,label,note,feed,thumb:fn,meta:fn}]}
    return ensure('hidden').then(function () { return Promise.all(opt.sections.map(function (sc) { return liveFeed(sc.feed); })); }).then(function (feeds) {
      var H = state.hidden;
      view.innerHTML = head('Hallym University / Website CMS', opt.title, opt.desc, '<span>자동 수집</span><br><strong>' + esc(feeds[0].fetched_at || '—') + '</strong>') +
        opt.sections.map(function (sc, i) {
          var items = feeds[i].items || [];
          return '<div class="panel"><div class="ph"><div><h3>' + esc(sc.label) + ' <span class="muted" style="font-weight:500;font-size:14px">' + items.length + '건</span></h3><p>' + sc.note + '</p></div><span class="small muted">' + esc(feeds[i].fetched_at || '') + ' 수집</span></div>' +
            '<div class="search" style="margin-bottom:8px"><input type="search" placeholder="검색" data-fsearch="' + i + '" style="width:100%;max-width:360px;border:1px solid var(--line);border-radius:10px;padding:9px 12px;font-size:14px"></div>' +
            (items.length ? '<div data-flist="' + i + '">' + items.map(function (it) { var id = String(it.id), off = H[sc.key].indexOf(id) > -1; var th = sc.thumb ? sc.thumb(it) : ''; return '<div class="feed-row' + (off ? ' off' : '') + '" data-text="' + esc(String(it.title || it.name || '').toLowerCase()) + '">' + (th ? '<img class="th" src="' + esc(th) + '" alt="" loading="lazy">' : '<span class="th ph">—</span>') + '<div><div class="t">' + esc(it.title || it.name) + '</div><div class="m">' + esc(sc.meta ? sc.meta(it) : (it.when || it.date || it.published || '')) + (off ? ' · 숨김' : '') + '</div></div><span class="acts">' + (it.url ? '<a class="btn ghost xs" href="' + esc(it.url) + '" target="_blank" rel="noopener">원문</a>' : '') + '<button class="btn ' + (off ? '' : 'ghost ') + 'xs" type="button" data-k="' + sc.key + '" data-id="' + esc(id) + '">' + (off ? '보이기' : '숨기기') + '</button></span></div>'; }).join('') + '</div>' : '<p class="small muted">수집된 글이 없습니다</p>') + '</div>';
        }).join('');
      qs('#top-actions').innerHTML = '<button class="btn ghost sm" type="button" id="f-dispatch">지금 다시 수집</button>';
      qsa('[data-fsearch]', view).forEach(function (s) { s.addEventListener('input', function () { var q = s.value.trim().toLowerCase(); qsa('[data-flist="' + s.getAttribute('data-fsearch') + '"] .feed-row', view).forEach(function (r) { r.style.display = !q || r.getAttribute('data-text').indexOf(q) > -1 ? '' : 'none'; }); }); });
      qsa('[data-k]', view).forEach(function (b) { b.addEventListener('click', function () { var k = b.getAttribute('data-k'), id = b.getAttribute('data-id'); var i = H[k].indexOf(id); if (i > -1) H[k].splice(i, 1); else H[k].push(id); b.disabled = true; saveJson('content/hidden.json', H, (i > -1 ? '자동 연동 글 보이기: ' : '자동 연동 글 숨기기: ') + k + ' ' + id).then(function () { afterSave(i > -1 ? '다시 보이게 했습니다' : '숨겼습니다'); route(); }).catch(function (e) { fail(e); b.disabled = false; }); }); });
      qs('#f-dispatch').addEventListener('click', function () { dispatch().then(function () { afterSave('다시 수집을 시작했습니다'); }).catch(function (e) { toast('실행 실패: ' + e.message, 6000); }); });
    });
  }
  function vServices() { return feedView({ title: '서비스(Marketplace)', desc: '한림 AI 교육 포털(ai.hallym.ac.kr/hallym-ai)에 등록된 서비스를 매일 새로 받아 Marketplace 카드 · 서비스 페이지 · 홈 · 관심 서비스 목록을 만듭니다. 이름·설명·그림·주소는 포털에서 고치고, 여기서는 보일지만 정합니다.',
    sections: [{ key: 'services', label: '포털 등록 서비스', note: '숨기면 사이트 전체(Marketplace · 홈 · 도입 문의 폼)에서 빠집니다. 숨긴 서비스도 포털에는 그대로 있습니다.', feed: 'services', thumb: function (it) { return it.icon; }, meta: function (it) { return it.category + ' · ' + (it.status === 'live' ? '운영 중' : '준비 중') + (it.summary ? ' · ' + it.summary : ''); } }] }); }
  function vEvents() { return feedView({ title: '행사', desc: 'AI교육확산센터 사이트(aiadvcenter.csedu4all.com)의 [KELI] 글을 매일 가져와 행사 목록과 글 페이지를 만듭니다. 행사 안내를 직접 쓰려면 소식·공지에서 분류 "행사 안내"로 올리세요.',
    sections: [{ key: 'events', label: '센터 사이트 [KELI] 글', note: '제목 앞에 [KELI]가 붙은 글만 가져옵니다.', feed: 'events', thumb: function (it) { return it.thumb; }, meta: function (it) { return it.when || it.date || ''; } }] }); }
  function vPress() { return feedView({ title: '보도·언론', desc: '한림대학교 보도자료(KELI·켈리)와 한국대학신문 기사(한림대 KELI·켈리)를 매일 가져와 뉴스레터·보도자료 목록에 보여 줍니다.',
    sections: [{ key: 'press', label: '한림대학교 보도자료', note: 'hallym.ac.kr › 홍보 › 보도자료 중 제목에 KELI 또는 켈리가 들어간 글. 사이트 안에 글 페이지가 만들어집니다.', feed: 'press', thumb: function (it) { return it.thumb; }, meta: function (it) { return (it.date || '') + (it.category ? ' · ' + it.category : ''); } },
      { key: 'unn', label: '한국대학신문 기사', note: '제목·요약·사진만 보여 주고 원문(새 창)으로 연결합니다.', feed: 'unn', thumb: function (it) { return it.thumb; }, meta: function (it) { return (it.date || '') + (it.reporter ? ' · ' + it.reporter : ''); } }] }); }
  function vVideos() { return feedView({ title: '영상', desc: '한림대학교 유튜브(@HALLYMNEWS)의 KELI·켈리 영상을 매일 가져옵니다. 서비스 데모 영상은 한림 AI 교육 포털에서 따로 가져옵니다(전체 데모 영상 페이지).',
    sections: [{ key: 'videos', label: '유튜브 KELI·켈리 영상', note: '숨기면 소식 · 영상 페이지에서 빠집니다.', feed: 'videos', thumb: function (it) { return it.thumb; }, meta: function (it) { return (it.published || it.date || '') + (it.group === 'keli' ? ' · KELI' : ' · 관련'); } }] }); }

  // ---------------------------------------------------------------- 게시 기록: 누가 언제 무엇을 바꿨나
  function vHistory() {
    return gh('/repos/' + CFG.repo + '/commits?per_page=40&sha=' + CFG.branch).then(function (list) {
      view.innerHTML = head('Hallym University / Website CMS', '게시 기록', '이 화면에서 저장한 내용과 자동 배포 기록입니다. 각 줄의 "보기"에서 그때의 파일 내용을 볼 수 있어 잘못 지운 글도 복구할 수 있습니다.') +
        '<div class="panel"><div class="hist">' + (list || []).map(function (c) {
          var m = (c.commit.message || '').split('\n')[0]; var who = (c.author && c.author.login) || (c.commit.author && c.commit.author.name) || ''; var when = new Date(c.commit.author.date).toLocaleString('ko-KR', { hour12: false });
          return '<div class="h"><div><div>' + esc(m) + '</div><div class="m">' + esc(who) + ' · ' + esc(when) + '</div></div><a class="btn ghost xs" href="' + esc(c.html_url) + '" target="_blank" rel="noopener">보기</a></div>';
        }).join('') + '</div></div>' +
        '<p class="small muted" style="margin-top:12px">되돌리기: "보기"에서 바뀐 파일(content/notices.json 등)의 이전 내용을 복사해 두고, 소식·공지 화면에서 같은 글을 다시 올리면 됩니다. 사무국(033-248-3246)에 알려 주시면 대신 복구해 드립니다.</p>';
    });
  }

  // ---------------------------------------------------------------- 사이트 설정 · 도움말
  function vSettings() {
    var usersPanel = SERVER ? '<div class="panel" id="users-panel"><div class="ph"><div><h3>사용자(직원 계정)</h3><p>아이디·비밀번호로 들어오는 사람들입니다. 관리자는 사용자를 추가·삭제하고 비밀번호를 다시 정할 수 있습니다.</p></div></div><div id="users-list" class="small muted">불러오는 중…</div>' +
      '<form id="user-add" class="form" style="margin-top:16px;gap:12px"><div class="grid g2" style="gap:12px"><div class="field"><label>아이디</label><input id="ua-id" placeholder="영문·숫자 2~32자" autocomplete="off"></div><div class="field"><label>이름</label><input id="ua-name" placeholder="홍길동"></div><div class="field"><label>비밀번호</label><input id="ua-pass" type="password" placeholder="8자 이상" autocomplete="new-password"></div><div class="field"><label>권한</label><select id="ua-role"><option value="editor">편집자(글 쓰기·고치기)</option><option value="admin">관리자(사용자 관리까지)</option></select></div></div><span class="msg" id="ua-msg"></span><div><button class="btn sm" type="submit" id="ua-go">사용자 추가</button></div></form></div>' +
      '<div class="panel"><div class="ph"><div><h3>내 비밀번호 바꾸기</h3></div></div><form id="pw-form" class="form" style="gap:12px"><div class="grid g2" style="gap:12px"><div class="field"><label>현재 비밀번호</label><input id="pw-old" type="password" autocomplete="current-password"></div><div class="field"><label>새 비밀번호</label><input id="pw-new" type="password" autocomplete="new-password" placeholder="8자 이상"></div></div><span class="msg" id="pw-msg"></span><div><button class="btn sm" type="submit" id="pw-go">바꾸기</button></div></form><p class="small muted" style="margin:10px 0 0">바꾸면 다른 기기의 로그인은 모두 풀립니다.</p></div>' : '';
    view.innerHTML = head('Hallym University / Website CMS', '사이트 설정', '로그인 · 사용자 · 배포 · 문제 해결.') + usersPanel +
      '<div class="panel"><div class="ph"><div><h3>로그인 정보</h3></div></div><p style="margin:0 0 12px">' + (user ? (SERVER ? '관리자 서버 계정 <strong>' + esc(user.login) + '</strong>(' + esc(user.role === 'admin' ? '관리자' : '편집자') + ')' : 'GitHub 계정 <strong>' + esc(user.login) + '</strong>') + ' 으로 들어와 있습니다.' : '') + ' 로그인 정보는 이 브라우저에만 저장됩니다. 공용 PC에서는 로그아웃 하세요.</p><button class="btn ghost sm" type="button" id="hp-logout">로그아웃</button></div>' +
      '<div class="panel"><div class="ph"><div><h3>관리자 서버 주소</h3><p>Cloudflare 에 올린 관리자 서버(아이디·비밀번호 로그인 · 용량 제한 없는 첨부)의 주소입니다. 여기에 저장하면 모든 사람의 관리자 화면에 적용됩니다.</p></div></div><form id="api-form" class="form" style="gap:12px"><div class="field"><label>서버 주소</label><input id="api-url" value="' + esc(CFG.api || '') + '" placeholder="https://keli-admin.<계정>.workers.dev"></div><div style="display:flex;gap:8px"><button class="btn sm" type="submit" id="api-go">저장하고 게시</button></div></form><p class="small muted" style="margin:10px 0 0">현재 이 브라우저가 쓰는 주소: ' + esc(SERVER || '(없음 — GitHub 토큰 로그인)') + '</p></div>' +
      '<div class="panel"><div class="ph"><div><h3>배포</h3><p>저장 → GitHub 저장소(' + esc(CFG.repo) + ')에 커밋 → GitHub Actions 가 사이트를 다시 만들어 배포(1~2분). 서비스·행사·보도자료·영상은 배포할 때마다 다시 수집되고, 매일 새벽 3시 17분에도 자동으로 돌아갑니다.</p></div></div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" type="button" id="s-dispatch">지금 다시 수집·배포</button><a class="btn ghost sm" href="https://github.com/' + esc(CFG.repo) + '/actions" target="_blank" rel="noopener">배포 기록(GitHub)</a><a class="btn ghost sm" href="' + esc(CFG.site) + '" target="_blank" rel="noopener">사이트 열기</a></div></div>' +
      '<div class="panel"><div class="ph"><div><h3>글쓰기 요령</h3></div></div><ul style="padding-left:20px;margin:0"><li>편집기에서 Enter 는 문단, Shift+Enter 는 줄바꿈입니다. 긴 글도 됩니다(길이 제한 없음).</li><li>다른 곳에서 만든 HTML 이 있으면 "HTML" 을 눌러 소스를 통째로 붙여 넣으세요(표·iframe 가능).</li><li>이미지는 "이미지" 버튼으로 올리면 글 안에 들어갑니다. 첨부파일은 글 아래 목록으로 나옵니다.</li><li>"비공개로 저장"은 홈페이지에 보이지 않게 저장(초안)하고, "게시하기"는 바로 보이게 합니다.</li><li>사이트의 모든 문장은 저장 후 자동으로 "단어·어절·마침표" 줄바꿈 규칙이 적용됩니다.</li></ul></div>' +
      '<div class="panel"><div class="ph"><div><h3>문제가 생기면</h3></div></div><dl class="kv" style="margin:0"><dt>저장 실패 401/403</dt><dd>토큰이 만료되었거나 권한이 부족합니다. 로그아웃 후 새 토큰(Contents: Read and write, Actions: Read and write)으로 다시 들어오세요.</dd><dt>저장 실패 409</dt><dd>다른 사람이 같은 파일을 먼저 저장했습니다. 한 번 더 저장하면 됩니다.</dd><dt>배포 실패</dt><dd>배포 기록 링크에서 빨간 단계를 열어 보고 사무국(033-248-3246)에 알려 주세요. 이전 버전은 그대로 서비스됩니다.</dd><dt>되돌리기</dt><dd>"게시 기록"에서 이전 버전을 볼 수 있습니다.</dd></dl></div>';
    qs('#hp-logout').addEventListener('click', logout);
    qs('#s-dispatch').addEventListener('click', function () { dispatch().then(function () { afterSave('다시 수집·배포를 시작했습니다'); }).catch(function (e) { toast('실행 실패: ' + e.message, 6000); }); });
    qs('#api-form').addEventListener('submit', function (e) {
      e.preventDefault(); var v = qs('#api-url').value.trim().replace(/\/+$/, ''); var b = qs('#api-go'); b.disabled = true;
      ensure('site').then(function () { state.site.admin = state.site.admin || {}; state.site.admin.api = v; return saveJson('content/site.json', state.site, '관리자 서버 주소 ' + (v ? '설정' : '해제')); }).then(function () { try { if (v) localStorage.setItem('keli_api', v); else localStorage.removeItem('keli_api'); } catch (e2) {} afterSave('서버 주소를 저장했습니다. 다음 배포부터 모두에게 적용됩니다'); }).catch(fail).then(function () { b.disabled = false; });
    });
    if (SERVER) {
      function renderUsers() {
        srv('/api/users').then(function (j) {
          qs('#users-list').innerHTML = '<div class="hist">' + j.users.map(function (u) { return '<div class="h"><div><div><strong>' + esc(u.name) + '</strong> <span class="muted">@' + esc(u.username) + '</span> · ' + (u.role === 'admin' ? '관리자' : '편집자') + '</div><div class="m">' + esc((u.created || '').slice(0, 10)) + ' 만듦</div></div><span style="display:flex;gap:6px"><button class="btn ghost xs" type="button" data-pw="' + esc(u.username) + '">비밀번호 재설정</button>' + (user && u.username === user.login ? '' : '<button class="btn ghost xs danger" type="button" data-rm="' + esc(u.username) + '">삭제</button>') + '</span></div>'; }).join('') + '</div>';
          qsa('[data-rm]', view).forEach(function (b) { b.addEventListener('click', function () { var u = b.getAttribute('data-rm'); confirmBox('이 사용자를 삭제할까요?', '@' + u + ' 은(는) 더 이상 로그인할 수 없습니다.', '삭제', true).then(function (ok) { if (!ok) return; srv('/api/users/' + u, { method: 'DELETE' }).then(function () { toast('삭제했습니다'); renderUsers(); }).catch(fail); }); }); });
          qsa('[data-pw]', view).forEach(function (b) { b.addEventListener('click', function () { var u = b.getAttribute('data-pw'); var bx = modal('<h3 style="margin:0 0 12px;font-size:20px">@' + esc(u) + ' 비밀번호 재설정</h3><div class="field"><label>새 비밀번호</label><input id="rp-pass" type="password" placeholder="8자 이상"></div><div style="display:flex;gap:8px;justify-content:flex-end;margin-top:16px"><button class="btn ghost" type="button" id="rp-x">취소</button><button class="btn" type="button" id="rp-ok">바꾸기</button></div>'); qs('#rp-x', bx).addEventListener('click', closeModal); qs('#rp-ok', bx).addEventListener('click', function () { var p = qs('#rp-pass', bx).value; srv('/api/users/' + u + '/password', { method: 'POST', body: { password: p } }).then(function () { closeModal(); toast('비밀번호를 바꿨습니다. 본인에게 알려 주세요'); }).catch(function (e) { toast(e.message, 5000); }); }); }); });
        }).catch(function (e) { qs('#users-list').innerHTML = '<span class="muted">' + esc(e.status === 403 ? '사용자 목록은 관리자만 볼 수 있습니다' : e.message) + '</span>'; qs('#user-add').hidden = true; });
      }
      renderUsers();
      qs('#user-add').addEventListener('submit', function (e) { e.preventDefault(); var m = qs('#ua-msg'); m.style.display = 'none'; var b = qs('#ua-go'); b.disabled = true; srv('/api/users', { method: 'POST', body: { username: qs('#ua-id').value.trim(), password: qs('#ua-pass').value, name: qs('#ua-name').value.trim(), role: qs('#ua-role').value } }).then(function () { toast('사용자를 추가했습니다'); qs('#ua-id').value = ''; qs('#ua-name').value = ''; qs('#ua-pass').value = ''; renderUsers(); }).catch(function (err) { m.textContent = err.message; m.style.display = 'block'; }).then(function () { b.disabled = false; }); });
      qs('#pw-form').addEventListener('submit', function (e) { e.preventDefault(); var m = qs('#pw-msg'); m.style.display = 'none'; var b = qs('#pw-go'); b.disabled = true; srv('/api/me/password', { method: 'POST', body: { old: qs('#pw-old').value, password: qs('#pw-new').value } }).then(function (j) { token = j.token; saveToken(token, !!loadToken() && !!localStorage.getItem(tokKey())); qs('#pw-old').value = ''; qs('#pw-new').value = ''; toast('비밀번호를 바꿨습니다'); }).catch(function (err) { m.textContent = err.message; m.style.display = 'block'; }).then(function () { b.disabled = false; }); });
    }
  }

  // ---------------------------------------------------------------- 로그인 흐름
  function showLogin(msg) {
    qs('#adm-login').hidden = false; qs('#adm-app').hidden = true;
    var pw = qs('#login-pw'), tk = qs('#login-tok'); if (pw && tk) { pw.hidden = !SERVER; tk.hidden = !!SERVER; }
    var sv = qs('#srv-cur'); if (sv) sv.textContent = SERVER ? SERVER : '(없음 — GitHub 토큰으로 로그인)';
    if (SERVER) srv('/api/ping').then(function (j) { SERVER_FILES = !!j.files; var st = qs('#setup-card'); if (st) st.hidden = !j.setup; }).catch(function () { var m2 = qs('#tok-msg'); m2.textContent = '관리자 서버(' + SERVER + ')에 연결하지 못했습니다. 주소를 확인하세요'; m2.style.display = 'block'; });
    if (msg) { var m = qs('#tok-msg'); m.textContent = msg; m.style.display = 'block'; }
  }
  function enter() {
    return (SERVER ? srv('/api/ping').then(function (j) { SERVER_FILES = !!j.files; }).catch(function () {}) : Promise.resolve()).then(function () { return gh('/user'); }).then(function (u) { user = u; return gh('/repos/' + CFG.repo); }).then(function (r) {
      if (!(r.permissions && (r.permissions.push || r.permissions.admin || r.permissions.maintain))) throw new Error('이 토큰으로는 ' + CFG.repo + ' 저장소에 쓸 수 없습니다. 토큰의 Repository access 와 Contents 권한을 확인하세요');
      qs('#adm-login').hidden = true; qs('#adm-app').hidden = false; qs('#adm-logout').hidden = false;
      qs('#u-name').textContent = user.name || user.login; qs('#u-avatar').textContent = String(user.name || user.login).slice(0, 1).toUpperCase();
      checkDeploy(false); route();
      Promise.all([liveFeed('services'), liveFeed('events'), liveFeed('press'), liveFeed('unn'), liveFeed('videos'), ensure('notices'), ensure('archive')]).then(counts).catch(function () {});
    });
  }
  function logout() { clearToken(); token = null; user = null; state = { notices: null, archive: null, hidden: null, stats: null, site: null, cats: null, feeds: {}, sha: {} }; showLogin(''); location.hash = ''; }
  qs('#adm-logout').addEventListener('click', logout);
  qs('#login-form').addEventListener('submit', function (e) {
    e.preventDefault(); var m = qs('#tok-msg'); m.style.display = 'none'; var btn = qs('#tok-go'); var keep = qs('#tok-keep').checked;
    if (SERVER) {   // 아이디·비밀번호 → 서버가 세션 토큰을 준다
      var id = qs('#login-id').value.trim(), pw = qs('#login-pass').value; if (!id || !pw) { m.textContent = '아이디와 비밀번호를 입력해 주세요'; m.style.display = 'block'; return; }
      btn.disabled = true; btn.textContent = '확인 중…';
      srv('/api/login', { method: 'POST', body: { username: id, password: pw } }).then(function (j) { token = j.token; return enter().then(function () { saveToken(token, keep); qs('#login-pass').value = ''; toast((user.name || user.login) + ' 님, 어서 오세요'); }); })
        .catch(function (err) { token = null; showLogin(err.message); }).then(function () { btn.disabled = false; btn.textContent = '들어가기'; });
      return;
    }
    var t = qs('#tok').value.trim(); if (!t) { m.textContent = '토큰을 붙여 넣어 주세요'; m.style.display = 'block'; return; }
    btn.disabled = true; btn.textContent = '확인 중…'; token = t;
    enter().then(function () { saveToken(t, keep); qs('#tok').value = ''; toast((user.name || user.login) + ' 님, 어서 오세요'); }).catch(function (err) { token = null; showLogin(err.status === 401 ? '토큰이 올바르지 않거나 만료되었습니다' : err.message); }).then(function () { btn.disabled = false; btn.textContent = '들어가기'; });
  });
  // 서버 주소 바꾸기(이 브라우저에만 저장) · 첫 관리자 만들기
  var srvForm = qs('#srv-form');
  if (srvForm) srvForm.addEventListener('submit', function (e) { e.preventDefault(); var v = qs('#srv-url').value.trim().replace(/\/+$/, ''); try { if (v) localStorage.setItem('keli_api', v); else localStorage.removeItem('keli_api'); } catch (e2) {} location.reload(); });
  var setupForm = qs('#setup-form');
  if (setupForm) setupForm.addEventListener('submit', function (e) {
    e.preventDefault(); var b = qs('#setup-go'); b.disabled = true;
    srv('/api/setup', { method: 'POST', body: { setup_key: qs('#setup-key').value.trim(), username: qs('#setup-id').value.trim(), password: qs('#setup-pass').value, name: qs('#setup-name').value.trim() } })
      .then(function (j) { token = j.token; return enter().then(function () { saveToken(token, true); toast('첫 관리자 계정을 만들었습니다'); }); })
      .catch(function (err) { var m = qs('#setup-msg'); m.textContent = err.message; m.style.display = 'block'; }).then(function () { b.disabled = false; });
  });
  qs('#tok-help').addEventListener('click', function (e) { e.preventDefault(); qs('#help-card').scrollIntoView({ behavior: 'smooth' }); });

  var saved = loadToken();
  if (saved) { token = saved; enter().catch(function (err) { token = null; clearToken(); showLogin(err.status === 401 ? '저장된 토큰이 만료되었습니다. 새 토큰으로 들어오세요' : err.message); }); }
  else showLogin('');
})();
