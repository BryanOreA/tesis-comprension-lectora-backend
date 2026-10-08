import spacy
from typing import List

try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    nlp = None
    print("⚠️ Modelo de spaCy no encontrado. Ejecuta: python -m spacy download es_core_news_sm")


# Diccionario simple de sinónimos para simplificación
SYNONYMS = {
    "astuto": "listo",
    "posado": "parado",
    "halagar": "adular",
    "plumaje": "plumas",
    "ingenio": "inteligencia",
    "apariencia": "aspecto",
    "inmediatamente": "al instante",
    "presumida": "creída",
    "constantemente": "todo el tiempo",
    "frondoso": "con muchos árboles",
    "distanciada": "lejos",
    "contrincante": "rival",
    "perseverancia": "constancia",
    "velozmente": "rápidamente",
    "asombro": "sorpresa",
}


def simplify_text(text: str, target_level: str = "En Inicio") -> str:
    """
    Simplifica un texto según el nivel objetivo.
    - En Inicio: divide oraciones largas + reemplaza sinónimos
    - En Proceso: solo reemplaza sinónimos
    - Satisfactorio: devuelve el texto original
    """
    if target_level == "Satisfactorio" or not nlp:
        return text

    doc = nlp(text)
    sentences = []

    for sent in doc.sents:
        simplified = sent.text
        # Reemplazar sinónimos
        for complex_word, simple_word in SYNONYMS.items():
            simplified = simplified.replace(complex_word, simple_word)

        # Si es nivel "En Inicio", dividir oraciones largas
        if target_level == "En Inicio" and len(simplified.split()) > 15:
            parts = simplified.split(", ")
            if len(parts) > 1:
                simplified = ". ".join(parts)

        sentences.append(simplified.strip())

    return " ".join(sentences)


def calculate_readability(text: str) -> dict:
    """
    Calcula métricas básicas de legibilidad.
    """
    if not nlp:
        words = text.split()
        return {
            "word_count": len(words),
            "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 1),
            "sentence_count": text.count(".") + text.count("!") + text.count("?"),
            "avg_sentence_length": 0,
        }

    doc = nlp(text)
    words = [token.text for token in doc if not token.is_punct and not token.is_space]
    sentences = list(doc.sents)

    return {
        "word_count": len(words),
        "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 1),
        "sentence_count": len(sentences),
        "avg_sentence_length": round(len(words) / max(len(sentences), 1), 1),
    }