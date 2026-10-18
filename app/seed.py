"""
Script para poblar la base de datos con datos de prueba realistas.
Ejecuta: python -m app.seed
"""
import random
from datetime import datetime, timedelta
from app.db.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.text import Text
from app.models.quiz import Quiz
from app.models.progress import Progress
from app.core.security import hash_password

random.seed(42)
Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(User).count() > 0:
    print("⚠️  La base de datos ya tiene datos. Omitiendo seed.")
    db.close()
    exit(0)

# ============================
# 1. CREAR PADRES (Primero para obtener sus IDs)
# ============================
print("👨‍👩‍👧 Creando padres...")
parents_data = [
    {"username": "padre", "full_name": "Sr. Carlos Pérez", "email": "carlos.perez@gmail.com"},
    {"username": "padre2", "full_name": "Sra. Rosa García", "email": "rosa.garcia@gmail.com"},
    {"username": "padre3", "full_name": "Sr. Luis Torres", "email": "luis.torres@gmail.com"},
    {"username": "padre4", "full_name": "Sra. Elena Mendoza", "email": "elena.mendoza@gmail.com"},
]

parents = []
for p in parents_data:
    user = User(
        username=p["username"],
        hashed_password=hash_password("123456"),
        full_name=p["full_name"],
        email=p["email"],
        role="padre",
        is_active=True
    )
    db.add(user)
    parents.append(user)

db.commit()
# Ahora los padres tienen IDs asignados (ej. 1, 2, 3, 4)

# ============================
# 2. CREAR DOCENTES, ADMIN Y ESTUDIANTES
# ============================
print("👥 Creando docentes, admin y estudiantes...")

# Admin
db.add(User(username="admin", hashed_password=hash_password("123456"), full_name="Administrador del Sistema", email="admin@lectura.pe", role="administrador"))

# Docentes
db.add(User(username="docente", hashed_password=hash_password("123456"), full_name="Prof. María López", email="maria.lopez@lectura.pe", role="docente"))
db.add(User(username="docente2", hashed_password=hash_password("123456"), full_name="Prof. Carlos Ramos", email="carlos.ramos@lectura.pe", role="docente"))
db.add(User(username="docente3", hashed_password=hash_password("123456"), full_name="Prof. Ana Vargas", email="ana.vargas@lectura.pe", role="docente"))

# Estudiantes (Asignando un padre a los primeros 4)
students_data = [
    {"username": "estudiante", "full_name": "Juan Pérez García", "email": "juan.perez@estudiante.pe", "parent": parents[0]},
    {"username": "est_maria", "full_name": "María Rodríguez", "email": "maria.rodriguez@estudiante.pe", "parent": parents[1]},
    {"username": "est_luis", "full_name": "Luis Torres Mendoza", "email": "luis.torres@estudiante.pe", "parent": parents[2]},
    {"username": "est_ana", "full_name": "Ana Ramírez Silva", "email": "ana.ramirez@estudiante.pe", "parent": parents[3]},
    {"username": "est_carlos", "full_name": "Carlos Mendoza Ruiz", "email": "carlos.mendoza@estudiante.pe", "parent": None},
    {"username": "est_sofia", "full_name": "Sofía Rojas Vega", "email": "sofia.rojas@estudiante.pe", "parent": None},
    {"username": "est_diego", "full_name": "Diego Castro León", "email": "diego.castro@estudiante.pe", "parent": None},
    {"username": "est_valeria", "full_name": "Valeria Sánchez Luna", "email": "valeria.sanchez@estudiante.pe", "parent": None},
    {"username": "est_mateo", "full_name": "Mateo Fernández Ríos", "email": "mateo.fernandez@estudiante.pe", "parent": None},
    {"username": "est_camila", "full_name": "Camila Ortiz Delgado", "email": "camila.ortiz@estudiante.pe", "parent": None},
]

for s in students_data:
    user = User(
        username=s["username"],
        hashed_password=hash_password("123456"),
        full_name=s["full_name"],
        email=s["email"],
        role="estudiante",
        is_active=True,
        parent_id=s["parent"].id if s["parent"] else None
    )
    db.add(user)

db.commit()
print(f"   ✅ Usuarios creados")

# ============================
# 3. TEXTOS Y PREGUNTAS (Mismo código anterior)
# ============================
print("📚 Creando textos...")
texts_data = [
    {
        "title": "El Gato y el Ratón",
        "content": "Un gato dormía junto a un agujero. Un ratón salió a buscar comida. El gato abrió un ojo y esperó. El ratón tomó el queso y volvió a su casa. El gato se quedó con hambre.",
        "level": "En Inicio", "genre": "Fábula",
        "questions": [
            {"q": "¿Quién dormía junto al agujero?", "opts": ["El ratón", "El gato", "El perro", "El pájaro"], "a": 1, "type": "literal"},
            {"q": "¿Qué buscaba el ratón?", "opts": ["Jugar", "Comida", "Dormir", "Correr"], "a": 1, "type": "literal"},
            {"q": "¿Cómo se quedó el gato al final?", "opts": ["Feliz", "Con hambre", "Dormido", "Cansado"], "a": 1, "type": "inferencial"},
        ]
    },
    {
        "title": "La Hormiga Trabajadora",
        "content": "Una hormiga pequeña trabajaba todo el día. Guardaba comida para el invierno. Sus amigas solo jugaban. Cuando llegó el frío, la hormiga tenía mucha comida. Sus amigas no tenían nada. La hormiga compartió con ellas.",
        "level": "En Inicio", "genre": "Fábula",
        "questions": [
            {"q": "¿Qué hacía la hormiga todo el día?", "opts": ["Jugar", "Dormir", "Trabajar", "Cantar"], "a": 2, "type": "literal"},
            {"q": "¿Para qué guardaba comida?", "opts": ["Para vender", "Para el invierno", "Para regalar", "Para tirar"], "a": 1, "type": "literal"},
            {"q": "¿Cómo era la hormiga?", "opts": ["Egoísta", "Generosa", "Perezosa", "Triste"], "a": 1, "type": "inferencial"},
        ]
    },
    {
        "title": "Los Tres Cerditos",
        "content": "Tres cerditos construyeron sus casas. El primero hizo una de paja. El segundo, de madera. El tercero, de ladrillos. Un lobo sopló y derribó las dos primeras. La casa de ladrillos resistió. Los tres cerditos vivieron juntos y seguros.",
        "level": "En Inicio", "genre": "Cuento clásico",
        "questions": [
            {"q": "¿De qué hizo su casa el primer cerdito?", "opts": ["Ladrillos", "Madera", "Paja", "Piedra"], "a": 2, "type": "literal"},
            {"q": "¿Cuál casa resistió al lobo?", "opts": ["La de paja", "La de madera", "La de ladrillos", "Ninguna"], "a": 2, "type": "literal"},
            {"q": "¿Qué nos enseña el cuento?", "opts": ["Ser rápido", "Ser trabajador", "Ser perezoso", "Ser egoísta"], "a": 1, "type": "critica"},
        ]
    },
    {
        "title": "El Zorro y el Cuervo",
        "content": "Un zorro muy astuto vio a un cuervo posado en una rama con un pedazo de queso en el pico. El zorro, hambriento, decidió usar su ingenio para conseguir el queso. Se acercó lentamente y comenzó a halagar al cuervo: '¡Qué plumaje tan hermoso tienes! Sin duda tu voz debe ser tan bella como tu apariencia'. El cuervo, halagado, abrió el pico para cantar, y el queso cayó directamente a la boca del zorro.",
        "level": "En Proceso", "genre": "Fábula",
        "questions": [
            {"q": "¿Qué animal tenía el queso?", "opts": ["El zorro", "El cuervo", "El perro", "El gato"], "a": 1, "type": "literal"},
            {"q": "¿Qué quería el zorro?", "opts": ["Dormir", "El queso", "Volar", "Cantar"], "a": 1, "type": "literal"},
            {"q": "¿Cómo era el zorro?", "opts": ["Tonto", "Astuto", "Perezoso", "Tímido"], "a": 1, "type": "inferencial"},
            {"q": "¿Por qué el cuervo abrió el pico?", "opts": ["Por hambre", "Porque fue halagado", "Por miedo", "Por sueño"], "a": 1, "type": "inferencial"},
        ]
    },
    {
        "title": "El León y el Ratón",
        "content": "Un león dormía tranquilamente cuando un ratón pasó sobre su cabeza. El león lo atrapó y el ratón le pidió que lo perdonara. El león se rió y lo dejó ir. Tiempo después, el león quedó atrapado en una red de cazadores. El ratón escuchó sus rugidos y royó las cuerdas hasta liberarlo. Desde entonces, el león comprendió que hasta los más pequeños pueden ser grandes aliados.",
        "level": "En Proceso", "genre": "Fábula",
        "questions": [
            {"q": "¿Qué hacía el león cuando el ratón pasó?", "opts": ["Comía", "Dormía", "Cazaba", "Corría"], "a": 1, "type": "literal"},
            {"q": "¿Cómo atrapó el león al ratón?", "opts": ["Con una red", "Con las patas", "Con los dientes", "Con una trampa"], "a": 1, "type": "literal"},
            {"q": "¿Qué hizo el ratón para salvar al león?", "opts": ["Llamó ayuda", "Royó las cuerdas", "Trajo una llave", "Cavó un túnel"], "a": 1, "type": "inferencial"},
        ]
    },
    {
        "title": "La Tortuga y la Liebre",
        "content": "En un bosque frondoso, una liebre presumida se burlaba constantemente de la lentitud de una tortuga. Cansada de las burlas, la tortuga le propuso una carrera. La liebre, confiada en su velocidad, aceptó de inmediato y comenzó a correr velozmente, dejando muy atrás a su contrincante. Al verse tan distanciada, decidió tomar una siesta bajo un árbol. Mientras tanto, la tortuga avanzaba con paso firme y constante. Cuando la liebre despertó, la tortuga ya estaba cruzando la meta.",
        "level": "En Proceso", "genre": "Fábula",
        "questions": [
            {"q": "¿Quién se burlaba de la tortuga?", "opts": ["El zorro", "La liebre", "El cuervo", "El gato"], "a": 1, "type": "literal"},
            {"q": "¿Qué hizo la liebre durante la carrera?", "opts": ["Corrió sin parar", "Tomó una siesta", "Se rindió", "Se perdió"], "a": 1, "type": "literal"},
            {"q": "¿Cuál es la moraleja?", "opts": ["El más rápido gana", "La perseverancia vence al talento", "Dormir es bueno", "Las tortugas son lentas"], "a": 1, "type": "critica"},
        ]
    },
    {
        "title": "El Principito y la Rosa",
        "content": "En su pequeño planeta, el Principito cuidaba con esmero de una rosa única. Ella era hermosa pero vanidosa, y a menudo lo hacía dudar de sí mismo con sus exigencias y caprichos. Cansado de sus juegos, el Principito decidió emprender un viaje para conocer otros mundos y comprender mejor el significado de la amistad. En la Tierra, un zorro le enseñó que lo esencial es invisible a los ojos y que se vuelve responsable de aquello que se domestica.",
        "level": "Satisfactorio", "genre": "Novela corta",
        "questions": [
            {"q": "¿A quién cuidaba el Principito en su planeta?", "opts": ["A un zorro", "A una rosa", "A un rey", "A un farolero"], "a": 1, "type": "literal"},
            {"q": "¿Por qué el Principito decidió viajar?", "opts": ["Por aburrimiento", "Para conocer otros mundos", "Porque lo obligaron", "Para escapar"], "a": 1, "type": "literal"},
            {"q": "¿Qué le enseñó el zorro al Principito?", "opts": ["A cazar", "Que lo esencial es invisible a los ojos", "A pintar", "A cantar"], "a": 1, "type": "inferencial"},
            {"q": "¿Qué significa 'domesticar' en el texto?", "opts": ["Enseñar", "Crear lazos y ser responsable", "Entrenar", "Cuidar animales"], "a": 1, "type": "critica"},
        ]
    },
    {
        "title": "El Mito de Aracne",
        "content": "Aracne era una joven tejedora de extraordinario talento que vivía en la región de Lidia. Su habilidad era tan asombrosa que los habitantes comenzaron a compararla con la diosa Atenea. La joven, envanecida, osó desafiar a la diosa a un concurso de tejido. Aracne tejió un tapiz donde representaba los defectos de los dioses. Al ver la obra, la diosa montó en cólera por su insolencia y la golpeó con su lanzadera. Humillada, Aracne intentó ahorcarse, pero Atenea la transformó en araña, condenándola a tejer su tela por toda la eternidad.",
        "level": "Satisfactorio", "genre": "Mito griego",
        "questions": [
            {"q": "¿Cuál era el talento de Aracne?", "opts": ["Cantar", "Tejer", "Pintar", "Bailar"], "a": 1, "type": "literal"},
            {"q": "¿A quién desafió Aracne?", "opts": ["A Zeus", "A Atenea", "A Poseidón", "A Hera"], "a": 1, "type": "literal"},
            {"q": "¿Qué castigo recibió Aracne?", "opts": ["La muerte", "Ser transformada en araña", "El exilio", "La ceguera"], "a": 1, "type": "literal"},
        ]
    },
    {
        "title": "El Sueño de la Mariposa",
        "content": "Zhuangzi, un sabio filósofo chino, soñó una vez que era una mariposa que revoloteaba alegremente entre las flores, completamente ajena a su condición humana. En el sueño, era feliz y libre. Al despertar, se encontró nuevamente en su cuerpo, pero quedó sumido en una profunda confusión: no sabía si era Zhuangzi que había soñado ser mariposa, o si era una mariposa que ahora estaba soñando ser Zhuangzi. Esta paradoja lo llevó a reflexionar sobre la naturaleza de la realidad y la identidad.",
        "level": "Satisfactorio", "genre": "Parábola filosófica",
        "questions": [
            {"q": "¿Qué soñó Zhuangzi que era?", "opts": ["Un tigre", "Una mariposa", "Un sabio", "Un dios"], "a": 1, "type": "literal"},
            {"q": "¿Qué sintió al despertar?", "opts": ["Alegría", "Confusión", "Miedo", "Tristeza"], "a": 1, "type": "literal"},
            {"q": "¿Qué nos invita a reflexionar esta parábola?", "opts": ["Sobre los sueños", "Sobre la naturaleza de la realidad", "Sobre la vida", "Sobre la muerte"], "a": 1, "type": "critica"},
        ]
    },
]

created_texts = []
for td in texts_data:
    text = Text(title=td["title"], content=td["content"], level=td["level"], genre=td["genre"])
    db.add(text)
    db.commit()
    for q in td["questions"]:
        quiz = Quiz(text_id=text.id, question=q["q"], option_a=q["opts"][0], option_b=q["opts"][1], option_c=q["opts"][2], option_d=q["opts"][3], correct_answer=q["a"], question_type=q["type"])
        db.add(quiz)
    created_texts.append(text)
db.commit()
print(f"   ✅ {len(created_texts)} textos creados")

# ============================
# 4. PROGRESO SIMULADO
# ============================
print("📊 Generando progreso simulado...")
student_profiles = {
    "estudiante": {"sessions": 12, "avg_accuracy": 0.92, "level": "Satisfactorio"},
    "est_maria": {"sessions": 15, "avg_accuracy": 0.95, "level": "Satisfactorio"},
    "est_luis": {"sessions": 10, "avg_accuracy": 0.75, "level": "En Proceso"},
    "est_ana": {"sessions": 4, "avg_accuracy": 0.35, "level": "En Inicio"},
    "est_carlos": {"sessions": 8, "avg_accuracy": 0.68, "level": "En Proceso"},
    "est_sofia": {"sessions": 20, "avg_accuracy": 0.98, "level": "Satisfactorio"},
    "est_diego": {"sessions": 6, "avg_accuracy": 0.55, "level": "En Proceso"},
    "est_valeria": {"sessions": 3, "avg_accuracy": 0.30, "level": "En Inicio"},
    "est_mateo": {"sessions": 9, "avg_accuracy": 0.72, "level": "En Proceso"},
    "est_camila": {"sessions": 7, "avg_accuracy": 0.45, "level": "En Inicio"},
}

now = datetime.utcnow()
total_sessions = 0
for student_username, profile in student_profiles.items():
    student = db.query(User).filter(User.username == student_username).first()
    if not student: continue
    
    for i in range(profile["sessions"]):
        session_date = now - timedelta(days=random.randint(0, 6), hours=random.randint(0, 23))
        text = random.choice(created_texts)
        questions = db.query(Quiz).filter(Quiz.text_id == text.id).all()
        total_q = len(questions)
        base_correct = int(total_q * profile["avg_accuracy"])
        correct = max(0, min(total_q, base_correct + random.randint(-1, 1)))
        
        progress = Progress(
            student_id=student.id, text_id=text.id, score=correct, total_questions=total_q,
            time_spent=random.uniform(30, 180), level=profile["level"], points_earned=correct * 10, created_at=session_date
        )
        db.add(progress)
        total_sessions += 1

db.commit()
print(f"   ✅ {total_sessions} sesiones creadas")

print("\n============================================================")
print("✅ SEED COMPLETADO EXITOSAMENTE")
print("============================================================\n")
print("📋 Padres vinculados a hijos:")
print(f"   - padre (Carlos Pérez)  -> {parents[0].full_name} (hijo: Juan Pérez)")
print(f"   - padre2 (Rosa García)  -> {parents[1].full_name} (hijo: María Rodríguez)")
print(f"   - padre3 (Luis Torres)  -> {parents[2].full_name} (hijo: Luis Torres Mendoza)")
print(f"   - padre4 (Elena Mendoza)-> {parents[3].full_name} (hijo: Ana Ramírez Silva)")
print("\n============================================================")
db.close()