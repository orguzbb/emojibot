import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from httpx import AsyncClient, ASGITransport
import server

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <g transform="translate(10, 10) scale(0.8)">
    <circle cx="50" cy="50" r="40" fill="none" stroke="#000" stroke-width="4"/>
    <polygon points="50,15 61,38 86,38 66,54 73,78 50,62 27,78 34,54 14,38 39,38" fill="gold"/>
  </g>
</svg>"""

async def test():
    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test preview
        res = await client.post("/api/preview", json={
            "template_id": "14.tgs",
            "input_type": "svg",
            "text": "SVG",
            "font": "stapel",
            "scale": 1.0,
            "svg_data": test_svg
        })
        print("Preview status:", res.status_code)
        if res.status_code != 200:
            print("Preview error body:", res.text)
        else:
            data = res.json()
            layers = data.get("layers", [])
            print(f"Preview success: {len(layers)} layers returned.")
            # Check if SVG shapes are in the layers
            found_svg = False
            for l in layers:
                for sh in l.get("shapes", []):
                    if "SVG" in str(sh.get("nm", "")) or "Vector" in str(sh.get("nm", "")):
                        found_svg = True
            print("Found SVG shape in layer:", found_svg)

asyncio.run(test())
