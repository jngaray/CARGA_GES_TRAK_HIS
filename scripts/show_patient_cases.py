import os
from datetime import datetime

import pandas as pd


def format_rut(rut_number, dv):
    """Combine RUT number and verification digit into standard format"""
    if pd.isna(rut_number) or pd.isna(dv):
        return None
    return f"{rut_number}-{dv}"


def load_csv_safely(filename, separator=";"):
    """Load CSV with proper separator and encoding"""
    try:
        df = pd.read_csv(filename, sep=separator, encoding="latin-1", on_bad_lines="skip")
        return df
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None


def show_detailed_cases():
    """Show detailed individual patient cases"""

    print("=" * 80)
    print("DETAILED GES PATIENT CASES ANALYSIS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    try:
        # Load data
        print("Loading data files...")

        # Define paths relative to parent directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        inputs_path = os.path.join(base_path, "inputs")

        ges_df = pd.read_excel(os.path.join(inputs_path, "RUT_pob_ges.xlsx"))
        consulta_df = load_csv_safely(os.path.join(inputs_path, "reporte_consulta_ago.csv"), ";")
        farmacia_df = load_csv_safely(os.path.join(inputs_path, "reporte_farmacia_ago.csv"), ";")

        if farmacia_df is not None:
            # Fix RUT format in pharmacy data
            farmacia_df["RUT_Combined"] = [
                format_rut(row["RutPaciente"], row["DVPaciente"])
                for _, row in farmacia_df.iterrows()
            ]
            farmacia_df = farmacia_df.dropna(subset=["RUT_Combined"])

        # Get patient sets
        ges_patients = set(ges_df["RUT"].astype(str))
        appointment_patients = set()
        medication_patients = set()

        if consulta_df is not None:
            appointment_patients = set(consulta_df["RUNPaciente"].astype(str))
            ges_with_appointments = ges_patients.intersection(appointment_patients)
        else:
            ges_with_appointments = set()

        if farmacia_df is not None:
            medication_patients = set(farmacia_df["RUT_Combined"].astype(str))
            ges_with_medications = ges_patients.intersection(medication_patients)
        else:
            ges_with_medications = set()

        ges_with_both = ges_patients.intersection(appointment_patients).intersection(
            medication_patients
        )

        print(f"\n📊 SUMMARY:")
        print(f"Total GES Patients: {len(ges_patients):,}")
        print(
            f"With Appointments: {len(ges_with_appointments):,} ({len(ges_with_appointments)/len(ges_patients)*100:.1f}%)"
        )
        print(
            f"With Medications: {len(ges_with_medications):,} ({len(ges_with_medications)/len(ges_patients)*100:.1f}%)"
        )
        print(
            f"With Complete Care: {len(ges_with_both):,} ({len(ges_with_both)/len(ges_patients)*100:.1f}%)"
        )

        print("\n" + "=" * 80)
        print("DETAILED PATIENT CASES (First 30 with complete care)")
        print("=" * 80)

        # Show detailed cases for patients with both appointments and medications
        sample_patients = sorted(list(ges_with_both))[:30]

        for i, patient_rut in enumerate(sample_patients, 1):
            print(f"\n🏥 CASE #{i:2d} - PATIENT RUT: {patient_rut}")
            print("-" * 60)

            # Get GES condition
            patient_info = ges_df[ges_df["RUT"].astype(str) == patient_rut]
            if len(patient_info) > 0:
                condition = patient_info.iloc[0]["Patologia"]
                print(f"📋 GES Condition: {condition}")

            # Get appointment details
            if consulta_df is not None:
                appointments = consulta_df[consulta_df["RUNPaciente"].astype(str) == patient_rut]
                print(f"📅 Total Appointments: {len(appointments)}")

                attended = appointments[appointments["EstadoCita_Desc"] == "Atendido"]
                no_show = appointments[appointments["EstadoCita_Desc"] == "No Atendido"]

                print(f"   ✅ Attended: {len(attended)}")
                print(f"   ❌ No-show: {len(no_show)}")

                print("   📅 Recent Appointments:")
                for _, apt in appointments.head(5).iterrows():
                    date = apt["FechaCita"]
                    status = apt["EstadoCita_Desc"]
                    specialty = apt["EspecialidadLocal_Desc"]
                    status_icon = "✅" if status == "Atendido" else "❌"
                    print(f"      {status_icon} {date}: {specialty}")

            # Get medication details
            if farmacia_df is not None:
                medications = farmacia_df[farmacia_df["RUT_Combined"].astype(str) == patient_rut]
                print(f"💊 Total Prescriptions: {len(medications)}")

                dispensed = medications[medications["EstadoActualDeFarmacia_Desc"] == "Despachado"]
                pending = medications[medications["EstadoActualDeFarmacia_Desc"] != "Despachado"]

                print(f"   ✅ Dispensed: {len(dispensed)}")
                print(f"   ⏳ Pending: {len(pending)}")

                print("   💊 Medications:")
                unique_meds = medications["Farmaco_Desc"].value_counts()
                for med, count in unique_meds.head(5).items():
                    print(f"      • {med} (x{count})")

                if len(unique_meds) > 5:
                    print(f"      • ... and {len(unique_meds) - 5} more medications")

        # Show some patients with only appointments
        print("\n" + "=" * 80)
        print("PATIENTS WITH APPOINTMENTS ONLY (Sample)")
        print("=" * 80)

        appointments_only = ges_with_appointments - ges_with_medications
        sample_apt_only = sorted(list(appointments_only))[:10]

        for i, patient_rut in enumerate(sample_apt_only, 1):
            print(f"\n📅 CASE #{i} - PATIENT RUT: {patient_rut}")

            # Get GES condition
            patient_info = ges_df[ges_df["RUT"].astype(str) == patient_rut]
            if len(patient_info) > 0:
                condition = patient_info.iloc[0]["Patologia"]
                print(f"   📋 GES Condition: {condition}")

            # Get appointment summary
            if consulta_df is not None:
                appointments = consulta_df[consulta_df["RUNPaciente"].astype(str) == patient_rut]
                attended = len(appointments[appointments["EstadoCita_Desc"] == "Atendido"])
                print(f"   📅 Appointments: {len(appointments)} (Attended: {attended})")

        # Show some patients with only medications
        print("\n" + "=" * 80)
        print("PATIENTS WITH MEDICATIONS ONLY (Sample)")
        print("=" * 80)

        medications_only = ges_with_medications - ges_with_appointments
        sample_med_only = sorted(list(medications_only))[:10]

        for i, patient_rut in enumerate(sample_med_only, 1):
            print(f"\n💊 CASE #{i} - PATIENT RUT: {patient_rut}")

            # Get GES condition
            patient_info = ges_df[ges_df["RUT"].astype(str) == patient_rut]
            if len(patient_info) > 0:
                condition = patient_info.iloc[0]["Patologia"]
                print(f"   📋 GES Condition: {condition}")

            # Get medication summary
            if farmacia_df is not None:
                medications = farmacia_df[farmacia_df["RUT_Combined"].astype(str) == patient_rut]
                dispensed = len(
                    medications[medications["EstadoActualDeFarmacia_Desc"] == "Despachado"]
                )
                print(f"   💊 Prescriptions: {len(medications)} (Dispensed: {dispensed})")

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    show_detailed_cases()
