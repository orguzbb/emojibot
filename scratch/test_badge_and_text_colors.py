import json, gzip
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).parent.parent))
from lottie_processor import process_tgs_template, parse_svg_color, apply_badge_color_to_template

def test_template(t_num, badge_color="#EEB419", badge_bg_color="#1A1A2E", text_color="#00FFCC"):
    t_path = Path(f"shablonlar/{t_num}.tgs")
    if not t_path.exists():
        print(f"Template {t_num} not found")
        return
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
    data_str = json.dumps(data)
    
    # Check if colors appear in json
    c_badge = parse_svg_color(badge_color)[:3]
    c_bg = parse_svg_color(badge_bg_color)[:3]
    c_txt = parse_svg_color(text_color)[:3]
    
    badge_found = any(str(round(c_badge[0], 3)) in data_str and str(round(c_badge[1], 3)) in data_str for _ in [1])
    bg_found = any(str(round(c_bg[0], 3)) in data_str and str(round(c_bg[1], 3)) in data_str for _ in [1])
    txt_found = any(str(round(c_txt[0], 3)) in data_str and str(round(c_txt[1], 3)) in data_str for _ in [1])
    
    print(f"Template {t_num}.tgs -> Badge({badge_color}): {badge_found} | Bg({badge_bg_color}): {bg_found} | Text({text_color}): {txt_found}")

for t in [1, 5, 14, 15, 20, 50, 100, 117]:
    test_template(t)
