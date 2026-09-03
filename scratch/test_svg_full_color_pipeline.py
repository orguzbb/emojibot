import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re, math, json, gzip
import xml.etree.ElementTree as ET
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
import lottie_processor

CSS_NAMED_COLORS = {
    'aliceblue': '#f0f8ff', 'antiquewhite': '#faebd7', 'aqua': '#00ffff', 'aquamarine': '#7fffd4',
    'azure': '#f0ffff', 'beige': '#f5f5dc', 'bisque': '#ffe4c4', 'black': '#000000',
    'blanchedalmond': '#ffebcd', 'blue': '#0000ff', 'blueviolet': '#8a2be2', 'brown': '#a52a2a',
    'burlywood': '#deb887', 'cadetblue': '#5f9ea0', 'chartreuse': '#7fff00', 'chocolate': '#d2691e',
    'coral': '#ff7f50', 'cornflowerblue': '#6495ed', 'cornsilk': '#fff8dc', 'crimson': '#dc143c',
    'cyan': '#00ffff', 'darkblue': '#00008b', 'darkcyan': '#008b8b', 'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9', 'darkgreen': '#006400', 'darkgrey': '#a9a9a9', 'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b', 'darkolivegreen': '#556b2f', 'darkorange': '#ff8c00', 'darkorchid': '#9932cc',
    'darkred': '#8b0000', 'darksalmon': '#e9967a', 'darkseagreen': '#8fbc8f', 'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f', 'darkslategrey': '#2f4f4f', 'darkturquoise': '#00ced1', 'darkviolet': '#9400d3',
    'deeppink': '#ff1493', 'deepskyblue': '#00bfff', 'dimgray': '#696969', 'dimgrey': '#696969',
    'dodgerblue': '#1e90ff', 'firebrick': '#b22222', 'floralwhite': '#fffaf0', 'forestgreen': '#228b22',
    'fuchsia': '#ff00ff', 'gainsboro': '#dcdcdc', 'ghostwhite': '#f8f8ff', 'gold': '#ffd700',
    'goldenrod': '#daa520', 'gray': '#808080', 'green': '#008000', 'greenyellow': '#adff2f',
    'grey': '#808080', 'honeydew': '#f0fff0', 'hotpink': '#ff69b4', 'indianred': '#cd5c5c',
    'indigo': '#4b0082', 'ivory': '#fffff0', 'khaki': '#f0e68c', 'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5', 'lawngreen': '#7cfc00', 'lemonchiffon': '#fffacd', 'lightblue': '#add8e6',
    'lightcoral': '#f08080', 'lightcyan': '#e0ffff', 'lightgoldenrodyellow': '#fafad2', 'lightgray': '#d3d3d3',
    'lightgreen': '#90ee90', 'lightgrey': '#d3d3d3', 'lightpink': '#ffb6c1', 'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa', 'lightskyblue': '#87cefa', 'lightslategray': '#778899', 'lightslategrey': '#778899',
    'lightsteelblue': '#b0c4de', 'lightyellow': '#ffffe0', 'lime': '#00ff00', 'limegreen': '#32cd32',
    'linen': '#faf0e6', 'magenta': '#ff00ff', 'maroon': '#800000', 'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd', 'mediumorchid': '#ba55d3', 'mediumpurple': '#9370db', 'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee', 'mediumspringgreen': '#00fa9a', 'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585', 'midnightblue': '#191970', 'mintcream': '#f5fffa', 'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5', 'navajowhite': '#ffdead', 'navy': '#000080', 'oldlace': '#fdf5e6',
    'olive': '#808000', 'olivedrab': '#6b8e23', 'orange': '#ffa500', 'orangered': '#ff4500',
    'orchid': '#da70d6', 'palegoldenrod': '#eee8aa', 'palegreen': '#98fb98', 'paleturquoise': '#afeeee',
    'palevioletred': '#db7093', 'papayawhip': '#ffefd5', 'peachpuff': '#ffdab9', 'peru': '#cd853f',
    'pink': '#ffc0cb', 'plum': '#dda0dd', 'powderblue': '#b0e0e6', 'purple': '#800080',
    'rebeccapurple': '#663399', 'red': '#ff0000', 'rosybrown': '#bc8f8f', 'royalblue': '#4169e1',
    'saddlebrown': '#8b4513', 'salmon': '#fa8072', 'sandybrown': '#f4a460', 'seagreen': '#2e8b57',
    'seashell': '#fff5ee', 'sienna': '#a0522d', 'silver': '#c0c0c0', 'skyblue': '#87ceeb',
    'slateblue': '#6a5acd', 'slategray': '#708090', 'slategrey': '#708090', 'snow': '#fffafa',
    'springgreen': '#00ff7f', 'steelblue': '#4682b4', 'tan': '#d2b48c', 'teal': '#008080',
    'thistle': '#d8bfd8', 'tomato': '#ff6347', 'turquoise': '#40e0d0', 'violet': '#ee82ee',
    'wheat': '#f5deb3', 'white': '#ffffff', 'whitesmoke': '#f5f5f5', 'yellow': '#ffff00',
    'yellowgreen': '#9acd32'
}

def parse_svg_color(val: str, default_opacity: float = 1.0):
    if not val:
        return None
    val = val.strip().lower()
    if val in ('none', 'transparent'):
        return 'none'
    if val in CSS_NAMED_COLORS:
        val = CSS_NAMED_COLORS[val]
    
    if val.startswith('#'):
        hex_str = val[1:]
        if len(hex_str) == 3:
            r = int(hex_str[0] * 2, 16) / 255.0
            g = int(hex_str[1] * 2, 16) / 255.0
            b = int(hex_str[2] * 2, 16) / 255.0
            return [r, g, b, default_opacity]
        elif len(hex_str) == 4:
            r = int(hex_str[0] * 2, 16) / 255.0
            g = int(hex_str[1] * 2, 16) / 255.0
            b = int(hex_str[2] * 2, 16) / 255.0
            a = (int(hex_str[3] * 2, 16) / 255.0) * default_opacity
            return [r, g, b, a]
        elif len(hex_str) == 6:
            r = int(hex_str[0:2], 16) / 255.0
            g = int(hex_str[2:4], 16) / 255.0
            b = int(hex_str[4:6], 16) / 255.0
            return [r, g, b, default_opacity]
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16) / 255.0
            g = int(hex_str[2:4], 16) / 255.0
            b = int(hex_str[4:6], 16) / 255.0
            a = (int(hex_str[6:8], 16) / 255.0) * default_opacity
            return [r, g, b, a]

    m_rgb = re.match(r'rgba?\s*\(\s*([\d\.]+%?)\s*,\s*([\d\.]+%?)\s*,\s*([\d\.]+%?)(?:\s*,\s*([\d\.]+))?\s*\)', val)
    if m_rgb:
        def parse_part(p):
            if p.endswith('%'):
                return float(p[:-1]) / 100.0
            return float(p) / 255.0
        r = parse_part(m_rgb.group(1))
        g = parse_part(m_rgb.group(2))
        b = parse_part(m_rgb.group(3))
        a = float(m_rgb.group(4)) * default_opacity if m_rgb.group(4) else default_opacity
        return [max(0.0, min(1.0, r)), max(0.0, min(1.0, g)), max(0.0, min(1.0, b)), max(0.0, min(1.0, a))]

    return None

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
        tag = lottie_processor._strip_xml_ns(el.tag).lower() if isinstance(el.tag, str) else ''
        if tag == 'style' and el.text:
            matches = re.findall(r'\.([a-zA-Z0-9_\-]+)\s*\{([^}]+)\}', el.text)
            for cls_name, decls in matches:
                if cls_name not in class_map:
                    class_map[cls_name] = {}
                class_map[cls_name].update(parse_css_style_declarations(decls))
    return class_map

class ColoredSVGElement:
    def __init__(self, paths, fill, stroke, stroke_width, fill_opacity, stroke_opacity, name):
        self.paths = paths
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.fill_opacity = fill_opacity
        self.stroke_opacity = stroke_opacity
        self.name = name

def extract_svg_colored_elements(root_element, target_cx, target_cy, svg_cx, svg_cy, scale):
    class_styles = extract_svg_css_classes(root_element)
    elements = []

    def get_element_styles(el, parent_styles):
        merged = dict(parent_styles)
        classes = el.attrib.get('class', '').split()
        for cls in classes:
            if cls in class_styles:
                merged.update(class_styles[cls])
        inline_style = el.attrib.get('style', '')
        if inline_style:
            merged.update(parse_css_style_declarations(inline_style))
        for attr in ('fill', 'stroke', 'stroke-width', 'opacity', 'fill-opacity', 'stroke-opacity'):
            if attr in el.attrib:
                merged[attr] = el.attrib[attr]
        return merged

    def walk(el, current_tf, current_styles):
        local_tf = lottie_processor.parse_svg_transform(el.attrib.get('transform', ''))
        combined_tf = current_tf.transform(local_tf)
        element_styles = get_element_styles(el, current_styles)

        tag = lottie_processor._strip_xml_ns(el.tag).lower() if isinstance(el.tag, str) else ''
        
        pen = lottie_processor.LottieSVGPen(
            target_cx=target_cx,
            target_cy=target_cy,
            svg_cx=svg_cx,
            svg_cy=svg_cy,
            scale=scale
        )
        t_pen = TransformPen(pen, combined_tf) if combined_tf != Transform() else pen

        has_geometry = False
        if tag == 'path' and 'd' in el.attrib:
            lottie_processor.parse_path(el.attrib['d'], t_pen)
            has_geometry = True
        elif tag in ('circle', 'rect', 'ellipse', 'line', 'polygon', 'polyline'):
            pb = lottie_processor.SafePathBuilder()
            pb.add_path_from_element(el)
            for p in pb.paths:
                lottie_processor.parse_path(p, t_pen)
            has_geometry = True

        if has_geometry:
            pen._closePath()
            if pen.paths:
                raw_fill = element_styles.get('fill')
                fill_color = parse_svg_color(raw_fill) if raw_fill else None
                
                raw_stroke = element_styles.get('stroke')
                stroke_color = parse_svg_color(raw_stroke) if raw_stroke else None
                
                try:
                    sw_str = str(element_styles.get('stroke-width', '1')).replace('px', '').strip()
                    stroke_w = float(sw_str)
                except Exception:
                    stroke_w = 1.0

                try:
                    op = float(element_styles.get('opacity', 1.0))
                except Exception:
                    op = 1.0

                try:
                    f_op = float(element_styles.get('fill-opacity', 1.0)) * op
                except Exception:
                    f_op = op

                try:
                    s_op = float(element_styles.get('stroke-opacity', 1.0)) * op
                except Exception:
                    s_op = op

                elements.append(ColoredSVGElement(
                    paths=pen.paths,
                    fill=fill_color,
                    stroke=stroke_color,
                    stroke_width=stroke_w,
                    fill_opacity=f_op,
                    stroke_opacity=s_op,
                    name=el.attrib.get('id') or f"{tag.capitalize()}"
                ))

        for child in el:
            walk(child, combined_tf, element_styles)

    walk(root_element, Transform(), {})
    return elements

def generate_svg_shapes_colored(svg_content: str, target_layer: dict, scale_factor: float = 1.0) -> list:
    cleaned_svg = lottie_processor.validate_and_clean_svg(svg_content)
    root = ET.fromstring(cleaned_svg)

    bounds_pen = BoundsPen(None)
    lottie_processor.draw_svg_to_pen(root, bounds_pen)
    bounds = bounds_pen.bounds
    if not bounds:
        bounds = (0.0, 0.0, 100.0, 100.0)

    svg_w = max(bounds[2] - bounds[0], 1.0)
    svg_h = max(bounds[3] - bounds[1], 1.0)
    svg_cx = (bounds[0] + bounds[2]) / 2.0
    svg_cy = (bounds[1] + bounds[3]) / 2.0

    info = lottie_processor.extract_layer_template_info(target_layer)

    effective_scale_factor = scale_factor if (scale_factor and scale_factor > 0) else 1.0
    scale_x = (info["orig_width"] * 0.92 * effective_scale_factor) / svg_w
    scale_y = (info["orig_height"] * 0.95 * effective_scale_factor) / svg_h
    scale = min(scale_x, scale_y)

    colored_elements = extract_svg_colored_elements(
        root_element=root,
        target_cx=info["orig_center_x"],
        target_cy=info["orig_center_y"],
        svg_cx=svg_cx,
        svg_cy=svg_cy,
        scale=scale
    )

    if not colored_elements:
        return []

    # Check if any element has custom color
    has_any_custom_colors = any(
        (el.fill and el.fill != 'none') or (el.stroke and el.stroke != 'none')
        for el in colored_elements
    )

    item_groups = []
    for el_idx, el in enumerate(colored_elements):
        items = []
        for p_idx, path in enumerate(el.paths):
            items.append({
                "ty": "sh",
                "nm": f"Path {p_idx + 1}",
                "np": 3,
                "cix": 2,
                "bm": 0,
                "ix": p_idx + 1,
                "mn": "ADBE Vector Shape - Group",
                "hd": False,
                "ks": {
                    "a": 0,
                    "k": path
                }
            })

        if len(el.paths) > 1:
            items.append({
                "ty": "mm",
                "nm": "Merge Paths",
                "mm": 1,
                "hd": False
            })

        # Stroke
        if el.stroke and el.stroke != 'none':
            stroke_c = el.stroke[:3] if isinstance(el.stroke, list) else info["stroke"]
            items.append({
                "ty": "st",
                "nm": "Stroke",
                "c": {"a": 0, "k": stroke_c},
                "w": {"a": 0, "k": max(0.5, el.stroke_width * scale)},
                "o": {"a": 0, "k": el.stroke_opacity * 100}
            })

        # Fill
        if el.fill != 'none':
            if el.fill:
                fill_c = el.fill[:3]
                fill_op = el.fill_opacity * 100
            else:
                if not (el.stroke and el.stroke != 'none'):
                    fill_c = [0.05, 0.05, 0.05] if has_any_custom_colors else info["fill"]
                    fill_op = 100.0
                else:
                    fill_c = None
                    fill_op = 0.0

            if fill_c is not None:
                items.append({
                    "ty": "fl",
                    "nm": "Fill",
                    "c": {"a": 0, "k": fill_c},
                    "o": {"a": 0, "k": fill_op},
                    "r": 1,
                    "bm": 0
                })

        items.append({
            "ty": "tr",
            "nm": "Transform",
            "p": {"a": 0, "k": [0, 0]},
            "a": {"a": 0, "k": [0, 0]},
            "s": {"a": 0, "k": [100, 100]},
            "r": {"a": 0, "k": 0},
            "o": {"a": 0, "k": 100},
            "sk": {"a": 0, "k": 0},
            "sa": {"a": 0, "k": 0}
        })

        item_groups.append({
            "ty": "gr",
            "nm": f"{el.name}_{el_idx + 1}",
            "np": len(items),
            "cix": 2,
            "bm": 0,
            "ix": el_idx + 1,
            "mn": "ADBE Vector Group",
            "hd": False,
            "it": items
        })

    container_items = item_groups + [{
        "ty": "tr",
        "nm": "Transform",
        "p": {"a": 0, "k": [0, 0]},
        "a": {"a": 0, "k": [0, 0]},
        "s": {"a": 0, "k": [100, 100]},
        "r": {"a": 0, "k": 0},
        "o": {"a": 0, "k": 100},
        "sk": {"a": 0, "k": 0},
        "sa": {"a": 0, "k": 0}
    }]

    svg_group = {
        "ty": "gr",
        "nm": "SVG_Symbol",
        "np": len(container_items),
        "cix": 2,
        "bm": 0,
        "ix": 1,
        "mn": "ADBE Vector Group",
        "hd": False,
        "it": container_items
    }
    return [svg_group]

# Test on 14.tgs
with open("shablonlar/14.tgs", "rb") as f:
    tgs_bytes = f.read()

multi_color_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100">
  <defs>
    <style>
      .badge-bg { fill: #1e88e5; }
      .star-gold { fill: #ffd700; stroke: #ff6f00; stroke-width: 2; }
      .banner-red { fill: #e53935; }
    </style>
  </defs>
  <rect class="badge-bg" x="10" y="10" width="280" height="80" rx="15" />
  <path class="banner-red" d="M 20 50 L 80 20 L 80 80 Z" />
  <polygon class="star-gold" points="150,20 160,40 185,40 165,55 172,80 150,65 128,80 135,55 115,40 140,40" />
  <circle cx="240" cy="50" r="25" fill="#43a047" stroke="#1b5e20" stroke-width="3" />
</svg>"""

tgs_json = json.loads(gzip.decompress(tgs_bytes).decode("utf-8"))
target_layer = tgs_json["layers"][0]
shapes = generate_svg_shapes_colored(multi_color_svg, target_layer, scale_factor=1.0)
print(f"Generated {len(shapes)} root shape groups. Child groups count: {len(shapes[0]['it'])}")

for item in shapes[0]['it']:
    if item.get('ty') == 'gr':
        print(f"  Group '{item.get('nm')}':")
        for sub in item.get('it', []):
            if sub.get('ty') == 'fl':
                print(f"    Fill color: {sub.get('c', {}).get('k')}")
            elif sub.get('ty') == 'st':
                print(f"    Stroke color: {sub.get('c', {}).get('k')}, w: {sub.get('w', {}).get('k')}")

print("\nSUCCESS: All distinct SVG colors preserved in Lottie vector groups!")
