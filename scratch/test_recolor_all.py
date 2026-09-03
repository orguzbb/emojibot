import json, gzip

def analyze_and_recolor(tpl_id, new_hex="#EEB419"):
    with open(f"shablonlar/{tpl_id}.tgs", "rb") as f:
        d = json.loads(gzip.decompress(f.read()))

    h = new_hex.lstrip("#")
    r, g, b = int(h[0:2], 16)/255.0, int(h[2:4], 16)/255.0, int(h[4:6], 16)/255.0

    replaced_count = 0

    def walk(item):
        nonlocal replaced_count
        if not isinstance(item, dict):
            return
        # Don't touch the text / SVG replacement group
        if item.get("nm") in ("SVG_Symbol", "TextGroup", "Text Layer"):
            # Note: in Text Layer, the letters are replaced, but let's check
            pass
        
        ty = item.get("ty")
        if ty in ("fl", "st") and "c" in item:
            c = item["c"].get("k")
            if isinstance(c, list) and len(c) >= 3 and isinstance(c[0], (int, float)):
                cr, cg, cb = c[:3]
                # Is it the outer white edge/border? (cr > 0.85 and cg > 0.85 and cb > 0.85)
                if cr > 0.85 and cg > 0.85 and cb > 0.85:
                    item["c"]["k"] = [r, g, b, c[3] if len(c) > 3 else 1.0]
                    replaced_count += 1

        for it in item.get("it", []):
            walk(it)
        for sh in item.get("shapes", []):
            walk(sh)

    for l in d.get("layers", []):
        # We only want to recolor non-text layers or badge layers
        if l.get("nm") != "Text Layer":
            walk(l)
    for a in d.get("assets", []):
        for l in a.get("layers", []):
            if l.get("nm") != "Text Layer":
                walk(l)

    print(f"Template {tpl_id}.tgs: replaced {replaced_count} white badge colors with {new_hex} ([{r:.2f}, {g:.2f}, {b:.2f}])")
    return d

for t in [14, 15, 16, 20, 25, 30, 50, 75, 100, 117]:
    analyze_and_recolor(t, "#EEB419")
