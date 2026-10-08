"""
Script para poblar la base de datos con usuarios y textos iniciales.
Ejecuta: python -m app.seed
"""
from app.db.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.text import Text
from app.models.quiz import Quiz
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Verificar si ya hay datos
if db.query(User).count() > 0:
    print("⚠️  La base de datos ya tiene datos. Omitiendo seed.")
else:
    # ============================
    # Usuarios
    # ============================
    users = [
        User(username="estudiante", hashed_password=hash_password("123456"),
             full_name="Juan Pérez", role="estudiante", email="juan@test.com"),
        User(username="docente", hashed_password=hash_password("123456"),
             full_name="Prof. María López", role="docente", email="maria@test.com"),
        User(username="padre", hashed_password=hash_password("123456"),
             full_name="Sr. Carlos Pérez", role="padre", email="carlos@test.com"),
        User(username="admin", hashed_password=hash_password("123456"),
             full_name="Administrador", role="administrador", email="admin@test.com"),
    ]
    db.add_all(users)
    db.commit()

    # ============================
    # Textos (uno por cada nivel)
    # ============================
    texts_data = [
        {
            "title": "El Gato y el Ratón",
            "content": "Un gato dormía tranquilamente junto a un agujero. Un ratón pequeño salió a buscar comida. El gato abrió un ojo y esperó. El ratón, muy rápido, tomó el queso y volvió a su casa. El gato se quedó con hambre.",
            "level": "En Inicio",
            "genre": "fábula"
        },
        {
            "title": "El Zorro y el Cuervo",
            "content": "Un zorro muy astuto vio a un cuervo posado en una rama con un pedazo de queso en el pico. El zorro, hambriento, decidió usar su ingenio para conseguir el queso. Se acercó lentamente y comenzó a halagar al cuervo: '¡Qué plumaje tan hermoso tienes! Sin duda tu voz debe ser tan bella como tu apariencia'. El cuervo, halagado, abrió el pico para cantar, y el queso cayó directamente a la boca del zorro, que se lo llevó sin perder tiempo.",
            "level": "En Proceso",
            "genre": "fábula"
        },
        {
            "title": "La Tortuga y la Liebre",
            "content": "En un bosque frondoso, una liebre presumida se burlaba constantemente de la lentitud de una tortuga. Cansada de las burlas, la tortuga le propuso una carrera. La liebre, confiada en su velocidad, aceptó de inmediato y comenzó a correr velozmente, dejando muy atrás a su contrincante. Al verse tan distanciada, decidió tomar una siesta bajo un árbol, pensando que tendría tiempo de sobra para ganar. Mientras tanto, la tortuga avanzaba con paso firme y constante, sin detenerse jamás. Cuando la liebre despertó, vio con asombro que la tortuga ya estaba cruzando la meta. La moraleja es clara: la perseverancia vence al talento cuando el talento no se esfuerza.",
            "level": "Satisfactorio",
            "genre": "fábula"
        },
    ]

    for td in texts_data:
        text = Text(**td)
        db.add(text)
        db.commit()

        # ============================
        # Preguntas por texto
        # ============================
        if text.level == "En Inicio":
            quiz_items = [
                Quiz(text_id=text.id, question="¿Quién dormía junto al agujero?",
                     option_a="El ratón", option_b="El gato", option_c="El perro", option_d="El pájaro",
                     correct_answer=1, question_type="literal"),
                Quiz(text_id=text.id, question="¿Qué buscaba el ratón?",
                     option_a="Jugar", option_b="Comida", option_c="Dormir", option_d="Correr",
                     correct_answer=1, question_type="literal"),
                Quiz(text_id=text.id, question="¿Cómo se quedó el gato al final?",
                     option_a="Feliz", option_b="Con hambre", option_c="Dormido", option_d="Cansado",
                     correct_answer=1, question_type="inferencial"),
            ]
        elif text.level == "En Proceso":
            quiz_items = [
                Quiz(text_id=text.id, question="¿Qué animal tenía el queso?",
                     option_a="El zorro", option_b="El cuervo", option_c="El perro", option_d="El gato",
                     correct_answer=1, question_type="literal"),
                Quiz(text_id=text.id, question="¿Qué quería el zorro?",
                     option_a="Dormir", option_b="El queso", option_c="Volar", option_d="Cantar",
                     correct_answer=1, question_type="literal"),
                Quiz(text_id=text.id, question="¿Cómo era el zorro?",
                     option_a="Tonto", option_b="Astuto", option_c="Perezoso", option_d="Tímido",
                     correct_answer=1, question_type="inferencial"),
                Quiz(text_id=text.id, question="¿Por qué el cuervo abrió el pico?",
                     option_a="Por hambre", option_b="Porque fue halagado", option_c="Por miedo", option_d="Por sueño",
                     correct_answer=1, question_type="inferencial"),
            ]
        else:  # Satisfactorio
            quiz_items = [
                Quiz(text_id=text.id, question="¿Quién se burlaba de la tortuga?",
                     option_a="El zorro", option_b="La liebre", option_c="El cuervo", option_d="El gato",
                     correct_answer=1, question_type="literal"),
                Quiz(text_id=text.id, question="¿Qué hizo la liebre durante la carrera?",
                     option_a="Corrió sin parar", option_b="Tomó una siesta", option_c="Se rindió", option_d="Se perdió",
                     correct_answer=1, question_type="literal"),
                Quiz(text_id=text.id, question="¿Cuál es la moraleja de la historia?",
                     option_a="El más rápido siempre gana",
                     option_b="La perseverancia vence al talento",
                     option_c="Dormir es bueno",
                     option_d="Las tortugas son lentas",
                     correct_answer=1, question_type="critica"),
                Quiz(text_id=text.id, question="¿Qué característica describe mejor a la tortuga?",
                     option_a="Perezosa", option_b="Constante", option_c="Presumida", option_d="Distraída",
                     correct_answer=1, question_type="inferencial"),
            ]

        db.add_all(quiz_items)
        db.commit()

    print("✅ Datos iniciales creados correctamente.")
    print("")
    print("📋 Usuarios creados (contraseña: 123456):")
    print("   - estudiante  → Juan Pérez")
    print("   - docente     → Prof. María López")
    print("   - padre       → Sr. Carlos Pérez")
    print("   - admin       → Administrador")
    print("")
    print("📚 Textos creados: 3 (uno por cada nivel)")
    print("   - En Inicio: El Gato y el Ratón")
    print("   - En Proceso: El Zorro y el Cuervo")
    print("   - Satisfactorio: La Tortuga y la Liebre")

db.close()