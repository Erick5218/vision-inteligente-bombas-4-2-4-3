"""Actividad 4.1: inferencia con la ResNet18 de la Actividad 3.3.

Entrada: una pieza ya recortada por imagen. Ejecución en CPU.
El modelo conserva dos clases: impulsor y tazon.
"""

import argparse
import csv
import hashlib
import json
import os
import platform
import time
from pathlib import Path

import torch
import torchvision
from PIL import Image, UnidentifiedImageError
from torch import nn
from torchvision import models, transforms

RAIZ = Path(__file__).resolve().parents[1]
EXTENSIONES = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}


def cargar_modelo(ruta, ruta_clases):
    """Recupera pesos, clases y transformación sin volver a entrenar."""
    if not ruta.is_file():
        raise FileNotFoundError(f'No se encuentra el modelo: {ruta}')
    inicio = time.perf_counter()
    datos = torch.load(ruta, map_location='cpu', weights_only=True)
    clases = datos['classes']
    clases_archivo = ruta_clases.read_text(encoding='utf-8').splitlines()
    if clases_archivo != clases:
        raise ValueError('El orden de clases.txt no coincide con el modelo.')
    modelo = models.resnet18(weights=None)
    modelo.fc = nn.Linear(modelo.fc.in_features, len(clases))
    modelo.load_state_dict(datos['state_dict'])
    modelo.eval()
    # Se conserva la transformación del entrenamiento, incluida la interpolación.
    transformar = transforms.Compose([
        transforms.Resize((datos['image_size'], datos['image_size'])),
        transforms.ToTensor(),
        transforms.Normalize(datos['mean'], datos['std']),
    ])
    carga_ms = (time.perf_counter() - inicio) * 1000
    return modelo, clases, transformar, carga_ms


def preprocesar_imagen(ruta, transformar):
    """Abre la imagen, pasa a RGB, ajusta tamaño y normaliza."""
    try:
        with Image.open(ruta) as imagen:
            return transformar(imagen.convert('RGB'))
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError(f'No se puede leer la imagen: {ruta.name}') from error


def inferir_grupo(modelo, rutas, transformar, clases):
    """Mide un grupo completo: lectura, preparación, red y posprocesamiento."""
    inicio = time.perf_counter()
    entrada = torch.stack([preprocesar_imagen(p, transformar) for p in rutas])
    with torch.no_grad():
        probabilidades = torch.softmax(modelo(entrada), dim=1)
    filas = []
    for ruta, probabilidades_imagen in zip(rutas, probabilidades):
        indice = int(probabilidades_imagen.argmax())
        fila = {'archivo': ruta.name, 'prediccion': clases[indice],
                'confianza_pct': round(float(probabilidades_imagen[indice]) * 100, 6)}
        for clase, valor in zip(clases, probabilidades_imagen):
            fila[f'p_{clase}'] = round(float(valor), 8)
        filas.append(fila)
    duracion_ms = (time.perf_counter() - inicio) * 1000
    return filas, duracion_ms


def guardar_csv(ruta, filas):
    with ruta.open('w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def nombre_cpu():
    ruta = Path('/proc/cpuinfo')
    if ruta.is_file():
        for linea in ruta.read_text().splitlines():
            if linea.startswith('model name'):
                return linea.split(':', 1)[1].strip()
    return platform.processor() or platform.machine()


def main(argumentos=None):
    parser = argparse.ArgumentParser(description=__doc__)
    entrada = parser.add_mutually_exclusive_group()
    entrada.add_argument('--imagen', type=Path, help='Una pieza recortada.')
    entrada.add_argument('--carpeta', type=Path, help='Carpeta de imágenes, sin subcarpetas.')
    parser.add_argument('--modelo', type=Path, default=RAIZ / 'models/modelo.pt')
    parser.add_argument('--clases', type=Path, default=RAIZ / 'data/clases.txt')
    parser.add_argument('--modo', choices=['lote', 'flujo'], default='lote')
    parser.add_argument('--lote', type=int, default=8)
    parser.add_argument('--intervalo', type=float, default=0.1,
                        help='Segundos de espera entre imágenes; solo modo flujo.')
    parser.add_argument('--hilos', type=int, default=3)
    parser.add_argument('--salida', type=Path, default=RAIZ / 'outputs/demo')
    args = parser.parse_args(argumentos)
    if args.lote < 1 or args.hilos < 1 or args.intervalo < 0:
        parser.error('Lote e hilos deben ser positivos; intervalo no puede ser negativo.')
    if args.imagen is not None:
        rutas = [args.imagen]
        if not args.imagen.is_file():
            raise FileNotFoundError(f'No existe la imagen: {args.imagen}')
    else:
        carpeta = args.carpeta or RAIZ / 'data/ejemplos'
        if not carpeta.is_dir():
            raise FileNotFoundError(f'No existe la carpeta: {carpeta}')
        rutas = sorted(p for p in carpeta.iterdir()
                       if p.is_file() and p.suffix.lower() in EXTENSIONES)
    if not rutas:
        raise ValueError('La carpeta no contiene imágenes compatibles.')

    torch.set_num_threads(min(args.hilos, os.cpu_count() or 1))
    modelo, clases, transformar, carga_ms = cargar_modelo(args.modelo, args.clases)
    # Una pasada previa prepara la ejecución. Se excluye de los tiempos medidos.
    inferir_grupo(modelo, rutas[:1], transformar, clases)
    tamano_lote = 1 if args.modo == 'flujo' else args.lote
    resultados, tiempos = [], []
    inicio_operacion = time.perf_counter()
    for inicio in range(0, len(rutas), tamano_lote):
        grupo = rutas[inicio:inicio + tamano_lote]
        filas, duracion_ms = inferir_grupo(modelo, grupo, transformar, clases)
        numero = len(tiempos) + 1
        for fila in filas:
            fila['grupo'] = numero
        resultados.extend(filas)
        tiempos.append({'grupo': numero, 'imagenes': len(grupo),
                        'procesamiento_ms': round(duracion_ms, 6)})
        if args.modo == 'flujo':
            print(f"{filas[0]['archivo']}: {filas[0]['prediccion']} "
                  f"({filas[0]['confianza_pct']:.2f} %)")
            if inicio + tamano_lote < len(rutas):
                time.sleep(args.intervalo)
    operacion_s = time.perf_counter() - inicio_operacion
    procesamiento_s = sum(f['procesamiento_ms'] for f in tiempos) / 1000
    resumen = {
        'modo': args.modo, 'imagenes': len(resultados), 'lote': tamano_lote,
        'intervalo_simulado_s': args.intervalo if args.modo == 'flujo' else 0,
        'carga_modelo_ms': round(carga_ms, 3),
        'procesamiento_s': round(procesamiento_s, 6),
        'operacion_s': round(operacion_s, 6),
        'promedio_procesamiento_ms_por_imagen': round(procesamiento_s * 1000 / len(rutas), 3),
        'imagenes_por_s_procesamiento': round(len(rutas) / procesamiento_s, 3),
        'imagenes_por_s_operacion': round(len(rutas) / operacion_s, 3),
        'calentamiento_imagenes': 1,
        'python': platform.python_version(), 'torch': torch.__version__,
        'torchvision': torchvision.__version__, 'pillow': Image.__version__,
        'sistema': platform.platform(), 'cpu': nombre_cpu(),
        'hilos': torch.get_num_threads(), 'dispositivo': 'cpu',
        'modelo_sha256': hashlib.sha256(args.modelo.read_bytes()).hexdigest(),
        'alcance': 'Clasificación de recortes; validación reutilizada de la Actividad 3.3.',
    }
    args.salida.mkdir(parents=True, exist_ok=True)
    guardar_csv(args.salida / 'predicciones.csv', resultados)
    guardar_csv(args.salida / 'tiempos.csv', tiempos)
    (args.salida / 'resumen.json').write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"{len(resultados)} imágenes | {args.modo} | "
          f"{resumen['promedio_procesamiento_ms_por_imagen']:.3f} ms/imagen "
          '(promedio de procesamiento)')
    print(f'Salida: {args.salida.name}/predicciones.csv, tiempos.csv y resumen.json')
    return resultados, resumen


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        raise SystemExit(f'ERROR: {error}')
