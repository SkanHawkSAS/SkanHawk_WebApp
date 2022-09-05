import imp
import re
from fastapi import Request
from helpers.helpers import ValidateToken
from fastapi.routing import APIRoute


class VerifyTokenRoute(APIRoute):

    def GetRouteHandler(self):
        original_route = super().getRouteHandler()

        async def VerifyTokenMiddleware(request:Request):
            token = request.headers["Authorization"].split(" ")[1]

            validationResponse = ValidateToken(token, output=False)
            if validationResponse == None:
                return await original_route(request)
            else:
                return validationResponse
            
        return VerifyTokenMiddleware