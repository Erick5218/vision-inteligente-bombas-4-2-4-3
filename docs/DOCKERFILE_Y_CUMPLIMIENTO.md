# Dockerfile y revisión de requisitos

`FROM` selecciona Python 3.12 sobre Debian slim. `WORKDIR` fija `/app` como carpeta de ejecución. `COPY` incorpora requisitos, código, pesos y datos. `RUN` instala las bibliotecas fijadas y prepara la salida. `ENTRYPOINT` establece el script de inferencia; `CMD` aporta los argumentos de la demo por lote. Los argumentos escritos después del nombre de imagen sustituyen el comando por omisión. No se expone un puerto porque la entrada y salida son archivos.

La imagen base conserva la rama 3.12 y puede actualizar su revisión. `requirements.txt` fija dependencias directas; los paquetes transitivos pueden cambiar. El registro de construcción y `id_imagen.txt` identifican la imagen real utilizada. Una repetición exacta requeriría conservar esa imagen o fijar su digest y todas las dependencias después de la construcción verificada.

| Solicitud o criterio | Archivo o evidencia | Estado al preparar el paquete |
|---|---|---|
| Estructura mínima: modelo, script, requirements, README. | Raíz del paquete, `models/` y `src/`. | Preparada. |
| Dockerfile. | `Dockerfile`. | Preparado; construcción pendiente. |
| Simular despliegue con medición. | Scripts `ejecutar_docker` y resultados que generan. | Pendiente de ejecución en Docker. |
| Paquete profesional. | Proyecto autónomo con demo, datos y manual. | Preparado. |
| Evidencia de ejecución del contenedor. | Registros, identificador de imagen y resultados en `evidencia_docker/`. | Pendiente. |
| Dominio conceptual. | Objetivo, explicación de instrucciones y límites. | Documentado. |
| Desarrollo técnico. | Pipeline local comprobado; mismo modelo y script de 4.1. | Local comprobado; Docker pendiente. |
| Análisis de resultados. | Referencia CPU y comparación propuesta con ejecución Docker. | Referencia local; falta análisis del contenedor. |
| Presentación y entregables. | README, estructura, comandos y archivos editables. | Falta incorporar evidencia Docker para entrega completa. |

La ejecución local no demuestra que la imagen construya o arranque correctamente. No debe marcarse 4.2 como terminada hasta ejecutar el contenedor y revisar su salida. Un ensayo CPU en Docker cubre la alternativa de contenedor del cuaderno; no equivale a una prueba sobre un dispositivo edge físico.
