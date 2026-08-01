import sys
import os

# Ajustar el path para importar correctamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import ConexionBaseDatos
from models.datawarehouse_model import DataWarehouseModel  # Ajusta la ruta según tu proyecto


def test_datawarehouse_model():
    print("Probando DataWarehouseModel...")

    try:
        # Crear instancia
        dw = DataWarehouseModel()
        print("✅ Instancia creada correctamente.")

        # Probar actualización del Data Warehouse
        try:
            dw.actualizar_datawarehouse()
            print("✅ Data Warehouse actualizado correctamente.")
        except Exception as error:
            print(f"❌ Error al actualizar el Data Warehouse: {error}")
            raise

        # Probar cierre de conexión
        dw.cerrar()
        print("✅ Conexión cerrada sin errores.")

        if dw.bd.conexion is None:
            print("✅ self.conexion quedó en None tras cerrar.")
        else:
            print("❌ self.conexion no se reseteó tras cerrar.")

    except Exception as error:
        print(f"\n❌ Ocurrió un error durante la prueba: {error}")
        raise


if __name__ == "__main__":
    test_datawarehouse_model()
