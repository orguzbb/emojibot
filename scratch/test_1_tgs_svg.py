import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, gzip
import lottie_processor

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="red"/>
  <path d="M20 20 L80 80"/>
</svg>"""

with open("shablonlar/1.tgs", "rb") as f:
    orig_bytes = f.read()

res_bytes = lottie_processor.process_tgs_template(orig_bytes, svg_content=test_svg, scale=1.0)
res_json = json.loads(gzip.decompress(res_bytes).decode("utf-8"))
res_str = json.dumps(res_json)
print("1.tgs Result size:", len(res_bytes))
print("1.tgs Contains 'SVG_Symbol':", "SVG_Symbol" in res_str)
