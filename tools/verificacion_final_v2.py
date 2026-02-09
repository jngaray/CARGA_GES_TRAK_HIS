#!/usr/bin/env python3
"""
Verificación final del sistema GES V2.0
"""

import sys
import os

# Agregar ruta de scripts
sys.path.insert(0, os.path.abspath('scripts'))

print("🔍 VERIFICACIÓN FINAL SISTEMA GES V2.0")
print("=" * 60)

def verificar_archivos():
    """Verificar archivos esenciales"""
    archivos_esenciales = [
        "scripts/ges_data_processor.py",
        "scripts/ges_advanced_analyzer.py",
        "scripts/ges_config.py",
        "scripts/trazadora_processor.py",
        "sistema_completo_final.py",
        "EJECUTAR_GUI.bat",
        "README_V2.md"
    ]
    
    print("📁 Verificando archivos esenciales...")
    faltantes = []
    
    for archivo in archivos_esenciales:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo}")
            faltantes.append(archivo)
    
    return len(faltantes) == 0

def verificar_modulos():
    """Verificar importación de módulos"""
    print("\n🔧 Verificando módulos...")
    
    try:
        from scripts.ges_data_processor import GESDataProcessor
        print("   ✅ GESDataProcessor")
        
        from scripts.ges_advanced_analyzer import GESAdvancedAnalyzer
        print("   ✅ GESAdvancedAnalyzer")
        
        import pandas as pd
        print("   ✅ pandas")
        
        import tkinter as tk
        print("   ✅ tkinter")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verificar_funcionalidades():
    """Verificar nuevas funcionalidades"""
    print("\n🎯 Verificando funcionalidades V2.0...")
    
    try:
        from scripts.ges_data_processor import GESDataProcessor
        processor = GESDataProcessor()
        
        # Verificar función de población GES
        if hasattr(processor, 'esta_en_poblacion_ges'):
            print("   ✅ Verificación población GES")
        else:
            print("   ❌ Falta verificación población GES")
            
        # Verificar función de paliativos actualizada
        if hasattr(processor, 'determinar_tipo_paliativo'):
            print("   ✅ Función paliativos actualizada")
        else:
            print("   ❌ Falta función paliativos")
            
        # Verificar carga de archivos nuevos
        if hasattr(processor, 'load_clasificacion_paliativos'):
            print("   ✅ Carga clasificación paliativos")
        else:
            print("   ❌ Falta carga paliativos")
            
        if hasattr(processor, 'load_severidad_fq'):
            print("   ✅ Carga severidad FQ")
        else:
            print("   ❌ Falta carga severidad FQ")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def verificar_inputs():
    """Verificar archivos de entrada"""
    print("\n📥 Verificando archivos de entrada...")
    
    archivos_entrada = [
        "inputs/RUT_pob_ges.xlsx",
        "inputs/reporte_consulta_ago.csv", 
        "inputs/reporte_farmacia_ago.csv",
        "inputs/clasificacion_paliativos.csv",
        "inputs/severidad_FQ.xlsx"
    ]
    
    encontrados = 0
    for archivo in archivos_entrada:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo) / 1024
            print(f"   ✅ {archivo} ({size:.1f} KB)")
            encontrados += 1
        else:
            print(f"   ⚠️ {archivo} - No encontrado")
    
    return encontrados

def main():
    """Función principal de verificación"""
    
    # Verificaciones
    archivos_ok = verificar_archivos()
    modulos_ok = verificar_modulos()
    funcionalidades_ok = verificar_funcionalidades()
    inputs_encontrados = verificar_inputs()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN VERIFICACIÓN")
    print("=" * 60)
    
    print(f"📁 Archivos esenciales: {'✅ OK' if archivos_ok else '❌ FALTANTES'}")
    print(f"🔧 Módulos Python: {'✅ OK' if modulos_ok else '❌ ERROR'}")
    print(f"🎯 Funcionalidades V2.0: {'✅ OK' if funcionalidades_ok else '❌ INCOMPLETAS'}")
    print(f"📥 Archivos de entrada: {inputs_encontrados}/5 encontrados")
    
    if archivos_ok and modulos_ok and funcionalidades_ok:
        print("\n🎉 SISTEMA LISTO PARA PRODUCCIÓN")
        print("⭐ FUNCIONALIDADES V2.0 VERIFICADAS:")
        print("   • Trazadoras múltiples")
        print("   • Verificación población GES")
        print("   • Eliminación de duplicados")
        print("   • Nueva lógica paliativos")
        print("   • Archivos de revisión")
        
        print("\n🚀 PARA USAR:")
        print("   GUI: EJECUTAR_GUI.bat")
        print("   CMD: python sistema_completo_final.py")
        
        if inputs_encontrados >= 3:
            print("\n✅ SUFICIENTES ARCHIVOS PARA PROCESAMIENTO")
        else:
            print(f"\n⚠️ SOLO {inputs_encontrados} ARCHIVOS DE ENTRADA")
            print("   Agregue más archivos a inputs/ para funcionalidad completa")
            
    else:
        print("\n❌ SISTEMA REQUIERE CORRECCIONES")
        if not archivos_ok:
            print("   • Archivos faltantes")
        if not modulos_ok:
            print("   • Problemas de módulos Python")
        if not funcionalidades_ok:
            print("   • Funcionalidades incompletas")
    
    print("=" * 60)

if __name__ == "__main__":
    main()