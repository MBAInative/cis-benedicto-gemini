# -*- coding: utf-8 -*-
"""
Buscar parametros para que PP > PSOE
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cis_estudios import crear_estudio

path = "data/cis_studies/3540_multi.xlsx"
estudio = crear_estudio(path)
vd = estudio.extraer_voto_directo()
rec = estudio.extraer_recuerdo_voto()

# Calcular Ks
partidos_ref = estudio.get_partidos_referencia()
sum_rec = sum(rec.values())
pp_rec_norm = (rec.get('PP', 0) / sum_rec) * 100
psoe_rec_norm = (rec.get('PSOE', 0) / sum_rec) * 100
k_pp = 1.0 + ((partidos_ref['PP'] / pp_rec_norm) - 1.0) * 0.40
k_psoe = 1.0 + ((partidos_ref['PSOE'] / psoe_rec_norm) - 1.0) * 0.40

print(f"VD: PP={vd['PP']}, PSOE={vd['PSOE']}")
print(f"K: PP={k_pp}, PSOE={k_psoe}")

# Probar rangos
print("\nProbando combinaciones (PP > PSOE?):")
found=False
for psoe_phi in [0.90, 0.88, 0.85, 0.82, 0.80]:
    for pp_phi in [0.92, 0.94, 0.96, 0.98, 1.00]:
        base_pp = vd['PP'] * k_pp * pp_phi
        base_psoe = vd['PSOE'] * k_psoe * psoe_phi
        
        diff = base_pp - base_psoe
        if diff > -1.0: # Show close ones too
            mark = "✅ GANADOR" if diff > 0 else "Casi..."
            print(f"PP={pp_phi}, PSOE={psoe_phi} -> PP={base_pp:.1f}, PSOE={base_psoe:.1f} (Diff: {diff:.1f}) {mark}")
            if diff > 0 and not found:
                found = True
        
print("OK")
