# from models.etl_model import ETLModel

# prueba =ETLModel()
# datoinicial =  prueba._leer_excel()
# dato =prueba._limpiar_valores_basura(datoinicial)
# #prueba._convertir_tipos_datos(dato)



# from models.inventory_model import InventarioModel

# dato = InventarioModel()
# abc,valor_total_inventario =dato.calcular_clasificacion_abc()
# dato.actualizar_clasificacion_abc()
# print(f"el valor total del inventario es {valor_total_inventario:,.2f}")
# print("Clasificacion")
# print(abc.head(340))
# print("ultimas filas ")
# print(abc.tail(70))




# import pandas as pd
# from models.inventory_model import InventarioModel

# datos =InventarioModel()

# dato2 =datos.calcular_stock_minimo_por_consumo()

# df_stock_minimo = pd.DataFrame(dato2, columns=["stock_minimo", "ELEM"])
# print(df_stock_minimo.head(220))
# print ("DATOS FINALES ")
# print(df_stock_minimo.tail(345))


# from models.datawarehouse_model import DataWarehouseModel
# from models.analytics_model import AnalyticsModels

# dataware =DataWarehouseModel()


# fecha = dataware._obtener_dim_tiempo()
# dataware.actualizar_datawarehouse()
# producto = dataware._obtener_dim_producto()
# movimiento =dataware._obtener_fact_movimientos()

# analisis = AnalyticsModels(producto,fecha,movimiento)
# #calcularValor =analisis.calcular_valorizacion_total_inventario()
# #clacificacionabc =analisis.calcular_clasificacion_abc()
# #clacificacioABC=clacificacionabc[["ELEM","NOMBRE_ELEMENTO","CATEGORIA","ACUM_CANTIDAD"]]
# #alertas =analisis.calcular_alertas_stock()
# #top10 = analisis.calcular_top10_menor_cobertura()
# #calcular_costo_proyectado_reposicion=analisis.calcular_costo_proyectado_reposicion()
# #calcular_indicador_obsolescencia =analisis.calcular_indicador_obsolescencia()
# # calcular_tendencia_de_consumo =analisis.calcular_tendencia_consumo()
# # calcular_pronostico_consumo_mensual=analisis.calcular_pronostico_consumo_mensual()
# #calcular_pronostico_agotamiento= analisis.calcular_pronostico_agotamiento()
# calcular_nivel_inventario_proyectado= analisis.calcular_nivel_inventario_proyectado()

# print(calcular_nivel_inventario_proyectado)

import customtkinter as ctk

from controllers.app_controller import AppController
from views.main_window import MainView


def main():
    """
    Punto de entrada de la aplicación.
    """

    # ============================================
    # CONFIGURACIÓN DE CUSTOMTKINTER
    # ============================================

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # ============================================
    # CREAR VENTANA PRINCIPAL
    # ============================================

    root = ctk.CTk()

    # ============================================
    # CREAR CONTROLADOR PRINCIPAL
    # ============================================

    controlador = AppController()
    
    # ============================================
    # EJECUTAR FLUJO DE CARGA Y KPIs
    # ============================================
    # controlador.cargar_excel()
    # controlador.actualizar_datawarehouse()
    # controlador.cargar_datawarehouse()
    # controlador.calcular_kpis()

    # ============================================
    # CREAR VISTA PRINCIPAL
    # ============================================

    MainView(
        root=root,
        controlador=controlador
    )

    # ============================================
    # INICIAR APLICACIÓN
    # ============================================

    root.mainloop()


if __name__ == "__main__":
    main()

