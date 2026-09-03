import gzip, json
from pathlib import Path

templates_dir = Path("shablonlar")
all_files = sorted(templates_dir.glob("*.tgs"), key=lambda f: (int(f.stem) if f.stem.isdigit() else 9999, f.name))

summary = {}
for f in all_files:
    data = json.loads(gzip.decompress(f.read_bytes()))
    colors = []
    
    def walk(item):
        if not isinstance(item, dict): return
        nm = str(item.get("nm", ""))
        if nm in ("SVG_Symbol", "TextGroup") or "SVG Path" in nm or "Logo path" in nm:
            return
        if item.get("ty") in ("fl", "st") and "c" in item:
            c = item["c"].get("k")
            if isinstance(c, list) and len(c) >= 3 and isinstance(c[0], (int, float)):
                r, g, b = [round(x, 3) for x in c[:3]]
                colors.append((item.get("ty"), nm, [r, g, b]))
        for it in item.get("it", []): walk(it)
        for sh in item.get("shapes", []): walk(sh)

    for l in data.get("layers", []): walk(l)
    for a in data.get("assets", []):
        for l in a.get("layers", []): walk(l)
    summary[f.name] = colors

print("Sample templates non-text colors:")
for name in ["1.tgs", "5.tgs", "14.tgs", "15.tgs", "20.tgs", "50.tgs", "75.tgs", "100.tgs", "117.tgs"]:
    print(f"\n{name}:")
    for ty, nm, c in summary.get(name, []):
        print(f"  {ty} '{nm}': {c}")
