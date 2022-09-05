from passlib.context import CryptContext
from config.db import conn
from models.user import users

SECRET_KEY = "cc9258c101bd150705b99792fdf715faf88a8811a8161e0a4aec1d573d58793d"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def VerifyPassword(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def GetPwdHash(password):
    return pwd_context.hash(password)


def AuthUser(userEmail: str, password: str):
    userInfo = conn.execute(users.select().where(users.c.email == userEmail)).first()
    if not userInfo:
        return 1
    if not VerifyPassword(password, userInfo.password):
        return 2
    return userInfo