import pandas as pd
import os
from cis_analyzer import analyze_cis_professional

def forensic_dump(f, t, out):
    out.write(f"\n{'='*60}\nFORENSIC DUMP: {f} ({t})\n{'='*60}\n")
    if not os.path.exists(f):
        out.write("FILE NOT FOUND\n")
        return
        
    try:
        xl = pd.ExcelFile(f)
        s_est = next((s for s in xl.sheet_names if "ESTIMACI" in s.upper()), None)
        if s_est:
            out.write(f"--- HEAD OF ESTIMACION ({s_est}) ---\n")
            out.write(pd.read_excel(xl, sheet_name=s_est).iloc[:20, :10].to_string() + "\n")
            
        res = analyze_cis_professional(f, study_type=t)
        if res:
            out.write("\n--- RESULTS SUMMARY ---\n")
            out.write(f"OFFICIAL: {res['official']}\n")
            out.write(f"ALDABON: {res['benedicto']}\n")
            out.write(f"RAW (IDV): {res['raw']}\n")
            out.write(f"METADATA: {res['meta']}\n")
    except Exception as e:
        out.write(f"CRASH: {e}\n")

if __name__ == "__main__":
    studies = [
        ('3540_multi.xlsx', 'BAROMETRO'),
        ('3536_multi.xlsx', 'AVANCE'),
        ('3536-multi.xlsx', 'AVANCE'),
        ('3543_multi_A.xlsx', 'AVANCE'),
        ('3543-multi_A.xlsx', 'AVANCE'),
    ]
    with open('forensic_audit_final.txt', 'w', encoding='utf-8') as out:
        for f_name, t in studies:
            f_path = os.path.join('data/cis_studies', f_name)
            forensic_dump(f_path, t, out)
    print("Audit written to forensic_audit_final.txt")
