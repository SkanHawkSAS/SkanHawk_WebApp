from pydantic import BaseModel
from typing import Optional


class OpData(BaseModel):
    id: Optional[str]
    fechaHora: float
    deviceId: str
    cargaGancho: float
    posicionBloque: float
    velocidadBloque: float
    profundidad: float    
    contadorTuberia: int
    operacion: str