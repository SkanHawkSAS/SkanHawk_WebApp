from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from config.db import conn
from models.user import users
from schemas.user import User
from cryptography.fernet import Fernet




user = APIRouter()

key = Fernet.generate_key()
f = Fernet(key)



@user.get('/')
def helloWorld():
    return HTMLResponse("<h1> Hello world </h1>")

@user.get('/users')
def get_users():
    return conn.execute(users.select()).fetchall()

@user.post('/users')
def create_user(user: User):
    new_user = {"name": user.name, "email": user.email, "company": user.company, "role": user.role, "accessLevel": user.accessLevel}
    new_user["password"] = f.encrypt(user.password.encode("utf-8"))
    result = conn.execute(users.insert().values(new_user))
    return conn.execute(users.select().where(users.c.id == result.lastrowid)).first()

@user.put('/users/{id}')
def edit_user(id:int, user:User):
    conn.execute(users.update().values(name=user.name, email=user.email, password=user.password).where(users.c.id == id))
    user = conn.execute(users.select().where(users.c.id == id)).first()
    return user

@user.delete('/users/{id}')
def delete_user(id:int):
    user = conn.execute(users.select().where(users.c.id == id)).first()
    conn.execute(users.delete().where(users.c.id == id))
    return f"se elimino el usuario {user.name}"