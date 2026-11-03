/* KELI 관리자 — GitHub 저장소의 content/*.json 과 assets/stats.json 을 브라우저에서 직접 고친다.
   저장 = 커밋. 커밋이 올라가면 GitHub Actions 가 사이트를 다시 만들어 1~2분 뒤 반영된다. */
(function () {
  'use strict';
  var CFG = window.KELI_ADMIN || { repo: 'yoong0520/keli-site', branch: 'main', site: './', workflow: 'pages.yml' };
  if (location.protocol !== 'file:') CFG.site = new URL('./', location.href).href;   // 주소(도메인)가 바뀌어도 그대로 동작
  var API = 'https://api.github.com';
  var qs = function (s, r) { return (r || document).querySelector(s); };
  var qsa = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var token = null, user = null, state = { notices: null, archive: null, hidden: null, stats: null, sha: {} };

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

  // ---------------------------------------------------------------- 토큰
  function loadToken() { try { return localStorage.getItem('keli_admin_token') || sessionStorage.getItem('keli_admin_token'); } catch (e) { return null; } }
  function saveToken(t, keep) { try { (keep ? localStorage : sessionStorage).setItem('keli_admin_token', t); (keep ? sessionStorage : localStorage).removeItem('keli_admin_token'); } catch (e) {} }
  function clearToken() { try { localStorage.removeItem('keli_admin_token'); sessionStorage.removeItem('keli_admin_token'); } catch (e) {} }

  // ---------------------------------------------------------------- GitHub API
  function gh(path, opt) {
    opt = opt || {};
    var h = { 'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + token, 'X-GitHub-Api-Version': '2022-11-28' };
    if (opt.body) h['Content-Type'] = 'application/json';
    return fetch(API + path, { method: opt.method || 'GET', headers: h, body: opt.body ? JSON.stringify(opt.body) : undefined, cache: 'no-store' }).then(function (r) {
      if (r.status === 204) return null;
      return r.text().then(function (t) { var j = {}; try { j = t ? JSON.parse(t) : {}; } catch (e) {} if (!r.ok) { var err = new Error(j.message || ('HTTP ' + r.status)); err.status = r.status; throw err; } return j; });
    });
  }
  function encPath(p) { return p.split('/').map(encodeURIComponent).join('/'); }
  function b64enc(str) { var bytes = new TextEncoder().encode(str), bin = ''; for (var i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000)); return btoa(bin); }
  function b64dec(b64) { var bin = atob(b64.replace(/\n/g, '')), bytes = new Uint8Array(bin.length); for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i); return new TextDecoder().decode(bytes); }
  function getFile(path) {
    return gh('/repos/' + CFG.repo + '/contents/' + encPath(path) + '?ref=' + CFG.branch).then(function (j) {
      if (j.content) return { sha: j.sha, text: b64dec(j.content) };
      // 1MB 넘는 파일은 content 가 비어 온다 → 원본 주소에서 받는다
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
        if (e.status === 409 || e.status === 422) { // 다른 곳에서 먼저 저장됨 → 최신 sha 로 한 번 더
          return getFile(path).then(function (f) { state.sha[path] = f.sha; return putFile(path, b64enc(text), message, f.sha); }).then(function (j) { state.sha[path] = j.content.sha; return j; });
        }
        throw e;
      });
  }
  function loadJson(path, fallback) { return getFile(path).then(function (f) { state.sha[path] = f.sha; if (!f.text) return fallback; try { return JSON.parse(f.text); } catch (e) { toast(path + ' 파일이 깨져 있어 새로 만듭니다'); return fallback; } }); }
  function readFileB64(file) { return new Promise(function (res, rej) { var r = new FileReader(); r.onload = function () { res(String(r.result).split(',')[1]); }; r.onerror = rej; r.readAsDataURL(file); }); }
  function safeName(n) { return n.normalize('NFC').replace(/[\\\/:*?"<>|#%&+\s]+/g, '_').replace(/_+/g, '_'); }
  function fmtSize(b) { return b > 1048576 ? (b / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(b / 1024)) + ' KB'; }
  function uploadFile(file, folder) {
    if (file.size > 100 * 1048576) return Promise.reject(new Error('100MB 를 넘는 파일은 올릴 수 없습니다'));
    var d = new Date(), ym = d.getFullYear() + '/' + String(d.getMonth() + 1).padStart(2, '0');
    var path = 'content/files/' + ym + '/' + Date.now().toString(36) + '_' + safeName(file.name);
    return readFileB64(file).then(function (b64) { return putFile(path, b64, '첨부 올림: ' + file.name); }).then(function () { return { name: file.name, url: path, size: fmtSize(file.size) }; });
  }
  function dispatch() { return gh('/repos/' + CFG.repo + '/actions/workflows/' + CFG.workflow + '/dispatches', { method: 'POST', body: { ref: CFG.branch } }); }

  // ---------------------------------------------------------------- 배포 상태
  var pollT = null;
  function deployState(st, text) { var d = qs('#deploy'); d.setAttribute('data-state', st); qs('#deploy-text').innerHTML = text; }
  function checkDeploy(keep) {
    clearTimeout(pollT);
    return gh('/repos/' + CFG.repo + '/actions/runs?per_page=1&branch=' + CFG.branch).then(function (j) {
      var r = (j.workflow_runs || [])[0]; if (!r) { deployState('idle', '배포 기록이 아직 없습니다'); return; }
      var when = new Date(r.created_at).toLocaleString('ko-KR', { hour12: false });
      if (r.status !== 'completed') { deployState('running', '배포 중 · ' + esc(r.display_title || '') + ' · 보통 1~2분 걸립니다'); pollT = setTimeout(function () { checkDeploy(true); }, 10000); return; }
      if (r.conclusion === 'success') deployState('ok', '반영 완료 · ' + when + ' · <a href="' + esc(CFG.site) + '" target="_blank" rel="noopener">사이트 보기</a>' + (keep ? ' — 방금 저장한 내용이 올라갔습니다' : ''));
      else deployState('fail', '배포 실패(' + esc(r.conclusion) + ') · <a href="' + esc(r.html_url) + '" target="_blank" rel="noopener">기록 보기</a> · 사무국에 알려 주세요');
    }).catch(function (e) { deployState('idle', '배포 상태를 읽지 못했습니다(' + esc(e.message) + '). 토큰에 Actions: Read 권한이 있는지 확인하세요'); });
  }
  function afterSave(msg) { toast(msg + ' · 1~2분 뒤 사이트에 반영됩니다'); deployState('running', '커밋됨 · 배포가 곧 시작됩니다'); clearTimeout(pollT); pollT = setTimeout(function () { checkDeploy(true); }, 8000); }

  // ---------------------------------------------------------------- 데이터
  function ensure(kind) {
    if (kind === 'notices' && !state.notices) return loadJson('content/notices.json', { items: [] }).then(function (j) { state.notices = j; });
    if (kind === 'archive' && !state.archive) return loadJson('content/archive.json', { items: [] }).then(function (j) { state.archive = j; });
    if (kind === 'hidden' && !state.hidden) return loadJson('content/hidden.json', { events: [], press: [], videos: [], unn: [] }).then(function (j) { state.hidden = j; });
    if (kind === 'stats' && !state.stats) return loadJson('assets/stats.json', { services: 19, universities: 23, companies: 31, courses: null, basis: '' }).then(function (j) { state.stats = j; });
    return Promise.resolve();
  }
  function counts() { qsa('[data-cnt]').forEach(function (e) { var k = e.getAttribute('data-cnt'); var s = state[k]; e.textContent = s ? (s.items || []).length : ''; }); }
  function today() { var d = new Date(); return d.getFullYear() + '.' + String(d.getMonth() + 1).padStart(2, '0') + '.' + String(d.getDate()).padStart(2, '0'); }
  function newId(p) { return p + Date.now().toString(36); }
  function sortNotices(items) { return items.slice().sort(function (a, b) { if (!!a.pinned !== !!b.pinned) return a.pinned ? -1 : 1; return (b.date || '').localeCompare(a.date || ''); }); }

  // ---------------------------------------------------------------- 라우터
  var view = qs('#view');
  function route() {
    var h = (location.hash || '#home').slice(1).split('/'); var v = h[0] || 'home';
    qsa('.adm-nav a').forEach(function (a) { a.classList.toggle('on', a.getAttribute('data-view') === v); });
    view.innerHTML = '<p class="muted">불러오는 중…</p>';
    var fn = { home: vHome, notices: vNotices, archive: vArchive, stats: vStats, feeds: vFeeds, help: vHelp }[v] || vHome;
    Promise.resolve(fn(h.slice(1))).catch(function (e) { view.innerHTML = '<div class="card"><p>불러오지 못했습니다: ' + esc(e.message) + '</p><p class="small muted">토큰 권한(Contents: Read and write)과 저장소 이름을 확인해 주세요.</p></div>'; });
  }
  window.addEventListener('hashchange', route);

  // ---------------------------------------------------------------- 대시보드
  function vHome() {
    return Promise.all([ensure('notices'), ensure('archive'), ensure('hidden')]).then(function () {
      counts();
      var n = state.notices.items || [], a = state.archive.items || [], hcount = (state.hidden.events || []).length + (state.hidden.press || []).length + (state.hidden.unn || []).length + (state.hidden.videos || []).length;
      view.innerHTML =
        '<div class="adm-head"><h2>대시보드</h2><div style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn sm" href="#notices/new">새 공지 쓰기</a><button class="btn ghost sm" type="button" id="h-dispatch">지금 다시 수집·배포</button></div></div>' +
        '<div class="grid g3" style="gap:16px">' +
        '<a class="card" href="#notices"><span class="k">공지사항</span><span class="num" style="font-size:36px">' + n.length + '</span><p>게시 ' + n.filter(function (x) { return x.published !== false; }).length + ' · 비공개 ' + n.filter(function (x) { return x.published === false; }).length + ' · 고정 ' + n.filter(function (x) { return x.pinned; }).length + '</p></a>' +
        '<a class="card" href="#archive"><span class="k">아카이브</span><span class="num" style="font-size:36px">' + a.length + '</span><p>사례 ' + a.filter(function (x) { return x.cat === 'case'; }).length + ' · 동향 ' + a.filter(function (x) { return x.cat === 'trend'; }).length + ' · 매뉴얼 ' + a.filter(function (x) { return x.cat === 'manual'; }).length + '</p></a>' +
        '<a class="card" href="#feeds"><span class="k">자동 연동 글</span><span class="num" style="font-size:36px">' + hcount + '</span><p>숨긴 글 수 · 행사(센터 사이트) · 보도자료(한림대) · 영상(유튜브)</p></a>' +
        '</div>' +
        '<div class="card" style="margin-top:20px"><span class="k">이 화면이 하는 일</span><p>여기서 저장하면 GitHub 저장소의 글 파일(content/*.json)이 바뀌고, 1~2분 뒤 사이트가 자동으로 다시 만들어집니다. 글 본문은 편집기로 쓰거나 HTML 소스를 그대로 붙여 넣을 수 있고 길이 제한이 없습니다. 첨부파일과 이미지는 저장소(content/files/)에 올라갑니다.</p><p class="small muted">행사·보도자료·영상은 매일 새벽 자동으로 수집되므로 직접 쓰지 않습니다. 필요 없는 글만 "자동 연동 글"에서 숨기면 됩니다.</p></div>';
      qs('#h-dispatch').addEventListener('click', function () { dispatch().then(function () { afterSave('다시 수집·배포를 시작했습니다'); }).catch(function (e) { toast('실행 실패: ' + e.message + ' (토큰에 Actions: Read and write 권한 필요)', 6000); }); });
    });
  }

  // ---------------------------------------------------------------- 공지사항
  var CATS = ['일반', '모집', '보도'];
  function vNotices(args) {
    return ensure('notices').then(function () {
      counts();
      if (args[0] === 'new') return editNotice(null);
      if (args[0] === 'edit') { var it = (state.notices.items || []).filter(function (x) { return x.id === args[1]; })[0]; if (!it) { toast('글을 찾지 못했습니다'); location.hash = '#notices'; return; } return editNotice(it); }
      var items = sortNotices(state.notices.items || []);
      view.innerHTML = '<div class="adm-head"><h2>공지사항 <span class="muted" style="font-size:16px;font-weight:500">' + items.length + '건</span></h2><a class="btn sm" href="#notices/new">새 공지 쓰기</a></div>' +
        (items.length ? '<div class="list">' + items.map(function (n) {
          return '<div class="li' + (n.published === false ? ' off' : '') + '"><span>' + (n.pinned ? '<span class="badge live" style="margin-right:6px">고정</span>' : '') + (n.published === false ? '<span class="badge soon" style="margin-right:6px">비공개</span>' : '') + '<span class="badge" style="margin-right:8px">' + esc(n.cat) + '</span><span class="t">' + esc(n.title) + '</span><br><span class="m">' + esc(n.date || '') + (n.files && n.files.length ? ' · 첨부 ' + n.files.length : '') + '</span></span>' +
            '<span class="acts"><a class="btn ghost xs" href="#notices/edit/' + esc(n.id) + '">수정</a><button class="btn ghost xs" type="button" data-act="pin" data-id="' + esc(n.id) + '">' + (n.pinned ? '고정 해제' : '상단 고정') + '</button><button class="btn ghost xs" type="button" data-act="pub" data-id="' + esc(n.id) + '">' + (n.published === false ? '게시' : '비공개') + '</button><a class="btn ghost xs" href="' + esc(CFG.site) + 'notice-' + esc(n.id) + '.html" target="_blank" rel="noopener">보기</a><button class="btn ghost xs danger" type="button" data-act="del" data-id="' + esc(n.id) + '">삭제</button></span></div>';
        }).join('') + '</div>' : '<div class="empty">아직 공지가 없습니다. "새 공지 쓰기"를 눌러 첫 글을 올려 보세요.</div>');
      qsa('[data-act]', view).forEach(function (b) {
        b.addEventListener('click', function () {
          var id = b.getAttribute('data-id'), act = b.getAttribute('data-act'); var it = state.notices.items.filter(function (x) { return x.id === id; })[0]; if (!it) return;
          if (act === 'del') { confirmBox('이 공지를 삭제할까요?', '"' + it.title + '" 글이 사이트에서 사라집니다. 되돌리려면 GitHub 기록에서 복구해야 합니다.', '삭제', true).then(function (ok) { if (!ok) return; state.notices.items = state.notices.items.filter(function (x) { return x.id !== id; }); saveJson('content/notices.json', state.notices, '공지 삭제: ' + it.title).then(function () { afterSave('삭제했습니다'); route(); }).catch(fail); }); return; }
          if (act === 'pin') it.pinned = !it.pinned;
          if (act === 'pub') it.published = it.published === false;
          saveJson('content/notices.json', state.notices, (act === 'pin' ? (it.pinned ? '공지 상단 고정: ' : '공지 고정 해제: ') : (it.published === false ? '공지 비공개: ' : '공지 게시: ')) + it.title).then(function () { afterSave('저장했습니다'); route(); }).catch(fail);
        });
      });
    });
  }
  function fail(e) { toast('저장 실패: ' + e.message, 6000); }

  // ---------------------------------------------------------------- 공용: 본문 편집기 · 첨부파일 상자
  var ED_BTNS = [['h3', '소제목'], ['bold', '굵게'], ['italic', '기울임'], ['sep'], ['ul', '• 목록'], ['ol', '1. 목록'], ['quote', '인용'], ['sep'], ['link', '링크'], ['img', '이미지'], ['table', '표'], ['sep'], ['clear', '서식 지우기'], ['html', 'HTML']];
  function editorHtml(id) {
    return '<div class="ed-bar" id="' + id + '-bar">' + ED_BTNS.map(function (b) { return b[0] === 'sep' ? '<span class="sep"></span>' : '<button type="button" data-ed="' + b[0] + '">' + b[1] + '</button>'; }).join('') + '</div>' +
      '<div class="ed" id="' + id + '" contenteditable="true"></div><textarea class="ed-src" id="' + id + '-src" hidden spellcheck="false"></textarea><input type="file" id="' + id + '-img" accept="image/*" hidden>';
  }
  function mountEditor(id, initial) {
    var ed = qs('#' + id), src = qs('#' + id + '-src'), htmlMode = false, listeners = [];
    ed.innerHTML = initial || '';
    function body() { return htmlMode ? src.value.trim() : ed.innerHTML.trim(); }
    function fire() { listeners.forEach(function (f) { f(); }); }
    qsa('[data-ed]', qs('#' + id + '-bar')).forEach(function (b) {
      b.addEventListener('mousedown', function (e) { e.preventDefault(); });
      b.addEventListener('click', function () {
        var c = b.getAttribute('data-ed');
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
    qs('#' + id + '-img').addEventListener('change', function () { var f = this.files[0]; if (!f) return; var inp = this; var range = window.getSelection().rangeCount ? window.getSelection().getRangeAt(0) : null; toast('이미지 올리는 중…'); uploadFile(f).then(function (r) { ed.focus(); if (range) { window.getSelection().removeAllRanges(); window.getSelection().addRange(range); } document.execCommand('insertHTML', false, '<figure class="art-fig"><img src="' + esc(r.url) + '" alt="' + esc(f.name.replace(/\.[^.]+$/, '')) + '"><figcaption></figcaption></figure><p></p>'); toast('이미지를 넣었습니다'); fire(); }).catch(function (e) { toast('이미지 실패: ' + e.message, 6000); }).then(function () { inp.value = ''; }); });
    ed.addEventListener('input', fire); src.addEventListener('input', fire);
    return { body: body, onInput: function (f) { listeners.push(f); } };
  }
  function filesHtml(id, hint) { return '<div class="files-box" id="' + id + '"></div><div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:8px"><input type="file" id="' + id + '-in" multiple><span class="small muted">' + (hint || 'PDF·HWP·이미지 등 여러 개 가능. 올리는 즉시 저장소에 들어갑니다') + '</span></div>'; }
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

  function editNotice(it) {
    var isNew = !it; it = it || { id: newId('n'), cat: '일반', title: '', date: today(), body: '', link: '', pinned: false, published: true, files: [] };
    var draftKey = 'keli_draft_' + it.id; var draft = null; try { draft = JSON.parse(localStorage.getItem(draftKey) || 'null'); } catch (e) {}
    view.innerHTML = '<div class="adm-head"><h2>' + (isNew ? '새 공지' : '공지 수정') + '</h2><a class="more" href="#notices">← 목록</a></div>' +
      '<form class="form" id="nf" novalidate>' +
      '<div class="grid g2" style="gap:16px"><div class="field" style="grid-column:1/-1"><label for="n-title">제목</label><input id="n-title" required value="' + esc(it.title) + '"><span class="msg" id="n-title-msg">제목을 입력해 주세요</span></div>' +
      '<div class="field"><label for="n-cat">분류</label><select id="n-cat">' + CATS.map(function (c) { return '<option' + (c === it.cat ? ' selected' : '') + '>' + c + '</option>'; }).join('') + '</select></div>' +
      '<div class="field"><label for="n-date">날짜</label><input id="n-date" value="' + esc(it.date) + '" placeholder="2026.11.02"></div>' +
      '<div class="field" style="grid-column:1/-1"><label for="n-link">관련 링크 (선택)</label><input id="n-link" value="' + esc(it.link || '') + '" placeholder="events.html 또는 https://…"></div></div>' +
      '<div class="field"><label>본문 <span class="muted" style="font-weight:400">— 편집기로 쓰거나 "HTML" 을 눌러 소스를 붙여 넣으세요. 길이 제한 없음</span></label>' + editorHtml('ed') + '</div>' +
      '<div class="field"><label>첨부파일</label>' + filesHtml('files') + '</div>' +
      '<div style="display:flex;gap:20px;flex-wrap:wrap"><label class="chk"><input type="checkbox" id="n-pin"' + (it.pinned ? ' checked' : '') + '><span>상단 고정</span></label><label class="chk"><input type="checkbox" id="n-pub"' + (it.published !== false ? ' checked' : '') + '><span>게시(끄면 비공개 저장)</span></label></div>' +
      '<div class="acts" style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn" type="submit" id="n-save">저장</button><button class="btn ghost" type="button" id="n-preview">미리보기</button><a class="btn ghost" href="#notices">취소</a></div>' +
      '</form>';
    var initial = it.body || '';
    if (draft && draft.body && draft.body !== it.body) { toast('저장하지 않은 임시 글이 있어 불러왔습니다', 4000); initial = draft.body; if (draft.title) qs('#n-title').value = draft.title; }
    var editor = mountEditor('ed', initial), fb = mountFiles('files', it.files ? it.files.slice() : []), files = fb.files;
    var draftT = null; function saveDraft() { clearTimeout(draftT); draftT = setTimeout(function () { try { localStorage.setItem(draftKey, JSON.stringify({ title: qs('#n-title').value, body: editor.body() })); } catch (e) {} }, 600); }
    editor.onInput(saveDraft); qs('#n-title').addEventListener('input', saveDraft);
    qs('#n-preview').addEventListener('click', function () { var fl = files.length ? '<div class="art-files"><strong>첨부파일</strong><ul>' + files.map(function (f) { return '<li>' + esc(f.name) + '</li>'; }).join('') + '</ul></div>' : ''; modal('<span class="eyebrow">공지사항 · ' + esc(qs('#n-cat').value) + '</span><h2 style="margin:4px 0 4px;font-size:30px">' + esc(qs('#n-title').value || '(제목 없음)') + '</h2><p class="muted">' + esc(qs('#n-date').value) + ' · KELI 사무국</p><article class="art">' + (editor.body() || '<p class="muted">(본문 없음)</p>') + '</article>' + fl + '<div style="display:flex;justify-content:flex-end;margin-top:16px"><button class="btn ghost" type="button" id="pv-x">닫기</button></div>', true); qs('#pv-x').addEventListener('click', closeModal); });
    qs('#nf').addEventListener('submit', function (e) {
      e.preventDefault(); var t = qs('#n-title').value.trim(); var msg = qs('#n-title-msg'); if (!t) { msg.style.display = 'block'; qs('#n-title').focus(); return; } msg.style.display = 'none';
      var btn = qs('#n-save'); btn.disabled = true; btn.textContent = '저장 중…';
      it.title = t; it.cat = qs('#n-cat').value; it.date = qs('#n-date').value.trim() || today(); it.link = qs('#n-link').value.trim(); it.body = editor.body(); it.pinned = qs('#n-pin').checked; it.published = qs('#n-pub').checked; it.files = files;
      if (isNew) state.notices.items = [it].concat(state.notices.items || []);
      saveJson('content/notices.json', state.notices, (isNew ? '공지 등록: ' : '공지 수정: ') + t).then(function () { try { localStorage.removeItem(draftKey); } catch (e2) {} afterSave(isNew ? '공지를 올렸습니다' : '공지를 고쳤습니다'); location.hash = '#notices'; }).catch(function (e2) { fail(e2); btn.disabled = false; btn.textContent = '저장'; });
    });
  }

  // ---------------------------------------------------------------- 아카이브: 외부 주소를 가져오거나, 파일을 직접 올리거나, 설명 글과 함께 올리거나
  var ACATS = [['manual', '매뉴얼·소개자료'], ['trend', '기술 동향·연구'], ['case', '실증 사례집']], ATYPES = [['pdf', 'PDF'], ['doc', '문서'], ['link', '링크'], ['video', '영상'], ['image', '이미지']];
  function lbl(list, k) { var m = list.filter(function (x) { return x[0] === k; })[0]; return m ? m[1] : k; }
  function typeOf(name) { return /\.pdf$/i.test(name) ? 'pdf' : /\.(png|jpe?g|gif|webp)$/i.test(name) ? 'image' : /\.(mp4|mov|webm)$/i.test(name) ? 'video' : /\.(hwpx?|docx?|pptx?|xlsx?|zip|txt)$/i.test(name) ? 'doc' : 'doc'; }
  function archiveOpen(a) { var fs = a.files || []; if (a.body || fs.length > 1 || (fs.length && a.url)) return CFG.site + 'archive-' + a.id + '.html'; return a.url || (fs[0] && fs[0].url) || (CFG.site + 'archive.html'); }
  function vArchive(args) {
    return ensure('archive').then(function () {
      counts();
      if (args[0] === 'new') return editArchive(null);
      if (args[0] === 'edit') { var it = (state.archive.items || []).filter(function (x) { return x.id === args[1]; })[0]; if (!it) { location.hash = '#archive'; return; } return editArchive(it); }
      var items = state.archive.items || [];
      view.innerHTML = '<div class="adm-head"><h2>아카이브 <span class="muted" style="font-size:16px;font-weight:500">' + items.length + '건</span></h2><a class="btn sm" href="#archive/new">자료 추가</a></div><p class="muted small" style="margin:0 0 4px">자료는 세 가지 방식으로 올립니다. 다른 사이트 주소를 가져오거나, 파일을 직접 올리거나, 설명 글과 첨부를 함께 올리면 자료 페이지가 생깁니다.</p>' +
        ACATS.map(function (c) { var li = items.filter(function (a) { return a.cat === c[0]; }); return '<h3 style="margin:24px 0 8px;font-size:18px">' + c[1] + ' <span class="muted" style="font-weight:500;font-size:14px">' + li.length + '</span></h3>' + (li.length ? '<div class="list">' + li.map(function (a) { var fs = a.files || []; return '<div class="li' + (a.published === false ? ' off' : '') + '"><span>' + (a.published === false ? '<span class="badge soon" style="margin-right:6px">비공개</span>' : '') + '<span class="badge" style="margin-right:8px">' + esc(lbl(ATYPES, a.type)) + '</span><span class="t">' + esc(a.title) + '</span><br><span class="m">' + esc(a.org || '') + ' · ' + esc(a.date || '') + (fs.length ? ' · 첨부 ' + fs.length : '') + (a.url ? ' · 외부 주소' : '') + (a.body ? ' · 설명 글' : '') + '</span></span><span class="acts"><a class="btn ghost xs" href="#archive/edit/' + esc(a.id) + '">수정</a><a class="btn ghost xs" href="' + esc(archiveOpen(a)) + '" target="_blank" rel="noopener">열기</a><button class="btn ghost xs danger" type="button" data-del="' + esc(a.id) + '">삭제</button></span></div>'; }).join('') + '</div>' : '<p class="muted small">없음</p>'); }).join('');
      qsa('[data-del]', view).forEach(function (b) { b.addEventListener('click', function () { var id = b.getAttribute('data-del'); var it = items.filter(function (x) { return x.id === id; })[0]; confirmBox('이 자료를 삭제할까요?', '"' + it.title + '" 이(가) 아카이브에서 사라집니다.', '삭제', true).then(function (ok) { if (!ok) return; state.archive.items = items.filter(function (x) { return x.id !== id; }); saveJson('content/archive.json', state.archive, '아카이브 삭제: ' + it.title).then(function () { afterSave('삭제했습니다'); route(); }).catch(fail); }); }); });
    });
  }
  function editArchive(it) {
    var isNew = !it; it = it || { id: newId('a'), cat: 'case', type: 'pdf', title: '', org: 'KELI 사무국', date: today(), url: '', body: '', files: [], published: true };
    view.innerHTML = '<div class="adm-head"><h2>' + (isNew ? '자료 추가' : '자료 수정') + '</h2><a class="more" href="#archive">← 목록</a></div>' +
      '<form class="form" id="af" novalidate><div class="grid g2" style="gap:16px">' +
      '<div class="field" style="grid-column:1/-1"><label for="a-title">제목</label><input id="a-title" value="' + esc(it.title) + '"><span class="msg" id="a-title-msg">제목을 입력해 주세요</span></div>' +
      '<div class="field"><label for="a-cat">분류</label><select id="a-cat">' + ACATS.map(function (c) { return '<option value="' + c[0] + '"' + (c[0] === it.cat ? ' selected' : '') + '>' + c[1] + '</option>'; }).join('') + '</select></div>' +
      '<div class="field"><label for="a-type">유형</label><select id="a-type">' + ATYPES.map(function (c) { return '<option value="' + c[0] + '"' + (c[0] === it.type ? ' selected' : '') + '>' + c[1] + '</option>'; }).join('') + '</select><span class="hint">파일을 올리면 자동으로 맞춰집니다</span></div>' +
      '<div class="field"><label for="a-org">기관</label><input id="a-org" value="' + esc(it.org || '') + '"></div>' +
      '<div class="field"><label for="a-date">날짜</label><input id="a-date" value="' + esc(it.date || '') + '" placeholder="2026.11"></div>' +
      '</div>' +
      '<div class="card" style="padding:20px 22px"><span class="k">방법 1 · 다른 사이트의 주소 가져오기</span><div class="field" style="margin-top:8px"><label for="a-url">외부 주소 (선택)</label><input id="a-url" value="' + esc(it.url || '') + '" placeholder="https://… (한림 AI 교육 포털, 구글 드라이브, 유튜브 등)"><span class="hint">주소만 넣으면 목록에서 그 주소가 새 창으로 열립니다</span></div></div>' +
      '<div class="card" style="padding:20px 22px"><span class="k">방법 2 · 파일 직접 올리기</span><div class="field" style="margin-top:8px"><label>첨부파일 (선택, 여러 개 가능)</label>' + filesHtml('a-files', 'PDF·HWP·PPT·이미지·영상 등. 파일이 하나면 목록에서 바로 열리고, 여러 개면 자료 페이지가 생깁니다') + '</div></div>' +
      '<div class="card" style="padding:20px 22px"><span class="k">방법 3 · 설명 글과 함께 올리기</span><div class="field" style="margin-top:8px"><label>설명 (선택)</label>' + editorHtml('a-ed') + '<span class="hint">설명을 쓰면 공지처럼 자료 페이지(제목 · 설명 · 첨부 · 외부 주소)가 만들어집니다</span></div></div>' +
      '<span class="msg" id="a-need-msg">외부 주소, 파일, 설명 가운데 하나는 있어야 합니다</span>' +
      '<label class="chk"><input type="checkbox" id="a-pub"' + (it.published !== false ? ' checked' : '') + '><span>게시(끄면 비공개 저장)</span></label>' +
      '<div class="acts" style="display:flex;gap:8px"><button class="btn" type="submit" id="a-save">저장</button><a class="btn ghost" href="#archive">취소</a></div></form>';
    var editor = mountEditor('a-ed', it.body || '');
    var fb = mountFiles('a-files', it.files ? it.files.slice() : [], function (files, added) { if (added && files.length === 1) qs('#a-type').value = typeOf(added.name); }), files = fb.files;
    qs('#a-url').addEventListener('change', function () { var u = this.value.trim(); if (!u) return; if (/youtu\.?be|vimeo|\/video/i.test(u)) qs('#a-type').value = 'video'; else if (/\.pdf(\?|$)/i.test(u)) qs('#a-type').value = 'pdf'; else if (!files.length) qs('#a-type').value = 'link'; });
    qs('#af').addEventListener('submit', function (e) {
      e.preventDefault(); var t = qs('#a-title').value.trim(), u = qs('#a-url').value.trim(), body = editor.body();
      qs('#a-title-msg').style.display = t ? 'none' : 'block'; var need = !u && !files.length && !body; qs('#a-need-msg').style.display = need ? 'block' : 'none'; if (!t || need) return;
      var btn = qs('#a-save'); btn.disabled = true; btn.textContent = '저장 중…';
      it.title = t; it.cat = qs('#a-cat').value; it.type = qs('#a-type').value; it.org = qs('#a-org').value.trim(); it.date = qs('#a-date').value.trim(); it.url = u; it.body = body; it.files = files; it.published = qs('#a-pub').checked;
      if (isNew) state.archive.items = (state.archive.items || []).concat([it]);
      saveJson('content/archive.json', state.archive, (isNew ? '아카이브 추가: ' : '아카이브 수정: ') + t).then(function () { afterSave(isNew ? '자료를 추가했습니다' : '자료를 고쳤습니다'); location.hash = '#archive'; }).catch(function (e2) { fail(e2); btn.disabled = false; btn.textContent = '저장'; });
    });
  }

  // ---------------------------------------------------------------- 홈 숫자
  function vStats() {
    return ensure('stats').then(function () {
      var s = state.stats;
      return fetch('assets/stats.live.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; }).then(function (live) {
        view.innerHTML = '<div class="adm-head"><h2>홈 숫자</h2></div><form class="form" id="sf" novalidate><div class="grid g2" style="gap:16px">' +
          '<div class="field"><label for="s-services">AI 교육 서비스 수</label><input id="s-services" type="number" min="0" value="' + esc(s.services) + '"></div>' +
          '<div class="field"><label for="s-univ">참여 대학 수</label><input id="s-univ" type="number" min="0" value="' + esc(s.universities) + '"></div>' +
          '<div class="field"><label for="s-comp">참여 에듀테크 기업 수</label><input id="s-comp" type="number" min="0" value="' + esc(s.companies) + '"></div>' +
          '<div class="field"><label for="s-courses">AI 결합 강좌 수</label><input id="s-courses" type="number" min="0" value="' + (s.courses == null ? '' : esc(s.courses)) + '" placeholder="비워 두면 포털 값 자동"><span class="hint">현재 포털 값: <strong>' + esc(live.courses != null ? Number(live.courses).toLocaleString('ko-KR') : '—') + '</strong> (' + esc(live.fetched_at || '') + ' 수집)</span></div>' +
          '<div class="field" style="grid-column:1/-1"><label for="s-basis">기준 설명 (홈 각주)</label><input id="s-basis" value="' + esc(s.basis || '') + '"></div></div>' +
          '<div class="acts" style="display:flex;gap:8px"><button class="btn" type="submit" id="s-save">저장</button></div><p class="small muted">참여 기관 수는 대학 + 기업으로 홈에 표시됩니다. 강좌 수를 직접 넣으면 포털 자동값 대신 그 값을 씁니다.</p></form>';
        qs('#sf').addEventListener('submit', function (e) {
          e.preventDefault(); var btn = qs('#s-save'); btn.disabled = true; btn.textContent = '저장 중…';
          function num(id) { var v = qs(id).value.trim(); return v === '' ? null : Number(v); }
          s.services = num('#s-services'); s.universities = num('#s-univ'); s.companies = num('#s-comp'); s.courses = num('#s-courses'); s.basis = qs('#s-basis').value.trim();
          saveJson('assets/stats.json', s, '홈 숫자 수정').then(function () { afterSave('홈 숫자를 저장했습니다'); }).catch(fail).then(function () { btn.disabled = false; btn.textContent = '저장'; });
        });
      });
    });
  }

  // ---------------------------------------------------------------- 자동 연동 글 숨기기
  function vFeeds() {
    return ensure('hidden').then(function () {
      var H = state.hidden; ['events', 'press', 'videos', 'unn'].forEach(function (k) { H[k] = (H[k] || []).map(String); });
      return Promise.all(['events', 'press', 'unn', 'videos'].map(function (k) { return fetch('assets/' + k + '.live.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : { items: [] }; }).catch(function () { return { items: [] }; }); })).then(function (feeds) {
        var secs = [['events', '행사', 'AI교육확산센터 소식의 [KELI] 글'], ['press', '보도자료', '한림대 보도자료 중 KELI·켈리'], ['unn', '언론 보도', '한국대학신문에서 「한림대 KELI」·「한림대 켈리」 검색(제목·요약·사진만 표시, 원문 연결)'], ['videos', '영상', '한림대 유튜브 KELI·켈리 + 관련 영상']];
        view.innerHTML = '<div class="adm-head"><h2>자동 연동 글</h2><button class="btn ghost sm" type="button" id="f-dispatch">지금 다시 수집</button></div><p class="muted small" style="margin:0 0 8px">자동으로 가져온 글은 여기서 쓰거나 고칠 수 없고, 원하지 않는 글만 숨길 수 있습니다. 숨김/보이기는 저장 즉시 커밋됩니다.</p>' +
          secs.map(function (sct, i) { var items = feeds[i].items || []; return '<h3 style="margin:24px 0 4px;font-size:18px">' + sct[1] + ' <span class="muted" style="font-weight:500;font-size:14px">' + items.length + '건 · ' + esc(feeds[i].fetched_at || '') + ' 수집</span></h3><p class="small muted" style="margin:0 0 8px">' + sct[2] + '</p>' + (items.length ? '<div class="list">' + items.map(function (it) { var id = String(it.id), off = H[sct[0]].indexOf(id) > -1; return '<div class="li' + (off ? ' off' : '') + '"><span>' + (off ? '<span class="badge soon" style="margin-right:8px">숨김</span>' : '') + '<span class="t">' + esc(it.title) + '</span><br><span class="m">' + esc(it.when || it.date || it.published || it.published_text || '') + '</span></span><span class="acts"><a class="btn ghost xs" href="' + esc(it.url) + '" target="_blank" rel="noopener">원문</a><button class="btn ghost xs" type="button" data-k="' + sct[0] + '" data-id="' + esc(id) + '">' + (off ? '보이기' : '숨기기') + '</button></span></div>'; }).join('') + '</div>' : '<p class="small muted">수집된 글이 없습니다</p>'); }).join('');
        qsa('[data-k]', view).forEach(function (b) { b.addEventListener('click', function () { var k = b.getAttribute('data-k'), id = b.getAttribute('data-id'); var i = H[k].indexOf(id); if (i > -1) H[k].splice(i, 1); else H[k].push(id); b.disabled = true; saveJson('content/hidden.json', H, (i > -1 ? '자동 연동 글 보이기: ' : '자동 연동 글 숨기기: ') + k + ' ' + id).then(function () { afterSave(i > -1 ? '다시 보이게 했습니다' : '숨겼습니다'); route(); }).catch(function (e) { fail(e); b.disabled = false; }); }); });
        qs('#f-dispatch').addEventListener('click', function () { dispatch().then(function () { afterSave('다시 수집을 시작했습니다'); }).catch(function (e) { toast('실행 실패: ' + e.message, 6000); }); });
      });
    });
  }

  // ---------------------------------------------------------------- 도움말
  function vHelp() {
    view.innerHTML = '<div class="adm-head"><h2>도움말</h2></div>' +
      '<div class="card"><span class="k">어떻게 반영되나</span><p>저장 → GitHub 저장소(' + esc(CFG.repo) + ')에 커밋 → GitHub Actions 가 사이트를 다시 만들어 배포(1~2분). 위의 배포 상태 줄이 "반영 완료"가 되면 사이트 보기로 확인합니다. 행사·보도자료·영상은 배포할 때마다 다시 수집되고, 매일 새벽 3시 17분에도 자동으로 돌아갑니다.</p></div>' +
      '<div class="card" style="margin-top:16px"><span class="k">글쓰기 요령</span><ul style="padding-left:20px;margin:8px 0 0"><li>편집기에서 Enter 는 문단, Shift+Enter 는 줄바꿈입니다. 긴 글도 됩니다(길이 제한 없음).</li><li>다른 곳에서 만든 HTML 이 있으면 "HTML" 을 눌러 소스를 통째로 붙여 넣으세요(표·iframe 가능).</li><li>이미지는 "이미지" 버튼으로 올리면 글 안에 들어갑니다. 첨부파일은 글 아래 목록으로 나옵니다.</li><li>저장 전 "미리보기"로 사이트 모양 그대로 확인할 수 있습니다. 쓰다 만 글은 이 브라우저에 임시 보관됩니다.</li><li>사이트의 모든 문장은 저장 후 자동으로 "단어·어절·마침표" 줄바꿈 규칙이 적용됩니다.</li></ul></div>' +
      '<div class="card" style="margin-top:16px"><span class="k">문제가 생기면</span><dl class="kv" style="margin:8px 0 0"><dt>저장 실패 401/403</dt><dd>토큰이 만료되었거나 권한이 부족합니다. 로그아웃 후 새 토큰(Contents: Read and write, Actions: Read and write)으로 다시 들어오세요.</dd><dt>저장 실패 409</dt><dd>다른 사람이 같은 파일을 먼저 저장했습니다. 한 번 더 저장하면 됩니다.</dd><dt>배포 실패</dt><dd>배포 기록 링크에서 빨간 단계를 열어 보고 사무국(033-248-3246)에 알려 주세요. 이전 버전은 그대로 서비스됩니다.</dd><dt>되돌리기</dt><dd>GitHub 저장소 → content 폴더 → 파일 → History 에서 이전 버전을 볼 수 있습니다.</dd></dl></div>' +
      '<div class="card" style="margin-top:16px"><span class="k">로그인 정보</span><p>' + (user ? 'GitHub 계정 <strong>' + esc(user.login) + '</strong> 으로 들어와 있습니다.' : '') + ' 토큰은 이 브라우저에만 저장됩니다. 공용 PC 에서는 로그아웃 하세요.</p><button class="btn ghost sm" type="button" id="hp-logout">로그아웃</button></div>';
    qs('#hp-logout').addEventListener('click', logout);
  }

  // ---------------------------------------------------------------- 로그인 흐름
  function showLogin(msg) { qs('#adm-login').hidden = false; qs('#adm-app').hidden = true; qs('#adm-logout').hidden = true; if (msg) { var m = qs('#tok-msg'); m.textContent = msg; m.style.display = 'block'; } }
  function enter() {
    return gh('/user').then(function (u) { user = u; return gh('/repos/' + CFG.repo); }).then(function (r) {
      if (!(r.permissions && (r.permissions.push || r.permissions.admin || r.permissions.maintain))) throw new Error('이 토큰으로는 ' + CFG.repo + ' 저장소에 쓸 수 없습니다. 토큰의 Repository access 와 Contents 권한을 확인하세요');
      qs('#adm-login').hidden = true; qs('#adm-app').hidden = false; qs('#adm-logout').hidden = false;
      checkDeploy(false); route();
    });
  }
  function logout() { clearToken(); token = null; user = null; state = { notices: null, archive: null, hidden: null, stats: null, sha: {} }; showLogin(''); location.hash = ''; }
  qs('#adm-logout').addEventListener('click', logout);
  qs('#login-form').addEventListener('submit', function (e) {
    e.preventDefault(); var t = qs('#tok').value.trim(); var m = qs('#tok-msg'); m.style.display = 'none'; if (!t) { m.textContent = '토큰을 붙여 넣어 주세요'; m.style.display = 'block'; return; }
    var btn = qs('#tok-go'); btn.disabled = true; btn.textContent = '확인 중…'; token = t;
    enter().then(function () { saveToken(t, qs('#tok-keep').checked); qs('#tok').value = ''; toast(user.login + ' 님, 어서 오세요'); }).catch(function (err) { token = null; showLogin(err.status === 401 ? '토큰이 올바르지 않거나 만료되었습니다' : err.message); }).then(function () { btn.disabled = false; btn.textContent = '들어가기'; });
  });
  qs('#tok-help').addEventListener('click', function (e) { e.preventDefault(); qs('#help-card').scrollIntoView({ behavior: 'smooth' }); });

  var saved = loadToken();
  if (saved) { token = saved; enter().catch(function (err) { token = null; clearToken(); showLogin(err.status === 401 ? '저장된 토큰이 만료되었습니다. 새 토큰으로 들어오세요' : err.message); }); }
  else showLogin('');
})();
