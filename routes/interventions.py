# Librerias de desarrollo web
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from config.db import conn as psconn
from config.sqlServer import conn as sqlconn
from config.sqlServer import engine as sqlEngine
from models.opData import opsData
from schemas.opData import OpData
from models.rig import rigs
from schemas.rig import Rig
import json
from sqlalchemy import desc
from middlewares.verifyTokenRoute import VerifyTokenRoute


# Librerias matematicas
import pandas as pd
import numpy as np
import keras
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler

interventions = APIRouter(prefix='/interv')#route_class=VerifyTokenRoute)


@interventions.get('/rigs')
def GetRig():
    return psconn.execute(''' SELECT dbo.interventions.id, dbo.rig.name_rig, dbo.well.name_well, dbo.interventions.name as intervention
                                FROM dbo.interventions
                                JOIN dbo.rig
                                ON dbo.rig.id = dbo.interventions.id_rig
                                JOIN dbo.well
                                on dbo.well.id = dbo.interventions.id_well
                          ''')
