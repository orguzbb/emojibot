import json, gzip, copy
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from lottie_processor import parse_svg_color

def apply_all_colors_test(data: dict, badge_color=None, badge_bg_color=None, text_color=None):
    cloned = copy.deepcopy(data)
    c_primary = parse_svg_color(badge_color)[:3] if badge_color else None
    c_secondary = parse_svg_color(badge_bg_color)[:3] if badge_bg_color else None
    c_text = parse_svg_color(text_color)[:3] if text_color else None
    
    recolored = {"outer": 0, "inner": 0, "text": 0}

    def walk(item, is_in_text=False):
        if not isinstance(item, dict): return
        nm = str(item.get("nm", ""))
        
        # Don't touch SVG user graphics
        if nm == "SVG_Symbol" or "SVG Path" in nm or "Logo path" in nm:
            return
            
        is_text_node = is_in_text or nm in ("TextGroup", "Text Layer", "NAME", "EMOJI 1") or (len(nm) == 1 and nm.isalnum())
        
        ty = item.get("ty")
        if ty in ("fl", "st") and "c" in item:
            c_val = item["c"].get("k")
            if isinstance(c_val, list) and len(c_val) >= 3 and isinstance(c_val[0], (int, float)):
                cr, cg, cb = c_val[:3]
                alpha = c_val[3] if len(c_val) > 3 else 1.0
                
                if is_text_node:
                    if c_text:
                        item["c"]["k"] = [c_text[0], c_text[1], c_text[2], alpha]
                        recolored["text"] += 1
                else:
                    # Outer border (white)
                    if c_primary and cr > 0.82 and cg > 0.82 and cb > 0.82:
                        item["c"]["k"] = [c_primary[0], c_primary[1], c_primary[2], alpha]
                        recolored["outer"] += 1
                    # Inner base (black/dark)
                    elif c_secondary and cr < 0.18 and cg < 0.18 and cb < 0.18:
                        item["c"]["k"] = [c_secondary[0], c_secondary[1], c_secondary[2], alpha]
                        recolored["inner"] += 1

        for it in item.get("it", []):
            walk(it, is_text_node)
        for sh in item.get("shapes", []):
            walk(sh, is_text_node)

    for l in cloned.get("layers", []):
        walk(l)
    for a in cloned.get("assets", []):
        for l in a.get("layers", []):
            walk(l)

    return recolored

for t_num in [1, 5, 14, 15, 20, 50, 75, 100, 117]:
    p = Path(f"shablonlar/{t_num}.tgs")
    if p.exists():
        d = json.loads(gzip.decompress(p.read_bytes()))
        res = apply_all_colors_test(d, badge_color="#EEB419", badge_bg_color="#1A1A2E", text_color="#FF0055")
        print(f"{t_num}.tgs -> Outer: {res['outer']}, Inner: {res['inner']}, Text: {res['text']}")
