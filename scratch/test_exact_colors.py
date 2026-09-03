import json, gzip
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from lottie_processor import process_tgs_template, parse_svg_color

def check_exact_colors(t_num, badge_color="#EEB419", badge_bg_color="#1A1A2E", text_color="#00FFCC"):
    t_path = Path(f"shablonlar/{t_num}.tgs")
    with open(t_path, "rb") as f:
        raw_bytes = f.read()

    processed = process_tgs_template(
        template_bytes=raw_bytes,
        text="TEST",
        font_path="fonts/stapel.ttf",
        scale=1.0,
        badge_color=badge_color,
        badge_bg_color=badge_bg_color,
        text_color=text_color
    )
    
    data = json.loads(gzip.decompress(processed))
    
    c_b = parse_svg_color(badge_color)[:3]
    c_bg = parse_svg_color(badge_bg_color)[:3]
    c_t = parse_svg_color(text_color)[:3]
    
    found_b = 0
    found_bg = 0
    found_t = 0
    
    def walk(item):
        nonlocal found_b, found_bg, found_t
        if not isinstance(item, dict): return
        if item.get("ty") in ("fl", "st") and "c" in item:
            c = item["c"].get("k")
            if isinstance(c, list) and len(c) >= 3 and isinstance(c[0], (int, float)):
                if abs(c[0]-c_b[0]) < 0.01 and abs(c[1]-c_b[1]) < 0.01 and abs(c[2]-c_b[2]) < 0.01:
                    found_b += 1
                if abs(c[0]-c_bg[0]) < 0.01 and abs(c[1]-c_bg[1]) < 0.01 and abs(c[2]-c_bg[2]) < 0.01:
                    found_bg += 1
                if abs(c[0]-c_t[0]) < 0.01 and abs(c[1]-c_t[1]) < 0.01 and abs(c[2]-c_t[2]) < 0.01:
                    found_t += 1
        for it in item.get("it", []): walk(it)
        for sh in item.get("shapes", []): walk(sh)

    for l in data.get("layers", []): walk(l)
    for a in data.get("assets", []):
        for l in a.get("layers", []): walk(l)

    print(f"{t_num}.tgs -> Found Outer: {found_b}, Inner: {found_bg}, Text: {found_t}")

for t in [1, 14, 15, 20, 50, 100, 117]:
    check_exact_colors(t)
