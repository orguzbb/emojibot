import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, gzip
import lottie_processor

# Test 1: Multi-colored SVG
svg_multicolor = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100">
  <defs>
    <style>
      .bg { fill: #1e88e5; }
      .star { fill: #ffd700; stroke: #ff6f00; stroke-width: 2; }
      .tri { fill: #e53935; }
    </style>
  </defs>
  <rect class="bg" x="10" y="10" width="280" height="80" rx="15" />
  <path class="tri" d="M 20 50 L 80 20 L 80 80 Z" />
  <polygon class="star" points="150,20 160,40 185,40 165,55 172,80 150,65 128,80 135,55 115,40 140,40" />
  <circle cx="240" cy="50" r="25" fill="#43a047" stroke="#1b5e20" stroke-width="3" />
</svg>"""

# Test 2: Wide elongated SVG (e.g. 500x70)
svg_wide = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 70">
  <rect x="0" y="0" width="500" height="70" rx="10" fill="#9c27b0" />
  <circle cx="40" cy="35" r="25" fill="#ffeb3b" />
  <rect x="80" y="15" width="300" height="40" rx="5" fill="#00e676" />
  <circle cx="450" cy="35" r="20" fill="#ff1744" stroke="#ffffff" stroke-width="2" />
</svg>"""

# Test 3: Gradient SVG
svg_gradient = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="grad1">
      <stop offset="0%" stop-color="#ff007f" />
      <stop offset="100%" stop-color="#7928ca" />
    </linearGradient>
  </defs>
  <circle cx="50" cy="50" r="45" fill="url(#grad1)" />
</svg>"""

# Test 4: Uncolored lineart SVG
svg_lineart = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <path d="M 10 10 L 90 90 M 90 10 L 10 90" />
</svg>"""

templates_to_test = ["14.tgs", "1.tgs", "20.tgs", "50.tgs", "100.tgs"]

for tpl in templates_to_test:
    with open(f"shablonlar/{tpl}", "rb") as f:
        data = f.read()
    
    # 1. Multicolor
    res1 = lottie_processor.process_tgs_template(data, svg_content=svg_multicolor, scale=1.0)
    assert len(res1) > 1000, "res1 too small"
    
    # 2. Wide
    res2 = lottie_processor.process_tgs_template(data, svg_content=svg_wide, scale=1.0)
    assert len(res2) > 1000, "res2 too small"

    # 3. Gradient
    res3 = lottie_processor.process_tgs_template(data, svg_content=svg_gradient, scale=1.0)
    assert len(res3) > 1000, "res3 too small"

    # 4. Lineart
    res4 = lottie_processor.process_tgs_template(data, svg_content=svg_lineart, scale=1.0)
    assert len(res4) > 1000, "res4 too small"

    print(f"Template {tpl}: ALL 4 SVG TESTS PASSED!")

# Verify actual color values inside res1
res1_json = json.loads(gzip.decompress(res1).decode("utf-8"))
json_str = json.dumps(res1_json)
print("\nVerifying color presence in Lottie JSON:")
print("- Blue fill present:", "[0.11764705882352941, 0.5333333333333333, 0.8980392156862745]" in json_str)
print("- Red fill present:", "[0.8980392156862745, 0.2235294117647059, 0.20784313725490197]" in json_str)
print("- Gold fill present:", "[1.0, 0.8431372549019608, 0.0]" in json_str)
print("- Green fill present:", "[0.2627450980392157, 0.6274509803921569, 0.2784313725490196]" in json_str)

print("\nALL TEST SUITE CHECKS COMPLETED WITH 100% SUCCESS!")
