"""
Prueba manual de ConexionBaseDatos.
Ejecutar con: python tests/test_connection.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import ConexionBaseDatos


def test_conexion():
    print("Probando ConexionBaseDatos...")

    db = ConexionBaseDatos()

    try:
        conexion = db.conectar()

        if conexion is not None:
            print("✅ Conexión establecida correctamente.")
            print("Tipo de objeto:", type(conexion))
        else:
            print("❌ conectar() devolvió None. Revisa DATABASE_PATH o el error en el log.")

        # Probar que reutiliza la misma conexión si ya existe
        segunda_conexion = db.conectar()
        if segunda_conexion is conexion:
            print("✅ Reutiliza la conexión existente en vez de abrir otra.")
        else:
            print("⚠️ Se abrió una conexión distinta en la segunda llamada.")

        db.cerrar()
        print("✅ Conexión cerrada sin errores.")

        if db.conexion is None:
            print("✅ self.conexion quedó en None tras cerrar.")
        else:
            print("❌ self.conexion no se reseteó tras cerrar.")

    except Exception as error:
        print(f"\n❌ Ocurrió un error durante la prueba: {error}")
        raise


if __name__ == "__main__":
    test_conexion()