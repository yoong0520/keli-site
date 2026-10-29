
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
  if(svc){ qsa('input[name="services"]').forEach(function(c){ if(c.value===svc) c.checked=true; }); var sel=qs('#f-type'); }
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
      var f=qs('#stats-form'); if(f){ ['services','universities','companies','courses','basis'].forEach(function(k){ var i=qs('[name="'+k+'"]',f); if(i&&s[k]!=null) i.value=s[k]; }); }
    }).catch(function(){}).then(function(){ return load('assets/stats.live.json'); }).then(function(l){
      if(l&&l.courses){ setStat('courses_live',l.courses); setStat('courses_date',l.fetched_at||''); if(!(manual&&manual.courses!=null&&manual.courses!=='')){ setStat('courses',l.courses); setStat('courses_note','한림 AI 교육 포털 '+(l.fetched_at||'')+' 기준'); } }
    }).catch(function(){}).then(countUp);
    // admin demo page
    var f=qs('#stats-form');
    if(f){
      function num(k){ var v=qs('[name="'+k+'"]',f).value.trim(); return v===''?null:Number(v); }
      function preview(){ var s=num('services'), u=num('universities')||0, c=num('companies')||0, k=num('courses'); qs('#p-services').textContent=fmt(s||0); qs('#p-partners').textContent=fmt(u+c); var live=qs('[data-stat="courses_live"]'); qs('#p-courses').textContent=k!=null?fmt(k):(live?live.textContent:'—'); }
      f.addEventListener('input',preview);
      qs('#s-copy').addEventListener('click',function(){
        var out={ "_안내": "KELI 사무국이 직접 고치는 파일입니다. 숫자만 바꾸고 저장하면 1~2분 뒤 홈 화면에 반영됩니다. courses를 null로 두면 한림 AI 교육 포털의 AI 강좌 수를 자동으로 씁니다.", services:num('services'), universities:num('universities'), companies:num('companies'), courses:num('courses'), basis:qs('[name="basis"]',f).value };
        var t=JSON.stringify(out,null,2); var d=qs('#s-done');
        function ok(){ if(d) d.setAttribute('data-show','1'); }
        if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(t).then(ok,function(){ var ta=qs('#s-json'); ta.hidden=false; ta.value=t; ta.select(); }); } else { var ta=qs('#s-json'); ta.hidden=false; ta.value=t; ta.select(); }
      });
    }
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
      var items=f.items||[]; if(!items.length) return;
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
  // press feed: 한림대 보도자료 KELI·켈리 글 (assets/press.live.json) → [data-press] 다시 그리기
  (function(){
    var boxes=qsa('[data-press]'); if(!boxes.length||location.protocol==='file:') return;
    function esc(s){ return String(s||'').replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
    function href(it,p){ return p.indexOf(String(it.id))>-1 ? 'press-'+it.id+'.html' : it.url; }
    function ext(it,p){ return p.indexOf(String(it.id))>-1 ? '' : ' target="_blank" rel="noopener"'; }
    function row(it,p,sum){ return '<a class="li" href="'+href(it,p)+'"'+ext(it,p)+'><span><span class="m">보도자료'+(it.category?' · '+esc(it.category):'')+'</span><br><span class="t">'+esc(it.title)+'</span>'+(sum&&it.summary?'<br><span class="m">'+esc(it.summary.slice(0,90))+'</span>':'')+'</span><span class="d">'+esc(it.date)+'</span></a>'; }
    fetch('assets/press.live.json',{cache:'no-store'}).then(function(r){ if(!r.ok) throw 0; return r.json(); }).then(function(f){
      var items=f.items||[]; if(!items.length) return;
      boxes.forEach(function(b){ var p=(b.getAttribute('data-pages')||'').split(','); var kind=b.getAttribute('data-press');
        if(kind==='rows') b.innerHTML=items.slice(0,3).map(function(it){ return row(it,p,false); }).join('');
        else if(kind==='list') b.innerHTML=items.map(function(it){ return row(it,p,true); }).join('');
      });
      var fd=qs('[data-press-date]'); if(fd&&f.fetched_at) fd.textContent=f.fetched_at;
    }).catch(function(){});
  })();
  // search
  var si=qs('#q'); if(si){ var rows=qsa('#results [data-q]'), rc=qs('#rc'); function run(){ var v=si.value.trim().toLowerCase(), n=0; rows.forEach(function(r){ var on=!v||r.getAttribute('data-q').indexOf(v)>-1; r.hidden=!on; if(on)n++; }); if(rc) rc.textContent=n+'건'; } si.addEventListener('input',run); var q0=p.get('q'); if(q0){ si.value=q0; } run(); }
})();
