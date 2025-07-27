import pytest_asyncio, httpx
from adaptive_ctx.memory_service import app
from adaptive_ctx.db import Base, engine


@pytest_asyncio.fixture
async def client():
    # ensure DB schema exists
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac