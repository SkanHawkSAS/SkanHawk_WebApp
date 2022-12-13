# Librerias de desarrollo web
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from config.analytic_db import conn as psconn
from sqlalchemy import desc
from middlewares.verifyTokenRoute import VerifyTokenRoute
from schemas.intervention import Intervention
from helpers.interventions import *


interventions = APIRouter(prefix='/analytic')#route_class=VerifyTokenRoute)


@interventions.get('/interventions')
async def GetInterventions():
    return await psconn.execute(''' SELECT dbo.interventions.id, dbo.client.name as client, dbo.rig.name_rig, dbo.well.name_well, dbo.interventions.name as intervention, dbo.zone.name as zone, dbo.interventions.date_start, dbo.interventions.date_reception, dbo.interventions.date_end
                                FROM dbo.interventions
                                JOIN dbo.rig
                                ON dbo.rig.id = dbo.interventions.id_rig
                                JOIN dbo.well
                                on dbo.well.id = dbo.interventions.id_well
                                JOIN dbo.cluster
                                ON dbo.cluster.id = dbo.well.id_cluster
                                JOIN dbo.field
                                ON dbo.cluster.id_field = dbo.field.id
                                JOIN dbo.zone
                                ON dbo.zone.id = dbo.field.id_zone
                                JOIN dbo.client
                                ON dbo.field.id_client = dbo.client.id
                          ''').fetchall()
@interventions.post('/interventions')
async def CreateIntervention(interv: Intervention):
    new_interv = {"client": interv.client, "nameRig": interv.nameRig, "nameWell": interv.nameWell, "intervention": interv.intervention, "zone": interv.zone, "dateStart": interv.dateStart, "dateReception": interv.dateReception, "dateEnd": interv.dateEnd}
    
    await addInterv(new_interv['client'], new_interv['nameRig'], new_interv['intervention'], new_interv['dateStart'], new_interv['dateReception'], new_interv['dateEnd'], new_interv['nameWell'])

    return "Intervention added successfully"

@interventions.put('/interventions/{id}')
async def EditIntervention(id:int, interv: Intervention):
    
    await updateInterv(id, interv.nameRig, interv.nameWell, interv.intervention, interv.dateStart, interv.dateReception, interv.dateEnd)
    

    return "Intervention updated successfully"

@interventions.delete('/interventions/{id}')
async def DeleteIntervention(id:int):
    
    await deleteInterv(id)
    return "Intervention deleted successfully"

    

    

    
