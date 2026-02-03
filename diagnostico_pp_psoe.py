# -*- coding: utf-8 -*-
"""
Diagnóstico comparativo PP vs PSOE en estudios Generales vs Autonómicas.
Objetivo: Identificar por qué el PP sale bajo en generales pero correcto en autonómicas.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cis_estudios import crear_estudio

ESTUDIOS_GENERALES = [
    "data/cis_studies/3524_multi_A.xlsx",  # Avance Generales
    "data/cis_studies/3528_multi_A.xlsx",  # Avance Generales
    "data/cis_studies/3530_multi_A.xlsx",  # Avance Generales
    "data/cis_studies/3536-multi.xlsx",    # Barómetro Nacional
]

ESTUDIOS_AUTONOMICOS = [
    "data/cis_studies/3543-multi_A.xlsx",  # Autonómicas Aragón
    "data/cis_studies/3538-multi_A.xlsx",  # Autonómicas Extremadura
]

def analizar_estudio(path, nombre):
    if not os.path.exists(path):
        return None
    
    estudio = crear_estudio(path)
    tipo = type(estudio).__name__
    
    vd = estudio.extraer_voto_directo()
    rec = estudio.extraer_recuerdo_voto()
    aldabon = estudio.calcular_aldabon_gemini()
    config = estudio.get_context_biases()
    partidos_ref = estudio.get_partidos_referencia()
    
    # Calcular factor K para PP y PSOE
    sum_rec = sum(rec.values()) if rec else 1
    
    pp_vd = vd.get('PP', 0)
    psoe_vd = vd.get('PSOE', 0)
    
    pp_rec_norm = (rec.get('PP', 0) / sum_rec) * 100 if sum_rec > 0 else 0
    psoe_rec_norm = (rec.get('PSOE', 0) / sum_rec) * 100 if sum_rec > 0 else 0
    
    pp_ref = partidos_ref.get('PP', 33.1)
    psoe_ref = partidos_ref.get('PSOE', 31.7)
    
    pp_k = (pp_ref / pp_rec_norm) if pp_rec_norm > 0 else 1.0  # K sin amortiguacion
    psoe_k = (psoe_ref / psoe_rec_norm) if psoe_rec_norm > 0 else 1.0
    
    pp_phi = config['fidelidad'].get('PP', 1.0)
    psoe_phi = config['fidelidad'].get('PSOE', 1.0)
    
    pp_lam = config['momentum'].get('PP', 1.0)
    psoe_lam = config['momentum'].get('PSOE', 1.0)
    
    # Cálculo paso a paso (pre-normalización)
    pp_base = pp_vd * pp_k * pp_phi
    psoe_base = psoe_vd * psoe_k * psoe_phi
    
    pp_final_raw = max(pp_vd, pp_base) + (max(pp_vd, pp_base) * (pp_lam - 1.0))
    psoe_final_raw = max(psoe_vd, psoe_base) + (max(psoe_vd, psoe_base) * (psoe_lam - 1.0))
    
    return {
        'nombre': nombre,
        'tipo': tipo,
        'pp_vd': round(pp_vd, 1),
        'psoe_vd': round(psoe_vd, 1),
        'ratio_vd_psoe_pp': round(psoe_vd / pp_vd, 2) if pp_vd > 0 else 0,
        'pp_rec_norm': round(pp_rec_norm, 1),
        'psoe_rec_norm': round(psoe_rec_norm, 1),
        'pp_ref': pp_ref,
        'psoe_ref': psoe_ref,
        'pp_k': round(pp_k, 3),
        'psoe_k': round(psoe_k, 3),
        'pp_phi': pp_phi,
        'psoe_phi': psoe_phi,
        'pp_lam': pp_lam,
        'psoe_lam': psoe_lam,
        'pp_base': round(pp_base, 1),
        'psoe_base': round(psoe_base, 1),
        'pp_final_raw': round(pp_final_raw, 1),
        'psoe_final_raw': round(psoe_final_raw, 1),
        'pp_aldabon': aldabon.get('PP', 0),
        'psoe_aldabon': aldabon.get('PSOE', 0),
        'diferencia_aldabon': round(aldabon.get('PP', 0) - aldabon.get('PSOE', 0), 1),
    }

print("=" * 100)
print("DIAGNOSTICO: Comparacion PP vs PSOE en estudios CIS")
print("=" * 100)

print("\n" + "=" * 100)
print("ESTUDIOS DE ELECCIONES GENERALES")
print("=" * 100)

for path in ESTUDIOS_GENERALES:
    nombre = os.path.basename(path)
    result = analizar_estudio(path, nombre)
    if result:
        print(f"\n--- {result['nombre']} ({result['tipo']}) ---")
        print(f"  Voto Directo:     PP={result['pp_vd']}%  PSOE={result['psoe_vd']}%  (PSOE/PP ratio: {result['ratio_vd_psoe_pp']})")
        print(f"  Recuerdo Norm:    PP={result['pp_rec_norm']}%  PSOE={result['psoe_rec_norm']}%")
        print(f"  Referencia 2023:  PP={result['pp_ref']}%  PSOE={result['psoe_ref']}%")
        print(f"  Factor K:         PP={result['pp_k']}  PSOE={result['psoe_k']}")
        print(f"  Fidelidad (Phi):  PP={result['pp_phi']}  PSOE={result['psoe_phi']}")
        print(f"  Momentum (Lam):   PP={result['pp_lam']}  PSOE={result['psoe_lam']}")
        print(f"  Base (VD*K*Phi):  PP={result['pp_base']}  PSOE={result['psoe_base']}")
        print(f"  Final Raw:        PP={result['pp_final_raw']}  PSOE={result['psoe_final_raw']}")
        print(f"  ALDABON OUTPUT:   PP={result['pp_aldabon']}%  PSOE={result['psoe_aldabon']}%  (Dif: {result['diferencia_aldabon']})")

print("\n" + "=" * 100)
print("ESTUDIOS DE ELECCIONES AUTONOMICAS")
print("=" * 100)

for path in ESTUDIOS_AUTONOMICOS:
    nombre = os.path.basename(path)
    result = analizar_estudio(path, nombre)
    if result:
        print(f"\n--- {result['nombre']} ({result['tipo']}) ---")
        print(f"  Voto Directo:     PP={result['pp_vd']}%  PSOE={result['psoe_vd']}%  (PSOE/PP ratio: {result['ratio_vd_psoe_pp']})")
        print(f"  Recuerdo Norm:    PP={result['pp_rec_norm']}%  PSOE={result['psoe_rec_norm']}%")
        print(f"  Referencia:       PP={result['pp_ref']}%  PSOE={result['psoe_ref']}%")
        print(f"  Factor K:         PP={result['pp_k']}  PSOE={result['psoe_k']}")
        print(f"  Fidelidad (Phi):  PP={result['pp_phi']}  PSOE={result['psoe_phi']}")
        print(f"  Momentum (Lam):   PP={result['pp_lam']}  PSOE={result['psoe_lam']}")
        print(f"  Base (VD*K*Phi):  PP={result['pp_base']}  PSOE={result['psoe_base']}")
        print(f"  Final Raw:        PP={result['pp_final_raw']}  PSOE={result['psoe_final_raw']}")
        print(f"  ALDABON OUTPUT:   PP={result['pp_aldabon']}%  PSOE={result['psoe_aldabon']}%  (Dif: {result['diferencia_aldabon']})")

print("\n" + "=" * 100)
print("ANÁLISIS")
print("=" * 100)
print("""
PROBLEMA DETECTADO:
- En los estudios del CIS para Generales, el Voto Directo del PSOE es sistemáticamente 
  más alto que el del PP (ratio ~1.4-2.0x), lo cual no se corresponde con otros sondeos.
- La fidelidad actual (PP=0.98, PSOE=0.80) no compensa este sesgo de entrada.
- El factor K sí intenta corregir, pero está amortiguado al 40%.

POSIBLES SOLUCIONES:
1. Aumentar la amortiguación del K para el PSOE (ej: 60% en lugar de 40%)
2. Reducir más la fidelidad del PSOE (ej: 0.70 en lugar de 0.80)
3. Aplicar un factor de corrección adicional por sesgo de deseabilidad social
""")
