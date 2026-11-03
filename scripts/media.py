#!/usr/bin/env python3
"""외부 글의 사진을 이 저장소(media/)로 내려받아 사이트 안에서 직접 서비스한다.
- 핫링크 차단·보안 정책(CSP)·원본 삭제에 영향받지 않도록 로컬 사본을 쓴다.
- 긴 변 1600px 이하 JPEG(품질 82)로 줄여 저장. 같은 이름의 파일이 있으면 다시 받지 않는다.
"""
import os, io, re, sys, hashlib, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
UA = {'User-Agent': 'KELI-site media fetcher (+https://keli-aied.org/)'}

def localize(url, folder, name, referer=None, fmt='jpg', max_px=1600, fresh=False):
    """url → 'media/<folder>/<name>.jpg|png' (상대 경로). 실패하면 None
    fmt='png' 이면 투명 배경(로고)을 지키며 PNG로 저장. fresh=True 이면 있어도 다시 받는다(로고처럼 바뀔 수 있는 그림)."""
    try:
        from PIL import Image
    except Exception:
        print('Pillow not available; keeping remote image', file=sys.stderr)
        return None
    safe = re.sub(r'[^A-Za-z0-9_-]', '', name)[:60] or hashlib.md5(url.encode()).hexdigest()[:12]
    rel = f'media/{folder}/{safe}.{"png" if fmt == "png" else "jpg"}'
    path = os.path.join(ROOT, rel)
    if not fresh and os.path.exists(path) and os.path.getsize(path) > 0:
        return rel
    try:
        headers = dict(UA)
        if referer:
            headers['Referer'] = referer
        req = urllib.request.Request(url, headers=headers)
        data = None
        for attempt in range(3):   # 연결이 끊기는 CDN이 있어 세 번까지 다시 시도
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = r.read(30_000_000)
                break
            except Exception as e:
                if attempt == 2:
                    raise
                import time; time.sleep(2 + 3 * attempt)
        im = Image.open(io.BytesIO(data))
        im.load()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if fmt == 'png':
            im = im.convert('RGBA')
            im.thumbnail((max_px, max_px))
            if fresh and os.path.exists(path):   # 같은 그림이면 파일을 건드리지 않는다(불필요한 커밋 방지)
                buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
                if open(path, 'rb').read() == buf.getvalue():
                    return rel
            im.save(path, 'PNG', optimize=True)
            return rel
        if im.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', im.size, (255, 255, 255))
            bg.paste(im.convert('RGBA'), mask=im.convert('RGBA').split()[-1])
            im = bg
        else:
            im = im.convert('RGB')
        im.thumbnail((max_px, max_px))
        im.save(path, 'JPEG', quality=82, optimize=True, progressive=True)
        return rel
    except Exception as e:
        print('media failed', url, e, file=sys.stderr)
        return None
