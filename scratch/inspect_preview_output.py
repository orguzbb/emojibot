import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from httpx import AsyncClient, ASGITransport
import server

test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="red"/>
  <path d="M20 20 L80 80"/>
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
        data = res.json()
        print("HTTP Status:", res.status_code)
        for i, l in enumerate(data.get("layers", [])):
            for j, s in enumerate(l.get("shapes", [])):
                for k, it in enumerate(s.get("it", [])):
                    print(f"Layer {i} Shape {j} Sub {k}: nm={it.get('nm')}")

asyncio.run(test())
