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
def get_rig():
    return psconn.execute(rigs.select()).fetchall()

@rig.post('/rigs')
def create_rig(rig: Rig):
    new_rig = {"number": rig.number, "zone": rig.zone, "operator": rig.operator, "owner": rig.owner}
    result = psconn.execute(rigs.insert().values(new_rig))
    print(result)
    return "Rig added successfully"

@rig.put('/rigs/{id}')
def edit_rig(id:int, rig:Rig):
    psconn.execute(rigs.update().values(number=rig.number, zone=rig.zone, operator=rig.operator, owner=rig.owner).where(rigs.c.id == id))
    rig = psconn.execute(rigs.select().where(rigs.c.id == id)).first()
    return f' Se actualizó correctamente el Rig {rig.number}'

@rig.delete('/rigs/{id}')
def delete_rig(id:int):
    rig = psconn.execute(rigs.select().where(rigs.c.id == id)).first()
    psconn.execute(rigs.delete().where(rigs.c.id == id))
    return f"se elimino el usuario {rig.number}"

##########################################################################################################################
## Funcionalidades
@rig.get('/rigs/{id}')
def get_rig_data(id:int):
    # Con este query obtengo los 60 registros mas recientes de la base de datos de SQL server
    query = f'''
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
    
    return HTMLResponse(data.to_html())