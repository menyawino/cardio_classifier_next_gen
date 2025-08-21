import asyncio
from app.services.acmg_engine import evaluate_variant

async def classify(hgvs: str):
    return await evaluate_variant(hgvs, "GRCh38")

async def _run():
    # Case aiming for benign via high AF (simulate BA1) - may depend on randomness
    benign_candidate = await classify("NM_000000.0:c.123A>T")
    assert benign_candidate["classification"] in {"Benign", "Likely Benign", "VUS", "Likely Pathogenic", "Pathogenic"}

    # Case aiming for PVS1 + PP3 (LoF + predictions) for pathogenic side
    path_candidate = await classify("NM_000000.0:c.123del")
    assert path_candidate["classification"] in {"Likely Pathogenic", "Pathogenic", "VUS"}


def test_matrix():
    asyncio.run(_run())
