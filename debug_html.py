import pandas as pd
import os

os.chdir('inputs')
filepath = 'recetas05_02_2026 16_10_29.xls'

# Leer como HTML - TODAS las tablas
all_tables = pd.read_html(filepath)
print(f"Total de tablas HTML encontradas: {len(all_tables)}")

for idx, df in enumerate(all_tables):
    print(f"\nTabla {idx}: {len(df)} filas, {len(df.columns)} columnas")
    print(f"  Columnas: {df.columns.tolist()[:5]}")
    if len(df) > 0:
        print(f"  Primera fila: {df.iloc[0].tolist()[:3]}")

