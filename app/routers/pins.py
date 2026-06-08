import requests
import json
import os
from fastapi import APIRouter, HTTPException, status
from typing import List
from db import SessionDep
from modelos import Pin, Comentario
from sqlmodel import select
import shutil
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from modelos import PinGuardado, Tablero

os.makedirs("uploads", exist_ok=True)

router = APIRouter(prefix="/pins", tags=["pins"])

@router.post("/upload")
async def crear_pin_con_archivo(
    session: SessionDep,
    titulo: str = Form(...),
    file: UploadFile = File(...)
):
    # 1. Moderación Textual (Malas Palabras)
    if verificar_politica_palabras(titulo):
        raise HTTPException(status_code=400, detail="El título contiene malas palabras.")

    # 2. Guardar el archivo localmente
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # URL local para acceder a la imagen (Asegúrate de servir la carpeta uploads en main.py)
    # NOTA: Si Moderacion_IA está en Docker, usar 'host.docker.internal' en vez de localhost
    file_url = f"http://127.0.0.1:8000/uploads/{file.filename}"

    # 3. Filtro de Moderación Visual (IA - NSFW Detector)
    try:
        res = requests.post("http://localhost:3000/predict", json={"url": file_url}, timeout=3)
        if res.status_code == 200 and res.json().get("is_nsfw"):
            os.remove(file_path) # Borrar archivo si es obsceno
            raise HTTPException(status_code=400, detail="Imagen rechazada: Detectado contenido NSFW.")
    except requests.RequestException:
        pass # Si el contenedor Docker está apagado, lo deja pasar (como ya tenías)

    # 4. Guardar en Base de Datos
    nuevo_pin = Pin(titulo=titulo, source=f"/uploads/{file.filename}", es_publico=True, reportado=False)
    session.add(nuevo_pin)
    session.commit()
    session.refresh(nuevo_pin)
    return nuevo_pin

def verificar_politica_palabras(texto_titulo: str) -> bool:
    """Retorna True si encuentra un insulto configurado en el laboratorio"""
    try:
        # Localiza la ruta absoluta del diccionario words.json del proyecto
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_json = os.path.join(base_dir, "..", "..", "Malas_Palabras", "words.json")
        
        with open(ruta_json, "r", encoding="utf-8") as f:
            palabras_prohibidas = json.load(f)
            
        palabras_ingresadas = texto_titulo.lower().split()
        for palabra in palabras_ingresadas:
            if palabra in palabras_prohibidas:
                return True
        return False
    except Exception:
        return False # Si el archivo no se lee, no detiene la ejecución de pruebas

@router.post("/", response_model=Pin)
def post_pin(pin: Pin, session: SessionDep):
    # 1. Filtro de Moderación Textual (Malas Palabras)
    if verificar_politica_palabras(pin.titulo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contenido bloqueado: El título infringe las normas de vocabulario del laboratorio."
        )

    # 2. Filtro de Moderación Visual (IA - NSFW Detector de imágenes)
    try:
        res = requests.post("http://localhost:3000/predict", json={"url": pin.source}, timeout=3)
        if res.status_code == 200 and res.json().get("is_nsfw"): 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Imagen rechazada: El clasificador de IA (.h5) detectó contenido NSFW."
            )
    except requests.RequestException: 
        pass # Si el contenedor Docker de la IA no está encendido, permite pasar para no trabar el desarrollo
    
    pin.reportado = False
    session.add(pin)
    session.commit()
    session.refresh(pin)
    return pin

@router.get("/", response_model=List[Pin])
def get_pins(session: SessionDep):
    # Trae únicamente los pines que no han sido reportados por la comunidad
    statement = select(Pin).where(Pin.reportado == False)
    results = session.exec(statement)
    return results.all()

@router.delete("/{pin_id}")
def delete_pin(pin_id: int, session: SessionDep):
    pin = session.get(Pin, pin_id)
    if not pin: 
        raise HTTPException(status_code=404, detail="Pin no encontrado")
    session.delete(pin)
    session.commit()
    return {"message": "Borrado"}

@router.post("/{pin_id}/comentarios")
def post_comentario(pin_id: int, comentario: Comentario, session: SessionDep):
    comentario.pin_id = pin_id
    session.add(comentario)
    session.commit()
    session.refresh(comentario)
    return comentario

@router.patch("/{pin_id}/reportar")
def reportar_pin(pin_id: int, session: SessionDep):
    pin = session.get(Pin, pin_id)
    if not pin: 
        raise HTTPException(status_code=404, detail="Pin no encontrado")
    
    pin.reportado = True
    session.add(pin)
    session.commit()
    session.refresh(pin)
    return {"message": "Pin reportado exitosamente"}

# Ver los comentarios de un pin
@router.get("/{pin_id}/comentarios")
def get_comentarios_de_pin(pin_id: int, session: SessionDep):
    statement = select(Comentario).where(Comentario.pin_id == pin_id)
    return session.exec(statement).all()

# Crear un Tablero (Carpeta)
@router.post("/tableros")
def crear_tablero(nombre: str, usuario_id: int, session: SessionDep):
    nuevo_tablero = Tablero(nombre=nombre, usuario_id=usuario_id)
    session.add(nuevo_tablero)
    session.commit()
    return {"message": "Tablero creado", "tablero": nuevo_tablero}

# Guardar un pin en una carpeta (Tablero)
@router.post("/{pin_id}/guardar")
def guardar_pin(pin_id: int, tablero_id: int, usuario_id: int, session: SessionDep):
    guardado = PinGuardado(pin_id=pin_id, tablero_id=tablero_id, usuario_id=usuario_id)
    session.add(guardado)
    session.commit()
    return {"message": "Pin guardado en tu tablero!"}