from cis_estudios import crear_estudio
import pandas as pd

studies = {
    '3543 (Aragón)': 'data/cis_studies/3543-multi_A.xlsx',
    '3538 (Extremadura)': 'data/cis_studies/3538_multi.xlsx',
    '3536 (Nacional)': 'data/cis_studies/3536-multi.xlsx'
}

print("ALDABÓN-GEMINI 2.5: CALIBRATION VERIFICATION")
print("="*40)

for name, path in studies.items():
    print(f"\nESTUDIO: {name}")
    try:
        e = crear_estudio(path)
        metrics = e._infer_context()
        biases = e.get_context_biases()
        estim = e.calcular_aldabon_gemini()
        
        print(f"  Diagnóstico: {biases['justificacion']['Diagnóstico Sociológico']}")
        print(f"  Sesgo: {biases['justificacion']['Sesgo de Muestra']}")
        
        print(f"  --- Fidelidades ---")
        fids = biases['fidelidad']
        print(f"  PSOE: {fids.get('PSOE', 'N/A')} | PP: {fids.get('PP', 'N/A')} | VOX: {fids.get('VOX', 'N/A')}")
        
        print(f"  --- Estimación Final ---")
        print(f"  PSOE: {estim.get('PSOE', 0)}% (Objetivo Real: ~26%)")
        print(f"  PP: {estim.get('PP', 0)}% (Objetivo Real: ~39-43%)")
        print(f"  VOX: {estim.get('VOX', 0)}% (Objetivo Real: ~11-16%)")
        
    except Exception as ex:
        print(f"  Error: {ex}")

print("\n" + "="*40)
