from pydantic import BaseModel
from typing import Optional


class Rig(BaseModel):
    id: Optional[str]
    number: str
    zone: str
    operator: str
    owner: str