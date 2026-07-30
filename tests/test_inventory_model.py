"""
Prueba de integración: ETL -> InventarioModel
Lee el Excel, transforma los datos y los inserta en la base de datos real.
Ejecutar con: python tests/test_integracion_etl_inventario.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.etl_model import ETLModel
from models.inventory_model import InventarioModel
from config import STOCK_MINIMO_DEFAULT, CATEGORIA_DEFAULT


def test_integracion():
    print("Ejecutando ETL...")

    etl = ETLModel()
    data_maestro, data_movimiento_repuestos = etl.tratamiento_datos()

    print(f"✅ ETL completado. Maestro: {len(data_maestro)} filas | Movimientos: {len(data_movimiento_repuestos)} filas")

    # =====================================================
    # PREPARAR DATOS PARA MAESTRO_REPUESTOS
    # =====================================================
    datos_maestro = [
        (
            fila["ELEM"],
            fila["NOMBRE_ELEMENTO"],
            fila["UNIDAD"],
            STOCK_MINIMO_DEFAULT,
            CATEGORIA_DEFAULT
        )
        for _, fila in data_maestro.iterrows()
    ]

    # =====================================================
    # PREPARAR DATOS PARA MOVIMIENTOS_INVENTARIO
    # =====================================================
    datos_movimientos = [
        tuple(fila) for _, fila in data_movimiento_repuestos.iterrows()
    ]

    # =====================================================
    # INSERTAR EN LA BASE DE DATOS
    # =====================================================
    print("\nInsertando en la base de datos...")

    inventario = InventarioModel()

    try:
        filas_maestro = inventario.insertar_maestro_repuestos(datos_maestro)
        print(f"✅ Maestro insertado. Filas nuevas: {filas_maestro}")

        filas_movimientos = inventario.insertar_movimientos(datos_movimientos)
        print(f"✅ Movimientos insertados. Filas nuevas: {filas_movimientos}")

        maestro_actual = inventario.obtener_maestro_repuestos()
        movimientos_actual = inventario.obtener_movimientos()

        print(f"\nTotal en MAESTRO_REPUESTOS: {len(maestro_actual)}")
        print(f"Total en MOVIMIENTOS_INVENTARIO: {len(movimientos_actual)}")

        print("\n✅ Integración ETL -> InventarioModel completada sin errores.")

    except Exception as error:
        print(f"\n❌ Error al insertar en la base de datos: {error}")
        raise


if __name__ == "__main__":
    test_integracion()