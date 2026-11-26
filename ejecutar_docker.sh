#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
evidencia="$PWD/evidencia_docker/$(date '+%Y%m%d_%H%M%S')_$$"
mkdir -p "$evidencia"
trap 'echo "Prueba incompleta. Registros: $evidencia" >&2' ERR

docker version > "$evidencia/version_docker.txt" 2>&1
docker info --format '{{.OSType}}' > "$evidencia/tipo_contenedor.txt" 2>&1
tipo=$(cat "$evidencia/tipo_contenedor.txt")
if [[ "$tipo" != linux ]]; then
  echo "Este proyecto requiere contenedores Linux." >&2
  exit 1
fi
echo "Construyendo vision-bombas:4.2."
docker build -t vision-bombas:4.2 . > "$evidencia/construccion.txt" 2>&1
docker image inspect --format '{{.Id}}' vision-bombas:4.2 > "$evidencia/id_imagen.txt"
montaje="type=bind,source=$evidencia,target=/app/outputs"
docker run --rm --network none --mount "$montaje" vision-bombas:4.2 \
  --carpeta data/validacion --modo lote --lote 8 --salida outputs/lote \
  > "$evidencia/ejecucion_lote.txt" 2>&1
docker run --rm --network none --mount "$montaje" vision-bombas:4.2 \
  --carpeta data/validacion --modo flujo --intervalo 0.1 --salida outputs/flujo \
  > "$evidencia/ejecucion_flujo.txt" 2>&1

shopt -s nullglob nocaseglob
propias=(data/propias/*.{jpg,jpeg,png,bmp,tif,tiff})
if (( ${#propias[@]} > 0 )); then
  docker run --rm --network none --mount "$montaje" \
    --mount "type=bind,source=$PWD/data/propias,target=/app/fotos_propias,readonly" \
    vision-bombas:4.2 --carpeta fotos_propias --salida outputs/propias \
    > "$evidencia/ejecucion_propias.txt" 2>&1
  cat "$evidencia/propias/predicciones.csv"
else
  echo 'Prueba con foto nueva pendiente.' > "$evidencia/ejecucion_propias.txt"
fi
docker run --rm --network none --mount "$montaje" --entrypoint python \
  vision-bombas:4.2 src/resumir_evidencia.py outputs \
  > "$evidencia/verificacion.txt" 2>&1
date -u '+Ejecución real de Docker terminada: %Y-%m-%dT%H:%M:%SZ' > "$evidencia/ESTADO_EJECUCION.txt"
cat "$evidencia/ejecucion_lote.txt" "$evidencia/verificacion.txt"
echo "Evidencia disponible en $evidencia."
