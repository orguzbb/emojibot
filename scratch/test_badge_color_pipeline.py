import json, gzip
import lottie_processor

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#00e676" stroke="#004d40" stroke-width="3"/>
</svg>"""

with open("shablonlar/14.tgs", "rb") as f:
    orig = f.read()

# Test 1: SVG mode + Badge Color #EEB419
res_svg = lottie_processor.process_tgs_template(
    template_bytes=orig,
    svg_content=test_svg,
    badge_color="#EEB419",
    scale=1.0
)

# Test 2: Text mode ("AZIZ") + Badge Color #EEB419
res_text = lottie_processor.process_tgs_template(
    template_bytes=orig,
    text="AZIZ",
    font_path="fonts/stapel.ttf",
    badge_color="#EEB419",
    scale=1.0
)

print("res_svg size:", len(res_svg))
print("res_text size:", len(res_text))
