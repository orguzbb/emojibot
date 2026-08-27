from __future__ import annotations
import os
import re
import time
import hashlib
import math
import gzip
import json
import copy
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Union, Dict, List, Any, Tuple
from fontTools.ttLib import TTFont
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen

SVG_CACHE = {}


def cache_svg(svg_content: str, title: str = "SVG") -> str:
    if not svg_content:
        return ""
    svg_id = hashlib.md5(svg_content.encode('utf-8')).hexdigest()[:12]
    SVG_CACHE[svg_id] = {
        "svg": svg_content,
        "title": title[:30] if title else "SVG",
        "time": time.time()
    }
    if len(SVG_CACHE) > 500:
        oldest_keys = sorted(SVG_CACHE.keys(), key=lambda k: SVG_CACHE[k]["time"])[:100]
        for k in oldest_keys:
            SVG_CACHE.pop(k, None)
    return svg_id


def get_cached_svg(svg_id: str) -> Optional[dict]:
    return SVG_CACHE.get(svg_id)


def to_svg_slug(title: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9]', '', title or "svg").lower()
    if not slug or not slug[0].isalpha():
        slug = f"svg{slug}"
    return slug[:14]


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


class LottieSVGPen(BasePen):
    def __init__(self, target_cx=0.0, target_cy=0.0, svg_cx=0.0, svg_cy=0.0, scale=1.0):
        super().__init__(None)
        self.target_cx = target_cx
        self.target_cy = target_cy
        self.svg_cx = svg_cx
        self.svg_cy = svg_cy
        self.scale = scale
        self.paths = []
        self.current_v = []
        self.current_i = []
        self.current_o = []
        self.current_pt = [0.0, 0.0]

    def _transform(self, pt):
        return [
            round(self.target_cx + (pt[0] - self.svg_cx) * self.scale, 3),
            round(self.target_cy + (pt[1] - self.svg_cy) * self.scale, 3)
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
        if not self.current_v:
            return
        is_closed = False
        if len(self.current_v) > 2:
            if abs(self.current_v[0][0] - self.current_v[-1][0]) < 1e-2 and \
               abs(self.current_v[0][1] - self.current_v[-1][1]) < 1e-2:
                is_closed = True
                self.current_i[0] = self.current_i[-1]
                self.current_v.pop()
                self.current_i.pop()
                self.current_o.pop()
        
        self.paths.append({
            "c": is_closed,
            "v": self.current_v,
            "i": self.current_i,
            "o": self.current_o
        })
        self.current_v = []
        self.current_i = []
        self.current_o = []


def parse_svg_transform(tf_str: str) -> Transform:
    """
    Parses full SVG transform attribute strings including:
    - translate(x, y) / translate(x)
    - scale(sx, sy) / scale(sx) [including negative scales]
    - rotate(deg) / rotate(deg, cx, cy)
    - matrix(a, b, c, d, e, f)
    - skewX(deg), skewY(deg)
    """
    if not tf_str:
        return Transform()
    
    t = Transform()
    pattern = re.compile(r'([a-zA-Z]+)\s*\(([^)]*)\)')
    for match in pattern.finditer(tf_str):
        op = match.group(1).lower().strip()
        args_str = match.group(2).strip()
        parts = [float(p) for p in re.split(r'[\s,]+', args_str) if p]
        
        if op == 'translate':
            tx = parts[0] if len(parts) > 0 else 0.0
            ty = parts[1] if len(parts) > 1 else 0.0
            t = t.translate(tx, ty)
        elif op == 'scale':
            sx = parts[0] if len(parts) > 0 else 1.0
            sy = parts[1] if len(parts) > 1 else sx
            t = t.scale(sx, sy)
        elif op == 'rotate':
            angle_deg = parts[0] if len(parts) > 0 else 0.0
            angle_rad = math.radians(angle_deg)
            if len(parts) == 3:
                cx, cy = parts[1], parts[2]
                t = t.translate(cx, cy).rotate(angle_rad).translate(-cx, -cy)
            else:
                t = t.rotate(angle_rad)
        elif op == 'matrix':
            if len(parts) == 6:
                t = t.transform(Transform(*parts))
        elif op == 'skewx':
            if len(parts) >= 1:
                t = t.skew(math.radians(parts[0]), 0)
        elif op == 'skewy':
            if len(parts) >= 1:
                t = t.skew(0, math.radians(parts[0]))
    return t


def _strip_xml_ns(tag: str) -> str:
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return str(tag or "")


try:
    from fontTools.svgLib.path import parse_path as ft_parse_path
except Exception:
    ft_parse_path = None


class SafePathBuilder:
    def __init__(self):
        self.paths = []

    def add_path_from_element(self, el):
        tag = _strip_xml_ns(el.tag).lower()
        attrib = el.attrib
        if tag == 'rect':
            x = float(attrib.get('x', 0))
            y = float(attrib.get('y', 0))
            w = float(attrib.get('width', 0))
            h = float(attrib.get('height', 0))
            rx = float(attrib.get('rx', 0))
            ry = float(attrib.get('ry', rx))
            if rx == 0 and ry == 0:
                self.paths.append(f"M {x} {y} h {w} v {h} h {-w} Z")
            else:
                self.paths.append(
                    f"M {x+rx} {y} h {w-2*rx} a {rx} {ry} 0 0 1 {rx} {ry} v {h-2*ry} a {rx} {ry} 0 0 1 {-rx} {ry} h {-w+2*rx} a {rx} {ry} 0 0 1 {-rx} {-ry} v {-h+2*ry} a {rx} {ry} 0 0 1 {rx} {-ry} Z"
                )
        elif tag == 'circle':
            cx = float(attrib.get('cx', 0))
            cy = float(attrib.get('cy', 0))
            r = float(attrib.get('r', 0))
            self.paths.append(f"M {cx-r} {cy} a {r} {r} 0 1 0 {2*r} 0 a {r} {r} 0 1 0 {-2*r} 0 Z")
        elif tag == 'ellipse':
            cx = float(attrib.get('cx', 0))
            cy = float(attrib.get('cy', 0))
            rx = float(attrib.get('rx', 0))
            ry = float(attrib.get('ry', 0))
            self.paths.append(f"M {cx-rx} {cy} a {rx} {ry} 0 1 0 {2*rx} 0 a {rx} {ry} 0 1 0 {-2*rx} 0 Z")
        elif tag == 'line':
            x1 = float(attrib.get('x1', 0))
            y1 = float(attrib.get('y1', 0))
            x2 = float(attrib.get('x2', 0))
            y2 = float(attrib.get('y2', 0))
            self.paths.append(f"M {x1} {y1} L {x2} {y2}")
        elif tag == 'polygon':
            pts = attrib.get('points', '').strip()
            if pts:
                self.paths.append(f"M {pts} Z")
        elif tag == 'polyline':
            pts = attrib.get('points', '').strip()
            if pts:
                self.paths.append(f"M {pts}")


_COMMAND_RE = re.compile(r'([MmLlHhVvCcSsQqTtAaZz])|([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)')

def _parse_svg_path_pure(d: str, pen):
    tokens = []
    for m in _COMMAND_RE.finditer(d):
        cmd, num = m.groups()
        if cmd:
            tokens.append(cmd)
        elif num:
            tokens.append(float(num))

    i = 0
    curr_x, curr_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    last_cmd = None

    while i < len(tokens):
        token = tokens[i]
        if isinstance(token, str):
            cmd = token
            i += 1
        else:
            cmd = last_cmd

        if not cmd:
            break

        if cmd == 'M':
            curr_x, curr_y = tokens[i], tokens[i+1]
            start_x, start_y = curr_x, curr_y
            pen.moveTo((curr_x, curr_y))
            i += 2
            last_cmd = 'L'
        elif cmd == 'm':
            curr_x += tokens[i]
            curr_y += tokens[i+1]
            start_x, start_y = curr_x, curr_y
            pen.moveTo((curr_x, curr_y))
            i += 2
            last_cmd = 'l'
        elif cmd == 'L':
            curr_x, curr_y = tokens[i], tokens[i+1]
            pen.lineTo((curr_x, curr_y))
            i += 2
            last_cmd = 'L'
        elif cmd == 'l':
            curr_x += tokens[i]
            curr_y += tokens[i+1]
            pen.lineTo((curr_x, curr_y))
            i += 2
            last_cmd = 'l'
        elif cmd == 'H':
            curr_x = tokens[i]
            pen.lineTo((curr_x, curr_y))
            i += 1
            last_cmd = 'H'
        elif cmd == 'h':
            curr_x += tokens[i]
            pen.lineTo((curr_x, curr_y))
            i += 1
            last_cmd = 'h'
        elif cmd == 'V':
            curr_y = tokens[i]
            pen.lineTo((curr_x, curr_y))
            i += 1
            last_cmd = 'V'
        elif cmd == 'v':
            curr_y += tokens[i]
            pen.lineTo((curr_x, curr_y))
            i += 1
            last_cmd = 'v'
        elif cmd == 'C':
            x1, y1 = tokens[i], tokens[i+1]
            x2, y2 = tokens[i+2], tokens[i+3]
            curr_x, curr_y = tokens[i+4], tokens[i+5]
            pen.curveToOne((x1, y1), (x2, y2), (curr_x, curr_y))
            i += 6
            last_cmd = 'C'
        elif cmd == 'c':
            x1, y1 = curr_x + tokens[i], curr_y + tokens[i+1]
            x2, y2 = curr_x + tokens[i+2], curr_y + tokens[i+3]
            curr_x += tokens[i+4]
            curr_y += tokens[i+5]
            pen.curveToOne((x1, y1), (x2, y2), (curr_x, curr_y))
            i += 6
            last_cmd = 'c'
        elif cmd in ('Z', 'z'):
            pen.closePath()
            curr_x, curr_y = start_x, start_y
            last_cmd = None
        else:
            i += 1


def parse_path(d_str: str, pen):
    if ft_parse_path is not None:
        try:
            ft_parse_path(d_str, pen)
            return
        except Exception:
            pass
    _parse_svg_path_pure(d_str, pen)


def draw_svg_to_pen(root_element, pen):
    """
    Recursively traverses an SVG XML element tree, propagating and multiplying
    all transformation matrices (including on <g>, <svg>, <path>, <rect>, etc.),
    and draws all vector shapes onto the given pen.
    """
    def walk(el, current_tf):
        local_tf = parse_svg_transform(el.attrib.get('transform', ''))
        combined_tf = current_tf.transform(local_tf)

        tag = _strip_xml_ns(el.tag).lower() if isinstance(el.tag, str) else ''
        
        if tag == 'path' and 'd' in el.attrib:
            t_pen = TransformPen(pen, combined_tf) if combined_tf != Transform() else pen
            parse_path(el.attrib['d'], t_pen)
        elif tag in ('circle', 'rect', 'ellipse', 'line', 'polygon', 'polyline'):
            pb = SafePathBuilder()
            pb.add_path_from_element(el)
            t_pen = TransformPen(pen, combined_tf) if combined_tf != Transform() else pen
            for p in pb.paths:
                parse_path(p, t_pen)

        for child in el:
            walk(child, combined_tf)

    walk(root_element, Transform())


def validate_and_clean_svg(raw_svg: Union[str, bytes]) -> str:
    """
    Validates and cleans SVG content:
    - Removes XML headers and comments
    - Ensures valid XML structure
    - Ensures SVG contains drawable vector paths
    """
    if isinstance(raw_svg, bytes):
        try:
            raw_svg = raw_svg.decode('utf-8')
        except UnicodeDecodeError:
            raw_svg = raw_svg.decode('latin-1')

    raw_svg = raw_svg.strip()
    
    # Strip XML declaration, doctype, and comments
    raw_svg = re.sub(r'<\?xml[^>]*\?>', '', raw_svg, flags=re.IGNORECASE)
    raw_svg = re.sub(r'<!DOCTYPE[^>]*>', '', raw_svg, flags=re.IGNORECASE)
    raw_svg = re.sub(r'<!--.*?-->', '', raw_svg, flags=re.DOTALL)
    raw_svg = raw_svg.strip()

    # Extract <svg>...</svg>
    svg_match = re.search(r'<svg[\s\S]*?</svg>', raw_svg, re.IGNORECASE)
    if svg_match:
        raw_svg = svg_match.group(0)
    else:
        raise ValueError("Yaroqli <svg>...</svg> tegi topilmadi.")

    # Validate XML parsing
    try:
        root = ET.fromstring(raw_svg)
    except Exception as e:
        raise ValueError(f"SVG XML formati noto'g'ri: {e}")

    # Validate that SVG can be drawn and contains vector paths
    try:
        bounds_pen = BoundsPen(None)
        draw_svg_to_pen(root, bounds_pen)
    except Exception as e:
        raise ValueError(f"SVG vektor shakllarini o'qib bo'lmadi: {e}")

    return raw_svg


def extract_layer_template_info(target_layer: dict):
    all_xs = []
    all_ys = []
    sample_fill = {"a": 0, "k": [0.8902, 0.1216, 0.1216, 1]}
    sample_stroke = {"a": 0, "k": [0, 0, 0, 0]}
    sample_stroke_w = {"a": 0, "k": 0}

    def collect_info(item):
        nonlocal sample_fill, sample_stroke, sample_stroke_w
        if not isinstance(item, dict):
            return
        
        ty = item.get('ty')
        if ty == 'sh':
            ks = item.get('ks', {}).get('k', {})
            if isinstance(ks, dict):
                for pt in ks.get('v', []):
                    all_xs.append(pt[0])
                    all_ys.append(pt[1])
            elif isinstance(ks, list):
                for kf in ks:
                    if isinstance(kf, dict):
                        s_val = kf.get('s', [{}])
                        if isinstance(s_val, list) and s_val and isinstance(s_val[0], dict):
                            for pt in s_val[0].get('v', []):
                                all_xs.append(pt[0])
                                all_ys.append(pt[1])
        elif ty == 'fl' and 'c' in item:
            sample_fill = copy.deepcopy(item.get('c'))
        elif ty == 'st' and 'c' in item:
            sample_stroke = copy.deepcopy(item.get('c'))
            if 'w' in item:
                sample_stroke_w = copy.deepcopy(item.get('w'))
        
        for sub in item.get('shapes', []):
            collect_info(sub)
        for sub in item.get('it', []):
            collect_info(sub)

    collect_info(target_layer)

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


def generate_text_shapes(text: str, font_path: str, target_layer: dict, scale_factor: float = 1.0) -> list:
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
        # Inter / Grobold naturally maintains 0.88-0.90 aspect ratio
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

    effective_scale_factor = scale_factor if (scale_factor and scale_factor > 0) else 1.0
    scale_x *= effective_scale_factor
    scale_y *= effective_scale_factor

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


def generate_svg_shapes(svg_content: str, target_layer: dict, scale_factor: float = 1.0) -> list:
    """
    Parses SVG vectors with full hierarchical transform propagation and fits them
    into the exact position, scale, orientation, and 3D styling of the target template badge/layer.
    """
    cleaned_svg = validate_and_clean_svg(svg_content)
    root = ET.fromstring(cleaned_svg)

    bounds_pen = BoundsPen(None)
    draw_svg_to_pen(root, bounds_pen)
    bounds = bounds_pen.bounds
    if not bounds:
        bounds = (0.0, 0.0, 100.0, 100.0)

    svg_w = max(bounds[2] - bounds[0], 1.0)
    svg_h = max(bounds[3] - bounds[1], 1.0)
    svg_cx = (bounds[0] + bounds[2]) / 2.0
    svg_cy = (bounds[1] + bounds[3]) / 2.0

    info = extract_layer_template_info(target_layer)

    effective_scale_factor = scale_factor if (scale_factor and scale_factor > 0) else 1.0
    scale_x = (info["orig_width"] * 0.92 * effective_scale_factor) / svg_w
    scale_y = (info["orig_height"] * 0.95 * effective_scale_factor) / svg_h
    scale = min(scale_x, scale_y)

    pen = LottieSVGPen(
        target_cx=info["orig_center_x"],
        target_cy=info["orig_center_y"],
        svg_cx=svg_cx,
        svg_cy=svg_cy,
        scale=scale
    )
    draw_svg_to_pen(root, pen)
    pen._closePath()

    if not pen.paths:
        return []

    items = []
    for p_idx, path in enumerate(pen.paths):
        items.append({
            "ty": "sh",
            "nm": f"SVG Path {p_idx + 1}",
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

    svg_group = {
        "ty": "gr",
        "nm": "SVG_Symbol",
        "np": len(items),
        "cix": 2,
        "bm": 0,
        "ix": 1,
        "mn": "ADBE Vector Group",
        "hd": False,
        "it": items
    }
    return [svg_group]


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


def process_shapes_list(shapes_list, font_path=None, text=None, svg_content=None, scale: float = 1.0):
    """
    Recursively finds text shape groups and replaces them with newly rendered font glyphs or SVG shapes.
    """
    is_svg = bool(svg_content)

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
                
        if is_svg:
            new_shapes = generate_svg_shapes(svg_content, target_group, scale_factor=scale)
        else:
            clean_txt = text if (text and text.strip()) else "ISMINGIZ"
            new_shapes = generate_text_shapes(clean_txt, font_path, target_group, scale_factor=scale)

        non_letters = [s for i, s in enumerate(shapes_list) if i not in letter_indices]
        trs = [s for s in non_letters if s.get('ty') == 'tr']
        others = [s for s in non_letters if s.get('ty') != 'tr']
        return new_shapes + others + trs, True

    modified = False
    new_list = []
    for item in shapes_list:
        if isinstance(item, dict):
            is_text, text_type = is_text_container(item)
            if is_text and text_type[0] in ('text_group', 'logo_paths'):
                target_group = {'shapes': [item]}
                if is_svg:
                    new_shapes = generate_svg_shapes(svg_content, target_group, scale_factor=scale)
                else:
                    clean_txt = text if (text and text.strip()) else "ISMINGIZ"
                    new_shapes = generate_text_shapes(clean_txt, font_path, target_group, scale_factor=scale)
                children = item.get('it', [])
                trs = [s for s in children if s.get('ty') == 'tr']
                item['it'] = new_shapes + trs
                modified = True
                new_list.append(item)
                continue
                
            if 'it' in item and isinstance(item['it'], list):
                new_it, changed = process_shapes_list(item['it'], font_path, text, svg_content, scale=scale)
                if changed:
                    item['it'] = new_it
                    modified = True
        new_list.append(item)
        
    return new_list, modified


def process_tgs_template(
    template_bytes: bytes,
    text: str = None,
    font_path: str = "fonts/stapel.ttf",
    svg_content: str = None,
    scale: float = 1.0,
    text_scale: float = None,
    svg_data: str = None,
    input_type: str = None
) -> bytes:
    """
    Processes a single .tgs template replacing text with either font-rendered text or SVG vector graphics.
    """
    effective_scale = text_scale if text_scale is not None else scale
    effective_svg = svg_content if svg_content is not None else svg_data
    if input_type == 'text':
        effective_svg = None

    data = json.loads(gzip.decompress(template_bytes))

    # Search in all layer collections: root layers and precomposition assets
    all_layer_lists = [data.get('layers', [])]
    for asset in data.get('assets', []):
        if 'layers' in asset:
            all_layer_lists.append(asset['layers'])

    for layers in all_layer_lists:
        for layer in layers:
            if 'shapes' in layer and isinstance(layer['shapes'], list):
                new_shapes, changed = process_shapes_list(
                    layer['shapes'],
                    font_path=font_path,
                    text=text,
                    svg_content=effective_svg,
                    scale=effective_scale
                )
                if changed:
                    layer['shapes'] = new_shapes

    return gzip.compress(json.dumps(data, separators=(',', ':')).encode('utf-8'))


def process_tgs_template_svg(template_bytes: bytes, svg_content: str, scale: float = 1.0) -> bytes:
    """
    Convenience function to process a .tgs template with SVG.
    """
    return process_tgs_template(template_bytes=template_bytes, svg_content=svg_content, scale=scale)


def process_all_templates(templates_dir: str, text: str, font_path: str = "fonts/stapel.ttf", scale: float = 1.0) -> list:
    p = Path(templates_dir)
    results = []
    tgs_files = sorted(p.glob("*.tgs"), key=lambda f: (len(f.name), f.name))
    for tgs_file in tgs_files:
        with open(tgs_file, "rb") as f:
            template_bytes = f.read()
        processed_bytes = process_tgs_template(template_bytes=template_bytes, text=text, font_path=font_path, scale=scale)
        results.append((tgs_file.name, processed_bytes))
    return results


def process_all_templates_svg(templates_dir: str, svg_content: str, scale: float = 1.0) -> list:
    p = Path(templates_dir)
    results = []
    tgs_files = sorted(p.glob("*.tgs"), key=lambda f: (len(f.name), f.name))
    for tgs_file in tgs_files:
        with open(tgs_file, "rb") as f:
            template_bytes = f.read()
        processed_bytes = process_tgs_template_svg(template_bytes=template_bytes, svg_content=svg_content, scale=scale)
        results.append((tgs_file.name, processed_bytes))
    return results
