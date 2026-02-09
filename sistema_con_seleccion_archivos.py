import sys
import os
import tkinter as tk
from tkinter import messagebox

# Forzar recarga del módulo
sys.path.insert(0, os.path.abspath('scripts'))
if 'ges_data_processor' in sys.modules:
    del sys.modules['ges_data_processor']

from scripts.ges_data_processor import GESDataProcessor

def ask_file_selection_mode():
    """Preguntar al usuario si quiere seleccionar archivos o usar los predeterminados"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    result = messagebox.askyesnocancel(
        "Modo de Selección de Archivos",
        "¿Cómo deseas cargar los archivos?\n\n"
        "SÍ = Seleccionar archivos manualmente\n"
        "NO = Usar archivos predeterminados de la carpeta 'inputs'\n"
        "CANCELAR = Salir del programa"
    )
    
    root.destroy()
    return result

def main():
    print("🚀 SISTEMA COMPLETO GES - GENERACIÓN DE ARCHIVOS")
    print("=" * 70)
    
    # Preguntar modo de selección
    selection_mode = ask_file_selection_mode()
    
    if selection_mode is None:  # Cancelar
        print("❌ Operación cancelada por el usuario")
        return
    
    # Crear processor según modo
    processor = GESDataProcessor(auto_select_files=not selection_mode)
    
    try:
        if selection_mode:  # Seleccionar archivos manualmente
            print("\n📂 MODO: Selección manual de archivos")
            success = processor.load_data()
        else:  # Usar archivos predeterminados
            print("\n📁 MODO: Archivos predeterminados")
            print("Cargando archivos desde la carpeta 'inputs'...")
            success = processor.load_data()
        
        if not success:
            print("❌ Error al cargar los datos")
            return
        
        print("✅ Archivos cargados exitosamente")
        
        # Ejecutar procesamiento completo de medicamentos
        print("\n💊 Procesando medicamentos para carga...")
        archivo_salida_medicamentos = os.path.join(
            processor.outputs_path, "archivo_farmacia_ges_completo.xlsx"
        )
        
        processor.procesar_medicamentos_para_carga(
            processor.farmacia_df, 
            archivo_salida_medicamentos
        )
        
        print(f"✅ Archivo de medicamentos generado: {archivo_salida_medicamentos}")
        
        # Ejecutar procesamiento completo de consultas
        print("\n👥 Procesando consultas para carga...")
        archivo_salida_consultas = os.path.join(
            processor.outputs_path, "archivo_consultas_ges_completo.xlsx"
        )
        
        processor.procesar_consultas_para_carga(
            processor.consulta_df,
            archivo_salida_consultas
        )
        
        print(f"✅ Archivo de consultas generado: {archivo_salida_consultas}")
        
        # Verificar archivos generados
        print("\n📋 RESUMEN DE ARCHIVOS GENERADOS:")
        if os.path.exists(archivo_salida_consultas):
            size_consultas = os.path.getsize(archivo_salida_consultas) / 1024
            print(f"   📄 {archivo_salida_consultas} ({size_consultas:.1f} KB)")
        
        if os.path.exists(archivo_salida_medicamentos):
            size_medicamentos = os.path.getsize(archivo_salida_medicamentos) / 1024
            print(f"   💊 {archivo_salida_medicamentos} ({size_medicamentos:.1f} KB)")
        
        print("\n🎉 PROCESO COMPLETADO EXITOSAMENTE!")
        print("Los archivos están listos para cargar en el sistema GES.")
        
        # Mostrar mensaje final
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Proceso Completado", 
            "Los archivos GES han sido generados exitosamente!\n\n"
            f"✅ {archivo_salida_consultas}\n"
            f"✅ {archivo_salida_medicamentos}\n\n"
            "Los archivos están en la carpeta 'outputs'."
        )
        root.destroy()
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL PROCESAMIENTO:")
        print(f"   {str(e)}")
        
        # Mostrar error en ventana
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error", 
            f"Error durante el procesamiento:\n\n{str(e)}\n\n"
            "Revisa la consola para más detalles."
        )
        root.destroy()
        
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()