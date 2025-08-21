import re
from pydantic import BaseModel, ValidationError

HGVS_CDNA_REGEX = re.compile(r"^[A-Z0-9_]+:c\.[0-9]+[ACGT]>[ACGT*]$")

class ParsedHGVS(BaseModel):
    transcript: str
    change: str

def validate_hgvs_cdna(hgvs: str) -> ParsedHGVS:
    if not HGVS_CDNA_REGEX.match(hgvs):
        raise ValidationError([
            {
                'loc': ('hgvs',),
                'msg': 'Invalid simplified HGVS cDNA format',
                'type': 'value_error'
            }
        ], ParsedHGVS)
    transcript, change = hgvs.split(":")
    return ParsedHGVS(transcript=transcript, change=change)
