import json, gzip

def analyze_all_elements(tpl_id):
    with open(f"shablonlar/{tpl_id}.tgs", "rb") as f:
        data = json.loads(gzip.decompress(f.read()))
    print(f"========== {tpl_id}.tgs ==========")
    for i, l in enumerate(data.get("layers", [])):
        lnm = l.get('nm', '')
        print(f"Layer {i}: '{lnm}'")
        for j, sh in enumerate(l.get("shapes", [])):
            print_shapes(sh, "  ")

def print_shapes(sh, indent):
    nm = sh.get("nm", "")
    ty = sh.get("ty", "")
    color = ""
    if ty == "fl":
        color = f" FL={sh.get('c',{}).get('k')}"
    elif ty == "st":
        color = f" ST={sh.get('c',{}).get('k')}"
    print(f"{indent}- '{nm}' ({ty}){color}")
    for it in sh.get("it", []):
        print_shapes(it, indent + "  ")

for t in [14, 15, 20]:
    analyze_all_elements(t)
