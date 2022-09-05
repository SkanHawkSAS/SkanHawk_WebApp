from fastapi.responses import JSONResponse

from fastapi import APIRouter, Header
from config.db import conn
from models.user import users
from schemas.user import User
from helpers.helpers import ValidateToken, WriteToken

from pydantic import BaseModel, EmailStr
from sqlalchemy.sql.sqltypes import String


auth = APIRouter()

class loginInfo(BaseModel):
    email: EmailStr
    password: str

@auth.post('/login')
def Login(user: loginInfo):

    userEmail = user.email
    userPass = user.password

    userInfo = conn.execute(users.select().where(users.c.email == userEmail)).first()

    if userInfo != None:
        pwd = userInfo.password
        if userPass == pwd:
            return WriteToken(user.dict())
        else:
            return JSONResponse(content={"message": "Incorrect Password"})
    else:
        return JSONResponse(content={"message": "User not found"}, status_code=404)
    
    
    


@auth.post("/verify/token")
def VerifyToken(Authorization: str = Header(None)):
    token = Authorization.split(" ")[1]
    return ValidateToken(token, output=True)