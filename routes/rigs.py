# Librerias de desarrollo web
from unittest import result
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
from datetime import datetime
from sklearn.preprocessing import StandardScaler

rig = APIRouter()#route_class=VerifyTokenRoute)


######################################################################################################################
##### CRUD 
@rig.get('/rigs')
def GetRig():
    return psconn.execute(rigs.select()).fetchall()

@rig.post('/rigs')
def CreateRig(rig: Rig):
    new_rig = {"number": rig.number, "zone": rig.zone, "operator": rig.operator, "owner": rig.owner}
    result = psconn.execute(rigs.insert().values(new_rig))
    return "Rig added successfully"

@rig.put('/rigs/{id}')
def EditRig(id:int, rig:Rig):
    psconn.execute(rigs.update().values(number=rig.number, zone=rig.zone, operator=rig.operator, owner=rig.owner).where(rigs.c.id == id))
    rig = psconn.execute(rigs.select().where(rigs.c.id == id)).first()
    return f' Se actualizó correctamente el Rig {rig.number}'

@rig.delete('/rigs/{id}')
def DeleteRig(id:int):
    rig = psconn.execute(rigs.select().where(rigs.c.id == id)).first()
    psconn.execute(rigs.delete().where(rigs.c.id == id))
    return f"se elimino el Rig {rig.number}"

##########################################################################################################################
## Funcionalidades
@rig.put('/rigs/{id}/update')
def GetRigDataUpdateDB(id: int):

    # Obtengo la ultima fila

    dataDB = psconn.execute(opsData.select().order_by(desc(opsData.c.id)).where(opsData.c.deviceId == f'IndependenceRig{id}').limit(1)).fetchall()
    dataDB = pd.DataFrame(dataDB)
    lastRegDate = dataDB['fechaHora'][0]

    dateNow = datetime.now()

    # Con este query obtengo los 60 registros mas recientes de la base de datos de SQL server
    query = f'''
        SELECT
            fecha_hora,
			deviceId,
            posicion_bloque,
            velocidad_bloque,
            carga_gancho,
            profundidad,
            contador_tuberia
            FROM tlc.Ecopetrol_Operational_data_SH
        WHERE deviceId = 'IndependenceRig{id}' AND fecha_hora BETWEEN {lastRegDate} AND {dateNow}	
        ORDER BY fecha_hora DESC
    '''
    data = pd.read_sql_query(query, sqlEngine)

    # reorganizo la data en del mas viejo al mas nuevo
    data = data.sort_values('fecha_hora').reset_index(drop=True)

    data = EvaluateData(data)


     
    # agrego la data al base de datos local
    
    for row in data.itertuples():
        # Se agregan solo los registros nuevos
        if not dataDB.empty:
            if dataDB['fechaHora'][0] < row.fecha_hora:
                new_data = {"fechaHora": row.fecha_hora,
                                "deviceId": row.deviceId,
                                "cargaGancho": row.carga_gancho,
                                "posicionBloque": row.posicion_bloque,
                                "velocidadBloque": row.velocidad_bloque,
                                "profundidad": row.profundidad,
                                "contadorTuberia": row.contador_tuberia,
                                "operacion": row.operacion}
                psconn.execute(opsData.insert().values(new_data))
        else:
            new_data = {"fechaHora": row.fecha_hora,
                                "deviceId": row.deviceId,
                                "cargaGancho": row.carga_gancho,
                                "posicionBloque": row.posicion_bloque,
                                "velocidadBloque": row.velocidad_bloque,
                                "profundidad": row.profundidad,
                                "contadorTuberia": row.contador_tuberia,
                                "operacion": row.operacion}
            psconn.execute(opsData.insert().values(new_data))  
    return 'UPDATED'

@rig.get('/rigs/{id}/historicos')
def GetRigDataHist(id:int, hoursBefore: int = 24):

    secs = hoursBefore*3600
    reg = int(secs/4)

    dataDB = psconn.execute(opsData.select().order_by(desc(opsData.c.id)).where(opsData.c.deviceId == f'IndependenceRig{id}').limit(reg)).fetchall()
    dataDB = pd.DataFrame(dataDB)

    dataDB['fecha_hora'] = dataDB['fecha_hora'].astype(str)

    dict_res = {}

    dicts = []
    

    for row in dataDB.itertuples():
        dict_res["fecha_hora"] = row.fecha_hora
        dict_res["deviceId"] = row.deviceId
        dict_res["carga_gancho"] = row.carga_gancho
        dict_res["posicion_bloque"] = row.posicion_bloque
        dict_res["velocidad_bloque"] = row.velocidad_bloque
        dict_res["profundidad"] = row.profundidad
        dict_res["contador_tuberia"] = row.contador_tuberia
        dict_res["operacion"] = row.operacion
        dicts.append(dict_res)

    dicts_ = {}
    for i in range(len(dicts)):
        dicts_[f"A{i}"] = dicts[i]

    return dicts_


@rig.get('/rigs/{id}')
def GetRigDataRT(id:int):
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

    # reorganizo la data en del mas viejo al mas nuevo
    data = data.sort_values('fechaHora').reset_index(drop=True)

    data = EvaluateData(data)


     # Obtengo la ultima fila

    dataDB = psconn.execute(opsData.select().order_by(desc(opsData.c.id)).where(opsData.c.deviceId == f'IndependenceRig{id}').limit(1)).fetchall()
    dataDB = pd.DataFrame(dataDB)
    # agrego la data al base de datos local
    
    for row in data.itertuples():
        # Se agregan solo los registros nuevos
        if not dataDB.empty:
            if dataDB['fechaHora'][0] < row.fecha_hora:
                new_data = {"fechaHora": row.fecha_hora,
                                "deviceId": row.deviceId,
                                "cargaGancho": row.carga_gancho,
                                "posicionBloque": row.posicion_bloque,
                                "velocidadBloque": row.velocidad_bloque,
                                "profundidad": row.profundidad,
                                "contadorTuberia": row.contador_tuberia,
                                "operacion": row.operacion}
                psconn.execute(opsData.insert().values(new_data))
        else:
            new_data = {"fechaHora": row.fecha_hora,
                                "deviceId": row.deviceId,
                                "cargaGancho": row.carga_gancho,
                                "posicionBloque": row.posicion_bloque,
                                "velocidadBloque": row.velocidad_bloque,
                                "profundidad": row.profundidad,
                                "contadorTuberia": row.contador_tuberia,
                                "operacion": row.operacion}
            psconn.execute(opsData.insert().values(new_data))  
    rslt_df = data[dataDB['fechaHora'][0]<data['fecha_hora']]

    if rslt_df.empty:
        rslt_df = data[dataDB['fechaHora'][0]==data['fecha_hora']]

    rslt_df['fecha_hora'] = rslt_df['fecha_hora'].astype(str)

    dict_res = {}

    dicts = []
    

    for row in rslt_df.itertuples():
        dict_res["fecha_hora"] = row.fecha_hora
        dict_res["deviceId"] = row.deviceId
        dict_res["carga_gancho"] = row.carga_gancho
        dict_res["posicion_bloque"] = row.posicion_bloque
        dict_res["velocidad_bloque"] = row.velocidad_bloque
        dict_res["profundidad"] = row.profundidad
        dict_res["contador_tuberia"] = row.contador_tuberia
        dict_res["operacion"] = row.operacion
        dicts.append(dict_res)

    dicts_ = {}
    for i in range(len(dicts)):
        dicts_[f"A{i}"] = dicts[i]

    return dicts_

# funcion que aplica el modelo de IA
def EvaluateData(data):

    data = data

    columns = ['posicion_bloque', 'profundidad', 'velocidad_bloque', 'carga_gancho', 'contador_tuberia']

    scaler = StandardScaler()
    scaler.fit(data[columns].values)

    # Cargo el modelo
    model = keras.models.load_model('./ML/ML_Model.h5')

    data_Scale = scaler.transform(data[columns].values)

    data_expand = np.expand_dims(data_Scale, axis=0)

    labels = ['POOH', 'RIH', 'OTHER']    

    prediction = model.predict(data_expand)

    value_label = labels[np.argmax(prediction)]

    tag = [value_label]*data_expand.shape[1]

    data['operacion'] = tag

    return data