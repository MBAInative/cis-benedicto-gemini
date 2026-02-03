import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cis_estudios import crear_estudio

path = "data/cis_studies/3536-multi.xlsx" # Barometro 3536

if not os.path.exists(path):
    print(f"No existe: {path}")
    sys.exit(1)

estudio = crear_estudio(path)
biases = estudio.get_context_biases()

pp = biases['fidelidad'].get('PP')
psoe = biases['fidelidad'].get('PSOE')

print(f"\nVALORES EN MEMORIA (Usando crear_estudio sobre 3536):")
print(f"Tipo: {type(estudio).__name__}")
print(f"PP: {pp}")
print(f"PSOE: {psoe}")

if pp == 0.98 and psoe == 0.80:
    print("\n[OK] Los valores coinciden.")
else:
    print("\n[ERROR] Los valores NO coinciden.")
