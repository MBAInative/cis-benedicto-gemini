from cis_estudios import crear_estudio
import pandas as pd

try:
    path = 'data/cis_studies/3538_multi.xlsx'
    e = crear_estudio(path)
    vd = e.extraer_voto_directo()
    es = e.extraer_estimacion_cis()
    print(f"ESTUDIO: 3538")
    print(f"Voto Directo PSOE: {vd.get('PSOE')}")
    print(f"Voto Directo PP: {vd.get('PP')}")
    print(f"Estimacion CIS (total keys): {len(es)}")
    for p, v in es.items():
        print(f"CIS {p}: {v}")
except Exception as ex:
    print(f"Error: {ex}")
