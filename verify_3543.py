import pandas as pd
from cis_analyzer import analyze_cis_professional
import json

file_path = 'data/cis_studies/3543-multi_A.xlsx'
results = analyze_cis_professional(file_path)

if results:
    print("\n--- RESULTS FOR STUDY 3543 ---")
    print(f"Ambito: {results['meta']['ambito']}")
    print(f"Region: {results['meta'].get('region')}")
    
    print("\nVoto Directo (Raw):")
    for p, v in results['raw'].items():
        print(f"  {p}: {v}%")
        
    print("\nEstimacion Oficial CIS:")
    for p, v in results['official'].items():
        print(f"  {p}: {v}%")
        
    print("\nEstimacion Aldabon-Gemini:")
    for p, v in results['benedicto'].items():
        print(f"  {p}: {v}%")
else:
    print("Failed to analyze study 3543.")
