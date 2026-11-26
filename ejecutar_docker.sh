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
argumentos_certificados=()
if [[ -n ${DOCKER_CERTIFICADOS_PROXY:-} ]]; then
  argumentos_certificados=(--secret "id=certificados_proxy,src=$DOCKER_CERTIFICADOS_PROXY")
fi
docker build --build-arg HTTP_PROXY --build-arg HTTPS_PROXY "${argumentos_certificados[@]}" \
  -t vision-bombas:4.2 . \
  > "$evidencia/construccion.txt" 2>&1
imagen=$(docker image inspect --format '{{.Id}}' vision-bombas:4.2)
printf '%s\n' "$imagen" > "$evidencia/id_imagen.txt"
montaje="type=bind,source=$evidencia,target=/app/outputs"
docker run --rm --network none --mount "$montaje" "$imagen" \
  --carpeta data/validacion --modo lote --lote 8 --salida outputs/lote \
  > "$evidencia/ejecucion_lote.txt" 2>&1
docker run --rm --network none --mount "$montaje" "$imagen" \
  --carpeta data/validacion --modo flujo --intervalo 0.1 --salida outputs/flujo \
  > "$evidencia/ejecucion_flujo.txt" 2>&1

docker run --rm --network none --mount "$montaje" "$imagen" \
  --imagen data/prueba_externa/impulsor_bomba_pozo.png --salida outputs/externa \
  > "$evidencia/ejecucion_externa.txt" 2>&1

shopt -s nullglob nocaseglob
propias=(data/propias/*.{jpg,jpeg,png,bmp,tif,tiff})
if (( ${#propias[@]} > 0 )); then
  docker run --rm --network none --mount "$montaje" \
    --mount "type=bind,source=$PWD/data/propias,target=/app/fotos_propias,readonly" \
    "$imagen" --carpeta fotos_propias --salida outputs/propias \
    > "$evidencia/ejecucion_propias.txt" 2>&1
  cat "$evidencia/propias/predicciones.csv"
else
  echo 'No se añadieron fotos propias para esta ejecución.' > "$evidencia/ejecucion_propias.txt"
fi
docker run --rm --network none --mount "$montaje" --entrypoint python \
  "$imagen" src/resumir_evidencia.py outputs \
  > "$evidencia/verificacion.txt" 2>&1
date -u '+Ejecución real de Docker terminada: %Y-%m-%dT%H:%M:%SZ' > "$evidencia/ESTADO_EJECUCION.txt"
cat "$evidencia/ejecucion_lote.txt" "$evidencia/ejecucion_externa.txt" "$evidencia/verificacion.txt"
echo "Evidencia disponible en $evidencia."
