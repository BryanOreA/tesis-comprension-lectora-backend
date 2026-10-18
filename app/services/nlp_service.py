import spacy

try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    nlp = None
    print("⚠️ Modelo de spaCy no encontrado.")

# Diccionario ampliado (puedes seguir agregando aquí)
SYNONYMS = {
    "astuto": "listo", "posado": "parado", "halagar": "adular",
    "plumaje": "plumas", "ingenio": "inteligencia", "apariencia": "aspecto",
    "inmediatamente": "al instante", "presumida": "creída",
    "constantemente": "todo el tiempo", "frondoso": "con muchos árboles",
    "distanciada": "lejos", "contrincante": "rival", "perseverancia": "constancia",
    "velozmente": "rápidamente", "asombro": "sorpresa", "esmero": "cuidado",
    "vanidosa": "creída", "caprichos": "gustos", "extraños": "raros",
    "súbditos": "ayudantes", "farolero": "el de la luz", "domestica": "cuida",
    "esencial": "importante", "invisible": "que no se ve"
}

def simplify_text(text: str, target_level: str = "En Inicio") -> str:
    if target_level == "Satisfactorio" or not nlp:
        return text

    doc = nlp(text)
    simplified_sentences = []

    for sent in doc.sents:
        # 1. Simplificación léxica (reemplazo de palabras)
        sentence_text = sent.text
        for complex_word, simple_word in SYNONYMS.items():
            sentence_text = sentence_text.replace(complex_word, simple_word)

        # 2. División inteligente de oraciones (Dependency Parsing)
        # Si el nivel es "En Inicio" y la oración es larga (> 12 palabras)
        if target_level == "En Inicio" and len(sentence_text.split()) > 12:
            
            # Buscar conjunciones coordinantes (y, o, pero) o subordinantes (porque, aunque)
            # que separan ideas en la gramática.
            split_points = []
            for token in sent:
                if token.dep_ in ("cc", "mark") and token.i > sent.start and token.i < sent.end - 1:
                    split_points.append(token.i)

            if split_points:
                # Si encontramos un punto de corte, partimos la oración ahí
                current_start = sent.start
                for split_idx in split_points:
                    part = doc[current_start:split_idx].text.strip()
                    if len(part) > 3: # Evitar cortes muy pequeños
                        simplified_sentences.append(part.capitalize() + ".")
                    current_start = split_idx + 1
                
                # Agregar el resto de la oración
                rest = doc[current_start:sent.end].text.strip()
                if len(rest) > 3:
                    simplified_sentences.append(rest.capitalize() + ".")
            else:
                # Si no hay conjunciones, dividir por comas o puntos y comas
                parts = sentence_text.replace(";", ",").split(", ")
                if len(parts) > 1:
                    for p in parts:
                        if len(p) > 3:
                            simplified_sentences.append(p.strip().capitalize() + ".")
                else:
                    simplified_sentences.append(sentence_text)
        else:
            simplified_sentences.append(sentence_text)

    return " ".join(simplified_sentences)

def calculate_readability(text: str) -> dict:
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