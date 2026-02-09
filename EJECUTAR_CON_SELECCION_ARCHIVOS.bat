@echo off
chcp 65001 > nul
cls
rem Cargar configuración central si existe
if exist "%~dp0config.bat" (
	call "%~dp0config.bat"
) else (
	rem Si no existe config.bat, usar la ruta por defecto incluida aquí
	set "PYTHON_EXE=C:\Users\mgalleguillos\AppData\Local\Programs\Python\Python313\python.exe"
)

if not exist "%PYTHON_EXE%" (
	echo ⚠️ Ruta de Python no encontrada: %PYTHON_EXE%
	echo Se intentará usar "python" desde PATH
	set "PYTHON_EXE=python"
)
echo.
echo ===============================================================
echo 🚀 SISTEMA GES - CON SELECCIÓN DINÁMICA DE ARCHIVOS
echo ===============================================================
echo.
echo Este script permite seleccionar automáticamente o manualmente
echo los archivos de consultas y farmacia que cambian cada mes.
echo.
echo Presiona cualquier tecla para continuar...
pause > nul

%PYTHON_EXE% EJECUTAR_CON_SELECCION_ARCHIVOS.py

echo.
echo Presiona cualquier tecla para cerrar...
pause > nul