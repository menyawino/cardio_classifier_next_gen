from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..services.acmg_engine import evaluate_variant
from ..services.hgvs_validate import validate_hgvs_cdna
from ..core.db import get_session
from ..repository.variants import VariantRepository
from ..models.variant import Variant as VariantModel
from ..repository.classification_events import ClassificationEventRepository
from ..core.security import get_current_user

class VariantRequest(BaseModel):
    hgvs: str
    genome_build: str = "GRCh38"

class VariantResponse(BaseModel):
    id: int | None = None
    hgvs: str
    genome_build: str
    classification: str
    applied_rules: list
    rationale: str

router = APIRouter()

@router.post("/classify", response_model=VariantResponse)
async def classify_variant(req: VariantRequest, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    # Validate HGVS format (simplified)
    try:
        validate_hgvs_cdna(req.hgvs)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    result = await evaluate_variant(req.hgvs, req.genome_build)
    repo = VariantRepository(session)
    variant = await repo.create(
        hgvs=req.hgvs,
        genome_build=req.genome_build,
        classification=result["classification"],
        evidence=result["applied_rules"],
        created_by=current_user.id,
    )
    ev_repo = ClassificationEventRepository(session)
    await ev_repo.add_event(variant_id=variant.id, user_id=current_user.id, classification=result["classification"], evidence=result["applied_rules"])
    return VariantResponse(id=variant.id, hgvs=variant.hgvs, genome_build=variant.genome_build, **result)


@router.get("/{variant_id}", response_model=VariantResponse)
async def get_variant(variant_id: int, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    repo = VariantRepository(session)
    variant = await repo.get(variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return VariantResponse(
        id=variant.id,
        hgvs=variant.hgvs,
        genome_build=variant.genome_build,
        classification=variant.classification,
        applied_rules=variant.evidence,
        rationale="Persisted record",
    )


@router.get("/", response_model=List[VariantResponse])
async def list_variants(hgvs: str | None = None, limit: int = 25, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    repo = VariantRepository(session)
    variants = await repo.list(hgvs=hgvs, limit=limit)
    return [
        VariantResponse(
            id=v.id,
            hgvs=v.hgvs,
            genome_build=v.genome_build,
            classification=v.classification,
            applied_rules=v.evidence,
            rationale="Persisted record",
        )
        for v in variants
    ]


class BatchRequest(BaseModel):
    variants: List[VariantRequest]

class BatchResultItem(BaseModel):
    hgvs: str
    genome_build: str
    classification: str
    id: int

@router.post("/batch", response_model=List[BatchResultItem])
async def batch_classify(req: BatchRequest, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    repo = VariantRepository(session)
    results: List[BatchResultItem] = []
    for v in req.variants:
        eval_res = await evaluate_variant(v.hgvs, v.genome_build)
        persisted = await repo.create(hgvs=v.hgvs, genome_build=v.genome_build, classification=eval_res["classification"], evidence=eval_res["applied_rules"], created_by=current_user.id)
        ev_repo = ClassificationEventRepository(session)
        await ev_repo.add_event(variant_id=persisted.id, user_id=current_user.id, classification=eval_res["classification"], evidence=eval_res["applied_rules"])
        results.append(BatchResultItem(hgvs=persisted.hgvs, genome_build=persisted.genome_build, classification=persisted.classification, id=persisted.id))
    return results

class ClassificationEventResponse(BaseModel):
    id: int
    classification: str
    evidence: list
    created_at: str
    user_id: int | None

@router.get("/{variant_id}/history", response_model=List[ClassificationEventResponse])
async def variant_history(variant_id: int, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    ev_repo = ClassificationEventRepository(session)
    events = await ev_repo.list_for_variant(variant_id)
    return [ClassificationEventResponse(id=e.id, classification=e.classification, evidence=e.evidence, created_at=str(e.created_at), user_id=e.user_id) for e in events]
