import pytest
from httpx import AsyncClient
from adaptive_ctx.memory_service import app

@pytest.mark.asyncio
async def test_auth_required():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # without key should get 401
        resp = await ac.post("/update", json={"q":"x","a":"y","ns":"auth"})
        assert resp.status_code == 401

@pytest.mark.asyncio
async def test_auth_ok():
    headers = {"X-API-Key": "testkey"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/update", headers=headers, json={"q":"AuthQ","a":"AuthA","ns":"auth"})
        assert resp.status_code == 200