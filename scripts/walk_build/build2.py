import json, os, sys, re
from PIL import Image, ImageChops
sys.path.insert(0, '/tmp/claude-0/walk'); from spec import SPEC; from spec2 import CROP, STEPS
try: from hot import HOT
except Exception: HOT = {}
SITE = '/home/claude/keli-site'; MP = '/tmp/claude-0/mp'; HI = '/tmp/claude-0/hi'
mv = {i['id']: i for i in json.load(open(f'{SITE}/assets/manual_videos.json', encoding='utf-8'))['items']}
def trim(im):
    bg = Image.new(im.mode, im.size, (255, 255, 255)); diff = ImageChops.difference(im, bg).convert('L').point(lambda v: 255 if v > 12 else 0); bb = diff.getbbox()
    if bb: im = im.crop((max(0, bb[0] - 16), max(0, bb[1] - 16), min(im.width, bb[2] + 16), min(im.height, bb[3] + 16)))
    return im
def page(key, n):
    for base in (HI, MP):
        d = f'{base}/{key}'
        if os.path.isdir(d):
            fs = [f for f in os.listdir(d) if re.fullmatch(rf'p-0*{n}\.jpg', f)]
            if fs: return Image.open(f'{d}/{fs[0]}').convert('RGB')
    raise SystemExit(f'no page {key} {n}')
out = json.load(open(f'{SITE}/content/walkthroughs.json', encoding='utf-8')); items = out.get('items', {}); only = set(sys.argv[1:])
for slug, (key, steps0) in SPEC.items():
    if only and slug not in only: continue
    d = f'{SITE}/media/walk/{slug}'; os.makedirs(d, exist_ok=True)
    for f in os.listdir(d): os.remove(os.path.join(d, f))
    st = []; crops = CROP.get(slug); hots = HOT.get(slug) or []
    for k, step in enumerate(STEPS[slug], 1):
        pg, title, text = step[:3]; im = page(key, pg)
        crop = crops[k - 1] if crops else (SPEC[slug][1][k - 1][3] if len(SPEC[slug][1][k - 1]) > 3 else None)
        if crop:
            W, H = im.size; im = im.crop((int(crop[0] * W), int(crop[1] * H), int(crop[2] * W), int(crop[3] * H)))
            if not crops: im = trim(im)
        else: im = trim(im)
        im.thumbnail((1500, 1500)); im.save(f'{d}/{k}.jpg', quality=78, optimize=True, progressive=True)
        s = {'img': f'media/walk/{slug}/{k}.jpg', 'title': title, 'text': text}
        if k - 1 < len(hots) and hots[k - 1]:
            h = dict(hots[k - 1])
            if h.get('title'): s['title'] = h.pop('title')
            if h.get('text'): s['text'] = h.pop('text')
            s.update(h)
        st.append(s)
    mid = key.rsplit('-', 1)[0]; idx = int(key.rsplit('-', 1)[1])
    man = (mv.get(mid, {}).get('manuals') or [{}] * (idx + 1))[idx].get('url', '') if mid in mv else ''
    items[slug] = {'steps': st, 'manual': man}
out['items'] = items
json.dump(out, open(f'{SITE}/content/walkthroughs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(items), 'services')
