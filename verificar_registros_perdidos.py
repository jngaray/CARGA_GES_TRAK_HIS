import pandas as pd

# Leer consolidado antiguo
df_old = pd.read_excel('outputs/FARMACIA_CONSOLIDATED_OLD.xlsx')

# Buscar esos registros
target_ruts = ['15946945', '10089095']
target_pres = [2508141, 2508156]

print('En consolidado ANTIGUO:')
found = False
for rut in target_ruts:
    for pres in target_pres:
        match = df_old[(df_old['RUT'].astype(str) == rut) & (df_old['PRESTACION'].astype(int) == pres)]
        if len(match) > 0:
            print(f'✓ Encontrado: RUT {rut}, PREST {pres}: {len(match)} registros')
            print(f'  DV: {match["DV"].values[0]}')
            found = True

if not found:
    print('✗ Ninguno de los 2 registros perdidos se encuentra en el consolidado antiguo')

# Verificar si estos RUTs aparecen en otro lado
print(f'\nTotal de registros con RUT 15946945: {len(df_old[df_old["RUT"].astype(str) == "15946945"])}')
print(f'Total de registros con RUT 10089095: {len(df_old[df_old["RUT"].astype(str) == "10089095"])}')

# Ver si aparecen con diferentes prestaciones
print('\nDetalle de RUT 15946945:')
print(df_old[df_old['RUT'].astype(str) == '15946945'][['RUT', 'DV', 'PRESTACION', 'TIPO']])

print('\nDetalle de RUT 10089095:')
print(df_old[df_old['RUT'].astype(str) == '10089095'][['RUT', 'DV', 'PRESTACION', 'TIPO']])
