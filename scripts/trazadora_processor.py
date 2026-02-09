import os
from datetime import datetime

import pandas as pd


class TrazadoraProcessor:
    def __init__(self, base_path=None):
        if base_path is None:
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.base_path = base_path

        self.outputs_path = os.path.join(self.base_path, "outputs")
        self.arancel_df = None
        self.trazadoras_medicamentos = {}
        self.exclusiones = {}

    def cargar_arancel_ges(self):
        """Cargar el archivo de arancel GES"""
        try:
            arancel_file = os.path.join(
                self.base_path, "(WEB) Arancel GES 2025 01012025 v.1.0 (6).xlsx"
            )
            df = pd.read_excel(arancel_file)

            # Los encabezados están en la fila 2
            headers = df.iloc[2].tolist()
            self.arancel_df = df.iloc[3:].copy()
            self.arancel_df.columns = headers

            print("OK - Arancel GES cargado correctamente")
            return True

        except Exception as e:
            print(f"ERROR - Error al cargar arancel: {e}")
            return False

    def normalizar_codigo_trazadora(self, codigo):
        """
        Normalizar códigos de trazadora para asegurar formato consistente:
        - Agregar 0 inicial si falta (101113 -> 0101113)
        - Mantener longitud estándar de 7 dígitos
        """
        if not codigo:
            return codigo
            
        codigo_str = str(codigo).strip()
        
        # Si el código tiene 6 dígitos, agregar 0 inicial
        if len(codigo_str) == 6 and codigo_str.isdigit():
            codigo_str = "0" + codigo_str
            
        return codigo_str

    def extraer_trazadoras_medicamentos(self):
        """Extraer trazadoras específicas para medicamentos"""
        if self.arancel_df is None:
            return

        # Filtrar solo las trazadoras de medicamentos para las patologías GES
        patologias_ges = {
            "ENFERMEDAD PULMONAR OBSTRUCTIVA CRÓNICA": "EPOC",
            "ASMA BRONQUIAL": "ASMA",  # Actualizado para coincidir con archivo población
            "FIBROSIS QUÍSTICA": "Fibrosis",  # Actualizado para coincidir con archivo población
            "ALIVIO DEL DOLOR": "Paliativos",
        }

        for patologia_completa, patologia_corta in patologias_ges.items():
            # Buscar registros de esta patología
            mask = self.arancel_df["Problema de Salud"].str.contains(
                patologia_completa, case=False, na=False
            )
            registros_patologia = self.arancel_df[mask]

            if len(registros_patologia) > 0:
                # Extraer trazadoras de medicamentos (intervención "TRATAMIENTO")
                medicamentos_mask = registros_patologia["Intervención Sanitaria"].str.upper() == "TRATAMIENTO"
                registros_medicamentos = registros_patologia[medicamentos_mask]
                
                # Si no hay tratamientos específicos, usar todos los registros
                if len(registros_medicamentos) == 0:
                    registros_medicamentos = registros_patologia
                
                trazadoras = registros_medicamentos["Trazadora"].dropna().unique()
                exclusiones = registros_medicamentos["Excluyentes"].dropna().unique()

                self.trazadoras_medicamentos[patologia_corta] = {
                    "trazadoras": list(trazadoras),
                    "exclusiones": list(exclusiones),
                }

                print(
                    f"OK - {patologia_corta} (Medicamentos): {len(trazadoras)} trazadoras, {len(exclusiones)} exclusiones"
                )

    def extraer_trazadoras_consultas(self):
        """Extraer trazadoras específicas para consultas"""
        if self.arancel_df is None:
            return

        # Filtrar solo las trazadoras de consultas para las patologías GES
        patologias_ges = {
            "ENFERMEDAD PULMONAR OBSTRUCTIVA CRÓNICA": "EPOC",
            "ASMA BRONQUIAL": "ASMA",
            "FIBROSIS QUÍSTICA": "Fibrosis",
            "ALIVIO DEL DOLOR": "Paliativos",
        }

        self.trazadoras_consultas = {}

        for patologia_completa, patologia_corta in patologias_ges.items():
            # Buscar registros de esta patología
            mask = self.arancel_df["Problema de Salud"].str.contains(
                patologia_completa, case=False, na=False
            )
            registros_patologia = self.arancel_df[mask]

            if len(registros_patologia) > 0:
                # Extraer trazadoras de consultas (intervención "DIAGNÓSTICO" típicamente corresponde a consultas)
                consultas_mask = registros_patologia["Intervención Sanitaria"].str.upper() == "DIAGNÓSTICO"
                registros_consultas = registros_patologia[consultas_mask]
                
                # Si no hay diagnósticos, usar todas las trazadoras disponibles
                if len(registros_consultas) == 0:
                    registros_consultas = registros_patologia

                trazadoras = registros_consultas["Trazadora"].dropna().unique()
                exclusiones = registros_consultas["Excluyentes"].dropna().unique()

                self.trazadoras_consultas[patologia_corta] = {
                    "trazadoras": list(trazadoras),
                    "exclusiones": list(exclusiones),
                }

                print(
                    f"OK - {patologia_corta} (Consultas): {len(trazadoras)} trazadoras, {len(exclusiones)} exclusiones"
                )

    def determinar_trazadora_medicamento(self, medicamento_desc, patologia, rut_paciente=None):
        """Determinar la trazadora apropiada para un medicamento según patología y tipo de medicamento"""
        
        # Convertir a string y limpiar con manejo robusto
        if pd.isna(medicamento_desc):
            medicamento_desc = ""
        else:
            medicamento_desc = str(medicamento_desc).upper().strip()
        
        # Manejo robusto de patología  
        if pd.isna(patologia):
            patologia = ""
        else:
            patologia = str(patologia).strip()
        
        if patologia == "ASMA":
            return self._determinar_trazadora_asma_medicamento(medicamento_desc)
        elif patologia == "Fibrosis":
            return self._determinar_trazadora_fibrosis_medicamento(medicamento_desc, rut_paciente)
        elif patologia == "EPOC":
            return "3801002"  # Una sola trazadora para EPOC medicamentos
        elif patologia == "Paliativos":
            return self._determinar_trazadora_paliativos_medicamento(rut_paciente)
        else:
            return "2301001"  # Código por defecto
    
    def _determinar_trazadora_asma_medicamento(self, medicamento_desc):
        """Determinar trazadora específica para medicamentos de ASMA según tipo"""
        medicamento_desc = medicamento_desc.upper()
        
        # Monoclonales específicos para ASMA (Mepolizumab / Omalizumab)
        if any(med in medicamento_desc for med in ["MEPOLIZUMAB", "OMALIZUMAB"]):
            return self.normalizar_codigo_trazadora("2508156")  # MAB ASMA (MEPOLIZUMAB/OMALIZUMAB)

            return self.normalizar_codigo_trazadora("3902006")  # Ipratropio bromuro
        elif any(med in medicamento_desc for med in ["PREDNIZONA", "PREDNISONA", "DELTISONA"]):
            return self.normalizar_codigo_trazadora("3902004")  # Prednizona
        elif any(med in medicamento_desc for med in ["DESLORATADINA", "AERIUS", "AZOMYR"]):
            return self.normalizar_codigo_trazadora("3902005")  # Desloratadina
        elif any(med in medicamento_desc for med in ["BUDESONIDA", "BECLOMETASONA", "FLUTICASONA", "INHALATORIO", "INHALED"]):
            return self.normalizar_codigo_trazadora("3902002")  # Corticoide inhalatorio
        else:
            return self.normalizar_codigo_trazadora("3902001")  # Por defecto salbutamol
    
    def _determinar_trazadora_fibrosis_medicamento(self, medicamento_desc, rut_paciente):
        """Determinar trazadora específica para medicamentos de Fibrosis según severidad y tipo"""
        medicamento_desc = medicamento_desc.upper()

        # Trazadora específica para TRIKAFTA (independiente de severidad)
        if any(med in medicamento_desc for med in ["TRIKAFTA", "ELEXACAFTOR", "TEZACAFTOR", "IVACAFTOR"]):
            return self.normalizar_codigo_trazadora("2508141")  # TRIKAFTA para Fibrosis Quística
        
        # Determinar severidad del paciente
        severidad = "leve"  # Por defecto
        if rut_paciente:
            severidad = self._obtener_severidad_fq(rut_paciente)
        
        # Trazadoras específicas según medicamento y severidad
        if any(med in medicamento_desc for med in ["TOBRAMICINA", "TOBI"]):
            return self.normalizar_codigo_trazadora("3004004")  # TRATAMIENTO FARMACOLOGICO CON TOBRAMICINA PARA PACIENTES CON FIBROSIS QUISTICA GRAVE
        else:
            # Trazadoras según severidad para otros medicamentos
            if severidad == "grave":
                return self.normalizar_codigo_trazadora("2505256")  # TRATAMIENTO FIBROSIS QUÍSTICA GRAVE
            elif severidad == "moderada":
                return self.normalizar_codigo_trazadora("2505260")  # TRATAMIENTO FIBROSIS QUÍSTICA MODERADA  
            else:  # leve
                return self.normalizar_codigo_trazadora("2505263")  # TRATAMIENTO FIBROSIS QUÍSTICA LEVE
    
    def _determinar_trazadora_paliativos_medicamento(self, rut_paciente):
        """Determinar trazadora para medicamentos de Paliativos según progresión"""
        if not rut_paciente:
            return self.normalizar_codigo_trazadora("3002123")  # No progresivo por defecto
            
        # Cargar datos de clasificación si no están cargados
        if not hasattr(self, 'clasificacion_paliativos_df'):
            try:
                clasificacion_file = os.path.join(self.base_path, "inputs", "clasificacion_paliativos.csv")
                self.clasificacion_paliativos_df = pd.read_csv(clasificacion_file, sep=';')
                # Limpiar nombres de columnas (quitar espacios extra)
                self.clasificacion_paliativos_df.columns = self.clasificacion_paliativos_df.columns.str.strip()
                print(f"Cargando clasificación paliativos con columnas: {list(self.clasificacion_paliativos_df.columns)}")
            except Exception as e:
                print(f"Error cargando clasificación paliativos: {e}")
                return self.normalizar_codigo_trazadora("3002123")  # No progresivo por defecto
        
        # Normalizar RUT (quitar guiones y dígito verificador)
        rut_normalizado = str(rut_paciente).split('-')[0].replace('-', '')
        
        # Buscar condición del paciente usando la nueva estructura
        # El archivo tiene columnas: RUT y condicion
        rut_series = self.clasificacion_paliativos_df['RUT'].astype(str).str.split('-').str[0]
        mask = rut_series == rut_normalizado
        if mask.any():
            condicion = str(self.clasificacion_paliativos_df[mask]['condicion'].iloc[0]).strip()
            
            # Mapear condición a trazadora
            # NP y CP-NO = No progresivo
            # Todo lo demás = Progresivo
            if condicion in ['NP', 'CP-NO']:
                return self.normalizar_codigo_trazadora("3002123")  # No progresivo - tratamiento integral
            else:
                return self.normalizar_codigo_trazadora("3002023")  # Progresivo - cáncer terminal
        
        print(f"⚠️ RUT {rut_paciente}: No se encontró clasificación paliativos, usando NO PROGRESIVO por defecto")
        return self.normalizar_codigo_trazadora("3002123")  # No progresivo por defecto
    
    def _obtener_severidad_fq(self, rut_paciente):
        """Obtener severidad de Fibrosis Quística para un paciente"""
        if not hasattr(self, 'severidad_fq_df'):
            try:
                severidad_file = os.path.join(self.base_path, "inputs", "severidad_FQ.xlsx")
                self.severidad_fq_df = pd.read_excel(severidad_file)
                # Limpiar nombres de columnas (quitar espacios)
                self.severidad_fq_df.columns = self.severidad_fq_df.columns.str.strip()
            except Exception as e:
                print(f"Error cargando severidad FQ: {e}")
                return "leve"
        
        # Normalizar RUT (quitar guiones y dígito verificador)
        rut_normalizado = str(rut_paciente).split('-')[0].replace('-', '')
        
        # Buscar severidad del paciente en la columna RUT (con posibles espacios)
        for col in ['RUT', 'Rut', 'rut', 'Rut ']:
            if col in self.severidad_fq_df.columns:
                # Extraer solo el número del RUT de la columna (sin DV)
                rut_series = self.severidad_fq_df[col].astype(str).str.split('-').str[0]
                mask = rut_series == rut_normalizado
                if mask.any():
                    severidad = str(self.severidad_fq_df[mask]['Severidad'].iloc[0]).lower().strip()
                    
                    # Mapear severidad actualizada a nombres estándar
                    if severidad in ['severo', 'grave']:
                        return "grave"
                    elif severidad in ['moderado', 'moderada']:
                        return "moderada" 
                    elif severidad in ['leve']:
                        return "leve"
                break
        
        return "leve"  # Por defecto

    def determinar_trazadora_consulta(self, especialidad, patologia, rut_paciente=None):
        """Determinar la trazadora apropiada para una consulta según requerimientos específicos"""
        
        # Manejo robusto de entrada
        if pd.isna(especialidad):
            especialidad = ""
        else:
            especialidad = str(especialidad).strip()
            
        if pd.isna(patologia):
            patologia = ""
        else:
            patologia = str(patologia).strip()
            
        # Códigos específicos según patología y severidad
        if patologia == "EPOC":
            codigo = "0101110"     # EPOC usa 0101110 (corregido)
        elif patologia == "ASMA":
            codigo = "0101113"     # ASMA usa 0101113 
        elif patologia == "Fibrosis":
            return self._determinar_trazadora_fibrosis_consulta(rut_paciente)
        elif patologia == "Paliativos":
            return self._determinar_trazadora_paliativos_consulta(rut_paciente)
        else:
            codigo = "0101322"     # Código por defecto
            
        return self.normalizar_codigo_trazadora(codigo)
    
    def _determinar_trazadora_fibrosis_consulta(self, rut_paciente):
        """Determinar trazadora para Fibrosis según severidad usando severidad_FQ.xlsx"""
        if not rut_paciente:
            return "3004501"  # Leve por defecto
            
        # Cargar datos de severidad si no están cargados
        if not hasattr(self, 'severidad_fq_df'):
            try:
                severidad_file = os.path.join(self.base_path, "inputs", "severidad_FQ.xlsx")
                self.severidad_fq_df = pd.read_excel(severidad_file)
                # Limpiar nombres de columnas (quitar espacios)
                self.severidad_fq_df.columns = self.severidad_fq_df.columns.str.strip()
            except Exception as e:
                print(f"Error cargando severidad FQ: {e}")
                return "3004501"  # Leve por defecto
        
        # Normalizar RUT (quitar guiones y dígito verificador)
        rut_normalizado = str(rut_paciente).split('-')[0].replace('-', '')
        
        # Buscar severidad del paciente en la columna RUT (con posibles espacios)
        for col in ['RUT', 'Rut', 'rut', 'Rut ']:
            if col in self.severidad_fq_df.columns:
                # Extraer solo el número del RUT de la columna (sin DV)
                rut_series = self.severidad_fq_df[col].astype(str).str.split('-').str[0]
                mask = rut_series == rut_normalizado
                if mask.any():
                    severidad = str(self.severidad_fq_df[mask]['Severidad'].iloc[0]).lower().strip()
                    
                    # Mapear severidad actualizada a trazadora
                    if severidad in ['severo', 'grave']:
                        return self.normalizar_codigo_trazadora("3004503")
                    elif severidad in ['moderado', 'moderada']:
                        return self.normalizar_codigo_trazadora("3004502") 
                    elif severidad in ['leve']:
                        return self.normalizar_codigo_trazadora("3004501")
                break
        
        print(f"⚠️ RUT {rut_paciente}: No se encontró severidad FQ, usando LEVE por defecto")
        return self.normalizar_codigo_trazadora("3004501")  # Leve por defecto
    
    def _determinar_trazadora_paliativos_consulta(self, rut_paciente):
        """Determinar trazadora para Paliativos según progresión usando clasificacion_paliativos.csv"""
        if not rut_paciente:
            return self.normalizar_codigo_trazadora("3002123")  # No progresivo por defecto
            
        # Cargar datos de clasificación si no están cargados
        if not hasattr(self, 'clasificacion_paliativos_df'):
            try:
                clasificacion_file = os.path.join(self.base_path, "inputs", "clasificacion_paliativos.csv")
                self.clasificacion_paliativos_df = pd.read_csv(clasificacion_file, sep=';')
                # Limpiar nombres de columnas (quitar espacios extra)
                self.clasificacion_paliativos_df.columns = self.clasificacion_paliativos_df.columns.str.strip()
                print(f"Cargando clasificación paliativos con columnas: {list(self.clasificacion_paliativos_df.columns)}")
            except Exception as e:
                print(f"Error cargando clasificación paliativos: {e}")
                return self.normalizar_codigo_trazadora("3002123")  # No progresivo por defecto
        
        # Normalizar RUT (quitar guiones y dígito verificador)
        rut_normalizado = str(rut_paciente).split('-')[0].replace('-', '')
        
        # Buscar condición del paciente usando la nueva estructura
        # El archivo tiene columnas: RUT y condicion
        rut_series = self.clasificacion_paliativos_df['RUT'].astype(str).str.split('-').str[0]
        mask = rut_series == rut_normalizado
        if mask.any():
            condicion = str(self.clasificacion_paliativos_df[mask]['condicion'].iloc[0]).strip()
            
            # Mapear condición a trazadora
            # NP y CP-NO = No progresivo
            # Todo lo demás = Progresivo
            if condicion in ['NP', 'CP-NO']:
                return self.normalizar_codigo_trazadora("3002123")  # No progresivo - tratamiento integral
            else:
                return self.normalizar_codigo_trazadora("3002023")  # Progresivo - cáncer terminal
        
        print(f"⚠️ RUT {rut_paciente}: No se encontró clasificación paliativos, usando NO PROGRESIVO por defecto")
        return self.normalizar_codigo_trazadora("3002123")  # No progresivo por defecto

    def generar_archivo_cruce(self, ges_df, consultas_df, farmacia_df):
        """Generar archivo de cruce mostrando RUT con indicadores de cita/medicación"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_cruce = os.path.join(self.outputs_path, f"ARCHIVO_CRUCE_GES_{timestamp}.csv")

        print("\n📊 GENERANDO ARCHIVO DE CRUCE...")

        # Crear DataFrame base con todos los pacientes GES
        cruce_data = []

        # Convertir RUTs a string y normalizar a mayúsculas para comparación (evita mismatches por dv minúscula)
        ges_patients = set(ges_df["RUT"].astype(str).str.upper())
        consultas_ruts = (
            set(consultas_df["RUNPaciente"].astype(str).str.upper()) if consultas_df is not None else set()
        )
        farmacia_ruts = set(farmacia_df["RUT_Combined"].astype(str).str.upper()) if farmacia_df is not None else set()

        for _, paciente in ges_df.iterrows():
            rut_completo = str(paciente["RUT"])
            rut_original = rut_completo  # Mantener el RUT original para comparación
            rut_original_upper = rut_original.upper()  # Normalizar para comparaciones posteriores
            # Determinar el nombre de la columna de patología
            patologia_col = "Ges" if "Ges" in ges_df.columns else "Patologia"
            patologia = paciente[patologia_col]

            # Separar RUT y DV para el reporte
            if "-" in rut_completo:
                rut_partes = rut_completo.split("-")
                rut_display = rut_partes[0]
                dv_display = rut_partes[1] if len(rut_partes) > 1 else ""
            else:
                rut_display = rut_completo
                dv_display = paciente.get("DV", "") if "DV" in paciente else ""

            # Verificar si tuvo consultas (usar RUT original)
            tuvo_consulta = rut_original in consultas_ruts
            consultas_count = 0
            especialidades_consulta = []

            if tuvo_consulta and consultas_df is not None:
                consultas_paciente = consultas_df[
                    consultas_df["RUNPaciente"].astype(str).str.upper() == rut_original_upper
                ]
                consultas_count = len(consultas_paciente)

                # Obtener especialidades únicas
                if "EspecialidadLocal" in consultas_paciente.columns:
                    especialidades_consulta = (
                        consultas_paciente["EspecialidadLocal"].dropna().unique().tolist()
                    )

            # Verificar si tuvo medicamentos (usar RUT original)
            tuvo_medicamento = rut_original in farmacia_ruts
            medicamentos_count = 0
            especialidades_farmacia = []

            if tuvo_medicamento and farmacia_df is not None:
                medicamentos_paciente = farmacia_df[farmacia_df["RUT_Combined"].astype(str).str.upper() == rut_original_upper]
                medicamentos_count = len(medicamentos_paciente)

                # Obtener locales solicitantes únicos (especialidades que prescribieron)
                if "LocalSolicitante" in medicamentos_paciente.columns:
                    especialidades_raw = (
                        medicamentos_paciente["LocalSolicitante"].dropna().unique().tolist()
                    )
                    # Limpiar especialidades (quitar INT- y -R/-P)
                    especialidades_farmacia = []
                    for esp in especialidades_raw:
                        esp_clean = str(esp).strip()
                        if esp_clean.startswith("INT-"):
                            esp_clean = esp_clean[4:]  # Eliminar "INT-"
                        if esp_clean.endswith("-R") or esp_clean.endswith("-P"):
                            esp_clean = esp_clean[:-2]  # Eliminar "-R" o "-P"
                        if esp_clean:
                            especialidades_farmacia.append(esp_clean)

            cruce_data.append(
                {
                    "RUT": rut_display,
                    "DV": dv_display,
                    "PATOLOGIA_GES": patologia,
                    "TUVO_CONSULTA": "SÍ" if tuvo_consulta else "NO",
                    "NUM_CONSULTAS": consultas_count,
                    "ESPECIALIDADES_CONSULTA": (
                        "; ".join(especialidades_consulta) if especialidades_consulta else ""
                    ),
                    "TUVO_MEDICAMENTO": "SÍ" if tuvo_medicamento else "NO",
                    "NUM_MEDICAMENTOS": medicamentos_count,
                    "ESPECIALIDADES_PRESCRIPCION": (
                        "; ".join(especialidades_farmacia) if especialidades_farmacia else ""
                    ),
                    "ATENCION_COMPLETA": "SÍ" if (tuvo_consulta and tuvo_medicamento) else "NO",
                    "SOLO_CONSULTA": "SÍ" if (tuvo_consulta and not tuvo_medicamento) else "NO",
                    "SOLO_MEDICAMENTO": "SÍ" if (not tuvo_consulta and tuvo_medicamento) else "NO",
                    "SIN_ATENCION": "SÍ" if (not tuvo_consulta and not tuvo_medicamento) else "NO",
                }
            )

        # Crear DataFrame y guardar
        df_cruce = pd.DataFrame(cruce_data)
        df_cruce.to_csv(archivo_cruce, sep="|", index=False, encoding="utf-8")

        print(f"OK - Archivo de cruce generado: {archivo_cruce}")
        print(f"INFO - Total pacientes: {len(df_cruce)}")
        print(f"INFO - Con consulta: {len(df_cruce[df_cruce['TUVO_CONSULTA'] == 'SÍ'])}")
        print(f"INFO - Con medicamento: {len(df_cruce[df_cruce['TUVO_MEDICAMENTO'] == 'SÍ'])}")
        print(f"INFO - Atención completa: {len(df_cruce[df_cruce['ATENCION_COMPLETA'] == 'SÍ'])}")

        return archivo_cruce
