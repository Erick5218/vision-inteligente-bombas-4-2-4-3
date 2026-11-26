# Actividades 4.2 y 4.3 de Visión Inteligente

**Clasificación de impulsores y tazones de bombas sumergibles**

Erick Martín Rodríguez Baeza · 26ZPM034 · Docente I.MT. Luis Alberto Espejo Ponce

Se reutilizan los pesos de ResNet18 de la actividad 3.3 y el script de inferencia de la 4.1. El proyecto recibe recortes de piezas individuales y muestra la clase predicha y su confianza. El `Dockerfile` empaqueta el código, los pesos, las dependencias de CPU, los recortes de validación y una fotografía externa.

El dataset original de 25 fotografías y sus anotaciones se incluye en `data/origen/dataset_bombas.zip`. Los recortes en `data/validacion/` proceden de la partición de validación de 3.3. La copia del dataset queda disponible en el repositorio. La inferencia en el contenedor usa los recortes, la fotografía externa y los pesos entrenados.

## Ejecutar en Windows

1. Abre esta carpeta en PowerShell y comprueba `git --version` y `docker version`. El segundo comando debe mostrar `Client` y `Server`. Si falta Git, usa [Git para Windows](https://git-scm.com/install/windows). Si falta Docker, sigue la [instalación oficial de Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Abre Docker Desktop y usa contenedores Linux. Si el instalador pide habilitar o actualizar WSL 2, sigue su indicación de administrador y reinicia si Windows lo solicita. Vuelve a abrir Docker Desktop antes de continuar.
3. Si tienes una foto nueva, copia un JPG o PNG de una sola pieza en `data/propias/`.
4. Ejecuta desde PowerShell:

```powershell
.\ejecutar_docker.bat
```

En Linux el equivalente es `bash ejecutar_docker.sh`. La primera construcción descarga la imagen base y las bibliotecas. Una vez creada la imagen, la inferencia corre con CPU y archivos locales. Python viene dentro de la imagen.

Cada ejecución guarda una carpeta nueva en `evidencia_docker/`. Encontrarás la versión de Docker, el registro de construcción, el identificador de imagen, los CSV de predicciones y tiempos, el resumen JSON y la comparación con la actividad 3.3. La fotografía externa incluida se prueba siempre y su resultado se guarda en `externa/`. Si el script encuentra fotos propias, guarda sus resultados en `propias/`. `ESTADO_EJECUCION.txt` aparece cuando termina la comprobación.

Para demostrar una inferencia individual después de construir la imagen, ejecuta el comando siguiente desde PowerShell o Bash. La procedencia de la fotografía está en `data/prueba_externa/FUENTE.md`.

```text
docker run --rm vision-bombas:4.2 --imagen data/prueba_externa/impulsor_bomba_pozo.png
```

## Reporte y evidencia

El PDF incluido documenta la prueba en CPU realizada en Linux fuera de Docker. En esa prueba se conservaron las 33 decisiones de la actividad 3.3, con 32 aciertos. El registro original puede compararse con los CSV en `evidencia_local/`. La carpeta `evidencia_docker/` queda lista para recibir los resultados del equipo donde se ejecute el contenedor.

Una vez que el script termine, copia `mediciones_docker.tex` de la carpeta de esa ejecución sobre `reporte/mediciones_docker.tex`. Abre `reporte/main.tex` y compila con pdfLaTeX. En Overleaf, sube los archivos de `reporte/` junto con la carpeta `assets/`. El reporte conserva portada, texto y tablas editables. Agrega la URL privada en la definición de `\LigaRepositorio` en `main.tex` cuando la tengas. Usa los CSV y registros de Docker si el profesor solicita evidencia adicional.

El tiempo de procesamiento suma lectura, preparación, inferencia y posprocesamiento. En modo flujo, el tiempo de operación incluye las pausas de 0.1 s. Las 33 imágenes se reutilizan para comprobar consistencia. La foto externa prueba que el comando admite una entrada que quedó fuera del entrenamiento y de la validación.

## Publicar en un repositorio privado

Al descomprimir este paquete ya existe un repositorio Git local en la rama `main`. `git status` permite confirmarlo. Conserva los archivos de tu carpeta original y copia a esta cualquier foto nueva.

Para publicar, comprueba primero con `git remote -v` que la carpeta no tenga ya un remoto destinado a la entrega. Con [GitHub CLI](https://cli.github.com/) disponible, puedes iniciar sesión con `gh auth login --hostname github.com --web`. Cuando GitHub confirme la cuenta, ejecuta:

```powershell
gh repo create vision-inteligente-bombas-4-2-4-3 --private --source . --remote origin --push
gh repo view --json url,isPrivate
```

Si ya creaste el repositorio privado para esta misma entrega, usa su URL y revisa primero el historial de ese repositorio. Si es nuevo y está vacío, se puede conectar con `git remote add origin URL_DEL_REPOSITORIO_PRIVADO` y publicar con `git push -u origin main`. Comprueba que GitHub indique **Private** y que el profesor tenga acceso a la liga antes de compartirla. Si ya había un remoto configurado, usa el correspondiente a este proyecto.

Para incluir la evidencia final, revisa las carpetas `evidencia_docker/` y `reporte/`, agrega la ejecución exitosa y el reporte actualizado a un commit y súbelo al mismo repositorio.

## Archivos principales

| Archivo o carpeta | Contenido |
|---|---|
| `src/pipeline_inferencia.py` | Inferencia de la actividad 4.1. |
| `models/` | Pesos de la actividad 3.3 y ficha de verificación. |
| `data/` | Ejemplos, recortes de validación, clases y procedencia. |
| `Dockerfile` y `requirements.txt` | Construcción de la imagen y dependencias. |
| `ejecutar_docker.bat` | Construcción, pruebas y captura de evidencia en Windows. |
| `evidencia_local/` | Resultados de la ejecución nativa en CPU. |
| `evidencia_docker/` | Evidencia que genera el contenedor al ejecutar la prueba. |
| `reporte/` | PDF de referencia y editable en LaTeX. |
| `docs/` | Alcance y verificación de las actividades. |

La salida del modelo ayuda a distinguir las dos clases entrenadas. Una foto con varias piezas requiere un recorte previo. La confianza corresponde a la puntuación del modelo para la clase elegida.
