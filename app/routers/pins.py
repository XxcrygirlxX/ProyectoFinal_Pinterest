import requests
from fastapi import APIRouter, HTTPException, status
from typing import List
from db import SessionDep
from modelos import Pin, Comentario
from sqlmodel import select

router = APIRouter(prefix="/pins", tags=["pins"])

@router.post("/")
def post_pin(pin: Pin, session: SessionDep):
    try:
        res = requests.post("http://localhost:3000/predict", json={"url": pin.source}, timeout=3)
        if res.json().get("is_nsfw"): raise HTTPException(status_code=400, detail="Imagen no apta")
    except: pass
    
    session.add(pin)
    session.commit()
    return pin

@router.get("/", response_model=List[Pin])
def get_pins(session: SessionDep):
    statement = select(Pin)
    results = session.exec(statement)
    return results.all()

@router.delete("/{pin_id}")
def delete_pin(pin_id: int, session: SessionDep):
    pin = session.get(Pin, pin_id)
    if not pin: raise HTTPException(status_code=404, detail="No encontrado")
    session.delete(pin)
    session.commit()
    return {"message": "Borrado"}

@router.post("/{pin_id}/comentarios")
def post_comentario(pin_id: int, comentario: Comentario, session: SessionDep):
    comentario.pin_id = pin_id
    session.add(comentario)
    session.commit()
    return comentario

@router.patch("/{pin_id}/reportar")
def reportar_pin(pin_id: int, session: SessionDep):
    pin = session.get(Pin, pin_id)
    if not pin: raise HTTPException(status_code=404, detail="Pin no encontrado")
    
    pin.reportado = True
    session.add(pin)
    session.commit()
    session.refresh(pin)
    return {"message": "Pin reportado exitosamente"}

@router.get("/")
def get_pins(session: SessionDep):
    return session.query(Pin).filter(Pin.reportado == False).all()