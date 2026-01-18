from cis_analyzer import analyze_cis_professional
from cis_data_manager import get_study_file

studies = ["Diciembre 2025", "Noviembre 2025", "Enero 2026"]

for s in studies:
    print(f"\nTesting {s}...")
    path, type_or_msg = get_study_file(s)
    print(f"Path: {path}, Type: {type_or_msg}")
    
    if path and "found" not in type_or_msg:
        res = analyze_cis_professional(path, study_type=type_or_msg)
        if res:
            print(f"SUCCESS: Loaded {len(res['benedicto'])} parties.")
            print(f"PSOE Official: {res['official'].get('PSOE')}")
            print(f"PSOE Aldabon: {res['benedicto'].get('PSOE')}")
        else:
            print("FAILURE: Returned None")
    else:
        print("FAILURE: Path not found")
