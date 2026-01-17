import os
import pandas as pd
import requests

# Mapping of Month-Year to Study ID (Approximate/Known)
# Mapping of Month-Year to Study ID (Approximate/Known)
# Source: CIS Barometer Search (2024-2025)
STUDY_MAP = {
    "Enero 2026": "3540",
    "Diciembre 2025": "3536",
    "Noviembre 2025": "3530", 
    "Octubre 2025": "3528",
    "Septiembre 2025": "3524",
    "Julio 2024": "3468", # Jumping back to 2024 sample
    "Mayo 2024": "3457",
    "Abril 2024": "3450",
    "Generales 23J (Base)": "3415"
}

DATA_DIR = "data/cis_studies"

def get_study_file(study_name):
    """
    Returns the path to the study Excel file.
    If not found locally, returns None and a download URL/instruction.
    """
    study_id = STUDY_MAP.get(study_name)
    if not study_id:
        return None, "Estudio no identificado."
    
    # Check flexible filenames: 3540_avance.xlsx, Es3540.xlsx, etc.
    possible_names = [f"{study_id}_avance.xlsx", f"Es{study_id}.xlsx", f"{study_id}.xlsx"]
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    for name in possible_names:
        path = os.path.join(DATA_DIR, name)
        if os.path.exists(path):
            return path, "OK"
            
    # Check root dir for legacy support (the current 3540_avance.xlsx is in root)
    if study_id == "3540":
         if os.path.exists("3540_avance.xlsx"):
             return "3540_avance.xlsx", "OK"
    
    # If not found
    cis_url = f"https://www.cis.es/cis/opencms/ES/11_barometros/estudio.html?id={study_id}"
    return None, f"Archivo no encontrado. Por favor, descargue el Excel del estudio {study_id} desde {cis_url} y guárdelo en {DATA_DIR} como '{study_id}_avance.xlsx'."

def list_available_studies():
    return list(STUDY_MAP.keys())
