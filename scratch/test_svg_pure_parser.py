import re, math

COMMAND_RE = re.compile(r'([MmLlHhVvCcSsQqTtAaZz])|([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)')

def parse_svg_path_pure(d: str, pen):
    tokens = []
    for m in COMMAND_RE.finditer(d):
        cmd, num = m.groups()
        if cmd:
            tokens.append(cmd)
        elif num:
            tokens.append(float(num))

    i = 0
    curr_x, curr_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    last_cmd = None
    last_cp = None

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
            last_cp = None
        elif cmd == 'm':
            curr_x += tokens[i]
            curr_y += tokens[i+1]
            start_x, start_y = curr_x, curr_y
            pen.moveTo((curr_x, curr_y))
            i += 2
            last_cmd = 'l'
            last_cp = None
        elif cmd == 'L':
            curr_x, curr_y = tokens[i], tokens[i+1]
            pen.lineTo((curr_x, curr_y))
            i += 2
            last_cmd = 'L'
            last_cp = None
        elif cmd == 'l':
            curr_x += tokens[i]
            curr_y += tokens[i+1]
            pen.lineTo((curr_x, curr_y))
            i += 2
            last_cmd = 'l'
            last_cp = None
        elif cmd == 'H':
            curr_x = tokens[i]
            pen.lineTo((curr_x, curr_y))
            i += 1
            last_cmd = 'H'
            last_cp = None
        elif cmd == 'h':
            curr_x += tokens[i]
            pen.lineTo((curr_x, curr_y))
            i += 1
            last_cmd = 'h'
            last_cp = None
        elif cmd == 'V':
            curr_y = tokens[i]
            pen.lineTo((curr_x, curr_y))
            i += 1
            last_cmd = 'V'
            last_cp = None
        elif cmd == 'v':
            curr_y += tokens[i]
            pen.lineTo((curr_x, curr_y))
            i += 1
            last_cmd = 'v'
            last_cp = None
        elif cmd == 'C':
            x1, y1 = tokens[i], tokens[i+1]
            x2, y2 = tokens[i+2], tokens[i+3]
            curr_x, curr_y = tokens[i+4], tokens[i+5]
            pen.curveToOne((x1, y1), (x2, y2), (curr_x, curr_y))
            last_cp = (x2, y2)
            i += 6
            last_cmd = 'C'
        elif cmd == 'c':
            x1, y1 = curr_x + tokens[i], curr_y + tokens[i+1]
            x2, y2 = curr_x + tokens[i+2], curr_y + tokens[i+3]
            curr_x += tokens[i+4]
            curr_y += tokens[i+5]
            pen.curveToOne((x1, y1), (x2, y2), (curr_x, curr_y))
            last_cp = (x2, y2)
            i += 6
            last_cmd = 'c'
        elif cmd in ('Z', 'z'):
            pen.closePath()
            curr_x, curr_y = start_x, start_y
            last_cmd = None
            last_cp = None
        else:
            i += 1

print("Pure SVG path parser defined successfully!")
