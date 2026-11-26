# Evidencia de la prueba en Docker

Ejecuta `ejecutar_docker.bat` con Docker Desktop abierto en Windows. El script guarda una carpeta por ejecución con los registros de construcción, el identificador de imagen, los tiempos y las predicciones. Usa la carpeta cuya prueba tenga `ESTADO_EJECUCION.txt`.

Copia el archivo `mediciones_docker.tex` de esa carpeta a `reporte/` y recompila `main.tex` para integrar las mediciones. En la copia entregada, las pruebas medidas están en `evidencia_local/` y corresponden a Python en Linux fuera de Docker.
