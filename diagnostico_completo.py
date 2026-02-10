import pandas as pd
import sys
import os

print("="*80)
print("DIAGNÓSTICO COMPLETO DEL SISTEMA")
print("="*80)

# Verificar rutas absolutas
sys.path.insert(0, 'scripts')
from ges_data_processor import GESDataProcessor

print("\n1. RUTAS DEL SISTEMA")
print("-"*80)
processor = GESDataProcessor()
print(f"📁 Base Path: {processor.base_path}")
print(f"📥 Inputs Path: {processor.inputs_path}")
print(f"📤 Outputs Path: {processor.outputs_path}")
print(f"🐍 Script ejecutándose desde: {os.path.abspath(__file__)}")
print(f"🔧 Directorio actual: {os.getcwd()}")

print("\n2. VERSIONES DE SOFTWARE")
print("-"*80)
print(f"Python: {sys.version}")
print(f"Pandas: {pd.__version__}")
try:
    import openpyxl
    print(f"Openpyxl: {openpyxl.__version__}")
except:
    print("Openpyxl: NO INSTALADO")

print("\n3. VERIFICANDO NORMALIZACIÓN EN CÓDIGO")
print("-"*80)
import ges_data_processor as gdp
import inspect
src = inspect.getsource(gdp.GESDataProcessor.format_rut)
if '.upper()' in src:
    print("✓ format_rut() tiene normalización .upper()")
else:
    print("✗ format_rut() NO tiene normalización .upper()")

src_load = inspect.getsource(gdp.GESDataProcessor.load_csv_safely)
if '.upper()' in src_load or 'normalize_dv' in src_load:
    print("✓ load_csv_safely() tiene normalización DV")
else:
    print("✗ load_csv_safely() NO tiene normalización DV")

src_normalize = inspect.getsource(gdp.GESDataProcessor.normalize_dv_in_dataframe)
print(f"✓ normalize_dv_in_dataframe() existe ({len(src_normalize)} caracteres)")

print("\n4. ARCHIVOS DE ENTRADA")
print("-"*80)
if os.path.exists('inputs/reporte_farmacia_enero.csv'):
    df_farm = pd.read_csv('inputs/reporte_farmacia_enero.csv', sep=';', encoding='latin-1', low_memory=False)
    print(f"✓ reporte_farmacia_enero.csv: {len(df_farm)} registros")
    
    k_min = len(df_farm[df_farm['DVPaciente'].astype(str).str.strip() == 'k'])
    k_may = len(df_farm[df_farm['DVPaciente'].astype(str).str.strip() == 'K'])
    print(f"  - DV='k' (minúscula): {k_min}")
    print(f"  - DV='K' (mayúscula): {k_may}")
    print(f"  - Total 'K': {k_min + k_may}")
else:
    print("✗ reporte_farmacia_enero.csv NO EXISTE")

if os.path.exists('inputs/reporte_consulta_enero.csv'):
    df_cons = pd.read_csv('inputs/reporte_consulta_enero.csv', sep=';', encoding='latin-1', low_memory=False)
    print(f"✓ reporte_consulta_enero.csv: {len(df_cons)} registros")
else:
    print("✗ reporte_consulta_enero.csv NO EXISTE")

print("\n5. ARCHIVOS EN CARPETA ANTIGUOS/")
print("-"*80)
if os.path.exists('antiguos'):
    files = os.listdir('antiguos')
    print(f"Archivos encontrados: {len(files)}")
    for f in sorted(files):
        if f.endswith('.xlsx'):
            try:
                df = pd.read_excel(os.path.join('antiguos', f))
                print(f"  - {f}: {len(df)} filas")
            except:
                print(f"  - {f}: ERROR al leer")
else:
    print("✗ Carpeta antiguos/ NO EXISTE")

print("\n6. ARCHIVOS EN CARPETA OUTPUTS/ (últimos generados)")
print("-"*80)
if os.path.exists('outputs'):
    files = [f for f in os.listdir('outputs') if f.startswith('archivo_farmacia_ges_completo') and f.endswith('.xlsx')]
    files.sort(key=lambda x: os.path.getmtime(os.path.join('outputs', x)), reverse=True)
    
    if files:
        print(f"Archivos más recientes (top 5):")
        for f in files[:5]:
            path = os.path.join('outputs', f)
            mtime = os.path.getmtime(path)
            from datetime import datetime
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            try:
                df = pd.read_excel(path)
                print(f"  - {f}: {len(df)} filas | Modificado: {mtime_str}")
            except:
                print(f"  - {f}: ERROR al leer | Modificado: {mtime_str}")
    else:
        print("  No hay archivos archivo_farmacia_ges_completo*.xlsx")
else:
    print("✗ Carpeta outputs/ NO EXISTE")

print("\n7. SIMULACIÓN DE CARGA CON NORMALIZACIÓN")
print("-"*80)
if os.path.exists('inputs/reporte_farmacia_enero.csv'):
    processor = gdp.GESDataProcessor(base_path=os.getcwd(), auto_select_files=False)
    
    # Cargar farmacia
    df_test = processor.load_csv_safely('inputs/reporte_farmacia_enero.csv', separator=';')
    print(f"Después de load_csv_safely: {len(df_test)} filas")
    
    # Normalizar
    df_test = processor.normalize_dv_in_dataframe(df_test)
    
    # Contar K
    k_total = len(df_test[df_test['DVPaciente'].astype(str).str.strip() == 'K'])
    k_min_after = len(df_test[df_test['DVPaciente'].astype(str).str.strip() == 'k'])
    
    print(f"Después de normalizar:")
    print(f"  - DV='K' (mayúscula): {k_total}")
    print(f"  - DV='k' (minúscula): {k_min_after}")
    
    if k_min_after == 0 and k_total > 3000:
        print("  ✓ NORMALIZACIÓN FUNCIONANDO CORRECTAMENTE")
    else:
        print("  ✗ PROBLEMA CON NORMALIZACIÓN")

print("\n8. RESUMEN")
print("-"*80)
print("Si tu colega obtiene resultados diferentes:")
print("  1. VERIFICAR QUE LA RUTA outputs_path SEA LA CORRECTA")
print("  2. Comparar versiones de Pandas")
print("  3. Verificar que carpeta outputs/ esté VACÍA antes de ejecutar")
print("  4. Verificar que carpeta antiguos/ tenga los mismos archivos")
print("  5. Ejecutar LIMPIAR_OUTPUTS.bat antes de análisis")
print("\n⚠️ IMPORTANTE: Verificar que outputs_path apunte a:")
print(f"   {processor.outputs_path}")
print("="*80)
