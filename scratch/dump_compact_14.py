import json, gzip

def inspect_all_layers(tpl_id):
    with open(f"shablonlar/{tpl_id}.tgs", "rb") as f:
        data = json.loads(gzip.decompress(f.read()))
    print(f"\n=================== TEMPLATE {tpl_id}.tgs ===================")
    for i, l in enumerate(data.get("layers", [])):
        lnm = repr(l.get('nm'))
        print(f"Layer {i}: nm={lnm}, ty={l.get('ty')}")
        for j, sh in enumerate(l.get("shapes", [])):
            dump_shape_compact(sh, f"  L{i} S{j}")

def dump_shape_compact(sh, prefix):
    nm = repr(sh.get("nm", ""))
    ty = sh.get("ty", "")
    info = ""
    if ty == "fl" and "c" in sh:
        info = f" [FILL: {sh['c'].get('k')}]"
    elif ty == "st" and "c" in sh:
        info = f" [STROKE: {sh['c'].get('k')}, w={sh.get('w', {}).get('k')}]"
    print(f"{prefix}: nm={nm}, ty={ty}{info}")
    if "it" in sh:
        for k, sub in enumerate(sh["it"]):
            dump_shape_compact(sub, f"{prefix}.{k}")

inspect_all_layers(14)
