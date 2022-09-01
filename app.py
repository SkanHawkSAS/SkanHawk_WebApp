from fastapi import FastAPI
from routes.users import user
from routes.rigs import rigs
app = FastAPI()

app.include_router(user) # declaro que la app usará las rutas definidas para user
app.include_router(rigs)