import pytest
from httpx import AsyncClient
from adaptive_ctx.memory_service import app

@pytest.mark.asyncio
async def test_auth_required(client):
    # without key should get 401
    resp = await client.post("/update", json={"q":"x","a":"y","ns":"auth"})
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_auth_ok(client):
    headers = {"X-API-Key": "testkey"}
    resp = await client.post("/update", headers=headers, json={"q":"AuthQ","a":"AuthA","ns":"auth"})
    assert resp.status_code == 200