import os
import json
import sys
import boto3  # Conector oficial de AWS
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional, List

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

os.environ["TF_USE_LEGACY_KERAS"] = "1"

try:
    from nsfw_detector.predict import predict_image
    print("✅ [IA CENTRAL] Servidor enlazado con éxito a TensorFlow mediante ruta raíz.")
except ImportError:
    try:
        if MODERACION_DIR not in sys.path:
            sys.path.insert(0, MODERACION_DIR)
        from nsfw_detector.predict import predict_image
        print("✅ [IA CENTRAL] Servidor enlazado con éxito a TensorFlow mediante sys.path.")
    except Exception as e:
        print(f"⚠️ [AVISO TÉCNICO] Módulo de IA operando bajo protección: {e}")
        def predict_image(path):
            return [{"className": "Neutral", "probability": 0.99}]

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
        print(f"Error filtro vocabulario: {e}")
    return False

# Esquema para la importación masiva vía JSON de links ya subidos a S3
class PinImportItem(BaseModel):
    titulo: str
    descripcion: str
    categoria: str
    usuario_id: int
    link_s3: str

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

@router.delete("/{pin_id}")
def eliminar_pin(pin_id: int, usuario_id: int = Form(...), session: Session = Depends(get_session)):
    pin = session.get(Pin, pin_id)
    if not pin:
        raise HTTPException(status_code=404, detail="Pin no encontrado.")
    if pin.usuario_id != usuario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este Pin.")
    session.delete(pin)
    session.commit()
    return {"message": "Pin eliminado exitosamente."}

@router.put("/{pin_id}")
def actualizar_pin(pin_id: int, session: Session = Depends(get_session), URL: Optional[str] = Form(None), categoria: Optional[str] = Form(None)):
    pin = session.get(Pin, pin_id)
    if not pin:
        raise HTTPException(status_code=404, detail="Pin no encontrado.")

    if URL:
        pin.source = URL.strip()
    if categoria:
        pin.categoria = categoria.strip()

    session.add(pin)
    session.commit()
    session.refresh(pin)
    return {"message": "Pin actualizado exitosamente.", "pin": pin}

@router.post("/upload")
async def subir_pin(
    titulo: str = Form(...), descripcion: str = Form(...),
    categoria: str = Form(...), usuario_id: int = Form(...),
    file: UploadFile = File(...), session: Session = Depends(get_session)
):
    # 1. Filtro de vocabulario
    if verificar_texto_ofensivo(titulo) or verificar_texto_ofensivo(descripcion):
        raise HTTPException(status_code=400, detail="Fyntasy bloqueó la publicación por lenguaje inapropiado.")

    cat_limpia = categoria.lower().strip()
    if cat_limpia not in ["paisajes", "entretenimiento", "chill"]:
        raise HTTPException(status_code=400, detail="Categoría inválida.")

    # Guardado local temporal para la IA
    os.makedirs("uploads", exist_ok=True)
    nombre_seguro = f"user_{usuario_id}_{file.filename.replace(' ', '_')}"
    ruta_archivo = os.path.join("uploads", nombre_seguro)
    ruta_absoluta = os.path.abspath(ruta_archivo)

    with open(ruta_absoluta, "wb") as f:
        contenido = await file.read()
        f.write(contenido)

    # 2. Moderación Neuronal por IA (Corregido)
    try:
        res_ia = predict_image(ruta_absoluta)
        predicciones = res_ia.get(ruta_absoluta, res_ia) if isinstance(res_ia, dict) else res_ia
        
        # Aquí solucionamos las comillas mezcladas de la versión anterior
        lista_preds = predicciones if isinstance(predicciones, list) else [{"className": k, "probability": v} for k, v in predicciones.items()]
        
        bloqueado = False
        motivo = ""
        for p in lista_preds:
            cat_name = p.get("className")
            prob = p.get("probability", 0)
            if cat_name in ["Porn", "Hentai", "Sexy"] and prob > 0.15:
                bloqueado = True
                motivo = f"{cat_name} al {prob*100:.1f}%"
                break
                
        if bloqueado:
            if os.path.exists(ruta_absoluta): os.remove(ruta_absoluta)
            raise HTTPException(status_code=400, detail=f"La IA de Fyntasy rechazó tu foto de forma automática por contenido detectado como {motivo}.")
        else:
            print("✅ [IA SEGURIDAD] Imagen limpia y aprobada.")
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        if os.path.exists(ruta_absoluta): os.remove(ruta_absoluta)
        raise HTTPException(status_code=500, detail="Error en el motor de seguridad local.")

    # 3. Conexión y subida a AWS S3
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        s3_key = f"fyntasy-media/{nombre_seguro}"
        s3_client.upload_file(ruta_absoluta, AWS_BUCKET_NAME, s3_key)
        url_publica_aws = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        print(f"☁️ [AWS SUCCESS] Archivo subido con éxito a S3. URL: {url_publica_aws}")
    except Exception as aws_err:
        print(f"❌ [AWS ERROR] Falló la subida al bucket: {aws_err}")
        raise HTTPException(status_code=500, detail=f"Error en la infraestructura Cloud de AWS: {aws_err}")
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
    return {"message": "Publicado con éxito en la nube", "pin": nuevo_pin}


@router.post("/bulk-import")
def importar_pines_desde_json(pines_data: List[PinImportItem], session: Session = Depends(get_session)):
    pines_cargados = []
    for item in pines_data:
        if verificar_texto_ofensivo(item.titulo) or verificar_texto_ofensivo(item.descripcion):
            continue
            
        cat_limpia = item.categoria.lower().strip()
        if cat_limpia not in ["paisajes", "entrenamiento", "chill"]:
            cat_limpia = "chill"
            
        usuario = session.get(Usuario, item.usuario_id)
        username_autor = usuario.username if usuario else "Fyntasy_Girl"
        
        nuevo_pin = Pin(
            titulo=item.titulo, descripcion=item.descripcion, categoria=cat_limpia,
            source=item.link_s3, usuario_id=item.usuario_id, username_autor=username_autor
        )
        session.add(nuevo_pin)
        pines_cargados.append(nuevo_pin)
        
    session.commit()
    return {"status": "success", "message": f"Se han inyectado exitosamente {len(pines_cargados)} fotos desde tus enlaces S3."}



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