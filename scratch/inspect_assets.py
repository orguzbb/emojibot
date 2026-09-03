import json, gzip

with open("shablonlar/15.tgs", "rb") as f:
    d = json.loads(gzip.decompress(f.read()))

print("15.tgs assets count:", len(d.get("assets", [])))
for a in d.get("assets", []):
    print(f"Asset id={a.get('id')}, layers count={len(a.get('layers', []))}")
    for l in a.get("layers", []):
        print(f"  Asset Layer: nm={repr(l.get('nm'))}, ty={l.get('ty')}")
