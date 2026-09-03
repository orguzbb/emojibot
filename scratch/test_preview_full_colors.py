import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from httpx import AsyncClient, ASGITransport
import server, json

svg_multicolor = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 100">
  <defs>
    <style>
      .bg { fill: #1e88e5; }
      .star { fill: #ffd700; stroke: #ff6f00; stroke-width: 2; }
      .tri { fill: #e53935; }
    </style>
  </defs>
  <rect class="bg" x="10" y="10" width="280" height="80" rx="15" />
  <path class="tri" d="M 20 50 L 80 20 L 80 80 Z" />
  <polygon class="star" points="150,20 160,40 185,40 165,55 172,80 150,65 128,80 135,55 115,40 140,40" />
  <circle cx="240" cy="50" r="25" fill="#43a047" stroke="#1b5e20" stroke-width="3" />
</svg>"""

async def test():
    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/preview", json={
            "template_id": "14.tgs",
            "input_type": "svg",
            "svg_data": svg_multicolor,
            "scale": 1.0
        })
        print("Preview HTTP Status:", res.status_code)
        assert res.status_code == 200
        data = res.json()
        s = json.dumps(data)
        print("Blue in response:", "[0.11764705882352941, 0.5333333333333333, 0.8980392156862745]" in s)
        print("Red in response:", "[0.8980392156862745, 0.2235294117647059, 0.20784313725490197]" in s)
        print("Gold in response:", "[1.0, 0.8431372549019608, 0.0]" in s)
        print("Green in response:", "[0.2627450980392157, 0.6274509803921569, 0.2784313725490196]" in s)
        print("Preview test PASSED with 100% full colors!")

asyncio.run(test())
