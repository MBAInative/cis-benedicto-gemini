import pandas as pd
from pypdf import PdfReader
import re
import os

def extract_official_data_from_pdf(pdf_path):
    """
    Extracts the 'Estimación de Voto' table from the CIS PDF.
    Returns a DataFrame with columns ['Partido', 'Estimación'].
    """
    print(f"Extracting data from {pdf_path}...")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    # Normalize text
    text = text.replace('\n', ' ')
    
    # Regex to find the estimation table context
    # Usually looks like "ESTIMACIÓN DE VOTO... PSOE 32.1 PP 29.8..."
    # We will look for specific party patterns followed by numbers
    
    data = {}
    
    # Common parties to look for
    parties = {
        'PSOE': r'PSOE.*?(\d+[\.,]\d+)',
        'PP': r'PP.*?(\d+[\.,]\d+)',
        'VOX': r'VOX.*?(\d+[\.,]\d+)',
        'Sumar': r'Sumar.*?(\d+[\.,]\d+)',
        'Podemos': r'Podemos.*?(\d+[\.,]\d+)',
        'SALF': r'Se Acabó la Fiesta.*?(\d+[\.,]\d+)',
        'ERC': r'ERC.*?(\d+[\.,]\d+)',
        'Junts': r'Junts.*?(\d+[\.,]\d+)',
        'EH Bildu': r'Bildu.*?(\d+[\.,]\d+)',
        'PNV': r'PNV.*?(\d+[\.,]\d+)',
        'BNG': r'BNG.*?(\d+[\.,]\d+)',
        'CCa': r'Coalición Canaria.*?(\d+[\.,]\d+)',
        'UPN': r'UPN.*?(\d+[\.,]\d+)',
        'PACMA': r'PACMA.*?(\d+[\.,]\d+)',
    }

    # Focus on the 'Estimación de Voto' section if possible
    # This is a simple heuristic: find the block of text containing "Estimación de Voto" and "válido"
    # But for now, let's just grep the first occurrence of each party's percentage 
    # appearing after the phrase "Estimación de Voto"
    
    start_marker = "Estimación de Voto"
    start_idx = text.find(start_marker)
    
    if start_idx == -1:
        print("Warning: 'Estimación de Voto' section not found explicitly. Searching entire text.")
        search_text = text
    else:
        # Search in the 2000 chars after the marker
        search_text = text[start_idx:start_idx+3000]

    print(f"Searching in text segment: {search_text[:200]}...")

    for party, pattern in parties.items():
        match = re.search(pattern, search_text, re.IGNORECASE)
        if match:
            val_str = match.group(1).replace(',', '.')
            try:
                data[party] = float(val_str)
            except ValueError:
                pass
    
    # Convert to DataFrame
    if not data:
        print("No data found!")
        return None

    df_official = pd.DataFrame(list(data.items()), columns=['Partido', 'Estimación'])
    print("Extracted Data:")
    print(df_official)
    return df_official

def append_to_excel(excel_path, df_official):
    """
    Appends the official dataframe as a new sheet 'Estimación de Voto' to the Excel file.
    """
    if df_official is None or df_official.empty:
        print("No data to append.")
        return

    print(f"Appending to {excel_path}...")
    
    # Load existing sheets
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_official.to_excel(writer, sheet_name='Estimación de Voto', index=False)
        print("Success! Sheet 'Estimación de Voto' added/updated.")
    except Exception as e:
        print(f"Error appending to Excel: {e}")

if __name__ == "__main__":
    study_id = "3536"
    base_dir = "data/cis_studies"
    pdf_path = os.path.join(base_dir, f"{study_id}_Estimacion.pdf")
    excel_path = os.path.join(base_dir, f"{study_id}_multi.xlsx")

    if os.path.exists(pdf_path) and os.path.exists(excel_path):
        df = extract_official_data_from_pdf(pdf_path)
        if df is not None:
            append_to_excel(excel_path, df)
    else:
        print(f"Files not found: {pdf_path} or {excel_path}")
