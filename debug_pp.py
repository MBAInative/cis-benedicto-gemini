# -*- coding: utf-8 -*-
"""
Script de diagnostico para analizar problema PP en estudios 3524, 3528, 3530, 3536
Guarda resultados en formato JSON para facil lectura
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
]

results = {}

for path in ESTUDIOS:
    if not os.path.exists(path):
        continue
    
    nombre = os.path.basename(path)
    results[nombre] = {}
    
    try:
        estudio = crear_estudio(path)
        
        vd = estudio.extraer_voto_directo()
        rec = estudio.extraer_recuerdo_voto()
        cis = estudio.extraer_estimacion_cis()
        aldabon = estudio.calcular_aldabon_gemini()
        
        partidos_ref = estudio.get_partidos_referencia()
        config = estudio.get_context_biases()
        
        pp_vd = vd.get('PP', 0)
        pp_rec = rec.get('PP', 0)
        pp_ref = partidos_ref.get('PP', 0)
        
        sum_rec = sum(rec.values()) if rec else 1
        pp_rec_norm = (pp_rec / sum_rec) * 100 if sum_rec > 0 else 0
        k_raw = pp_ref / pp_rec_norm if pp_rec_norm > 0 else 1.0
        k_amort = 1.0 + (k_raw - 1.0) * 0.40
        
        phi = config['fidelidad'].get('PP', 1.0)
        lam = config['momentum'].get('PP', 1.0)
        
        base = pp_vd * k_amort * phi
        final_calc = base * lam
        
        results[nombre] = {
            "voto_directo": {p: vd.get(p, 'N/A') for p in ['PP', 'PSOE', 'VOX', 'SUMAR']},
            "recuerdo": {p: rec.get(p, 'N/A') for p in ['PP', 'PSOE', 'VOX', 'SUMAR']},
            "estimacion_cis": {p: cis.get(p, 'N/A') for p in ['PP', 'PSOE', 'VOX', 'SUMAR']},
            "aldabon_gemini": {p: aldabon.get(p, 'N/A') for p in ['PP', 'PSOE', 'VOX', 'SUMAR']},
            "calculo_pp": {
                "voto_directo": round(pp_vd, 2),
                "recuerdo_bruto": round(pp_rec, 2),
                "recuerdo_norm": round(pp_rec_norm, 2),
                "referencia_23j": round(pp_ref, 2),
                "k_raw": round(k_raw, 4),
                "k_amort": round(k_amort, 4),
                "phi": phi,
                "lambda": lam,
                "base_calc": round(base, 2),
                "final_calc": round(final_calc, 2),
                "aldabon_output": aldabon.get('PP', 'N/A')
            }
        }
    except Exception as e:
        results[nombre] = {"error": str(e)}

with open("debug_pp_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("OK")
