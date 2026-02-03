import pandas as pd
import glob

targets = [13.4, 13.5, 13.6, 27.4, 27.5, 27.6]

def search_files(pattern):
    for path in glob.glob(pattern):
        print(f"\n--- Searching in {path} ---")
        try:
            xl = pd.ExcelFile(path)
            for sheet in xl.sheet_names:
                df = pd.read_excel(path, sheet_name=sheet, header=None)
                for i in range(len(df)):
                    for j in range(len(df.columns)):
                        val = df.iloc[i, j]
                        try:
                            fval = float(str(val).replace(',', '.'))
                            for t in targets:
                                if abs(fval - t) < 0.05:
                                    print(f"Match: {fval} at {sheet} [R{i}, C{j}]. Row label: {df.iloc[i, 0]}")
                        except:
                            pass
        except Exception as e:
            print(f"Error {path}: {e}")

search_files('data/cis_studies/353*.xlsx')
