import sys
import os

# Forzar recarga del módulo
sys.path.insert(0, os.path.abspath('scripts'))
if 'ges_data_processor' in sys.modules:
    del sys.modules['ges_data_processor']

from scripts.ges_data_processor import GESDataProcessor

print("EJECUTANDO SISTEMA COMPLETO GES - GENERACIÓN DE ARCHIVOS")
print("=" * 70)

# Crear processor con módulo actualizado
processor = GESDataProcessor()

try:
    # Cargar archivos
    print("📁 Cargando archivos de datos...")
    processor.load_data()
    processor.load_medicamentos_ges()
    processor.load_clasificacion_paliativos()
    processor.load_severidad_fq()
    processor.load_recetas_ges()  # Cargar recetas GES
    
    print("✅ Archivos cargados exitosamente")
    
    # Ejecutar procesamiento completo de medicamentos
    print("\n📊 Procesando medicamentos para carga...")
    archivo_salida_medicamentos = "archivo_farmacia_ges_completo.xlsx"
    
    # Usar el método que genera archivos de salida
    processor.procesar_medicamentos_para_carga(
        processor.farmacia_df, 
        archivo_salida_medicamentos
    )
    
    print(f"✅ Archivo de medicamentos generado: {archivo_salida_medicamentos}")
    
    # Ejecutar procesamiento completo de consultas
    print("\n📊 Procesando consultas para carga...")
    archivo_salida_consultas = "archivo_consultas_ges_completo.xlsx"
    
    processor.procesar_consultas_para_carga(
        processor.consulta_df,
        archivo_salida_consultas
    )
    
    print(f"✅ Archivo de consultas generado: {archivo_salida_consultas}")
    
    # Verificar archivos generados
    print("\n📂 Verificando archivos generados...")
    archivos_generados = []
    
    for archivo in [archivo_salida_medicamentos, archivo_salida_consultas]:
        if os.path.exists(archivo):
            archivos_generados.append(archivo)
            size = os.path.getsize(archivo) / 1024  # KB
            print(f"  ✅ {archivo} ({size:.1f} KB)")
        else:
            print(f"  ❌ {archivo} - No encontrado")
    
    # Analizar resultados de medicamentos
    if archivo_salida_medicamentos in archivos_generados:
        print(f"\n🎯 ANALIZANDO RESULTADOS DE MEDICAMENTOS:")
        import pandas as pd
        
        try:
            df_medicamentos = pd.read_excel(archivo_salida_medicamentos)
            print(f"Total registros de medicamentos: {len(df_medicamentos)}")
            
            if 'PRESTACION' in df_medicamentos.columns:
                # Analizar por códigos de prestación (trazadoras)
                trazadoras_count = df_medicamentos['PRESTACION'].value_counts()
                print(f"\n📋 TRAZADORAS DE MEDICAMENTOS:")
                print(f"   Total trazadoras únicas: {len(trazadoras_count)}")
                
                # Mapeo de códigos a patologías
                codigo_patologia = {
                    # ASMA
                    '3902001': 'ASMA - SALBUTAMOL',
                    '3902002': 'ASMA - CORTICOIDE',
                    '3902003': 'ASMA - TEOFILINA', 
                    '3902004': 'ASMA - PREDNISONA',
                    '3902005': 'ASMA - DESLORATADINA',
                    '3902006': 'ASMA - IPRATROPIO',
                    '2508156': 'ASMA - MEPOLIZUMAB/OMALIZUMAB',
                    # FIBROSIS
                    '3004004': 'FIBROSIS - TOBRAMICINA',
                    '2508141': 'FIBROSIS - TRIKAFTA',
                    '2505256': 'FIBROSIS - GRAVE',
                    '2505260': 'FIBROSIS - MODERADA',
                    '2505263': 'FIBROSIS - LEVE',
                    # PALIATIVOS
                    '3002023': 'PALIATIVOS - PROGRESIVO',
                    '3002123': 'PALIATIVOS - NO PROGRESIVO',
                    # EPOC
                    '3801002': 'EPOC - MEDICAMENTOS'
                }
                
                print(f"\n� DETALLE POR PATOLOGÍA:")
                
                # Agrupar por patología
                patologias = {}
                for codigo, count in trazadoras_count.items():
                    descripcion = codigo_patologia.get(codigo, f'OTRO - {codigo}')
                    patologia = descripcion.split(' - ')[0]
                    
                    if patologia not in patologias:
                        patologias[patologia] = {}
                    patologias[patologia][codigo] = {'descripcion': descripcion, 'count': count}
                
                for patologia, codigos in patologias.items():
                    total_patologia = sum(item['count'] for item in codigos.values())
                    print(f"\n   {patologia} - {total_patologia} registros totales:")
                    for codigo, info in codigos.items():
                        print(f"     {codigo}: {info['count']} registros ({info['descripcion']})")
                
                # Verificar que ASMA y FIBROSIS tengan múltiples trazadoras
                asma_codes = [k for k in trazadoras_count.keys() if str(k).startswith('3902')]
                fibrosis_codes = [k for k in trazadoras_count.keys() if str(k).startswith('2505') or str(k) == '3004004']
                
                print(f"\n✅ VALIDACIÓN DE REQUERIMIENTOS:")
                print(f"   ASMA - Trazadoras diferentes encontradas: {len(asma_codes)} ({asma_codes})")
                print(f"   FIBROSIS - Trazadoras diferentes encontradas: {len(fibrosis_codes)} ({fibrosis_codes})")
                
                if len(asma_codes) > 1:
                    print(f"   ✅ ASMA: CORRECTO - Múltiples trazadoras detectadas")
                else:
                    print(f"   ⚠️ ASMA: REVISAR - Solo {len(asma_codes)} trazadora encontrada")
                    
                if len(fibrosis_codes) > 1:
                    print(f"   ✅ FIBROSIS: CORRECTO - Múltiples trazadoras detectadas")
                else:
                    print(f"   ⚠️ FIBROSIS: REVISAR - Solo {len(fibrosis_codes)} trazadora encontrada")
            
            else:
                print("⚠️ Estructura de archivo no reconocida")
                print(f"Columnas disponibles: {list(df_medicamentos.columns)}")
                
        except Exception as e:
            print(f"❌ Error analizando archivo de medicamentos: {e}")
    
    # Analizar resultados de consultas
    if archivo_salida_consultas in archivos_generados:
        print(f"\n🎯 ANALIZANDO RESULTADOS DE CONSULTAS:")
        try:
            df_consultas = pd.read_excel(archivo_salida_consultas)
            print(f"Total registros de consultas: {len(df_consultas)}")
            
            if 'Condicion_GES' in df_consultas.columns:
                condiciones_consultas = df_consultas['Condicion_GES'].value_counts()
                print(f"\n📊 RESUMEN CONSULTAS POR CONDICIÓN:")
                for condicion, count in condiciones_consultas.items():
                    print(f"   {condicion}: {count} registros")
                    
        except Exception as e:
            print(f"❌ Error analizando archivo de consultas: {e}")
    
    print(f"\n🎉 SISTEMA COMPLETO EJECUTADO")
    print(f"Archivos generados: {len(archivos_generados)}")
    
except Exception as e:
    print(f"❌ Error en ejecución: {e}")
    import traceback
    traceback.print_exc()