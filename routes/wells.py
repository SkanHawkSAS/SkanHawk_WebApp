# Librerias de desarrollo web
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from config.analytic_db import conn as psconn
from middlewares.verifyTokenRoute import VerifyTokenRoute
from schemas.well import Well
from helpers.wells import *
import pandas as pd


wells = APIRouter(prefix='/analytic')#route_class=VerifyTokenRoute)


@wells.get('/wells')
def Getwells():
    return psconn.execute(''' SELECT dbo.well.id, dbo.well.name_well, dbo.cluster.name_cluster as cluster, dbo.client.name as owner, dbo.field.name_field as field, dbo.zone.name as zone, dbo.well.latitude, dbo.well.longitude
                                FROM dbo.well
                                JOIN dbo.cluster
                                ON dbo.well.id_cluster = dbo.cluster.id
                                JOIN dbo.field
                                ON dbo.field.id = dbo.cluster.id_field
                                JOIN dbo.zone
                                ON dbo.zone.id = dbo.field.id_zone
                                JOIN dbo.client
                                ON dbo.client.id = dbo.field.id_client
                          ''').fetchall()

    
@wells.post('/wells')
def CreateWell(well: Well):
    try:
        addWell(client=well.owner, well=well.name, 
            zone=well.zone, field=well.field, cluster=well.cluster, 
            longitude=well.longitude, latitude=well.latitude)
        return "Well created Successfully"
    except Exception as e:
        return e

@wells.put('/wells/{id}')
def UpdateWell(id:int, well: Well):
    try:
        updateWell(id_well=id, cluster=well.cluster, name=well.name, 
                   longitude=well.longitude, latitude=well.latitude)
        return "Well updated Successfully"
    except Exception as e:
        return e

@wells.delete('/wells/{id}')
def DeleteWell(id:int):
    try:
        deleteWell(id)
        return "Well deleted Successfully"
    except Exception as e:
        return e
    
@wells.get('/wells/{id}/survey')
def GetSurvey(id: int):
    # Libreria de calculos de pozos
    import wellpathpy as wp
    
    query = f''' SELECT [id]
                ,[order_id]
                ,[measured_depth]
                ,[inclination]
                ,[azimut]
                ,[true_vertical_depth]
                ,[dogleg_severity]
                FROM [dbo].[survey] 
                WHERE id_well = {id} '''
    df_survey  = pd.read_sql(query, engine)
    md = df_survey['measured_depth']
    inc = df_survey['inclination']
    azi = df_survey['azimut']
    
    # Calculos de desviacion
    dev = wp.deviation(md, inc, azi)
    
    
    depth_step = 1
    depths = list(range(0,int(dev.md[-1])+1, depth_step))
    depths[-1]
    
    pos = dev.minimum_curvature().resample(depths=depths)
    pos 
    
    resampled_dev = pos.deviation()
    
    pos_tvdss = pos.to_tvdss(datum_elevation = 0)
    
    df = pd.DataFrame()
    df['MD'] = resampled_dev.md
    df['inclination'] = resampled_dev.inc
    df['azimuth'] = resampled_dev.azi
    df['TVD'] = pos_tvdss.depth
    df['northing'] = pos_tvdss.northing
    df['easting'] = pos_tvdss.easting
    

    dicts = []
    i = 0
    
    for row in df.itertuples():
    
        dicts.append({"md": row.MD, 
                      "inclination": row.inclination,
                      "azimuth": row.azimuth,
                      "tvd": row.TVD,
                      "northing": row.northing,
                      "easting": row.easting})
        
    


    return dicts
    
    

    
