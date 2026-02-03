from cis_analyzer import analyze_cis_professional
from cis_data_manager import list_available_studies, get_study_file, get_id_from_name
import os

available = list_available_studies()
print(f"Detected {len(available)} studies.")

for s_display in available[:3]: # Test first 3
    study_id = get_id_from_name(s_display)
    print(f"\nTesting {s_display} (ID: {study_id})...")
    path, st_type = get_study_file(study_id)
    print(f"Path: {path}, Type: {st_type}")
    
    if path and os.path.exists(path):
        import os
        res = analyze_cis_professional(path, study_type=st_type)
        if res:
             print(f"SUCCESS: Loaded {len(res['benedicto'])} parties.")
             print(f"PSOE Official: {res['official'].get('PSOE')}")
             print(f"PSOE Aldabon: {res['benedicto'].get('PSOE')}")
        else:
             print("FAILURE: Analysis failed.")
    else:
        print("FAILURE: Path not found.")
