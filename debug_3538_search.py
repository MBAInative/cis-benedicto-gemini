from cis_estudios import crear_estudio
import pandas as pd

path = 'data/cis_studies/3538_multi.xlsx'
e = crear_estudio(path)
hoja = 'Resultados Extremadura '
df = pd.read_excel(path, sheet_name=hoja, header=None)

print(f"Investigating {hoja}")
for i in range(len(df)):
    cell = str(df.iloc[i, 0]).upper()
    if 'VOTARÍA' in cell and ('PRÓXIMAS' in cell or 'ELECCIONES' in cell):
        skip = any(x in cell for x in ['SIMPATÍA', 'RECODIFICADA', 'VOTO+', 'VOTO +'])
        print(f"R{i} match! cell: {cell[:50]}... Skip: {skip}")
        if not skip:
            # Check validation
            is_valid = True
            for offset in range(1, 15):
                if i + offset < len(df):
                    next_cell = str(df.iloc[i + offset, 0]).upper()
                    if any(x in next_cell for x in ['RECODIFICADA', 'SIMPATÍA', 'VOTO+']):
                        is_valid = False
                        print(f"  Invalid at offset {offset}: {next_cell[:50]}...")
                        break
            print(f"  Is_valid: {is_valid}")
            if is_valid:
                print(f"  SELECTED start_row: {i}")
                # break # removed to see all matches
