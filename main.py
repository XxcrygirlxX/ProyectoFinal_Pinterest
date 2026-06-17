import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from db import create_all_table
from app.routers import auth, pins, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_table()
    print(" Base de datos e infraestructura de Fyntasy inicializada correctamente.")
    yield

app = FastAPI(title="Fyntasy Core API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Montaje con prefijos limpios y estandarizados
app.include_router(auth.router, prefix="/api/v1")
app.include_router(pins.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

@app.get("/")
def home():
    return {"status": "online", "message": "Ecosistema Fyntasy activo"}