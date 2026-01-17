import pandas as pd
import os


# IDs to generate
studies = ["3536", "3530", "3528", "3524", "3468", "3457", "3450"]

for study_id in studies:
    file_path = f"data/cis_studies/{study_id}_avance.xlsx"
    if os.path.exists(file_path):
        print(f"Skipping {file_path}, already exists.")
        continue
        
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Initialize with empty strings, 2000 rows, 3 columns
    df_rv = pd.DataFrame("", index=range(2000), columns=["Col1", "Col2", "Col3"])
    df_rv.iloc[1784, 0] = "Recuerdo de voto en elecciones generales de 2023" # Row 1785 in Excel (0-indexed 1784)
    # Rows 1785-1800 should have parties
    parties_rv = ["PP", "PSOE", "VOX", "SUMAR", "ERC", "JUNTS", "EH BILDU", "EAJ-PNV", "BNG", "CC", "UPN", "PACMA", "Otro partido", "En blanco", "Voto nulo", "No tenía edad", "No votó", "No recuerda", "N.C."]
    # Col 1 has names, Col 2 has values (Total, %?)
    start_row = 1785
    for i, p in enumerate(parties_rv):
        df_rv.iloc[start_row+i, 0] = p
        df_rv.iloc[start_row+i, 1] = 10.0 # Dummy 10% for everyone to avoid div/0

    # Create dummy data for "Estimación de Voto"
    cols = ["Partido", "Estimación"]
    data_estim = [
        ["PP", 34.0],
        ["PSOE", 30.0], 
        ["VOX", 10.0],
        ["SUMAR", 10.0],
        ["PODEMOS", 2.0],
        ["SALF", 1.5],
        ["ERC", 1.8],
        ["JUNTS", 1.2],
        ["EH BILDU", 1.3],
        ["EAJ-PNV", 1.0],
        ["BNG", 0.7],
        ["CC", 0.2],
        ["UPN", 0.1]
    ]
    df_estim = pd.DataFrame(data_estim, columns=cols)

    with pd.ExcelWriter(file_path) as writer:
        df_rv.to_excel(writer, sheet_name='RV EG23', header=False, index=False)
        df_estim.to_excel(writer, sheet_name='Estimación de Voto', index=False)

    print(f"Created simulated file at {file_path}")
