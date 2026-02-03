import pandas as pd
import os
import glob

def search_in_excel(path, v1, v2):
    try:
        xl = pd.ExcelFile(path)
        for sheet in xl.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet, header=None)
            found1 = []
            found2 = []
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    val = str(df.iloc[i, j])
                    if v1 in val: found1.append((sheet, i, j, val))
                    if v2 in val: found2.append((sheet, i, j, val))
            
            if found1 and found2:
                print(f"MATCH in {path} - Sheet: {sheet}")
                print(f"  {v1} at: {found1[:3]}")
                print(f"  {v2} at: {found2[:3]}")
    except Exception as e:
        pass

files = glob.glob('data/cis_studies/*.xlsx')
for f in files:
    search_in_excel(f, "13.5", "27.5")
