import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_invalid_hgvs_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/variants/classify", json={"hgvs":"BAD_FORMAT", "genome_build":"GRCh38"})
        assert resp.status_code == 422
