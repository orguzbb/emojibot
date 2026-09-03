import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from httpx import AsyncClient, ASGITransport
import server, json

async def test_api_badge_color():
    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test 1: Preview with badge_color="#EEB419"
        res = await client.post("/api/preview", json={
            "template_id": "14.tgs",
            "text": "ALISHER",
            "badge_color": "#EEB419"
        })
        assert res.status_code == 200, f"Preview failed: {res.text}"
        data = res.json()
        s = json.dumps(data)
        # #EEB419 RGB in JSON
        print("0.9333333333333333 in preview:", "0.9333333333333333" in s)
        assert "0.9333333333333333" in s, "Expected #EEB419 color in preview response"

        # Test 2: Batch Preview with badge_color="#EEB419"
        res2 = await client.post("/api/batch_preview", json={
            "template_ids": ["14.tgs", "15.tgs", "20.tgs", "50.tgs"],
            "text": "ALISHER",
            "badge_color": "#EEB419"
        })
        assert res2.status_code == 200, f"Batch preview failed: {res2.text}"
        data2 = res2.json()
        assert len(data2["previews"]) == 4
        print("Batch preview returned all 4 templates successfully!")

        print("API TESTS WITH BADGE COLOR PASSED 100%!")

asyncio.run(test_api_badge_color())
