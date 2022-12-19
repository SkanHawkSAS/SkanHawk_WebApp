from config.analytic_db import conn
from config.analytic_db import engine
import pandas as pd
from helpers.times_calculation import *


def addWell(client, well, zone, field, cluster, longitude, latitude):
    
    query_cliente = f''' SELECT id FROM [dbo].[client] WHERE name = '{client}' '''
    
    df_client = pd.read_sql(query_cliente, engine)
    
    id_client = df_client.iloc[0,0]
    
    query_insert_zone = f''' INSERT INTO [dbo].[zone] (name)
                                  VALUES ('{zone}') '''
    query_zone = f''' SELECT id FROM [dbo].[zone] WHERE name = '{zone}' '''

    conn.execute(query_insert_zone)
    df_zone = pd.read_sql(query_zone, engine)
        
    id_zone = df_zone.iloc[0,0]
    
    query_insert_field = f''' INSERT INTO [dbo].[field] (id_client, id_zone , name_field)
                                VALUES ('{id_client}', '{id_zone}', '{field}') '''
    query_field = f''' SELECT id FROM [dbo].[field] WHERE name_field = '{field}' '''

    conn.execute(query_insert_field)
    df_field = pd.read_sql(query_field, engine)
    
    id_field = df_field.iloc[0,0]
    
    
    query_insert_cluster = f''' INSERT INTO [dbo].[cluster] (id_field, name_cluster)
                                VALUES ('{id_field}', '{cluster}') '''
    query_cluster = f''' SELECT id FROM [dbo].[cluster] WHERE name_cluster = '{cluster}' '''
    
    conn.execute(query_insert_cluster)
    df_cluster = pd.read_sql(query_cluster, engine)

    id_cluster = df_cluster.iloc[0,0]
    
    
    query_insert_well = f''' INSERT INTO [dbo].[well] (id_cluster, name_well, longitude, latitude)
                                  VALUES ('{id_cluster}', '{well}, {longitude}, {latitude}') '''
    
    conn.execute(query_insert_well)
    
def updateWell(id_well, cluster, longitude, latitude):
    
    query_cluster = f''' SELECT id FROM [dbo].[cluster] WHERE name = '{cluster}' '''
    
    df_cluster = pd.read_sql(query_cluster, engine)
    

    id_cluster = df_cluster.iloc[0,0]
    
    query = f''' UPDATE [dbo].[well]
                SET id_cluster = '{id_cluster}', longitude = '{longitude}', 
                latitude = '{latitude}'
                WHERE id = {id_well}  '''
                

    conn.execute(query)

def deleteWell(id_well):
    # Elimino el pozo
    query = f''' DELETE FROM [dbo].[well]
            WHERE id = {id_well} '''
    conn.execute(query)  
    
def calculateSurvey(id_well):
    
    query = f''' SELECT [id]
                ,[order_id]
                ,[measured_depth]
                ,[inclination]
                ,[azimut]
                ,[true_vertical_depth]
                ,[dogleg_severity]
                FROM [dbo].[survey] 
                WHERE id_well = {id_well} '''
    df_survey  = pd.read_sql(query, engine)
    
    pass