// ---------------------------------------------------------------- 방문 통계 수집 (관리자 서버 /api/hit)
// 쿠키·개인정보 없이 "어느 페이지를, 어디서 와서, 어떤 기기로" 봤는지만 보냅니다. IP 는 서버에서 날마다 바뀌는 해시로만 셉니다.
// 끄는 방법: 브라우저 "추적 안 함(DNT)" 설정, 또는 관리자 화면 → 방문 통계 → "내 방문 집계 제외".
(function () {
  var API = window.KELI_API; if (!API) return;
  try { if (localStorage.getItem('keli_no_track') === '1') return; } catch (e) {}
  if (navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.webdriver) return;
  if (/\/admin\.html$/.test(location.pathname)) return;
  function send(d) {
    try {
      var body = JSON.stringify(d);
      if (navigator.sendBeacon) { navigator.sendBeacon(API + '/api/hit', new Blob([body], { type: 'text/plain' })); return; }   // text/plain → 사전 요청(preflight) 없음
      fetch(API + '/api/hit', { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: body, keepalive: true }).catch(function () {});
    } catch (e) {}
  }
  var q = new URLSearchParams(location.search);
  send({ t: 'pv', p: location.pathname, ti: (document.title || '').split(' | ')[0].slice(0, 120), r: document.referrer || '', src: q.get('utm_source') || '', med: q.get('utm_medium') || '', cmp: q.get('utm_campaign') || '', l: document.documentElement.lang || 'ko' });
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null; if (!a || !a.href || /^(mailto|tel|javascript):/.test(a.href)) return;
    var ext = a.host && a.host !== location.host;
    var file = /\/content\/files\//.test(a.href) || /\.(pdf|hwpx?|docx?|pptx?|xlsx?|zip|mp4|png|jpe?g|gif)(\?|$)/i.test(a.pathname || '');
    if (ext || file) send({ t: 'click', p: location.pathname, x: a.href.slice(0, 300) });
  }, true);
})();
