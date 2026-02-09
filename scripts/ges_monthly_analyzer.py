import pandas as pd
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class GESAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GES Medical Analysis Tool")
        self.root.geometry("800x600")
        
        # Data storage
        self.ges_df = None
        self.consulta_df = None
        self.farmacia_df = None
        self.results = {}
        
        self.setup_gui()
        
    def setup_gui(self):
        """Create the GUI interface"""
        # Title
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="GES MEDICAL ANALYSIS TOOL", font=("Arial", 16, "bold")).pack()
        tk.Label(title_frame, text="Monthly Analysis of GES Patient Care", font=("Arial", 10)).pack()
        
        # File selection frame
        file_frame = tk.LabelFrame(self.root, text="1. Select Data Files", font=("Arial", 12, "bold"))
        file_frame.pack(fill="x", padx=20, pady=10)
        
        # GES population file
        tk.Button(file_frame, text="Select GES Population File (Excel)", 
                 command=self.select_ges_file, width=30).pack(pady=5)
        self.ges_label = tk.Label(file_frame, text="No file selected", fg="gray")
        self.ges_label.pack()
        
        # Consultation file
        tk.Button(file_frame, text="Select Consultation Report (CSV)", 
                 command=self.select_consultation_file, width=30).pack(pady=5)
        self.consulta_label = tk.Label(file_frame, text="No file selected", fg="gray")
        self.consulta_label.pack()
        
        # Pharmacy file
        tk.Button(file_frame, text="Select Pharmacy Report (CSV)", 
                 command=self.select_pharmacy_file, width=30).pack(pady=5)
        self.farmacia_label = tk.Label(file_frame, text="No file selected", fg="gray")
        self.farmacia_label.pack()
        
        # Analysis frame
        analysis_frame = tk.LabelFrame(self.root, text="2. Run Analysis", font=("Arial", 12, "bold"))
        analysis_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(analysis_frame, text="RUN COMPLETE ANALYSIS", 
                 command=self.run_analysis, bg="green", fg="white", 
                 font=("Arial", 12, "bold"), height=2).pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(analysis_frame, mode='indeterminate')
        self.progress.pack(fill="x", padx=20, pady=5)
        
        # Status label
        self.status_label = tk.Label(analysis_frame, text="Ready to analyze", fg="blue")
        self.status_label.pack()
        
        # Results frame
        results_frame = tk.LabelFrame(self.root, text="3. Results & Export", font=("Arial", 12, "bold"))
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Results text area with scrollbar
        text_frame = tk.Frame(results_frame)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.results_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 9))
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Export buttons
        export_frame = tk.Frame(results_frame)
        export_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(export_frame, text="Export Detailed Report", 
                 command=self.export_detailed_report).pack(side="left", padx=5)
        tk.Button(export_frame, text="Export Patient Cases", 
                 command=self.export_patient_cases).pack(side="left", padx=5)
        tk.Button(export_frame, text="Export Summary CSV", 
                 command=self.export_summary_csv).pack(side="left", padx=5)
    
    def select_ges_file(self):
        file_path = filedialog.askopenfilename(
            title="Select GES Population File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            self.ges_file = file_path
            self.ges_label.config(text=f"Selected: {os.path.basename(file_path)}", fg="green")
    
    def select_consultation_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Consultation Report",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.consulta_file = file_path
            self.consulta_label.config(text=f"Selected: {os.path.basename(file_path)}", fg="green")
    
    def select_pharmacy_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Pharmacy Report",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.farmacia_file = file_path
            self.farmacia_label.config(text=f"Selected: {os.path.basename(file_path)}", fg="green")
    
    def load_csv_safely(self, filename, separator=';'):
        """Load CSV with proper separator and encoding"""
        try:
            df = pd.read_csv(filename, sep=separator, encoding='latin-1', on_bad_lines='skip')
            return df
        except Exception as e:
            self.update_status(f"Error loading {filename}: {e}", "red")
            return None
    
    def format_rut(self, rut_number, dv):
        """Combine RUT number and verification digit into standard format"""
        if pd.isna(rut_number) or pd.isna(dv):
            return None
        return f"{rut_number}-{dv}"
    
    def update_status(self, message, color="blue"):
        """Update status label"""
        self.status_label.config(text=message, fg=color)
        self.root.update()
    
    def run_analysis(self):
        """Run the complete analysis in a separate thread"""
        if not hasattr(self, 'ges_file') or not hasattr(self, 'consulta_file') or not hasattr(self, 'farmacia_file'):
            messagebox.showerror("Error", "Please select all three files before running analysis")
            return
        
        # Start progress bar
        self.progress.start()
        self.update_status("Running analysis...", "orange")
        
        # Run analysis in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.perform_analysis)
        thread.daemon = True
        thread.start()
    
    def perform_analysis(self):
        """Perform the actual analysis"""
        try:
            self.results_text.delete(1.0, tk.END)
            
            # 1. Load GES population data
            self.update_status("Loading GES population data...")
            self.ges_df = pd.read_excel(self.ges_file)
            ges_patients = set(self.ges_df['RUT'].astype(str))
            
            # 2. Load consultation data
            self.update_status("Loading consultation data...")
            self.consulta_df = self.load_csv_safely(self.consulta_file, ';')
            if self.consulta_df is not None:
                appointment_patients = set(self.consulta_df['RUNPaciente'].astype(str))
            else:
                appointment_patients = set()
            
            # 3. Load and fix pharmacy data
            self.update_status("Loading and fixing pharmacy data...")
            self.farmacia_df = self.load_csv_safely(self.farmacia_file, ';')
            if self.farmacia_df is not None:
                # Fix RUT format
                self.farmacia_df['RUT_Combined'] = [
                    self.format_rut(row['RutPaciente'], row['DVPaciente'])
                    for _, row in self.farmacia_df.iterrows()
                ]
                self.farmacia_df = self.farmacia_df.dropna(subset=['RUT_Combined'])
                medication_patients = set(self.farmacia_df['RUT_Combined'].astype(str))
            else:
                medication_patients = set()
            
            # 4. Perform cross-reference analysis
            self.update_status("Performing cross-reference analysis...")
            ges_with_appointments = ges_patients.intersection(appointment_patients)
            ges_with_medications = ges_patients.intersection(medication_patients)
            ges_with_both = ges_patients.intersection(appointment_patients).intersection(medication_patients)
            
            # Store results
            self.results = {
                'ges_total': len(ges_patients),
                'ges_with_appointments': len(ges_with_appointments),
                'ges_with_medications': len(ges_with_medications),
                'ges_with_both': len(ges_with_both),
                'appointment_patients': appointment_patients,
                'medication_patients': medication_patients,
                'ges_with_appointments_list': ges_with_appointments,
                'ges_with_medications_list': ges_with_medications,
                'ges_with_both_list': ges_with_both
            }
            
            # 5. Display results
            self.display_results()
            
            self.progress.stop()
            self.update_status("Analysis completed successfully!", "green")
            
        except Exception as e:
            self.progress.stop()
            self.update_status(f"Analysis failed: {str(e)}", "red")
            messagebox.showerror("Analysis Error", f"An error occurred during analysis:\n{str(e)}")
    
    def display_results(self):
        """Display analysis results in the text area"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        output = f"""
================================================================================
GES MEDICAL ANALYSIS RESULTS
Generated: {timestamp}
================================================================================

📊 SUMMARY STATISTICS:
----------------------------------------
Total GES Patients: {self.results['ges_total']:,}
GES Patients with Appointments: {self.results['ges_with_appointments']:,} ({self.results['ges_with_appointments']/self.results['ges_total']*100:.1f}%)
GES Patients with Medications: {self.results['ges_with_medications']:,} ({self.results['ges_with_medications']/self.results['ges_total']*100:.1f}%)
GES Patients with BOTH: {self.results['ges_with_both']:,} ({self.results['ges_with_both']/self.results['ges_total']*100:.1f}%)

📋 GES POPULATION BREAKDOWN:
----------------------------------------
"""
        
        # Add pathology breakdown
        if self.ges_df is not None:
            pathology_counts = self.ges_df['Patologia'].value_counts()
            for pathology, count in pathology_counts.items():
                percentage = (count / len(self.ges_df)) * 100
                output += f"{pathology}: {count:,} patients ({percentage:.1f}%)\n"
        
        # Add consultation statistics if available
        if self.consulta_df is not None:
            output += f"""
🏥 APPOINTMENT STATISTICS:
----------------------------------------
Total Appointments: {len(self.consulta_df):,}
Attended: {len(self.consulta_df[self.consulta_df['EstadoCita_Desc'] == 'Atendido']):,} ({len(self.consulta_df[self.consulta_df['EstadoCita_Desc'] == 'Atendido'])/len(self.consulta_df)*100:.1f}%)
No-show: {len(self.consulta_df[self.consulta_df['EstadoCita_Desc'] == 'No Atendido']):,} ({len(self.consulta_df[self.consulta_df['EstadoCita_Desc'] == 'No Atendido'])/len(self.consulta_df)*100:.1f}%)
"""
        
        # Add pharmacy statistics if available
        if self.farmacia_df is not None:
            output += f"""
💊 MEDICATION STATISTICS:
----------------------------------------
Total Prescriptions: {len(self.farmacia_df):,}
Dispensed: {len(self.farmacia_df[self.farmacia_df['EstadoActualDeFarmacia_Desc'] == 'Despachado']):,} ({len(self.farmacia_df[self.farmacia_df['EstadoActualDeFarmacia_Desc'] == 'Despachado'])/len(self.farmacia_df)*100:.1f}%)

Top 5 Medications:
"""
            top_meds = self.farmacia_df['Farmaco_Desc'].value_counts().head(5)
            for i, (med, count) in enumerate(top_meds.items(), 1):
                output += f"{i}. {med}: {count:,} prescriptions\n"
        
        output += """
================================================================================
Use the export buttons below to generate detailed reports and patient lists.
================================================================================
"""
        
        self.results_text.insert(tk.END, output)
    
    def export_detailed_report(self):
        """Export detailed analysis report"""
        if not self.results:
            messagebox.showwarning("No Data", "Please run analysis first")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Detailed Report"
        )
        
        if filename:
            self.generate_detailed_report(filename)
            messagebox.showinfo("Success", f"Detailed report saved to:\n{filename}")
    
    def export_patient_cases(self):
        """Export detailed patient cases to Excel"""
        if not self.results:
            messagebox.showwarning("No Data", "Please run analysis first")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save Patient Cases"
        )
        
        if filename:
            self.generate_patient_cases_excel(filename)
            messagebox.showinfo("Success", f"Patient cases saved to:\n{filename}")
    
    def export_summary_csv(self):
        """Export summary statistics to CSV"""
        if not self.results:
            messagebox.showwarning("No Data", "Please run analysis first")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Summary CSV"
        )
        
        if filename:
            self.generate_summary_csv(filename)
            messagebox.showinfo("Success", f"Summary CSV saved to:\n{filename}")
    
    def generate_detailed_report(self, filename):
        """Generate comprehensive detailed report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("COMPREHENSIVE GES MEDICAL ANALYSIS REPORT\n")
            f.write(f"Generated: {timestamp}\n")
            f.write("="*80 + "\n\n")
            
            # Summary statistics
            f.write("📊 EXECUTIVE SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total GES Patients: {self.results['ges_total']:,}\n")
            f.write(f"Patients with Appointments: {self.results['ges_with_appointments']:,} ({self.results['ges_with_appointments']/self.results['ges_total']*100:.1f}%)\n")
            f.write(f"Patients with Medications: {self.results['ges_with_medications']:,} ({self.results['ges_with_medications']/self.results['ges_total']*100:.1f}%)\n")
            f.write(f"Patients with Complete Care: {self.results['ges_with_both']:,} ({self.results['ges_with_both']/self.results['ges_total']*100:.1f}%)\n\n")
            
            # Detailed patient examples
            f.write("👥 DETAILED PATIENT CASES (First 20)\n")
            f.write("-" * 40 + "\n")
            
            sample_patients = sorted(list(self.results['ges_with_both_list']))[:20]
            
            for i, patient_rut in enumerate(sample_patients, 1):
                f.write(f"\n{i:2d}. PATIENT RUT: {patient_rut}\n")
                
                # Get GES condition
                patient_info = None
                if self.ges_df is not None:
                    patient_info = self.ges_df[self.ges_df['RUT'].astype(str) == patient_rut]
                if patient_info is not None and len(patient_info) > 0:
                    condition = patient_info.iloc[0]['Patologia']
                    f.write(f"    GES Condition: {condition}\n")
                
                # Get appointments
                if self.consulta_df is not None:
                    appointments = self.consulta_df[self.consulta_df['RUNPaciente'].astype(str) == patient_rut]
                    f.write(f"    Appointments: {len(appointments)}\n")
                    
                    for _, apt in appointments.head(3).iterrows():
                        date = apt['FechaCita']
                        status = apt['EstadoCita_Desc']
                        specialty = apt['EspecialidadLocal_Desc']
                        f.write(f"      • {date}: {specialty} ({status})\n")
                
                # Get medications
                if self.farmacia_df is not None:
                    medications = self.farmacia_df[self.farmacia_df['RUT_Combined'].astype(str) == patient_rut]
                    f.write(f"    Medications: {len(medications)} prescriptions\n")
                    
                    unique_meds = medications['Farmaco_Desc'].unique()
                    for med in unique_meds[:3]:
                        f.write(f"      • {med}\n")
                    if len(unique_meds) > 3:
                        f.write(f"      • ... and {len(unique_meds) - 3} more\n")
    
    def generate_patient_cases_excel(self, filename):
        """Generate Excel file with detailed patient cases"""
        # Create different sheets for different categories
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            
            # Sheet 1: Patients with both appointments and medications
            if len(self.results['ges_with_both_list']) > 0:
                both_data = []
                for patient_rut in self.results['ges_with_both_list']:
                    row = {'RUT': patient_rut}
                    
                    # Get GES condition
                    patient_info = None
                    if self.ges_df is not None:
                        patient_info = self.ges_df[self.ges_df['RUT'].astype(str) == patient_rut]
                    if patient_info is not None and len(patient_info) > 0:
                        row['GES_Condition'] = patient_info.iloc[0]['Patologia']
                    
                    # Count appointments and medications
                    if self.consulta_df is not None:
                        appointments = self.consulta_df[self.consulta_df['RUNPaciente'].astype(str) == patient_rut]
                        row['Total_Appointments'] = len(appointments)
                        row['Attended_Appointments'] = len(appointments[appointments['EstadoCita_Desc'] == 'Atendido'])
                    
                    if self.farmacia_df is not None:
                        medications = self.farmacia_df[self.farmacia_df['RUT_Combined'].astype(str) == patient_rut]
                        row['Total_Prescriptions'] = len(medications)
                        row['Dispensed_Prescriptions'] = len(medications[medications['EstadoActualDeFarmacia_Desc'] == 'Despachado'])
                    
                    both_data.append(row)
                
                both_df = pd.DataFrame(both_data)
                both_df.to_excel(writer, sheet_name='Complete_Care_Patients', index=False)
            
            # Sheet 2: All GES patients with appointments
            if len(self.results['ges_with_appointments_list']) > 0:
                apt_data = []
                for patient_rut in self.results['ges_with_appointments_list']:
                    row = {'RUT': patient_rut}
                    
                    patient_info = None
                    if self.ges_df is not None:
                        patient_info = self.ges_df[self.ges_df['RUT'].astype(str) == patient_rut]
                    if patient_info is not None and len(patient_info) > 0:
                        row['GES_Condition'] = patient_info.iloc[0]['Patologia']
                    
                    if self.consulta_df is not None:
                        appointments = self.consulta_df[self.consulta_df['RUNPaciente'].astype(str) == patient_rut]
                        row['Total_Appointments'] = len(appointments)
                        row['Attended_Appointments'] = len(appointments[appointments['EstadoCita_Desc'] == 'Atendido'])
                    
                    apt_data.append(row)
                
                apt_df = pd.DataFrame(apt_data)
                apt_df.to_excel(writer, sheet_name='Patients_with_Appointments', index=False)
            
            # Sheet 3: All GES patients with medications
            if len(self.results['ges_with_medications_list']) > 0:
                med_data = []
                for patient_rut in self.results['ges_with_medications_list']:
                    row = {'RUT': patient_rut}
                    
                    patient_info = None
                    if self.ges_df is not None:
                        patient_info = self.ges_df[self.ges_df['RUT'].astype(str) == patient_rut]
                    if patient_info is not None and len(patient_info) > 0:
                        row['GES_Condition'] = patient_info.iloc[0]['Patologia']
                    
                    if self.farmacia_df is not None:
                        medications = self.farmacia_df[self.farmacia_df['RUT_Combined'].astype(str) == patient_rut]
                        row['Total_Prescriptions'] = len(medications)
                        row['Dispensed_Prescriptions'] = len(medications[medications['EstadoActualDeFarmacia_Desc'] == 'Despachado'])
                    
                    med_data.append(row)
                
                med_df = pd.DataFrame(med_data)
                med_df.to_excel(writer, sheet_name='Patients_with_Medications', index=False)
    
    def generate_summary_csv(self, filename):
        """Generate summary statistics CSV"""
        summary_data = {
            'Metric': [
                'Total GES Patients',
                'GES Patients with Appointments',
                'GES Patients with Medications', 
                'GES Patients with Complete Care',
                'Appointment Coverage (%)',
                'Medication Coverage (%)',
                'Complete Care Coverage (%)'
            ],
            'Count': [
                self.results['ges_total'],
                self.results['ges_with_appointments'],
                self.results['ges_with_medications'],
                self.results['ges_with_both'],
                f"{self.results['ges_with_appointments']/self.results['ges_total']*100:.1f}%",
                f"{self.results['ges_with_medications']/self.results['ges_total']*100:.1f}%",
                f"{self.results['ges_with_both']/self.results['ges_total']*100:.1f}%"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(filename, index=False)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = GESAnalyzer()
    app.run()