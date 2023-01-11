# Librerias de desarrollo web
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from config.analytic_db import conn as psconn
from config.sqlServer import conn as sqlconn
from config.sqlServer import engine as sqlEngine
from config.db import conn as dbconn
from models.opData import opsData
from schemas.opData import OpData
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

rig = APIRouter()#route_class=VerifyTokenRoute)


######################################################################################################################
##### CRUD 
@rig.get('/rigs')
def GetRig():
    return psconn.execute(''' SELECT * FROM dbo.rig ''').fetchall()

@rig.post('/rigs')
def CreateRig(rig: Rig):
    
    result = psconn.execute(f''' INSERT INTO [dbo].[rig]
           ([name_rig])
     VALUES
           ('{rig.name}') ''')
    return "Rig added successfully"

@rig.put('/rigs/{id}')
def EditRig(id:int, rig:Rig):
    psconn.execute(f''' UPDATE [dbo].[rig]
                        SET [name_rig] = '{rig.name}'
                        WHERE id = {id} ''')
    return f' Rig {rig.name} updated successfully'

@rig.delete('/rigs/{id}')
def DeleteRig(id:int):
    query = psconn.execute(f''' DELETE FROM dbo.rig WHERE id = {id} ''')
    return f"Rig deleted successfully"

##########################################################################################################################
## Funcionalidades
@rig.put('/rigs/{id}/update')
def GetRigDataUpdateDB(id: int):

    # Obtengo la ultima fila

    dataDB = dbconn.execute(opsData.select().order_by(desc(opsData.c.id)).where(opsData.c.deviceId == f'IndependenceRig{id}').limit(1)).fetchall()
    dataDB = pd.DataFrame(dataDB)
    lastRegDate = dataDB['fechaHora'][0]

    dateNow = datetime.now() - timedelta(hours=5)
    dateNow = dateNow.strftime("%Y-%m-%d %H:%M:%S")

    lastRegDate = pd.to_datetime(dataDB['fechaHora'][0])
    lastRegDate = lastRegDate.strftime("%Y-%m-%d %H:%M:%S")

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
        WHERE deviceId = 'IndependenceRig{id}' AND fecha_hora BETWEEN '{lastRegDate}' AND '{dateNow}'	
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

@rig.get('/rigs/{id}/historicos/')
async def GetRigDataHist(id:int, hoursBefore: int = 24, dateStart: str ='', dateEnd: str = '', cliente: str = 'ECOPETROL'):
    print(dateStart)
    print(dateEnd)
    print(cliente)
    
    if dateStart == '':

        secs = hoursBefore*3600
        reg = int(secs/4)

        dataDB = await getDataQuery2(id, reg)
        return dataDB
    else:
        if cliente == 'ECOPETROL':
            print('hola ecop')
        
            from config.db_ecop import engine as engine_op
            from config.db_ecop import conn as dataconn
            
            # Consulta SQL para solicitar los datos operacionales
            query = f'''SELECT
            fecha_hora, deviceId, posicion_bloque, velocidad_bloque, carga_gancho, profundidad, torque_hidraulica_max, torque_potencia_max
            FROM [tlc].[Ecopetrol_Operational_data_SH]
                WHERE (fecha_hora BETWEEN '{dateStart}' AND '{dateEnd}') AND deviceID ='IndependenceRig{id}' 
                ORDER BY fecha_hora ASC'''
            return dataconn.execute(query).fetchall()
    
        else:
            print('Hola oxy')
            from config.db_oxy import engine as engine_op
            from config.db_oxy import conn as dataconn
            # Consulta SQL para solicitar los datos operacionales
            query = f'''SELECT
            fecha_hora, deviceId, posicion_bloque, velocidad_bloque, carga_gancho, profundidad, torque_hidraulica_max, torque_potencia_max
            FROM Oxy.Oxy_Operational_data
                WHERE (fecha_hora BETWEEN '{dateStart}' AND '{dateEnd}') AND deviceID ='IndependenceRig{id}' '''
            
            return dataconn.execute(query).fetchall()


@rig.get('/rigs/{id}')
async def GetRigDataRT(id:int):
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
    data = data.sort_values('fecha_hora').reset_index(drop=True)

    data = EvaluateData(data)


     # Obtengo la ultima fila

    dataDB = await getDataQuery1(id)
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
                dbconn.execute(opsData.insert().values(new_data))
        else:
            new_data = {"fechaHora": row.fecha_hora,
                                "deviceId": row.deviceId,
                                "cargaGancho": row.carga_gancho,
                                "posicionBloque": row.posicion_bloque,
                                "velocidadBloque": row.velocidad_bloque,
                                "profundidad": row.profundidad,
                                "contadorTuberia": row.contador_tuberia,
                                "operacion": row.operacion}
            dbconn.execute(opsData.insert().values(new_data))  
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


    return dicts


async def getDataQuery1(id):
    return dbconn.execute(opsData.select().order_by(desc(opsData.c.id)).where(opsData.c.deviceId == f'IndependenceRig{id}').limit(1)).fetchall()

async def getDataQuery2(id, reg):
    return dbconn.execute(opsData.select().order_by(desc(opsData.c.id)).where(opsData.c.deviceId == f'IndependenceRig{id}').limit(reg)).fetchall()


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