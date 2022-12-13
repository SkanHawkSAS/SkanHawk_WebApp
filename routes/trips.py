# Librerias de desarrollo web
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from config.analytic_db import conn as psconn
from sqlalchemy import desc
from middlewares.verifyTokenRoute import VerifyTokenRoute
from schemas.trip import Trip
from helpers.trips import *


trips = APIRouter(prefix='/analytic')#route_class=VerifyTokenRoute)


@trips.get('/trips/{page}')
async def GetTrips(page: int):
    return await psconn.execute(f'''SELECT id, client,rig,  well, 
                            intervention, zone, 
                            date_start, date_end, activity, pipe, [key] , comments
                            FROM (SELECT ROW_NUMBER() OVER (ORDER BY dbo.trips.id) as row ,dbo.trips.id, dbo.client.name as client, dbo.rig.name_rig as rig, dbo.well.name_well as well, 
                            dbo.interventions.name as intervention, dbo.zone.name as zone, 
                            dbo.trips.date_start, dbo.trips.date_end, dbo.trips.activity, dbo.pipe_details.name as pipe, dbo.trips.[key] , dbo.trips.comments
                            FROM dbo.trips
                            JOIN dbo.interventions
                            ON dbo.trips.id_interventions = dbo.interventions.id
                            JOIN dbo.rig
                            ON dbo.interventions.id_rig = dbo.rig.id
                            JOIN dbo.pipe_details
                            ON dbo.pipe_details.id = dbo.trips.id_pipe
                            JOIN dbo.well
                            ON dbo.interventions.id_well = dbo.well.id
                            JOIN dbo.cluster
                            ON dbo.cluster.id = dbo.well.id_cluster
                            JOIN dbo.field
                            ON dbo.field.id = dbo.cluster.id_field
                            JOIN dbo.zone
                            ON dbo.zone.id = dbo.field.id_zone
                            JOIN dbo.client
                            ON dbo.client.id = dbo.field.id_client) as roweredTable
                            WHERE roweredTable.row BETWEEN {(page-1)*100} AND {(page)*100}
                          ''').fetchall()
    
@trips.post('/trips')
async def CreateTrip(trip: Trip):
    
    await addTrip(trip.nameRig, trip.client, trip.nameWell, trip.activity,
            trip.intervention, trip.pipe, trip.key, trip.dateStart, 
            trip.dateEnd, trip.comments)

    return "Trip added successfully"

@trips.put('/trips/{id}')
async def EditIntervention(id:int, trip: Trip):
    print(trip)
    
    await updateTrip(id, trip.activity, trip.nameWell, trip.intervention, trip.pipe, 
               trip.key, trip.dateStart, trip.dateEnd, trip.comments)
    
    return "Trip updated successfully"

@trips.delete('/trips/{id}')
async def DeleteIntervention(id:int):
    
    await deleteTrip(id)
    
    return "Trip deleted Successfully"

    
# @trips.get('/wells')
# def GetWells():
#     return psconn.execute(''' SELECT dbo.well.id, dbo.well.name_well, dbo.cluster.name_cluster as cluster, dbo.client.name as owner, dbo.field.name_field as field, dbo.zone.name as zone
#                                 FROM dbo.well
#                                 JOIN dbo.cluster
#                                 ON dbo.well.id_cluster = dbo.cluster.id
#                                 JOIN dbo.field
#                                 ON dbo.field.id = dbo.cluster.id_field
#                                 JOIN dbo.zone
#                                 ON dbo.zone.id = dbo.field.id_zone
#                                 JOIN dbo.client
#                                 ON dbo.client.id = dbo.field.id_client
#                           ''').fetchall()


# @trips.get('/clients')
# def GetClients():
#     return psconn.execute(''' SELECT *
#                                 FROM dbo.client
#                           ''').fetchall()
    
    

    

    
