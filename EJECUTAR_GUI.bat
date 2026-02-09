@echo off
chcp 65001 >nul
cls

echo ================================================================
echo                    SISTEMA GES - GUI PRINCIPAL
echo              Instituto Nacional de Enfermedades
echo             Respiratorias y Cirugia Toracica
echo ================================================================
echo.
echo 🚀 INICIANDO INTERFAZ GRAFICA...
echo.
echo ✨ FUNCIONALIDADES DISPONIBLES:
echo    📊 Análisis completo de pacientes GES
echo    💊 Procesamiento inteligente de medicamentos
echo    🏥 Gestión de consultas y especialidades
echo    📄 Generación de archivos de carga
echo    🎯 Integración con Arancel GES 2025
echo.
echo ================================================================

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

%PYTHON_EXE% scripts\ges_advanced_analyzer.py

if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar el sistema
    echo 💡 Verifique que Python esté instalado correctamente
    pause
) else (
    echo.
    echo ✅ Sistema ejecutado correctamente
)

pause