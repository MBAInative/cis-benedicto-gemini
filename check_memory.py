import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print(f"Python executable: {sys.executable}")
print(f"CWD: {os.getcwd()}")
print(f"Path to cis_estudios: {os.path.abspath('cis_estudios.py')}")

try:
    from cis_estudios import EstudioCIS
    print("Modulo importado correctamente")
    
    # Crear una instancia dummy (hacky pero rapida, no necesitamos leer excel)
    # Solo necesitamos llamar a get_context_biases que es estatico conceptualmente
    class Dummy(EstudioCIS):
        def __init__(self): pass
        
    d = Dummy()
    biases = d.get_context_biases()
    
    pp = biases['fidelidad'].get('PP')
    psoe = biases['fidelidad'].get('PSOE')
    
    print(f"\nVALORES EN MEMORIA:")
    print(f"PP: {pp}")
    print(f"PSOE: {psoe}")
    
    if pp == 0.98 and psoe == 0.80:
        print("\n[OK] Los valores en memoria coinciden con la edicion.")
    else:
        print("\n[ERROR] Los valores NO coinciden. Algo esta sobrescribiendo o cargando una version vieja.")

except Exception as e:
    print(f"Error: {e}")
