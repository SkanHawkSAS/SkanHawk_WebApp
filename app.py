from fastapi import FastAPI
from routes.users import user
from routes.rigs import rig
from routes.auth import auth
from routes.interventions import interventions
from routes.pipes import pipes
from routes.wells import wells
from routes.trips import trips
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://192.168.1.71:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user) # declaro que la app usará las rutas definidas para user
app.include_router(rig)
app.include_router(auth)
app.include_router(interventions)
app.include_router(pipes)
app.include_router(trips)
app.include_router(wells)