import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import glob
import lottie_processor

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <g transform="translate(10, 10) scale(0.8)">
    <circle cx="50" cy="50" r="40" fill="none" stroke="#000" stroke-width="4"/>
    <polygon points="50,15 61,38 86,38 66,54 73,78 50,62 27,78 34,54 14,38 39,38" fill="gold"/>
  </g>
</svg>"""

tgs_files = glob.glob("shablonlar/*.tgs")
print(f"Testing SVG rendering on {len(tgs_files)} templates...")

success_count = 0
for fpath in tgs_files:
    with open(fpath, "rb") as f:
        data = f.read()
    try:
        out = lottie_processor.process_tgs_template(template_bytes=data, svg_content=test_svg, scale=1.0)
        assert len(out) > 500, f"Output too small: {len(out)}"
        success_count += 1
    except Exception as e:
        print(f"FAILED on {fpath}: {e}")

print(f"SUCCESS: {success_count}/{len(tgs_files)} templates rendered with SVG perfectly!")
