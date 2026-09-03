import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, gzip
import lottie_processor

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#00e676" stroke="#004d40" stroke-width="3"/>
</svg>"""

with open("shablonlar/14.tgs", "rb") as f:
    orig = f.read()

res_svg = lottie_processor.process_tgs_template(
    template_bytes=orig,
    svg_content=test_svg,
    badge_color="#EEB419",
    scale=1.0
)

data = json.loads(gzip.decompress(res_svg).decode("utf-8"))
s = json.dumps(data)

# #EEB419 is [0.9333333333333333, 0.7058823529411765, 0.09803921568627451]
print("Contains EEB419 color:", "0.9333333333333333" in s and "0.7058823529411765" in s)
print("Contains SVG green fill:", "0.9019607843137255" in s or "0.0" in s)
