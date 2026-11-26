# Actividades 4.2 y 4.3 de Visión Inteligente

**Clasificación de impulsores y tazones de bombas sumergibles**

Erick Martín Rodríguez Baeza · 26ZPM034 · Docente I.MT. Luis Alberto Espejo Ponce

Se reutilizan los pesos de ResNet18 de la actividad 3.3 y el script de inferencia de la 4.1. El proyecto recibe recortes de piezas individuales y muestra la clase predicha y su confianza. El `Dockerfile` empaqueta el código, los pesos, las dependencias de CPU, los recortes de validación y una fotografía externa.

El dataset original de 25 fotografías y sus anotaciones se incluye en `data/origen/dataset_bombas.zip`. Los recortes en `data/validacion/` proceden de la partición de la 3.3. El dataset conserva también las anotaciones de flechas de bomba. El clasificador entrenado emplea las dos clases registradas en `data/clases.txt`.

## Ejecutar en Windows

1. Abre esta carpeta en PowerShell y comprueba `git --version` y `docker version`. El segundo comando debe mostrar `Client` y `Server`. Si falta Git, usa [Git para Windows](https://git-scm.com/install/windows). Si falta Docker, sigue la [instalación oficial de Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Abre Docker Desktop y usa contenedores Linux. Si el instalador pide habilitar o actualizar WSL 2, sigue su indicación de administrador y reinicia si Windows lo solicita. Vuelve a abrir Docker Desktop antes de continuar.
3. Si tienes una foto nueva, copia un JPG o PNG de una sola pieza en `data/propias/`.
4. Ejecuta desde PowerShell:

```powershell
.\ejecutar_docker.bat
```

En Linux el equivalente es `bash ejecutar_docker.sh`. La construcción usa BuildKit, que viene con Docker Desktop. La primera vez descarga la imagen base y las bibliotecas. Una vez creada la imagen, la inferencia corre con CPU y archivos locales. Python viene dentro de la imagen.

Cada ejecución guarda una carpeta nueva en `evidencia_docker/`. Encontrarás la versión de Docker, el registro de construcción, el identificador de imagen, los CSV de predicciones y tiempos, el resumen JSON y la comparación con la actividad 3.3. La fotografía externa incluida se prueba siempre y su resultado se guarda en `externa/`. Si el script encuentra fotos propias, guarda sus resultados en `propias/`. `ESTADO_EJECUCION.txt` aparece cuando termina la comprobación.

Para demostrar una inferencia individual después de construir la imagen, ejecuta el comando siguiente desde PowerShell o Bash. La procedencia de la fotografía está en `data/prueba_externa/FUENTE.md`.

```text
docker run --rm vision-bombas:4.2 --modo flujo --imagen data/prueba_externa/impulsor_bomba_pozo.png
```

## Reporte y evidencia

El PDF incluye una ejecución en Docker Engine 28.5.2 sobre Linux virtual, además de la referencia en CPU. Los registros de la construcción, las predicciones y los tiempos medidos del contenedor están en `evidencia_docker/`. La referencia nativa está en `evidencia_local/`.

El reporte se compila con pdfLaTeX desde `reporte/main.tex`. Para importarlo en Overleaf, carga `main.tex` y la carpeta `assets/` juntos en un ZIP, con `main.tex` en la raíz del proyecto. Si repites la prueba y quieres actualizar la tabla del reporte, usa las mediciones que la ejecución guarda junto a sus registros.

El tiempo de procesamiento suma lectura, preparación, inferencia y posprocesamiento. En modo flujo, el tiempo de operación incluye las pausas de 0.1 s. Las 33 imágenes se reutilizan para comprobar consistencia. La foto externa prueba que el comando admite una entrada que quedó fuera del entrenamiento y de la validación.

## Repositorio de la entrega

La entrega conjunta está en [el repositorio de GitHub](https://github.com/Erick5218/vision-inteligente-bombas-4-2-4-3). Se puede clonar la rama principal y ejecutar las pruebas desde esa carpeta.

```text
git clone https://github.com/Erick5218/vision-inteligente-bombas-4-2-4-3.git
```

El PDF que se presenta en la actividad 4.3 incluye la liga del repositorio. La imagen de Docker se puede reconstruir con el Dockerfile y conservar en el equipo donde se ejecute.

## Archivos principales

| Archivo o carpeta | Contenido |
|---|---|
| `src/pipeline_inferencia.py` | Inferencia de la actividad 4.1. |
| `models/` | Pesos de la actividad 3.3 y ficha de verificación. |
| `data/` | Ejemplos, recortes de validación, clases y procedencia. |
| `Dockerfile` y `requirements.txt` | Construcción de la imagen y dependencias. |
| `ejecutar_docker.bat` | Construcción, pruebas y captura de evidencia en Windows. |
| `evidencia_local/` | Resultados de la ejecución nativa en CPU. |
| `evidencia_docker/` | Construcción, identificación de la imagen, predicciones, mediciones y resumen de la ejecución. |
| `reporte/` | PDF de ejecución y editable en LaTeX. |
| `docs/` | Alcance y verificación de las actividades. |

La salida del modelo ayuda a distinguir las dos clases entrenadas. Una foto con varias piezas requiere un recorte previo. La confianza corresponde a la puntuación del modelo para la clase elegida.
