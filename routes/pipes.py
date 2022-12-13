# Librerias de desarrollo web
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from config.analytic_db import conn as psconn
from sqlalchemy import desc
from middlewares.verifyTokenRoute import VerifyTokenRoute
from schemas.pipe import Pipe
from helpers.pipes import *


pipes = APIRouter(prefix='/analytic')#route_class=VerifyTokenRoute)


@pipes.get('/pipes')
def GetPipes():
    return psconn.execute(''' SELECT *
                                FROM dbo.pipe_details
                          ''').fetchall()
    
@pipes.post('/pipes')
async def CreatePipe(pipe: Pipe):
    
    await addPipe(pipe.name, pipe.tqMin, pipe.tqOptimum, pipe.tqMax)

    return "Pipe added successfully"

@pipes.put('/pipes/{id}')
async def EditPipe(id:int, pipe: Pipe):
    
    await updatePipe(id, pipe.name, pipe.tqMin, pipe.tqOptimum, pipe.tqMax)
    
    return "Pipe updated successfully"

@pipes.delete('/pipes/{id}')
async def DeletePipe(id:int):
    
    await deletePipe(id)
    
    return "Pipe deleted Successfully"