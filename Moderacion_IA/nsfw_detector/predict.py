import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

IMAGE_DIM = 224

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "nsfw_model.h5")

model = None

def load_nsfw_model():
    global model
    if model is None:
        if os.path.exists(MODEL_PATH):
            print(f"🔮 [IA Fyntasy] Cargando archivo de pesos neuronales: {MODEL_PATH}")
            model = load_model(MODEL_PATH, custom_objects={'KerasLayer': hub.KerasLayer}, compile=False)
        else:
            raise FileNotFoundError(f"❌ [IA ERROR] No se encontró el modelo: {MODEL_PATH}")
    return model

def predict_image(image_path):
    """Analiza la imagen forzando la impresión de resultados en la terminal."""
    print(f"🔎 [IA EXAMINANDO] Escaneando píxeles de: {image_path}")
    loaded_model = load_nsfw_model()
    
    # Eliminamos el fallback silencioso. Si hay error, que explote para verlo.
    img = image.load_img(image_path, target_size=(IMAGE_DIM, IMAGE_DIM))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0  

    preds = loaded_model.predict(x)
    
    categories = ["Drawings", "Hentai", "Neutral", "Porn", "Sexy"]
    results = []
    for i, prob in enumerate(preds[0]):
        results.append({"className": categories[i], "probability": float(prob)})
        
    # ESTO IMPRIMIRÁ EXACTAMENTE LO QUE LA IA PIENSA DE LA FOTO EN TU TERMINAL
    print(f"📊 [IA PREDICCIONES EXACTAS] {results}")
    return results