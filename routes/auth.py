from jwt import encode, decode
from jwt import exceptions
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

from fastapi import APIRouter, Header
from config.db import conn
from models.user import users
from schemas.user import User
from cryptography.fernet import Fernet
from routes.users import f
from pydantic import BaseModel, EmailStr
from sqlalchemy.sql.sqltypes import String


auth = APIRouter()

class loginInfo(BaseModel):
    email: EmailStr
    password: str

@auth.post('/login')
def login(user: loginInfo):

    userEmail = user.email
    userPass = user.password

    userInfo = conn.execute(users.select().where(users.c.email == userEmail)).first()

    if userPass == f.decrypt(userInfo.password.encode("utf-8")):
        return userInfo
    return f.decrypt(userInfo.password)















SECRET = '%$sk4nh4wk&d3s4rr0ll02022*!=?'

def expireToken(days: int):
    date = datetime.now()
    newDate = date +  timedelta(days)
    return newDate


def writeToken(data: dict):
    token = encode(payload={**data, "exp": expireToken(2)}, key=SECRET, algorithm="HS256")
    return token


def validateToken(token, output=False):
    try:
        if output:
            return decode(token, key=SECRET, algorithms=["HS256"])
        decode(token, key=SECRET, algorithms=["HS256"])
    except exceptions.DecodeError:
        return JSONResponse(content={"message": "Invalid Token"}, status_code=401)
    except exceptions.ExpiredSignatureError:
        return JSONResponse(content={"message": "Token Expired"}, status_code=401)