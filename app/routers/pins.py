from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from db import SessionDep
from modelos import Pin, Comentario, PinCreate

router = APIRouter(prefix="/pins", tags=["pins"])

@router.get("/")
def get_pins(session: SessionDep):
    return session.exec(select(Pin)).all()

@router.post("/", response_model=Pin, status_code=status.HTTP_201_CREATED)
def post_pin(pin: Pin, session: SessionDep):
    session.add(pin)
    session.commit()
    session.refresh(pin)
    return pin

@router.put("/{pin_id}", response_model=Pin)
def update_pin(pin_id: int, pin_data: PinCreate, session: SessionDep):
    db_pin = session.get(Pin, pin_id)
    if not db_pin:
        raise HTTPException(status_code=404, detail="Pin no encontrado")
    
    data = pin_data.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_pin, key, value)
        
    session.add(db_pin)
    session.commit()
    session.refresh(db_pin)
    return db_pin

@router.delete("/{pin_id}")
def delete_pin(pin_id: int, session: SessionDep):
    db_pin = session.get(Pin, pin_id)
    if not db_pin:
        raise HTTPException(status_code=404, detail="Pin no encontrado")
    session.delete(db_pin)
    session.commit()
    return {"message": "Pin eliminado"}

@router.post("/comentarios")
def post_comentario(comentario: Comentario, session: SessionDep):
    session.add(comentario)
    session.commit()
    session.refresh(comentario)
    return comentario