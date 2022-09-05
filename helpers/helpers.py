from jwt import encode, decode
from jwt import exceptions
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

SECRET = '%$sk4nh4wk&d3s4rr0ll02022*!=?'

def ExpireToken(days: int):
    date = datetime.now()
    newDate = date +  timedelta(days)
    return newDate


def WriteToken(data: dict):
    token = encode(payload={**data, "exp": ExpireToken(2)}, key=SECRET, algorithm="HS256")
    return token


def ValidateToken(token, output=False):
    try:
        if output:
            return decode(token, key=SECRET, algorithms=["HS256"])
        decode(token, key=SECRET, algorithms=["HS256"])
    except exceptions.DecodeError:
        return JSONResponse(content={"message": "Invalid Token"}, status_code=401)
    except exceptions.ExpiredSignatureError:
        return JSONResponse(content={"message": "Token Expired"}, status_code=401)