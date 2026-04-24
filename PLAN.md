# Proyecto Integrador DevOps — CI/CD con FastAPI, Docker, Jenkins y Kubernetes

## Resultado de Aprendizaje

> Diseña e implementa pipelines de integración y entrega continua (CI/CD), automatizando procesos de desarrollo y despliegue, y aplica prácticas de DevOps para gestionar entornos de infraestructura escalables y eficientes, utilizando herramientas como Docker, Kubernetes y Jenkins.

---

## Nombre del Proyecto

**DevOps Task Manager API** — API REST de gestión de tareas construida con FastAPI, contenerizada con Docker, desplegada en Kubernetes (Docker Desktop) y automatizada mediante un pipeline Jenkins.

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Aplicación | Python 3.12 + FastAPI |
| Base de datos | SQLite (embebida) |
| Tests | pytest + httpx |
| Contenerización | Docker (multistage) |
| Registry de imágenes | Docker Hub |
| CI/CD | Jenkins (docker-compose) |
| Orquestación | Kubernetes (Docker Desktop) |
| Escalabilidad | Horizontal Pod Autoscaler (HPA) |

---

## Estructura del Repositorio

```
material-devops-integracion/
├── app/
│   ├── main.py              # Entrypoint FastAPI + endpoint /health
│   ├── routers/
│   │   └── tasks.py         # CRUD de tareas
│   ├── models.py            # Modelos Pydantic
│   └── database.py          # Configuración SQLite
├── tests/
│   └── test_tasks.py        # Tests con pytest y TestClient
├── k8s/
│   ├── namespace.yaml       # Namespace devops-project
│   ├── deployment.yaml      # Deployment (2 réplicas + probes)
│   ├── service.yaml         # Service tipo LoadBalancer
│   ├── configmap.yaml       # Variables de entorno
│   └── hpa.yaml             # HPA: 2-5 pods al 60% CPU
├── jenkins/
│   └── docker-compose.yml   # Jenkins LTS con Docker socket
├── Dockerfile               # Imagen multistage de producción
├── docker-compose.yml       # Entorno de desarrollo local
├── Jenkinsfile              # Pipeline declarativo (4 stages)
├── requirements.txt
├── PLAN.md
└── README.md
```

---

## Plan de 3 Semanas

### Semana 1 — Aplicación + Docker

**Objetivo**: tener la aplicación corriendo localmente en un contenedor.

| # | Tarea | Archivo(s) |
|---|---|---|
| 1 | Scaffolding del repositorio | `requirements.txt`, `.gitignore`, `README.md` |
| 2 | FastAPI CRUD (`GET`, `POST`, `PUT`, `DELETE /tasks`) con persistencia SQLite | `app/main.py`, `app/routers/tasks.py`, `app/models.py`, `app/database.py` |
| 3 | Endpoint `/health` para probes de Kubernetes | `app/main.py` |
| 4 | Tests con pytest: crear tarea, listar tareas, eliminar tarea | `tests/test_tasks.py` |
| 5 | Dockerfile multistage (etapa builder + etapa runtime slim) | `Dockerfile` |
| 6 | docker-compose para desarrollo local con hot-reload | `docker-compose.yml` |
| 7 | Push inicial a GitHub | — |

**Verificación**:
```bash
docker build -t taskapi . && docker run -p 8000:8000 taskapi
# → http://localhost:8000/docs responde
pytest tests/ -v
# → todos los tests en verde
```

---

### Semana 2 — Jenkins CI Pipeline

**Objetivo**: cada push al repositorio dispara automáticamente el pipeline de integración.

| # | Tarea | Archivo(s) |
|---|---|---|
| 8 | Jenkins LTS con docker-compose (volumen persistente, puerto 8080) | `jenkins/docker-compose.yml` |
| 9 | Jenkinsfile con stage **Checkout** | `Jenkinsfile` |
| 10 | Jenkinsfile con stage **Test** (pytest + reporte JUnit XML) | `Jenkinsfile` |
| 11 | Jenkinsfile con stage **Build** (`docker build -t user/taskapi:$BUILD_NUMBER`) | `Jenkinsfile` |
| 12 | Jenkinsfile con stage **Push** a Docker Hub (credencial en Jenkins) | `Jenkinsfile` |
| 13 | Configurar credenciales Docker Hub en Jenkins | — |
| 14 | Trigger SCM polling cada 5 min (`H/5 * * * *`) | `Jenkinsfile` |
| 15 | Capturar reporte de tests como artefacto Jenkins | `Jenkinsfile` |

**Verificación**:
- Commit → Jenkins detecta cambio → pipeline ejecuta los 4 stages → imagen publicada en Docker Hub

---

### Semana 3 — Kubernetes + Pipeline Completo

**Objetivo**: el pipeline despliega automáticamente la nueva imagen en Kubernetes.

| # | Tarea | Archivo(s) |
|---|---|---|
| 16 | Namespace `devops-project` | `k8s/namespace.yaml` |
| 17 | Deployment: 2 réplicas, liveness probe (`GET /health`), readiness probe | `k8s/deployment.yaml` |
| 18 | Service tipo LoadBalancer para acceso local vía Docker Desktop | `k8s/service.yaml` |
| 19 | ConfigMap con variables de entorno de la app | `k8s/configmap.yaml` |
| 20 | HPA: escalar entre 2 y 5 pods cuando CPU supere el 60% | `k8s/hpa.yaml` |
| 21 | Stage **Deploy** en Jenkinsfile (`kubectl apply -f k8s/`) | `Jenkinsfile` |
| 22 | Validación end-to-end: commit → Jenkins → imagen nueva → K8s actualiza sin downtime | — |
| 23 | Redacción del informe técnico PDF con capturas y evidencias | — |

**Verificación**:
```bash
kubectl get pods -n devops-project
# → 2 pods en estado Running
kubectl get hpa -n devops-project
# → HPA activo
kubectl get svc -n devops-project
# → EXTERNAL-IP accesible
```

---

## Pipeline Jenkins — Stages

```
Checkout → Test → Build → Push → Deploy
```

```groovy
// Vista simplificada del Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Checkout') { ... }   // git clone
        stage('Test')     { ... }   // pytest + junit report
        stage('Build')    { ... }   // docker build
        stage('Push')     { ... }   // docker push a Docker Hub
        stage('Deploy')   { ... }   // kubectl apply -f k8s/
    }
}
```

---

## Arquitectura del Sistema

```
Developer
    │
    │  git push
    ▼
GitHub Repository
    │
    │  SCM polling / webhook
    ▼
Jenkins (docker-compose)
    ├── Stage: Test   ──────────── pytest (JUnit report)
    ├── Stage: Build  ──────────── docker build (multistage)
    ├── Stage: Push   ──────────── Docker Hub registry
    └── Stage: Deploy ──────────── kubectl apply
                                        │
                                        ▼
                              Kubernetes (Docker Desktop)
                              Namespace: devops-project
                              ┌─────────────────────────┐
                              │  Deployment             │
                              │  ├── Pod 1 (FastAPI)    │
                              │  └── Pod 2 (FastAPI)    │
                              │  HPA (2-5 pods)         │
                              │  Service (LoadBalancer)  │
                              └─────────────────────────┘
```

---

## Decisiones de Diseño

| Decisión | Justificación |
|---|---|
| SQLite en lugar de PostgreSQL | Elimina complejidad de BD en K8s; el foco es el pipeline, no la persistencia |
| Docker Hub como registry | Gratuito, sin infraestructura adicional |
| kubectl dentro de Jenkins | Vía kubeconfig montado, sin plugins adicionales de K8s |
| Imagen multistage | Imagen de producción ligera; separa dependencias de build del runtime |
| HPA con límite de CPU | Demuestra escalabilidad horizontal requerida en el RA |

**Fuera del alcance** (complejidad no requerida para el RA):
- HTTPS / TLS / Ingress Controller
- Secrets management avanzado (Vault, Sealed Secrets)
- Monitoreo y observabilidad (Prometheus, Grafana)
- Múltiples ambientes (staging / producción)

---

## Entregables Finales

1. **Repositorio GitHub** con todo el código, manifiestos y Jenkinsfile
2. **Informe técnico PDF** con:
   - Descripción de la arquitectura
   - Capturas de Jenkins (stages en verde)
   - Capturas de `kubectl get pods/hpa/svc`
   - Evidencia del flujo end-to-end (commit → deploy)
   - Conclusiones y lecciones aprendidas
