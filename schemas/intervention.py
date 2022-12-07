from pydantic import BaseModel
from typing import Optional


class Intervention(BaseModel):
    id: Optional[str]
    client: str
    nameRig: str
    nameWell: str
    intervention: str
    zone: str
    dateStart: str
    dateReception: str
    dateEnd: str