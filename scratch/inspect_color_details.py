import json, gzip

def inspect_colors_detail(tpl_id):
    with open(f"shablonlar/{tpl_id}.tgs", "rb") as f:
        d = json.loads(gzip.decompress(f.read()))

    print(f"\n================ TEMPLATE {tpl_id}.tgs ================")
    
    def walk(item, path=""):
        if not isinstance(item, dict): return
        nm = str(item.get("nm", ""))
        ty = item.get("ty")
        if ty in ("fl", "st") and "c" in item:
            c = item["c"].get("k")
            if isinstance(c, list) and len(c) >= 3 and isinstance(c[0], (int, float)):
                r, g, b = [round(x, 3) for x in c[:3]]
                print(f"  {path} > {nm} ({ty}) -> [{r}, {g}, {b}]")
        
        for it in item.get("it", []):
            walk(it, f"{path} > {nm}")
        for sh in item.get("shapes", []):
            walk(sh, f"{path} > {nm}")

    for i, l in enumerate(d.get("layers", [])):
        print(f"Layer {i}: nm='{l.get('nm')}'")
        walk(l, f"L{i}")
    for a in d.get("assets", []):
        for j, l in enumerate(a.get("layers", [])):
            print(f"Asset Layer {j}: nm='{l.get('nm')}'")
            walk(l, f"Asset.L{j}")

for t in [1, 2, 14, 15, 20, 50]:
    inspect_colors_detail(t)
