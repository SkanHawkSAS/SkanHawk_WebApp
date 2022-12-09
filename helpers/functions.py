from config.analytic_db import conn
from config.analytic_db import engine
import pandas as pd

def addInterv(cliente, torre, intervention, fecha_inicio, fecha_recepcion, fecha_fin, pozo):
    cliente = cliente
    Torre = torre
    intervencion = intervention
    fecha_recepcion = fecha_inicio
    fecha_inicio = fecha_recepcion
    fecha_fin = fecha_fin
    pozo = pozo
    
    # Obtengo el id del cliente
    query_cliente = f''' SELECT id FROM [dbo].[client] WHERE name = '{cliente}' '''
    
    df_client = pd.read_sql(query_cliente, engine)
    
    id_client = df_client.iloc[0,0]
    
    # Obtengo el id de la torre
    query_torre = f''' SELECT id FROM [dbo].[rig] WHERE name_rig = '{Torre}' '''
    
    df_torre = pd.read_sql(query_torre, engine)
    
    if len(df_torre) == 0:
        query_insert_torre = f''' INSERT INTO [dbo].[rig] (name_rig)
                                  VALUES ('{Torre}') '''
        query_torre = f''' SELECT id FROM [dbo].[rig] WHERE name_rig = '{Torre}' '''
    
        conn.execute(query_insert_torre)
        
        df_torre = pd.read_sql(query_torre, engine)
    
    id_torre = df_torre.iloc[0,0]
    
    # Obtengo el id del pozo
    query_pozo = f''' SELECT id FROM [dbo].[well] WHERE name_well = '{pozo}' '''
    
    df_pozo = pd.read_sql(query_pozo, engine)

    id_pozo = df_pozo.iloc[0,0]
    
    # Reviso si ya existe la intervención
    
    # Agrego la información de la intervencion
    query_insert_interv = f''' INSERT INTO [dbo].[interventions] (id_rig, id_well, date_reception, date_start, date_end, name)
                                    VALUES ({id_torre},{id_pozo}, '{fecha_recepcion}', '{fecha_inicio}', '{fecha_fin}', '{intervencion}') '''
    conn.execute(query_insert_interv)
    
    
    
def updateInterv(id_interv, torre, pozo, name, date_start, date_recep, date_end):
    # Obtengo el id de la torre
    query_torre = f''' SELECT id FROM [dbo].[rig] WHERE name_rig = '{torre}' '''
    
    df_torre = pd.read_sql(query_torre, engine)
    
    if len(df_torre) == 0:
        query_insert_torre = f''' INSERT INTO [dbo].[rig] (name_rig)
                                  VALUES ('{torre}') '''
        query_torre = f''' SELECT id FROM [dbo].[rig] WHERE name_rig = '{torre}' '''
    
        conn.execute(query_insert_torre)
        
        df_torre = pd.read_sql(query_torre, engine)
    
    id_torre = df_torre.iloc[0,0]
    
    # Obtengo el id del pozo
    query_pozo = f''' SELECT id FROM [dbo].[well] WHERE name_well = '{pozo}' '''
    
    df_pozo = pd.read_sql(query_pozo, engine)

    id_pozo = df_pozo.iloc[0,0]
    
    query = f''' UPDATE [dbo].[interventions]
                SET id_rig = '{id_torre}', id_well = '{id_pozo}', name = '{name}', date_start = '{date_start}', date_reception = '{date_recep}', date_end = '{date_end}'
                WHERE id = {id_interv}  '''
                
    try:
        conn.execute(query)
    except:
        return True
    
def deleteInterv(id):
    # Borrar Trip times
        # Obtengo los id de los viajes de esa intervencion
        query1 = f'''  SELECT id FROM dbo.trips
                      WHERE dbo.trips.id_interventions = {id}  '''
        df_trips = pd.read_sql(query1, engine)
        
        # para cada viaje elimino los calculos correspondientes
        for row in df_trips:
            id_trip = row
            # Calculos de tiempos
            query2 = f''' DELETE FROM [dbo].[trips_times]
                        WHERE id_trip = {id_trip} '''
            conn.execute(query2)
            
            # Calculos de pruebas de presion
            query3 = f''' DELETE FROM [dbo].[pressure_test]
                        WHERE id_trip = {id_trip} '''
            conn.execute(query3)
            
            # Elimino el viaje
            query4 = f''' DELETE FROM [dbo].[trips]
                    WHERE id = {id_trip} '''
            conn.execute(query4)    
    
    # Borrar Intervention
        query5 = f''' DELETE FROM [dbo].[dbo].[interventions]
                    WHERE id = {id} '''
        
        
        
        return conn.execute(query5) 
    
    