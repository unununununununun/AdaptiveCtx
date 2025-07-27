import json, pytest
from httpx import AsyncClient
from adaptive_ctx.memory_service import app

headers={"X-API-Key":"testkey"}

@pytest.mark.asyncio
async def test_export_import_cycle(client):
    # add sample
    await client.post("/update", headers=headers, json={"q":"E1","a":"A1","ns":"ns1"})
    # export
    res = await client.get("/admin/export", headers=headers, params={"ns":"ns1"})
    assert res.status_code==200
    data=json.loads(res.content)
    assert data and data[0]["text"].startswith("Q: E1")
    # import into ns2
    res2=await client.post("/admin/import", headers=headers,json={"ns":"ns2","items":data})
    assert res2.json()["imported"]==len(data)
    # query in ns2
    res3=await client.post("/query", headers=headers, json={"query":"A1","top_k":1,"ns":"ns2"})
    assert res3.status_code==200
    assert res3.json()