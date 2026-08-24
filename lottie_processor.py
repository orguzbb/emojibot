import os
import gzip
import json
import copy
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen


class LottieGlyphPen(BasePen):
    def __init__(self, glyphSet=None, scale_x=1.0, scale_y=1.0, offset_x=0.0, offset_y=0.0):
        super().__init__(glyphSet)
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.paths = []
        self.current_v = []
        self.current_i = []
        self.current_o = []
        self.current_pt = [0.0, 0.0]

    def _transform(self, pt):
        return [
            round(self.offset_x + pt[0] * self.scale_x, 3),
            round(self.offset_y - pt[1] * self.scale_y, 3)
        ]

    def _moveTo(self, pt):
        if self.current_v:
            self._closePath()
        t_pt = self._transform(pt)
        self.current_pt = t_pt
        self.current_v = [t_pt]
        self.current_i = [[0.0, 0.0]]
        self.current_o = [[0.0, 0.0]]

    def _lineTo(self, pt):
        t_pt = self._transform(pt)
        self.current_v.append(t_pt)
        self.current_i.append([0.0, 0.0])
        self.current_o.append([0.0, 0.0])
        self.current_pt = t_pt

    def _curveToOne(self, pt1, pt2, pt3):
        t_p1 = self._transform(pt1)
        t_p2 = self._transform(pt2)
        t_p3 = self._transform(pt3)

        self.current_o[-1] = [
            round(t_p1[0] - self.current_pt[0], 3),
            round(t_p1[1] - self.current_pt[1], 3)
        ]
        self.current_v.append(t_p3)
        self.current_i.append([
            round(t_p2[0] - t_p3[0], 3),
            round(t_p2[1] - t_p3[1], 3)
        ])
        self.current_o.append([0.0, 0.0])
        self.current_pt = t_p3

    def _closePath(self):
        if not self.current_v:
            return
        if len(self.current_v) > 1:
            if abs(self.current_v[0][0] - self.current_v[-1][0]) < 1e-3 and \
               abs(self.current_v[0][1] - self.current_v[-1][1]) < 1e-3:
                self.current_i[0] = self.current_i[-1]
                self.current_v.pop()
                self.current_i.pop()
                self.current_o.pop()

        self.paths.append({
            "c": True,
            "v": self.current_v,
            "i": self.current_i,
            "o": self.current_o
        })
        self.current_v = []
        self.current_i = []
        self.current_o = []

    def _endPath(self):
        self._closePath()


def extract_layer_template_info(target_layer: dict):
    all_xs = []
    all_ys = []
    sample_fill = {"a": 0, "k": [0.8902, 0.1216, 0.1216, 1]}
    sample_stroke = {"a": 0, "k": [0, 0, 0, 0]}
    sample_stroke_w = {"a": 0, "k": 0}

    for s in target_layer.get('shapes', []):
        for it in s.get('it', []):
            if it.get('ty') == 'sh':
                ks = it.get('ks', {}).get('k', {})
                v = ks.get('v', [])
                for pt in v:
                    all_xs.append(pt[0])
                    all_ys.append(pt[1])
            elif it.get('ty') == 'fl' and 'c' in it:
                sample_fill = copy.deepcopy(it.get('c'))
            elif it.get('ty') == 'st' and 'c' in it:
                sample_stroke = copy.deepcopy(it.get('c'))
                if 'w' in it:
                    sample_stroke_w = copy.deepcopy(it.get('w'))

    if all_xs and all_ys:
        min_x, max_x = min(all_xs), max(all_xs)
        min_y, max_y = min(all_ys), max(all_ys)
    else:
        min_x, max_x = -150.0, 150.0
        min_y, max_y = -82.8, -16.4

    orig_width = max_x - min_x
    orig_height = max_y - min_y
    orig_center_x = (min_x + max_x) / 2.0
    orig_center_y = (min_y + max_y) / 2.0

    return {
        "orig_width": orig_width,
        "orig_height": orig_height,
        "orig_center_x": orig_center_x,
        "orig_center_y": orig_center_y,
        "orig_min_x": min_x,
        "orig_max_x": max_x,
        "orig_min_y": min_y,
        "orig_max_y": max_y,
        "fill": sample_fill,
        "stroke": sample_stroke,
        "stroke_w": sample_stroke_w
    }


def generate_text_shapes(text: str, font_path: str, target_layer: dict, text_scale: float = 1.0) -> list:
    font = TTFont(str(font_path))
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font['hmtx']
    os2 = font.get('OS/2')
    if os2 and getattr(os2, 'sCapHeight', 0) > 0:
        cap_height = float(os2.sCapHeight)
    else:
        cap_height = float(font['head'].unitsPerEm) * 0.70

    info = extract_layer_template_info(target_layer)

    chars = list(text.strip().upper())
    glyph_names = []
    advances = []

    for char in chars:
        gname = cmap.get(ord(char), '.notdef')
        glyph_names.append(gname)
        adv, lsb = hmtx.metrics.get(gname, (int(cap_height * 0.8), 0))
        advances.append(adv)

    raw_font_width = sum(advances) if advances else 1

    # Pure, undistorted natural font typography
    is_stapel = "stapel" in str(font_path).lower()
    if is_stapel:
        base_scale_y = info["orig_height"] / cap_height
        native_aspect_ratio = 0.7635  # Native Stapel tracking for the templates
        max_allowed_width = info["orig_width"] * 0.95
    else:
        # Inter naturally maintains 0.88-0.90 aspect ratio
        base_scale_y = (info["orig_height"] * 1.06) / cap_height
        native_aspect_ratio = 0.88
        max_allowed_width = info["orig_width"] * 0.95

    base_scale_x = base_scale_y * native_aspect_ratio
    unscaled_width = raw_font_width * base_scale_x

    # Strict uniform scaling: Never squish or stretch the font glyphs!
    if unscaled_width > max_allowed_width:
        reduction_factor = max_allowed_width / unscaled_width
        scale_x = base_scale_x * reduction_factor
        scale_y = base_scale_y * reduction_factor
    else:
        scale_x = base_scale_x
        scale_y = base_scale_y

    # Apply user custom text_scale factor
    if text_scale != 1.0:
        scale_x *= max(0.4, min(2.0, text_scale))
        scale_y *= max(0.4, min(2.0, text_scale))

    total_rendered_width = raw_font_width * scale_x
    total_rendered_height = cap_height * scale_y

    # Precise horizontal and vertical centering inside the badge
    start_x = info["orig_center_x"] - (total_rendered_width / 2.0)
    baseline_y = info["orig_center_y"] + (total_rendered_height / 2.0)

    new_shapes = []
    curr_x = start_x

    for idx, (char, gname, adv) in enumerate(zip(chars, glyph_names, advances)):
        pen = LottieGlyphPen(glyph_set, scale_x=scale_x, scale_y=scale_y, offset_x=curr_x, offset_y=baseline_y)
        glyph = glyph_set[gname]
        glyph.draw(pen)
        pen._closePath()

        items = []
        for p_idx, path in enumerate(pen.paths):
            items.append({
                "ty": "sh",
                "nm": char,
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

        if len(pen.paths) > 1:
            items.append({
                "ty": "mm",
                "nm": "Merge Paths",
                "mm": 1,
                "hd": False
            })

        items.append({
            "ty": "st",
            "nm": "Stroke",
            "c": info["stroke"],
            "w": info["stroke_w"],
            "o": {"a": 0, "k": 100}
        })

        items.append({
            "ty": "fl",
            "nm": "Fill",
            "c": info["fill"],
            "o": {"a": 0, "k": 100},
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

        letter_group = {
            "ty": "gr",
            "nm": char,
            "np": len(items),
            "cix": 2,
            "bm": 0,
            "ix": idx + 1,
            "mn": "ADBE Vector Group",
            "hd": False,
            "it": items
        }
        new_shapes.append(letter_group)
        curr_x += adv * scale_x

    return new_shapes


def is_text_container(item):
    """
    Checks if a shape group is a text container:
    1. Has multiple child groups named after single characters ('A', 'B', 'K', 'X', etc.)
    2. Or is explicitly named 'TextGroup', 'Text', 'NAME', 'Letters', etc.
    3. Or has child shape paths named 'Logo path' / 'Char' / 'Glyph'
    """
    if not isinstance(item, dict):
        return False, []
    
    children = item.get('it', []) or item.get('shapes', [])
    if not isinstance(children, list) or not children:
        return False, []
    
    # Check 1: single character letter groups (at least 2 letters)
    letter_indices = [
        i for i, s in enumerate(children)
        if isinstance(s, dict) and bool(s.get('nm')) and len(s.get('nm')) == 1 and s.get('nm').isalnum()
    ]
    if len(letter_indices) >= 2:
        return True, ('letters', letter_indices)
    
    # Check 2: group named TextGroup, NAME, Letters, etc.
    nm = str(item.get('nm', '')).lower()
    if any(k in nm for k in ['textgroup', 'name', 'letters', 'caption', 'word']):
        return True, ('text_group', list(range(len(children))))
        
    # Check 3: child shape paths named 'Logo path'
    logo_paths = [
        i for i, s in enumerate(children)
        if isinstance(s, dict) and s.get('ty') == 'sh' and 'logo path' in str(s.get('nm', '')).lower()
    ]
    if len(logo_paths) >= 2:
        return True, ('logo_paths', logo_paths)
        
    return False, []


def process_shapes_list(shapes_list, font_path, text, text_scale: float = 1.0):
    """
    Recursively finds text shape groups and replaces them with newly rendered font glyphs.
    """
    letter_indices = [
        i for i, s in enumerate(shapes_list)
        if isinstance(s, dict) and bool(s.get('nm')) and len(s.get('nm')) == 1 and s.get('nm').isalnum()
    ]
    if len(letter_indices) >= 2:
        target_group = {
            'shapes': [shapes_list[i] for i in letter_indices]
        }
        for s in shapes_list:
            if isinstance(s, dict) and s.get('ty') in ('fl', 'st'):
                target_group['shapes'].append(s)
                
        new_letter_shapes = generate_text_shapes(text, font_path, target_group, text_scale=text_scale)
        non_letters = [s for i, s in enumerate(shapes_list) if i not in letter_indices]
        trs = [s for s in non_letters if s.get('ty') == 'tr']
        others = [s for s in non_letters if s.get('ty') != 'tr']
        return new_letter_shapes + others + trs, True

    modified = False
    new_list = []
    for item in shapes_list:
        if isinstance(item, dict):
            is_text, text_type = is_text_container(item)
            if is_text and text_type[0] in ('text_group', 'logo_paths'):
                target_group = {'shapes': [item]}
                new_letter_shapes = generate_text_shapes(text, font_path, target_group, text_scale=text_scale)
                children = item.get('it', [])
                trs = [s for s in children if s.get('ty') == 'tr']
                item['it'] = new_letter_shapes + trs
                modified = True
                new_list.append(item)
                continue
                
            if 'it' in item and isinstance(item['it'], list):
                new_it, changed = process_shapes_list(item['it'], font_path, text, text_scale=text_scale)
                if changed:
                    item['it'] = new_it
                    modified = True
        new_list.append(item)
        
    return new_list, modified


def process_tgs_template(template_bytes: bytes, text: str, font_path: str = "fonts/stapel.ttf", text_scale: float = 1.0) -> bytes:
    data = json.loads(gzip.decompress(template_bytes))

    # Search in all layer collections: root layers and precomposition assets
    all_layer_lists = [data.get('layers', [])]
    for asset in data.get('assets', []):
        if 'layers' in asset:
            all_layer_lists.append(asset['layers'])

    for layers in all_layer_lists:
        for layer in layers:
            if 'shapes' in layer and isinstance(layer['shapes'], list):
                new_shapes, changed = process_shapes_list(layer['shapes'], font_path, text, text_scale=text_scale)
                if changed:
                    layer['shapes'] = new_shapes

    return gzip.compress(json.dumps(data, separators=(',', ':')).encode('utf-8'))


def process_all_templates(templates_dir: str, text: str, font_path: str = "fonts/stapel.ttf", text_scale: float = 1.0) -> list:
    p = Path(templates_dir)
    results = []
    tgs_files = sorted(p.glob("*.tgs"), key=lambda f: (len(f.name), f.name))
    for tgs_file in tgs_files:
        with open(tgs_file, "rb") as f:
            template_bytes = f.read()
        proc_bytes = process_tgs_template(template_bytes, text, font_path, text_scale=text_scale)
        results.append((tgs_file.name, proc_bytes))
    return results

