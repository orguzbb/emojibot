import json, gzip
import lottie_processor

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <polygon points="50,15 61,38 86,38 66,54 73,78 50,62 27,78 34,54 14,38 39,38" fill="#ffd700" stroke="#ff6f00" stroke-width="2"/>
</svg>"""

with open("shablonlar/14.tgs", "rb") as f:
    tgs_bytes = f.read()

# Test process_tgs_template with custom badge colors!
res = lottie_processor.process_tgs_template(
    template_bytes=tgs_bytes,
    svg_content=test_svg,
    scale=1.0
)

print("Standard output size:", len(res))
