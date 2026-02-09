from scripts.ges_data_processor import GESDataProcessor
import os

p = GESDataProcessor(auto_select_files=True)
print('Loading data...')
ok = p.load_data()
print('load_data returned', ok)
if not ok:
    raise SystemExit('Failed to load data')

out_meds = os.path.join(p.outputs_path, 'test_run_meds.xlsx')
print('Processing meds ->', out_meds)
p.procesar_medicamentos_para_carga(p.farmacia_df, out_meds)

print('\nProcessing consultas...')
out_cons = os.path.join(p.outputs_path, 'test_run_consultas.xlsx')
if hasattr(p, 'procesar_consultas_para_carga'):
    p.procesar_consultas_para_carga(p.consulta_df, out_cons)

print('Done')
