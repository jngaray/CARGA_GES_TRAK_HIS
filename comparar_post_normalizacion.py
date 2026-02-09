import pandas as pd
import os

outputs_path = r"c:\Users\jarojas\Downloads\DISTRIBUCION_GES_V2\outputs"
antiguos_path = r"c:\Users\jarojas\Downloads\DISTRIBUCION_GES_V2\antiguos"

print("="*80)
print("COMPARACIÓN DESPUÉS DE NORMALIZACIÓN DE DV")
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

# Leer archivos nuevos
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

print(f"\nArchivos antiguos consolidados: {len(df_old)} filas")
print(f"Archivos nuevos consolidados: {len(df_current)} filas")
print(f"Diferencia: {len(df_current) - len(df_old)} filas")

# Normalizar DV a mayúsculas en ambos para comparación justa
df_old['DV'] = df_old['DV'].astype(str).str.upper()
df_current['DV'] = df_current['DV'].astype(str).str.upper()

print("\n" + "="*80)
print("DISTRIBUCIÓN DE DV (después de normalizar ambos a mayúsculas)")
print("="*80)

print("\nAntiguo:")
print(df_old['DV'].value_counts())

print("\nNuevo:")
print(df_current['DV'].value_counts())

# Crear llaves para comparación
df_old['KEY'] = df_old['RUT'].astype(str) + '|' + df_old['PRESTACION'].astype(str) + '|' + df_old['TIPO'].astype(str)
df_current['KEY'] = df_current['RUT'].astype(str) + '|' + df_current['PRESTACION'].astype(str) + '|' + df_current['TIPO'].astype(str)

keys_old = set(df_old['KEY'].unique())
keys_current = set(df_current['KEY'].unique())

keys_solo_old = keys_old - keys_current
keys_solo_current = keys_current - keys_old

print("\n" + "="*80)
print("COMPARACIÓN DE REGISTROS")
print("="*80)

print(f"Registros únicos (antiguo): {len(keys_old)}")
print(f"Registros únicos (nuevo): {len(keys_current)}")
print(f"Registros en común: {len(keys_old & keys_current)}")

print(f"\n✅ Registros PERDIDOS (antes vs ahora): {len(keys_solo_old)}")
print(f"✅ Registros NUEVOS (antes vs ahora): {len(keys_solo_current)}")

if len(keys_solo_old) > 0:
    print(f"\n⚠️ TODAVÍA HAY REGISTROS PERDIDOS: {len(keys_solo_old)}")
    print("Ejemplos de registros perdidos:")
    for i, key in enumerate(list(keys_solo_old)[:5]):
        rut, pres, tipo = key.split('|')
        old_rows = df_old[df_old['KEY'] == key]
        dv = old_rows['DV'].values[0] if len(old_rows) > 0 else 'N/A'
        print(f"  RUT {rut}-{dv} | PREST: {pres}")
else:
    print(f"\n✅✅✅ EXCELENTE: NO HAY REGISTROS PERDIDOS")

# Comparación de RUTs
print("\n" + "="*80)
print("COMPARACIÓN DE RUTs")
print("="*80)

ruts_old = set(df_old['RUT'].astype(str).unique())
ruts_current = set(df_current['RUT'].astype(str).unique())

ruts_solo_old = ruts_old - ruts_current
ruts_solo_current = ruts_current - ruts_old

print(f"RUTs únicos (antiguo): {len(ruts_old)}")
print(f"RUTs únicos (nuevo): {len(ruts_current)}")
print(f"RUTs PERDIDOS: {len(ruts_solo_old)}")
print(f"RUTs NUEVOS: {len(ruts_solo_current)}")

if len(ruts_solo_old) > 0:
    print(f"\n⚠️ RUTs perdidos: {sorted(ruts_solo_old)}")

# Comparación de DV='K' específicamente
print("\n" + "="*80)
print("ANÁLISIS ESPECÍFICO DE DV='K'")
print("="*80)

k_old = len(df_old[df_old['DV'] == 'K'])
k_new = len(df_current[df_current['DV'] == 'K'])

print(f"Registros con DV='K' (antiguo): {k_old}")
print(f"Registros con DV='K' (nuevo): {k_new}")
print(f"Diferencia: {k_new - k_old}")

if k_new > k_old:
    print(f"\n✅✅✅ ÉXITO: Se recuperaron {k_new - k_old} registros con DV='K'")
elif k_new == k_old:
    print(f"\n⚠️ Se mantiene igual cantidad de DV='K'")
else:
    print(f"\n❌ Se perdieron {k_old - k_new} registros con DV='K'")

print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80)
if len(keys_solo_old) == 0 and k_new > k_old:
    print("✅✅✅ TODOS LOS PROBLEMAS HAN SIDO CORREGIDOS")
    print(f"✅ Se recuperaron {k_new - k_old} registros con DV='K'")
    print(f"✅ No hay registros perdidos")
elif len(keys_solo_old) == 0:
    print("✅ No hay registros perdidos")
    print(f"⚠️ Pero DV='K' no cambió significativamente")
else:
    print(f"❌ Todavía hay {len(keys_solo_old)} registros perdidos")
    print("Se debe investigar si la normalización se aplicó correctamente")
