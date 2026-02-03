# -*- coding: utf-8 -*-
"""
Diagnostico DETALLADO: Ver exactamente de donde se extraen datos
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from cis_estudios import crear_estudio
import pandas as pd

ESTUDIOS = [
    "data/cis_studies/3524_multi_A.xlsx",
    "data/cis_studies/3528_multi_A.xlsx",
    "data/cis_studies/3530_multi_A.xlsx",
    "data/cis_studies/3536-multi.xlsx",
    "data/cis_studies/3540_multi.xlsx",
]

results = {}

for path in ESTUDIOS:
    if not os.path.exists(path):
        continue
    
    nombre = os.path.basename(path)
    estudio = crear_estudio(path)
    
    # Encontrar hoja de estimacion
    hoja_estim = estudio._encontrar_hoja_estimacion()
    
    results[nombre] = {
        "tipo_clase": type(estudio).__name__,
        "hoja_estimacion_encontrada": hoja_estim,
        "usa_resultados": 'RESULTADOS' in (hoja_estim or '').upper() if hoja_estim else False,
        "hojas_disponibles": estudio.sheet_names[:8],
    }

with open("debug_hojas.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("OK - ver debug_hojas.json")
