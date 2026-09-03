import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from httpx import AsyncClient, ASGITransport
import server, json

async def run_suite():
    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Preview with custom hex color (#EEB419)
        r1 = await client.post("/api/preview", json={
            "template_id": "14.tgs",
            "input_type": "text",
            "text": "SHOHRUH",
            "badge_color": "#EEB419"
        })
        assert r1.status_code == 200
        d1 = r1.json()
        s1 = json.dumps(d1)
        assert "0.9333333333333333" in s1
        print("Test 1 (Text + #EEB419 badge): PASSED!")

        # 2. Preview with SVG + #EEB419 badge
        svg_sample = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="#00e676"/></svg>'
        r2 = await client.post("/api/preview", json={
            "template_id": "14.tgs",
            "input_type": "svg",
            "svg_data": svg_sample,
            "badge_color": "#EEB419"
        })
        assert r2.status_code == 200
        d2 = r2.json()
        s2 = json.dumps(d2)
        assert "0.9333333333333333" in s2
        assert "0.9019607843137255" in s2 # Green SVG color
        print("Test 2 (SVG + #EEB419 badge): PASSED!")

        # 3. Batch Preview with #EEB419
        r3 = await client.post("/api/batch_preview", json={
            "template_ids": ["14.tgs", "15.tgs", "20.tgs", "50.tgs", "100.tgs"],
            "input_type": "svg",
            "svg_data": svg_sample,
            "badge_color": "#EEB419"
        })
        assert r3.status_code == 200
        d3 = r3.json()
        assert len(d3["previews"]) == 5
        print("Test 3 (Batch Preview 5 templates with #EEB419): PASSED!")

        # 4. WebApp static files response test
        r_index = await client.get("/")
        assert r_index.status_code == 200
        assert "logo-color-section" in r_index.text
        print("Test 4 (index.html contains logo-color-section): PASSED!")

        r_css = await client.get("/style.css")
        assert r_css.status_code == 200
        assert "logo-color-customizer-section" in r_css.text
        print("Test 5 (style.css contains logo-color-customizer-section): PASSED!")

        r_js = await client.get("/app.js")
        assert r_js.status_code == 200
        assert "setBadgeColor" in r_js.text
        print("Test 6 (app.js contains setBadgeColor): PASSED!")

        print("\n🎉 ALL LOGO COLOR CUSTOMIZATION TESTS PASSED WITH 100% PERFECTION!")

asyncio.run(run_suite())
