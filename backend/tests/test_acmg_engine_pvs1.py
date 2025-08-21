import asyncio
from app.services.acmg_engine import evaluate_variant

async def _run():
    res = await evaluate_variant("NM_000000.0:c.123G>*", "GRCh38")
    assert any(r["code"] == "PVS1" for r in res["applied_rules"]), "Expected PVS1 evidence present"
    assert res["classification"] in {"Pathogenic", "Likely Pathogenic", "VUS"}

def test_pvs1():
    asyncio.run(_run())
