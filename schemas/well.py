from pydantic import BaseModel
from typing import Optional


class Well(BaseModel):
    id: Optional[str]
    name: str
    cluster: str
    owner: str
    field: str
    zone: str
    latitude: str
    longitude: str