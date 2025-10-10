import unicodedata
import re
from transformers import pipeline

# --- modelo de emociones Hugging Face ---
analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

class AnalisisWrapper:
    def __init__(self, output, probas, texto_total):
        self.output = output
        self.probas = probas
        self.texto_total = texto_total

def normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = texto.lower()
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def analizar_emocion(posts):
    if isinstance(posts, str):
        texto_total = normalizar_texto(posts)
    elif isinstance(posts, list):
        if all(isinstance(p, dict) and "content" in p for p in posts):
            texto_total = " ".join(normalizar_texto(p["content"]) for p in posts)
        elif all(isinstance(p, str) for p in posts):
            texto_total = " ".join(normalizar_texto(p) for p in posts)
        else:
            raise ValueError("La lista debe contener solo strings o diccionarios con 'content'")
    else:
        raise TypeError("La entrada debe ser string o lista")

    resultado = analyzer(texto_total)[0]
    emocion_principal = max(resultado, key=lambda x: x["score"])["label"]
    probabilidades = {r["label"]: r["score"] for r in resultado}

    return AnalisisWrapper(emocion_principal, probabilidades, texto_total)
