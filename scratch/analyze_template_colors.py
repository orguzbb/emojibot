import json, gzip

def analyze_template_colors(tpl_id):
    with open(f"shablonlar/{tpl_id}.tgs", "rb") as f:
        data = json.loads(gzip.decompress(f.read()))
    out = []
    out.append(f"\n=================== TEMPLATE {tpl_id}.tgs ===================")
    for i, l in enumerate(data.get("layers", [])):
        lnm = l.get('nm', '')
        out.append(f"--- Layer {i}: nm={repr(lnm)} (ty={l.get('ty')}) ---")
        for j, sh in enumerate(l.get("shapes", [])):
            find_colors(sh, f"L{i}.S{j}", out)
    return "\n".join(out)

def find_colors(item, path, out):
    if not isinstance(item, dict):
        return
    ty = item.get("ty")
    nm = item.get("nm", "")
    if ty == "fl" and "c" in item:
        c = item["c"].get("k")
        out.append(f"  {path} ({repr(nm)}) -> FILL: {c}")
    elif ty == "st" and "c" in item:
        c = item["c"].get("k")
        w = item.get("w", {}).get("k")
        out.append(f"  {path} ({repr(nm)}) -> STROKE: {c}, width={w}")
    for sub in item.get("it", []):
        find_colors(sub, f"{path}.it", out)
    for sub in item.get("shapes", []):
        find_colors(sub, f"{path}.shapes", out)

res = []
for t in [14, 15, 16, 20, 25, 50, 100]:
    res.append(analyze_template_colors(t))

with open("scratch/colors_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(res))

print("Analysis written to scratch/colors_analysis.txt")
