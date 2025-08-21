import re
from pydantic import BaseModel

HGVS_CDNA_REGEX = re.compile(r"^[A-Z0-9_]+:c\.[0-9]+[ACGT]>[ACGT*]$")

class ParsedHGVS(BaseModel):
    transcript: str
    change: str

def validate_hgvs_cdna(hgvs: str) -> ParsedHGVS:
    """Very lightweight HGVS cDNA format validation.

    Raises ValueError if invalid; caller converts to HTTPException for API layer.
    """
    if not HGVS_CDNA_REGEX.match(hgvs):
        raise ValueError("Invalid simplified HGVS cDNA format")
    transcript, change = hgvs.split(":")
    return ParsedHGVS(transcript=transcript, change=change)
