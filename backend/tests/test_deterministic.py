import asyncio
import os
from app.services.acmg_engine import evaluate_variant

async def _run():
    os.environ["DETERMINISTIC_TESTS"] = "1"
    res1 = await evaluate_variant("NM_000000.0:c.123A>T", "GRCh38")
    res2 = await evaluate_variant("NM_000000.0:c.123A>T", "GRCh38")
    assert res1 == res2, "Deterministic mode results should match"

def test_deterministic():
    asyncio.run(_run())
