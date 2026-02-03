from cis_estudios import crear_estudio
import pandas as pd

def debug_3538():
    print("\n--- DEBUG 3538 ---")
    f = 'data/cis_studies/3538_multi.xlsx'
    e = crear_estudio(f)
    print(f"Tipo: {type(e).__name__}")
    hoja = e._encontrar_hoja_estimacion()
    print(f"Hoja: {hoja}")
    
    if hoja:
        df = pd.read_excel(f, sheet_name=hoja, header=None)
        print("Muestra (filas 7-30):")
        print(df.iloc[7:30, [0, 1, 3]])
        
    vd = e.extraer_voto_directo()
    ec = e.extraer_estimacion_cis()
    print(f"VD Extracted: {vd}")
    print(f"CIS Extracted: {ec}")

def debug_3536():
    print("\n--- DEBUG 3536 ---")
    f = 'data/cis_studies/3536-multi.xlsx'
    e = crear_estudio(f)
    print(f"Tipo: {type(e).__name__}")
    
    vd = e.extraer_voto_directo()
    rv = e.extraer_recuerdo_voto()
    print(f"VD: {vd}")
    print(f"RV: {rv}")
    
    ag = e.calcular_aldabon_gemini()
    print(f"AG: {ag}")

if __name__ == "__main__":
    debug_3538()
    debug_3536()
