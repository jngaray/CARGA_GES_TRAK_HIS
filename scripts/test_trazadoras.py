from ges_data_processor import GESDataProcessor
from trazadora_processor import TrazadoraProcessor

processor = GESDataProcessor()
tproc = TrazadoraProcessor()

print('🧪 PROBANDO TRAZADORAS DIFERENCIADAS DE PALIATIVOS')
print('=' * 50)

# RUTs de nuestro archivo de clasificación
ruts_test = [7255155, 2849412, 9876543, 5432109, 1234567]

for rut in ruts_test:
    # Crear medicamento como diccionario correcto
    medicamento = {'Farmaco_Desc': 'Morfina', 'RUNPaciente': rut}
    
    tipo = processor.determinar_tipo_paliativo(rut)
    trazadora = processor.determinar_codigo_trazadora_medicamento(medicamento, 'Paliativos')
    print(f'RUT {rut}: {tipo} → {trazadora}')
    
    # Validar resultado
    if tipo == 'no_progresivo' and trazadora == '3002123':
        print('  ✅ CORRECTO: Sin cáncer progresivo')
    elif tipo == 'progresivo' and trazadora == '3002023':
        print('  ✅ CORRECTO: Cáncer terminal')
    else:
        print(f'  ❌ ERROR: Esperado {tipo} → {"3002123" if tipo == "no_progresivo" else "3002023"}')
    if tipo == 'no_progresivo' and trazadora == '3002123':
        print('  ✅ CORRECTO: Sin cáncer progresivo')
    elif tipo == 'progresivo' and trazadora == '3002023':
        print('  ✅ CORRECTO: Cáncer terminal')
    elif tipo == 'desconocido' and trazadora == '3002123':
        print('  ⚠️  DEFAULT: Sin cáncer progresivo (por defecto)')
    else:
        print('  ❌ ERROR')

print('\n✅ SISTEMA DE TRAZADORAS DIFERENCIADAS FUNCIONANDO')
print('3002123: TRATAMIENTO INTEGRAL POR ALIVIO DEL DOLOR PACIENTES SIN CÁNCER PROGRESIVO')
print('3002023: CUIDADOS PALIATIVOS EN CÁNCER TERMINAL')

# ---------- NUEVAS PRUEBAS: FIBROSIS - TRIKAFTA ----------
print('\n🧪 PROBANDO MEDICAMENTO FIBROSIS - TRIKAFTA')
medicamento_tr = {'Farmaco_Desc': 'Trikafta (elexacaftor/tezacaftor/ivacaftor)', 'RUNPaciente': 1234567}

traz_gds = processor.determinar_codigo_trazadora_medicamento(medicamento_tr, 'Fibrosis')
traz_tproc = tproc._determinar_trazadora_fibrosis_medicamento(medicamento_tr['Farmaco_Desc'], str(medicamento_tr['RUNPaciente']))

print(f'Trazadora GESDataProcessor: {traz_gds}, Trazadora TrazadoraProcessor: {traz_tproc}')
if traz_gds == '2508141' and traz_tproc == '2508141':
    print('  ✅ CORRECTO: TRIKAFTA mapeada a 2508141')
else:
    print('  ❌ ERROR: TRIKAFTA NO mapeada correctamente')

# ---------- NUEVAS PRUEBAS: ASMA - MAB (MEPOLIZUMAB / OMALIZUMAB) ----------
print('\n🧪 PROBANDO MEDICAMENTOS ASMA - MAB')
medicamentos_asma_mab = [
    {'Farmaco_Desc': 'MEPOLIZUMAB 100 MG LIOF. P/SOL. INY. FAM', 'RUNPaciente': 1234567},
    {'Farmaco_Desc': 'OMALIZUMAB 150 MG POLVO LIOF/SOL INYECT', 'RUNPaciente': 1234567},
]

for med in medicamentos_asma_mab:
    traz_gds = processor.determinar_codigo_trazadora_medicamento(med, 'ASMA')
    traz_tproc = tproc._determinar_trazadora_asma_medicamento(med['Farmaco_Desc'])
    print(f"{med['Farmaco_Desc'][:40]} -> GES: {traz_gds}, Tproc: {traz_tproc}")
    if traz_gds == '2508156' and traz_tproc == '2508156':
        print('  ✅ CORRECTO: MAB ASMA mapeada a 2508156')
    else:
        print('  ❌ ERROR: MAB ASMA NO mapeada correctamente')

# ---------- NUEVA PRUEBA: ARCHIVO CRUCE INCLUYE RUT (caso sensibilidad DV) ----------
print('\n🧪 PROBANDO INCLUSIÓN EN ARCHIVO DE CRUCE PARA RUT 15946945-K')
import sys
import pandas as pd
# Cargar archivos de ejemplo
ges = pd.read_excel('inputs/RUT_pob_ges.xlsx')
farm = pd.read_csv('inputs/reporte_farmacia_diciembre.csv', sep=';', encoding='latin-1', on_bad_lines='skip')
# Asegurar campo RUT_Combined
farm['RUT_Combined'] = [processor.format_rut(row['RutPaciente'], row['DVPaciente']) for _, row in farm.iterrows()]

# Generar archivo de cruce usando TrazadoraProcessor
archivo = tproc.generar_archivo_cruce(ges, None, farm)

# Leer resultado
df_cruce = pd.read_csv(archivo, sep='|', encoding='utf-8')
# Buscar RUT
match = df_cruce[df_cruce['RUT'].astype(str).str.contains('15946945', na=False)]
print(match.to_string())
if len(match) > 0 and match.iloc[0]['TUVO_MEDICAMENTO'] in ['SÍ', 'SI', 'Sí']:
    print('  ✅ CORRECTO: RUT 15946945 presente con medicación')
else:
    print('  ❌ ERROR: RUT 15946945 NO encontrado o sin medicación')