import importlib
import cis_estudios
importlib.reload(cis_estudios)

# Parchear temporalmente para debug
orig_normalizar = cis_estudios.EstudioCIS._normalizar_partido

def debug_normalizar(self, nombre):
    result = orig_normalizar(self, nombre)
    if 'IU' in str(nombre).upper() or 'SUMAR' in str(nombre).upper():
        print(f'DEBUG: _normalizar_partido("{nombre}") -> "{result}"')
    return result

cis_estudios.EstudioCIS._normalizar_partido = debug_normalizar

e = cis_estudios.crear_estudio('data/cis_studies/3543-multi_A.xlsx')
vd = e.extraer_voto_directo()
print('\n=== Resultado Final ===')
print('SUMAR:', vd.get('SUMAR', 'NO ENCONTRADO'))
