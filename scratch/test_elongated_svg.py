import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, gzip
import xml.etree.ElementTree as ET
import lottie_processor

# Wide elongated SVG (e.g. 400x80)
wide_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 80">
  <rect x="5" y="5" width="390" height="70" rx="20" fill="#ff5722" stroke="#bf360c" stroke-width="4"/>
  <circle cx="50" cy="40" r="25" fill="#ffeb3b" stroke="#f57f17" stroke-width="3"/>
  <path d="M 40 40 L 50 25 L 60 40 L 55 55 L 45 55 Z" fill="#2196f3"/>
  <rect x="100" y="20" width="180" height="40" rx="8" fill="#4caf50"/>
  <circle cx="340" cy="40" r="20" fill="#9c27b0"/>
</svg>"""

# Tall elongated SVG (e.g. 80x300)
tall_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 300">
  <rect x="5" y="5" width="70" height="290" rx="15" fill="#00bcd4"/>
  <circle cx="40" cy="50" r="25" fill="#e91e63"/>
  <polygon points="40,110 65,150 15,150" fill="#ffc107"/>
  <circle cx="40" cy="220" r="25" fill="#3f51b5"/>
</svg>"""

print("Testing wide and tall SVGs...")
