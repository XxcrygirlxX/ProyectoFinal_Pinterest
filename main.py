import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlmodel import select
from db import get_session, create_all_table 
from modelos import Usuario 
from fastapi import FastAPI, HTTPException, Form, status, Body
from fastapi.middleware.cors import CORSMiddleware
from ldap3 import Server, Connection, ALL
from app.routers import auth, pins, users
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_table() 
    print("¡Base de datos SQLite inicializada exitosamente!")
    yield
    print("Apagando API de Pinterest...")

app = FastAPI(
    title="Pinterest - Integración Directa con Active Directory",
    lifespan=lifespan
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(pins.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"status": "Pinterest API online"}

# ==========================================
# CONFIGURACIÓN DEL DIRECTORIO ACTIVO
# ==========================================
IP_DINAMICA_DC01 = "192.168.165.23"  
DOMINIO_LABORATORIO = "UIDE.A"

def validar_credenciales_en_dc01(usuario_login: str, contrasenia_login: str) -> bool:
    servidor_ad = Server(IP_DINAMICA_DC01, get_info=ALL)
    try:
        user_principal_name = f"{usuario_login}@{DOMINIO_LABORATORIO}"
        conexion = Connection(
            servidor_ad, 
            user=user_principal_name, 
            password=contrasenia_login, 
            check_names=True, 
            lazy=False
        )
        if conexion.bind():
            conexion.unbind() 
            return True
        return False
    except Exception as e:
        logging.error(f"Error al conectar con DC01 ({IP_DINAMICA_DC01}): {e}")
        return False

@app.post("/api/v1/auth/login-uide")
async def login_uide(
    username: str = Form(..., description="Usuario del Active Directory"),
    password: str = Form(..., description="Contraseña de la cuenta")
):
    es_valido = validar_credenciales_en_dc01(username, password)
    if not es_valido:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Acceso denegado en el dominio {DOMINIO_LABORATORIO}"
        )
    
    # Sincronización transparente de identidades LDAP con SQLite local
    with next(get_session()) as session:
        statement = select(Usuario).where(Usuario.email == f"{username}@{DOMINIO_LABORATORIO}")
        usuario_db = session.exec(statement).first()
        
        if not usuario_db:
            usuario_db = Usuario(email=f"{username}@{DOMINIO_LABORATORIO}", nombre=username)
            session.add(usuario_db)
            session.commit()
            session.refresh(usuario_db)
            
        usuario_id = usuario_db.id

    if username.lower() == "aremache":
        rol_asignado = "Administrador de Sistemas"
        permisos = ["crear_usuarios", "eliminar_pines", "moderar_contenido_sensible"]
    else:
        rol_asignado = "Usuario General"
        permisos = ["ver_pines", "subir_imagenes", "crear_tableros"]

    return {
        "status": "success",
        "message": "¡Autenticación centralizada exitosa!",
        "usuario_id": usuario_id,
        "datos_sesion": {
            "nombre_usuario": username,
            "rol_en_app": rol_asignado,
            "permisos_pinterest": permisos
        }
    }

# ==========================================
# CONFIGURACIÓN GOOGLE LOGIN Y CORREOS
# ==========================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "elianna.suasnavaso@gmail.com" 
SENDER_PASSWORD = "Elianna2006" 
GOOGLE_CLIENT_ID = "62688628748-80so2m75d6mtoeortm12mt1pf4stdup6.apps.googleusercontent.com"

def enviar_correo_confirmacion(destinatario_email: str, nombre_usuario: str):
    try:
        mensaje = MIMEMultipart()
        mensaje["From"] = SENDER_EMAIL
        mensaje["To"] = destinatario_email
        mensaje["Subject"] = "¡Te damos la bienvenida a Pinterest!"
        cuerpo_html = f"<h2>¡Hola, {nombre_usuario}! Tu registro fue exitoso.</h2>"
        mensaje.attach(MIMEText(cuerpo_html, "html"))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario_email, mensaje.as_string())
        server.quit()
    except Exception as e:
        print(f"Error SMTP: {e}")

@app.post("/api/v1/auth/google-login-register")
async def google_login_register(payload: dict = Body(...)):
    token = payload.get("credential")
    if not token:
        raise HTTPException(status_code=400, detail="Falta token")
    
    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        email_usuario = id_info.get("email")
        google_id = id_info.get("sub")
        nombre_usuario = id_info.get("name", "Usuario de Pinterest")
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    with next(get_session()) as session:
        statement = select(Usuario).where(Usuario.email == email_usuario)
        usuario_existente = session.exec(statement).first()
        
        if not usuario_existente:
            nuevo_usuario = Usuario(email=email_usuario, google_id=google_id, password=None, nombre=nombre_usuario)
            session.add(nuevo_usuario)
            session.commit()
            session.refresh(nuevo_usuario)
            usuario_id = nuevo_usuario.id
        else:
            usuario_id = usuario_existente.id
            
        enviar_correo_confirmacion(email_usuario, nombre_usuario)
        return {
            "status": "success",
            "usuario_id": usuario_id,
            "datos_sesion": {
                "nombre_usuario": nombre_usuario,
                "rol_en_app": "Usuario General",
                "permisos_pinterest": ["ver", "subir", "crear"]
            }
        }