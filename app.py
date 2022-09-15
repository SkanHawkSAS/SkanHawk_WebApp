from fastapi import FastAPI
from routes.users import user
from routes.rigs import rig
from routes.auth import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://192.168.1.71",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user) # declaro que la app usará las rutas definidas para user
app.include_router(rig)
app.include_router(auth)