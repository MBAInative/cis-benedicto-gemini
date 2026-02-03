# -*- coding: utf-8 -*-
"""
Script de verificación post-cambios
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cis_estudios import crear_estudio

# Estudio nacional para probar
path = "data/cis_studies/3540_multi.xlsx"
if not os.path.exists(path):
    # Fallback to another study if 3540 is not available
    path = "data/cis_studies/3536-multi.xlsx"

print(f"=== Verificando cambios en {os.path.basename(path)} ===")
estudio = crear_estudio(path)

rec = estudio.extraer_recuerdo_voto()
result = estudio.calcular_aldabon_gemini()
config = estudio.get_context_biases()

print(f"Fidelidad Actual: PP={config['fidelidad']['PP']}, PSOE={config['fidelidad']['PSOE']}")
print(f"Momentum Actual: PP={config['momentum']['PP']}, PSOE={config['momentum']['PSOE']}")

pp_val = result.get('PP', 0)
psoe_val = result.get('PSOE', 0)

print(f"\nResultado Aldabón-Gemini:")
print(f"  PP:   {pp_val:.1f}%")
print(f"  PSOE: {psoe_val:.1f}%")

if pp_val > psoe_val:
    print("\n✅ ÉXITO: El PP supera al PSOE como se esperaba.")
else:
    print(f"\n❌ AVISO: El PSOE sigue por encima (Dif: {psoe_val - pp_val:.1f}%)")
