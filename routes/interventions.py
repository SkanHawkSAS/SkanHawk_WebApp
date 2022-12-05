# Librerias de desarrollo web
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from config.analytic_db import conn as psconn
from sqlalchemy import desc
from middlewares.verifyTokenRoute import VerifyTokenRoute


interventions = APIRouter(prefix='/analytic')#route_class=VerifyTokenRoute)


@interventions.get('/interventions')
def GetInterverntios():
    return psconn.execute(''' SELECT dbo.interventions.id, dbo.rig.name_rig, dbo.well.name_well, dbo.interventions.name as intervention, dbo.interventions.date_start, dbo.interventions.date_reception, dbo.interventions.date_end
                                FROM dbo.interventions
                                JOIN dbo.rig
                                ON dbo.rig.id = dbo.interventions.id_rig
                                JOIN dbo.well
                                on dbo.well.id = dbo.interventions.id_well
                          ''').fetchall()
    
    
@interventions.get('/wells')
def GetWells():
    return psconn.execute(''' SELECT dbo.well.id, dbo.well.name_well, dbo.cluster.name_cluster, dbo.client.name, dbo.field.name_field, dbo.zone.name
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


@interventions.get('/trips')
def GetTrips():
    return psconn.execute(''' SELECT dbo.trips.id, dbo.well.name_well as well, dbo.interventions.name as intervention, dbo.trips.date_start, dbo.trips.date_end, dbo.trips.activity, dbo.pipe_details.name as pipe, dbo.trips.[key], dbo.trips.comments
                                FROM dbo.trips
                                JOIN dbo.interventions
                                ON dbo.trips.id_interventions = dbo.interventions.id
                                JOIN dbo.pipe_details
                                on dbo.pipe_details.id = dbo.trips.id_pipe
                                JOIN dbo.well
                                ON dbo.well.id = dbo.interventions.id_well
                          ''').fetchall()


@interventions.get('/clients')
def GetClients():
    return psconn.execute(''' SELECT *
                                FROM dbo.client
                          ''').fetchall()
    
@interventions.get('/clients')
def GetPipes():
    return psconn.execute(''' SELECT *
                                FROM dbo.pipe_details
                          ''').fetchall()
    
