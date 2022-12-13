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
def CreatePipe(pipe: Pipe):
    
    addPipe(pipe.name, pipe.tqMin, pipe.tqOptimum, pipe.tqMax)

    return "Pipe added successfully"

@pipes.put('/pipes/{id}')
def EditPipe(id:int, pipe: Pipe):
    
    updatePipe(id, pipe.name, pipe.tqMin, pipe.tqOptimum, pipe.tqMax)
    
    return "Pipe updated successfully"

@pipes.delete('/pipes/{id}')
def DeletePipe(id:int):
    
    deletePipe(id)
    
    return "Pipe deleted Successfully"