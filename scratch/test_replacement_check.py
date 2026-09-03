import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, gzip
import lottie_processor

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="red"/>
  <path d="M20 20 L80 80"/>
</svg>"""

with open("shablonlar/14.tgs", "rb") as f:
    orig_bytes = f.read()

res_bytes = lottie_processor.process_tgs_template(orig_bytes, svg_content=test_svg, scale=1.0)
res_json = json.loads(gzip.decompress(res_bytes).decode("utf-8"))

print(f"Original size: {len(orig_bytes)}, Result size: {len(res_bytes)}")

# Check if 'N', 'A', 'M', 'E' still exist in res_json
res_str = json.dumps(res_json)
print("Contains 'Logo path':", "Logo path" in res_str)
print("Contains 'SVG_Symbol':", "SVG_Symbol" in res_str)
print("Contains 'SVG Path':", "SVG Path" in res_str)
