"""Compara las predicciones y prepara la tabla del informe de Docker."""

import csv
import json
import re
import sys
from pathlib import Path


def leer_csv(ruta):
    with ruta.open(encoding='utf-8', newline='') as archivo:
        return list(csv.DictReader(archivo))


def revisar_modalidad(evidencia, modo, referencia, huella):
    carpeta = evidencia / modo
    resumen = json.loads((carpeta / 'resumen.json').read_text(encoding='utf-8'))
    filas = leer_csv(carpeta / 'predicciones.csv')
    archivos = {fila['archivo'] for fila in filas}
    if resumen['modelo_sha256'] != huella:
        raise ValueError(f'{modo}: cambió el archivo de pesos previsto.')
    if resumen['modo'] != modo or len(filas) != resumen['imagenes']:
        raise ValueError(f'{modo}: el CSV no coincide con el resumen.')
    if archivos != set(referencia) or len(archivos) != len(filas):
        raise ValueError(f'{modo}: las imágenes no coinciden con la validación de 3.3.')
    datos = {
        'resumen': resumen,
        'aciertos': sum(fila['prediccion'] == referencia[fila['archivo']]['real']
                        for fila in filas),
        'coinciden_con_3_3': sum(
            fila['prediccion'] == referencia[fila['archivo']]['prediccion']
            for fila in filas
        ),
    }
    return datos, {fila['archivo']: fila['prediccion'] for fila in filas}


def tabla_latex(modos, coincidencias, propias, imagen):
    def fila(modo, datos):
        s = datos['resumen']
        return (f"{modo.capitalize()} & {s['imagenes']} & {s['procesamiento_s']:.3f} & "
                f"{s['operacion_s']:.3f} & {s['promedio_procesamiento_ms_por_imagen']:.2f} & "
                f"{datos['aciertos']} " + r'\\')

    texto = [
        r'La imagen se construyó y se ejecutó con Docker. Su identificador abreviado es '
        + r'\texttt{' + imagen.split(':')[1][:12] + '}.',
        r'\begin{center}\small',
        r'\begin{tabular}{lrrrrr}\toprule',
        r'Modo & Imágenes & Proceso (s) & Operación (s) & ms/imagen & Aciertos \\\midrule',
        *(fila(modo, datos) for modo, datos in modos.items()),
        r'\bottomrule\end{tabular}\end{center}',
        f'El lote y el flujo coincidieron en {coincidencias} clases predichas.',
    ]
    if not propias:
        texto.append('La prueba independiente queda pendiente de una fotografía nueva.')
    else:
        for i, r in enumerate(propias, 1):
            clase = {'impulsor': 'impulsor', 'tazon': 'tazón'}[r['prediccion']]
            texto.append(
                f"En la foto propia {i} el modelo predijo {clase} "
                f"con una confianza de {float(r['confianza_pct']):.2f}\\%."
            )
    return '\n'.join(texto) + '\n'


def main():
    evidencia = Path(sys.argv[1])
    imagen = (evidencia / 'id_imagen.txt').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', imagen):
        raise ValueError('Falta el identificador de la imagen Docker construida.')
    raiz = Path(__file__).resolve().parents[1]
    ficha = json.loads((raiz / 'models/ficha_modelo.json').read_text(encoding='utf-8'))
    huella = ficha['modelo_sha256']
    referencia = {r['archivo']: r for r in leer_csv(raiz / 'data/origen/predicciones_3_3.csv')}
    lote, plote = revisar_modalidad(evidencia, 'lote', referencia, huella)
    flujo, pflujo = revisar_modalidad(evidencia, 'flujo', referencia, huella)
    coincidencias = sum(plote[n] == pflujo[n] for n in plote)
    ruta_propias = evidencia / 'propias/predicciones.csv'
    propias = leer_csv(ruta_propias) if ruta_propias.is_file() else []
    modos = {'lote': lote, 'flujo': flujo}
    resultados = {'imagen_docker': imagen, 'modos': modos, 'coincidencias': coincidencias,
                  'fotos_propias': propias}
    (evidencia / 'verificacion.json').write_text(
        json.dumps(resultados, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (evidencia / 'mediciones_docker.tex').write_text(
        tabla_latex(modos, coincidencias, propias, imagen), encoding='utf-8')
    print(f'Docker procesó {len(plote)} recortes en cada modalidad.')
    print(f'Coincidencias lote y flujo: {coincidencias}/{len(plote)}.')
    print(f'Fotos propias procesadas: {len(propias)}.')


if __name__ == '__main__':
    main()
