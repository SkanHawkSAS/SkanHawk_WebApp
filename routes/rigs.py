import numbers
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from config.db import conn as psconn
from config.sqlServer import conn as sqlconn
from config.sqlServer import engine as sqlEngine
from models.opData import opsData
from schemas.opData import OpData
from models.rig import rigs
from schemas.rig import Rig
import pandas as pd


rig = APIRouter()


######################################################################################################################
##### CRUD 
@rig.get('/rigs')
async def get_rig():
    return psconn.execute(rigs.select()).fetchall()

@rig.post('/rigs')
async def create_rig(rig: Rig):
    new_rig = {"number": rig.number, "zone": rig.zone, "operator": rig.operator, "owner": rig.owner}
    result = await psconn.execute(rigs.insert().values(new_rig))
    print(result)
    return "User created successfully"

@rig.put('/rigs/{id}')
async def edit_rig(id:int, rig:Rig):
    await psconn.execute(rigs.update().values(number=rig.number, zone=rig.zone, operator=rig.operator, owner=rig.owner).where(rigs.c.id == id))
    rig = await psconn.execute(rigs.select().where(rigs.c.id == id)).first()
    return f' Se actualizó correctamente el Rig {rig.number}'

@rig.delete('/rigs/{id}')
async def delete_rig(id:int):
    rig = await psconn.execute(rigs.select().where(rigs.c.id == id)).first()
    await psconn.execute(rigs.delete().where(rigs.c.id == id))
    return f"se elimino el usuario {rig.number}"

##########################################################################################################################
## Funcionalidades
@rig.get('/rigs/{id}')
async def get_rig_data(id:int):
    query = '''
        SELECT TOP 60 
            fecha_hora,
			deviceId,
            posicion_bloque,
            velocidad_bloque,
            carga_gancho,
            profundidad,
            contador_tuberia
            FROM tlc.Ecopetrol_Operational_data_SH
        WHERE deviceId = 'IndependenceRig{id}'			
        ORDER BY fecha_hora DESC
    '''
    data = pd.read_sql_query(query, sqlEngine)
    return data
