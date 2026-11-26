@echo off
setlocal
cd /d "%~dp0"
python src\pipeline_inferencia.py --carpeta data\ejemplos --modo lote --salida outputs\demo
if errorlevel 1 exit /b 1
echo Demo completada. Revisa outputs\demo.
