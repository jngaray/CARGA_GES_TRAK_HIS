@echo off
chcp 65001 >nul
cls

echo ================================================================
echo                    INSTALADOR SISTEMA GES V2.0
echo              Instituto Nacional de Enfermedades
echo             Respiratorias y Cirugia Toracica
echo ================================================================
echo.
echo ⭐ NUEVA VERSION 2.0 - FUNCIONALIDADES MEJORADAS
echo.
echo 🎯 MEJORAS INCLUIDAS:
echo    • Trazadoras múltiples (ASMA: 6, FIBROSIS: 4)
echo    • Verificación automática población GES
echo    • Eliminación de duplicados
echo    • Nueva lógica paliativos oncológicos
echo    • Archivos de casos para revisión
echo.
echo ================================================================
echo.

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

echo 🔍 Verificando Python...
%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado
    echo 💡 Por favor instale Python 3.7 o superior desde python.org o actualice la variable PYTHON_EXE en este archivo
    pause
    exit /b 1
) else (
    echo ✅ Python encontrado
    %PYTHON_EXE% --version
)

echo.
echo 📦 Instalando dependencias...
%PYTHON_EXE% -m pip install --upgrade pip
%PYTHON_EXE% -m pip install pandas openpyxl
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
) else (
    echo ✅ Dependencias instaladas correctamente
)

echo.
echo 📁 Verificando estructura de directorios...
if not exist "inputs" mkdir inputs
if not exist "outputs" mkdir outputs
if not exist "scripts" (
    echo ❌ Error: Directorio scripts no encontrado
    pause
    exit /b 1
)

echo ✅ Estructura de directorios verificada

echo.
echo 📋 Verificando archivos principales...
if not exist "scripts\ges_data_processor.py" (
    echo ❌ Error: Archivo principal no encontrado
    pause
    exit /b 1
)

if not exist "scripts\ges_advanced_analyzer.py" (
    echo ❌ Error: GUI no encontrada
    pause
    exit /b 1
)

echo ✅ Archivos principales encontrados

echo.
echo 🎯 Verificando archivos de entrada...
set missing_files=0

if not exist "inputs\RUT_pob_ges.xlsx" (
    echo ⚠️ Falta: inputs\RUT_pob_ges.xlsx
    set missing_files=1
)

if not exist "inputs\reporte_consulta_ago.csv" (
    echo ⚠️ Falta: inputs\reporte_consulta_ago.csv
    set missing_files=1
)

if not exist "inputs\reporte_farmacia_ago.csv" (
    echo ⚠️ Falta: inputs\reporte_farmacia_ago.csv
    set missing_files=1
)

if not exist "inputs\clasificacion_paliativos.csv" (
    echo ⚠️ Falta: inputs\clasificacion_paliativos.csv
    set missing_files=1
)

if %missing_files%==1 (
    echo.
    echo ⚠️ ARCHIVOS FALTANTES DETECTADOS
    echo 📁 Por favor coloque los archivos faltantes en la carpeta 'inputs'
    echo 💡 El sistema funcionará con los archivos disponibles
) else (
    echo ✅ Todos los archivos de entrada encontrados
)

echo.
echo 🧪 Probando sistema...
%PYTHON_EXE% -c "import sys; sys.path.append('scripts'); from ges_data_processor import GESDataProcessor; print('✅ Sistema funcionando correctamente')"
if errorlevel 1 (
    echo ❌ Error en prueba del sistema
    pause
    exit /b 1
)

echo.
echo ================================================================
echo                    ✅ INSTALACION COMPLETADA
echo ================================================================
echo.
echo 🚀 PARA EJECUTAR EL SISTEMA:
echo.
echo 🖥️ INTERFAZ GRAFICA (Recomendado):
echo    EJECUTAR_GUI.bat
echo.
echo 💻 LINEA DE COMANDOS:
echo    python sistema_completo_final.py
echo.
echo 📚 DOCUMENTACION:
echo    README_V2.md
echo.
echo ⭐ SISTEMA GES V2.0 LISTO PARA USO
echo ================================================================

pause