from fastapi.responses import JSONResponse

from fastapi import APIRouter, Header
from config.db import conn
from models.user import users
from schemas.user import User
from helpers.helpers import ValidateToken, WriteToken

from pydantic import BaseModel, EmailStr
from sqlalchemy.sql.sqltypes import String
from helpers.auth import AuthUser

auth = APIRouter()

class loginInfo(BaseModel):
    email: EmailStr
    password: str


@auth.post('/login')
def Login(user: loginInfo):

    userEmail = user.email
    userPass = user.password

    userInfo = AuthUser(userEmail, userPass)
    
    if userInfo==1 or userInfo==2:
        if userInfo == 1:
            return JSONResponse(content={"message": "User not found"}, status_code=404)
        else:
            return JSONResponse(content={"message": "Incorrect Password"})
    else:
        return WriteToken(user.dict())
    
    


@auth.post("/verify/token")
def VerifyToken(Authorization: str = Header(None)):
    token = Authorization.split(" ")[1]
    return ValidateToken(token, output=True)