import pandas as pd
import os
from pathlib import Path

# Rutas
antiguos_path = r"c:\Users\jarojas\Downloads\DISTRIBUCION_GES_V2\antiguos"
outputs_path = r"c:\Users\jarojas\Downloads\DISTRIBUCION_GES_V2\outputs"

print("=" * 80)
print("LEYENDO ARCHIVOS ANTIGUOS...")
print("=" * 80)

# Leer archivos antiguos
old_files = [
    "archivo_farmacia_ges_completo_old.xlsx",
    "archivo_farmacia_ges_completo_part2_old.xlsx",
    "archivo_farmacia_ges_completo_part3_old.xlsx",
    "archivo_farmacia_ges_completo_part4_old.xlsx"
]

dfs_old = []
for file in old_files:
    filepath = os.path.join(antiguos_path, file)
    if os.path.exists(filepath):
        try:
            df = pd.read_excel(filepath)
            dfs_old.append(df)
            print(f"✓ {file}: {len(df)} filas")
        except Exception as e:
            print(f"✗ {file}: Error - {e}")
    else:
        print(f"✗ {file}: No encontrado")

# Concatenar antiguos
df_old = pd.concat(dfs_old, ignore_index=True)
print(f"\nTotal archivos antiguos: {len(df_old)} filas\n")

print("=" * 80)
print("LEYENDO ARCHIVOS ACTUALES...")
print("=" * 80)

# Leer archivos actuales
current_files = [
    "archivo_farmacia_ges_completo.xlsx",
    "archivo_farmacia_ges_completo_part2.xlsx",
    "archivo_farmacia_ges_completo_part3.xlsx",
    "archivo_farmacia_ges_completo_part4.xlsx",
    "archivo_farmacia_ges_completo_part5.xlsx"
]

dfs_current = []
for file in current_files:
    filepath = os.path.join(outputs_path, file)
    if os.path.exists(filepath):
        try:
            df = pd.read_excel(filepath)
            dfs_current.append(df)
            print(f"✓ {file}: {len(df)} filas")
        except Exception as e:
            print(f"✗ {file}: Error - {e}")
    else:
        print(f"✗ {file}: No encontrado")

# Concatenar actuales
df_current = pd.concat(dfs_current, ignore_index=True)
print(f"\nTotal archivos actuales: {len(df_current)} filas\n")

print("=" * 80)
print("ANÁLISIS INICIAL")
print("=" * 80)
print(f"Filas en version antigua: {len(df_old)}")
print(f"Filas en version actual: {len(df_current)}")
print(f"Diferencia: {len(df_current) - len(df_old)} filas")

print(f"\nColumnas en version antigua: {list(df_old.columns)}")
print(f"Columnas en version actual: {list(df_current.columns)}")

# Mostrar primeras filas para entender estructura
print("\n" + "=" * 80)
print("PRIMERAS FILAS ANTIGUAS:")
print("=" * 80)
print(df_old.head(3))

print("\n" + "=" * 80)
print("PRIMERAS FILAS ACTUALES:")
print("=" * 80)
print(df_current.head(3))

# Búsqueda de columnas con RUT
rut_cols_old = [col for col in df_old.columns if 'rut' in col.lower() or 'paciente' in col.lower()]
rut_cols_current = [col for col in df_current.columns if 'rut' in col.lower() or 'paciente' in col.lower()]

med_cols_old = [col for col in df_old.columns if 'med' in col.lower() or 'drug' in col.lower() or 'farmaco' in col.lower()]
med_cols_current = [col for col in df_current.columns if 'med' in col.lower() or 'drug' in col.lower() or 'farmaco' in col.lower()]

print(f"\nColumnas con RUT (antiguo): {rut_cols_old}")
print(f"Columnas con RUT (actual): {rut_cols_current}")
print(f"\nColumnas con medicamento (antiguo): {med_cols_old}")
print(f"Columnas con medicamento (actual): {med_cols_current}")

# Normalizar RUTs (remover "k" para comparación)
def normalize_rut(rut):
    if pd.isna(rut):
        return ""
    rut_str = str(rut).upper().replace("-", "").replace("K", "")
    return rut_str

print("\n" + "=" * 80)
print("COMPARACIÓN DE RUTs ÚNICOS")
print("=" * 80)

if rut_cols_old and rut_cols_current:
    col_old = rut_cols_old[0]
    col_current = rut_cols_current[0]
    
    ruts_old = set(df_old[col_old].astype(str).unique())
    ruts_current = set(df_current[col_current].astype(str).unique())
    
    print(f"RUTs únicos (antiguo): {len(ruts_old)}")
    print(f"RUTs únicos (actual): {len(ruts_current)}")
    
    ruts_solo_old = ruts_old - ruts_current
    ruts_solo_current = ruts_current - ruts_old
    
    print(f"RUTs solo en versión antigua: {len(ruts_solo_old)}")
    print(f"RUTs solo en versión actual: {len(ruts_solo_current)}")
    
    if ruts_solo_old:
        print(f"  Ejemplo (primeros 5): {list(ruts_solo_old)[:5]}")
    if ruts_solo_current:
        print(f"  Ejemplo (primeros 5): {list(ruts_solo_current)[:5]}")

# Comparación de medicamentos
print("\n" + "=" * 80)
print("COMPARACIÓN DE MEDICAMENTOS ÚNICOS")
print("=" * 80)

if med_cols_old and med_cols_current:
    col_old = med_cols_old[0]
    col_current = med_cols_current[0]
    
    meds_old = set(df_old[col_old].astype(str).unique())
    meds_current = set(df_current[col_current].astype(str).unique())
    
    print(f"Medicamentos únicos (antiguo): {len(meds_old)}")
    print(f"Medicamentos únicos (actual): {len(meds_current)}")
    
    meds_solo_old = meds_old - meds_current
    meds_solo_current = meds_current - meds_old
    
    print(f"Medicamentos solo en versión antigua: {len(meds_solo_old)}")
    print(f"Medicamentos solo en versión actual: {len(meds_solo_current)}")
    
    if meds_solo_old:
        print(f"  Ejemplos (primeros 10):")
        for med in list(meds_solo_old)[:10]:
            print(f"    - {med}")
    
    if meds_solo_current:
        print(f"  Ejemplos (primeros 10):")
        for med in list(meds_solo_current)[:10]:
            print(f"    - {med}")

print("\n" + "=" * 80)
print("FIN DE COMPARACIÓN")
print("=" * 80)
