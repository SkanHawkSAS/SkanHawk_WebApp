from pydantic import BaseModel
from typing import Optional


class Trip(BaseModel):
    id: Optional[str]
    client: str
    nameRig: str
    nameWell: str
    intervention: str
    zone: str
    dateStart: str
    dateEnd: str
    activity: str
    pipe: str
    key: str
    comments: str