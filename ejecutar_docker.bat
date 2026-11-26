@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0" || exit /b 1

for /f %%T in ('powershell.exe -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "MARCA=%%T"
if not defined MARCA exit /b 1
set "EVID=%CD%\evidencia_docker\%MARCA%_%RANDOM%"
mkdir "%EVID%" || exit /b 1

docker version > "%EVID%\version_docker.txt" 2>&1
if errorlevel 1 (
    type "%EVID%\version_docker.txt"
    echo Abre Docker Desktop y espera a que inicie el motor.
    goto :fallo
)
docker info --format "{{.OSType}}" > "%EVID%\tipo_contenedor.txt" 2>&1
if errorlevel 1 goto :fallo
findstr /x /c:"linux" "%EVID%\tipo_contenedor.txt" >nul
if errorlevel 1 (
    echo Selecciona contenedores Linux en Docker Desktop.
    goto :fallo
)

echo Construyendo vision-bombas:4.2. Consulta construccion.txt si tarda.
docker build -t vision-bombas:4.2 . > "%EVID%\construccion.txt" 2>&1
if errorlevel 1 (
    type "%EVID%\construccion.txt"
    goto :fallo
)
docker image inspect --format "{{.Id}}" vision-bombas:4.2 > "%EVID%\id_imagen.txt" 2>&1
if errorlevel 1 goto :fallo
set "IMAGEN="
set /p "IMAGEN=" < "%EVID%\id_imagen.txt"
if not defined IMAGEN goto :fallo

docker run --rm --network none --mount "type=bind,source=%EVID%,target=/app/outputs" "%IMAGEN%" --carpeta data/validacion --modo lote --lote 8 --salida outputs/lote > "%EVID%\ejecucion_lote.txt" 2>&1
if errorlevel 1 goto :fallo
docker run --rm --network none --mount "type=bind,source=%EVID%,target=/app/outputs" "%IMAGEN%" --carpeta data/validacion --modo flujo --intervalo 0.1 --salida outputs/flujo > "%EVID%\ejecucion_flujo.txt" 2>&1
if errorlevel 1 goto :fallo

docker run --rm --network none --mount "type=bind,source=%EVID%,target=/app/outputs" "%IMAGEN%" --imagen data/prueba_externa/impulsor_bomba_pozo.png --salida outputs/externa > "%EVID%\ejecucion_externa.txt" 2>&1
if errorlevel 1 goto :fallo

set "FOTO_PROPIA="
for %%F in (data\propias\*.jpg data\propias\*.jpeg data\propias\*.png data\propias\*.bmp data\propias\*.tif data\propias\*.tiff) do if exist "%%~fF" set "FOTO_PROPIA=1"
if defined FOTO_PROPIA (
    docker run --rm --network none --mount "type=bind,source=%CD%\data\propias,target=/app/fotos_propias,readonly" --mount "type=bind,source=%EVID%,target=/app/outputs" "%IMAGEN%" --carpeta fotos_propias --salida outputs/propias > "%EVID%\ejecucion_propias.txt" 2>&1
    if errorlevel 1 goto :fallo
    type "%EVID%\propias\predicciones.csv"
) else (
    echo Sin fotos propias adicionales en esta ejecucion. > "%EVID%\ejecucion_propias.txt"
)

docker run --rm --network none --mount "type=bind,source=%EVID%,target=/app/outputs" --entrypoint python "%IMAGEN%" src/resumir_evidencia.py outputs > "%EVID%\verificacion.txt" 2>&1
if errorlevel 1 goto :fallo
echo Ejecucion real de Docker terminada: %DATE% %TIME% > "%EVID%\ESTADO_EJECUCION.txt"
type "%EVID%\ejecucion_lote.txt"
type "%EVID%\ejecucion_externa.txt"
type "%EVID%\verificacion.txt"
echo Evidencia disponible en "%EVID%".
exit /b 0

:fallo
echo La prueba quedo incompleta. Revisa los registros en "%EVID%".
exit /b 1
