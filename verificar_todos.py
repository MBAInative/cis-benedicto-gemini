from cis_estudios import crear_estudio
files = ['3524_multi_A.xlsx', '3528_multi_A.xlsx', '3530_multi_A.xlsx', 
         '3536-multi.xlsx', '3538_multi.xlsx', '3540_multi.xlsx', '3543-multi_A.xlsx']

for f in files:
    print(f"\n{'='*60}")
    print(f"ARCHIVO: {f}")
    print(f"{'='*60}")
    try:
        e = crear_estudio('data/cis_studies/'+f)
        print(f"Tipo: {type(e).__name__}")
        print(f"Hoja Estimación: {e._encontrar_hoja_estimacion()}")
        
        vd = e.extraer_voto_directo()
        cis = e.extraer_estimacion_cis()
        
        print(f"Voto Directo: {len(vd)} partidos, suma={round(sum(vd.values()),1)}%")
        print(f"Estimación CIS: {len(cis)} partidos, suma={round(sum(cis.values()),1)}%")
        
        if vd:
            print("Top 5 partidos VD:")
            for p, v in sorted(vd.items(), key=lambda x:-x[1])[:5]:
                print(f"  {p}: {v}%")
    except Exception as ex:
        print(f"ERROR: {ex}")
