# Librerias de desarrollo web
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from config.analytic_db import conn as psconn
from middlewares.verifyTokenRoute import VerifyTokenRoute
from schemas.well import Well
from helpers.wells import *


wells = APIRouter(prefix='/analytic')#route_class=VerifyTokenRoute)


@wells.get('/wells')
def Getwells():
    return psconn.execute(''' SELECT dbo.well.id, dbo.well.name_well, dbo.cluster.name_cluster as cluster, dbo.client.name as owner, dbo.field.name_field as field, dbo.zone.name as zone
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
def CreateTrip(well: Well):
    
    pass

@wells.put('/wells/{id}')
def EditIntervention(id:int, well: Well):
    pass

@wells.delete('/wells/{id}')
def DeleteIntervention(id:int):
    try:
        deleteWell(id)
        return "Well deleted Successfully"
    except Exception as e:
        return Exception
    
@wells.get('/wells/{id}/survey')
def GetSurvey():
    pass
    

    
