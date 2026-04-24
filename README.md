# DevOps Task Manager API

API REST de gestión de tareas construida con **FastAPI**, contenerizada con **Docker** y automatizada mediante un pipeline **Jenkins** + desplegada en **Kubernetes**.

> Proyecto Integrador — Especialización en Arquitectura de Software · Curso DevOps e Integración Continua · 2026

---

## Stack

| Capa | Tecnología |
|---|---|
| Aplicación | Python 3.12 + FastAPI |
| Base de datos | SQLite (embebida) |
| Tests | pytest + httpx |
| Contenerización | Docker (multistage) |
| Registry | Docker Hub |
| CI/CD | Jenkins (docker-compose) |
| Orquestación | Kubernetes (Docker Desktop) |

---

## Semana 1 — Aplicación + Docker ✅

### Pre-requisitos

- Python 3.12
- Docker Desktop ≥ 4.28

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/material-devops-integracion.git
cd material-devops-integracion

# Crear entorno virtual
python -m venv .venv

# Activar (Windows PowerShell)
.venv\Scripts\Activate.ps1
# Activar (Linux / macOS)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Correr la API en desarrollo

```bash
# Opción A — uvicorn directo (con hot-reload)
uvicorn app.main:app --reload --port 8000

# Opción B — Docker Compose (recomendado)
docker compose up --build
```

Abrir en el navegador: **http://localhost:8000/docs**

### Ejecutar los tests

```bash
pytest tests/ -v

# Con reporte XML para Jenkins
pytest tests/ -v --junitxml=tests/results.xml
```

### Construir y ejecutar la imagen de producción

```bash
docker build -t taskapi .
docker run -p 8000:8000 taskapi
```

---

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Liveness / readiness probe |
| `GET` | `/tasks/` | Listar todas las tareas |
| `POST` | `/tasks/` | Crear una tarea |
| `GET` | `/tasks/{id}` | Obtener tarea por ID |
| `PUT` | `/tasks/{id}` | Actualizar tarea |
| `DELETE` | `/tasks/{id}` | Eliminar tarea |

---

## Estructura del repositorio

```
material-devops-integracion/
├── app/
│   ├── main.py              # Entrypoint FastAPI + /health
│   ├── models.py            # Modelos Pydantic
│   ├── database.py          # SQLite con SQLAlchemy
│   └── routers/
│       └── tasks.py         # CRUD de tareas
├── tests/
│   └── test_tasks.py        # Tests con pytest
├── k8s/                     # Manifiestos Kubernetes (Semana 3)
├── jenkins/                 # docker-compose Jenkins (Semana 2)
├── Dockerfile               # Imagen multistage
├── docker-compose.yml       # Entorno de desarrollo local
├── Jenkinsfile              # Pipeline CI/CD (Semana 2)
├── requirements.txt
├── PLAN.md
└── overview.html
```
