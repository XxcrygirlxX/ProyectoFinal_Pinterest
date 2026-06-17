import os
import json
import sys
import boto3  # Conector de AWS S3
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from typing import Optional

from db import get_session
from modelos import Pin, Comentario, Usuario, Reporte

router = APIRouter(prefix="/pins", tags=["Pines"])

AWS_ACCESS_KEY_ID = "AKIAVUX27GSLYZGV2TP5,2Amfi4+x8nfpjsmHg7ehrLsygwuPuq6d+0sftmXP"
AWS_SECRET_ACCESS_KEY = "AKIAVUX27GSLYZGV2TP5,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"
AWS_BUCKET_NAME = "multimediaintegrador"
AWS_REGION = "us-east-2"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORDS_JSON_PATH = os.path.join(BASE_DIR, "Malas_Palabras", "words.json")
MODERACION_DIR = os.path.join(BASE_DIR, "Moderacion_IA")

if MODERACION_DIR not in sys.path:
    sys.path.insert(0, MODERACION_DIR)

try:
    from nsfw_detector.predict import predict_image
    print(" [IA CENTRAL] Servidor enlazado con éxito a TensorFlow.")
except Exception as e:
    print(f" [AVISO CRÍTICO] La IA no pudo conectarse: {e}")
    def predict_image(path):
        raise Exception("Motor de Inteligencia Artificial apagado o desconectado.")

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
        print(f"Error procesando el filtro de vocabulario: {e}")
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
        raise HTTPException(status_code=404, detail="El Pin no está disponible.")
    return pin

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
        raise HTTPException(status_code=400, detail="Fyntasy alcanzó el límite ético: publicación bloqueada por lenguaje inapropiado.")

    cat_limpia = categoria.lower().strip()
    if cat_limpia not in ["paisajes", "entretenimiento", "chill"]:
        raise HTTPException(status_code=400, detail="Categoría inválida.")

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
                motivo = f"{cat_name} al {prob*100:.1f}%"
                break
                
        if bloqueado:
            raise HTTPException(status_code=400, detail=f"La IA de Fyntasy rechazó tu foto de forma automática por contenido detectado como {motivo}.")

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        s3_key = f"fyntasy-media/{nombre_seguro}"
        s3_client.upload_file(ruta_absoluta, AWS_BUCKET_NAME, s3_key)
        url_publica_aws = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        print(f"☁️ [AWS] Imagen enviada a S3: {url_publica_aws}")

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        print(f" [ERROR] Fallo en el procesamiento del archivo: {e}")
        raise HTTPException(status_code=500, detail="Error interno en el motor de seguridad o almacenamiento.")
    finally:
        if os.path.exists(ruta_absoluta):
            os.remove(ruta_absoluta)

    usuario = session.get(Usuario, usuario_id)
    username_autor = usuario.username if usuario else "Fyntasy_Girl"

    nuevo_pin = Pin(
        titulo=titulo, descripcion=descripcion, categoria=cat_limpia,
        source=url_publica_aws, usuario_id=usuario_id, username_autor=username_autor
    )
    session.add(nuevo_pin)
    session.commit()
    session.refresh(nuevo_pin)
    return {"message": "Publicado con éxito", "pin": nuevo_pin}

@router.get("/{pin_id}/comments")
def listar_comentarios(pin_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Comentario).where(Comentario.pin_id == pin_id)).all()

@router.post("/{pin_id}/comments")
def agregar_comentario(
    pin_id: int, texto: str = Form(...), usuario_id: int = Form(...),
    username_autor: str = Form(...), session: Session = Depends(get_session)
):
    if verificar_texto_ofensivo(texto):
        raise HTTPException(status_code=400, detail="Tu comentario fue rechazado por palabras obscenas.")
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
        return {"message": "Ya has reportado este pin previamente. Está bajo auditoría de Fyntasy."}

    nuevo_reporte = Reporte(pin_id=pin_id, usuario_id=usuario_id)
    session.add(nuevo_reporte)
    session.commit()

    total_reportes = len(session.exec(select(Reporte).where(Reporte.pin_id == pin_id)).all())

    if total_reportes >= 3:
        pin.reportado = True
        session.add(pin)
        session.commit()
        return {"message": "El pin ha alcanzado 3 reportes de usuarios distintos y ha sido eliminado de la plataforma."}
    
    return {"message": f"Reporte registrado con éxito. El pin lleva {total_reportes}/3 reportes para ser eliminado."}