from pydantic import BaseModel
from typing import Optional


class Rig(BaseModel):
    id: Optional[str]
    name: str