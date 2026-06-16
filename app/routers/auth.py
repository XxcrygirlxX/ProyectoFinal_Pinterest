import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel

from db import get_session
from modelos import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# Configuración SMTP Real para Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
CORREO_REMITENTE = "elianna.suasnavas@gmail.com"  # <-- Tu Gmail emisor real
CONTRASENA_APLICACION = "ndam jufr mrxo agdg"       # <-- Tu clave de aplicación de 16 letras

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleTokenRequest(BaseModel):
    token: str

def despachar_correo_real(email_destino: str, username: str, tipo_evento: str = "Registro de Cuenta"):
    mensaje = MIMEMultipart()
    mensaje["From"] = CORREO_REMITENTE
    mensaje["To"] = email_destino
    mensaje["Subject"] = f"Fyntasy - Notificación: {tipo_evento}"

    cuerpo_html = f"""
    <html>
        <body style="background-color: #fff5f6; font-family: 'Segoe UI', sans-serif; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 20px; border: 1px solid #ffe3e8; text-align: center;">
                <h2 style="color: #ff4d6d; font-family: Georgia, serif;">Fyntasy</h2>
                <p style="color: #3a2226; font-size: 16px;">¡Hola, <strong>@{username}</strong>!</p>
                <p style="color: #8a7377; font-size: 14px; line-height: 1.5;">
                    Te notificamos que se ha procesado con éxito un evento de <strong>{tipo_evento}</strong> en tu perfil.
                </p>
                <div style="background-color: #fffafb; border-left: 4px solid #ff8fa3; padding: 10px; margin: 20px 0; text-align: left; font-size: 12px; color: #8a7377;">
                     <strong>Ecosistema Seguro:</strong> Mantenemos una comunidad armónica usando filtros automáticos de vocabulario y moderación por Inteligencia Artificial.
                </div>
            </div>
        </body>
    </html>
    """
    mensaje.attach(MIMEText(cuerpo_html, "html"))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(CORREO_REMITENTE, CONTRASENA_APLICACION)
        server.sendmail(CORREO_REMITENTE, email_destino, mensaje.as_string())
        server.quit()
        print(f"--> [SMTP SUCCESS] Correo Fyntasy enviado a: {email_destino}")
    except Exception as e:
        print(f"--> [SMTP ERROR] No se pudo enviar el correo: {e}")

@router.post("/register")
def registrar_usuario(usuario_nuevo: Usuario, session: Session = Depends(get_session)):
    usuario_existente = session.exec(select(Usuario).where(Usuario.email == usuario_nuevo.email)).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
    session.add(usuario_nuevo)
    session.commit()
    session.refresh(usuario_nuevo)
    despachar_correo_real(usuario_nuevo.email, usuario_nuevo.username, "Registro de Cuenta Nueva")
    return {"status": "success", "usuario_id": usuario_nuevo.id}

@router.post("/login")
def login_normal(datos: LoginRequest, session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.email == datos.email)).first()
    if not usuario or usuario.password != datos.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
    despachar_correo_real(usuario.email, usuario.username, "Inicio de Sesión Tradicional")
    return {"usuario_id": usuario.id, "user": {"username": usuario.username, "email": usuario.email}}

@router.post("/google")
def login_google(data: GoogleTokenRequest, session: Session = Depends(get_session)):
    email_google = "tu_cuenta_personal@gmail.com"  # <-- Tu correo real de pruebas
    username_google = "google_girl"
    usuario = session.exec(select(Usuario).where(Usuario.email == email_google)).first()
    if not usuario:
        usuario = Usuario(username=username_google, email=email_google, password="oauth_google_secure_123")
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
    despachar_correo_real(usuario.email, usuario.username, "Inicio de Sesión vía Google Identity")
    return {"usuario_id": usuario.id, "user": {"username": usuario.username, "email": usuario.email}}