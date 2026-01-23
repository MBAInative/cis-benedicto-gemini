import os
import pandas as pd

# Mapping of Month-Year to Study ID (Approximate/Known)
# Mapping of Month-Year to Study ID (Approximate/Known)
# Source: CIS Barometer Search (2024-2025)
# Mapping of Month-Year to Study ID (Strictly these 5)
STUDY_MAP = {
    "Febrero 2026": "3543",
    "Enero 2026": "3540",
    "Diciembre 2025": "3536",
    "Noviembre 2025": "3530", 
    "Octubre 2025": "3528",
    "Septiembre 2025": "3524"
}

# Metadatos adicionales para cada estudio
STUDY_METADATA = {
    "3543": {
        "Elecciones": "Autonómicas (Aragón)", 
        "Sondeo": "Enero-Febrero 2026", 
        "N": "3.313 entrevistas",
        "Campo": "20 de enero al 3 de febrero de 2026"
    },
    "3540": {
        "Elecciones": "Generales (Barómetro)", 
        "Sondeo": "Enero 2026", 
        "N": "4.000 entrevistas (aprox.)",
        "Campo": "2 al 12 de enero de 2026"
    },
    "3536": {
        "Elecciones": "Generales (Barómetro)", 
        "Sondeo": "Diciembre 2025", 
        "N": "3.950 entrevistas",
        "Campo": "1 al 13 de diciembre de 2025"
    },
    "3530": {
        "Elecciones": "Generales (Barómetro)", 
        "Sondeo": "Noviembre 2025", 
        "N": "4.000 entrevistas",
        "Campo": "2 al 12 de noviembre de 2025"
    },
    "3528": {
        "Elecciones": "Generales (Barómetro)", 
        "Sondeo": "Octubre 2025", 
        "N": "3.800 entrevistas",
        "Campo": "1 al 11 de octubre de 2025"
    },
    "3524": {
        "Elecciones": "Generales (Barómetro)", 
        "Sondeo": "Septiembre 2025", 
        "N": "4.000 entrevistas",
        "Campo": "1 al 12 de septiembre de 2025"
    }
}

DATA_DIR = "data/cis_studies"

def get_study_metadata(study_name):
    """Retorna un dict con información del estudio."""
    study_id = STUDY_MAP.get(study_name)
    return STUDY_METADATA.get(study_id, {"Elecciones": "Nacional", "Sondeo": "Desconocido"})

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
        try:
            os.makedirs(DATA_DIR)
        except Exception:
            pass # Ignorar si no hay permisos (normal en Cloud si el dir ya debería estar en Git)
        
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
