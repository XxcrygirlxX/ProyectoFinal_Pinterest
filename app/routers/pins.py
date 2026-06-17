import os
import json
import sys
import boto3
from dotenv import load_dotenv 
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from typing import Optional

from db import get_session
from modelos import Pin, Comentario, Usuario, Reporte

load_dotenv() 

router = APIRouter(prefix="/pins", tags=["Pines"])

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = "multimediaintegrador"
AWS_REGION = "us-east-2"

MAPEO_CARPETAS = {
    "chill": "Categoria1",
    "entrenamiento": "Categoria2",
    "paisajes": "Categoria3"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORDS_JSON_PATH = os.path.join(BASE_DIR, "Malas_Palabras", "words.json")
MODERACION_DIR = os.path.join(BASE_DIR, "Moderacion_IA")

if MODERACION_DIR not in sys.path:
    sys.path.insert(0, MODERACION_DIR)

try:
    from nsfw_detector.predict import predict_image
    print("[INFO] Módulo TensorFlow cargado exitosamente.")
except Exception as e:
    print(f"[CRITICAL] Error al inicializar TensorFlow: {e}")
    def predict_image(path):
        raise Exception("Motor de IA fuera de línea.")

def verificar_texto_ofensivo(texto: str) -> bool:
    if not texto or not os.path.exists(WORDS_JSON_PATH):
        return False
    try:
        with open(WORDS_JSON_PATH, "r", encoding="utf-8") as f:
            datos = json.load(f)
            palabras_prohibidas = datos if isinstance(datos, list) else datos.get("words", [])
            texto_limpio = texto.lower().strip()
            for palabra in palabras_prohibidas:
                if palabra.lower().strip() in texto_limpio:
                    return True
    except Exception as e:
        print(f"[ERROR] Filtro de vocabulario fallido: {e}")
        return False
    return False

@router.get("")
def listar_pines(categoria: Optional[str] = None, session: Session = Depends(get_session)):
    query = select(Pin).where(Pin.reportado == False)
    if categoria and categoria.lower().strip() != "todas":
        query = query.where(Pin.categoria == categoria.lower().strip())
    return session.exec(query).all()

@router.get("/{pin_id}")
def obtener_pin(pin_id: int, session: Session = Depends(get_session)):
    pin = session.get(Pin, pin_id)
    if not pin or pin.reportado:
        raise HTTPException(status_code=404, detail="El pin solicitado no está disponible.")
    return pin

@router.put("/{pin_id}")
def editar_pin(pin_id: int, session: Session = Depends(get_session), titulo: Optional[str] = Form(None), descripcion: Optional[str] = Form(None)):
    pin = session.get(Pin, pin_id)
    if not pin:
        raise HTTPException(status_code=404, detail="Pin no encontrado.")
    if titulo:
        if verificar_texto_ofensivo(titulo):
            raise HTTPException(status_code=400, detail="Título rechazado por contener vocabulario restringido.")
        pin.titulo = titulo
    if descripcion:
        if verificar_texto_ofensivo(descripcion):
            raise HTTPException(status_code=400, detail="Descripción rechazada por contener vocabulario restringido.")
        pin.descripcion = descripcion
    session.add(pin)
    session.commit()
    session.refresh(pin)
    return {"message": "Pin actualizado exitosamente", "pin": pin}

@router.delete("/{pin_id}")
def eliminar_pin(pin_id: int, session: Session = Depends(get_session)):
    pin = session.get(Pin, pin_id)
    if not pin:
        raise HTTPException(status_code=404, detail="Pin no encontrado.")
    session.delete(pin)
    session.commit()
    return {"message": "Pin eliminado exitosamente"}

@router.post("/upload")
async def subir_pin(
    titulo: str = Form(...),
    descripcion: str = Form(...),
    categoria: str = Form(...), 
    usuario_id: int = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    if verificar_texto_ofensivo(titulo) or verificar_texto_ofensivo(descripcion):
        raise HTTPException(status_code=400, detail="Contenido bloqueado por infracción de políticas de vocabulario.")

    cat_limpia = categoria.lower().strip()
    if cat_limpia not in MAPEO_CARPETAS:
        raise HTTPException(status_code=400, detail="Categoría no válida.")

    os.makedirs("uploads", exist_ok=True)
    nombre_seguro = f"user_{usuario_id}_{file.filename.replace(' ', '_')}"
    ruta_archivo = os.path.join("uploads", nombre_seguro)
    ruta_absoluta = os.path.abspath(ruta_archivo)

    try:
        with open(ruta_absoluta, "wb") as f:
            contenido = await file.read()
            f.write(contenido)

        res_ia = predict_image(ruta_absoluta)
        predicciones = res_ia.get(ruta_absoluta, res_ia) if isinstance(res_ia, dict) else res_ia
        
        bloqueado = False
        motivo = ""
        lista_preds = predicciones if isinstance(predicciones, list) else [{"className": k, "probability": v} for k, v in predicciones.items()]
        
        for p in lista_preds:
            cat_name = p.get("className")
            prob = p.get("probability", 0)
            if cat_name in ["Porn", "Hentai", "Sexy"] and prob > 0.15:
                bloqueado = True
                motivo = f"{cat_name} ({prob*100:.1f}%)"
                break
                
        if bloqueado:
            raise HTTPException(status_code=400, detail=f"Imagen rechazada por el clasificador automático: {motivo}")

        subcarpeta_real = MAPEO_CARPETAS[cat_limpia]

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        s3_key = f"{subcarpeta_real}/{nombre_seguro}"
        s3_client.upload_file(ruta_absoluta, AWS_BUCKET_NAME, s3_key)
        url_publica_aws = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        print(f"[SUCCESS] Archivo transferido a S3 en carpeta '{subcarpeta_real}': {url_publica_aws}")

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        print(f"[ERROR] Fallo en el pipeline de almacenamiento: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor en el procesamiento de medios.")
    finally:
        if os.path.exists(ruta_absoluta):
            os.remove(ruta_absoluta)

    usuario = session.get(Usuario, usuario_id)
    username_autor = usuario.username if usuario else "Fyntasy_User"

    nuevo_pin = Pin(
        titulo=titulo, descripcion=descripcion, categoria=cat_limpia,
        source=url_publica_aws, usuario_id=usuario_id, username_autor=username_autor
    )
    session.add(nuevo_pin)
    session.commit()
    session.refresh(nuevo_pin)
    return {"message": "Publicación exitosa", "pin": nuevo_pin}

@router.get("/{pin_id}/comments")
def listar_comentarios(pin_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Comentario).where(Comentario.pin_id == pin_id)).all()

@router.post("/{pin_id}/comments")
def agregar_comentario(
    pin_id: int, texto: str = Form(...), usuario_id: int = Form(...),
    username_autor: str = Form(...), session: Session = Depends(get_session)
):
    if verificar_texto_ofensivo(texto):
        raise HTTPException(status_code=400, detail="Comentario rechazado por contener vocabulario restringido.")
    nuevo_c = Comentario(texto=texto, pin_id=pin_id, usuario_id=usuario_id, username_autor=username_autor)
    session.add(nuevo_c)
    session.commit()
    session.refresh(nuevo_c)
    return {"message": "Comentario aprobado", "comentario": nuevo_c}

@router.get("/user/{usuario_id}")
def obtener_pines_usuario(usuario_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Pin).where(Pin.usuario_id == usuario_id)).all()

@router.post("/{pin_id}/report")
def reportar_pin(pin_id: int, usuario_id: int = Form(...), session: Session = Depends(get_session)):
    pin = session.get(Pin, pin_id)
    if not pin: raise HTTPException(status_code=404, detail="Pin no encontrado.")

    reporte_existente = session.exec(select(Reporte).where(Reporte.pin_id == pin_id, Reporte.usuario_id == usuario_id)).first()
    if reporte_existente:
        return {"message": "Reporte previamente registrado para este pin. Bajo revisión administrativa."}

    nuevo_reporte = Reporte(pin_id=pin_id, usuario_id=usuario_id)
    session.add(nuevo_reporte)
    session.commit()

    total_reportes = len(session.exec(select(Reporte).where(Reporte.pin_id == pin_id)).all())

    if total_reportes >= 3:
        pin.reportado = True
        session.add(pin)
        session.commit()
        return {"message": "El pin alcanzó el umbral de 3 reportes comunitarios y fue retirado automáticamente."}
    
    return {"message": f"Reporte registrado. Estado actual: {total_reportes}/3 reportes para remoción."}