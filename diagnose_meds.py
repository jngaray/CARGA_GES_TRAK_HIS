import sys
sys.path.insert(0, 'scripts')
from ges_data_processor import GESDataProcessor
import pandas as pd

processor = GESDataProcessor()
processor.setup_input_files()
processor.load_data()

print("\n=== DIAGNÓSTICO MEDICAMENTOS ===\n")

# Combinar igual que procesar_medicamentos_para_carga
if processor.farmacia_df is not None and processor.recetas_ges_df is not None:
    if '_origen' not in processor.farmacia_df.columns:
        processor.farmacia_df['_origen'] = 'farmacia'
    
    df_combined = pd.concat([processor.farmacia_df, processor.recetas_ges_df], ignore_index=True)
    print(f"✅ Combinados: {len(df_combined)} registros")
    
    # Verifi car primer registro de cada fuente
    print(f"\n--- FARMACIA (primeros 2 registros) ---")
    farmacia_only = processor.farmacia_df.head(2)
    print(f"Columnas: {farmacia_only.columns.tolist()}")
    print(f"RUT_Combined: {farmacia_only['RUT_Combined'].tolist()}")
    print(f"FechaDespacho: {farmacia_only['FechaDespacho'].tolist()}")
    
    print(f"\n--- RECETAS (primeros 2 registros) ---")
    recetas_only = processor.recetas_ges_df.head(2)
    print(f"Columnas: {recetas_only.columns.tolist()}")
    print(f"RUT_Combined: {recetas_only['RUT_Combined'].tolist()}")
    print(f"FechaEmision: {recetas_only['FechaEmision'].tolist()}")
    
    # Verificar población GES
    ges_patients = set(
        processor.ges_df.apply(lambda r: processor.format_rut(r["RUT"], r.get("DV", "")), axis=1)
    )
    print(f"\n✓ Pacientes en GES: {len(ges_patients)}")
    
    # Filtrar GES
    df_ges = df_combined[df_combined["RUT_Combined"].isin(ges_patients)]
    print(f"✓ Medicamentos de pacientes GES: {len(df_ges)}")
    
    # Verificar conditions
    print(f"\n--- VERIFICACIÓN DE CONDITIONS ---")
    for rut in df_ges['RUT_Combined'].head(5):
        condition = processor.get_ges_condition(rut)
        print(f"RUT {rut}: condition = {condition}")
    
    # Contar medicamentos por origin
    print(f"\n--- POR ORIGEN ---")
    print(f"Farmacia: {len(df_combined[df_combined['_origen']=='farmacia'])}")
    print(f"Recetas: {len(df_combined[df_combined['_origen']=='recetas'])}")
