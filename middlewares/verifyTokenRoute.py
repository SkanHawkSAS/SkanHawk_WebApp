from fastapi import Request
from helpers.helpers import ValidateToken
from fastapi.routing import APIRoute


# class VerifyTokenRoute(APIRoute):

#     def GetRouteHandler(self):
#         original_route = super().GetRouteHandler()

#         async def VerifyTokenMiddleware(request:Request):
#             token = request.headers["Authorization"].split(" ")[1]

#             validationResponse = ValidateToken(token, output=False)
#             print(validationResponse)
#             if validationResponse == None:
#                 return await original_route(request)
#             else:
#                 return validationResponse
            
#         return VerifyTokenMiddleware

class VerifyTokenRoute(APIRoute):
    def get_route_handler(self):
        original_route = super().get_route_handler()
        
        async def verify_token_middleware(request:Request):
            token = request.headers["Authorization"].split(" ")[1]
            
            validation_response = ValidateToken(token, output=False)
            if validation_response == None:
                return await original_route(request)
            else:
                return validation_response

        return verify_token_middleware