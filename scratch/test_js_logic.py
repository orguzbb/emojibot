import json, gzip

with open("shablonlar/14.tgs", "rb") as f:
    orig = json.loads(gzip.decompress(f.read()).decode("utf-8"))

def apply_badge_color_js_logic(json_obj, hex_color):
    hex_color = hex_color.strip().lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0

    count = 0
    def walk(item):
        nonlocal count
        if not isinstance(item, dict): return
        nm = str(item.get("nm", ""))
        if nm in ("SVG_Symbol", "TextGroup") or "SVG Path" in nm or "Logo path" in nm:
            return
        ty = item.get("ty")
        if ty in ("fl", "st") and "c" in item:
            c = item["c"].get("k")
            if isinstance(c, list) and len(c) >= 3 and isinstance(c[0], (int, float)):
                if c[0] > 0.82 and c[1] > 0.82 and c[2] > 0.82:
                    c[0] = r
                    c[1] = g
                    c[2] = b
                    count += 1
        for it in item.get("it", []): walk(it)
        for sh in item.get("shapes", []): walk(sh)

    for l in json_obj.get("layers", []): walk(l)
    for a in json_obj.get("assets", []):
        for l in a.get("layers", []): walk(l)

    print(f"Recolored {count} shapes to #{hex_color}")

apply_badge_color_js_logic(orig, "EEB419")
