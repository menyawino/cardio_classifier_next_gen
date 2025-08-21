import asyncio
from app.services.acmg_engine import evaluate_variant

async def _run():
    res = await evaluate_variant("NM_000000.0:c.123A>T", "GRCh38")
    assert res["classification"] in {"Likely Pathogenic", "VUS"}
    assert "applied_rules" in res

def test_eval_sync():
    asyncio.run(_run())
