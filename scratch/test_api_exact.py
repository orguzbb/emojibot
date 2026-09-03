import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from httpx import AsyncClient, ASGITransport
import server, json

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="red"/>
</svg>"""

async def test():
    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/preview", json={
            "template_id": "14.tgs",
            "input_type": "svg",
            "svg_data": test_svg,
            "scale": 1.0
        })
        layers = res.json().get("layers", [])
        s = json.dumps(layers)
        print("SVG_Symbol count in JSON response:", s.count("SVG_Symbol"))
        print("SVG Path count in JSON response:", s.count("SVG Path"))
        print("Logo path count in JSON response:", s.count("Logo path"))

asyncio.run(test())
