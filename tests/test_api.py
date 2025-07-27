import asyncio, os, json, pytest
from httpx import AsyncClient
from adaptive_ctx.memory_service import app

os.environ["ADCTX_API_KEYS"] = "testkey"

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_update_query_cycle(client):
    headers = {"X-API-Key": "testkey"}
    resp = await client.post("/update", headers=headers, json={"q":"Hello","a":"World","ns":"pytest"})
    assert resp.status_code == 200
    resp = await client.post("/query", headers=headers, json={"query":"World","top_k":1,"ns":"pytest"})
    assert resp.status_code == 200
    data = resp.json()
    assert data and data[0]["text"].startswith("Q: Hello")