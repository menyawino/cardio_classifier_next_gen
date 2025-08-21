from pydantic import BaseModel
from typing import List, Dict, Any
import os
import httpx
from loguru import logger
from .cache import cache_get, cache_set
import hashlib

class EvidenceItem(BaseModel):
    code: str
    strength: str  # e.g., VeryStrong, Strong, Moderate, Supporting, StandAlone, Strong-Benign, Supporting-Benign
    satisfied: bool
    rationale: str
    sources: list[str] = []

# Mapping ACMG rule codes to categorical strengths (pathogenic or benign side)
RULE_STRENGTH_MAP: Dict[str, str] = {
    # Pathogenic side (subset for prototype)
    "PVS1": "VeryStrong",
    "PS1": "Strong",
    "PS2": "Strong",
    "PS3": "Strong",
    "PS4": "Strong",
    "PM1": "Moderate",
    "PM2": "Moderate",
    "PM5": "Moderate",
    "PP3": "Supporting",
    "PP5": "Supporting",
    # Benign side
    "BA1": "StandAloneBenign",
    "BS1": "StrongBenign",
    "BS2": "StrongBenign",
    "BP4": "SupportingBenign",
    "BP7": "SupportingBenign",
}

MCP_BASE = os.getenv("MCP_SERVER_URL", "http://localhost:8100")

async def mcp_call(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{MCP_BASE}{path}"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.warning(f"MCP call failed {url}: {e}")
        return {}

def deterministic_choice(values: List, key: str):
    h = int(hashlib.sha256(key.encode()).hexdigest(), 16)
    return values[h % len(values)]

async def fetch_evidence(hgvs: str) -> List[EvidenceItem]:
    evidence: List[EvidenceItem] = []
    deterministic = os.getenv("DETERMINISTIC_TESTS", "0") == "1"
    cache_key = f"evidence:{hgvs}"
    if not deterministic:
        cached = await cache_get(cache_key)
        if cached:
            return [EvidenceItem(**e) for e in cached]

    if deterministic:
        # Synthesize deterministic payloads
        clinvar = {"clinical_significance": deterministic_choice([None, "Pathogenic", "Likely pathogenic", "VUS"], hgvs)}
        gnomad = {"allele_frequency": deterministic_choice([0.00001, 0.0002, 0.002, 0.02], hgvs)}
        deleterious_tools = deterministic_choice(list(range(6)), hgvs)
        preds = {"deleterious_tools": deleterious_tools, "total_tools": 5}
    else:
        clinvar = await mcp_call("/clinvar", {"hgvs": hgvs})
        gnomad = await mcp_call("/gnomad", {"hgvs": hgvs})
        preds = await mcp_call("/predictions", {"hgvs": hgvs})
    # PM1 (hotspot) heuristic: if variant has certain pattern (e.g., :c.123A>G) just a placeholder
    if ":c." in hgvs and hgvs.endswith(">A"):
        evidence.append(EvidenceItem(code="PM1", strength="Moderate", satisfied=True, rationale="Hotspot region heuristic", sources=["heuristic"]))

    # BP7 (synonymous with no predicted splice impact) heuristic
    if "syn" in hgvs:
        evidence.append(EvidenceItem(code="BP7", strength="SupportingBenign", satisfied=True, rationale="Synonymous with no predicted splice impact (heuristic)", sources=["heuristic"]))

    # Loss-of-function heuristic
    if any(token in hgvs for token in ["del", "dup", "fs", "*", "stop"]):
        evidence.append(EvidenceItem(code="PVS1", strength="VeryStrong", satisfied=True, rationale="Predicted null variant in gene with established LoF mechanism (heuristic)", sources=["heuristic"]))

    # ClinVar significance translation (simplified)
    sig = clinvar.get("clinical_significance") if isinstance(clinvar, dict) else None
    if sig and "Pathogenic" in sig:
        evidence.append(EvidenceItem(code="PP5", strength="Supporting", satisfied=True, rationale=f"ClinVar significance {sig}", sources=["mcp:clinvar"]))
    elif sig and sig == "Benign":
        evidence.append(EvidenceItem(code="BP4", strength="SupportingBenign", satisfied=True, rationale="ClinVar benign", sources=["mcp:clinvar"]))

    # Population frequency for BS1 / BA1 simplistic thresholds
    af = gnomad.get("allele_frequency") if isinstance(gnomad, dict) else None
    if af is not None:
        if af > 0.01:
            evidence.append(EvidenceItem(code="BA1", strength="StandAloneBenign", satisfied=True, rationale=f"High AF {af}", sources=["mcp:gnomad"]))
        elif af > 0.001:
            evidence.append(EvidenceItem(code="BS1", strength="StrongBenign", satisfied=True, rationale=f"AF {af} exceeds BS1 threshold", sources=["mcp:gnomad"]))
    # In-silico predictions
    if preds:
        deleterious = preds.get("deleterious_tools", 0)
        total = preds.get("total_tools", 0) or 1
        if deleterious / total >= 0.6 and deleterious >=3:
            evidence.append(EvidenceItem(code="PP3", strength="Supporting", satisfied=True, rationale=f"{deleterious}/{total} deleterious tools", sources=["mcp:predictions"]))
        elif deleterious <=1:
            evidence.append(EvidenceItem(code="BP4", strength="SupportingBenign", satisfied=True, rationale=f"Low deleterious consensus {deleterious}/{total}", sources=["mcp:predictions"]))
    if not deterministic:
        await cache_set(cache_key, [e.model_dump() for e in evidence])
    return evidence


def combine_classification(counts: Dict[str, int]) -> str:
    vs = counts.get("VeryStrong", 0)
    s = counts.get("Strong", 0)
    m = counts.get("Moderate", 0)
    p = counts.get("Supporting", 0)
    ba = counts.get("StandAloneBenign", 0)
    bs = counts.get("StrongBenign", 0)
    bp = counts.get("SupportingBenign", 0)

    # Benign side first
    if ba >= 1 or bs >= 2:
        return "Benign"
    if (bs >= 1 and bp >=1) or (bp >= 2):
        return "Likely Benign"

    # Pathogenic side (ClinGen refined combinations simplified)
    if (vs >=1 and s >=1) or (vs >=1 and m >=2) or (vs >=1 and (m >=1 and p >=1)) or (s >=2 and m >=1) or (s >=1 and m >=3) or (vs >=1 and p >=2):
        return "Pathogenic"
    if (vs >=1 and m >=1) or (s >=1 and m >=1 and p >=2) or (s >=1 and p >=4) or (m >=3) or (m >=2 and p >=2) or (m >=1 and p >=4):
        return "Likely Pathogenic"

    return "VUS"


async def evaluate_variant(hgvs: str, genome_build: str) -> Dict[str, Any]:
    evidence = await fetch_evidence(hgvs)
    counts = {"VeryStrong":0, "Strong":0, "Moderate":0, "Supporting":0, "StandAloneBenign":0, "StrongBenign":0, "SupportingBenign":0}
    applied = []
    for ev in evidence:
        if not ev.satisfied:
            continue
        st = ev.strength
        if st in counts:
            counts[st] += 1
        elif st.startswith("StrongBenign"):
            counts["StrongBenign"] += 1
        elif st.startswith("SupportingBenign"):
            counts["SupportingBenign"] += 1
        applied.append(ev.model_dump())

    classification = combine_classification(counts)

    return {
        "classification": classification,
        "applied_rules": applied,
        "rationale": f"Counts: {counts}",
    }
