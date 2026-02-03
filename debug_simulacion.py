# -*- coding: utf-8 -*-
"""
Simulacion: Como afectan diferentes parametros de fidelidad al resultado final
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cis_estudios import crear_estudio

# Estudio nacional para probar
path = "data/cis_studies/3540_multi.xlsx"
estudio = crear_estudio(path)

vd = estudio.extraer_voto_directo()
rec = estudio.extraer_recuerdo_voto()

with open("debug_simulacion.txt", "w", encoding="utf-8") as f:
    f.write("=== Estudio 3540 (Nacional) ===\n")
    f.write(f"Voto Directo: PP={vd.get('PP'):.1f}%, PSOE={vd.get('PSOE'):.1f}%\n")
    f.write(f"Recuerdo: PP={rec.get('PP'):.1f}%, PSOE={rec.get('PSOE'):.1f}%\n")

    # Config actual
    config = estudio.get_context_biases()
    f.write(f"\nConfig ACTUAL:\n")
    f.write(f"  Fidelidad: PP={config['fidelidad']['PP']}, PSOE={config['fidelidad']['PSOE']}\n")
    f.write(f"  Momentum: PP={config['momentum']['PP']}, PSOE={config['momentum']['PSOE']}\n")

    result1 = estudio.calcular_aldabon_gemini()
    f.write(f"\nResultado ACTUAL: PP={result1.get('PP'):.1f}%, PSOE={result1.get('PSOE'):.1f}%\n")

    # Calcular manualmente con nuevos parametros
    partidos_ref = estudio.get_partidos_referencia()
    sum_rec = sum(rec.values())

    # K factors
    pp_rec_norm = (rec.get('PP', 0) / sum_rec) * 100
    psoe_rec_norm = (rec.get('PSOE', 0) / sum_rec) * 100

    k_pp = 1.0 + ((partidos_ref['PP'] / pp_rec_norm) - 1.0) * 0.40
    k_psoe = 1.0 + ((partidos_ref['PSOE'] / psoe_rec_norm) - 1.0) * 0.40

    f.write(f"\nFactores K:\n")
    f.write(f"  K_pp = {k_pp:.3f} (Ref={partidos_ref['PP']}%, Rec_norm={pp_rec_norm:.1f}%)\n")
    f.write(f"  K_psoe = {k_psoe:.3f} (Ref={partidos_ref['PSOE']}%, Rec_norm={psoe_rec_norm:.1f}%)\n")

    f.write(f"\n=== PROBLEMA IDENTIFICADO ===\n")
    f.write(f"El K del PP ({k_pp:.3f}) es MAYOR que el del PSOE ({k_psoe:.3f})\n")
    f.write(f"Esto es correcto: el PP tiene 'voto oculto'\n")
    f.write(f"\nPERO la fidelidad actual:\n")
    f.write(f"  PP=0.92, PSOE=0.93\n")
    f.write(f"neutraliza casi todo el efecto K, dejando al PSOE por encima.\n")
    
    f.write(f"\n=== COMPARACION DE ESCENARIOS ===\n")
    
    # Escenario 1: Actual
    base_pp_1 = vd['PP'] * k_pp * 0.92
    base_psoe_1 = vd['PSOE'] * k_psoe * 0.93
    f.write(f"ACTUAL (PP=0.92, PSOE=0.93): PP={base_pp_1:.1f}%, PSOE={base_psoe_1:.1f}% --> PSOE gana\n")
    
    # Escenario 2: Invertir ligeramente
    base_pp_2 = vd['PP'] * k_pp * 0.94
    base_psoe_2 = vd['PSOE'] * k_psoe * 0.90
    f.write(f"PROPUESTA (PP=0.94, PSOE=0.90): PP={base_pp_2:.1f}%, PSOE={base_psoe_2:.1f}% --> PP gana\n")
    
    # Escenario 3: Como Aragon
    base_pp_3 = vd['PP'] * k_pp * 0.78
    base_psoe_3 = vd['PSOE'] * k_psoe * 0.59
    f.write(f"ARAGON (PP=0.78, PSOE=0.59): PP={base_pp_3:.1f}%, PSOE={base_psoe_3:.1f}% --> PP gana mucho\n")

print("OK - ver debug_simulacion.txt")
