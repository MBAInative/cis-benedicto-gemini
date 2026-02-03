# -*- coding: utf-8 -*-
"""
Diagnostico: Verificar que todos los estudios usan el mismo tipo de clase
"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from cis_estudios import crear_estudio

ESTUDIOS = [
    "data/cis_studies/3524_multi_A.xlsx",
    "data/cis_studies/3528_multi_A.xlsx", 
    "data/cis_studies/3530_multi_A.xlsx",
    "data/cis_studies/3536-multi.xlsx",
    "data/cis_studies/3538_multi.xlsx",
    "data/cis_studies/3540_multi.xlsx",
    "data/cis_studies/3543-multi_A.xlsx",
]

results = {}

for path in ESTUDIOS:
    if not os.path.exists(path):
        continue
    
    nombre = os.path.basename(path)
    estudio = crear_estudio(path)
    
    ficha = estudio.extraer_ficha_tecnica()
    config = estudio.get_context_biases()
    
    results[nombre] = {
        "tipo_clase": type(estudio).__name__,
        "hoja_rv": estudio.get_hoja_rv(),
        "ficha_tipo": ficha.get('tipo'),
        "ficha_ref": ficha.get('referencia'),
        "partidos_ref": list(estudio.get_partidos_referencia().keys())[:6],
        "fidelidad_pp": config['fidelidad'].get('PP'),
        "fidelidad_psoe": config['fidelidad'].get('PSOE'),
        "momentum_pp": config['momentum'].get('PP'),
        "momentum_psoe": config['momentum'].get('PSOE'),
    }

with open("debug_tipos.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("OK - ver debug_tipos.json")
