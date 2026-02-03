"""
Script de diagnóstico profundo de la estructura de archivos CIS.
Analiza CADA archivo Excel para entender las diferencias.
"""
import pandas as pd
import os

DATA_DIR = "data/cis_studies"
files = [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx') and not f.startswith('~$')]

print("=" * 80)
print("ANÁLISIS PROFUNDO DE ESTRUCTURA DE ARCHIVOS CIS")
print("=" * 80)

for filename in sorted(files):
    filepath = os.path.join(DATA_DIR, filename)
    print(f"\n{'='*80}")
    print(f"ARCHIVO: {filename}")
    print(f"{'='*80}")
    
    try:
        xl = pd.ExcelFile(filepath)
        print(f"Hojas disponibles: {xl.sheet_names}")
        
        # Buscar hoja de Estimación
        hoja_estim = None
        for sheet in xl.sheet_names:
            if 'estimaci' in sheet.lower() or 'estimación' in sheet.lower():
                hoja_estim = sheet
                break
        
        print(f"Hoja de Estimación encontrada: {hoja_estim}")
        
        if hoja_estim:
            df = pd.read_excel(xl, sheet_name=hoja_estim, header=None)
            print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
            
            # Mostrar primeras filas con datos en columna 0
            print("\nPrimeras filas con datos:")
            for i in range(min(25, len(df))):
                if pd.notna(df.iloc[i, 0]) and str(df.iloc[i, 0]).strip():
                    col0 = str(df.iloc[i, 0])[:25]
                    col1 = str(df.iloc[i, 1])[:12] if len(df.columns) > 1 and pd.notna(df.iloc[i, 1]) else "N/A"
                    col3 = str(df.iloc[i, 3])[:12] if len(df.columns) > 3 and pd.notna(df.iloc[i, 3]) else "N/A"
                    print(f"  Fila {i}: col0='{col0}' | col1='{col1}' | col3='{col3}'")
        else:
            print("NO HAY HOJA DE ESTIMACIÓN - Este archivo requiere PDF externo")
            
    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("FIN DEL ANÁLISIS")
print("=" * 80)
