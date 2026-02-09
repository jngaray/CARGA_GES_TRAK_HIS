import pandas as pd
import os
from pathlib import Path

# Rutas
antiguos_path = r"c:\Users\jarojas\Downloads\DISTRIBUCION_GES_V2\antiguos"
outputs_path = r"c:\Users\jarojas\Downloads\DISTRIBUCION_GES_V2\outputs"

print("="*80)
print("LEYENDO Y CONSOLIDANDO ARCHIVOS...")
print("="*80)

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
        df = pd.read_excel(filepath)
        dfs_old.append(df)

df_old = pd.concat(dfs_old, ignore_index=True)

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
        df = pd.read_excel(filepath)
        dfs_current.append(df)

df_current = pd.concat(dfs_current, ignore_index=True)

print(f"Archivos antiguos consolidados: {len(df_old)} filas")
print(f"Archivos actuales consolidados: {len(df_current)} filas")
print(f"Diferencia: {len(df_current) - len(df_old)} filas ({((len(df_current) / len(df_old) - 1) * 100):.1f}% más)\n")

print("="*80)
print("ANÁLISIS DE RUTs (sin considerar DV)")
print("="*80)

# Crear identificador único: RUT + PRESTACION + TIPO (sin DV)
df_old['KEY'] = df_old['RUT'].astype(str) + '|' + df_old['PRESTACION'].astype(str) + '|' + df_old['TIPO'].astype(str)
df_current['KEY'] = df_current['RUT'].astype(str) + '|' + df_current['PRESTACION'].astype(str) + '|' + df_current['TIPO'].astype(str)

keys_old = set(df_old['KEY'].unique())
keys_current = set(df_current['KEY'].unique())

print(f"Registros únicos (antiguo): {len(keys_old)}")
print(f"Registros únicos (actual): {len(keys_current)}")
print(f"Registros en común: {len(keys_old & keys_current)}")

keys_solo_old = keys_old - keys_current
keys_solo_current = keys_current - keys_old

print(f"\nRegistros SOLO en versión antigua: {len(keys_solo_old)}")
print(f"Registros SOLO en versión actual: {len(keys_solo_current)}\n")

# Mostrar ejemplos
if keys_solo_old:
    print("Ejemplos de registros perdidos (antiguos sin equivalente en actual):")
    for i, key in enumerate(list(keys_solo_old)[:5]):
        rut, pres, tipo = key.split('|')
        old_rows = df_old[df_old['KEY'] == key]
        print(f"  {key} - DV: {old_rows['DV'].values[0] if len(old_rows) > 0 else 'N/A'} - Fecha: {old_rows['FECHA'].values[0] if len(old_rows) > 0 else 'N/A'}")

print()

if keys_solo_current:
    print("Ejemplos de registros nuevos (actuales sin equivalente en antigua):")
    for i, key in enumerate(list(keys_solo_current)[:5]):
        rut, pres, tipo = key.split('|')
        new_rows = df_current[df_current['KEY'] == key]
        print(f"  {key} - DV: {new_rows['DV'].values[0] if len(new_rows) > 0 else 'N/A'} - Fecha: {new_rows['FECHA'].values[0] if len(new_rows) > 0 else 'N/A'}")

print("\n" + "="*80)
print("ANÁLISIS POR RUT (sin considerar DV)")
print("="*80)

ruts_old = set(df_old['RUT'].astype(str).unique())
ruts_current = set(df_current['RUT'].astype(str).unique())

ruts_solo_old = ruts_old - ruts_current
ruts_solo_current = ruts_current - ruts_old

print(f"RUTs únicos (antiguo): {len(ruts_old)}")
print(f"RUTs únicos (actual): {len(ruts_current)}")
print(f"RUTs PERDIDOS (solo en antigua): {len(ruts_solo_old)}")
print(f"RUTs NUEVOS (solo en actual): {len(ruts_solo_current)}\n")

# Análisis de PRESTACIÓN por tipo
print("="*80)
print("ANÁLISIS DE PRESTACIONES ÚNICAS")
print("="*80)

pres_old = set(df_old['PRESTACION'].astype(str).unique())
pres_current = set(df_current['PRESTACION'].astype(str).unique())

print(f"Prestaciones únicas (antiguo): {len(pres_old)}")
print(f"Prestaciones únicas (actual): {len(pres_current)}")

pres_solo_old = pres_old - pres_current
pres_solo_current = pres_current - pres_old

print(f"Prestaciones perdidas: {pres_solo_old if pres_solo_old else 'Ninguna'}")
print(f"Prestaciones nuevas: {pres_solo_current if pres_solo_current else 'Ninguna'}")

# Estadísticas de distribución
print("\n" + "="*80)
print("DISTRIBUCIÓN POR TIPO")
print("="*80)

print("\nAntiguo:")
print(df_old['TIPO'].value_counts())

print("\nActual:")
print(df_current['TIPO'].value_counts())

# Análisis de fechas
print("\n" + "="*80)
print("ANÁLISIS DE FECHAS")
print("="*80)

print(f"Rango de fechas (antiguo): {df_old['FECHA'].min()} a {df_old['FECHA'].max()}")
print(f"Rango de fechas (actual): {df_current['FECHA'].min()} a {df_current['FECHA'].max()}")

# Contar registros por PS-FAM
print("\n" + "="*80)
print("ANÁLISIS POR PS-FAM (CENTRO DE SALUD)")
print("="*80)

psfam_old = df_old.groupby('PS-FAM ').size().sort_values(ascending=False)
psfam_current = df_current.groupby('PS-FAM ').size().sort_values(ascending=False)

print(f"\nCentros en versión antigua: {len(psfam_old)}")
print(f"Centros en versión actual: {len(psfam_current)}")

print("\nTop 5 centros (antiguo):")
print(psfam_old.head())

print("\nTop 5 centros (actual):")
print(psfam_current.head())

# Guardas los datos consolidados para referencia
df_old.to_excel(os.path.join(outputs_path, 'FARMACIA_CONSOLIDATED_OLD.xlsx'), index=False)
df_current.to_excel(os.path.join(outputs_path, 'FARMACIA_CONSOLIDATED_CURRENT.xlsx'), index=False)

print("\n" + "="*80)
print("Archivos consolidados guardados en outputs/")
print("="*80)
