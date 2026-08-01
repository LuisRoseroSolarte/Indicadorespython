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
    # Verificar que no haya valores nulos ni vacíos en UNIDAD
           
                # Filtrar filas problemáticas
        data_maestro = data_maestro[data_maestro["UNIDAD"].isnull() | (data_maestro["UNIDAD"].str.strip() == "")]
                
        if data_maestro.empty:
            print("✅ La columna UNIDAD está limpia: no hay valores nulos ni vacíos.")
        else:
            print("❌ Se encontraron registros con UNIDAD vacía o nula:")
            print(data_maestro)
    
            # Uso después de la limpieza
        

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
    