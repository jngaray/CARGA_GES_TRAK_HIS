"""
Test para verificar que la normalización de DV funciona correctamente
"""
import pandas as pd
import os
import sys

# Agregar scripts al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from ges_data_processor import GESDataProcessor

# Crear instancia
processor = GESDataProcessor(
    base_path=r"c:\Users\jarojas\Downloads\DISTRIBUCION_GES_V2",
    auto_select_files=False
)

# Leer archivos antiguos para comparación
print("="*80)
print("PRUEBA DE NORMALIZACIÓN DE DV")
print("="*80)

# Leer versión antigua consolidada
df_old_consolidated = pd.read_excel(r"c:\Users\jarojas\Downloads\DISTRIBUCION_GES_V2\outputs\FARMACIA_CONSOLIDATED_OLD.xlsx")

print(f"\nVersión antigua consolidada: {len(df_old_consolidated)} filas")
print(f"DV='K': {len(df_old_consolidated[df_old_consolidated['DV'] == 'K'])}")
print(f"DV='k': {len(df_old_consolidated[df_old_consolidated['DV'] == 'k'])}")

# Ahora probar cargando con processor (que tiene normalización)
print("\n" + "="*80)
print("CARGANDO DATOS CON NORMALIZACIÓN...")
print("="*80)

# Cargar farmacia directamente
farmacia_file = r"c:\Users\jarojas\Downloads\DISTRIBUCION_GES_V2\inputs\reporte_farmacia_enero.csv"
if os.path.exists(farmacia_file):
    df_farmacia = processor.load_csv_safely(farmacia_file, separator=";")
    print(f"\nFarmacia cargada: {len(df_farmacia)} filas")
    
    # Mostrar distribución de DV ANTES de normalización
    print("\nDV antes de normalización:")
    print(df_farmacia['DVPaciente'].value_counts().head(15))
    
    # Aplicar normalización
    df_farmacia = processor.normalize_dv_in_dataframe(df_farmacia)
    print("\nDV después de normalización:")
    print(df_farmacia['DVPaciente'].value_counts().head(15))
    
    # Crear RUT_Combined
    df_farmacia['RUT_Combined'] = [
        processor.format_rut(row["RutPaciente"], row["DVPaciente"])
        for _, row in df_farmacia.iterrows()
    ]
    
    print(f"\nRUT_Combined creados: {len(df_farmacia[df_farmacia['RUT_Combined'].notna()])} válidos")
    
    # Mostrar ejemplos de RUTs con K
    k_ruts = df_farmacia[df_farmacia['RUT_Combined'].str.contains('-K', na=False)]['RUT_Combined'].unique()
    print(f"\nEjemplos de RUTs con -K: {list(k_ruts)[:5]}")
    
else:
    print(f"❌ Archivo no encontrado: {farmacia_file}")

print("\n" + "="*80)
print("✅ TEST COMPLETADO")
print("="*80)
