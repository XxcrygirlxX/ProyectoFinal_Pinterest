import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlmodel import select
from db import get_session, create_all_table
from modelos import Usuario 
import logging
from fastapi import FastAPI, HTTPException, Form, status, Body
from fastapi.middleware.cors import CORSMiddleware
from ldap3 import Server, Connection, ALL
from app.routers import auth, pins

app = FastAPI(
    title="Pinterest - Integración Directa con Active Directory",
    lifespan=create_all_table
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(pins.router)

@app.get("/")
def root():
    return {"status": "Pinterest API online"}

# 4. CONFIGURACIÓN DEL CONTROLADOR DE DOMINIO (DC01)
# Recuerda verificar con un 'ipconfig' en tu VM si esta IP cambia por DHCP el día de la defensa
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
        logging.error(f"Error de red o IP incorrecta al conectar con DC01 ({IP_DINAMICA_DC01}): {e}")
        return False

@app.post("/api/v1/auth/login-uide")
async def login_uide(
    username: str = Form(..., description="Usuario del Active Directory"),
    password: str = Form(..., description="Contraseña de la cuenta en la VM")
):
    es_valido = validar_credenciales_en_dc01(username, password)
    
    if not es_valido:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Acceso denegado: Usuario o contraseña incorrectos en el dominio {DOMINIO_LABORATORIO}"
        )
    
    # Simulación de Roles basados en cuentas del laboratorio
    if username.lower() == "aremache":
        rol_asignado = "Administrador de Sistemas"
        permisos = ["crear_usuarios", "eliminar_pines", "moderar_contenido_sensible"]
    else:
        rol_asignado = "Usuario General"
        permisos = ["ver_pines", "subir_imagenes", "crear_tableros"]

    return {
        "status": "success",
        "message": f"¡Autenticación centralizada exitosa en {DOMINIO_LABORATORIO}!",
        "datos_sesion": {
            "nombre_usuario": username,
            "rol_en_app": rol_asignado,
            "permisos_pinterest": permisos
        }
    }


# Configuración de tu cuenta de correo saliente (SMTP)
# Tip: Si usas Gmail, recuerda activar una "Contraseña de aplicación" en tu cuenta de Google
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "tu_correo_de_pruebas@gmail.com" 
SENDER_PASSWORD = "tu_contraseña_de_aplicacion_aqui" 

GOOGLE_CLIENT_ID = "62688628748-80so2m75d6mtoeortm12mt1pf4stdup6.apps.googleusercontent.com"

def enviar_correo_confirmacion(destinatario_email: str, nombre_usuario: str):
    """Función para automatizar el despacho de correos electrónicos de bienvenida"""
    try:
        mensaje = MIMEMultipart()
        mensaje["From"] = SENDER_EMAIL
        mensaje["To"] = destinatario_email
        mensaje["Subject"] = "¡Te damos la bienvenida a Pinterest (Proyecto Laboratorio)!"

        cuerpo_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 20px;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 10px; border: 1px solid #e1e1e1;">
                    <h2 style="color: #e60023; text-align: center;">¡Hola, {nombre_usuario}!</h2>
                    <p style="font-size: 16px; color: #333333; text-align: center;">
                        Tu registro o inicio de sesión mediante **Google Sign-In** se ha procesado correctamente.
                    </p>
                    <hr style="border: none; border-top: 1px solid #eeeeee; margin: 20px 0;">
                    <p style="font-size: 14px; color: #767676; text-align: center;">
                        Esta es una notificación automática de tu laboratorio de Sistemas de Información.
                    </p>
                </div>
            </body>
        </html>
        """
        mensaje.attach(MIMEText(cuerpo_html, "html"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario_email, mensaje.as_string())
        server.quit()
        print(f"Correo de confirmación enviado exitosamente a: {destinatario_email}")
    except Exception as e:
        print(f"Error al enviar el correo SMTP: {e}")

@app.post("/api/v1/auth/google-login-register")
async def google_login_register(payload: dict = Body(...)):
    token = payload.get("credential")
    if not token:
        raise HTTPException(status_code=400, detail="Falta el token de credencial de Google")
    
    try:
        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        
        email_usuario = id_info.get("email")
        google_id = id_info.get("sub")
        nombre_usuario = id_info.get("name", "Usuario de Pinterest")
        
    except ValueError:
        raise HTTPException(status_code=401, detail="Token de Google inválido o expirado")
    
    with next(get_session()) as session:
        statement = select(Usuario).where(Usuario.email == email_usuario)
        usuario_existente = session.exec(statement).first()
        
        if not usuario_existente:
            nuevo_usuario = Usuario(
                email=email_usuario,
                google_id=google_id,
                password=None 
            )
            session.add(nuevo_usuario)
            session.commit()
            session.refresh(nuevo_usuario)
            print(f"Nuevo usuario creado mediante Google: {email_usuario}")
        
        enviar_correo_confirmacion(email_usuario, nombre_usuario)
        
        return {
            "status": "success",
            "message": "Autenticación de Google verificada",
            "datos_sesion": {
                "nombre_usuario": nombre_usuario,
                "email": email_usuario,
                "rol_en_app": "Usuario General",
                "permisos_pinterest": ["ver_pines", "subir_imagenes", "crear_tableros"]
            }
        }