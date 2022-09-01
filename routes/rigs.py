import numbers
from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from config.db import conn
from models.opData import opsData
from schemas.opData import OpData
from models.rig import rigs
from schemas.rig import Rig


rig = APIRouter()

@rig.get('/rigs')
def get_users():
    return conn.execute(rigs.select()).fetchall()

@rig.post('/rigs')
def create_user(rig: Rig):
    new_rig = {"number": rig.number, "zone": rig.zone, "operator": rig.operator, "owner": rig.owner}
    result = conn.execute(rigs.insert().values(new_rig))
    print(result)
    return "User created successfully"

@rig.put('/rigs/{id}')
def edit_rig(id:int, rig:Rig):
    conn.execute(rigs.update().values(number=rig.number, zone=rig.name, operator=rig.operator, owner=rig.owner).where(rigs.c.id == id))
    rig = conn.execute(rigs.select().where(rigs.c.id == id)).first()
    return f' Se actualizó correctamente el Rig {rig.number}'

@rig.delete('/rigs/{id}')
def delete_user(id:int):
    rig = conn.execute(rigs.select().where(rigs.c.id == id)).first()
    conn.execute(rigs.delete().where(rigs.c.id == id))
    return f"se elimino el usuario {rig.number}"