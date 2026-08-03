import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.app_controller import AppController


def test_flujo_paso_a_paso():
    app = AppController()

    print("PASO 1: cargando Excel...")
    app.cargar_excel()
    print("✅ Listo.\n")

    print("PASO 2: actualizando Data Warehouse...")
    app.actualizar_datawarehouse()
    print("✅ Listo.\n")

    print("PASO 3: cargando DataFrames...")
    app.cargar_datawarehouse()
    print(f"✅ DIM_PRODUCTO: {len(app.dim_producto)} filas")
    print(f"✅ FACT_MOVIMIENTOS: {len(app.fact_movimientos)} filas\n")

    print("PASO 4: calculando KPIs...")
    app.calcular_kpis()
    print("✅ KPI 1 (muestra):")
    print(app.kpi1_clasificacion_abc.head())
    print("\n✅ KPI 4 (Top 10 menor cobertura):")
    print(app.kpi4_menor_cobertura)
    print()

    print("PASO 5: cerrando conexiones...")
    app.cerrar()
    print("✅ Listo.")


if __name__ == "__main__":
    test_flujo_paso_a_paso()