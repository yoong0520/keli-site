#!/usr/bin/env python3
"""현행 KELI 포털(keliedu.org/keli/contents/archive/*)의 아카이브 글을 한 번에 가져와 content/archive.json 에 넣는다(1회 이관용).

- 게시판: business(실증 사례집 → case) · technic(최신 기술 동향 → trend) · policy(정책 연구 보고서 → trend) · guidebook(간행물 → manual)
- 글마다 제목 · 날짜 · 본문 · 표지 그림 · 첨부파일을 읽는다(목록은 data-seq, 상세는 POST mode=view).
- 첨부는 content/files/archive/<seq>/ 에, 표지는 media/archive/<seq>.jpg 에 저장한다.
- 본문은 KELI 글 블록(리드 · 핵심 정보 · 점 목록)으로 다시 구성한다. 이관 뒤에는 관리자 화면에서 자유롭게 고친다.
- 이미 있는 항목(id 'o<seq>')은 제목·본문·파일을 덮어쓰고, 관리자가 만든 다른 항목은 그대로 둔다.
"""
import json, re, sys, os, html, urllib.request, urllib.parse, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'gen'))
from media import localize
from fetch_events import clean_html, text as _text

BASE = 'https://keliedu.org'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128 Safari/537.36', 'Accept-Language': 'ko'}
BOARDS = [('business', 'case'), ('technic', 'trend'), ('policy', 'trend'), ('guidebook', 'manual')]
OUT = os.path.join(ROOT, 'content', 'archive.json')

def get(url, data=None):
    h = dict(UA)
    if data is not None:
        h['Content-Type'] = 'application/x-www-form-urlencoded'
        data = urllib.parse.urlencode(data).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=60) as r:
        return r.read().decode('utf-8', 'ignore')

def download(url, dest):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        cd = r.headers.get('Content-Disposition', '')
        m = re.search(r"filename\*=UTF-8''([^;]+)", cd)
        name = urllib.parse.unquote(m.group(1)) if m else os.path.basename(dest)
        data = r.read()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, 'wb').write(data)
    return name, len(data)

def safe(n):
    return re.sub(r'_+', '_', re.sub(r'[\\/:*?"<>|#%&+\s]+', '_', n)).strip('_')

def fmt_size(b):
    return f'{b / 1048576:.1f} MB' if b > 1048576 else f'{max(1, round(b / 1024))} KB'

def parse_view(h):
    it = {}
    m = re.search(r'board-title">\s*(.*?)\s*</div>', h, flags=re.S); it['title_raw'] = html.unescape(m.group(1)).strip() if m else ''
    m = re.search(r'skinTb-date">\s*([\d-]+)', h); it['date'] = m.group(1).replace('-', '.') if m else ''
    m = re.search(r'<div class="skinTb-td skinTb-conts">(.*?)</div>\s*</div>\s*(?:<!-- 첨부파일표시|<div class="skinTb-tr">\s*<div class="skinTb-th col2 skinTxa-center" data-hidden="mob">첨부파일)', h, flags=re.S)
    conts = m.group(1) if m else ''
    cov = re.search(r'<img src="(/upload/board/[^"]+)"', conts)
    it['cover_remote'] = (BASE + cov.group(1)) if cov else ''
    conts = re.sub(r'<div class="boGalleryView">.*?</div>\s*</div>', '', conts, flags=re.S)
    it['body_raw'] = clean_html(conts, BASE)
    it['files_raw'] = [(BASE + u, html.unescape(_text(n)).strip()) for u, n in re.findall(r'<a href="(/egf/bp/common/front/\d+/download)">(.*?)</a>', h, flags=re.S)]
    return it

KV = re.compile(r'^\s*(교과목명|교수명|대학명|전공명|작성자|발행|저자|기관|분야)\s*[:：]\s*(.+?)\s*$')
def restyle_archive(body_html):
    """목록의 '키: 값' 줄 → 핵심 정보 카드, '목 차' 줄 → 목차 목록, 나머지 → 리드 문단"""
    from gen2 import restyle, _clean_inline
    items = [_text(li) for li in re.findall(r'<li[^>]*>(.*?)</li>', body_html, flags=re.S)]
    kv, toc, rest = [], [], []
    for t in items:
        t = re.sub(r'\s+', ' ', t).strip()
        m = KV.match(t)
        if m:
            kv.append((m.group(1), m.group(2)))
        elif t.startswith('목 차') or t.startswith('목차'):
            toc = [x.strip() for x in re.split(r'\s(?=\d{2}\s)', t.replace('목 차', '').replace('목차', '').strip()) if x.strip()]
        elif t:
            rest.append(t)
    paras = [html.unescape(re.sub(r'<[^>]+>', ' ', p)).strip() for p in re.findall(r'<p[^>]*>(.*?)</p>', body_html, flags=re.S)]
    paras = [re.sub(r'\s+', ' ', p) for p in paras if re.sub(r'\s+', ' ', p).strip()]
    out = ''
    if paras:
        out += f'<p class="art-lead">{html.escape(paras[0])}</p>' + ''.join(f'<p>{html.escape(p)}</p>' for p in paras[1:])
    if kv:
        out += '<dl class="art-kv">' + ''.join(f'<dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd>' for k, v in kv) + '</dl>'
    if toc:
        out += '<h3 class="art-h">목차</h3><ol class="art-ol">' + ''.join(f'<li>{html.escape(re.sub(r"^\d{2}\s*", "", x))}</li>' for x in toc) + '</ol>'
    if rest:
        out += '<ul class="art-ul">' + ''.join(f'<li>{html.escape(x)}</li>' for x in rest) + '</ul>'
    if not out:   # 목록이 없는 글은 일반 규칙으로
        out = restyle(body_html, kind='archive')
    return out, dict(kv)

def main():
    data = json.load(open(OUT, encoding='utf-8'))
    keep = [a for a in data['items'] if not str(a.get('url', '')).startswith('https://keliedu.org/keli/contents/archive') and not str(a.get('id', '')).startswith('o')]
    imported = []
    for board, cat in BOARDS:
        lst = get(f'{BASE}/keli/contents/archive/{board}')
        seqs = re.findall(r'data-seq="(\d+)"', lst)
        seqs = list(dict.fromkeys(seqs))
        print(board, len(seqs), 'posts')
        for seq in seqs:
            v = parse_view(get(f'{BASE}/keli/contents/archive/{board}', {'pageIndex': '1', 'mode': 'view', 'articleSeq': seq}))
            title = re.sub(r'^\[AI 활용 수업 사례집\]\s*', '', v['title_raw'])
            title = re.sub(r'\s*-\s*한림대학교\s*$', '', title).strip()
            body, kv = restyle_archive(v['body_raw'])
            files = []
            for u, n in v['files_raw']:
                if re.search(r'\.(jpe?g|png|gif)$', n, flags=re.I):   # 표지 그림은 첨부가 아니라 표지로
                    continue
                dest = os.path.join(ROOT, 'content', 'files', 'archive', seq, safe(n))
                if os.path.exists(dest):
                    size = os.path.getsize(dest)
                else:
                    _, size = download(u, dest)
                files.append({'name': n, 'url': 'content/files/archive/' + seq + '/' + safe(n), 'size': fmt_size(size)})
            cover = localize(v['cover_remote'], 'archive', seq, referer=BASE) if v['cover_remote'] else ''
            if not cover and files and files[0]['url'].lower().endswith('.pdf'):   # 표지가 없으면 PDF 첫 장
                try:
                    import subprocess
                    png = os.path.join(ROOT, 'media', 'archive', seq)
                    subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-r', '110', '-jpeg', os.path.join(ROOT, files[0]['url']), png], check=True, capture_output=True)
                    made = [f for f in os.listdir(os.path.join(ROOT, 'media', 'archive')) if f.startswith(seq + '-')]
                    if made:
                        shutil.move(os.path.join(ROOT, 'media', 'archive', made[0]), png + '.jpg'); cover = f'media/archive/{seq}.jpg'
                except Exception as e:
                    print('cover from pdf failed', seq, e, file=sys.stderr)
            org = '한림대학교' + (f' {kv["전공명"]}' if kv.get('전공명') else '') if cat == 'case' else 'KELI 사무국'
            it = {'id': 'o' + seq, 'cat': cat, 'type': 'pdf' if files else 'doc', 'title': title, 'org': org, 'author': kv.get('교수명', ''), 'date': v['date'],
                  'url': '', 'body': body, 'files': files, 'cover': cover or '', 'published': True, 'source': f'{BASE}/keli/contents/archive/{board} (이관 seq {seq})'}
            imported.append(it)
            print(' ', seq, cat, title[:40], '| files', len(files), '| cover', bool(cover))
    data['items'] = imported + keep
    json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('written', len(imported), 'imported +', len(keep), 'kept')

if __name__ == '__main__':
    main()
