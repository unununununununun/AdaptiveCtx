import asyncio, os, json, pytest
from httpx import AsyncClient
from memory_service import app

os.environ["ADCTX_API_KEYS"] = "testkey"

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_update_query_cycle():
    headers = {"X-API-Key": "testkey"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # update
        resp = await ac.post("/update", headers=headers, json={"q":"Hello","a":"World","ns":"pytest"})
        assert resp.status_code == 200
        # query
        resp = await ac.post("/query", headers=headers, json={"query":"World","top_k":1,"ns":"pytest"})
        assert resp.status_code == 200
        data = resp.json()
        assert data and data[0]["text"].startswith("Q: Hello")