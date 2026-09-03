import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, gzip

with open("shablonlar/14.tgs", "rb") as f:
    data = json.loads(gzip.decompress(f.read()))

def dump_tree(item, depth=0):
    indent = "  " * depth
    if isinstance(item, dict):
        nm = item.get("nm", "")
        ty = item.get("ty", "")
        print(f"{indent}- nm: '{nm}', ty: '{ty}'")
        if "it" in item:
            print(f"{indent}  (it len={len(item['it'])})")
            for sub in item["it"]:
                dump_tree(sub, depth+1)
        if "shapes" in item:
            print(f"{indent}  (shapes len={len(item['shapes'])})")
            for sub in item["shapes"]:
                dump_tree(sub, depth+1)

dump_tree(data["layers"][0])
