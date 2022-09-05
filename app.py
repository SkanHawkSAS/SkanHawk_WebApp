from fastapi import FastAPI
from routes.users import user
from routes.rigs import rig
from routes.auth import auth
app = FastAPI()

app.include_router(user) # declaro que la app usará las rutas definidas para user
app.include_router(rig)
app.include_router(auth)