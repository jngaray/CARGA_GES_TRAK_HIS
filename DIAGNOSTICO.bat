@echo off
echo ================================================================================
echo DIAGNOSTICO DE CONFIGURACION Y VERSION
echo ================================================================================
echo.

echo 1. VERIFICANDO VERSION DEL CODIGO (normalizacion DV)...
python -c "import scripts.ges_data_processor as gdp; import inspect; src = inspect.getsource(gdp.GESDataProcessor.format_rut); print('✓ Normalizacion DV implementada' if '.upper()' in src else '✗ FALTA normalizacion DV')"

echo.
echo 2. VERIFICANDO ARCHIVOS DE ENTRADA...
echo Archivos consulta:
dir /b inputs\reporte_consulta*.csv 2>nul || echo   (ninguno)
echo Archivos farmacia:
dir /b inputs\reporte_farmacia*.csv 2>nul || echo   (ninguno)
echo Archivos recetas:
dir /b inputs\recetas*.xls 2>nul || echo   (ninguno)

echo.
echo 3. CONTANDO REGISTROS EN ARCHIVOS DE ENTRADA...
python -c "import pandas as pd; df = pd.read_csv('inputs/reporte_farmacia_enero.csv', sep=';', encoding='latin-1', low_memory=False); print(f'Farmacia: {len(df)} registros')"
python -c "import pandas as pd; df = pd.read_csv('inputs/reporte_consulta_enero.csv', sep=';', encoding='latin-1', low_memory=False); print(f'Consultas: {len(df)} registros')"

echo.
echo 4. VERIFICANDO DV EN FARMACIA (k minuscula vs K mayuscula)...
python -c "import pandas as pd; df = pd.read_csv('inputs/reporte_farmacia_enero.csv', sep=';', encoding='latin-1', low_memory=False); k_min = len(df[df['DVPaciente'].astype(str).str.strip() == 'k']); k_may = len(df[df['DVPaciente'].astype(str).str.strip() == 'K']); print(f'DV=k minuscula: {k_min}'); print(f'DV=K mayuscula: {k_may}'); print(f'Total K: {k_min + k_may}')"

echo.
echo 5. VERIFICANDO ULTIMO COMMIT...
git log -1 --oneline

echo.
echo 6. VERIFICANDO CAMBIOS LOCALES...
git status --short

echo.
echo ================================================================================
echo FIN DEL DIAGNOSTICO
echo ================================================================================
echo.
echo Compartir este resultado con el equipo para diagnosticar diferencias
pause
