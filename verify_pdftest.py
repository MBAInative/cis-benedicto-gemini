from cis_pdf_processor import extract_official_data_from_pdf
import os

pdf_path = "data/cis_studies/3536_Estimacion.pdf"
if os.path.exists(pdf_path):
    print(f"Testing PDF extraction for {pdf_path}")
    df = extract_official_data_from_pdf(pdf_path)
    if df is not None:
        print("Success!")
        print(df)
    else:
        print("Failed to extract data.")
else:
    print(f"PDF not found: {pdf_path}")
