@echo off
echo Limpiando archivos de salida antiguos...
echo.

if exist outputs\archivo_farmacia_ges_completo*.xlsx (
    echo Eliminando archivos archivo_farmacia_ges_completo*.xlsx...
    del /Q outputs\archivo_farmacia_ges_completo*.xlsx
)

if exist outputs\archivo_consultas_ges_completo*.xlsx (
    echo Eliminando archivos archivo_consultas_ges_completo*.xlsx...
    del /Q outputs\archivo_consultas_ges_completo*.xlsx
)

if exist outputs\ARCHIVO_CRUCE*.csv (
    echo Eliminando archivos ARCHIVO_CRUCE*.csv...
    del /Q outputs\ARCHIVO_CRUCE*.csv
)

if exist outputs\REPORTE*.txt (
    echo Eliminando reportes...
    del /Q outputs\REPORTE*.txt
)

if exist outputs\ANALISIS*.txt (
    echo Eliminando análisis...
    del /Q outputs\ANALISIS*.txt
)

if exist outputs\CARGA*.xlsx (
    echo Eliminando archivos de carga...
    del /Q outputs\CARGA*.xlsx
)

if exist outputs\FARMACIA_CONSOLIDATED*.xlsx (
    echo Eliminando consolidados de comparación...
    del /Q outputs\FARMACIA_CONSOLIDATED*.xlsx
)

if exist outputs\REGISTROS_PERDIDOS*.xlsx (
    echo Eliminando archivos de registros perdidos...
    del /Q outputs\REGISTROS_PERDIDOS*.xlsx
)

echo.
echo ✓ Limpieza completa
echo.
echo Ahora puedes ejecutar el análisis con datos limpios
pause
