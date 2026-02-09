import sys
sys.path.insert(0, 'scripts')
from ges_data_processor import GESDataProcessor
import pandas as pd

processor = GESDataProcessor()
processor.setup_input_files()
processor.load_data()

print("\n=== DIAGNÓSTICO RUT ===\n")

# Ver los RUTs en GES
ges_ruts_sample = processor.ges_df['RUT'].head(10).tolist()
print(f"Muestra de RUTs en GES:")
for rut in ges_ruts_sample:
    print(f"  {rut} (tipo: {type(rut).__name__})")

# Ver los RUTs en farmacia
farm_ruts = processor.farmacia_df[['RUT_Combined', 'RutPaciente']].head(5)
print(f"\nMuestra de RUTs en Farmacia:")
print(farm_ruts)

# Ver los RUTs en recetas
recetas_ruts = processor.recetas_ges_df[['RUT_Combined', 'RutPaciente']].head(5)
print(f"\nMuestra de RUTs en Recetas:")
print(recetas_ruts)

# Intentar matching
print(f"\n=== INTENTO DE MATCHING ===")
# Crear conjunto GES con ambas versiones
ges_set = set()
for _, row in processor.ges_df.iterrows():
    rut_num = row['RUT']
    dv = row.get('DV', '')
    # Agregar ambas versiones
    ges_set.add(f"{rut_num}-{dv}")
    ges_set.add(str(rut_num))

print(f"Total RUTs en GES set: {len(ges_set)}")

# Probar algunos medicamentos
farm_sample = processor.farmacia_df['RUT_Combined'].unique()[:5]
print(f"\nIntentando matching Farmacia → GES:")
for rut in farm_sample:
    match = rut in ges_set
    print(f"  {rut}: {match}")

recetas_sample = processor.recetas_ges_df['RUT_Combined'].unique()[:5]
print(f"\nIntentando matching Recetas → GES:")
for rut in recetas_sample:
    match = rut in ges_set
    print(f"  {rut}: {match}")
