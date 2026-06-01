from fastapi import APIRouter, HTTPException
from modelos import Usuario, UsuarioCreate
from db import SessionDep

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(datos: UsuarioCreate, session: SessionDep):
    usuario = Usuario(email=datos.email, password=datos.password)
    session.add(usuario)
    session.commit()
    return {"message": "Usuario registrado"}

@router.post("/login")
def login(datos: Usuario, session: SessionDep):
    user = session.query(Usuario).filter(Usuario.email == datos.email).first()
    if not user or user.password != datos.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"message": "Login exitoso"}