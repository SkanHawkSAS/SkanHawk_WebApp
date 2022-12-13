from config.analytic_db import conn
from config.analytic_db import engine
import pandas as pd
from helpers.times_calculation import *

def addTrip(rig, client, well, activity, intervention, pipe, key, dateStart, dateEnd, comments):
    torre = rig
    cliente = client
    pozo = well
    actividad = activity
    interv = intervention
    tipo_tuberia = pipe
    llave = key
    fecha_inicio = dateStart
    fecha_fin = dateEnd
    comentarios = comments
    
    # Agrego la información del viaje
    # Obtengo id de la intervención
    query_interv = f''' SELECT [dbo].[interventions].id FROM [dbo].[interventions] 
                        INNER JOIN dbo.well ON dbo.interventions.id_well = dbo.well.id 
                        WHERE name_well = '{pozo}' AND dbo.interventions.name = '{interv}'  '''
    
    df_interv = pd.read_sql(query_interv, engine)
    
    id_interv = df_interv.iloc[0,0]
    
    # Obtengo id del pozo
    query_pipe = f''' SELECT id FROM [dbo].[pipe_details] WHERE name = '{tipo_tuberia}' '''
    
    df_pipe = pd.read_sql(query_pipe, engine)
    
    id_pipe = df_pipe.iloc[0,0]
    

    query_insert_trips = f''' INSERT INTO [dbo].[trips] (id_interventions, id_pipe, [key], date_start, date_end, comments, activity)
                                VALUES ('{id_interv}', '{id_pipe}', '{llave}', '{fecha_inicio}', '{fecha_fin}', '{comentarios}', '{actividad}') '''
    conn.execute(query_insert_trips)
    
    # Obtengo el id del trip
    query_trip = f'''
        SELECT id FROM [dbo].[trips] WHERE id_interventions = '{id_interv}' and activity = '{actividad}'
    '''
    df_trip = pd.read_sql(query_trip, engine)
    id_trip = df_trip.iloc[0,0]
    
    if cliente == 'ECOPETROL':
        
        from config.db_ecop import engine as engine_op
        
        # Consulta SQL para solicitar los datos operacionales
        query = f'''SELECT
        fecha_hora, deviceId, posicion_bloque, velocidad_bloque, carga_gancho, profundidad, torque_hidraulica_max, torque_potencia_max
        FROM [tlc].[Ecopetrol_Operational_data_SH]
            WHERE (fecha_hora BETWEEN '{fecha_inicio}' AND '{fecha_fin}') AND deviceID ='{torre}' '''
    
    else:
        
        from config.db_oxy import engine as engine_op
        # Consulta SQL para solicitar los datos operacionales
        query = f'''SELECT
        fecha_hora, deviceId, posicion_bloque, velocidad_bloque, carga_gancho, profundidad, torque_hidraulica_max, torque_potencia_max
        FROM Oxy.Oxy_Operational_data
            WHERE (fecha_hora BETWEEN '{fecha_inicio}' AND '{fecha_fin}') AND deviceID ='{torre}' '''

    # Se crea un DataFrame con los datos de la consulta SQL.
    df = pd.read_sql(query, engine_op)

    # Se eliminan los datos duplicados.
    df = df.drop_duplicates().reset_index(drop=True)

    # Se convierte la columna fecha_hora a formato de fecha y hora.
    df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])

    # Se ordenan los datos por fecha y hora.
    df = df.sort_values(by="fecha_hora").reset_index(drop=True)
    
    df = df[['deviceId', 'fecha_hora', 'posicion_bloque', 'velocidad_bloque',
       'carga_gancho', 'profundidad', 'torque_hidraulica_max',
       'torque_potencia_max']]
    
    columns = ["Torre", "fecha_hora", "Posición Bloque [ft]", "Velocidad Bloque [ft/min]", "Carga Gancho [lb]", "Profundidad [ft]", "TQ. Llave Hid.  Max [lb*ft]", "TQ. Llave Pot.  Max [lb*ft]2"]
    df.columns = columns
    df["Posición Bloque [ft]"] = df['Posición Bloque [ft]'].abs()
    
    data_moments = deteccion_momentos_bloque(df, actividad, tipo_tuberia)
    data_times = tiempos_tuberia(data_moments, actividad)
    
    carga_min_bef = 2850
    carga_max_bef = 2850
    carga_avg_bef = 2850
    
    for row in data_times.itertuples():
        
        carga_maxima = row.carga_maxima
        carga_minima = row.carga_minima
        carga_promedio = row.carga_promedio
        
        ##############################
        if str(carga_maxima) == 'nan':
            carga_maxima = carga_max_bef
            
        if str(carga_minima) == 'nan':
            carga_minima = carga_min_bef
            
        if str(carga_promedio) == 'nan':
            carga_promedio = carga_avg_bef
            
            
            
        #####################################
        if str(row.carga_maxima) != 'nan':
            carga_max_bef = row.carga_maxima
        
        if str(row.carga_minima) != 'nan':
            carga_min_bef = row.carga_minima
            
        if str(row.carga_promedio) != 'nan':
            carga_avg_bef = row.carga_promedio
        
        values_list = [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20]]
        
        for j in range(len(values_list)):
            if str(values_list[j]) == 'nan':
                values_list[j] = 0                
              
                    
        
        # Agrego la información de la intervencion
        query_insert_times = f''' INSERT INTO [dbo].[trips_times]
                                        VALUES ('{id_trip}','{row.fecha_hora_inicio}','{row.fecha_hora_fin}',
                                        '{row.conexion}', '{carga_maxima}', '{carga_minima}', '{carga_promedio}',
                                        '{values_list[7]}', '{values_list[8]}', '{values_list[9]}', '{values_list[10]}', '{values_list[11]}',
                                        '{values_list[12]}', '{values_list[13]}', '{values_list[14]}', '{values_list[15]}', '{values_list[16]}','{values_list[17]}',
                                        '{values_list[18]}', '{values_list[19]}', '{values_list[20]}') '''

        conn.execute(query_insert_times)
    try:
        
        if 'RIH' in actividad:
            print('Identificando pruebas de presión...')
            print()
            df_presion = pruebas_presion(pd.to_datetime(fecha_inicio), pd.to_datetime(fecha_fin), cliente, torre, pozo, actividad, tipo_tuberia)
            # Recorremos el dataFrame que ya contiene todos los registros de las pruebas y finalmente se guardan en la base de datos
            for row in df_presion.itertuples():
                query = f'''INSERT INTO [dbo].[pressure_test]
                                values ('{id_trip}', '{row.fecha_hora}', '{row.barriles_por_minuto}', '{row.presion_bomba}', '{row.Prueba}')'''
                conn.execute(query)       
    except:
        print('No se encontraron pruebas de presión') 
        print() 
        
def updateTrip(id_trip, well, activity, intervention, pipe, key, dateStart, dateEnd, comments):
    
    # Obtengo el id del pozo
    query_well = f''' SELECT id FROM [dbo].[well] WHERE name_well = '{well}' '''
    
    df_well = pd.read_sql(query_well, engine)
    
    id_well = df_well.iloc[0,0]
    print(id_well)
    
    # Obtengo el id de la intervencion
    query_intervention = f''' SELECT id FROM [dbo].[interventions] WHERE name = '{intervention}' AND id_well = '{id_well}'  '''
    
    df_intervention = pd.read_sql(query_intervention, engine)
    
    id_intervention = df_intervention.iloc[0,0]
    print(id_intervention)
    
    # Obtengo el id de la tuberia
    query_pipe = f''' SELECT id FROM [dbo].[pipe_details] WHERE name = '{pipe}' '''
    
    df_pipe = pd.read_sql(query_pipe, engine)

    id_pipe = df_pipe.iloc[0,0]
    print(id_pipe)
    
    query = f''' UPDATE [dbo].[trips]
                SET id_interventions = '{id_intervention}', id_pipe = '{id_pipe}', 
                key = '{key}', date_start = '{dateStart}', date_end = '{dateEnd}', 
                comments = '{comments}', activity = '{activity}'  
                WHERE id = {id_trip}  '''
                

    conn.execute(query)
    
def deleteTrip(id):
    # Borrar Trip times
    id_trip = id
    print(id_trip)
    # Calculos de tiempos
    query1 = f''' DELETE FROM [dbo].[trips_times]
                WHERE id_trips = {id_trip} '''
    conn.execute(query1)
    
    # Calculos de pruebas de presion
    query2 = f''' DELETE FROM [dbo].[pressure_test]
                WHERE id_trips = {id_trip} '''
    conn.execute(query2)
    
    # Elimino el viaje
    query3 = f''' DELETE FROM [dbo].[trips]
            WHERE id = {id_trip} '''
    conn.execute(query3)    
        
        
    conn.execute(query3) 