"""
Seed de base de datos — DevOps Task Manager API
Crea tareas iniciales para poder probar el pipeline y los endpoints.

Uso:
    py seed.py
"""

from app.database import Base, engine, SessionLocal, TaskDB

TASKS = [
    {
        "title": "Configurar repositorio GitHub",
        "description": "Crear el repositorio, agregar .gitignore y hacer el primer push.",
        "completed": True,
    },
    {
        "title": "Implementar FastAPI CRUD",
        "description": "Endpoints GET, POST, PUT, DELETE para /tasks y endpoint /health.",
        "completed": True,
    },
    {
        "title": "Escribir tests con pytest",
        "description": "Cubrir: crear tarea, listar tareas, actualizar y eliminar. Usar BD en memoria.",
        "completed": True,
    },
    {
        "title": "Crear Dockerfile multistage",
        "description": "Etapa builder para instalar dependencias y etapa runtime slim para producción.",
        "completed": True,
    },
    {
        "title": "Levantar Jenkins con docker-compose",
        "description": "Jenkins LTS con volumen persistente en puerto 8080, socket Docker montado.",
        "completed": False,
    },
    {
        "title": "Escribir Jenkinsfile con 4 stages",
        "description": "Stages: Checkout → Test → Build → Push. Pipeline as Code versionado en el repo.",
        "completed": False,
    },
    {
        "title": "Configurar credenciales Docker Hub en Jenkins",
        "description": "Agregar credencial 'dockerhub-creds' de tipo Username/Password en Jenkins.",
        "completed": False,
    },
    {
        "title": "Desplegar en Kubernetes",
        "description": "Namespace devops-project, Deployment 2 réplicas, Service LoadBalancer y HPA.",
        "completed": False,
    },
    {
        "title": "Validar pipeline end-to-end",
        "description": "Commit → Jenkins detecta cambio → tests pasan → imagen en Docker Hub → K8s actualiza pods.",
        "completed": False,
    },
    {
        "title": "Redactar informe técnico",
        "description": "PDF con capturas de pantalla de cada stage del pipeline y evidencias de despliegue.",
        "completed": False,
    },
]


def seed():
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Evitar duplicados: solo ejecutar si la tabla está vacía
        existing = db.query(TaskDB).count()
        if existing > 0:
            print(f"⚠️  La base de datos ya tiene {existing} tarea(s). Seed omitido.")
            print("   Ejecuta: py seed.py --force  para limpiar y re-insertar.")
            return

        for data in TASKS:
            task = TaskDB(**data)
            db.add(task)

        db.commit()
        print(f"✅ Seed completado: {len(TASKS)} tareas insertadas en tasks.db")
        print()
        print("   Prueba la API en: http://localhost:8000/docs")
        print("   O consulta directo:")
        print("   curl http://localhost:8000/tasks/")

    finally:
        db.close()


def seed_force():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for data in TASKS:
            task = TaskDB(**data)
            db.add(task)
        db.commit()
        print(f"✅ Seed forzado: {len(TASKS)} tareas insertadas (tabla limpiada previamente).")
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if "--force" in sys.argv:
        seed_force()
    else:
        seed()
