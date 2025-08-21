from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..models.classification_event import ClassificationEvent

class ClassificationEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_event(self, variant_id: int, user_id: int | None, classification: str, evidence: list) -> ClassificationEvent:
        ev = ClassificationEvent(variant_id=variant_id, user_id=user_id, classification=classification, evidence=evidence)
        self.session.add(ev)
        await self.session.commit()
        await self.session.refresh(ev)
        return ev

    async def list_for_variant(self, variant_id: int, limit: int = 50) -> List[ClassificationEvent]:
        stmt = select(ClassificationEvent).where(ClassificationEvent.variant_id == variant_id).order_by(ClassificationEvent.id.desc()).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars())
