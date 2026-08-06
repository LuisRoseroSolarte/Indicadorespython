"""
Prueba para inspeccionar el resultado del KPI 9
(pronóstico de agotamiento del inventario).
Ejecutar con: python tests/test_kpi9_pronostico_agotamiento.py
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from controllers.app_controller import AppController


def test_kpi9():
    print("Cargando Data Warehouse...")

    # =====================================================
    # 1. CARGA DE DATA WAREHOUSE
    # =====================================================
    print("PASO 1: Cargando Data Warehouse...")
    app = AppController()
    app.cargar_datawarehouse()
    print("✅ Data Warehouse cargado.\n")

    # =====================================================
    # 2. CARGA DE EXCEL
    # =====================================================
    print("PASO 2: Cargando Excel...")
    app.cargar_excel()
    print("✅ Excel cargado.\n")

    # =====================================================
    # 3. ACTUALIZACIÓN DEL DATA WAREHOUSE
    # =====================================================
    print("PASO 3: Actualizando Data Warehouse...")
    app.actualizar_datawarehouse()
    print("✅ Data Warehouse actualizado.\n")

    # =====================================================
    # 4. CARGA DE DATAFRAMES
    # =====================================================
    print("PASO 4: Cargando DataFrames...")
    app.cargar_datawarehouse()
    print(f"✅ DIM_PRODUCTO: {len(app.dim_producto)} filas")
    print(f"✅ FACT_MOVIMIENTOS: {len(app.fact_movimientos)} filas\n")

    # =====================================================
    # 5. CÁLCULO DE KPIs
    # =====================================================
    print("PASO 5: Calculando KPIs...")
    app.calcular_kpis()
    print("✅ KPI 1 (Clasificación ABC):")
    print(app.kpi1_clasificacion_abc.head(), "\n")
    print("✅ KPI 4 (Top 10 menor cobertura):")
    print(app.kpi4_menor_cobertura, "\n")
    print("Calculando KPI 9...\n")
    resultado = app.analytics_model.calcular_pronostico_agotamiento()

    # =====================================================
    # 1. RESUMEN GENERAL
    # =====================================================
    print("=" * 60)
    print("RESUMEN KPI 9 - PRONÓSTICO DE AGOTAMIENTO DEL INVENTARIO")
    print("=" * 60)
    print(f"Cantidad de productos críticos (<= 30 días) : {resultado['cantidad_criticos']}")

    # Mostrar todas las filas y columnas sin truncar
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    # =====================================================
    # 2. DETALLE COMPLETO (como tabla)
    # =====================================================
    print("\n" + "=" * 60)
    print(f"DETALLE COMPLETO ({len(resultado['detalle'])} repuestos)")
    print("=" * 60)
    print(resultado["detalle"])

    # =====================================================
    # 3. CONTEO POR ESTADO
    # =====================================================
    print("\n" + "=" * 60)
    print("CONTEO POR ESTADO")
    print("=" * 60)
    print(resultado["detalle"]["estado"].value_counts())

    # =====================================================
    # 4. LOS 10 CASOS MÁS CRÍTICOS (menor días de agotamiento)
    # =====================================================
    print("\n" + "=" * 60)
    print("TOP 10 - MENOR TIEMPO DE AGOTAMIENTO (MÁS CRÍTICOS)")
    print("=" * 60)
    print(resultado["detalle"].head(10))


if __name__ == "__main__":
    test_kpi9()