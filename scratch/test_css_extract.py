import re
import xml.etree.ElementTree as ET

def parse_css_style_declarations(style_text: str) -> dict:
    styles = {}
    if not style_text:
        return styles
    for item in style_text.split(';'):
        if ':' in item:
            k, v = item.split(':', 1)
            styles[k.strip().lower()] = v.strip()
    return styles

def extract_svg_css_classes(root_element) -> dict:
    class_map = {}
    for el in root_element.iter():
        tag = el.tag.split('}')[-1].lower() if isinstance(el.tag, str) else ''
        if tag == 'style' and el.text:
            # Match .classname { key: value; ... }
            matches = re.findall(r'\.([a-zA-Z0-9_\-]+)\s*\{([^}]+)\}', el.text)
            for cls_name, decls in matches:
                if cls_name not in class_map:
                    class_map[cls_name] = {}
                class_map[cls_name].update(parse_css_style_declarations(decls))
    return class_map

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <style>
      .cls-1 { fill: #f34235; }
      .cls-2 { fill: #2196f3; stroke: #0d47a1; stroke-width: 2; }
    </style>
  </defs>
  <path class="cls-1" d="M10 10 L90 90" />
  <circle class="cls-2" cx="50" cy="50" r="30" style="fill: gold;" />
</svg>"""

root = ET.fromstring(test_svg)
cls_map = extract_svg_css_classes(root)
print("Extracted CSS classes:", cls_map)
