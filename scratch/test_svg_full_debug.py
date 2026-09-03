import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import traceback
import lottie_processor

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect x="10" y="10" width="80" height="80" rx="10"/>
  <circle cx="50" cy="50" r="30"/>
  <path d="M 20 20 L 80 80 M 80 20 L 20 80"/>
</svg>"""

try:
    cleaned = lottie_processor.validate_and_clean_svg(test_svg)
    print("validate_and_clean_svg passed!")
except Exception as e:
    print("validate_and_clean_svg failed:")
    traceback.print_exc()

try:
    with open("shablonlar/14.tgs", "rb") as f:
        tgs_bytes = f.read()
    res = lottie_processor.process_tgs_template(template_bytes=tgs_bytes, svg_content=test_svg, scale=1.0)
    print("process_tgs_template SVG passed! Output bytes:", len(res))
except Exception as e:
    print("process_tgs_template failed:")
    traceback.print_exc()
