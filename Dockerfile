FROM python:3.12-slim

# Evita buffer de logs travar no stream
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias primeiro (cache de layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Codigo + assets. data/ e output/ inclusos (data.json = fallback).
COPY . .

# Porta injetada pelo Railway ($PORT). Default 8501 p/ local.
EXPOSE 8501
ENV PORT=8501

# exec form p/ signal handling limpo (SIGTERM do Railway).
# shell form com ${PORT} nao funciona em exec form -> usar sh -c.
ENTRYPOINT ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true"]
