#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
python src/pipeline_inferencia.py --carpeta data/ejemplos --modo lote --salida outputs/demo
echo "Demo completada. Revisa outputs/demo."
