from pydantic import BaseModel
from typing import Optional


class OpData(BaseModel):
    id: Optional[str]
    md: float
    inclination: str
    azimuth: float
    tvd: float
    northing: float
    easting: float  