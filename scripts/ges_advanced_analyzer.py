import os
import threading
import glob
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ges_data_processor import GESDataProcessor


class GESAdvancedAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GES Advanced Analysis System")
        self.root.geometry("900x700")

        self.processor = GESDataProcessor()
        self.manual_mode = tk.BooleanVar(value=False)
        self.manual_files = {
            "consultas": None,
            "farmacia": None,
            "recetas_ges": [],
        }

        self.setup_gui()

    def setup_gui(self):
        """Crear interfaz GUI avanzada"""
        # Título principal
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        tk.Label(
            title_frame, text="SISTEMA AVANZADO DE ANÁLISIS GES", font=("Arial", 16, "bold")
        ).pack()
        tk.Label(
            title_frame, text="Instituto Nacional de Enfermedades Respiratorias", font=("Arial", 10)
        ).pack()
        tk.Label(
            title_frame, text="⭐ V2.0 - Trazadoras Múltiples | Verificación Población GES | Sin Duplicados", 
            font=("Arial", 9), fg="blue"
        ).pack()

        # Notebook para pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Pestaña 1: Análisis General
        self.setup_general_tab(notebook)

        # Pestaña 2: Medicamentos GES
        self.setup_medicamentos_tab(notebook)

        # Pestaña 3: Archivos de Carga
        self.setup_carga_tab(notebook)

        # Pestaña 4: Configuración
        self.setup_config_tab(notebook)

        # Frame de resultados (abajo)
        self.setup_results_frame()

    def setup_general_tab(self, notebook):
        """Pestaña de análisis general"""
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="📊 Análisis General")

        # Selección de archivos
        files_frame = tk.LabelFrame(
            general_frame, text="Archivos de Datos", font=("Arial", 12, "bold")
        )
        files_frame.pack(fill="x", padx=10, pady=10)

        # Status de archivos
        self.file_status = {}

        files = [
            ("GES Population", "RUT_pob_ges.xlsx"),
            ("Consultas", "reporte_consulta_*.csv"),
            ("Farmacia", "reporte_farmacia_*.csv"),
            ("Recetas GES", "recetas*.xls"),
            ("Medicamentos GES", "Medicamentos GES (1).xlsx"),
            ("Clasificación Paliativos", "clasificacion_paliativos.csv"),
            ("Severidad FQ", "severidad_FQ.xlsx"),
        ]

        for i, (label, filename) in enumerate(files):
            frame = tk.Frame(files_frame)
            frame.pack(fill="x", padx=10, pady=2)

            tk.Label(frame, text=f"{label}:", width=15, anchor="w").pack(side="left")

            status_label = tk.Label(frame, text="❓ No verificado", fg="gray")
            status_label.pack(side="left", padx=10)

            self.file_status[filename] = status_label

        # Botones de acción
        action_frame = tk.Frame(general_frame)
        action_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(
            action_frame,
            text="🔍 Verificar Archivos",
            command=self.verificar_archivos,
            bg="blue",
            fg="white",
        ).pack(side="left", padx=5)

        tk.Button(
            action_frame,
            text="🚀 Análisis Completo",
            command=self.run_full_analysis,
            bg="green",
            fg="white",
            font=("Arial", 12, "bold"),
        ).pack(side="left", padx=5)

    def setup_medicamentos_tab(self, notebook):
        """Pestaña de análisis de medicamentos GES"""
        med_frame = ttk.Frame(notebook)
        notebook.add(med_frame, text="💊 Medicamentos GES")

        # Información
        info_frame = tk.LabelFrame(
            med_frame, text="Análisis de Medicamentos GES", font=("Arial", 12, "bold")
        )
        info_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            info_frame,
            text="Este análisis verifica qué medicamentos administrados\nestán en el listado oficial GES (excluyendo paliativos).",
            justify="left",
        ).pack(anchor="w", padx=10, pady=5)

        # Botones
        button_frame = tk.Frame(med_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(
            button_frame, text="📋 Cargar Medicamentos GES", command=self.load_medicamentos_ges
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame, text="🔍 Analizar Coincidencias", command=self.analyze_medicamentos
        ).pack(side="left", padx=5)

        # Resultados
        results_frame = tk.LabelFrame(med_frame, text="Resultados", font=("Arial", 12, "bold"))
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview para mostrar resultados
        self.med_tree = ttk.Treeview(
            results_frame, columns=("medicamento", "tipo", "pacientes"), show="headings"
        )
        self.med_tree.heading("medicamento", text="Medicamento")
        self.med_tree.heading("tipo", text="Tipo")
        self.med_tree.heading("pacientes", text="Pacientes")

        med_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.med_tree.yview)
        self.med_tree.configure(yscrollcommand=med_scrollbar.set)

        self.med_tree.pack(side="left", fill="both", expand=True)
        med_scrollbar.pack(side="right", fill="y")

    def setup_carga_tab(self, notebook):
        """Pestaña de generación de archivos de carga"""
        carga_frame = ttk.Frame(notebook)
        notebook.add(carga_frame, text="📤 Archivos de Carga")

        # Información sobre formato
        info_frame = tk.LabelFrame(
            carga_frame, text="Formato de Archivos de Carga V2.0", font=("Arial", 12, "bold")
        )
        info_frame.pack(fill="x", padx=10, pady=10)

        format_text = """
FORMATO CONSULTAS: FECHA | RUT | DV | PRESTACION | TIPO | PS | COD FAM
FORMATO FARMACIA:  FECHA | RUT | DV | PRESTACION | TIPO | PS | COD FAM

⭐ MEJORAS V2.0:
• ASMA: 6 trazadoras (3902001-3902006) según medicamento específico
• FIBROSIS: 4 trazadoras (2505256/60/63, 3004004) según severidad
• PALIATIVOS: Nueva lógica *-NO = no oncológicos
• SIN DUPLICADOS: Eliminación automática por RUT+PRESTACION
• VERIFICACIÓN GES: Solo pacientes de población válida
• CASOS REVISIÓN: Archivo separado para pacientes NO-GES
        """

        tk.Label(info_frame, text=format_text, justify="left", font=("Courier", 8)).pack(
            anchor="w", padx=10, pady=5
        )

        # Opciones de generación
        options_frame = tk.LabelFrame(
            carga_frame, text="Opciones de Generación V2.0", font=("Arial", 12, "bold")
        )
        options_frame.pack(fill="x", padx=10, pady=10)

        self.include_paliativos = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame, text="✅ Incluir pacientes paliativos (con nueva lógica)", variable=self.include_paliativos
        ).pack(anchor="w", padx=10, pady=2)

        self.separar_archivos = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="✅ Generar archivos separados (consultas y medicamentos)",
            variable=self.separar_archivos,
        ).pack(anchor="w", padx=10, pady=2)
        
        self.verificar_poblacion_ges = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="🔍 Verificar población GES (excluir NO-GES automáticamente)",
            variable=self.verificar_poblacion_ges,
        ).pack(anchor="w", padx=10, pady=2)
        
        self.generar_archivo_revision = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="📋 Generar archivo de casos para revisión (NO-GES)",
            variable=self.generar_archivo_revision,
        ).pack(anchor="w", padx=10, pady=2)

        # Botones de generación
        button_frame = tk.Frame(carga_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(
            button_frame,
            text="📋 Generar Archivo Consultas",
            command=self.generate_consultas_file,
            bg="orange",
            fg="white",
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="💊 Generar Archivo Medicamentos",
            command=self.generate_medicamentos_file,
            bg="purple",
            fg="white",
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="📦 Generar Ambos",
            command=self.generate_both_files,
            bg="navy",
            fg="white",
            font=("Arial", 12, "bold"),
        ).pack(side="left", padx=5)

    def setup_config_tab(self, notebook):
        """Pestaña de configuración"""
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="⚙️ Configuración")

        # Códigos GES
        codes_frame = tk.LabelFrame(
            config_frame, text="Códigos de Prestación GES", font=("Arial", 12, "bold")
        )
        codes_frame.pack(fill="x", padx=10, pady=10)

        codes_text = """
EPOC / Asma / Fibrosis Quística: PS = 51
Paliativos: PS = 67

Nota: Los códigos trazadora están configurados en ges_config.py
        """
        tk.Label(codes_frame, text=codes_text, justify="left").pack(anchor="w", padx=10, pady=5)

        # Rutas
        paths_frame = tk.LabelFrame(
            config_frame, text="Rutas de Archivos", font=("Arial", 12, "bold")
        )
        paths_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            paths_frame, text=f"Inputs: {self.processor.inputs_path}", font=("Courier", 9)
        ).pack(anchor="w", padx=10, pady=2)
        tk.Label(
            paths_frame, text=f"Outputs: {self.processor.outputs_path}", font=("Courier", 9)
        ).pack(anchor="w", padx=10, pady=2)

        # Selección manual de archivos
        manual_frame = tk.LabelFrame(
            config_frame, text="Selección manual de archivos", font=("Arial", 12, "bold")
        )
        manual_frame.pack(fill="x", padx=10, pady=10)

        tk.Checkbutton(
            manual_frame,
            text="Usar selección manual",
            variable=self.manual_mode,
            command=self.toggle_manual_mode,
        ).pack(anchor="w", padx=10, pady=5)

        self.manual_labels = {
            "consultas": tk.StringVar(value="No seleccionado"),
            "farmacia": tk.StringVar(value="No seleccionado"),
            "recetas_ges": tk.StringVar(value="No seleccionado"),
        }

        self._add_manual_selector(
            manual_frame,
            "Consultas (CSV)",
            self.manual_labels["consultas"],
            self.select_consultas_file,
        )
        self._add_manual_selector(
            manual_frame,
            "Farmacia (CSV)",
            self.manual_labels["farmacia"],
            self.select_farmacia_file,
        )
        self._add_manual_selector(
            manual_frame,
            "Recetas GES (XLS/XLSX)",
            self.manual_labels["recetas_ges"],
            self.select_recetas_files,
        )

        tk.Button(
            manual_frame,
            text="Limpiar selección",
            command=self.clear_manual_selection,
        ).pack(anchor="w", padx=10, pady=5)

        # Botones de configuración
        config_buttons = tk.Frame(config_frame)
        config_buttons.pack(fill="x", padx=10, pady=10)

        tk.Button(
            config_buttons, text="📁 Abrir Carpeta Inputs", command=self.open_inputs_folder
        ).pack(side="left", padx=5)
        tk.Button(
            config_buttons, text="📁 Abrir Carpeta Outputs", command=self.open_outputs_folder
        ).pack(side="left", padx=5)

    def setup_results_frame(self):
        """Frame de resultados en la parte inferior"""
        results_frame = tk.LabelFrame(
            self.root, text="Resultados y Log", font=("Arial", 12, "bold")
        )
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(results_frame, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=5)

        # Status label
        self.status_label = tk.Label(results_frame, text="Listo para procesar", fg="blue")
        self.status_label.pack(pady=2)

        # Text area para resultados
        text_frame = tk.Frame(results_frame)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.results_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 9), height=8)
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _add_manual_selector(self, parent, label, var, command):
        row = tk.Frame(parent)
        row.pack(fill="x", padx=10, pady=2)
        tk.Label(row, text=f"{label}:", width=22, anchor="w").pack(side="left")
        tk.Label(row, textvariable=var, anchor="w").pack(side="left", padx=6, fill="x", expand=True)
        tk.Button(row, text="Seleccionar", command=command).pack(side="right")

    def toggle_manual_mode(self):
        self.processor.auto_select_files = not self.manual_mode.get()
        mode = "manual" if self.manual_mode.get() else "automático"
        self.log_message(f"🔧 Modo de selección: {mode}")

    def select_consultas_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de CONSULTAS",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=self.processor.inputs_path,
        )
        if filename:
            self.manual_mode.set(True)
            self.processor.auto_select_files = False
            self.manual_files["consultas"] = filename
            self.processor.selected_files["consultas"] = filename
            self.manual_labels["consultas"].set(os.path.basename(filename))
            self.log_message(f"✅ Consultas seleccionadas: {os.path.basename(filename)}")

    def select_farmacia_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de FARMACIA",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=self.processor.inputs_path,
        )
        if filename:
            self.manual_mode.set(True)
            self.processor.auto_select_files = False
            self.manual_files["farmacia"] = filename
            self.processor.selected_files["farmacia"] = filename
            self.manual_labels["farmacia"].set(os.path.basename(filename))
            self.log_message(f"✅ Farmacia seleccionada: {os.path.basename(filename)}")

    def select_recetas_files(self):
        filenames = filedialog.askopenfilenames(
            title="Seleccionar archivos de RECETAS GES",
            filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")],
            initialdir=self.processor.inputs_path,
        )
        if filenames:
            self.manual_mode.set(True)
            self.processor.auto_select_files = False
            self.manual_files["recetas_ges"] = list(filenames)
            self.processor.selected_files["recetas_ges"] = list(filenames)
            self.manual_labels["recetas_ges"].set(f"{len(filenames)} archivos")
            self.log_message(f"✅ Recetas GES seleccionadas: {len(filenames)} archivos")

    def clear_manual_selection(self):
        self.manual_files = {"consultas": None, "farmacia": None, "recetas_ges": []}
        self.processor.selected_files = {}
        self.manual_labels["consultas"].set("No seleccionado")
        self.manual_labels["farmacia"].set("No seleccionado")
        self.manual_labels["recetas_ges"].set("No seleccionado")
        self.log_message("🧹 Selección manual limpiada")

    def update_status(self, message, color="blue"):
        """Actualizar mensaje de estado"""
        self.status_label.config(text=message, fg=color)
        self.root.update()

    def log_message(self, message):
        """Agregar mensaje al log"""
        self.results_text.insert(tk.END, f"{message}\n")
        self.results_text.see(tk.END)
        self.root.update()

    def verificar_archivos(self):
        """Verificar existencia de archivos"""
        self.update_status("Verificando archivos...", "orange")

        for filename, status_label in self.file_status.items():
            if any(ch in filename for ch in ["*", "?"]):
                pattern = os.path.join(self.processor.inputs_path, filename)
                matches = glob.glob(pattern)
                if matches:
                    status_label.config(text=f"✅ Encontrado ({len(matches)})", fg="green")
                    self.log_message(f"✅ {filename} encontrado: {len(matches)} archivo(s)")
                else:
                    status_label.config(text="❌ No encontrado", fg="red")
                    self.log_message(f"❌ {filename} no encontrado")
            else:
                filepath = os.path.join(self.processor.inputs_path, filename)
                if os.path.exists(filepath):
                    status_label.config(text="✅ Encontrado", fg="green")
                    self.log_message(f"✅ {filename} encontrado")
                else:
                    status_label.config(text="❌ No encontrado", fg="red")
                    self.log_message(f"❌ {filename} no encontrado")

        self.update_status("Verificación completada", "green")

    def run_full_analysis(self):
        """Ejecutar análisis completo con nuevas funcionalidades V2.0"""
        self.progress.start()
        self.update_status("Ejecutando análisis completo V2.0...", "orange")

        def run_analysis():
            try:
                self.log_message("🚀 Iniciando análisis completo V2.0...")
                self.log_message("⭐ Funcionalidades: Trazadoras Múltiples | Verificación GES | Sin Duplicados")
                
                # Configurar modo de selección
                self.processor.auto_select_files = not self.manual_mode.get()
                if self.manual_mode.get():
                    if not self.processor.selected_files.get("consultas") or not self.processor.selected_files.get("farmacia"):
                        self.log_message("❌ Faltan archivos requeridos (consultas/farmacia) en selección manual")
                        self.update_status("Faltan archivos en selección manual", "red")
                        return

                # Cargar todos los datos incluyendo nuevos archivos
                self.log_message("📁 Cargando archivos de datos...")
                self.processor.load_data()
                self.processor.load_medicamentos_ges()
                self.processor.load_clasificacion_paliativos()
                self.processor.load_severidad_fq()
                
                self.log_message("✅ Archivos cargados correctamente")
                
                # Procesar medicamentos con nuevas funcionalidades
                self.log_message("💊 Procesando medicamentos (con verificación población GES)...")
                archivo_medicamentos = os.path.join(
                    self.processor.outputs_path, "archivo_farmacia_ges_completo.xlsx"
                )
                self.processor.procesar_medicamentos_para_carga(
                    self.processor.farmacia_df, 
                    archivo_medicamentos
                )
                
                # Procesar consultas
                self.log_message("🏥 Procesando consultas (eliminando duplicados)...")
                archivo_consultas = os.path.join(
                    self.processor.outputs_path, "archivo_consultas_ges_completo.xlsx"
                )
                self.processor.procesar_consultas_para_carga(
                    self.processor.consulta_df,
                    archivo_consultas
                )
                
                # Verificar archivos generados
                archivos_generados = []
                for archivo in [archivo_medicamentos, archivo_consultas]:
                    if os.path.exists(archivo):
                        size = os.path.getsize(archivo) / 1024
                        archivos_generados.append(archivo)
                        self.log_message(f"   ✅ {archivo} ({size:.1f} KB)")
                
                # Verificar archivo de casos para revisión
                archivo_revision = archivo_medicamentos.replace('.xlsx', '_CASOS_REVISION.xlsx')
                if os.path.exists(archivo_revision):
                    size = os.path.getsize(archivo_revision) / 1024
                    self.log_message(f"   📋 {archivo_revision} ({size:.1f} KB) - CASOS NO-GES PARA REVISIÓN")
                
                if len(archivos_generados) > 0:
                    self.log_message("✅ Análisis completado exitosamente")
                    self.log_message(f"📁 Archivos generados: {len(archivos_generados)}")
                    self.log_message("🎯 MEJORAS V2.0:")
                    self.log_message("   • ASMA: 6 trazadoras diferentes")
                    self.log_message("   • FIBROSIS: 4 trazadoras por severidad")
                    self.log_message("   • PALIATIVOS: Nueva lógica *-NO = no oncológicos")
                    self.log_message("   • SIN DUPLICADOS: Eliminación automática")
                    self.log_message("   • VERIFICACIÓN GES: Solo pacientes válidos")
                    self.update_status("Análisis V2.0 completado", "green")
                else:
                    self.log_message("❌ Error: No se generaron archivos")
                    self.update_status("Error en análisis", "red")

            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                self.update_status("Error", "red")
            finally:
                self.progress.stop()

        thread = threading.Thread(target=run_analysis)
        thread.daemon = True
        thread.start()

    def load_medicamentos_ges(self):
        """Cargar archivo de medicamentos GES"""
        filename = filedialog.askopenfilename(
            title="Seleccionar Archivo de Medicamentos GES",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=self.processor.inputs_path,
        )

        if filename:
            # Copiar archivo a inputs si no está ahí
            import shutil

            target = os.path.join(self.processor.inputs_path, "Medicamentos GES (1).xlsx")
            shutil.copy2(filename, target)
            self.log_message(f"📋 Medicamentos GES cargado: {os.path.basename(filename)}")

    def analyze_medicamentos(self):
        """Analizar medicamentos GES"""
        self.update_status("Analizando medicamentos...", "orange")

        try:
            self.processor.auto_select_files = not self.manual_mode.get()
            self.processor.load_data()
            self.processor.analizar_medicamentos_ges()

            # Mostrar resultados en el tree
            self.med_tree.delete(*self.med_tree.get_children())

            if self.processor.medicamentos_encontrados:
                # Agregar coincidencias
                for med in self.processor.medicamentos_encontrados["coincidencias"]:
                    self.med_tree.insert(
                        "",
                        "end",
                        values=(med["medicamento_administrado"][:50], "✅ GES", med["pacientes"]),
                    )

                # Agregar no coincidencias
                for med in self.processor.medicamentos_encontrados["no_coincidencias"]:
                    self.med_tree.insert(
                        "",
                        "end",
                        values=(
                            med["medicamento_administrado"][:50],
                            "❓ No GES",
                            med["pacientes"],
                        ),
                    )

                self.log_message("✅ Análisis de medicamentos completado")
                self.update_status("Análisis completado", "green")

        except Exception as e:
            self.log_message(f"❌ Error analizando medicamentos: {str(e)}")
            self.update_status("Error", "red")

    def generate_consultas_file(self):
        """Generar archivo de consultas"""
        self.update_status("Generando archivo de consultas...", "orange")
        try:
            self.processor.auto_select_files = not self.manual_mode.get()
            self.processor.load_data()
            archivo_consultas = os.path.join(
                self.processor.outputs_path, "archivo_consultas_ges_completo.xlsx"
            )
            self.processor.procesar_consultas_para_carga(
                self.processor.consulta_df, archivo_consultas
            )
            self.log_message("✅ Archivo de consultas generado")
            self.update_status("Archivo generado", "green")
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            self.update_status("Error", "red")

    def generate_medicamentos_file(self):
        """Generar archivo de medicamentos"""
        self.update_status("Generando archivo de medicamentos...", "orange")
        try:
            self.processor.auto_select_files = not self.manual_mode.get()
            self.processor.load_data()
            archivo_medicamentos = os.path.join(
                self.processor.outputs_path, "archivo_farmacia_ges_completo.xlsx"
            )
            self.processor.procesar_medicamentos_para_carga(
                self.processor.farmacia_df, archivo_medicamentos
            )
            self.log_message("✅ Archivo de medicamentos generado")
            self.update_status("Archivo generado", "green")
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            self.update_status("Error", "red")

    def generate_both_files(self):
        """Generar ambos archivos"""
        self.progress.start()
        self.update_status("Generando archivos de carga...", "orange")

        def generate():
            try:
                self.processor.auto_select_files = not self.manual_mode.get()
                self.processor.load_data()
                archivo_consultas = os.path.join(
                    self.processor.outputs_path, "archivo_consultas_ges_completo.xlsx"
                )
                archivo_medicamentos = os.path.join(
                    self.processor.outputs_path, "archivo_farmacia_ges_completo.xlsx"
                )
                self.processor.procesar_consultas_para_carga(
                    self.processor.consulta_df, archivo_consultas
                )
                self.processor.procesar_medicamentos_para_carga(
                    self.processor.farmacia_df, archivo_medicamentos
                )
                self.log_message("✅ Archivos de carga generados")
                self.update_status("Archivos generados", "green")
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                self.update_status("Error", "red")
            finally:
                self.progress.stop()

        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()

    def open_inputs_folder(self):
        """Abrir carpeta de inputs"""
        os.startfile(self.processor.inputs_path)

    def open_outputs_folder(self):
        """Abrir carpeta de outputs"""
        os.startfile(self.processor.outputs_path)

    def run(self):
        """Iniciar la aplicación"""
        self.root.mainloop()


if __name__ == "__main__":
    app = GESAdvancedAnalyzer()
    app.run()
