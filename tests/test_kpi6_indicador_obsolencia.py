# """
# Prueba para inspeccionar el resultado del KPI 6 (obsolescencia).
# Ejecutar con: python tests/test_kpi6_obsolescencia.py
# """

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from controllers.app_controller import AppController


# def test_kpi6():
#     print("Cargando Data Warehouse...")

#     app = AppController()
#     app.cargar_datawarehouse()  # asume que la BD y el DW ya existen y están actualizados
    
#     print("PASO 1: cargando Excel...")
#     app.cargar_excel()
#     print("✅ Listo.\n")
    
#     print("PASO 2: actualizando Data Warehouse...")
#     app.actualizar_datawarehouse()
#     print("✅ Listo.\n")
    
#     print("PASO 3: cargando DataFrames...")
#     app.cargar_datawarehouse()
#     print(f"✅ DIM_PRODUCTO: {len(app.dim_producto)} filas")
#     print(f"✅ FACT_MOVIMIENTOS: {len(app.fact_movimientos)} filas\n")
    
#     print("PASO 4: calculando KPIs...")
#     app.calcular_kpis()
#     print("✅ KPI 1 (muestra):")
#     print(app.kpi1_clasificacion_abc.head())
#     print("\n✅ KPI 4 (Top 10 menor cobertura):")
#     print(app.kpi4_menor_cobertura)
#     print()

#     print("Calculando KPI 6...\n")
#     resultado = app.analytics_model.calcular_indicador_obsolescencia()

#     # =====================================================
#     # 1. RESUMEN GENERAL
#     # =====================================================
#     print("=" * 60)
#     print("RESUMEN KPI 6 - OBSOLESCENCIA")
#     print("=" * 60)
#     print(f"Cantidad con alta probabilidad : {resultado['cantidad_alta_probabilidad']}")
#     print(f"Porcentaje del inventario      : {resultado['porcentaje']}%")

#     # =====================================================
#     # 2. DESGLOSE POR CATEGORÍA ABC (grafica)
#     # =====================================================
#     print("\n" + "=" * 60)
#     print("DESGLOSE ABC (solo productos con alta probabilidad)")
#     print("=" * 60)
#     grafica_df = pd.DataFrame(
#         list(resultado["grafica"].items()),
#         columns=["CATEGORIA", "CANTIDAD"]
#     )
#     print(grafica_df.to_string(index=False))

#     # =====================================================
#     # 3. DETALLE COMPLETO (como tabla)
#     # =====================================================
#     print("\n" + "=" * 60)
#     print(f"DETALLE COMPLETO ({len(resultado['detalle'])} repuestos)")
#     print("=" * 60)

#     # Mostrar todas las filas y columnas sin truncar
#     pd.set_option("display.max_rows", None)
#     pd.set_option("display.max_columns", None)
#     pd.set_option("display.width", None)

#     print(resultado["detalle"])

#     # =====================================================
#     # 4. CONTEO POR PROBABILIDAD (Baja/Media/Alta/Sin datos)
#     # =====================================================
#     print("\n" + "=" * 60)
#     print("CONTEO POR NIVEL DE PROBABILIDAD (todos los repuestos)")
#     print("=" * 60)
#     print(resultado["detalle"]["probabilidad_obsolescencia"].value_counts())


# if __name__ == "__main__":
#     test_kpi6()

"""
Prueba organizada para inspeccionar el resultado del KPI 6 (obsolescencia).
Ejecutar con: python tests/test_kpi6_obsolescencia.py
"""

# import sys
# import os
# import pandas as pd

# from controllers.app_controller import AppController

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_kpi6():
    print("\n" + "="*70)
    print("INICIO DE PRUEBA KPI 6 - OBSOLESCENCIA")
    print("="*70 + "\n")

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

    # =====================================================
    # 6. CÁLCULO DEL KPI 6 (OBSOLESCENCIA)
    # =====================================================
    print("PASO 6: Calculando KPI 6 (Obsolescencia)...\n")
    resultado = app.analytics_model.calcular_indicador_obsolescencia()

    # =====================================================
    # 6.1 RESUMEN GENERAL
    # =====================================================
    print("="*70)
    print("RESUMEN KPI 6 - OBSOLESCENCIA")
    print("="*70)
    print(f"Cantidad con alta probabilidad : {resultado['cantidad_alta_probabilidad']}")
    print(f"Porcentaje del inventario      : {resultado['porcentaje']}%\n")

    # =====================================================
    # 6.2 DESGLOSE POR CATEGORÍA ABC
    # =====================================================
    print("="*70)
    print("DESGLOSE ABC (solo productos con alta probabilidad)")
    print("="*70)
    grafica_df = pd.DataFrame(list(resultado["grafica"].items()), columns=["CATEGORIA", "CANTIDAD"])
    print(grafica_df.to_string(index=False), "\n")

    # =====================================================
    # 6.3 DETALLE COMPLETO (solo primeros 20)
    # =====================================================
    print("="*70)
    print(f"DETALLE COMPLETO (primeras 20 filas de {len(resultado['detalle'])} repuestos)")
    print("="*70)

    # Mostrar solo las primeras 20 filas
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    print(resultado["detalle"].head(20))
    # =====================================================
    # 6.4 CONTEO POR PROBABILIDAD
    # =====================================================
    print("="*70)
    print("CONTEO POR NIVEL DE PROBABILIDAD (todos los repuestos)")
    print("="*70)
    print(resultado["detalle"]["probabilidad_obsolescencia"].value_counts(), "\n")

    print("="*70)
    print("FIN DE PRUEBA KPI 6 - OBSOLESCENCIA")
    print("="*70)

if __name__ == "__main__":
    test_kpi6()
