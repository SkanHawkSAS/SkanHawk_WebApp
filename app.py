from fastapi import FastAPI
from routes.users import user

app = FastAPI()

app.include_router(user) # declaro que la app usará las rutas definidas para user