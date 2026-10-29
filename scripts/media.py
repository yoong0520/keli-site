#!/usr/bin/env python3
"""외부 글의 사진을 이 저장소(media/)로 내려받아 사이트 안에서 직접 서비스한다.
- 핫링크 차단·보안 정책(CSP)·원본 삭제에 영향받지 않도록 로컬 사본을 쓴다.
- 긴 변 1600px 이하 JPEG(품질 82)로 줄여 저장. 같은 이름의 파일이 있으면 다시 받지 않는다.
"""
import os, io, re, sys, hashlib, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
UA = {'User-Agent': 'KELI-site media fetcher (+https://yoong0520.github.io/keli-site/)'}

def localize(url, folder, name, referer=None):
    """url → 'media/<folder>/<name>.jpg' (상대 경로). 실패하면 None"""
    try:
        from PIL import Image
    except Exception:
        print('Pillow not available; keeping remote image', file=sys.stderr)
        return None
    safe = re.sub(r'[^A-Za-z0-9_-]', '', name)[:60] or hashlib.md5(url.encode()).hexdigest()[:12]
    rel = f'media/{folder}/{safe}.jpg'
    path = os.path.join(ROOT, rel)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return rel
    try:
        headers = dict(UA)
        if referer:
            headers['Referer'] = referer
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read(30_000_000)
        im = Image.open(io.BytesIO(data))
        im.load()
        if im.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', im.size, (255, 255, 255))
            bg.paste(im.convert('RGBA'), mask=im.convert('RGBA').split()[-1])
            im = bg
        else:
            im = im.convert('RGB')
        im.thumbnail((1600, 1600))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im.save(path, 'JPEG', quality=82, optimize=True, progressive=True)
        return rel
    except Exception as e:
        print('media failed', url, e, file=sys.stderr)
        return None
