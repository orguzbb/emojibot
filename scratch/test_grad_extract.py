import re
import xml.etree.ElementTree as ET

def extract_svg_gradients(root_element, class_styles=None) -> dict:
    class_styles = class_styles or {}
    grad_map = {}
    for el in root_element.iter():
        tag = el.tag.split('}')[-1].lower() if isinstance(el.tag, str) else ''
        if tag in ('lineargradient', 'radialgradient'):
            grad_id = el.attrib.get('id')
            if not grad_id:
                continue
            stops = []
            for child in el.iter():
                ctag = child.tag.split('}')[-1].lower() if isinstance(child.tag, str) else ''
                if ctag == 'stop':
                    # Color from stop-color attribute or style
                    sc = child.attrib.get('stop-color')
                    if not sc and 'style' in child.attrib:
                        for part in child.attrib['style'].split(';'):
                            if 'stop-color' in part:
                                sc = part.split(':', 1)[1].strip()
                    if sc:
                        stops.append(sc)
            if stops:
                grad_map[grad_id] = stops
    return grad_map

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="my-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF5722" />
      <stop offset="100%" style="stop-color: #4CAF50;" />
    </linearGradient>
  </defs>
  <path fill="url(#my-grad)" d="M10 10 L90 90" />
</svg>"""

root = ET.fromstring(test_svg)
grads = extract_svg_gradients(root)
print("Extracted gradients:", grads)
