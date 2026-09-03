import json, gzip

with open("shablonlar/14.tgs", "rb") as f:
    data = json.loads(gzip.decompress(f.read()))

print("Layers count:", len(data.get("layers", [])))
for i, l in enumerate(data.get("layers", [])):
    print(f"Layer {i}: nm={l.get('nm')}, ty={l.get('ty')}")
    for j, sh in enumerate(l.get("shapes", [])):
        print(f"  Shape {j}: nm={sh.get('nm')}, ty={sh.get('ty')}")
        if "it" in sh:
            for k, it in enumerate(sh["it"]):
                print(f"    Sub-item {k}: nm={it.get('nm')}, ty={it.get('ty')}")
