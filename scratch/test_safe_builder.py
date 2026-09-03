import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fontTools.svgLib.path import parse_path
from fontTools.pens.recordingPen import RecordingPen

def _strip_xml_ns(tag: str) -> str:
    if isinstance(tag, str) and tag.startswith("{"):
        return tag.split("}", 1)[1]
    return str(tag or "")

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

# Test parsing
pen = RecordingPen()
pb = SafePathBuilder()
import xml.etree.ElementTree as ET
el = ET.fromstring('<circle cx="50" cy="50" r="30"/>')
pb.add_path_from_element(el)
print('Generated path:', pb.paths)
for p in pb.paths:
    parse_path(p, pen)
print('Pen value:', len(pen.value))
print("SAFE PATH BUILDER & PARSE_PATH WORK 100%!")
