# ==============================================================================
# COPYRIGHT NOTICE & LICENSE AGREEMENT (C) 2026 GN STUDIO
# Project: GnEmoji Studio — Animated Lottie Vector Engine
# All Rights Reserved.
# ==============================================================================

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


def cache_svg(svg_content: str, title: str = "SVG", badge_color: str = None, badge_bg_color: str = None, text_color: str = None) -> str:
    if not svg_content:
        return ""
    content_key = f"{svg_content}_{badge_color or ''}_{badge_bg_color or ''}_{text_color or ''}"
    svg_id = hashlib.md5(content_key.encode('utf-8')).hexdigest()[:12]
    SVG_CACHE[svg_id] = {
        "svg": svg_content,
        "title": title[:30] if title else "SVG",
        "badge_color": badge_color,
        "badge_bg_color": badge_bg_color,
        "text_color": text_color,
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


def generate_text_shapes(text: str, font_path: str, target_layer: dict, scale_factor: float = 1.0, text_color: str = None) -> list:
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
    if text_color:
        t_str = text_color.strip()
        if not t_str.startswith('#') and len(t_str) in (3, 6, 8):
            t_str = f"#{t_str}"
        tc = parse_svg_color(t_str)
        if tc and tc != 'none' and isinstance(tc, list):
            info["fill"] = {"a": 0, "k": [tc[0], tc[1], tc[2], 1.0]}

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

        if info.get("stroke_w") and isinstance(info["stroke_w"], dict) and info["stroke_w"].get("k", 0) > 0:
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

def parse_svg_color(val: str, default_opacity: float = 1.0, grad_map: dict = None):
    if not val:
        return None
    val = val.strip()
    val_lower = val.lower()
    if val_lower in ('none', 'transparent'):
        return 'none'
    if val_lower == 'currentcolor':
        return 'currentcolor'
    
    # Handle url(#gradId)
    if val_lower.startswith('url(') and grad_map:
        m = re.search(r'url\s*\(\s*[\'"]?#?([^\'")]+)[\'"]?\s*\)', val, re.IGNORECASE)
        if m:
            gid = m.group(1).strip()
            if gid in grad_map and grad_map[gid]:
                return parse_svg_color(grad_map[gid][0], default_opacity, None)
    
    if val_lower in CSS_NAMED_COLORS:
        val_lower = CSS_NAMED_COLORS[val_lower]
    
    if val_lower.startswith('#'):
        hex_str = val_lower[1:]
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

    m_rgb = re.match(r'rgba?\s*\(\s*([\d\.]+%?)\s*,\s*([\d\.]+%?)\s*,\s*([\d\.]+%?)(?:\s*,\s*([\d\.]+))?\s*\)', val_lower)
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
        tag = _strip_xml_ns(el.tag).lower() if isinstance(el.tag, str) else ''
        if tag == 'style' and el.text:
            matches = re.findall(r'\.([a-zA-Z0-9_\-]+)\s*\{([^}]+)\}', el.text)
            for cls_name, decls in matches:
                if cls_name not in class_map:
                    class_map[cls_name] = {}
                class_map[cls_name].update(parse_css_style_declarations(decls))
    return class_map

def extract_svg_gradients(root_element) -> dict:
    grad_map = {}
    for el in root_element.iter():
        tag = _strip_xml_ns(el.tag).lower() if isinstance(el.tag, str) else ''
        if tag in ('lineargradient', 'radialgradient'):
            grad_id = el.attrib.get('id')
            if not grad_id:
                continue
            stops = []
            for child in el.iter():
                ctag = _strip_xml_ns(child.tag).lower() if isinstance(child.tag, str) else ''
                if ctag == 'stop':
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

class ColoredSVGElement:
    def __init__(self, paths, fill, stroke, stroke_width, fill_opacity, stroke_opacity, name):
        self.paths = paths
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.fill_opacity = fill_opacity
        self.stroke_opacity = stroke_opacity
        self.name = name

def extract_svg_colored_elements(root_element, target_cx, target_cy, svg_cx, svg_cy, scale, fallback_fill):
    class_styles = extract_svg_css_classes(root_element)
    grad_map = extract_svg_gradients(root_element)
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
        local_tf = parse_svg_transform(el.attrib.get('transform', ''))
        combined_tf = current_tf.transform(local_tf)
        element_styles = get_element_styles(el, current_styles)

        tag = _strip_xml_ns(el.tag).lower() if isinstance(el.tag, str) else ''
        
        pen = LottieSVGPen(
            target_cx=target_cx,
            target_cy=target_cy,
            svg_cx=svg_cx,
            svg_cy=svg_cy,
            scale=scale
        )
        t_pen = TransformPen(pen, combined_tf) if combined_tf != Transform() else pen

        has_geometry = False
        if tag == 'path' and 'd' in el.attrib:
            parse_path(el.attrib['d'], t_pen)
            has_geometry = True
        elif tag in ('circle', 'rect', 'ellipse', 'line', 'polygon', 'polyline'):
            pb = SafePathBuilder()
            pb.add_path_from_element(el)
            for p in pb.paths:
                parse_path(p, t_pen)
            has_geometry = True

        if has_geometry:
            pen._closePath()
            if pen.paths:
                raw_fill = element_styles.get('fill')
                fill_color = parse_svg_color(raw_fill, grad_map=grad_map) if raw_fill else None
                if fill_color == 'currentcolor':
                    fill_color = fallback_fill
                
                raw_stroke = element_styles.get('stroke')
                stroke_color = parse_svg_color(raw_stroke, grad_map=grad_map) if raw_stroke else None
                if stroke_color == 'currentcolor':
                    stroke_color = fallback_fill
                
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


def generate_svg_shapes(svg_content: str, target_layer: dict, scale_factor: float = 1.0) -> list:
    """
    Parses SVG vectors with full color, transform, and opacity preservation and fits them
    into the exact position, scale, orientation, and bounds of the target template badge/layer.
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

    fallback_fill_color = info["fill"]["k"] if isinstance(info["fill"], dict) and "k" in info["fill"] else [1.0, 1.0, 1.0, 1.0]

    colored_elements = extract_svg_colored_elements(
        root_element=root,
        target_cx=info["orig_center_x"],
        target_cy=info["orig_center_y"],
        svg_cx=svg_cx,
        svg_cy=svg_cy,
        scale=scale,
        fallback_fill=fallback_fill_color
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
            stroke_c = el.stroke[:3] if isinstance(el.stroke, list) else [0.0, 0.0, 0.0]
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
                fill_c = el.fill[:3] if isinstance(el.fill, list) else [0.0, 0.0, 0.0]
                fill_op = el.fill_opacity * 100
            else:
                if not (el.stroke and el.stroke != 'none'):
                    fill_c = [0.05, 0.05, 0.05] if has_any_custom_colors else fallback_fill_color[:3]
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


def is_text_container(item):
    """
    Checks if a shape group is a text container:
    1. Has multiple child groups named after single characters ('A', 'B', 'K', 'X', etc.)
    2. Or is explicitly named 'TextGroup', 'NAME', 'Letters', 'caption', 'word'
    3. Or has child shape paths named 'Logo path' or child groups named 'Svg Group'
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
        
    # Check 3: child shape paths named 'Logo path' or child groups named 'Svg Group'
    logo_paths = [
        i for i, s in enumerate(children)
        if isinstance(s, dict) and (
            (s.get('ty') == 'sh' and 'logo path' in str(s.get('nm', '')).lower()) or
            (s.get('ty') == 'gr' and 'svg group' in str(s.get('nm', '')).lower())
        )
    ]
    if len(logo_paths) >= 1:
        return True, ('logo_paths', logo_paths)
        
    return False, []


def process_shapes_list(shapes_list, font_path=None, text=None, svg_content=None, scale: float = 1.0, text_color: str = None):
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
            new_shapes = generate_text_shapes(clean_txt, font_path, target_group, scale_factor=scale, text_color=text_color)

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
                    new_shapes = generate_text_shapes(clean_txt, font_path, target_group, scale_factor=scale, text_color=text_color)
                children = item.get('it', [])
                trs = [s for s in children if s.get('ty') == 'tr']
                item['it'] = new_shapes + trs
                modified = True
                new_list.append(item)
                continue
                
            if 'it' in item and isinstance(item['it'], list):
                new_it, changed = process_shapes_list(item['it'], font_path, text, svg_content, scale=scale, text_color=text_color)
                if changed:
                    item['it'] = new_it
                    modified = True
        new_list.append(item)
        
    return new_list, modified


def apply_badge_color_to_template(data: dict, badge_color: str = None, badge_bg_color: str = None, text_color: str = None):
    """
    Recolors logo templates:
    1. badge_color: outer badge frame/border (strokes ty=='st' or light elements cr > 0.82)
    2. badge_bg_color: inner base/background (fills ty=='fl' and dark elements cr < 0.18)
    3. text_color: text fill across text layers/groups (inside TextGroup)
    Excludes custom user SVG elements (SVG_Symbol).
    """
    c_primary = None
    if badge_color:
        b_str = badge_color.strip()
        if not b_str.startswith('#') and len(b_str) in (3, 6, 8):
            b_str = f"#{b_str}"
        c_p = parse_svg_color(b_str)
        if c_p and c_p != 'none' and isinstance(c_p, list):
            c_primary = c_p[:3]

    c_secondary = None
    if badge_bg_color:
        bg_str = badge_bg_color.strip()
        if not bg_str.startswith('#') and len(bg_str) in (3, 6, 8):
            bg_str = f"#{bg_str}"
        c_s = parse_svg_color(bg_str)
        if c_s and c_s != 'none' and isinstance(c_s, list):
            c_secondary = c_s[:3]

    c_text = None
    if text_color:
        t_str = text_color.strip()
        if not t_str.startswith('#') and len(t_str) in (3, 6, 8):
            t_str = f"#{t_str}"
        c_t = parse_svg_color(t_str)
        if c_t and c_t != 'none' and isinstance(c_t, list):
            c_text = c_t[:3]

    def walk_item(item, is_in_text=False):
        if not isinstance(item, dict):
            return
        
        nm = str(item.get("nm", ""))
        if nm in ("SVG_Symbol",) or "SVG Path" in nm or "Logo path" in nm:
            return

        is_text_node = is_in_text or nm in ("TextGroup", "EMOJI") or (nm and len(nm) == 1 and nm.isalnum() and item.get("ty") == "gr")

        ty = item.get("ty")
        if ty in ("fl", "st") and "c" in item:
            c_val = item["c"].get("k")
            if isinstance(c_val, list) and len(c_val) >= 3 and isinstance(c_val[0], (int, float)):
                cr, cg, cb = c_val[:3]
                alpha = c_val[3] if len(c_val) > 3 else 1.0

                # Tag role permanently once based on structure & initial colors
                if "_role" not in item:
                    if is_text_node:
                        item["_role"] = "text"
                    elif ty == "st" or (cr > 0.82 and cg > 0.82 and cb > 0.82):
                        item["_role"] = "outer"
                    elif ty == "fl" and cr < 0.18 and cg < 0.18 and cb < 0.18:
                        item["_role"] = "inner"
                    else:
                        item["_role"] = "none"

                if item["_role"] == "outer" and c_primary:
                    item["c"]["k"] = [c_primary[0], c_primary[1], c_primary[2], alpha]
                elif item["_role"] == "inner" and c_secondary:
                    item["c"]["k"] = [c_secondary[0], c_secondary[1], c_secondary[2], alpha]
                elif item["_role"] == "text" and c_text:
                    item["c"]["k"] = [c_text[0], c_text[1], c_text[2], alpha]

        for it in item.get("it", []):
            walk_item(it, is_text_node)
        for sh in item.get("shapes", []):
            walk_item(sh, is_text_node)

    for l in data.get("layers", []):
        walk_item(l, False)
    for a in data.get("assets", []):
        for l in a.get("layers", []):
            walk_item(l, False)


def process_tgs_template(
    template_bytes: bytes,
    text: str = None,
    font_path: str = "fonts/stapel.ttf",
    svg_content: str = None,
    scale: float = 1.0,
    text_scale: float = None,
    svg_data: str = None,
    input_type: str = None,
    badge_color: str = None,
    badge_bg_color: str = None,
    text_color: str = None
) -> bytes:
    """
    Processes a single .tgs template replacing text with either font-rendered text or SVG vector graphics,
    and applies custom badge colors (outer border, inner base, and text color).
    """
    effective_scale = text_scale if text_scale is not None else scale
    effective_svg = svg_content if svg_content is not None else svg_data
    if input_type == 'text':
        effective_svg = None

    data = json.loads(gzip.decompress(template_bytes))

    # Search in all layer collections: root layers and precomposition assets
    all_layer_lists = [data.get('layers', [])]
    for asset in data.get('assets', []):
        asset_id = str(asset.get('id', '')).lower()
        is_logo_asset = any(k in asset_id for k in ['mylogo', 'logo', 'text_logo', 'emojilogo', 'logocomp', 'logo_comp'])
        if 'layers' in asset:
            for layer in asset['layers']:
                if is_logo_asset and 'shapes' in layer and isinstance(layer['shapes'], list) and len(layer['shapes']) > 0:
                    target_group = {'shapes': layer['shapes']}
                    if effective_svg:
                        new_shapes = generate_svg_shapes(effective_svg, target_group, scale_factor=effective_scale)
                    else:
                        clean_txt = text if (text and text.strip()) else "ISMINGIZ"
                        new_shapes = generate_text_shapes(clean_txt, font_path, target_group, scale_factor=effective_scale, text_color=text_color)
                    layer['shapes'] = new_shapes
                else:
                    all_layer_lists.append([layer])

    for layers in all_layer_lists:
        for layer in layers:
            if 'shapes' in layer and isinstance(layer['shapes'], list):
                new_shapes, changed = process_shapes_list(
                    layer['shapes'],
                    font_path=font_path,
                    text=text,
                    svg_content=effective_svg,
                    scale=effective_scale,
                    text_color=text_color
                )
                if changed:
                    layer['shapes'] = new_shapes

    # Tag roles and apply custom badge/border/inner/text colors
    apply_badge_color_to_template(data, badge_color=badge_color, badge_bg_color=badge_bg_color, text_color=text_color)

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
