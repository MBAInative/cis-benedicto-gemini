import pandas as pd
import os

def export_sheet(file_path):
    abs_path = os.path.abspath(file_path)
    print(f"Checking: {abs_path}")
    if not os.path.exists(abs_path):
        print(f"NOT FOUND: {abs_path}")
        return
    try:
        xl = pd.ExcelFile(abs_path)
        print(f"Sheets in {file_path}: {xl.sheet_names}")
        sheet = next((s for s in xl.sheet_names if "ESTIMACI" in s.upper()), None)
        if not sheet:
            print(f"NO ESTIMACION SHEET in {file_path}")
            return
        df = pd.read_excel(xl, sheet_name=sheet)
        output_file = os.path.basename(file_path).replace(".xlsx", "_structure.csv")
        df.iloc[:60, :12].to_csv(output_file, index=False)
        print(f"Exported to {output_file}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    base = os.path.join(os.getcwd(), "data", "cis_studies")
    print(f"Base dir: {base}")
    if os.path.exists(base):
        print(f"Contents of base: {os.listdir(base)}")
    else:
        print(f"BASE DIR NOT FOUND!")
        
    for f in os.listdir(base):
        if f.endswith(".xlsx"):
            export_sheet(os.path.join(base, f))
