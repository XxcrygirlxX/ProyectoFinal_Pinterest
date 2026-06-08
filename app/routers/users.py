from fastapi import APIRouter
from sqlmodel import select
from db import SessionDep
from modelos import Usuario, Pin, PinGuardado

router = APIRouter()

# Editar perfil (biografía, nombre, foto)
@router.put("/perfil/{usuario_id}")
def editar_perfil(usuario_id: int, nombre: str, biografia: str, session: SessionDep):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario.nombre = nombre
    usuario.biografia = biografia
    session.add(usuario)
    session.commit()
    return {"message": "Perfil actualizado", "usuario": usuario}

# Obtener los pines CREADOS por el usuario
@router.get("/perfil/{usuario_id}/pines-creados")
def pines_creados(usuario_id: int, session: SessionDep):
    statement = select(Pin).where(Pin.usuario_id == usuario_id)
    return session.exec(statement).all()

# Obtener los pines GUARDADOS por el usuario
@router.get("/perfil/{usuario_id}/pines-guardados")
def pines_guardados(usuario_id: int, session: SessionDep):
    statement = select(PinGuardado).where(PinGuardado.usuario_id == usuario_id)
    return session.exec(statement).all()