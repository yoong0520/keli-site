
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
      try{ localStorage.setItem('tab:'+bar.getAttribute('data-tabs'),key);}catch(e){}
    }
    qsa('.tab',bar).forEach(function(t){ t.addEventListener('click',function(){ apply(t.getAttribute('data-val')); }); });
    var init='all'; try{ init=localStorage.getItem('tab:'+bar.getAttribute('data-tabs'))||'all'; }catch(e){}
    var h=location.hash.replace('#',''); if(h && qs('.tab[data-val="'+h+'"]',bar)) init=h;
    apply(init);
  });
  // forms (demo: validate, show receipt)
  function validate(f){ var ok=true; qsa('.field',f).forEach(function(fd){ var inp=qs('input,select,textarea',fd); if(!inp) return; var bad=false; if(inp.required && !inp.value.trim()) bad=true; if(inp.type==='email' && inp.value && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(inp.value)) bad=true; fd.classList.toggle('err',bad); if(bad) ok=false; }); var ag=qs('input[type=checkbox][required]',f); if(ag&&!ag.checked){ ok=false; ag.focus(); } return ok; }
  qsa('form[data-demo]').forEach(function(f){
    f.addEventListener('submit',function(e){ e.preventDefault(); if(!validate(f)) return; var d=qs('.done',f); var id=f.getAttribute('data-demo').toUpperCase()+'-'+new Date().toISOString().slice(0,10).replace(/-/g,'')+'-'+String(Math.floor(Math.random()*900)+100); if(d){ var c=qs('code',d); if(c) c.textContent=id; d.setAttribute('data-show','1'); d.scrollIntoView({block:'nearest'}); } var sub=qs('button[type=submit]',f); if(sub){ sub.disabled=true; sub.textContent='접수되었습니다'; } });
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
  // search
  var si=qs('#q'); if(si){ var rows=qsa('#results [data-q]'), rc=qs('#rc'); function run(){ var v=si.value.trim().toLowerCase(), n=0; rows.forEach(function(r){ var on=!v||r.getAttribute('data-q').indexOf(v)>-1; r.hidden=!on; if(on)n++; }); if(rc) rc.textContent=n+'건'; } si.addEventListener('input',run); var q0=p.get('q'); if(q0){ si.value=q0; } run(); }
})();
