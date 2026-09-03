import json, gzip

def replace_template_colors(data, primary_hex=None, secondary_hex=None):
    # Convert hex to [r, g, b, 1]
    def hex_to_rgb(h):
        if not h: return None
        h = h.lstrip('#')
        if len(h) == 3:
            h = ''.join([c*2 for c in h])
        if len(h) == 6:
            return [int(h[0:2], 16)/255.0, int(h[2:4], 16)/255.0, int(h[4:6], 16)/255.0, 1.0]
        return None

    c_primary = hex_to_rgb(primary_hex) # e.g. replaces white or accent
    c_secondary = hex_to_rgb(secondary_hex) # e.g. replaces black/dark

    def walk_and_replace(item):
        if not isinstance(item, dict):
            return
        ty = item.get('ty')
        # Skip the replaced text/SVG symbol group itself!
        if item.get('nm') in ('SVG_Symbol', 'TextGroup'):
            return
        
        if ty in ('fl', 'st') and 'c' in item:
            c_val = item['c'].get('k')
            if isinstance(c_val, list) and len(c_val) >= 3 and isinstance(c_val[0], (int, float)):
                r, g, b = c_val[:3]
                # Is it close to white / light? (r > 0.8 and g > 0.8 and b > 0.8)
                if c_primary and r > 0.85 and g > 0.85 and b > 0.85:
                    item['c']['k'] = [c_primary[0], c_primary[1], c_primary[2], c_val[3] if len(c_val)>3 else 1.0]
                # Is it close to black / dark? (r < 0.15 and g < 0.15 and b < 0.15)
                elif c_secondary and r < 0.15 and g < 0.15 and b < 0.15:
                    item['c']['k'] = [c_secondary[0], c_secondary[1], c_secondary[2], c_val[3] if len(c_val)>3 else 1.0]

        for it in item.get('it', []):
            walk_and_replace(it)
        for sh in item.get('shapes', []):
            walk_and_replace(sh)

    # Walk layers
    for l in data.get('layers', []):
        walk_and_replace(l)
    # Walk assets / precomps
    for a in data.get('assets', []):
        for l in a.get('layers', []):
            walk_and_replace(l)

    return data

# Test on 14.tgs with #EEB419
with open("shablonlar/14.tgs", "rb") as f:
    d = json.loads(gzip.decompress(f.read()))

modified_d = replace_template_colors(d, primary_hex="#EEB419")
print("Template modified successfully!")
