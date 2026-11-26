# Dockerfile y revisión de requisitos

`FROM` selecciona Python 3.12 sobre Debian slim. `WORKDIR` fija `/app` como carpeta de ejecución. `COPY` incorpora requisitos, código, pesos y datos de inferencia. `RUN` instala las bibliotecas fijadas y prepara la salida. `ENTRYPOINT` establece el script de inferencia y `CMD` aporta los argumentos de la demo por lote. Los argumentos escritos después del nombre de imagen sustituyen el comando por omisión.

La imagen base conserva la rama 3.12 y `requirements.txt` fija las dependencias directas. El registro de construcción y `id_imagen.txt` identifican la imagen que se usó para las pruebas. BuildKit permite montar de forma temporal los certificados del entorno de construcción cuando se usa un proxy.

| Solicitud o criterio | Archivo o evidencia | Verificación |
|---|---|---|
| Estructura mínima: modelo, script, requirements, README. | Raíz del paquete, `models/` y `src/`. | Preparada. |
| Dockerfile. | `Dockerfile`. | Imagen construida con Docker Engine. |
| Simular despliegue con medición. | CSV y JSON de lote y flujo. | Tiempos medidos en el contenedor. |
| Paquete profesional. | Dataset, modelo, pipeline y manual. | Integrados en el repositorio. |
| Evidencia de ejecución del contenedor. | Registros, identificador de imagen y resultados en `evidencia_docker/`. | Incluye lote, flujo y fotografía externa. |
| Dominio conceptual. | Objetivo, explicación de instrucciones y límites. | Documentado. |
| Desarrollo técnico. | Modelo y script de 4.1. | Verificación de huellas y ejecución en Docker. |
| Análisis de resultados. | Referencia CPU, mediciones de Docker y foto externa. | Incluidos en el PDF. |
| Presentación y entregables. | README, repositorio y reporte breve. | Entrega conjunta en la actividad 4.3. |

El cuaderno de la Unidad 4 admite la simulación de despliegue con contenedor. Las mediciones de Docker corresponden a una máquina virtual Linux con CPU emulada.
