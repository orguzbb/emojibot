import json, gzip

def inspect_tpl(tpl_id):
    with open(f"shablonlar/{tpl_id}.tgs", "rb") as f:
        data = json.loads(gzip.decompress(f.read()))
    print(f"\n=================== TEMPLATE {tpl_id}.tgs ===================")
    for i, l in enumerate(data.get("layers", [])):
        print(f"Layer {i}: nm='{l.get('nm')}', ty={l.get('ty')}")
        for j, sh in enumerate(l.get("shapes", [])):
            dump_shape(sh, f"  Shape {j}")

def dump_shape(sh, prefix):
    nm = sh.get("nm", "")
    ty = sh.get("ty", "")
    color_info = ""
    if ty == "fl" and "c" in sh:
        color_info = f" -> Fill: {sh['c'].get('k')}"
    elif ty == "st" and "c" in sh:
        color_info = f" -> Stroke: {sh['c'].get('k')}, w={sh.get('w', {}).get('k')}"
    elif ty == "gfl":
        color_info = f" -> GradFill"
    elif ty == "gst":
        color_info = f" -> GradStroke"
    print(f"{prefix}: nm='{nm}', ty='{ty}'{color_info}")
    if "it" in sh:
        for k, sub in enumerate(sh["it"]):
            dump_shape(sub, f"{prefix} -> it[{k}]")

for t in [14, 15, 20, 50]:
    inspect_tpl(t)
