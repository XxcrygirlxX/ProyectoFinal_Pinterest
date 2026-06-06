from fastapi import FastAPI, HTTPException, Form, status
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, pins
from db import create_all_table
from ldap3 import Server, Connection, ALL
import logging

app = FastAPI(lifespan=create_all_table)

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


#conexión con Active Directory
app = FastAPI(title="Pinterest - Integración Directa con Active Directory")

#cambiar dia de defensa por la ip que dio el DHCP en el DC01
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
            detail="Acceso denegado: Usuario o contraseña incorrectos en el dominio UIDE.A"
        )
    
    if username.lower() == "amartinez":
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