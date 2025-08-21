from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from ..models.variant import Variant

class VariantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, hgvs: str, genome_build: str, classification: str, evidence: list) -> Variant:
        obj = Variant(hgvs=hgvs, genome_build=genome_build, classification=classification, evidence=evidence)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get(self, variant_id: int) -> Optional[Variant]:
        return await self.session.get(Variant, variant_id)

    async def list(self, hgvs: Optional[str] = None, limit: int = 25) -> List[Variant]:
        stmt = select(Variant).order_by(Variant.id.desc()).limit(limit)
        if hgvs:
            stmt = select(Variant).where(Variant.hgvs == hgvs).order_by(Variant.id.desc()).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars())
