import pytest, httpx
from adaptive_ctx.memory_service import app

@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app, lifespan="on")
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac