# Actividad 4.2. Mismo script y pesos de la práctica 4.1, en CPU.
FROM python:3.12-slim-bookworm
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN --mount=type=secret,id=certificados_proxy,target=/etc/ssl/certs/ca-certificates.crt \
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt python -m pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/
RUN mkdir -p /app/outputs
ENTRYPOINT ["python", "src/pipeline_inferencia.py"]
CMD ["--carpeta", "data/validacion", "--modo", "lote", "--lote", "8", "--salida", "outputs/docker_lote"]
