"""
Prueba manual de EsquemaBaseDatos.
Ejecutar con: python tests/test_schema.py
"""

import sys
import os
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.schema import EsquemaBaseDatos
from config import DATABASE_PATH


def test_crear_tablas():
    print("Probando EsquemaBaseDatos.crearTablas()...")

    try:
        esquema = EsquemaBaseDatos()
        esquema.crearTablas()

        print("\n✅ crearTablas() ejecutado sin errores.\n")

        if os.path.exists(DATABASE_PATH):
            print(f"✅ El archivo de base de datos existe en: {DATABASE_PATH}")
        else:
            print("❌ No se encontró el archivo .db en la ruta esperada.")
            return

        # Verificamos que las tablas realmente quedaron creadas
        conexion_verificacion = sqlite3.connect(DATABASE_PATH)
        cursor = conexion_verificacion.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = [fila[0] for fila in cursor.fetchall()]

        print("Tablas encontradas:", tablas)

        for tabla_esperada in ["MAESTRO_REPUESTOS", "MOVIMIENTOS_INVENTARIO"]:
            if tabla_esperada in tablas:
                print(f"✅ Tabla '{tabla_esperada}' creada correctamente.")
            else:
                print(f"❌ Falta la tabla '{tabla_esperada}'.")

        conexion_verificacion.close()

    except Exception as error:
        print(f"\n❌ Ocurrió un error durante la prueba: {error}")
        raise


if __name__ == "__main__":
    test_crear_tablas()