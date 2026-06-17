from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from modelos import Usuario

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

@router.get("", response_model=list[Usuario])
def listar_usuarios(session: Session = Depends(get_session)):
    return session.exec(select(Usuario)).all()

@router.get("/{user_id}", response_model=Usuario)
def obtener_usuario(user_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return usuario