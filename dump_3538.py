import pandas as pd
df = pd.read_excel('data/cis_studies/3538_multi.xlsx', sheet_name='Resultados Extremadura ', header=None)

def print_table(start, end):
    print(f"\n--- Rows {start} to {end} ---")
    for i in range(start, end):
        row = df.iloc[i].tolist()
        print(f"R{i}: {row[:6]}")

# Table 1: P11 (Intención?)
print_table(240, 260)

# Table 2: P12R (????)
print_table(259, 275)

# Table 3: P13 (Simpatía?)
print_table(279, 290)

# Table 4: Voto+Simpatía?
print_table(295, 305)
