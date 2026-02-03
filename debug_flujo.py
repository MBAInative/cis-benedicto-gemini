# -*- coding: utf-8 -*-
"""
Diagnostico COMPLETO: Comparar flujo de datos entre estudios
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from cis_estudios import crear_estudio
import pandas as pd

ESTUDIOS = [
    "data/cis_studies/3536-multi.xlsx",  # Barometro - problema reportado
    "data/cis_studies/3540_multi.xlsx",  # Avance - mas reciente
    "data/cis_studies/3543-multi_A.xlsx", # Aragon - funciona bien
]

results = {}

for path in ESTUDIOS:
    if not os.path.exists(path):
        continue
    
    nombre = os.path.basename(path)
    estudio = crear_estudio(path)
    
    # Datos crudos
    vd = estudio.extraer_voto_directo()
    rec = estudio.extraer_recuerdo_voto()
    cis = estudio.extraer_estimacion_cis()
    
    # Verificar hojas disponibles
    xl = pd.ExcelFile(path)
    
    results[nombre] = {
        "tipo_clase": type(estudio).__name__,
        "hojas": xl.sheet_names[:10],
        "voto_directo_total": round(sum(vd.values()), 2) if vd else 0,
        "voto_directo": {p: round(vd.get(p, 0), 2) for p in ['PP', 'PSOE', 'VOX', 'SUMAR', 'SALF', 'No Sabe', 'Abstención']},
        "recuerdo_total": round(sum(rec.values()), 2) if rec else 0,
        "recuerdo": {p: round(rec.get(p, 0), 2) for p in ['PP', 'PSOE', 'VOX', 'SUMAR']},
        "estimacion_cis": {p: cis.get(p, 'N/A') for p in ['PP', 'PSOE', 'VOX', 'SUMAR', 'SALF']},
    }

with open("debug_flujo.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("OK - ver debug_flujo.json")
