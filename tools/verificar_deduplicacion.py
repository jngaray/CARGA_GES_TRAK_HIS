import pandas as pd

# Leer archivo
df = pd.read_excel('archivo_farmacia_ges_completo.xlsx')
print(f'Total filas en archivo: {len(df)}')

# Buscar RUT 12725553
rut_12725553 = df[df['RUT'] == 12725553]
print(f'\nRUT 12725553: {len(rut_12725553)} registros')

if len(rut_12725553) > 0:
    print('\nDETALLE DE REGISTROS:')
    print(rut_12725553[['FECHA', 'RUT', 'DV', 'PRESTACION', 'TIPO', 'PS-FAM ', 'ESPECIALIDAD']].to_string(index=False))
    
    print('\nPRESTACIONES ÚNICAS:')
    print(rut_12725553['PRESTACION'].unique())
else:
    print('No se encontró el RUT 12725553 en este archivo. Buscando en otros...')
    
# Verificar total de RUTs únicos
print(f'\nTotal RUTs únicos: {df["RUT"].nunique()}')
print(f'Total registros: {len(df)}')
