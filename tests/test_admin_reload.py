import os, pytest, shutil, tempfile, json
from httpx import AsyncClient
from adaptive_ctx.memory_service import app, get_encoder
from sentence_transformers import SentenceTransformer

headers={"X-API-Key":"testkey"}

@pytest.mark.asyncio
async def test_reload_encoder_invalid():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.post("/admin/reload_encoder", headers=headers, json={"path":"/not/exist"})
        assert res.status_code==400

@pytest.mark.asyncio
async def test_reload_encoder_ok():
    # save current encoder to temp dir
    tmpdir=tempfile.mkdtemp()
    get_encoder().save(tmpdir)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.post("/admin/reload_encoder", headers=headers, json={"path":tmpdir})
        assert res.status_code==200
    shutil.rmtree(tmpdir)