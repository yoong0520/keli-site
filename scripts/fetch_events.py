#!/usr/bin/env python3
"""AI교육확산센터 사이트(aiadvcenter.csedu4all.com/news/stories)에서 제목이 [KELI]로 시작하는 글만 모아
assets/events.live.json 에 기록한다. KELI 사이트의 '행사'는 이 파일만 보고 그린다.

- 목록 페이지(서버 렌더 HTML)의 카드에서 제목·링크·분류·일시·장소·썸네일을 읽고
- 글마다 상세 페이지를 열어 게시일·본문 요약·첨부파일을 보탠다.
- 실패하면 기존 파일을 그대로 둔다(배포는 계속 진행).
"""
import json, re, sys, os, html, datetime, urllib.request, urllib.parse

BASE = 'https://aiadvcenter.csedu4all.com'
LIST = BASE + '/news/stories'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'events.live.json')
UA = {'User-Agent': 'KELI-site events fetcher (+https://yoong0520.github.io/keli-site/)'}
PREFIX = '[KELI]'

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'ignore')

def text(s):
    s = re.sub(r'<svg.*?</svg>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

ALLOWED = {'p', 'br', 'ul', 'ol', 'li', 'strong', 'b', 'em', 'i', 'u', 'a', 'h3', 'h4', 'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'img'}
def clean_html(s, base=None):
    base = base or BASE
    """본문 HTML 정리: 허용 태그만 남기고 속성은 a[href]·img[src,alt]만 유지. 제목 태그는 h3으로."""
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = re.sub(r'<(/?)h[12]\b', r'<\1h3', s)
    def tag(m):
        close, name, attrs = m.group(1), m.group(2).lower(), m.group(3) or ''
        if name not in ALLOWED:
            return ''
        if close:
            return f'</{name}>'
        keep = ''
        if name == 'a':
            h = re.search(r'href="([^"]*)"', attrs)
            if h:
                href = html.unescape(h.group(1))
                if href.lower().startswith('javascript:'):
                    return ''
                if href.startswith('/'):
                    href = base + href
                keep = f' href="{html.escape(href, quote=True)}" target="_blank" rel="noopener"'
        elif name == 'img':
            sm = re.search(r'src="([^"]*)"', attrs)
            if not sm:
                return ''
            srcv = sm.group(1)
            if srcv.startswith('/'):
                srcv = base + srcv
            keep = f' src="{html.escape(srcv, quote=True)}" alt="" loading="lazy"'
        return f'<{name}{keep}>'
    s = re.sub(r'<(/?)([A-Za-z0-9]+)([^>]*)>', tag, s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s.strip()

def parse_when(w):
    """'2026.10.20(화) 10:00~17:00' / '2026.10.21(수) 16:00 ~ 2026.10.24(토) 03:08' → (start, end) ISO"""
    ds = re.findall(r'(\d{4})\.(\d{1,2})\.(\d{1,2})(?:\([^)]*\))?\s*(\d{1,2}:\d{2})?', w)
    if not ds:
        return None, None
    def iso(d):
        y, m, dd, t = d
        return f'{y}-{int(m):02d}-{int(dd):02d}T{t or "00:00"}'
    start = iso(ds[0])
    if len(ds) > 1:
        end = iso(ds[-1])
    else:
        t2 = re.search(r'~\s*(\d{1,2}:\d{2})', w)
        end = f'{start[:10]}T{t2.group(1)}' if t2 else f'{start[:10]}T23:59'
    return start, end

def parse_list(h):
    items = []
    for card in re.findall(r'<li class="StoryGrid_card__[^"]*">(.*?)</li>', h, flags=re.S):
        m = re.search(r'href="(/news/stories/(\d+))">([^<]+)</a>', card)
        if not m:
            continue
        title = html.unescape(m.group(3)).strip()
        if not title.startswith(PREFIX):
            continue
        img = re.search(r'<img src="([^"]+)"', card)
        dds = [text(x) for x in re.findall(r'<dd>(.*?)</dd>', card, flags=re.S)]
        badges = [text(b) for b in re.findall(r'class="badge[^"]*">(.*?)</span>', card)]
        items.append({
            'id': int(m.group(2)),
            'title_raw': title,
            'title': title[len(PREFIX):].strip(),
            'url': BASE + m.group(1),
            'badges': [b for b in badges if b not in ('새 글',)],
            'when': dds[0] if dds else '',
            'place': re.sub(r'^[●•·\-\s]+', '', dds[1]) if len(dds) > 1 else '',
            'thumb': (BASE + img.group(1)) if img and img.group(1).startswith('/') else (img.group(1) if img else ''),
        })
    return items

def parse_detail(h, it):
    body = re.search(r'<main.*?</main>', h, flags=re.S)
    s = body.group(0) if body else h
    m = re.search(r'게시일\s*</dt>\s*<dd[^>]*>([^<]+)', s) or re.search(r'게시일\D{0,40}(\d{4}\.\d{2}\.\d{2})', text(s))
    if m:
        it['posted'] = m.group(1).strip()
    i = s.find('class="PostView_body__')
    j = min([k for k in (s.find('PostView_files__', i), s.find('PostView_adjacent__', i), s.find('PostView_actions__', i)) if k > 0] or [len(s)])
    if i > 0:
        inner = s[i:j]
        sd = re.search(r'srcDoc="([^"]*)"', inner)
        bh = html.unescape(sd.group(1)) if sd else inner
        bh = re.sub(r'<(style|script|head).*?</\1>', '', bh, flags=re.S)
        bm = re.search(r'<body[^>]*>(.*?)</body>', bh, flags=re.S)
        bh = bm.group(1) if bm else bh
        it['body_html'] = clean_html(bh)
        t = text(bh)
        it['summary'] = (t[:160] + '…') if len(t) > 160 else t
        link = re.search(r'href="(https?://[^"]+)"', bh)
        if link:
            it['link'] = html.unescape(link.group(1))
    files = []
    for fm in re.finditer(r'<a[^>]+href="(/api/files/([A-Za-z0-9]+))\?download=1"[^>]*>(.*?)</a>', s, flags=re.S):
        t = text(fm.group(3))
        nm = re.search(r'(.+?\.(?:pdf|hwpx?|docx?|pptx?|xlsx?|zip|jpe?g|png))', t, flags=re.I)
        name = re.sub(r'^(PDF|HWPX?|DOCX?|PPTX?|XLSX?|ZIP|JPG|PNG)\s*', '', nm.group(1)).strip() if nm else t[:80]
        if not any(f['id'] == fm.group(2) for f in files):
            files.append({'id': fm.group(2), 'name': name, 'url': BASE + fm.group(1)})
    it['files'] = files[:6]
    return it

def main():
    try:
        seen, items = set(), []
        for page in range(1, 11):
            h = get(LIST if page == 1 else f'{LIST}?page={page}')
            got = parse_list(h)
            ids = {g['id'] for g in got}
            if not got or ids <= seen:
                break
            for g in got:
                if g['id'] not in seen:
                    seen.add(g['id']); items.append(g)
            if len(re.findall(r'<li class="StoryGrid_card__', h)) < 5:
                break
        if not items:
            raise RuntimeError('no [KELI] stories found')
        for it in items:
            try:
                parse_detail(get(it['url']), it)
            except Exception as e:  # 상세 실패는 목록 정보만으로 진행
                print('detail failed', it['url'], e, file=sys.stderr)
            it['start'], it['end'] = parse_when(it.get('when', ''))
        items.sort(key=lambda x: x.get('start') or '', reverse=True)
        kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        data = {'source': LIST, 'filter': f'제목이 {PREFIX}로 시작하는 글', 'fetched_at': kst.strftime('%Y. %m. %d.').replace(' 0', ' '),
                'fetched_iso': kst.isoformat(timespec='minutes'), 'count': len(items), 'items': items}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('ok', len(items), [i['title'] for i in items])
    except Exception as e:
        print('fetch failed, keeping previous file:', e, file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()
