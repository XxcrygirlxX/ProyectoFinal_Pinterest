from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import pins
from db import create_all_table

app = FastAPI(lifespan=create_all_table)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(pins.router)

@app.get("/")
def root():
    return {"status": "Pinterest API online"}