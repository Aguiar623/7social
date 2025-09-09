import spacy
import unicodedata
import re
from pysentimiento import create_analyzer
from langdetect import detect

nlp = spacy.load("es_core_news_lg")
analyzer = create_analyzer(task="emotion", lang="es")


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
            raise ValueError(
                "La lista debe contener solo strings o diccionarios con content"
            )
    else:
        raise TypeError("La entrada debe ser string o lista")

    try:
        idioma = detect(texto_total)
        if idioma != "es":
            return None
    except:
        return None

    resultado = analyzer.predict(texto_total)
    return AnalisisWrapper(resultado.output, resultado.probas, texto_total)
