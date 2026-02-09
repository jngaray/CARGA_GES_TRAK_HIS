import pandas as pd
import os
from scripts.ges_data_processor import GESDataProcessor

def create_test_pharmacy_data():
    """Create test data with intentional duplicates"""
    return pd.DataFrame({
        'RutPaciente': [12345678, 12345678, 12345678, 12345678, 87654321],
        'DVPaciente': ['1', '1', '1', '1', '2'],
        'Farmaco_Desc': ['SALBUTAMOL', 'SALBUTAMOL', 'PREDNISONA', 'SALBUTAMOL', 'IPRATROPIO'],
        'FechaDespacho': ['2025-03-01', '2025-03-01', '2025-03-01', '2025-03-15', '2025-03-01'],
        'CantidadDespachada': [30, 30, 30, 30, 30],
        'LocalSolicitante': ['INT-07-102-0', 'INT-07-102-0', 'INT-07-102-0', 'INT-07-102-0', 'INT-07-102-0']
    })

def create_test_ges_population():
    """Create test GES population data"""
    return pd.DataFrame({
        'RUT': [12345678, 87654321],
        'DV': ['1', '2'],
        'Ges': ['ASMA', 'EPOC']
    })

def test_pharmacy_deduplication(show_details=True):
    """Test pharmacy data processing with focus on deduplication"""
    print("\n=== PRUEBA DE DEDUPLICACIÓN DE FARMACIA ===")
    
    # Crear processor y configurar datos de prueba
    processor = GESDataProcessor(auto_select_files=False)
    processor.farmacia_df = create_test_pharmacy_data()
    processor.ges_df = create_test_ges_population()
    
    if show_details:
        print("\nDatos originales de farmacia:")
        print(processor.farmacia_df[['RutPaciente', 'DVPaciente', 'Farmaco_Desc', 'FechaDespacho']].to_string())
    
    # Generar archivo de prueba
    test_output = os.path.join(processor.outputs_path, 'test_farmacia_output.xlsx')
    processor.procesar_medicamentos_para_carga(processor.farmacia_df, test_output)
    
    # Verificar resultado
    if os.path.exists(test_output):
        result_df = pd.read_excel(test_output)
        print(f"\nRegistros en archivo final: {len(result_df)}")
        if show_details:
            print("\nRegistros procesados (después de deduplicación):")
            print(result_df.to_string())
            
        # Análisis de duplicados
        duplicates = result_df.groupby(['RUT', 'DV', 'PRESTACION', 'FECHA']).size().reset_index(name='count')
        duplicates = duplicates[duplicates['count'] > 1]
        if not duplicates.empty:
            print("\n⚠️ DUPLICADOS ENCONTRADOS:")
            print(duplicates.to_string())
        else:
            print("\n✅ No se encontraron duplicados")
    else:
        print(f"\n❌ Error: No se generó el archivo {test_output}")

def test_load_real_files():
    """Test loading and processing real pharmacy files"""
    processor = GESDataProcessor(auto_select_files=False)
    
    # Intenta cargar archivo de marzo (problemático)
    march_file = r"c:\Users\mgalleguillos\Desktop\Producción INT\producción farmacia 2025\reporte_farmacia_marzo.csv"
    if os.path.exists(march_file):
        print("\n=== PRUEBA ARCHIVO MARZO ===")
        df_march = processor.load_csv_safely(march_file)
        if df_march is not None:
            print(f"Columnas: {df_march.columns.tolist()}")
            print("\nPrimeros 5 RUTs:")
            print(df_march[['RutPaciente', 'DVPaciente']].head().to_string())
    
    # Intenta cargar archivo que funciona bien (ajusta la ruta)
    working_file = "inputs/reporte_farmacia_febrero.csv"  # ajusta según corresponda
    if os.path.exists(working_file):
        print("\n=== PRUEBA ARCHIVO QUE FUNCIONA ===")
        df_working = processor.load_csv_safely(working_file)
        if df_working is not None:
            print(f"Columnas: {df_working.columns.tolist()}")
            print("\nPrimeros 5 RUTs:")
            print(df_working[['RutPaciente', 'DVPaciente']].head().to_string())

if __name__ == "__main__":
    print("=== INICIANDO PRUEBAS DE FARMACIA ===")
    
    # Prueba 1: Deduplicación con datos sintéticos
    test_pharmacy_deduplication()
    
    # Prueba 2: Carga de archivos reales
    test_load_real_files()
