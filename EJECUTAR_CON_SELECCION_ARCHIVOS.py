#!/usr/bin/env python3
"""
Script para ejecutar el sistema GES con selección dinámica de archivos
Permite elegir entre modo automático o selección manual de archivos
"""
import sys
import os

# Forzar recarga del módulo
sys.path.insert(0, os.path.abspath('scripts'))
if 'ges_data_processor' in sys.modules:
    del sys.modules['ges_data_processor']

from scripts.ges_data_processor import GESDataProcessor

def mostrar_menu():
    """Mostrar menú de opciones"""
    print("=" * 60)
    print("🚀 SISTEMA GES - SELECCIÓN DE ARCHIVOS")
    print("=" * 60)
    print("\n📁 MODOS DE SELECCIÓN DE ARCHIVOS:")
    print("1. 🔍 AUTOMÁTICO - Buscar archivos por patrón")
    print("   (busca: reporte_consulta_*.csv, reporte_farmacia_*.csv)")
    print()
    print("2. 👆 MANUAL - Seleccionar archivos manualmente")
    print("   (abre diálogos para elegir archivos)")
    print()
    print("3. ❌ Salir")
    print("=" * 60)

def main():
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n👉 Selecciona una opción (1-3): ").strip()
            
            if opcion == "1":
                print("\n🔍 Modo AUTOMÁTICO seleccionado")
                auto_select = True
                break
                
            elif opcion == "2":
                print("\n👆 Modo MANUAL seleccionado")
                auto_select = False
                break
                
            elif opcion == "3":
                print("\n👋 ¡Hasta luego!")
                return
                
            else:
                print("\n❌ Opción inválida. Por favor selecciona 1, 2 o 3.")
                input("Presiona Enter para continuar...")
                continue
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            return
    
    # Ejecutar sistema con el modo seleccionado
    print(f"\n🚀 EJECUTANDO SISTEMA GES...")
    print("=" * 70)
    
    try:
        # Crear processor con el modo seleccionado
        processor = GESDataProcessor(auto_select_files=auto_select)
        
        # Cargar archivos
        print("\n📁 Cargando archivos de datos...")
        if not processor.load_data():
            print("\n❌ Error al cargar datos. Revisa los archivos de entrada.")
            return
        
        # Cargar archivos adicionales
        processor.load_medicamentos_ges()
        processor.load_clasificacion_paliativos()
        processor.load_severidad_fq()
        
        print("\n✅ Archivos cargados exitosamente")
        
        # Ejecutar procesamiento completo de medicamentos
        print("\n📊 Procesando medicamentos para carga...")
        archivo_salida_medicamentos = "archivo_farmacia_ges_completo.xlsx"
        
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
        print("\n📋 RESUMEN DE ARCHIVOS GENERADOS:")
        for archivo in [archivo_salida_medicamentos, archivo_salida_consultas]:
            if os.path.exists(archivo):
                size = os.path.getsize(archivo) / 1024  # KB
                print(f"  ✅ {archivo} ({size:.1f} KB)")
            else:
                print(f"  ❌ {archivo} - No generado")
        
        print("\n🎉 ¡PROCESAMIENTO COMPLETADO EXITOSAMENTE!")
        
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n👉 Presiona Enter para continuar...")

if __name__ == "__main__":
    main()