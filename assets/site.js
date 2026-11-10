
(function(){
  var qs=function(s,r){return (r||document).querySelector(s)}, qsa=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
  // mobile nav
  var b=qs('.burger'), m=qs('.mnav');
  if(b&&m){ b.addEventListener('click',function(){ var o=m.getAttribute('data-open')==='1'; m.setAttribute('data-open',o?'0':'1'); b.setAttribute('aria-expanded',String(!o)); }); }
  // generic tab filters: [data-tabs] buttons filter [data-items] children by data-key
  qsa('[data-tabs]').forEach(function(bar){
    var target=qs('[data-items="'+bar.getAttribute('data-tabs')+'"]'); if(!target) return;
    var count=qs('[data-count="'+bar.getAttribute('data-tabs')+'"]');
    function apply(key){
      var n=0; qsa('[data-key]',target).forEach(function(el){ var on=(key==='all'||el.getAttribute('data-key')===key); el.hidden=!on; if(on)n++; });
      qsa('.tab',bar).forEach(function(t){ t.setAttribute('aria-pressed',String(t.getAttribute('data-val')===key)); });
      if(count) count.textContent=n+'개';
    }
    qsa('.tab',bar).forEach(function(t){ t.addEventListener('click',function(){ apply(t.getAttribute('data-val')); }); });
    // 처음 열면 항상 "전체". 주소 뒤에 #분류 가 붙어 있을 때만 그 분류로(전체 메뉴의 하위 항목). 지난번 선택은 기억하지 않음(사무국 결정 2026-11-03)
    var init='all';
    var h=''; try{ h=decodeURIComponent(location.hash.replace('#','')); }catch(e){ h=location.hash.replace('#',''); }
    if(h && qs('.tab[data-val="'+h+'"]',bar)) init=h;
    apply(init);
  });
  // forms (demo: validate, show receipt)
  function validate(f){ var ok=true; qsa('.field',f).forEach(function(fd){ var inp=qs('input,select,textarea',fd); if(!inp) return; var bad=false; if(inp.required && !inp.value.trim()) bad=true; if(inp.type==='email' && inp.value && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(inp.value)) bad=true; fd.classList.toggle('err',bad); if(bad) ok=false; }); var ag=qs('input[type=checkbox][required]',f); if(ag&&!ag.checked){ ok=false; ag.focus(); } return ok; }
  qsa('form[data-demo]').forEach(function(f){
    f.addEventListener('submit',function(e){ e.preventDefault(); if(!validate(f)) return; var d=qs('.done',f); var id=f.getAttribute('data-demo').toUpperCase()+'-'+new Date().toISOString().slice(0,10).replace(/-/g,'')+'-'+String(Math.floor(Math.random()*900)+100); if(d){ var c=qs('code',d); if(c) c.textContent=id; d.setAttribute('data-show','1'); d.scrollIntoView({block:'nearest'}); } var sub=qs('button[type=submit]',f); if(sub){ sub.disabled=true; sub.textContent='접수되었습니다'; } });
  });
  // 도입·참여 문의: 관리자 서버(/api/contact)로 보냄 → 사무국 메일(contact@keliedu.org) 전달 + 관리자 문의함 보관. 서버가 안 되면 메일 앱으로 넘김
  qsa('form[data-inquiry]').forEach(function(f){
    f.addEventListener('submit',function(e){ e.preventDefault(); if(!validate(f)) return;
      var sub=qs('button[type=submit]',f), done=qs('.done',f), fail=qs('.fail',f); if(fail){ fail.hidden=true; fail.textContent=''; }
      function val(n){ var el=f.elements[n]; return el?String(el.value||'').trim():''; }
      var sv=qsa('input[name="services"]:checked',f).map(function(c){ return c.value; });
      var data={ type: val('type'), org: val('org'), name: val('name'), email: val('email'), tel: val('tel'), services: sv, course: val('course'), body: val('body'), hp: val('hp'), page: location.pathname, lang: document.documentElement.lang||'ko' };
      function mailto(){ var t=['참여 유형: '+(qs('#f-type option:checked',f)||{}).textContent,'기관명: '+data.org,'담당자: '+data.name,'이메일: '+data.email,'연락처: '+(data.tel||'-'),'관심 서비스: '+(sv.join(', ')||'-'),'적용 교과목: '+(data.course||'-'),'','문의 내용:',data.body||'-'].join('\n'); location.href='mailto:contact@keliedu.org?subject='+encodeURIComponent('[서비스 도입 문의] '+data.org+' · '+data.name)+'&body='+encodeURIComponent(t); }
      function bad(msg){ if(sub){ sub.disabled=false; sub.textContent='문의 보내기'; } if(fail){ fail.hidden=false; fail.innerHTML=msg; } }
      if(!window.KELI_API){ mailto(); return; }
      if(sub){ sub.disabled=true; sub.textContent='보내는 중…'; }
      fetch(window.KELI_API+'/api/contact',{ method:'POST', headers:{'Content-Type':'text/plain'}, body: JSON.stringify(data) }).then(function(r){ return r.json().catch(function(){ return {}; }).then(function(j){ return {ok:r.ok, st:r.status, j:j}; }); }).then(function(x){
        if(x.st===404||x.st===401){ if(sub){ sub.disabled=false; sub.textContent='문의 보내기'; } mailto(); return; }   // 서버가 아직 옛 코드 → 메일 앱으로
        if(!x.ok||!x.j.ok){ bad((x.j&&x.j.error?x.j.error:'보내지 못했습니다.')+' <a href="mailto:contact@keliedu.org">contact@keliedu.org</a> 로 직접 보내 주셔도 됩니다.'); return; }
        if(done){ var c=qs('code',done); if(c) c.textContent=x.j.ref; done.setAttribute('data-show','1'); done.scrollIntoView({block:'nearest'}); }
        if(sub) sub.textContent='접수되었습니다';
        try{ if(navigator.sendBeacon) navigator.sendBeacon(window.KELI_API+'/api/hit', new Blob([JSON.stringify({t:'click',p:location.pathname,x:'inquiry:sent'})],{type:'text/plain'})); }catch(e){}
      }).catch(function(){ bad('네트워크 문제로 보내지 못했습니다. <a href="#" data-mailto>메일 앱으로 보내기</a> 또는 contact@keliedu.org 로 보내 주세요.'); var a=qs('[data-mailto]',f); if(a) a.addEventListener('click',function(ev){ ev.preventDefault(); mailto(); }); });
    });
  });
  // prefill service from ?service= or #svc=
  var p=new URLSearchParams(location.search); var svc=p.get('service');
  function nrm(t){ return String(t||'').toLowerCase().replace(/[^a-z0-9가-힣]/g,''); }
  if(svc){ var ns=nrm(svc); qsa('input[name="services"]').forEach(function(c){ if(c.value===svc||nrm(c.value).indexOf(ns)===0) c.checked=true; }); }
  // copy buttons
  qsa('[data-copy]').forEach(function(btn){ btn.addEventListener('click',function(){ var t=btn.getAttribute('data-copy'); function ok(){ btn.textContent='복사됨'; setTimeout(function(){btn.textContent='복사';},1500);} if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(t).then(ok,function(){ fallback(); }); } else fallback(); function fallback(){ var s=document.createElement('textarea'); s.value=t; document.body.appendChild(s); s.select(); try{document.execCommand('copy'); ok();}catch(e){} document.body.removeChild(s);} }); });
  // stats: admin-entered numbers (assets/stats.json) + live course count (assets/stats.live.json) + count-up
  (function(){
    if(!qsa('[data-stat]').length) return;
    function fmt(n){ return Number(n).toLocaleString('ko-KR'); }
    function setStat(k,v){ qsa('[data-stat="'+k+'"]').forEach(function(e){ if(e.hasAttribute('data-count')) e.setAttribute('data-count',String(v)); else e.textContent=(typeof v==='number')?fmt(v):String(v); }); }
    function countUp(){
      var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      qsa('[data-count]').forEach(function(el){
        var to=parseInt(el.getAttribute('data-count'),10)||0;
        if(reduce||!('IntersectionObserver' in window)){ el.textContent=fmt(to); return; }
        el.textContent='0';
        var io=new IntersectionObserver(function(en){ if(!en[0].isIntersecting) return; io.disconnect();
          var t0=null, dur=1400;
          function step(ts){ if(!t0) t0=ts; var p=Math.min(1,(ts-t0)/dur), e=1-Math.pow(1-p,3); el.textContent=fmt(Math.round(to*e)); if(p<1) requestAnimationFrame(step); }
          requestAnimationFrame(step); },{threshold:0.35});
        io.observe(el);
      });
    }
    function load(u){ return fetch(u,{cache:'no-store'}).then(function(r){ if(!r.ok) throw new Error(u); return r.json(); }); }
    var manual=null;
    if(location.protocol==='file:'){ countUp(); return; }   // zip을 로컬에서 열었을 때는 내장값으로
    load('assets/stats.json').then(function(s){ manual=s;
      if(s.services!=null) setStat('services',s.services);
      if(s.universities!=null) setStat('universities',s.universities);
      if(s.companies!=null) setStat('companies',s.companies);
      if(s.universities!=null&&s.companies!=null) setStat('partners',Number(s.universities)+Number(s.companies));
      if(s.courses!=null&&s.courses!==''){ setStat('courses',s.courses); setStat('courses_note','사무국 입력값'); }
    }).catch(function(){}).then(function(){ return load('assets/stats.live.json'); }).then(function(l){
      if(l&&l.courses){ setStat('courses_live',l.courses); setStat('courses_date',l.fetched_at||''); if(!(manual&&manual.courses!=null&&manual.courses!=='')){ setStat('courses',l.courses); setStat('courses_note','한림 AI 교육 포털 '+(l.fetched_at||'')+' 기준'); } }
    }).catch(function(){}).then(function(){ return load('assets/services.live.json'); }).then(function(v){
      if(v&&v.count&&!(manual&&manual.services!=null&&manual.services!=='')){ setStat('services',v.count); setStat('services_note','운영 중 '+(v.live_count||'')+' · 오픈 예정 '+(v.coming_count||'')+' · 포털 '+String(v.fetched_at||'').replace(/ /g,'\u00a0')+' 기준'); }
    }).catch(function(){}).then(countUp);
  })();
  // 관리자가 숨긴 자동 연동 글(content/hidden.json → window.KELI_HIDDEN)은 다시 그릴 때도 뺀다
  function hid(kind, items){ var h=((window.KELI_HIDDEN||{})[kind])||[]; return items.filter(function(it){ return h.indexOf(String(it.id))<0; }); }
  // 관심 서비스 체크 목록: 포털 피드(assets/services.live.json)로 다시 그림 (체크 상태 유지)
  (function(){
    var box=qs('#svc-opts'); if(!box||location.protocol==='file:') return;
    fetch('assets/services.live.json',{cache:'no-store'}).then(function(r){ return r.ok?r.json():null; }).then(function(d){
      if(!d||!d.items||!d.items.length) return; var items=hid('services', d.items); var cats=d.categories||[];
      var checked={}; qsa('input[name=services]:checked', box).forEach(function(i){ checked[i.value]=1; });
      var html=''; cats.forEach(function(c){ var its=items.filter(function(i){ return i.category===c; }); if(!its.length) return;
        html+='<div class="chipgrp"><span class="gk">'+esc(c)+'</span><div class="chips">'+its.map(function(i){ return '<label class="chip sel"><input type="checkbox" name="services" value="'+esc(i.name)+'"'+(checked[i.name]?' checked':'')+'> '+esc(i.name)+(i.status==='coming_soon'?' <small>오픈 예정</small>':'')+'</label>'; }).join('')+'</div></div>'; });
      if(html){ box.innerHTML=html; var src=qs('#svc-src'); if(src&&d.fetched_at) src.textContent='목록은 한림 AI 교육 포털(ai.hallym.ac.kr/hallym-ai)에서 매일 자동으로 가져옵니다 · '+d.fetched_at+' 기준.'; }
    }).catch(function(){});
  })();
  // events feed: AI교육확산센터 [KELI] 글 (assets/events.live.json) → [data-events] 다시 그리기
  (function(){
    var boxes=qsa('[data-events]'); if(!boxes.length||location.protocol==='file:') return;
    function esc(s){ return String(s||'').replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
    function status(it){ var now=new Date(Date.now()+9*3600e3).toISOString().slice(0,16); if(it.start&&now<it.start) return ['upcoming','예정']; if(it.end&&now<=it.end) return ['live','진행 중']; return ['ended','종료']; }
    function href(it,pages){ return pages.indexOf(String(it.id))>-1 ? 'event-'+it.id+'.html' : it.url; }
    function ext(it,pages){ return pages.indexOf(String(it.id))>-1 ? '' : ' target="_blank" rel="noopener"'; }
    function badge(it){ var s=status(it); return '<span class="badge '+(s[0]==='upcoming'?'live':'')+'">'+s[1]+'</span>'; }
    function d(it){ return (it.start||'').slice(0,10).replace(/-/g,'.'); }
    function th(it,c){ return it.thumb?'<span class="'+c+'"><img src="'+esc(it.thumb)+'" alt="" loading="lazy"></span>':''; }
    function card(it,p){ return '<a class="card card-ev" href="'+href(it,p)+'"'+ext(it,p)+'>'+th(it,'card-thumb')+'<div class="row"><span class="k">'+esc((it.badges||['행사'])[0])+'</span>'+badge(it)+'</div><h3>'+esc(it.title)+'</h3><p>'+esc(it.when)+'<br>'+esc(it.place)+'</p><span class="more">자세히 보기</span></a>'; }
    function row(it,p){ return '<a class="li li-ev" href="'+href(it,p)+'"'+ext(it,p)+'>'+th(it,'li-thumb')+'<span><span class="m">'+esc((it.badges||['행사'])[0])+' · '+esc(it.place)+'</span><br><span class="t">'+esc(it.title)+'</span><br><span class="m">'+esc(it.when)+'</span></span><span class="d">'+d(it)+' '+badge(it)+'</span></a>'; }
    function short(it,p){ return '<a class="li" href="'+href(it,p)+'"'+ext(it,p)+'><span><span class="m">'+esc((it.badges||['행사'])[0])+'</span><br><span class="t">'+esc(it.title)+'</span></span><span class="d">'+d(it)+'</span></a>'; }
    fetch('assets/events.live.json',{cache:'no-store'}).then(function(r){ if(!r.ok) throw 0; return r.json(); }).then(function(f){
      var items=hid('events', f.items||[]); if(!items.length) return;
      boxes.forEach(function(b){ var p=(b.getAttribute('data-pages')||'').split(','); var kind=b.getAttribute('data-events');
        if(kind==='home') b.innerHTML=card(items[0],p);
        else if(kind==='rows') b.innerHTML=items.slice(0,3).map(function(it){ return short(it,p); }).join('');
        else if(kind==='list') b.innerHTML=items.map(function(it){ return row(it,p); }).join('');
      });
      var up=items.some(function(it){ return status(it)[0]!=='ended'; }); var em=qs('[data-ev-empty]'); if(em) em.hidden=up;
      var fd=qs('[data-feed-date]'); if(fd&&f.fetched_at) fd.textContent=f.fetched_at;
      qsa('[data-ev-status]').forEach(function(el){ var id=(el.closest('[data-ev]')||{}).getAttribute? el.closest('[data-ev]').getAttribute('data-ev'):null; var it=items.filter(function(x){ return String(x.id)===id; })[0]; if(it){ var s=status(it); el.textContent=s[1]; el.className='badge '+(s[0]==='upcoming'?'live':''); } });
    }).catch(function(){});
  })();
  // press feed: 한림대 보도자료(press.live.json) + 한국대학신문 기사(unn.live.json) 병합 → [data-press] 다시 그리기
  (function(){
    var boxes=qsa('[data-press]'); if(!boxes.length||location.protocol==='file:') return;
    function esc(s){ return String(s||'').replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
    function href(it,p){ return it.src==='unn' ? it.url : (p.indexOf(String(it.id))>-1 ? 'press-'+it.id+'.html' : it.url); }
    function ext(it,p){ return (it.src==='unn' || p.indexOf(String(it.id))<0) ? ' target="_blank" rel="noopener"' : ''; }
    function th(it){ return it.thumb ? '<span class="li-thumb"><img src="'+esc(it.thumb)+'" alt="" loading="lazy"></span>' : '<span class="li-thumb li-thumb-ph"><span>'+(it.src==='unn'?'한국대학신문':'한림대학교')+'</span></span>'; }
    function meta(it){ return it.src==='unn' ? '언론 보도 · 한국대학신문'+(it.reporter?' · '+esc(it.reporter):'') : '보도자료 · 한림대학교'+(it.category?' · '+esc(it.category):''); }
    function row(it,p,sum){ return '<a class="li li-ev" href="'+href(it,p)+'"'+ext(it,p)+'>'+th(it)+'<span><span class="m">'+meta(it)+'</span><br><span class="t">'+esc(it.title)+'</span>'+(sum&&it.summary?'<br><span class="m">'+esc(it.summary.slice(0,90))+'</span>':'')+'</span><span class="d">'+esc(it.date||'')+'</span></a>'; }
    function load(u){ return fetch(u,{cache:'no-store'}).then(function(r){ return r.ok ? r.json() : {items:[]}; }).catch(function(){ return {items:[]}; }); }
    Promise.all([load('assets/press.live.json'), load('assets/unn.live.json')]).then(function(fs){
      var a=hid('press', fs[0].items||[]), b=hid('unn', (fs[1].items||[]).map(function(x){ x.src='unn'; return x; }));
      var items=a.concat(b).sort(function(x,y){ return (y.date||'').localeCompare(x.date||''); }); if(!items.length) return;
      boxes.forEach(function(bx){ var p=(bx.getAttribute('data-pages')||'').split(','); var kind=bx.getAttribute('data-press');
        if(kind==='rows') bx.innerHTML=items.slice(0,3).map(function(it){ return row(it,p,false); }).join('');
        else if(kind==='list') bx.innerHTML=items.map(function(it){ return row(it,p,true); }).join('');
      });
      var fd=qs('[data-press-date]'); if(fd&&fs[0].fetched_at) fd.textContent=fs[0].fetched_at;
    });
  })();
  // videos: 클릭하면 그 자리에서 YouTube 재생 (처음엔 썸네일만 → 데이터 절약)
  function wirePlay(root){ qsa('.vid-play', root||document).forEach(function(b){ if(b._wired) return; b._wired=true; b.addEventListener('click',function(){ var v=b.closest('.vid'); var f=document.createElement('iframe'); f.src=v.getAttribute('data-embed'); f.title=b.getAttribute('aria-label')||'영상'; f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share'; f.setAttribute('allowfullscreen',''); b.replaceWith(f); }); }); }
  wirePlay();
  (function(){
    var boxes=qsa('[data-videos]'); if(!boxes.length||location.protocol==='file:') return;
    function esc(s){ return String(s||'').replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
    function card(v){ var meta=[(v.group==='keli'?'KELI 영상':'HAI · 소프트랩'), v.published||v.published_text||'', v.views||''].filter(Boolean).join(' · ');
      return '<div class="vid" data-vid="'+esc(v.id)+'" data-embed="'+esc(v.embed)+'"><button type="button" class="vid-play" aria-label="'+esc(v.title)+' 재생"><img src="'+esc(v.thumb)+'" alt="" loading="lazy"><span class="play"></span>'+(v.length?'<span class="len">'+esc(v.length)+'</span>':'')+'</button><div class="vid-body"><span class="m">'+esc(meta)+'</span>'+(v.is_live_recording?'<span class="badge" style="margin-left:6px">실시간 녹화</span>':'')+'<strong class="t">'+esc(v.title)+'</strong><a class="more" href="'+esc(v.url)+'" target="_blank" rel="noopener">YouTube에서 보기</a></div></div>'; }
    fetch('assets/videos.live.json',{cache:'no-store'}).then(function(r){ if(!r.ok) throw 0; return r.json(); }).then(function(f){
      var items=hid('videos', f.items||[]); if(!items.length) return; var keli=items.filter(function(v){ return v.group==='keli'; }), rel=items.filter(function(v){ return v.group!=='keli'; });
      boxes.forEach(function(b){ var k=b.getAttribute('data-videos');
        if(k==='hub') b.innerHTML=keli.concat(rel).slice(0,2).map(card).join('');
        else if(k==='keli') b.innerHTML=keli.map(card).join('')||'<div class="empty">아직 KELI 영상이 없습니다.</div>';
        else if(k==='related') b.innerHTML=rel.map(card).join('');
      });
      var fd=qs('[data-video-date]'); if(fd&&f.fetched_at) fd.textContent=f.fetched_at;
      wirePlay();
    }).catch(function(){});
  })();
  // mega menu: 상단 메뉴에 올리거나(마우스) 누르면(터치) 전체 메뉴 펼침 (펼침 애니메이션 + 뒤 배경 어둡게)
  (function(){
    var mega=qs('#mega'), hdr=qs('.hdr'), dim=qs('#dim'); if(!mega||!hdr) return;
    var navLinks=qsa('.nav a[data-menu]'), timer=null;
    function isOpen(){ return mega.classList.contains('open'); }
    function open(key){ clearTimeout(timer); mega.classList.add('open'); mega.setAttribute('aria-hidden','false'); if(dim) dim.classList.add('on'); qsa('.mega-col',mega).forEach(function(c){ c.classList.toggle('hot', c.getAttribute('data-menu')===key); }); navLinks.forEach(function(a){ a.setAttribute('aria-expanded', a.getAttribute('data-menu')===key?'true':'false'); }); }
    function closeNow(){ mega.classList.remove('open'); mega.setAttribute('aria-hidden','true'); if(dim) dim.classList.remove('on'); navLinks.forEach(function(a){ a.setAttribute('aria-expanded','false'); }); }
    function close(){ clearTimeout(timer); timer=setTimeout(closeNow,160); }
    navLinks.forEach(function(a){
      a.setAttribute('aria-haspopup','true'); a.setAttribute('aria-expanded','false');
      a.addEventListener('mouseenter',function(){ open(a.getAttribute('data-menu')); });
      a.addEventListener('focus',function(){ open(a.getAttribute('data-menu')); });
      a.addEventListener('click',function(e){ if(window.innerWidth<=860) return; var k=a.getAttribute('data-menu'); var hot=qs('.mega-col.hot',mega); if(!isOpen()||!hot||hot.getAttribute('data-menu')!==k){ e.preventDefault(); open(k); } });
    });
    qs('.nav').addEventListener('mouseenter', function(){ var cur=qs('.nav a.on')||navLinks[0]; if(!isOpen()) open(cur?cur.getAttribute('data-menu'):null); });
    qs('.nav').addEventListener('mouseleave', close); mega.addEventListener('mouseenter', function(){ clearTimeout(timer); }); mega.addEventListener('mouseleave', close);
    if(dim){ dim.addEventListener('mouseenter', close); dim.addEventListener('click', closeNow); }
    hdr.addEventListener('focusout', function(e){ if(!hdr.contains(e.relatedTarget)) close(); });
    document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeNow(); });
    document.addEventListener('click', function(e){ if(!hdr.contains(e.target)) closeNow(); });
  })();
  // home hero: 점 파도 (prefers-reduced-motion이면 정지 화면 한 장만)
  (function(){
    var cv=qs('#hero-wave'); if(!cv||!cv.getContext) return;
    var ctx=cv.getContext('2d'), w, h, t=0, cols=72, rows=24, mx=0, sx=0, on=true;
    var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function resize(){ var dpr=Math.min(2, window.devicePixelRatio||1); w=cv.clientWidth; h=cv.clientHeight; cv.width=w*dpr; cv.height=h*dpr; ctx.setTransform(dpr,0,0,dpr,0,0); if(w<700){ cols=44; rows=18; } else { cols=72; rows=24; } }
    function frame(){
      sx+=(mx-sx)*.03; t+=.016; ctx.clearRect(0,0,w,h);
      var i,j,cx=w/2;
      var depth=w<700?.42:.60; for(j=0;j<rows;j++){ var zr=j/(rows-1), spread=1.25-.62*zr, baseY=h*.98-zr*h*depth;
        for(i=0;i<cols;i++){ var x=(i/(cols-1)-.5)*2; var yv=Math.sin(x*3.1+t*1.1+sx)*Math.cos(zr*5.2-t*.9)*.5+Math.sin(x*7-t*.7)*.18; var amp=h*.11*(1-.55*zr);
          var X=cx+x*w*.5*spread, Y=baseY-yv*amp, r=.9+1.5*(1-zr), k=Math.max(0,Math.min(1,(yv+.7)/1.4));
          ctx.fillStyle='rgba('+Math.round(205-194*k)+','+Math.round(222-130*k)+',255,'+((.25+.75*k)*(1-.55*zr)).toFixed(3)+')'; ctx.beginPath(); ctx.arc(X,Y,r,0,6.283); ctx.fill(); } }
    }
    resize(); frame();
    window.addEventListener('resize', function(){ resize(); frame(); });
    if(reduce) return;
    window.addEventListener('mousemove', function(e){ mx=(e.clientX/window.innerWidth-.5)*2; }, {passive:true});
    if('IntersectionObserver' in window){ new IntersectionObserver(function(es){ on=es[0].isIntersecting; },{threshold:.02}).observe(cv); }
    document.addEventListener('visibilitychange', function(){ if(!document.hidden) on=true; });
    (function loop(){ if(on&&!document.hidden) frame(); requestAnimationFrame(loop); })();
  })();
  // search overlay: 검색 아이콘을 누르면 페이지를 떠나지 않고 팝업으로 검색 (assets/search.json)
  (function(){
    var triggers=qsa('a[href="search.html"]'); if(!triggers.length||location.protocol==='file:') return;
    var box=null, data=null, inp, list, cnt;
    function esc(t){ return String(t||'').replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
    function build(){
      box=document.createElement('div'); box.className='srch'; box.setAttribute('role','dialog'); box.setAttribute('aria-modal','true'); box.setAttribute('aria-label','검색');
      box.innerHTML='<div class="srch-back"></div><div class="srch-box"><div class="srch-head"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg><input type="search" placeholder="무엇을 찾으세요? 예) 수학, 진단평가, 심포지엄" aria-label="검색어" autocomplete="off"><button type="button" class="srch-x" aria-label="닫기">✕</button></div><div class="srch-cnt"></div><div class="srch-list"></div><div class="srch-foot">Enter 첫 결과로 이동 · Esc 닫기 · <a href="search.html">검색 페이지로</a></div></div>';
      document.body.appendChild(box); inp=qs('input',box); list=qs('.srch-list',box); cnt=qs('.srch-cnt',box);
      qs('.srch-back',box).addEventListener('click', hide); qs('.srch-x',box).addEventListener('click', hide);
      inp.addEventListener('input', run); inp.addEventListener('keydown', function(e){ if(e.key==='Enter'){ var f=qs('a',list); if(f) location.href=f.getAttribute('href'); } });
    }
    function show(){ if(!box) build(); box.classList.add('on'); document.body.classList.add('noscroll'); setTimeout(function(){ inp.focus(); },50); if(!data){ fetch('assets/search.json',{cache:'no-store'}).then(function(r){ return r.json(); }).then(function(d){ data=d; run(); }).catch(function(){ cnt.textContent='검색 목록을 불러오지 못했습니다. 검색 페이지로 이동해 주세요.'; }); } else run(); }
    function hide(){ if(box){ box.classList.remove('on'); document.body.classList.remove('noscroll'); } }
    function run(){ if(!data) return; var v=inp.value.trim().toLowerCase(); if(!v){ list.innerHTML=''; cnt.textContent='Marketplace · 소식 · 아카이브 · 영상 전체 '+data.length+'건에서 찾습니다'; return; }
      var hits=data.filter(function(x){ return (x.t+' '+x.d).toLowerCase().indexOf(v)>-1; }); cnt.textContent=hits.length+'건';
      list.innerHTML=hits.slice(0,30).map(function(x){ return '<a class="li" href="'+esc(x.h)+'"><span class="t">'+esc(x.t)+'</span><span class="d">'+esc(x.d)+'</span></a>'; }).join('')||'<p class="muted" style="padding:16px 4px">결과가 없습니다.</p>'; }
    triggers.forEach(function(a){ a.addEventListener('click', function(e){ if(a.closest('.srch')) return; e.preventDefault(); show(); }); });
    document.addEventListener('keydown', function(e){ if(e.key==='Escape') hide(); if((e.ctrlKey||e.metaKey)&&e.key==='k'){ e.preventDefault(); show(); } });
  })();
  // 글 안의 영상: data-hd(1080p)·data-sd(720p)가 있으면 화면 폭·회선에 따라 하나를 고른다(좁은 화면·느린 회선 → 720p)
  (function(){ var sd=window.innerWidth<820||(navigator.connection&&/2g|3g/.test(navigator.connection.effectiveType||'')); qsa('video[data-hd]').forEach(function(v){ if(v.getAttribute('src')) return; v.src=(sd&&v.getAttribute('data-sd'))||v.getAttribute('data-hd'); }); })();
  // lightbox: 글 안의 그림(.art-fig img · .gallery img)을 누르면 크게 보기(한 번 더 누르면 원본 크기, 바깥 누르거나 Esc로 닫기)
  (function(){
    var imgs=qsa('.art-fig img, .gallery img, .post img'); if(!imgs.length) return;
    var box=document.createElement('div'); box.className='lightbox'; box.innerHTML='<div class="lb-bar"><span class="lb-cap"></span><a class="lb-open" target="_blank" rel="noopener">원본 새 창 ↗</a><button type="button" class="lb-x" aria-label="닫기">✕</button></div><div class="lb-body"><button type="button" class="lb-nav lb-prev" aria-label="이전">‹</button><img alt=""><button type="button" class="lb-nav lb-next" aria-label="다음">›</button></div>'; document.body.appendChild(box);
    var im=qs('img',box), body=qs('.lb-body',box), cur=0;
    function srcOf(i){ return i.getAttribute('data-full')||i.currentSrc||i.src; }
    function capOf(i){ var f=i.closest('figure'); var c=f&&f.querySelector('figcaption'); return c?c.textContent:(i.alt||''); }
    function close(){ box.classList.remove('on','zoom'); document.body.style.overflow=''; }
    function show(k){ cur=(k+imgs.length)%imgs.length; var i=imgs[cur]; im.src=srcOf(i); qs('.lb-cap',box).textContent=(imgs.length>1?(cur+1)+' / '+imgs.length+'  ':'')+capOf(i); qs('.lb-open',box).href=srcOf(i); box.classList.remove('zoom'); box.classList.toggle('multi', imgs.length>1); }
    function open(k){ show(k); box.classList.add('on'); document.body.style.overflow='hidden'; }
    imgs.forEach(function(i,k){ i.style.cursor='zoom-in'; i.addEventListener('click',function(e){ e.preventDefault(); e.stopPropagation(); open(k); }); });
    im.addEventListener('click',function(e){ e.stopPropagation(); box.classList.toggle('zoom'); });
    qs('.lb-prev',box).addEventListener('click',function(e){ e.stopPropagation(); show(cur-1); }); qs('.lb-next',box).addEventListener('click',function(e){ e.stopPropagation(); show(cur+1); });
    box.addEventListener('click',function(e){ if(e.target===box||e.target===body) close(); });
    qs('.lb-x',box).addEventListener('click',close);
    document.addEventListener('keydown',function(e){ if(!box.classList.contains('on')) return; if(e.key==='Escape') close(); if(e.key==='ArrowLeft') show(cur-1); if(e.key==='ArrowRight') show(cur+1); });
  })();
  // search
  var si=qs('#q'); if(si){ var rows=qsa('#results [data-q]'), rc=qs('#rc'); function run(){ var v=si.value.trim().toLowerCase(), n=0; rows.forEach(function(r){ var on=!v||r.getAttribute('data-q').indexOf(v)>-1; r.hidden=!on; if(on)n++; }); if(rc) rc.textContent=n+'건'; } si.addEventListener('input',run); var q0=p.get('q'); if(q0){ si.value=q0; } run(); }
})();

// 마스코트 챗봇(이음이 · 이루미) — 사이트 내용(assets/kb.json)으로 답한다.
// 서버(window.KELI_API 의 /api/chat)가 있으면 AI가 답하고, 없거나 막히면 자주 묻는 질문(assets/chatbot.json)과 지식 조각 검색으로 답한다.
(function(){
  var root=document.getElementById('kchat'), fab=document.getElementById('kchat-fab'); if(!root||!fab) return;
  var qs=function(s,r){ return (r||document).querySelector(s); }, qsa=function(s,r){ return Array.prototype.slice.call((r||document).querySelectorAll(s)); };
  var esc=function(s){ return String(s==null?'':s).replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); };
  var API=(window.KELI_API||'').replace(/\/+$/,''); var body=qs('.kc-body',root), quick=qs('.kc-quick',root), form=qs('.kc-form',root), inp=qs('.kc-in',root), send=qs('.kc-send',root);
  var cfg=null, kb=null, lang=root.getAttribute('data-lang')||'ko', history=[], busy=false, opened=false;
  var M={ ko:{ name:'이음이', sub:'KELI 사무국 마스코트 · AI 안내', face:'media/mascot/eumi.png', ph:'무엇이든 물어보세요', note:'AI가 사이트 내용을 바탕으로 답해요. 정확한 사항은 사무국(033-248-3242)로 전화해 주세요.', fail:'지금은 답을 가져오지 못했어요. 잠시 뒤 다시 물어보시거나 사무국(033-248-3242)로 전화해 주세요.', src:'관련 페이지', more:'더 자세한 내용은 사무국(033-248-3242)로 전화해 주세요.' },
          en:{ name:'Iru-mi', sub:'KELI mascot · AI guide', face:'media/mascot/irumi.png', ph:'Ask me anything', note:'Answers are generated by AI from this site. Please confirm details with the secretariat (contact@keliedu.org).', fail:"I couldn't get an answer right now. Please try again shortly or contact the secretariat (contact@keliedu.org).", src:'Related pages', more:'For details, please contact the secretariat: contact@keliedu.org' } };
  try{ var saved=localStorage.getItem('kchat_lang'); if(saved==='ko'||saved==='en') lang=saved; }catch(e){}

  function load(u){ return fetch(u,{cache:'no-store'}).then(function(r){ return r.ok?r.json():null; }).catch(function(){ return null; }); }
  function applyLang(){
    var m=M[lang]; qs('.kc-name',root).textContent=m.name; qs('.kc-sub',root).textContent=m.sub; qs('.kc-face',root).src=m.face; fab.querySelector('img').src=m.face; inp.placeholder=m.ph; qs('.kc-note',root).textContent=m.note;
    qsa('.kc-lang button',root).forEach(function(b){ b.setAttribute('aria-pressed', String(b.getAttribute('data-lang')===lang)); });
    try{ localStorage.setItem('kchat_lang',lang); }catch(e){}
    renderQuick();
  }
  function renderQuick(){ var list=(cfg&&cfg['quick_'+lang])||[]; quick.innerHTML=list.map(function(q){ return '<button type="button">'+esc(q)+'</button>'; }).join(''); qsa('button',quick).forEach(function(b){ b.addEventListener('click',function(){ ask(b.textContent); }); }); }
  function md(t){   // 아주 작은 마크다운: 줄바꿈 · 목록 · 굵게 · 링크
    var h=esc(t).replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/(https?:\/\/[^\s<)]+)/g,function(u){ return '<a href="'+u+'" target="_blank" rel="noopener">'+u.replace(/^https?:\/\//,'')+'</a>'; });
    var lines=h.split(/\n/), out='', inList='';   // inList: '' | 'ul' | 'ol'
    var close=function(){ if(inList){ out+='</'+inList+'>'; inList=''; } };
    lines.forEach(function(l){ var m=l.match(/^\s*[-•·*]\s+(.*)$/), n=l.match(/^\s*\d+[.)]\s+(.*)$/); var tag=m?'ul':(n?'ol':'');
      if(tag){ if(inList!==tag){ close(); out+='<'+tag+'>'; inList=tag; } out+='<li>'+(m||n)[1]+'</li>'; } else { close(); if(l.trim()) out+='<p>'+l+'</p>'; } });
    close(); return out||'<p></p>';
  }
  function bubble(role, html, sources){
    var d=document.createElement('div'); d.className='kc-msg '+(role==='me'?'me':'bot');
    var s=(sources&&sources.length)?'<div class="kc-src">'+sources.slice(0,3).map(function(x){ return '<a href="'+esc(x.url)+'">'+esc(x.title)+'</a>'; }).join('')+'</div>':'';
    d.innerHTML=(role==='me'?'':'<img src="'+M[lang].face+'" alt="">')+'<div class="kc-bub">'+html+s+'</div>'; body.appendChild(d); body.scrollTop=body.scrollHeight; return d;
  }
  function typing(){ var d=document.createElement('div'); d.className='kc-msg bot'; d.innerHTML='<img src="'+M[lang].face+'" alt=""><div class="kc-bub kc-typing"><span></span><span></span><span></span></div>'; body.appendChild(d); body.scrollTop=body.scrollHeight; return d; }
  function greet(){ body.innerHTML=''; history=[]; var g=(cfg&&cfg['greeting_'+lang])||(lang==='ko'?'안녕하세요! 무엇이든 물어보세요.':'Hi! Ask me anything.'); bubble('bot', md(g)); }

  // ---- 서버 없이 답하기: 자주 묻는 질문 → 지식 조각 검색
  function tokens(s){ return String(s||'').toLowerCase().replace(/[^\w가-힣a-z0-9]+/g,' ').split(' ').filter(function(w){ return w.length>1; }); }
  function score(q, text){ var qt=tokens(q), tt=String(text||'').toLowerCase(); var n=0; qt.forEach(function(w){ if(tt.indexOf(w)>-1) n+=w.length>2?2:1; for(var i=0;i+2<=w.length&&i<4;i++){ if(w.length>2&&tt.indexOf(w.slice(i,i+2))>-1) n+=.2; } }); return n; }
  function localAnswer(q){
    var faq=(cfg&&cfg.faq)||[]; var best=null, bs=0;
    faq.forEach(function(f){ var s=score(q,(f['q_'+lang]||'')+' '+(f['a_'+lang]||'')); if(s>bs){ bs=s; best=f; } });
    if(best&&bs>=3&&best['a_'+lang]) return { text: best['a_'+lang], sources: [] };
    if(kb&&kb.chunks){ var ranked=kb.chunks.filter(function(c){ return c.lang===lang||(lang==='ko'&&c.lang!=='en'); }).map(function(c){ return {c:c, s:score(q,c.title+' '+c.text)}; }).sort(function(a,b){ return b.s-a.s; }).filter(function(x){ return x.s>=2; }).slice(0,3);
      if(ranked.length){ var top=ranked[0].c; var t=top.text.length>420?top.text.slice(0,420).replace(/\s\S*$/,'')+'…':top.text; return { text:(lang==='ko'?'사이트에서 찾은 내용이에요.\n\n':'Here is what I found on the site.\n\n')+'**'+top.title+'** — '+t, sources: ranked.map(function(x){ return {title:x.c.title,url:x.c.url}; }) }; }
    }
    return { text: lang==='ko'?'아직 잘 모르는 내용이에요. '+M.ko.more:'I am not sure about that yet. '+M.en.more, sources: [{title:lang==='ko'?'도입 문의':'Contact', url:'join.html#inquiry'}] };
  }
  function ask(q){
    q=String(q||'').trim(); if(!q||busy) return; busy=true; send.disabled=true; inp.value='';
    bubble('me', esc(q)); history.push({role:'user',content:q}); var t=typing();
    var done=function(ans){ t.remove(); bubble('bot', md(ans.text), ans.sources); history.push({role:'assistant',content:ans.text}); if(history.length>12) history=history.slice(-12); busy=false; send.disabled=false; inp.focus(); };
    if(!API){ setTimeout(function(){ done(localAnswer(q)); }, 350); return; }
    fetch(API+'/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({lang:lang,page:location.pathname.split('/').pop()||'index.html',messages:history.slice(-8)})})
      .then(function(r){ return r.ok?r.json():Promise.reject(new Error('HTTP '+r.status)); })
      .then(function(j){ if(!j||!j.answer) throw new Error('empty'); done({text:j.answer, sources:j.sources||[]}); })
      .catch(function(){ var a=localAnswer(q); done(a); });
  }
  function open(){ root.hidden=false; fab.setAttribute('aria-expanded','true'); if(!opened){ opened=true; Promise.all([cfg?null:load('assets/chatbot.json'), kb?null:load('assets/kb.json')]).then(function(r){ cfg=cfg||r[0]||{}; kb=kb||r[1]; applyLang(); greet(); }); } setTimeout(function(){ inp.focus(); },50); }
  function close(){ root.hidden=true; fab.setAttribute('aria-expanded','false'); }
  fab.addEventListener('click',open); qs('.kc-x',root).addEventListener('click',close);
  qsa('.kc-lang button',root).forEach(function(b){ b.addEventListener('click',function(){ var l=b.getAttribute('data-lang'); if(l===lang) return; lang=l; applyLang(); greet(); }); });
  form.addEventListener('submit',function(e){ e.preventDefault(); ask(inp.value); });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape'&&!root.hidden) close(); });
  applyLang();
})();

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
