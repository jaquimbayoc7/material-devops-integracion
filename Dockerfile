# ─────────────────────────────────────────────────────────────────
# Etapa 1 — Builder: instala dependencias
# ─────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─────────────────────────────────────────────────────────────────
# Etapa 2 — Runtime: imagen de producción ligera
# ─────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copiar dependencias instaladas desde el builder
COPY --from=builder /install /usr/local

# Copiar el código fuente
COPY app/ ./app/

# Puerto de la aplicación
EXPOSE 8000

# Usuario sin privilegios por seguridad
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/data \
    && chown appuser:appuser /app/data
USER appuser

ENV DATABASE_URL=sqlite:////app/data/tasks.db

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
