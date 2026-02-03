# -*- coding: utf-8 -*-
"""
Ver contenido crudo de hoja Estimacion de Voto para diagnostico
"""
import pandas as pd
import os

path = "data/cis_studies/3524_multi_A.xlsx"
xl = pd.ExcelFile(path)

with open("debug_hoja_raw.txt", "w", encoding="utf-8") as f:
    f.write(f"Hojas: {xl.sheet_names}\n\n")

    # Leer hoja de estimacion
    df = pd.read_excel(xl, sheet_name="Estimación de Voto", header=None)

    f.write(f"Primeras 30 filas de 'Estimacion de Voto':\n")
    for i in range(min(30, len(df))):
        row = df.iloc[i]
        col0 = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        col1 = str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else ""
        col2 = str(row.iloc[2]) if len(row) > 2 and pd.notna(row.iloc[2]) else ""
        col3 = str(row.iloc[3]) if len(row) > 3 and pd.notna(row.iloc[3]) else ""
        
        f.write(f"  {i:2d}: [{col0[:35]:35s}] | [{col1[:12]:12s}] | [{col2[:12]:12s}] | [{col3[:12]:12s}]\n")

print("OK")
