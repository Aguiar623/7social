import spacy
import unicodedata
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Cargar SpaCy
nlp = spacy.load("es_core_news_lg")

# Cargar modelo y tokenizer de Hugging Face
MODEL_NAME = "pysentimiento/robertuito-emotion-analysis"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Clases de emociones del modelo
labels = ["joy", "sadness", "anger", "surprise", "disgust", "fear", "others"]

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

    # Tokenizar texto
    inputs = tokenizer(texto_total, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)

    # Calcular probabilidades
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
    max_idx = torch.argmax(probs).item()
    output = labels[max_idx]
    probas = {labels[i]: float(probs[i]) for i in range(len(labels))}

    return AnalisisWrapper(output, probas, texto_total)

