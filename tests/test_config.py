# import sys
# import os

# ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(ruta_raiz)

# print("Raíz calculada:", ruta_raiz)
# print("Contenido de la raíz:", os.listdir(ruta_raiz))

# from config import (
#     BASE_DIR,
#     RUTA_ARCHIVO_EXCEL
# )

# print(f"BASE_DIR           : {BASE_DIR}")
# print(f"RUTA_ARCHIVO_EXCEL : {RUTA_ARCHIVO_EXCEL}")
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    BASE_DIR,
    RUTA_ARCHIVO_EXCEL
)

print(f"BASE_DIR           : {BASE_DIR}")
print(f"RUTA_ARCHIVO_EXCEL : {RUTA_ARCHIVO_EXCEL}")

if os.path.exists(RUTA_ARCHIVO_EXCEL):
    print("✅ El archivo existe en esa ruta exacta.")
else:
    print("❌ El archivo NO existe en esa ruta. Revisa el nombre exacto.")
    print("\nArchivos .xlsx encontrados en BASE_DIR:")
    for archivo in os.listdir(BASE_DIR):
        if archivo.lower().endswith(".xlsx"):
            print(f"  -> '{archivo}'")