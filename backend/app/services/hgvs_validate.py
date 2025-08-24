import re
from pydantic import BaseModel

"""Simplified HGVS cDNA regex.

Accepts transcript accession (letters/digits/underscore) with optional version suffix
e.g. NM_000000.0:c.123A>T
Position: simple numeric (no intronic +/- handling yet)
Substitution: reference base (A/C/G/T) > alt base (A/C/G/T or * for stop)
"""
HGVS_CDNA_REGEX = re.compile(r"^[A-Z0-9_]+(?:\.[0-9]+)?:c\.[0-9]+[ACGT]>[ACGT*]$")

class ParsedHGVS(BaseModel):
    transcript: str
    change: str

def validate_hgvs_cdna(hgvs: str) -> ParsedHGVS:
    """Very lightweight HGVS cDNA format validation.

    Raises ValueError if invalid; caller converts to HTTPException for API layer.
    """
    if not HGVS_CDNA_REGEX.match(hgvs):
        raise ValueError(
            "Invalid HGVS cDNA format (expected like NM_000001.1:c.123A>T). Currently only simple substitutions supported."
        )
    transcript, change = hgvs.split(":")
    return ParsedHGVS(transcript=transcript, change=change)
