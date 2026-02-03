import pandas as pd
import glob

v1_range = (13.4, 13.7)
v2_range = (27.4, 27.7)

for path in glob.glob('data/cis_studies/3538*.xlsx'):
    xl = pd.ExcelFile(path)
    for sheet in xl.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet, header=None)
        rows_v1 = []
        rows_v2 = []
        for i in range(len(df)):
            for j in range(len(df.columns)):
                try:
                    val = float(str(df.iloc[i, j]).replace(',', '.'))
                    if v1_range[0] <= val <= v1_range[1]: rows_v1.append(i)
                    if v2_range[0] <= val <= v2_range[1]: rows_v2.append(i)
                except: pass
        
        for r1 in rows_v1:
            for r2 in rows_v2:
                if abs(r1 - r2) < 15:
                    print(f"PROXIMITY MATCH in {path} - Sheet: {sheet}")
                    print(f"  V1 (13.5-ish) at row {r1}: {df.iloc[r1].tolist()[:3]}")
                    print(f"  V2 (27.5-ish) at row {r2}: {df.iloc[r2].tolist()[:3]}")
