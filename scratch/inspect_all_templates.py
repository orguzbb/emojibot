import json, gzip

templates = [14, 15, 16, 20, 25, 30, 50, 75, 100, 117]

for t in templates:
    with open(f"shablonlar/{t}.tgs", "rb") as f:
        d = json.loads(gzip.decompress(f.read()))
    print(f"=== {t}.tgs (layers: {len(d['layers'])}) ===")
    for i, l in enumerate(d['layers']):
        shapes = l.get('shapes', [])
        fills = []
        strokes = []
        def get_fs(item):
            ty = item.get('ty')
            if ty == 'fl' and 'c' in item:
                k = item['c'].get('k')
                if isinstance(k, list) and len(k) >= 3 and isinstance(k[0], (int, float)):
                    fills.append([round(x, 2) for x in k[:3]])
            elif ty == 'st' and 'c' in item:
                k = item['c'].get('k')
                if isinstance(k, list) and len(k) >= 3 and isinstance(k[0], (int, float)):
                    strokes.append([round(x, 2) for x in k[:3]])
            for it in item.get('it', []):
                get_fs(it)
        for sh in shapes:
            get_fs(sh)
        print(f"  Layer {i} ('{l.get('nm')}'): fills={fills}, strokes={strokes}")
