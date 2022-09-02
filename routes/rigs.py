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
from sqlalchemy import desc

# Librerias matematicas
import pandas as pd
import numpy as np
import keras
from sklearn.preprocessing import StandardScaler

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

    # reorganizo la data en del mas viejo al mas nuevo
    data = data.sort_values('fecha_hora').reset_index(drop=True)

    data = evaluate_data(data)
    
    dataDB = psconn.execute(opsData.select().order_by(desc(opsData.c.id)).limit(10)).fetchall()

    dataDB = pd.DataFrame(dataDB)

    # agrego la data al base de datos local
    if not dataDB.empty:
        # reorganizo la data en del mas viejo al mas nuevo
        dataDB = dataDB.sort_values('fechaHora').reset_index(drop=True)

        for row in data.itertuples():
                for row2 in dataDB.itertuples():
                    if row2.fechaHora == row.fecha_hora and row2.deviceId == row.deviceId:
                        id_row = row2.id
                        if row2.operacion != row.operacion:
                            print(id_row)
                            psconn.execute(opsData.update().values(operacion=row.operacion).where(opsData.c.id == id_row))

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
                        break

    else:
        for row in data.itertuples():
            new_data = {"fechaHora": row.fecha_hora,
                            "deviceId": row.deviceId,
                            "cargaGancho": row.carga_gancho,
                            "posicionBloque": row.posicion_bloque,
                            "velocidadBloque": row.velocidad_bloque,
                            "profundidad": row.profundidad,
                            "contadorTuberia": row.contador_tuberia,
                            "operacion": row.operacion}
            psconn.execute(opsData.insert().values(new_data))   

    return HTMLResponse(data.to_html())


# funcion que aplica el modelo de IA
def evaluate_data(data):

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