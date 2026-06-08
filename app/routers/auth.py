import smtplib

from fastapi import APIRouter, HTTPException
from modelos import Usuario, UsuarioCreate
from db import SessionDep

router = APIRouter(prefix="/auth", tags=["auth"])

def enviar_correo(email_destino: str):
    msg = EmailMessage()
    msg.set_content("Bienvenido a nuestro Pinterest. ¡Tu cuenta ha sido creada exitosamente!")
    msg['Subject'] = 'Bienvenido a Pinterest'
    msg['From'] = "elianna.suasnavaso@gmail.com"
    msg['To'] = email_destino

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("elianna.suasnavaso@gmail.com", "Elianna2006")
        smtp.send_message(msg)

@router.post("/register")
def register(datos: Usuario, session: SessionDep):
    user = session.query(Usuario).filter(Usuario.email == datos.email).first()
    if user: raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    nuevo_usuario = Usuario(email=datos.email, password=datos.password)
    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario) # IMPORTANTE: Obliga a SQLite a darnos el ID generado
    
    enviar_correo(datos.email)
    
    return {
        "message": "Usuario registrado y notificado",
        "usuario_id": nuevo_usuario.id,
        "nombre_usuario": nuevo_usuario.email.split("@")[0]
    }

@router.post("/login")
def login(datos: Usuario, session: SessionDep):
    user = session.query(Usuario).filter(Usuario.email == datos.email).first()
    if not user or user.password != datos.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    return {
        "message": "Login exitoso",
        "usuario_id": user.id,
        "nombre_usuario": user.nombre or user.email.split("@")[0]
    }

@router.post("/google-login")
def google_login(datos: dict, session: SessionDep):
    email = datos.get("email")
    user = session.query(Usuario).filter(Usuario.email == email).first()
    if not user:
        user = Usuario(email=email, google_id=datos.get("sub"))
        session.add(user)
        session.commit()
        enviar_correo(email)
    return {"message": "Login con Google exitoso"}