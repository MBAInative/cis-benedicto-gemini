import os
import pandas as pd
import requests

# Mapping of Month-Year to Study ID (Approximate/Known)
# Mapping of Month-Year to Study ID (Approximate/Known)
# Source: CIS Barometer Search (2024-2025)
# Mapping of Month-Year to Study ID (Strictly these 5)
STUDY_MAP = {
    "Enero 2026": "3540",
    "Diciembre 2025": "3536",
    "Noviembre 2025": "3530", 
    "Octubre 2025": "3528",
    "Septiembre 2025": "3524"
}

DATA_DIR = "data/cis_studies"

def get_study_file(study_name):
    """
    Returns (path_to_excel, status_or_type).
    Status types: 'AVANCE', 'BAROMETRO', or error message.
    """
    study_id = STUDY_MAP.get(study_name)
    if not study_id:
        return None, "Estudio no identificado."
    
    # Priority 1: Avance (Self-contained) -> XXXX-multi_A.xlsx
    avance_name = f"{study_id}-multi_A.xlsx"
    
    # Priority 2: Barometro (Needs PDF usually) -> XXXX-multi.xlsx or XXXX_multi.xlsx
    baro_names = [f"{study_id}-multi.xlsx", f"{study_id}_multi.xlsx"]

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    # Check Avance
    path = os.path.join(DATA_DIR, avance_name)
    if os.path.exists(path):
        return os.path.abspath(path), "AVANCE"
    if os.path.exists(avance_name): # Root fallback
        return os.path.abspath(avance_name), "AVANCE"

    # Check Barometro
    for b_name in baro_names:
        path = os.path.join(DATA_DIR, b_name)
        if os.path.exists(path):
             return os.path.abspath(path), "BAROMETRO"
        if os.path.exists(b_name): # Root fallback
             return os.path.abspath(b_name), "BAROMETRO"

    # If not found
    cis_url = f"https://www.cis.es/cis/opencms/ES/11_barometros/estudio.html?id={study_id}"
    return None, f"Archivos no encontrados para estudio {study_id}. Se requiere '{study_id}-multi_A.xlsx' (Avance) o '{study_id}-multi.xlsx' (Barómetro)."

def list_available_studies():
    return list(STUDY_MAP.keys())
