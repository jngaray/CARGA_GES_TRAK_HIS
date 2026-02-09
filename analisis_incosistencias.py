import pandas as pd
import os

# Rutas
antiguos_path = r"c:\Users\jarojas\Downloads\DISTRIBUCION_GES_V2\antiguos"
outputs_path = r"c:\Users\jarojas\Downloads\DISTRIBUCION_GES_V2\outputs"

print("="*80)
print("ANÁLISIS DETALLADO DE INCONSISTENCIAS")
print("="*80)

# Leer archivos consolidados (ya existen del script anterior)
df_old = pd.read_excel(os.path.join(outputs_path, 'FARMACIA_CONSOLIDATED_OLD.xlsx'))
df_current = pd.read_excel(os.path.join(outputs_path, 'FARMACIA_CONSOLIDATED_CURRENT.xlsx'))

# Crear llaves
df_old['KEY'] = df_old['RUT'].astype(str) + '|' + df_old['PRESTACION'].astype(str) + '|' + df_old['TIPO'].astype(str)
df_current['KEY'] = df_current['RUT'].astype(str) + '|' + df_current['PRESTACION'].astype(str) + '|' + df_current['TIPO'].astype(str)

keys_old = set(df_old['KEY'].unique())
keys_current = set(df_current['KEY'].unique())

keys_solo_old = keys_old - keys_current
keys_solo_current = keys_current - keys_old

# ============================================================================
# 1. ANÁLISIS DE REGISTROS PERDIDOS
# ============================================================================
print("\n1️⃣ REGISTROS PERDIDOS (en antigua pero NO en actual)")
print("="*80)

df_lost = df_old[df_old['KEY'].isin(keys_solo_old)].copy()
print(f"Total de registros perdidos: {len(df_lost)}")
print(f"RUTs únicos en perdidos: {df_lost['RUT'].nunique()}")

# Análisis por DV
print("\nDistribución de DV en registros perdidos:")
print(df_lost['DV'].value_counts().to_string())

# Análisis por Prestación
print("\nDistribución de PRESTACIÓN en registros perdidos:")
print(df_lost['PRESTACION'].value_counts().to_string())

# Mostrar todos los registros perdidos
print("\n📋 LISTA COMPLETA DE REGISTROS PERDIDOS:")
print("-"*80)
for idx, row in df_lost.iterrows():
    print(f"RUT: {row['RUT']}-{row['DV']} | PREST: {row['PRESTACION']} | FECHA: {row['FECHA']} | PS-FAM: {row['PS-FAM ']} | ESPECIALIDAD: {row['ESPECIALIDAD']}")

# ============================================================================
# 2. ANÁLISIS DE REGISTROS NUEVOS
# ============================================================================
print("\n\n2️⃣ REGISTROS NUEVOS (en actual pero NO en antigua)")
print("="*80)

df_new = df_current[df_current['KEY'].isin(keys_solo_current)].copy()
print(f"Total de registros nuevos: {len(df_new)}")
print(f"RUTs únicos en nuevos: {df_new['RUT'].nunique()}")

# Análisis por DV
print("\nDistribución de DV en registros nuevos:")
print(df_new['DV'].value_counts().to_string())

# Análisis por Prestación
print("\nDistribución de PRESTACIÓN en registros nuevos:")
print(df_new['PRESTACION'].value_counts().to_string())

# ============================================================================
# 3. BÚSQUEDA DE DUPLICADOS
# ============================================================================
print("\n\n3️⃣ BÚSQUEDA DE DUPLICADOS Y ANOMALÍAS")
print("="*80)

# Duplicados en versión antigua
print("\nDuplicados en versión antigua (mismo RUT-DV-PRESTACION):")
dupes_old = df_old[df_old.duplicated(subset=['RUT', 'DV', 'PRESTACION'], keep=False)].sort_values(['RUT', 'PRESTACION'])
if len(dupes_old) > 0:
    print(f"  Encontrados: {len(dupes_old)} filas con duplicados")
    print(dupes_old[['FECHA', 'RUT', 'DV', 'PRESTACION', 'PS-FAM ']].head(10).to_string())
else:
    print("  ✓ No hay duplicados")

# Duplicados en versión actual
print("\nDuplicados en versión actual (mismo RUT-DV-PRESTACION):")
dupes_current = df_current[df_current.duplicated(subset=['RUT', 'DV', 'PRESTACION'], keep=False)].sort_values(['RUT', 'PRESTACION'])
if len(dupes_current) > 0:
    print(f"  Encontrados: {len(dupes_current)} filas con duplicados")
    print(dupes_current[['FECHA', 'RUT', 'DV', 'PRESTACION', 'PS-FAM ']].head(10).to_string())
else:
    print("  ✓ No hay duplicados")

# ============================================================================
# 4. ANÁLISIS DE CAMBIOS EN DATOS COMPARTIDOS
# ============================================================================
print("\n\n4️⃣ CAMBIOS EN REGISTROS COMUNES")
print("="*80)

# Encontrar registros que existen en ambas versiones pero con datos diferentes
keys_common = keys_old & keys_current

changes = []
for key in keys_common:
    old_rows = df_old[df_old['KEY'] == key]
    new_rows = df_current[df_current['KEY'] == key]
    
    # Comparar DV, FECHA, PS-FAM, ESPECIALIDAD
    old_dv = set(old_rows['DV'].unique())
    new_dv = set(new_rows['DV'].unique())
    
    old_psfam = set(old_rows['PS-FAM '].unique())
    new_psfam = set(new_rows['PS-FAM '].unique())
    
    old_esp = set(old_rows['ESPECIALIDAD'].unique())
    new_esp = set(new_rows['ESPECIALIDAD'].unique())
    
    if old_dv != new_dv or old_psfam != new_psfam or old_esp != new_esp:
        changes.append({
            'KEY': key,
            'old_dv': old_dv,
            'new_dv': new_dv,
            'old_psfam': old_psfam,
            'new_psfam': new_psfam,
            'old_esp': old_esp,
            'new_esp': new_esp
        })

if changes:
    print(f"⚠️ Encontrados {len(changes)} cambios en registros comunes:")
    for i, change in enumerate(changes[:10]):  # Mostrar primeros 10
        print(f"\n  Cambio {i+1}: {change['KEY']}")
        if change['old_dv'] != change['new_dv']:
            print(f"    DV cambió: {change['old_dv']} → {change['new_dv']}")
        if change['old_psfam'] != change['new_psfam']:
            print(f"    PS-FAM cambió: {change['old_psfam']} → {change['new_psfam']}")
        if change['old_esp'] != change['new_esp']:
            print(f"    ESPECIALIDAD cambió: {change['old_esp']} → {change['new_esp']}")
else:
    print("✓ No hay cambios en registros comunes")

# ============================================================================
# 5. ANÁLISIS DE PATRÓN EN DV
# ============================================================================
print("\n\n5️⃣ ANÁLISIS DE PATRÓN EN DV (DÍGITO VERIFICADOR)")
print("="*80)

print("\nDistribución de DV en versión antigua:")
print(df_old['DV'].value_counts().to_string())

print("\nDistribución de DV en versión actual:")
print(df_current['DV'].value_counts().to_string())

# Contar DV = K
dv_k_old = len(df_old[df_old['DV'] == 'K'])
dv_k_new = len(df_current[df_current['DV'] == 'K'])

print(f"\nRegistros con DV='K':")
print(f"  Antigua: {dv_k_old} ({dv_k_old/len(df_old)*100:.1f}%)")
print(f"  Actual: {dv_k_new} ({dv_k_new/len(df_current)*100:.1f}%)")

# ============================================================================
# 6. INCONSISTENCIAS POTENCIALES
# ============================================================================
print("\n\n6️⃣ INCONSISTENCIAS DETECTADAS")
print("="*80)

inconsistencies = []

# Inconsistencia 1: Pérdida de registros con DV="K"
if dv_k_old > dv_k_new:
    inconsistencies.append(f"⚠️ Se perdieron registros con DV='K': {dv_k_old} → {dv_k_new} (-{dv_k_old - dv_k_new})")

# Inconsistencia 2: Cambio en distribución de centros
psfam_old_61 = len(df_old[df_old['PS-FAM '] == 61])
psfam_new_61 = len(df_current[df_current['PS-FAM '] == 61])
if psfam_old_61 != 0:
    pct_change = (psfam_new_61 - psfam_old_61) / psfam_old_61 * 100
    inconsistencies.append(f"⚠️ Centro PS-FAM=61 cambió proporcionalmente: {psfam_old_61} → {psfam_new_61} ({pct_change:+.1f}%)")

# Inconsistencia 3: Cambios en prestaciones
if len(df_lost['PRESTACION'].unique()) > 0:
    pres_perdidas = df_lost['PRESTACION'].unique()
    inconsistencies.append(f"⚠️ Prestaciones perdidas: {list(pres_perdidas)}")

# Inconsistencia 4: RUTs completamente nuevos
nuevos_ruts = set(df_new['RUT'].astype(str).unique()) - set(df_lost['RUT'].astype(str).unique())
if len(nuevos_ruts) > 0:
    inconsistencies.append(f"⚠️ {len(nuevos_ruts)} RUTs completamente nuevos (no tenían registro en antigua)")

# Inconsistencia 5: Cambios de formato de fecha
print(f"\n📅 Tipo de dato FECHA:")
print(f"  Antigua: {df_old['FECHA'].dtype}")
print(f"  Actual: {df_current['FECHA'].dtype}")
if df_old['FECHA'].dtype != df_current['FECHA'].dtype:
    inconsistencies.append(f"⚠️ Cambio en tipo de dato FECHA: {df_old['FECHA'].dtype} → {df_current['FECHA'].dtype}")

for i, inconsistency in enumerate(inconsistencies, 1):
    print(f"\n{i}. {inconsistency}")

print("\n" + "="*80)
print("FIN DEL ANÁLISIS")
print("="*80)

# Guardar reporte de registros perdidos
df_lost.to_excel(os.path.join(outputs_path, 'REGISTROS_PERDIDOS_FARMACIA.xlsx'), index=False)
print(f"\n✓ Reporte de registros perdidos guardado en: REGISTROS_PERDIDOS_FARMACIA.xlsx")
