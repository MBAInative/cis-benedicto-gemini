
import pandas as pd
import sys

# Encoding fix
sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    file_path = 'data/cis_studies/3536_multi.xlsx'
output_file = 'structure_info.txt'

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Inspecting {file_path}...\n")
        xl = pd.ExcelFile(file_path)
        f.write(f"Sheet Names: {xl.sheet_names}\n")
        
        # Dump Estimación if exists (Key for Avance)
        sheet = 'Estimación de Voto'
        if sheet in xl.sheet_names:
            f.write(f"\n--- Head of {sheet} ---\n")
            df_est = pd.read_excel(xl, sheet_name=sheet)
            f.write(df_est.head(20).to_string())
            f.write("\n-------------------\n")

        sheet = 'RV EG23'
        if sheet in xl.sheet_names:
             f.write(f"\n--- Head of {sheet} ---\n")
             df_rv = pd.read_excel(xl, sheet_name=sheet)
             f.write(df_rv.head(20).to_string())
             f.write("\n-------------------\n")

        # Search for Intention Questions in Resultados
        sheet = 'Resultados'
        if sheet in xl.sheet_names:
             f.write(f"\n--- Searching {sheet} for Vote Intention ---\n")
             df = pd.read_excel(xl, sheet_name=sheet)
             # Search for keywords
             keywords = ["Si mañana se celebrasen", "intención de voto", "+ simpatía", "VOTO+SIMPATÍA"]
             for key in keywords:
                 # Use regex=False to avoid errors with '+'
                 matches = df[df.apply(lambda row: row.astype(str).str.contains(key, case=False, regex=False).any(), axis=1)]
                 if not matches.empty:
                     f.write(f"Found '{key}' at rows:\n")
                     f.write(matches.head(10).to_string())
                     f.write("\n")
                     
                     # Print context around first match
                     first_idx = matches.index[0]
                     start = max(0, first_idx - 5)
                     end = min(len(df), first_idx + 40) # Show 40 rows to see the options
                     f.write(f"Context for first '{key}' match:\n")
                     f.write(df.iloc[start:end].to_string())
                     f.write("\n-------------------\n")
             
    print(f"Done. Wrote to {output_file}")
        
except Exception as e:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Error: {e}")
    print(f"Error: {e}")
