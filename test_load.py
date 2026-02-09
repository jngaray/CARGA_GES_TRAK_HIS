import sys
sys.path.insert(0, 'scripts')
from ges_data_processor import GESDataProcessor

processor = GESDataProcessor()
processor.setup_input_files()
processor.load_data()

print("\n\n=== RESULTADO CARGA RECETAS ===")
print(f"Tipo recetas_ges_df: {type(processor.recetas_ges_df)}")
if processor.recetas_ges_df is not None:
    print(f"Filas: {len(processor.recetas_ges_df)}")
    print(f"Columnas: {processor.recetas_ges_df.columns.tolist()[:5]}")
else:
    print("recetas_ges_df es None")

print("\n=== RESULTADO CARGA FARMACIA ===")
print(f"Tipo farmacia_df: {type(processor.farmacia_df)}")
if processor.farmacia_df is not None:
    print(f"Filas: {len(processor.farmacia_df)}")
else:
    print("farmacia_df es None")
