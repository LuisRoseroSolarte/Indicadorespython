import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.etl_model import ETLModel

def main():
    print("Probando ETLModel...")

    etl = ETLModel()

    try:
        data_maestro, data_movimiento_repuestos = etl.tratamiento_datos()

        print("\n✅ ETL ejecutado sin errores.\n")

        print("--- MAESTRO DE REPUESTOS ---")
        print(data_maestro.shape)
        print(data_maestro.head())

        print("\n--- MOVIMIENTOS DE REPUESTOS ---")
        print(data_movimiento_repuestos.shape)
        print(data_movimiento_repuestos.head())

        resumen = etl.obtener_resumen(data_maestro, data_movimiento_repuestos)
        print("\n--- RESUMEN ---")
        print(resumen)

    except Exception as error:
        print(f"\n❌ Ocurrió un error durante la prueba: {error}")
        raise  # relanza para ver el traceback completo en consola


if __name__ == "__main__":
    main()
    