import os
from datetime import datetime
import glob
import tkinter as tk
from tkinter import filedialog, messagebox

import pandas as pd
from ges_config import *
from trazadora_processor import TrazadoraProcessor


class GESDataProcessor:
    def __init__(self, base_path=None, auto_select_files=True):
        if base_path is None:
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.base_path = base_path

        self.inputs_path = os.path.join(self.base_path, "inputs")
        self.outputs_path = os.path.join(self.base_path, "outputs")

        # Configuración de selección de archivos
        self.auto_select_files = auto_select_files
        self.selected_files = {}

        # DataFrames
        self.ges_df = None
        self.consulta_df = None
        self.farmacia_df = None
        self.medicamentos_ges_df = None
        self.recetas_ges_df = None  # Nuevo: archivo de recetas GES por patología

        # Resultados
        self.medicamentos_encontrados = {}
        self.consultas_procesadas = []
        self.medicamentos_procesados = []

        # Procesador de trazadoras
        self.trazadora_processor = TrazadoraProcessor(self.base_path)

    def find_files_by_pattern(self, pattern, description="archivo"):
        """Buscar archivos automáticamente por patrón"""
        search_pattern = os.path.join(self.inputs_path, pattern)
        found_files = glob.glob(search_pattern)
        
        if found_files:
            # Ordenar por fecha de modificación (más reciente primero)
            found_files.sort(key=os.path.getmtime, reverse=True)
            selected_file = found_files[0]
            print(f"✓ {description} encontrado automáticamente: {os.path.basename(selected_file)}")
            return selected_file
        else:
            print(f"⚠️  No se encontró {description} con patrón: {pattern}")
            return None

    def select_file_dialog(self, title, filetypes):
        """Seleccionar archivo mediante diálogo"""
        try:
            root = tk.Tk()
            root.withdraw()  # Ocultar ventana principal
            
            file_path = filedialog.askopenfilename(
                title=title,
                initialdir=self.inputs_path,
                filetypes=filetypes
            )
            
            root.destroy()
            
            if file_path:
                print(f"✓ Archivo seleccionado: {os.path.basename(file_path)}")
                return file_path
            else:
                print("⚠️  No se seleccionó archivo")
                return None
                
        except Exception as e:
            print(f"❌ Error en selección de archivo: {e}")
            return None

    def select_files_dialog(self, title, filetypes):
        """Seleccionar múltiples archivos mediante diálogo"""
        try:
            root = tk.Tk()
            root.withdraw()  # Ocultar ventana principal

            file_paths = filedialog.askopenfilenames(
                title=title,
                initialdir=self.inputs_path,
                filetypes=filetypes,
            )

            root.destroy()

            if file_paths:
                print(f"✓ Archivos seleccionados: {len(file_paths)}")
                return list(file_paths)
            else:
                print("⚠️  No se seleccionaron archivos")
                return []

        except Exception as e:
            print(f"❌ Error en selección de archivos: {e}")
            return []

    def setup_input_files(self, month_filter=None):
        """Configurar archivos de entrada según el modo seleccionado"""
        print("\n📁 CONFIGURANDO ARCHIVOS DE ENTRADA...")
        
        if self.auto_select_files:
            print("🔍 Modo automático: Buscando archivos por patrón...")
            
            # Si se especifica un mes, incluirlo en los patrones
            if month_filter:
                print(f"🗓️  Filtrando por mes: {month_filter}")
                month_patterns = [f"*{month_filter}*", f"*{month_filter.lower()}*", f"*{month_filter.upper()}*"]
            else:
                month_patterns = ["*"]
            
            # Buscar archivo de consultas
            consultas_patterns = []
            for month_pat in month_patterns:
                consultas_patterns.extend([
                    f"reporte_consulta_{month_pat}.csv",
                    f"{month_pat}consulta*.csv", 
                    f"consultas_{month_pat}.csv",
                    f"reporte_consulta*.csv",  # Fallback
                    f"*consulta*.csv"
                ])
            
            for pattern in consultas_patterns:
                consultas_file = self.find_files_by_pattern(pattern, "archivo de consultas")
                if consultas_file:
                    self.selected_files['consultas'] = consultas_file
                    break
            
            # Buscar archivo de farmacia
            farmacia_patterns = []
            for month_pat in month_patterns:
                farmacia_patterns.extend([
                    f"reporte_farmacia_{month_pat}.csv",
                    f"{month_pat}farmacia*.csv",
                    f"farmacia_{month_pat}.csv",
                    f"reporte_farmacia*.csv",  # Fallback
                    f"*farmacia*.csv"
                ])
            
            for pattern in farmacia_patterns:
                farmacia_file = self.find_files_by_pattern(pattern, "archivo de farmacia")
                if farmacia_file:
                    self.selected_files['farmacia'] = farmacia_file
                    break
            
            # Buscar archivos de recetas GES (prescripciones por patología)
            recetas_patterns = []
            for month_pat in month_patterns:
                recetas_patterns.extend([
                    f"recetas*{month_pat}*.xlsx",
                    f"recetas*{month_pat}*.xls",
                    f"recetas*.xlsx",  # Fallback
                    f"recetas*.xls"
                ])
            
            # Buscar TODOS los archivos de recetas (uno por patología)
            recetas_files = []
            for pattern in recetas_patterns:
                search_pattern = os.path.join(self.inputs_path, pattern)
                found = glob.glob(search_pattern)
                if found:
                    recetas_files.extend(found)
            
            if recetas_files:
                self.selected_files['recetas_ges'] = list(set(recetas_files))  # Eliminar duplicados
                print(f"✓ Archivos de recetas GES encontrados: {len(self.selected_files['recetas_ges'])}")
                    
        else:
            print("👆 Modo manual: Selecciona los archivos...")

            # Si ya están preconfigurados, no abrir diálogos
            if self.selected_files.get('consultas') and self.selected_files.get('farmacia'):
                print("✓ Archivos manuales ya configurados, omitiendo selección")
            else:
            
                # Seleccionar archivo de consultas
                consultas_file = self.select_file_dialog(
                    "Seleccionar archivo de CONSULTAS",
                    [("CSV files", "*.csv"), ("All files", "*.*")]
                )
                if consultas_file:
                    self.selected_files['consultas'] = consultas_file
                
                # Seleccionar archivo de farmacia
                farmacia_file = self.select_file_dialog(
                    "Seleccionar archivo de FARMACIA", 
                    [("CSV files", "*.csv"), ("All files", "*.*")]
                )
                if farmacia_file:
                    self.selected_files['farmacia'] = farmacia_file

                # Seleccionar archivos de recetas GES (opcional, permite múltiples)
                recetas_files = self.select_files_dialog(
                    "Seleccionar archivos de RECETAS GES (opcional)",
                    [("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")],
                )
                if recetas_files:
                    self.selected_files['recetas_ges'] = recetas_files
        
        # Mostrar resumen
        print("\n📋 ARCHIVOS CONFIGURADOS:")
        for tipo, archivo in self.selected_files.items():
            if archivo:
                if isinstance(archivo, list):
                    print(f"  {tipo.upper()}: {len(archivo)} archivos")
                else:
                    print(f"  {tipo.upper()}: {os.path.basename(archivo)}")
            else:
                print(f"  {tipo.upper()}: ❌ No configurado")
        
        return len(self.selected_files) > 0

    def load_data(self):
        """Cargar todos los archivos de datos"""
        print("\n📊 CARGANDO ARCHIVOS DE DATOS...")

        try:
            # Configurar archivos de entrada primero
            if not self.setup_input_files():
                print("❌ No se pudieron configurar los archivos de entrada")
                return False

            # Cargar población GES (archivo fijo)
            ges_file = os.path.join(self.inputs_path, "RUT_pob_ges.xlsx")
            if os.path.exists(ges_file):
                self.ges_df = pd.read_excel(ges_file)
                print(f"✓ Población GES: {len(self.ges_df)} pacientes")
            else:
                print("❌ No se encontró archivo RUT_pob_ges.xlsx")
                return False

            # Cargar consultas usando archivo seleccionado
            if 'consultas' in self.selected_files and self.selected_files['consultas']:
                self.consulta_df = self.load_csv_safely(self.selected_files['consultas'])
                if self.consulta_df is not None:
                    # Normalizar DV a mayúsculas
                    self.consulta_df = self.normalize_dv_in_dataframe(self.consulta_df)
                    print(f"✓ Consultas: {len(self.consulta_df)} registros")
            else:
                print("⚠️  No se configuró archivo de consultas")

            # Cargar farmacia usando archivo seleccionado
            if 'farmacia' in self.selected_files and self.selected_files['farmacia']:
                self.farmacia_df = self.load_csv_safely(self.selected_files['farmacia'])
                if self.farmacia_df is not None:
                    # Normalizar DV a mayúsculas
                    self.farmacia_df = self.normalize_dv_in_dataframe(self.farmacia_df)
                    # Combinar RUT
                    self.farmacia_df["RUT_Combined"] = [
                        self.format_rut(row["RutPaciente"], row["DVPaciente"])
                        for _, row in self.farmacia_df.iterrows()
                    ]
                    self.farmacia_df = self.farmacia_df.dropna(subset=["RUT_Combined"])
                    print(f"✓ Farmacia: {len(self.farmacia_df)} registros")
            else:
                print("⚠️  No se configuró archivo de farmacia")

            # Buscar archivo de medicamentos GES
            self.load_medicamentos_ges()

            # Cargar clasificación de paliativos
            self.load_clasificacion_paliativos()
            
            # Cargar severidad de Fibrosis Quística
            self.load_severidad_fq()
            
            # Cargar recetas GES (prescripciones por patología)
            self.load_recetas_ges()

            return True

        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return False

    def load_medicamentos_ges(self):
        """Cargar archivo de medicamentos GES"""
        possible_files = [
            "Medicamentos GES (1).xlsx",
            "Medicamentos GES (1).csv",
            "medicamentos_ges.xlsx",
            "medicamentos_ges.csv",
        ]

        for filename in possible_files:
            filepath = os.path.join(self.inputs_path, filename)
            if os.path.exists(filepath):
                try:
                    if filename.endswith(".xlsx"):
                        self.medicamentos_ges_df = pd.read_excel(filepath)
                    else:
                        self.medicamentos_ges_df = self.load_csv_safely(filepath)

                    print(f"✓ Medicamentos GES: {len(self.medicamentos_ges_df)} medicamentos")
                    print(f"  Columnas disponibles: {list(self.medicamentos_ges_df.columns)}")
                    return
                except Exception as e:
                    print(f"⚠️  Error cargando {filename}: {e}")

        print("⚠️  No se encontró archivo de medicamentos GES")
        print("   Archivos esperados:", possible_files)

    def load_clasificacion_paliativos(self):
        """Cargar archivo de clasificación de paliativos"""
        possible_files = [
            "clasificacion paliativos.xlsx",
            "clasificacion_paliativos.xlsx", 
            "Clasificacion Paliativos.xlsx",
            "clasificacion paliativos.csv",
            "clasificacion_paliativos.csv"
        ]

        for filename in possible_files:
            filepath = os.path.join(self.inputs_path, filename)
            if os.path.exists(filepath):
                try:
                    if filename.endswith(".xlsx"):
                        df = pd.read_excel(filepath)
                    else:
                        # Intentar con punto y coma primero (formato correcto)
                        df = pd.read_csv(filepath, sep=';', encoding='latin-1')
                        
                        # Limpiar nombres de columnas (quitar espacios)
                        df.columns = df.columns.str.strip()

                    if df is not None and len(df) > 0:
                        self.clasificacion_paliativos_df = df
                        print(f"✓ Clasificación Paliativos: {len(df)} registros")
                        print(f"  Columnas disponibles: {list(df.columns)}")
                        
                        # Verificar que tenemos las columnas necesarias
                        expected_cols = ['RUT', 'condicion']
                        missing_cols = [col for col in expected_cols if col not in df.columns]
                        if missing_cols:
                            print(f"  ⚠️ Columnas faltantes: {missing_cols}")
                            print(f"  📊 Muestra de datos:")
                            print(df.head(3))
                        else:
                            print(f"  ✅ Columnas correctas encontradas")
                        
                        return
                except Exception as e:
                    print(f"⚠️  Error cargando {filename}: {e}")

        print("⚠️  No se encontró archivo de clasificación de paliativos")
        print("   Archivos esperados:", possible_files)
        self.clasificacion_paliativos_df = None

    def load_severidad_fq(self):
        """Cargar archivo de severidad de Fibrosis Quística"""
        possible_files = [
            "severidad_FQ.xlsx",
            "severidad_fq.xlsx", 
            "Severidad_FQ.xlsx",
            "severidad_FQ.csv",
            "severidad_fq.csv"
        ]

        for filename in possible_files:
            filepath = os.path.join(self.inputs_path, filename)
            if os.path.exists(filepath):
                try:
                    if filename.endswith(".xlsx"):
                        df = pd.read_excel(filepath)
                    else:
                        df = pd.read_csv(filepath, sep=',')

                    if df is not None:
                        self.severidad_fq_df = df
                        print(f"✓ Severidad FQ: {len(df)} registros")
                        print(f"  Columnas disponibles: {list(df.columns)}")
                        return
                except Exception as e:
                    print(f"⚠️  Error cargando {filename}: {e}")

        print("⚠️  No se encontró archivo de severidad FQ")
        print("   Archivos esperados:", possible_files)
        self.severidad_fq_df = None

    def determinar_severidad_fq(self, rut):
        """Determina la severidad de Fibrosis Quística para un RUT"""
        try:
            if self.severidad_fq_df is None:
                print(f"⚠️ FQ SIN BD: RUT {rut} - No hay base de datos de severidad FQ cargada")
                return "leve"  # Default
            
            # Convertir RUT a string para comparación
            rut_str = str(rut).split('-')[0]  # Quitar DV si existe
            
            # Buscar en diferentes posibles nombres de columna RUT
            rut_column = None
            for col in ['RUT', 'Rut', 'rut', 'Rut ']:
                if col in self.severidad_fq_df.columns:
                    rut_column = col
                    break
            
            if rut_column is None:
                print(f"⚠️ FQ SIN COLUMNA RUT: RUT {rut} - No se encontró columna RUT en la base de datos")
                print(f"   Columnas disponibles: {list(self.severidad_fq_df.columns)}")
                return "leve"
            
            # Extraer solo el número del RUT (sin DV) de la columna
            rut_series = self.severidad_fq_df[rut_column].astype(str).str.split('-').str[0]
            mask = rut_series == rut_str
            
            if mask.any():
                severidad_row = self.severidad_fq_df[mask]
                severidad_raw = severidad_row['Severidad'].iloc[0]
                
                # Verificar si el campo está vacío
                if pd.isna(severidad_raw) or str(severidad_raw).strip() == '' or str(severidad_raw).lower() in ['nan', 'none', 'null']:
                    print(f"⚠️ FQ CAMPO VACÍO: RUT {rut} - Campo 'Severidad' está vacío")
                    return "leve"  # Default para continuar procesamiento
                
                severidad = str(severidad_raw).upper().strip()
                
                # Mapear severidad a nombres estándar
                if severidad in ['SEVERO', 'GRAVE']:
                    return "grave"
                elif severidad in ['MODERADO', 'MODERADA']:
                    return "moderada" 
                elif severidad in ['LEVE']:
                    return "leve"
                else:
                    print(f"⚠️ FQ SEVERIDAD DESCONOCIDA: RUT {rut} - Severidad '{severidad}' no reconocida")
                    return "leve"
            else:
                print(f"⚠️ FQ NO ENCONTRADO: RUT {rut} - No existe en la base de datos de severidad FQ")
                return "leve"  # Default si no se encuentra
                
        except Exception as e:
            print(f"❌ Error determinando severidad FQ para RUT {rut}: {e}")
            return "leve"

    def esta_en_poblacion_ges(self, rut):
        """
        Verificar si un RUT está en la población GES
        
        Args:
            rut (str): RUT del paciente
            
        Returns:
            bool: True si está en población GES, False si no
        """
        if self.ges_df is None or self.ges_df.empty:
            return False
            
        try:
            # Normalizar el RUT de entrada
            rut_str = str(rut).strip()
            if '-' in rut_str:
                rut_numero = int(rut_str.split('-')[0])
            else:
                rut_numero = int(rut_str)
                
            # Buscar en población GES usando diferentes posibles nombres de columna
            for col in ['RUT', 'Rut', 'rut', 'RUT_PACIENTE']:
                if col in self.ges_df.columns:
                    # Buscar por RUT numérico
                    match = self.ges_df[self.ges_df[col] == rut_numero]
                    if not match.empty:
                        return True
                    
                    # Buscar por RUT completo (con DV)
                    match = self.ges_df[self.ges_df[col].astype(str) == rut_str]
                    if not match.empty:
                        return True
            
            return False
            
        except (ValueError, TypeError):
            return False

    def determinar_tipo_paliativo(self, rut):
        """
        Determina si un paciente con paliativos es progresivo o no progresivo.
        SOLO procesa pacientes que estén en la población GES.
        Si hay campos vacíos, reporta el caso sin asignar categoría por defecto.
        Maneja RUTs con formato "12345678-9" y sin dígito verificador.
        Returns: 'progresivo', 'no_progresivo', 'campo_vacio', 'no_ges' o None si hay error
        """
        try:
            # PRIMERO verificar si está en población GES
            if not self.esta_en_poblacion_ges(rut):
                return "no_ges"
                
            if self.clasificacion_paliativos_df is None:
                print(f"⚠️ RUT {rut}: No se encontró clasificación paliativos, usando NO PROGRESIVO por defecto")
                return "no_progresivo"
            
            # Extraer solo la parte numérica del RUT (sin dígito verificador)
            try:
                rut_str = str(rut).strip()
                # Si el RUT tiene formato "12345678-9", extraer solo la parte antes del guión
                if '-' in rut_str:
                    rut_numero = rut_str.split('-')[0]
                else:
                    rut_numero = rut_str
                
                # Convertir a entero
                rut_int = int(rut_numero)
                print(f"🔬 DEBUG PALIATIVO: RUT original '{rut}' → RUT procesado '{rut_int}'")
                
            except ValueError:
                print(f"⚠️ PALIATIVO RUT INVÁLIDO: {rut} - No se puede extraer número del RUT")
                return None
            
            # Buscar el RUT en el archivo de clasificación usando diferentes posibles columnas
            rut_column = None
            for col in ['RUT', 'Rut', 'rut']:
                if col in self.clasificacion_paliativos_df.columns:
                    rut_column = col
                    break
            
            if rut_column is None:
                print(f"⚠️ PALIATIVO SIN COLUMNA RUT: RUT {rut} - No se encontró columna RUT en la BD")
                return None
            
            # Buscar por RUT numérico (sin DV)
            clasificacion_row = self.clasificacion_paliativos_df[self.clasificacion_paliativos_df[rut_column] == rut_int]
            
            # Si no encuentra por número, intentar buscar por RUT completo (con DV)
            if clasificacion_row.empty:
                clasificacion_row = self.clasificacion_paliativos_df[self.clasificacion_paliativos_df[rut_column] == rut_str]
            
            if not clasificacion_row.empty:
                # Determinar cuál columna usar para el tipo/condición
                tipo_column = None
                for col in ['condicion', 'Tipo', 'tipo', 'Condicion']:
                    if col in self.clasificacion_paliativos_df.columns:
                        tipo_column = col
                        break
                
                if tipo_column is None:
                    print(f"⚠️ PALIATIVO SIN COLUMNA TIPO: RUT {rut} - No se encontró columna de tipo/condición")
                    return None
                
                tipo_raw = clasificacion_row.iloc[0][tipo_column]
                
                # Verificar si el campo está vacío o es NaN
                if pd.isna(tipo_raw) or str(tipo_raw).strip() == '' or str(tipo_raw).lower() in ['nan', 'none', 'null']:
                    print(f"⚠️ PALIATIVO CAMPO VACÍO: RUT {rut} - Campo '{tipo_column}' está vacío en la base de datos")
                    return "campo_vacio"
                
                condicion = str(tipo_raw).upper().strip()
                
                # Mapear códigos de condición según nueva lógica:
                # TODOS son progresivos EXCEPTO: CP-NO, DC-NO, DO NO, NP
                if condicion in ['CP-NO', 'DC-NO', 'DO NO', 'NP']:
                    # Estos específicos son no progresivos
                    print(f"🎯 PALIATIVO NO PROGRESIVO: RUT {rut} - Condición '{condicion}'")
                    return "no_progresivo"
                else:
                    # Todos los demás (I, D, T, E, etc.) son progresivos
                    print(f"🎯 PALIATIVO PROGRESIVO: RUT {rut} - Condición '{condicion}'")
                    return "progresivo"
            else:
                print(f"⚠️ RUT {rut}: No se encontró clasificación paliativos, usando NO PROGRESIVO por defecto")
                return "no_progresivo"
                
        except Exception as e:
            print(f"❌ Error determinando tipo paliativo para RUT {rut}: {e}")
            return None

    def load_recetas_ges(self):
        """Cargar archivos de recetas GES (prescripciones por patología)"""
        if 'recetas_ges' not in self.selected_files or not self.selected_files['recetas_ges']:
            print("⚠️  No se encontraron archivos de recetas GES")
            return
        
        recetas_files = self.selected_files['recetas_ges']
        if not isinstance(recetas_files, list):
            recetas_files = [recetas_files]
        
        print(f"\n💊 CARGANDO ARCHIVOS DE RECETAS GES...")
        
        all_recetas = []
        for filepath in recetas_files:
            try:
                filename = os.path.basename(filepath)
                print(f"  📄 Procesando: {filename}")
                
                # Leer archivo Excel o HTML (muchos .xls son HTML descargados)
                df = None
                try:
                    if filepath.endswith('.xls'):
                        df = pd.read_excel(filepath, engine='xlrd')
                    else:
                        df = pd.read_excel(filepath)
                except Exception as xls_error:
                    # Si falla, intentar como HTML (muchos .xls descargados son HTML)
                    try:
                        print(f"    ℹ️  Leyendo como HTML (archivo no es XLS válido)...")
                        all_tables = pd.read_html(filepath)
                        # La tabla 0 es metadata, la tabla 1 es los datos reales
                        if len(all_tables) >= 2:
                            df = all_tables[1]
                        elif len(all_tables) == 1:
                            df = all_tables[0]
                        else:
                            raise Exception("No se encontraron tablas HTML")
                        
                        # Si las columnas son numéricas [0,1,2...], la primera fila tiene los nombres
                        if len(df) > 0 and all(isinstance(col, int) for col in df.columns):
                            # Usar primera fila como encabezados
                            header_row = df.iloc[0].tolist()
                            df.columns = header_row
                            df = df[1:].reset_index(drop=True)
                    except Exception as html_error:
                        raise Exception(f"No se pudo leer como XLS ni HTML: {xls_error} / {html_error}")
                
                if df is None or df.empty:
                    print(f"    ❌ DataFrame vacío después de leer {filename}")
                    continue
                
                # Mapear nombres de columnas a formato estándar
                column_mapping = {
                    'FECHA': 'FechaEmision',
                    'FECHA EMISIÓN': 'FechaEmision',
                    'FECHA EMISION': 'FechaEmision',
                    'RUT': 'RutPaciente',
                    'RUT PACIENTE': 'RutPaciente',
                    'DÍGITO': 'DVPaciente',
                    'DÍGITO PACIENTE': 'DVPaciente',
                    'DIGITO': 'DVPaciente',
                    'DIGITO PACIENTE': 'DVPaciente',
                    'NOMBRE MEDICAMENTO': 'Farmaco_Desc',
                    'MEDICAMENTO': 'Farmaco_Desc',
                    'MEDICAMENTOS': 'Farmaco_Desc',
                    'NOMBRE MEDICINA': 'Farmaco_Desc',
                    'CANT.': 'CantidadDespachada',
                    'CANT': 'CantidadDespachada',
                    'CANTIDAD': 'CantidadDespachada',
                    'POLICLÍNICO': 'LocalSolicitante',
                    'POLICLINICO': 'LocalSolicitante',
                    'NOMBRE PACIENTE': 'NombrePaciente',
                    'NOMBRE': 'NombrePaciente',
                    'EDAD': 'EdadPaciente',
                    'PREVISIÓN': 'Prevision',
                    'PREVISION': 'Prevision',
                    'UM': 'UnidadMedida',
                    'UNIDAD': 'UnidadMedida',
                    'DURACIÓN': 'DuracionReceta',
                    'DURACIÓN RECETA': 'DuracionReceta',
                    'DURACION': 'DuracionReceta',
                    'DURACION RECETA': 'DuracionReceta',
                    'COMUNA': 'Comuna',
                }
                
                # Renombrar columnas (case-insensitive)
                df.columns = df.columns.str.upper()
                df_renamed = df.rename(columns=column_mapping)
                
                # Normalizar DV a mayúsculas
                df_renamed = self.normalize_dv_in_dataframe(df_renamed)
                
                # Verificar columnas críticas
                required = ['FechaEmision', 'RutPaciente', 'DVPaciente', 'Farmaco_Desc']
                missing = [col for col in required if col not in df_renamed.columns]
                
                if missing:
                    print(f"    ⚠️  Columnas faltantes en {filename}: {missing}")
                    print(f"    Columnas disponibles: {list(df.columns)}")
                    continue
                
                # Agregar columna RUT_Combined
                df_renamed['RUT_Combined'] = df_renamed.apply(
                    lambda row: self.format_rut(row['RutPaciente'], row['DVPaciente']),
                    axis=1
                )
                
                # Marcar origen como 'recetas'
                df_renamed['_origen'] = 'recetas'
                
                all_recetas.append(df_renamed)
                print(f"    ✅ Cargadas {len(df_renamed)} prescripciones")
                
            except Exception as e:
                print(f"    ❌ Error cargando {filepath}: {e}")
                continue
        
        if all_recetas:
            self.recetas_ges_df = pd.concat(all_recetas, ignore_index=True)
            self.recetas_ges_df = self.recetas_ges_df.dropna(subset=['RUT_Combined'])
            print(f"✅ Total recetas GES cargadas: {len(self.recetas_ges_df)} registros")
            print(f"   Pacientes únicos: {self.recetas_ges_df['RUT_Combined'].nunique()}")
        else:
            print("⚠️  No se pudieron cargar archivos de recetas GES")
            self.recetas_ges_df = None

    def load_csv_safely(self, filename, separator=";"):
        """Cargar CSV con manejo de errores y normalización de DV"""
        try:
            df = pd.read_csv(filename, sep=separator, encoding="latin-1", on_bad_lines="skip")
            
            # Normalizar DV a mayúsculas si existe columna DV
            dv_columns = [col for col in df.columns if col.upper().strip() in ['DV', 'DIGITO', 'DÍGITO', 'DVV']]
            for col in dv_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.upper()
            
            return df
        except Exception as e:
            print(f"❌ Error cargando {filename}: {e}")
            return None

    def format_rut(self, rut_number, dv):
        """Formatear RUT"""
        if pd.isna(rut_number) or pd.isna(dv):
            return None
        try:
            # Convert float to int if needed
            if isinstance(rut_number, float):
                rut_number = int(rut_number)
            # Clean DV and normalize to uppercase (K can be lowercase or uppercase)
            dv = str(dv).strip().upper()
            return f"{rut_number}-{dv}"
        except:
            return None

    def normalize_dv_in_dataframe(self, df):
        """Normalizar columnas DV a mayúsculas en un dataframe"""
        if df is None:
            return df
        
        # Buscar columnas DV/DígitoDV (varias variaciones posibles)
        dv_col_variations = ['DV', 'DVPaciente', 'DIGITO', 'DÍGITO', 'DV_PACIENTE', 'DIGITO_PACIENTE', 'DVV']
        
        for col in df.columns:
            if col.upper() in [v.upper() for v in dv_col_variations]:
                if col in df.columns and df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip().str.upper()
        
        return df

    def get_ges_condition(self, rut):
        """Obtener condición GES de un paciente"""
        if self.ges_df is None:
            return None

        # Aceptar rut como '12345678' o '12345678-1' y tratar ambos casos
        rut_str = str(rut)
        posibles = {rut_str}
        if "-" in rut_str:
            posibles.add(rut_str.split("-")[0])
        # Buscar coincidencias en la columna RUT (comparando la parte numérica y/o completa)
        patient_info = self.ges_df[self.ges_df["RUT"].astype(str).isin(posibles)]
        if len(patient_info) > 0:
            # Determinar el nombre de la columna de patología
            patologia_col = "Ges" if "Ges" in self.ges_df.columns else "Patologia"
            return patient_info.iloc[0][patologia_col]
        return None

    def get_codigo_prestacion(self, condition):
        """Obtener código de prestación GES"""
        return CODIGOS_PRESTACION_GES.get(condition, "")

    def get_codigo_familia(self, condition):
        """Obtener código de familia"""
        # Ya no usamos códigos fijos, usamos las columnas EspecialidadLocal y LocalSolicitante
        return (
            ""  # Se define en las funciones específicas get_cod_fam_consulta y get_cod_fam_farmacia
        )

    def analizar_medicamentos_ges(self):
        """Analizar qué medicamentos administrados están en el listado GES"""
        if self.medicamentos_ges_df is None or self.farmacia_df is None:
            print("❌ No se pueden analizar medicamentos: datos faltantes")
            return

        print("\n🔍 ANALIZANDO MEDICAMENTOS GES...")

        # Obtener lista de medicamentos GES (asumiendo que hay una columna de nombre)
        # Nota: Ajustar según la estructura real del archivo
        if "Farmaco_Desc" in self.medicamentos_ges_df.columns:
            medicamentos_ges_list = set(self.medicamentos_ges_df["Farmaco_Desc"].str.upper())
        elif "Medicamento" in self.medicamentos_ges_df.columns:
            medicamentos_ges_list = set(self.medicamentos_ges_df["Medicamento"].str.upper())
        else:
            # Usar la primera columna como medicamentos
            medicamentos_ges_list = set(self.medicamentos_ges_df.iloc[:, 0].str.upper())

        print(f"📋 Medicamentos en listado GES: {len(medicamentos_ges_list)}")

        # Verificar que tenemos datos de población GES
        if self.ges_df is None:
            print("❌ No hay datos de población GES")
            return

        # Filtrar solo pacientes GES (excluyendo paliativos)
        ges_patients = set(self.ges_df["RUT"].astype(str))
        # Determinar el nombre de la columna de patología
        patologia_col = "Ges" if "Ges" in self.ges_df.columns else "Patologia"
        no_paliativos = self.ges_df[self.ges_df[patologia_col] != "Paliativos"]["RUT"].astype(str)
        ges_no_paliativos = set(no_paliativos)

        # Analizar medicamentos administrados a pacientes GES no paliativos
        farmacia_ges = self.farmacia_df[self.farmacia_df["RUT_Combined"].isin(ges_no_paliativos)]

        medicamentos_administrados = farmacia_ges["Farmaco_Desc"].str.upper()

        # Encontrar coincidencias
        coincidencias = []
        no_coincidencias = []

        for med_admin in medicamentos_administrados.unique():
            if pd.isna(med_admin):
                continue

            encontrado = False
            for med_ges in medicamentos_ges_list:
                if pd.isna(med_ges):
                    continue
                # Buscar coincidencias parciales (medicamento GES contenido en administrado)
                if med_ges in med_admin or self.similar_medicine_name(med_admin, med_ges):
                    coincidencias.append(
                        {
                            "medicamento_administrado": med_admin,
                            "medicamento_ges": med_ges,
                            "pacientes": len(
                                farmacia_ges[farmacia_ges["Farmaco_Desc"].str.upper() == med_admin]
                            ),
                        }
                    )
                    encontrado = True
                    break

            if not encontrado:
                no_coincidencias.append(
                    {
                        "medicamento_administrado": med_admin,
                        "pacientes": len(
                            farmacia_ges[farmacia_ges["Farmaco_Desc"].str.upper() == med_admin]
                        ),
                    }
                )

        self.medicamentos_encontrados = {
            "coincidencias": coincidencias,
            "no_coincidencias": no_coincidencias,
            "total_ges": len(medicamentos_ges_list),
            "total_administrados": len(medicamentos_administrados.unique()),
        }

        print(f"✅ Medicamentos GES encontrados: {len(coincidencias)}")
        print(f"❓ Medicamentos no en listado GES: {len(no_coincidencias)}")

    def similar_medicine_name(self, name1, name2):
        """Verificar si dos nombres de medicamentos son similares"""
        # Simplificar nombres eliminando espacios y comparar palabras clave
        words1 = set(name1.replace("-", " ").split())
        words2 = set(name2.replace("-", " ").split())

        # Si hay más del 60% de palabras en común, considerar similar
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if len(union) == 0:
            return False

        similarity = len(intersection) / len(union)
        return similarity > 0.6

    def get_cod_fam_consulta(self, row):
        """
        Obtiene el código de familia para consultas usando EspecialidadLocal
        """
        try:
            return str(row.get("EspecialidadLocal", "")).strip()
        except:
            return ""

    def get_cod_fam_farmacia(self, row):
        """
        Obtiene el código de familia para farmacia usando LocalSolicitante
        y limpia el formato eliminando prefijos y sufijos
        """
        try:
            cod_fam = str(row.get("LocalSolicitante", "")).strip()

            # Limpiar formato: eliminar "INT-" al inicio
            if cod_fam.startswith("INT-"):
                cod_fam = cod_fam[4:]  # Eliminar "INT-"

            # Eliminar sufijos complejos usando regex
            import re

            # Eliminar patrones como: -R, -P, -A, -PS, A, B, A2, etc. al final
            cod_fam = re.sub(r"(-[A-Z]+|-PS|[A-Z]\d*|\s+[A-Z]\d*|\s+[A-Z]+)$", "", cod_fam)
            # Limpiar espacios extra
            cod_fam = cod_fam.strip()

            return cod_fam
        except:
            return ""

    def procesar_consultas_para_carga(self, df_consultas, archivo_salida):
        """Procesar consultas para generar archivo de carga"""
        if df_consultas is None:
            print("ERROR - No hay datos de consultas para procesar")
            return

        if self.ges_df is None:
            print("ERROR - No hay datos de población GES cargados")
            return

        print("\n INFO - PROCESANDO CONSULTAS PARA CARGA...")

        ges_patients = set(self.ges_df["RUT"].astype(str))

        # Filtrar solo pacientes GES
        consultas_ges = df_consultas[df_consultas["RUNPaciente"].astype(str).isin(ges_patients)]

        # Filtrar solo consultas atendidas o que llegaron
        estados_validos = ["Atendido", "Llegó"]
        consultas_validas = consultas_ges[consultas_ges["EstadoCita_Desc"].isin(estados_validos)]

        print(f"INFO - Consultas totales GES: {len(consultas_ges)}")
        print(f"INFO - Consultas atendidas/llegó: {len(consultas_validas)}")

        # Aplicar filtro de especialidades GES válidas
        consultas_especialidad_valida = self.filtrar_consultas_especialidades_ges(consultas_validas)
        
        print(f"INFO - Consultas con especialidad GES válida: {len(consultas_especialidad_valida)}")

        consultas_procesadas = []

        # Agrupar consultas por RUT para manejar duplicados
        consultas_agrupadas = {}

        for _, consulta in consultas_especialidad_valida.iterrows():
            rut_paciente = str(consulta["RUNPaciente"])
            condition = self.get_ges_condition(rut_paciente)

            if condition:
                # Determinar código trazadora basado en tipo de consulta
                prestacion_code = self.determinar_codigo_trazadora_consulta(consulta, condition)

                # Obtener COD_FAM según nuevos requerimientos
                cod_fam_normalizado = self.get_cod_fam_consulta_actualizado(consulta, condition)

                registro = {
                    "FECHA": self.format_date_for_excel(consulta["FechaCita"]),
                    "RUT": self.extract_rut_number(rut_paciente),
                    "DV": self.extract_rut_dv(rut_paciente),
                    "PRESTACION": prestacion_code,
                    "TIPO": "AUGE",  # Cambiar a AUGE en lugar de abreviaturas
                    "PS-FAM ": self.get_codigo_prestacion(condition),
                    "ESPECIALIDAD": cod_fam_normalizado,
                }

                # Agrupar por RUT
                if rut_paciente not in consultas_agrupadas:
                    consultas_agrupadas[rut_paciente] = []
                consultas_agrupadas[rut_paciente].append(registro)

        # Procesar agrupación por RUT para evitar duplicados
        print(f"INFO - Deduplicando consultas por RUT y especialidad...")
        for rut, consultas_rut in consultas_agrupadas.items():
            consultas_finales = self.agrupar_consultas_por_rut(consultas_rut)
            consultas_procesadas.extend(consultas_finales)

        # Crear DataFrame y guardar archivo en formato Excel
        if consultas_procesadas:
            df_resultado = pd.DataFrame(consultas_procesadas)
            
            # Cambiar extensión a .xlsx para Excel
            archivo_excel = archivo_salida.replace('.csv', '.xlsx')
            
            # Guardar en formato Excel usando chunking (500 filas por archivo)
            self.save_df_in_chunks(df_resultado, archivo_excel, chunk_size=499)
            print(f"OK - Archivo(s) de consultas generados a partir: {archivo_excel}")
            print(f"OK - Total consultas procesadas (deduplicadas): {len(consultas_procesadas)}")
            print(f"OK - Pacientes únicos con consultas: {len(consultas_agrupadas)}")
        else:
            print("WARNING - No se encontraron consultas para procesar")

    def filtrar_consultas_especialidades_ges(self, df_consultas):
        """Filtrar consultas para incluir solo especialidades válidas para GES por patología"""
        from ges_config import es_especialidad_ges_valida
        
        consultas_filtradas = []
        
        for _, consulta in df_consultas.iterrows():
            rut_paciente = str(consulta["RUNPaciente"])
            condition = self.get_ges_condition(rut_paciente)
            codigo_especialidad = consulta.get("EspecialidadLocal", "")
            
            if condition and es_especialidad_ges_valida(codigo_especialidad, condition):
                consultas_filtradas.append(consulta)
        
        if consultas_filtradas:
            return pd.DataFrame(consultas_filtradas)
        else:
            # Retornar DataFrame vacío con las mismas columnas
            return pd.DataFrame(columns=df_consultas.columns)

    def procesar_medicamentos_para_carga(self, df_farmacia, archivo_salida):
        """Procesar medicamentos para generar archivo de carga con agrupación por RUT"""
        if df_farmacia is None and self.recetas_ges_df is None:
            print("❌ No hay datos de farmacia ni recetas GES para procesar")
            return

        if self.ges_df is None:
            print("❌ No hay datos de población GES cargados")
            return

        print("\n💊 PROCESANDO MEDICAMENTOS PARA CARGA...")
        
        # Combinar datos de farmacia y recetas GES si ambos existen
        if df_farmacia is not None and self.recetas_ges_df is not None:
            print("🔄 Combinando datos de farmacia y recetas GES...")
            # Asegurar que farmacia tenga la columna _origen
            if '_origen' not in df_farmacia.columns:
                df_farmacia['_origen'] = 'farmacia'
            # Combinar ambos DataFrames
            df_medicamentos_combined = pd.concat([df_farmacia, self.recetas_ges_df], ignore_index=True)
            print(f"   Total registros combinados: {len(df_medicamentos_combined)}")
        elif df_farmacia is not None:
            df_medicamentos_combined = df_farmacia.copy()
            if '_origen' not in df_medicamentos_combined.columns:
                df_medicamentos_combined['_origen'] = 'farmacia'
        else:
            df_medicamentos_combined = self.recetas_ges_df.copy()

        # Asegurar que exista la columna RUT_Combined (cuando se pasa un df manual en tests)
        if "RUT_Combined" not in df_medicamentos_combined.columns:
            df_medicamentos_combined["RUT_Combined"] = [
                self.format_rut(row["RutPaciente"], row["DVPaciente"]) for _, row in df_medicamentos_combined.iterrows()
            ]
            df_medicamentos_combined = df_medicamentos_combined.dropna(subset=["RUT_Combined"])

        # Separar pacientes GES de no-GES
        # Los RUTs en GES ya vienen en formato "{numero}-{dv}", usar directamente
        try:
            ges_patients = set(self.ges_df["RUT"].astype(str))
        except Exception:
            ges_patients = set()
        
        farmacia_ges = df_medicamentos_combined[df_medicamentos_combined["RUT_Combined"].isin(ges_patients)]
        farmacia_no_ges = df_medicamentos_combined[~df_medicamentos_combined["RUT_Combined"].isin(ges_patients)]

        # Lista para casos de revisión (no-GES con medicamentos especiales)
        casos_revision = []
        
        medicamentos_procesados = []

        # Procesar medicamentos por RUT para manejar duplicados
        medicamentos_agrupados = {}
        # Registrar medicamentos sin fecha de despacho para revisión
        casos_sin_fecha = []

        for _, medicamento in farmacia_ges.iterrows():
            try:
                rut_paciente = medicamento["RUT_Combined"]
                condition = self.get_ges_condition(rut_paciente)

                if condition:
                    # Determinar código trazadora basado en medicamento
                    # IMPORTANTE: Convertir pandas Series a dict para funciones de trazadora
                    medicamento_dict = medicamento.to_dict() if hasattr(medicamento, 'to_dict') else medicamento
                    prestacion_code = self.determinar_codigo_trazadora_medicamento(
                        medicamento_dict, condition
                    )
                    
                    # Si prestacion_code es None, saltar este medicamento (ej: paliativos con campos vacíos)
                    if prestacion_code is None:
                        continue

                    # Obtener COD_FAM según nuevos requerimientos para medicamentos
                    cod_fam = self.get_cod_fam_medicamento_actualizado(medicamento, condition)

                    # Verificar campos requeridos: usar la fecha según el origen
                    # - FechaDespacho para datos de farmacia (despacho real)
                    # - FechaEmision para datos de recetas GES (prescripciones)
                    origen = medicamento.get("_origen", "farmacia")
                    if origen == "recetas":
                        fecha_medicamento = medicamento.get("FechaEmision", "")
                    else:
                        fecha_medicamento = medicamento.get("FechaDespacho", "")
                    
                    if pd.isna(fecha_medicamento):
                        fecha_medicamento = ""

                    # Si no hay fecha, registrar el caso y omitirlo del output
                    if not fecha_medicamento or str(fecha_medicamento).strip() == "":
                        casos_sin_fecha.append({
                            "RUT_Combined": rut_paciente,
                            "Farmaco_Desc": medicamento.get("Farmaco_Desc", ""),
                            "CantidadDespachada": medicamento.get("CantidadDespachada", ""),
                            "LocalSolicitante": medicamento.get("LocalSolicitante", ""),
                            "Fecha": fecha_medicamento,
                            "Origen": origen,
                        })
                        # Omitir este registro
                        continue

                    # Usar datetime object para FECHA (igual que en consultas)
                    fecha_formateada = None
                    try:
                        fecha_formateada = self.format_date_for_excel(fecha_medicamento)
                    except Exception:
                        fecha_formateada = datetime.now()

                    registro = {
                        "FECHA": fecha_formateada,
                        "RUT": self.extract_rut_number(rut_paciente),
                        "DV": self.extract_rut_dv(rut_paciente),
                        "PRESTACION": prestacion_code,
                        "TIPO": "AUGE",  # Cambiar a AUGE en lugar de ME
                        "PS-FAM ": self.get_codigo_prestacion(condition),
                        "ESPECIALIDAD": cod_fam,
                        "MEDICAMENTO": medicamento.get("Farmaco_Desc", ""),
                    }

                    # Agrupar por RUT
                    if rut_paciente not in medicamentos_agrupados:
                        medicamentos_agrupados[rut_paciente] = []
                    medicamentos_agrupados[rut_paciente].append(registro)
                    
            except Exception as e:
                print(f"⚠️ Error procesando medicamento para RUT {medicamento.get('RUT_Combined', 'N/A')}: {e}")
                continue

        # PROCESAR CASOS NO-GES PARA REVISIÓN
        print(f"🔍 Identificando casos NO-GES con medicamentos especiales...")
        codigos_especiales = ['3002023', '3002123']  # Códigos de paliativos
        
        for _, medicamento in farmacia_no_ges.iterrows():
            try:
                rut_paciente = medicamento["RUT_Combined"]
                
                # Verificar si es un medicamento especial que requiere revisión
                medicamento_dict = medicamento.to_dict() if hasattr(medicamento, 'to_dict') else medicamento
                farmaco_desc = str(medicamento.get("Farmaco_Desc", "")).upper()
                
                # Detectar si es paliativo u otro medicamento especial
                es_especial = False
                tipo_medicamento = ""
                
                if any(keyword in farmaco_desc for keyword in ['MORFINA', 'FENTANILO', 'TRAMADOL', 'OXICODONA']):
                    es_especial = True
                    tipo_medicamento = "PALIATIVO"
                elif any(keyword in farmaco_desc for keyword in ['SALBUTAMOL', 'BECLOMETASONA', 'BUDESONIDA']):
                    es_especial = True
                    tipo_medicamento = "ASMA"
                elif any(keyword in farmaco_desc for keyword in ['TOBRAMICINA', 'COLISTINA']):
                    es_especial = True
                    tipo_medicamento = "FIBROSIS_QUISTICA"
                
                if es_especial:
                    caso_revision = {
                        "RUT": rut_paciente,
                        "FARMACO": medicamento.get("Farmaco_Desc", ""),
                        "TIPO_MEDICAMENTO": tipo_medicamento,
                        "FECHA_DESPACHO": medicamento.get("FechaDespacho", ""),
                        "MOTIVO": "PACIENTE NO ESTÁ EN POBLACIÓN GES",
                        "ACCION_REQUERIDA": "VERIFICAR SI DEBE INCLUIRSE EN GES"
                    }
                    casos_revision.append(caso_revision)
                    
            except Exception as e:
                print(f"⚠️ Error procesando caso no-GES para RUT {medicamento.get('RUT_Combined', 'N/A')}: {e}")
                continue

        # Guardar casos de revisión si los hay
        if casos_revision:
            archivo_revision = archivo_salida.replace('.xlsx', '_CASOS_REVISION.xlsx').replace('.csv', '_CASOS_REVISION.xlsx')
            df_revision = pd.DataFrame(casos_revision)
            # Guardar archivo de revisión (particionado si es necesario)
            self.save_df_in_chunks(df_revision, archivo_revision, chunk_size=499)
            print(f"⚠️ CASOS PARA REVISIÓN: {len(casos_revision)} casos guardados en {archivo_revision}")
            print(f"   Estos pacientes NO están en población GES pero reciben medicamentos especiales")

        # Guardar lista de medicamentos sin fecha si existen
        if casos_sin_fecha:
            archivo_sin_fecha = archivo_salida.replace('.xlsx', '_SIN_FECHA.xlsx').replace('.csv', '_SIN_FECHA.xlsx')
            df_sin_fecha = pd.DataFrame(casos_sin_fecha)
            self.save_df_in_chunks(df_sin_fecha, archivo_sin_fecha, chunk_size=499)
            print(f"⚠️ MEDICAMENTOS SIN FECHA: {len(casos_sin_fecha)} casos guardados en {archivo_sin_fecha}")

        # Procesar agrupación por RUT manteniendo códigos excluyentes separados
        print(f"📋 Agrupando medicamentos por RUT...")
        for rut, medicamentos_rut in medicamentos_agrupados.items():
            medicamentos_finales = self.agrupar_medicamentos_por_rut(medicamentos_rut)
            medicamentos_procesados.extend(medicamentos_finales)

        # Crear DataFrame y guardar archivo en formato Excel
        if medicamentos_procesados:
            df_resultado = pd.DataFrame(medicamentos_procesados)
            # Eliminar la columna auxiliar MEDICAMENTO antes de guardar
            if "MEDICAMENTO" in df_resultado.columns:
                df_resultado = df_resultado.drop("MEDICAMENTO", axis=1)

            # Eliminar filas donde la primera columna FECHA esté vacía o nula
            if "FECHA" in df_resultado.columns:
                conteo_before = len(df_resultado)
                df_resultado = df_resultado[~(df_resultado["FECHA"].isnull() | (df_resultado["FECHA"].astype(str).str.strip() == ""))]
                removed = conteo_before - len(df_resultado)
                if removed > 0:
                    print(f"⚠️ Se eliminaron {removed} filas sin fecha del output final")

            # Cambiar extensión a .xlsx para Excel
            archivo_excel = archivo_salida.replace('.csv', '.xlsx')
            
            # Guardar en formato Excel usando chunking (500 filas por archivo)
            self.save_df_in_chunks(df_resultado, archivo_excel, chunk_size=499)
            print(f"✅ Archivo(s) de medicamentos generados a partir: {archivo_excel}")
            print(f"✅ Medicamentos procesados: {len(medicamentos_procesados)}")
            print(f"✅ Medicamentos únicos por RUT: {len(medicamentos_agrupados)}")
        else:
            print("❌ No se encontraron medicamentos para procesar")

    def determinar_codigo_trazadora_consulta(self, consulta, condition):
        """Determinar código trazadora para consulta usando datos del arancel"""
        try:
            # Obtener la especialidad de la consulta con manejo robusto
            especialidad = consulta.get("EspecialidadLocal", "")
            if pd.isna(especialidad):
                especialidad = ""
            else:
                especialidad = str(especialidad).strip()

            # Usar el procesador de trazadoras para obtener código dinámico del arancel
            if hasattr(self.trazadora_processor, "determinar_trazadora_consulta"):
                # Pasar información adicional del paciente para diferenciación con manejo robusto
                rut_raw = consulta.get("RUNPaciente", "")
                if pd.isna(rut_raw):
                    rut_paciente = ""
                else:
                    rut_paciente = str(rut_raw).strip()
                    
                trazadora = self.trazadora_processor.determinar_trazadora_consulta(
                    especialidad, condition, rut_paciente
                )
                return trazadora
            else:
                # Fallback al código fijo si no está disponible el procesador
                if condition in CODIGOS_TRAZADORA:
                    return CODIGOS_TRAZADORA[condition]["consultas"].get(
                        "consulta_especialidad", "0101322"
                    )
                return "0101322"

        except Exception as e:
            print(f"⚠️ Error al determinar trazadora de consulta: {e}")
            return "0101322"  # Código por defecto

    def determinar_codigo_trazadora_medicamento(self, medicamento, condition):
        """Determinar código trazadora para medicamento usando datos del arancel"""
        try:
            # Manejar tanto diccionarios como cadenas
            if isinstance(medicamento, dict):
                # Buscar el campo del medicamento en diferentes posibles nombres
                medicamento_desc = ""
                possible_fields = ["Farmaco_Desc", "MEDICAMENTO", "medicamento", "Farmaco", "FARMACO"]
                
                for field in possible_fields:
                    if field in medicamento and medicamento[field] and str(medicamento[field]).strip():
                        medicamento_desc = str(medicamento[field])
                        print(f"🔬 DEBUG: Usando campo '{field}' = '{medicamento_desc[:50]}...'")
                        break
                
                if not medicamento_desc:
                    # Si no encontramos ningún campo específico, buscar cualquier campo que contenga medicina
                    for key, value in medicamento.items():
                        if value and str(value).strip() and key.lower() in ["farmaco_desc", "medicamento", "farmaco"]:
                            medicamento_desc = str(value)
                            print(f"🔬 DEBUG: Campo fallback '{key}' = '{medicamento_desc[:50]}...'")
                            break
                
                rut_paciente = str(medicamento.get("RUNPaciente", "") or medicamento.get("RUT", "") or medicamento.get("RutPaciente", ""))
            else:
                medicamento_desc = str(medicamento)
                rut_paciente = ""
            
            # Para PALIATIVOS: Usar nuestra función mejorada que maneja campos vacíos
            if condition == "Paliativos":
                tipo_paliativo = self.determinar_tipo_paliativo(rut_paciente)
                
                if tipo_paliativo == "progresivo":
                    return "3002023"  # Progresivo - cáncer terminal
                elif tipo_paliativo == "no_progresivo":
                    return "3002123"  # No progresivo - tratamiento integral
                elif tipo_paliativo == "campo_vacio":
                    print(f"⚠️ PALIATIVO SKIPPED: RUT {rut_paciente} - Campo vacío, saltando procesamiento")
                    return None  # Saltar este medicamento
                else:  # tipo_paliativo es None (no encontrado o error)
                    print(f"⚠️ PALIATIVO SKIPPED: RUT {rut_paciente} - No encontrado en BD, saltando procesamiento")
                    return None  # Saltar este medicamento
            
            # Para FIBROSIS: Usar severidad específica Y mapeo por medicamento mejorado
            elif condition == "Fibrosis":
                # Mapeo específico de medicamentos FQ con detección mejorada
                medicamento_lower = medicamento_desc.lower()
                
                # TOBRAMICINA - detección ampliada para diferentes presentaciones
                if any(keyword in medicamento_lower for keyword in [
                    "tobramicina", "tobrex", "bramitob", "nebcin"
                ]):
                    return "3004004"  # TRATAMIENTO FARMACOLOGICO CON TOBRAMICINA
                
                # Usar severidad para el resto de medicamentos
                if rut_paciente:
                    try:
                        severidad = self.determinar_severidad_fq(int(rut_paciente))
                    except:
                        severidad = "leve"  # Por defecto si hay error
                else:
                    severidad = "leve"  # Por defecto
                
                if severidad == "grave":
                    return "2505256"  # TRATAMIENTO FIBROSIS QUISTICA GRAVE
                elif severidad == "moderada":
                    return "2505260"  # TRATAMIENTO FIBROSIS QUISTICA MODERADA
                else:  # leve
                    return "2505263"  # TRATAMIENTO FIBROSIS QUISTICA LEVE
            
            # Para EPOC: Usar nueva trazadora
            elif condition == "EPOC":
                return "3801002"  # Nueva trazadora EPOC medicamentos
            
            # Para ASMA: Mapear por medicamento específico con detección mejorada
            elif condition == "ASMA":
                medicamento_lower = medicamento_desc.lower()
                print(f"🔬 DEBUG ASMA: {medicamento_desc[:50]}... → lower: {medicamento_lower[:50]}...")
                
                # Mapeo específico de medicamentos ASMA según arancel (orden de prioridad)
                # 1. SALBUTAMOL - broncodilatador específico
                if "salbutamol" in medicamento_lower:
                    print(f"🎯 DETECTADO SALBUTAMOL → 3902001")
                    return "3902001"  # SALBUTAMOL 200 DOSIS (100 UG)
                
                # 2. TEOFILINA - broncodilatador oral
                elif "teofilina" in medicamento_lower or "aminofilina" in medicamento_lower:
                    print(f"🎯 DETECTADO TEOFILINA → 3902003")
                    return "3902003"  # TEOFILINA ANH CM 200MG
                
                # 3. PREDNISONA - corticoesteroide oral
                elif "prednizona" in medicamento_lower or "prednisona" in medicamento_lower:
                    print(f"🎯 DETECTADO PREDNISONA → 3902004")
                    return "3902004"  # PREDNISONA 5 MG
                
                # 4. IPRATROPIO - anticolinérgico
                elif "ipratropio" in medicamento_lower or "ipatropio" in medicamento_lower:
                    print(f"🎯 DETECTADO IPRATROPIO → 3902006")
                    return "3902006"  # IPRATROPIO BROMURO INH. 20 MCG/1DO FC 200 DOSIS
                
                # 5. DESLORATADINA - antihistamínico específico (no loratadina genérica)
                elif "desloratadina" in medicamento_lower:
                    print(f"🎯 DETECTADO DESLORATADINA → 3902005")
                    return "3902005"  # DESLORATADINA 5 MG
                
                # 6. CORTICOIDES INHALATORIOS - detección ampliada
                elif any(keyword in medicamento_lower for keyword in [
                    "budesonida", "budes", "fluticasona", "fluti", "beclometasona", "mometasona",
                    "corticoide", "formoterol", "salmeterol", "vilanterol"
                ]):
                    print(f"🎯 DETECTADO CORTICOIDE → 3902002")
                    return "3902002"  # CORTICOIDE INHALATORIO/BETA2 DE ACCIÓN PROLONGADA
                
                # Por defecto: SALBUTAMOL
                else:
                    print(f"🎯 NO DETECTADO → 3902001 (default)")
                    return "3902001"  # SALBUTAMOL por defecto
            
            # Intentar usar trazadora processor para otras condiciones
            elif hasattr(self.trazadora_processor, "determinar_trazadora_medicamento"):
                trazadora = self.trazadora_processor.determinar_trazadora_medicamento(
                    medicamento_desc, condition
                )
                return trazadora
            
            # Fallback a códigos por defecto
            else:
                return "2301001"  # Por defecto
                
        except Exception as e:
            print(f"⚠️ Error al determinar trazadora de medicamento para {condition}: {e}")
            # Fallback con códigos actualizados
            if condition == "EPOC":
                return "3801002"
            elif condition == "Paliativos":
                return "3002123"  # Por defecto no progresivo
            elif condition == "Fibrosis":
                return "2505263"  # Por defecto leve
            elif condition == "ASMA":
                return "3902001"  # SALBUTAMOL por defecto
            else:
                return "2301001"

    def determinar_tipo_prestacion(self, consulta):
        """Determinar tipo de prestación"""
        # Lógica simplificada
        return "CN"  # Consulta Nueva por defecto

    def agrupar_medicamentos_por_rut(self, medicamentos_rut):
        """
        Agrupar medicamentos eliminando duplicados por RUT + PRESTACIÓN.
        Para cada RUT + PRESTACIÓN, mantener solo el registro más reciente.
        Permite diferentes prestaciones para el mismo RUT, pero una sola prestación por RUT.
        """
        if not medicamentos_rut:
            return []

        # Si solo hay un medicamento, retornarlo
        if len(medicamentos_rut) == 1:
            return medicamentos_rut

        # Ordenar primero por fecha para mantener la más reciente
        medicamentos_rut_sorted = sorted(medicamentos_rut, 
                                       key=lambda x: pd.to_datetime(x.get("FECHA"), format="%d-%m-%Y", errors='coerce'), 
                                       reverse=True)

        # Deduplicar por RUT + PRESTACIÓN: mantener SOLO el más reciente
        medicamentos_unicos = {}

        for medicamento in medicamentos_rut_sorted:
            rut = medicamento.get("RUT", "")
            prestacion = medicamento.get("PRESTACION", "")
            
            # Crear clave única por RUT + PRESTACIÓN (SIN fecha)
            clave_unica = f"{rut}_{prestacion}"
            
            # Si no existe esta combinación RUT+PRESTACIÓN, guardar el registro (será el más reciente)
            # Si ya existe, ignorarlo (ya tenemos el más reciente por el ordenamiento)
            if clave_unica not in medicamentos_unicos:
                medicamentos_unicos[clave_unica] = medicamento

        medicamentos_finales = list(medicamentos_unicos.values())

        if len(medicamentos_rut) != len(medicamentos_finales):
            rut_sample = medicamentos_rut[0].get("RUT", "")
            eliminados = len(medicamentos_rut) - len(medicamentos_finales)
            print(f"    🔄 RUT {rut_sample}: {len(medicamentos_rut)} → {len(medicamentos_finales)} medicamentos (eliminados {eliminados} duplicados por RUT+PRESTACIÓN)")

        return medicamentos_finales

    def normalizar_codigo_familia(self, cod_fam):
        """
        Normalizar códigos de familia manteniendo las terminaciones importantes:
        - NO normalizar códigos con terminaciones -2, -3, etc. que son específicas
        - Solo normalizar códigos claramente erróneos o duplicados
        """
        if not cod_fam:
            return cod_fam
            
        # Mantener códigos con terminaciones específicas importantes
        # NO normalizar códigos que ya tienen formato correcto como 07-102-2, 07-116-3, etc.
        if cod_fam in ["07-102-2", "07-116-3", "07-102-0", "07-102-0", "07-117-0", "07-117-3"]:
            return cod_fam
        
        # Solo normalizar casos específicos problemáticos si es necesario
        # Por ahora, mantener el código original
        return cod_fam

    def get_cod_fam_consulta_actualizado(self, row, condition):
        """
        Obtiene el código de familia para consultas según nuevos requerimientos:
        - Paliativos: 07-116-3 (cambiado de 07-102-3)
        - EPOC/ASMA: usar código específico de broncopulmonar
        - Fibrosis: usar código específico según especialidad
        - Resto: usar EspecialidadLocal tal como está (sin normalizar)
        """
        if condition == "Paliativos":
            return "07-116-3"
        else:
            # Para todas las demás patologías, usar EspecialidadLocal sin modificar
            # para preservar las terminaciones específicas como -0, -2, etc.
            cod_fam_original = str(row.get("EspecialidadLocal", "")).strip()
            
            # NO normalizar - mantener el código tal como está
            return cod_fam_original if cod_fam_original else "07-102-0"

    def get_cod_fam_medicamento_actualizado(self, row, condition):
        """
        Obtiene el código de familia para medicamentos según nuevos requerimientos:
        - Paliativos: 07-116-3 (cambiado de 07-102-3)
        - Resto: 07-102-0 (cambiado de 07-102-2)
        """
        if condition == "Paliativos":
            return "07-116-3"
        else:
            return "07-102-0"

    def agrupar_consultas_por_rut(self, consultas_rut):
        """
        Agrupar consultas eliminando duplicados por RUT + PRESTACIÓN + FECHA.
        Si hay misma prestación pero diferentes especialidades, usar solo una.
        """
        if not consultas_rut:
            return []

        # Si solo hay una consulta, retornarla
        if len(consultas_rut) == 1:
            return consultas_rut

        # Agrupar por RUT + PRESTACION + FECHA para eliminar duplicados exactos
        consultas_unicas = {}

        # Ordenar primero por fecha para mantener la más reciente
        consultas_rut_sorted = sorted(consultas_rut, 
                                    key=lambda x: pd.to_datetime(x.get("FECHA"), format="%d-%m-%Y", errors='coerce'), 
                                    reverse=True)

        for consulta in consultas_rut_sorted:
            # Crear clave única por RUT + PRESTACIÓN + FECHA
            rut = consulta.get("RUT", "")  # Cambiado de NUMDOCUMENTO a RUT
            prestacion = consulta.get("PRESTACION", "")
            fecha = consulta.get("FECHA", "")
            clave_unica = f"{rut}_{prestacion}_{fecha}"
            
            # Si no existe, guardarlo
            if clave_unica not in consultas_unicas:
                consultas_unicas[clave_unica] = consulta
            # Si ya existe con la misma fecha, ignorar (duplicado real)

        consultas_finales = list(consultas_unicas.values())
        
        if len(consultas_rut) != len(consultas_finales):
            rut = consultas_rut[0].get("RUT", "")  # Cambiado de NUMDOCUMENTO a RUT
            print(f"    🔄 RUT {rut}: {len(consultas_rut)} → {len(consultas_finales)} consultas (eliminados duplicados por prestación y fecha)")
            # Imprimir detalles de las consultas eliminadas para debug
            fechas_originales = set(c.get("FECHA", "") for c in consultas_rut)
            fechas_finales = set(c.get("FECHA", "") for c in consultas_finales)
            fechas_eliminadas = fechas_originales - fechas_finales
            if fechas_eliminadas:
                print(f"       📅 Fechas eliminadas: {sorted(list(fechas_eliminadas))}")

        return consultas_finales

    def format_date(self, date_str):
        """Formatear fecha para el archivo de carga"""
        try:
            if pd.isna(date_str):
                return datetime.now().strftime("%d-%m-%Y")

            # Intentar diferentes formatos
            for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"]:
                try:
                    return pd.to_datetime(str(date_str), format=fmt).strftime("%d-%m-%Y")
                except:
                    continue

            return pd.to_datetime(str(date_str)).strftime("%d-%m-%Y")
        except:
            return datetime.now().strftime("%d-%m-%Y")

    def format_date_for_excel(self, date_str):
        """Formatear fecha como datetime object para Excel (como en archivo de referencia)"""
        try:
            if pd.isna(date_str):
                return datetime.now()

            # Intentar diferentes formatos y retornar datetime object
            for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"]:
                try:
                    return pd.to_datetime(str(date_str), format=fmt)
                except:
                    continue

            return pd.to_datetime(str(date_str))
        except:
            return datetime.now()

    def save_df_in_chunks(self, df, target_path, chunk_size=499):
        """
        Guardar un DataFrame dividiéndolo en archivos de tamaño máximo `chunk_size` filas.

        - Si el DataFrame cabe en una sola parte se guarda en `target_path`.
        - Si requiere particionado, la primera parte se guarda en `target_path` y
          las siguientes en `base_part2.ext`, `base_part3.ext`, ...
        - Soporta .xlsx, .xls y .csv (elige motor adecuado automáticamente).
        """
        try:
            if df is None or df.empty:
                print(f"INFO - DataFrame vacío, no se genera archivo: {target_path}")
                return

            # Asegurar carpeta de salida
            out_dir = os.path.dirname(target_path) or self.outputs_path
            if out_dir and not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)

            base, ext = os.path.splitext(target_path)
            ext = ext.lower()

            # Elegir motor por extensión
            if ext == ".xlsx":
                engine = 'openpyxl'
            elif ext == ".xls":
                engine = 'xlwt'
            elif ext == ".csv":
                engine = None
            else:
                # Default a xlsx
                engine = 'openpyxl'
                ext = '.xlsx'
                target_path = base + ext

            total = len(df)
            if total <= chunk_size:
                # Guardar todo en un solo archivo
                if ext == '.csv':
                    df.to_csv(target_path, index=False)
                else:
                    df.to_excel(target_path, index=False, engine=engine)
                print(f"✅ Archivo guardado: {target_path} ({total} filas)")
                return

            # Particionar y guardar. Primera parte en target_path para compatibilidad.
            part_index = 1
            for start in range(0, total, chunk_size):
                part_df = df.iloc[start:start+chunk_size]
                if part_index == 1:
                    part_path = target_path
                else:
                    part_path = f"{base}_part{part_index}{ext}"

                if ext == '.csv':
                    part_df.to_csv(part_path, index=False)
                else:
                    part_df.to_excel(part_path, index=False, engine=engine)

                print(f"✅ Parte {part_index} guardada: {part_path} ({len(part_df)} filas)")
                part_index += 1

        except Exception as e:
            print(f"❌ Error guardando archivos en chunks para {target_path}: {e}")

    def extract_rut_number(self, rut_complete):
        """Extraer número del RUT como entero"""
        try:
            rut_num = str(rut_complete).split("-")[0]
            return int(rut_num)
        except:
            try:
                return int(rut_complete)
            except:
                return rut_complete

    def extract_rut_dv(self, rut_complete):
        """Extraer dígito verificador del RUT"""
        try:
            return str(rut_complete).split("-")[1]
        except:
            return "0"

    def generar_archivos_carga(self):
        """Generar archivos finales para carga en el sistema"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generar archivo de consultas en formato Excel
        if self.consultas_procesadas:
            consultas_df = pd.DataFrame(self.consultas_procesadas)
            consultas_file = os.path.join(self.outputs_path, f"CARGA_CONSULTAS_GES_{timestamp}.xls")
            # Guardar consultas en chunks (500 filas por archivo)
            self.save_df_in_chunks(consultas_df, consultas_file, chunk_size=499)
            print(f"✅ Archivo(s) de consultas generado: {consultas_file}")

        # Generar archivo de medicamentos en formato Excel
        if self.medicamentos_procesados:
            medicamentos_df = pd.DataFrame(self.medicamentos_procesados)
            medicamentos_file = os.path.join(
                self.outputs_path, f"CARGA_MEDICAMENTOS_GES_{timestamp}.xls"
            )
            # Guardar medicamentos en chunks (500 filas por archivo)
            self.save_df_in_chunks(medicamentos_df, medicamentos_file, chunk_size=499)
            print(f"✅ Archivo(s) de medicamentos generado: {medicamentos_file}")
            print(f"✅ Archivo(s) de medicamentos generado: {medicamentos_file}")

    def generar_reporte_medicamentos_ges(self):
        """Generar reporte de análisis de medicamentos GES"""
        if not self.medicamentos_encontrados:
            print("❌ No hay análisis de medicamentos para reportar")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reporte_file = os.path.join(self.outputs_path, f"ANALISIS_MEDICAMENTOS_GES_{timestamp}.txt")

        with open(reporte_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("ANÁLISIS DE MEDICAMENTOS GES\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"📊 RESUMEN:\n")
            f.write(
                f"Total medicamentos en listado GES: {self.medicamentos_encontrados['total_ges']}\n"
            )
            f.write(
                f"Total medicamentos administrados: {self.medicamentos_encontrados['total_administrados']}\n"
            )
            f.write(
                f"Medicamentos GES encontrados: {len(self.medicamentos_encontrados['coincidencias'])}\n"
            )
            f.write(
                f"Medicamentos NO en listado GES: {len(self.medicamentos_encontrados['no_coincidencias'])}\n\n"
            )

            f.write("✅ MEDICAMENTOS GES ENCONTRADOS:\n")
            f.write("-" * 40 + "\n")
            for med in self.medicamentos_encontrados["coincidencias"]:
                f.write(f"• {med['medicamento_administrado']}\n")
                f.write(f"  Coincide con: {med['medicamento_ges']}\n")
                f.write(f"  Pacientes tratados: {med['pacientes']}\n\n")

            f.write("❓ MEDICAMENTOS NO EN LISTADO GES:\n")
            f.write("-" * 40 + "\n")
            for med in self.medicamentos_encontrados["no_coincidencias"]:
                f.write(f"• {med['medicamento_administrado']}\n")
                f.write(f"  Pacientes tratados: {med['pacientes']}\n\n")

        print(f"✅ Reporte de medicamentos generado: {reporte_file}")

    def generar_reportes_detallados(self):
        """Generar reportes detallados adicionales"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. Reporte de pacientes por patología
        self.generar_reporte_pacientes_patologia(timestamp)

        # 2. Reporte de medicamentos por patología
        self.generar_reporte_medicamentos_patologia(timestamp)

        # 3. Reporte de consultas por especialidad
        self.generar_reporte_consultas_especialidad(timestamp)

        # 4. Reporte estadístico general
        self.generar_reporte_estadistico_general(timestamp)

    def generar_reporte_pacientes_patologia(self, timestamp):
        """Generar reporte de pacientes por patología"""
        if self.ges_df is None:
            return

        reporte_file = os.path.join(
            self.outputs_path, f"REPORTE_PACIENTES_PATOLOGIA_{timestamp}.txt"
        )

        with open(reporte_file, "w", encoding="utf-8") as f:
            f.write("REPORTE DE PACIENTES POR PATOLOGÍA GES\n")
            f.write("=" * 50 + "\n\n")

            # Estadísticas por patología
            patologia_col = "Ges" if "Ges" in self.ges_df.columns else "Patologia"
            patologias = self.ges_df[patologia_col].value_counts()

            f.write("DISTRIBUCIÓN DE PACIENTES:\n")
            f.write("-" * 30 + "\n")
            for patologia, cantidad in patologias.items():
                f.write(f"{patologia}: {cantidad} pacientes\n")

            f.write(f"\nTOTAL PACIENTES GES: {len(self.ges_df)}\n")

        print(f"✅ Reporte de pacientes generado: {reporte_file}")

    def generar_reporte_medicamentos_patologia(self, timestamp):
        """Generar reporte de medicamentos por patología"""
        if self.farmacia_df is None or self.ges_df is None:
            return

        reporte_file = os.path.join(
            self.outputs_path, f"REPORTE_MEDICAMENTOS_PATOLOGIA_{timestamp}.txt"
        )

        with open(reporte_file, "w", encoding="utf-8") as f:
            f.write("REPORTE DE MEDICAMENTOS POR PATOLOGÍA GES\n")
            f.write("=" * 50 + "\n\n")

            ges_patients = set(self.ges_df["RUT"].astype(str))
            farmacia_ges = self.farmacia_df[self.farmacia_df["RUT_Combined"].isin(ges_patients)]

            patologia_col = "Ges" if "Ges" in self.ges_df.columns else "Patologia"
            for patologia in self.ges_df[patologia_col].unique():
                if pd.isna(patologia):
                    continue

                f.write(f"\n{patologia.upper()}\n")
                f.write("-" * len(patologia) + "\n")

                # Pacientes con esta patología
                pacientes_patologia = set(
                    self.ges_df[self.ges_df[patologia_col] == patologia]["RUT"].astype(str)
                )
                medicamentos_patologia = farmacia_ges[
                    farmacia_ges["RUT_Combined"].isin(pacientes_patologia)
                ]

                if len(medicamentos_patologia) > 0:
                    meds_count = medicamentos_patologia["Farmaco_Desc"].value_counts().head(10)
                    f.write("Top 10 medicamentos más administrados:\n")
                    for med, count in meds_count.items():
                        f.write(f"• {med}: {count} dispensaciones\n")
                else:
                    f.write("No se encontraron medicamentos dispensados.\n")

        print(f"✅ Reporte de medicamentos por patología generado: {reporte_file}")

    def generar_reporte_consultas_especialidad(self, timestamp):
        """Generar reporte de consultas por especialidad"""
        if self.consulta_df is None or self.ges_df is None:
            return

        reporte_file = os.path.join(
            self.outputs_path, f"REPORTE_CONSULTAS_ESPECIALIDAD_{timestamp}.txt"
        )

        with open(reporte_file, "w", encoding="utf-8") as f:
            f.write("REPORTE DE CONSULTAS POR ESPECIALIDAD\n")
            f.write("=" * 40 + "\n\n")

            ges_patients = set(self.ges_df["RUT"].astype(str))
            consultas_ges = self.consulta_df[
                self.consulta_df["RUNPaciente"].astype(str).isin(ges_patients)
            ]

            # Consultas por especialidad
            if "EspecialidadLocal" in consultas_ges.columns:
                especialidades = consultas_ges["EspecialidadLocal"].value_counts()

                f.write("CONSULTAS POR ESPECIALIDAD:\n")
                f.write("-" * 30 + "\n")
                for esp, count in especialidades.head(15).items():
                    f.write(f"{esp}: {count} consultas\n")

            # Estados de citas
            if "EstadoCita_Desc" in consultas_ges.columns:
                f.write("\nESTADOS DE CITAS:\n")
                f.write("-" * 20 + "\n")
                estados = consultas_ges["EstadoCita_Desc"].value_counts()
                for estado, count in estados.items():
                    f.write(f"{estado}: {count} citas\n")

        print(f"✅ Reporte de consultas por especialidad generado: {reporte_file}")

    def generar_reporte_estadistico_general(self, timestamp):
        """Generar reporte estadístico general"""
        reporte_file = os.path.join(
            self.outputs_path, f"REPORTE_ESTADISTICO_GENERAL_{timestamp}.txt"
        )

        with open(reporte_file, "w", encoding="utf-8") as f:
            f.write("REPORTE ESTADÍSTICO GENERAL GES\n")
            f.write("=" * 35 + "\n\n")

            # Estadísticas generales
            f.write("RESUMEN GENERAL:\n")
            f.write("-" * 20 + "\n")

            if self.ges_df is not None:
                f.write(f"Total pacientes GES: {len(self.ges_df)}\n")
                ges_patients = set(self.ges_df["RUT"].astype(str))

                if self.consulta_df is not None:
                    consultas_ges = self.consulta_df[
                        self.consulta_df["RUNPaciente"].astype(str).isin(ges_patients)
                    ]
                    f.write(f"Total consultas GES: {len(consultas_ges)}\n")

                if self.farmacia_df is not None:
                    farmacia_ges = self.farmacia_df[
                        self.farmacia_df["RUT_Combined"].isin(ges_patients)
                    ]
                    f.write(f"Total dispensaciones GES: {len(farmacia_ges)}\n")

            # Códigos PS utilizados
            f.write("\nCÓDIGOS PS CONFIGURADOS:\n")
            f.write("-" * 25 + "\n")
            for condition, code in CODIGOS_PRESTACION_GES.items():
                f.write(f"{condition}: PS {code}\n")

        print(f"✅ Reporte estadístico general generado: {reporte_file}")

    def procesar_todo(self):
        """Procesar todo el flujo completo"""
        print("🚀 INICIANDO PROCESAMIENTO COMPLETO GES")
        print("=" * 50)

        # 1. Cargar datos
        if not self.load_data():
            return False

        # 1.5. Cargar arancel GES para trazadoras
        print("\n📋 CARGANDO ARANCEL GES...")
        if self.trazadora_processor.cargar_arancel_ges():
            self.trazadora_processor.extraer_trazadoras_medicamentos()
            self.trazadora_processor.extraer_trazadoras_consultas()
            # self.trazadora_processor.extraer_especialidades_del_arancel()  # Método no existe

        # 2. Analizar medicamentos GES
        self.analizar_medicamentos_ges()

        # 3. Procesar consultas
        if hasattr(self, "consulta_df") and self.consulta_df is not None:
            archivo_consultas = os.path.join(
                self.outputs_path,
                f"CARGA_CONSULTAS_GES_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xls",
            )
            self.procesar_consultas_para_carga(self.consulta_df, archivo_consultas)

        # 4. Procesar medicamentos
        if hasattr(self, "farmacia_df") and self.farmacia_df is not None:
            archivo_medicamentos = os.path.join(
                self.outputs_path,
                f"CARGA_MEDICAMENTOS_GES_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xls",
            )
            self.procesar_medicamentos_para_carga(self.farmacia_df, archivo_medicamentos)

        # 5. Generar archivo de cruce con especialidades
        if self.ges_df is not None:
            self.trazadora_processor.generar_archivo_cruce(
                self.ges_df, self.consulta_df, self.farmacia_df
            )

        # 6. Generar archivos adicionales
        self.generar_reporte_medicamentos_ges()
        self.generar_reportes_detallados()

        print("\n🎉 PROCESAMIENTO COMPLETADO")
        print("Revisa la carpeta 'outputs' para ver los resultados")

        return True


if __name__ == "__main__":
    processor = GESDataProcessor()
    processor.procesar_todo()
