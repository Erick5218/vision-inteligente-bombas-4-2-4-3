# Evidencia de la prueba en Docker

Cada carpeta con `ESTADO_EJECUCION.txt` contiene una prueba completa. Incluye la versión del motor, la construcción, la huella de la imagen, los tiempos y las predicciones de lote, flujo y fotografía externa. La ejecución de referencia se hizo con Docker Engine en una máquina virtual Linux.

Para repetirla, ejecuta `ejecutar_docker.bat` con Docker Desktop abierto en Windows o `bash ejecutar_docker.sh` en Linux. El archivo `mediciones_docker.tex` de la ejecución sirve de referencia si actualizas la tabla en `reporte/main.tex`. En `evidencia_local/` están las mediciones de referencia en Python y CPU.
