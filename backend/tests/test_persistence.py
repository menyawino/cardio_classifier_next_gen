import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from app.main import app
from app.core.db import AsyncSessionLocal
from app.models.variant import Variant

@pytest.mark.asyncio
async def test_classify_persists_variant():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post('/variants/classify', json={'hgvs':'NM_000001:c.100A>T','genome_build':'GRCh38'})
        assert r.status_code == 200
        vid = r.json()['id']
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(Variant).where(Variant.id == vid))
            obj = res.scalar_one()
            assert obj.hgvs == 'NM_000001:c.100A>T'
            assert obj.classification in { 'Pathogenic','Likely Pathogenic','Likely Benign','Benign','VUS' }
