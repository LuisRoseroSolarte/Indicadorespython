from models.etl_model import ETLModel
from models.inventory_model import InventarioModel
from models.datawarehouse_model import DataWarehouseModel
from models.analytics_model import AnalyticsModels
from database.connection import ConexionBaseDatos
from utils.logger import logger
from views.main_window import MainView
import pandas as pd


class AppController:
    """
    Controlador principal de la aplicación.

    FLUJO GENERAL (ejecutar en este orden):

        PASO 1 -> cargar_excel()
                  Excel -> ETL -> Base de Datos Operativa
                  (incluye calcular STOCK_MINIMO y CATEGORIA)

        PASO 2 -> actualizar_datawarehouse()
                  Base de Datos Operativa -> Data Warehouse (SQLite)

        PASO 3 -> cargar_datawarehouse()
                  Data Warehouse (SQLite) -> DataFrames en memoria

        PASO 4 -> calcular_kpis()
                  DataFrames -> Cálculo de los 10 KPIs

        PASO 5 -> cerrar()
                  Libera las conexiones abiertas

    Cada paso depende de que el anterior haya corrido con éxito.
    """

    def __init__(self):

        # ============================
        # Modelos
        # ============================
        self.inventory_model = None
        self.datawarehouse_model = None
        self.analytics_model = None
        self.etl_model = ETLModel()
        self.main_view = None
        # ============================
        # DataFrames del Data Warehouse
        # ============================
        self.dim_producto = None
        self.dim_tiempo = None
        self.fact_movimientos = None

        # ============================
        # KPIs
        # ============================
        self.kpi1_clasificacion_abc = {"A": 0, "B": 0, "C": 0}
        self.kpi2_valorizacion_total =0
        self.kpi3_alertas_stock = pd.DataFrame(columns=["INDICADOR", "CANTIDAD"])
        self.kpi4_menor_cobertura = pd.DataFrame(
                                                    columns=[
                                                        "ELEM",
                                                        "NOMBRE_ELEMENTO",
                                                        "stock_actual",
                                                        "consumo_diario_promedio",
                                                        "dias_cobertura"
                                                    ]
                                                )
        self.kpi5_costo_reposicion = {
                                        "costo_total_proyectado": 0,
                                        "detalle": pd.DataFrame(
                                            columns=[
                                                "ELEM",
                                                "NOMBRE_ELEMENTO",
                                                "CATEGORIA",
                                                "unitario_actual",
                                                "unitario_proyectado",
                                                "cantidad_a_reponer",
                                                "costo_actual",
                                                "costo_proyectado"
                                            ]
                                        ),
                                        "grafica": pd.DataFrame(
                                            columns=["CATEGORIA", "costo_actual", "costo_proyectado"]
                                        )
                                    }
        
        self.kpi6_obsolescencia =   {
                                        "cantidad_alta_probabilidad": 0,
                                        "porcentaje": 0.0,
                                        "grafica": {
                                            "A": 0,
                                            "B": 0,
                                            "C": 0
                                        },
                                        "detalle": pd.DataFrame(
                                            columns=[
                                                "ELEM",
                                                "NOMBRE_ELEMENTO",
                                                "CATEGORIA",
                                                "meses_sin_movimiento",
                                                "probabilidad_obsolescencia"
                                            ]
                                        )
                                    }
        self.kpi7_tendencia_consumo =  {
                                        "creciente": 0,
                                        "decreciente": 0,
                                        "estable": 0,
                                        "sin_datos_suficientes": 0,
                                        "detalle": pd.DataFrame()
                                         }
        self.kpi8_pronostico_consumo = {
                                        "total_pronosticado": 0.0,
                                        "productos_sin_datos_suficientes": 0,
                                        "detalle": pd.DataFrame(
                                            columns=[
                                                "ELEM",
                                                "NOMBRE_ELEMENTO",
                                                "meses_historial",
                                                "pronostico_proximo_mes"
                                            ]
                                        )
                                    }
        self.kpi9_pronostico_agotamiento = {
                                                "cantidad_criticos": 0,
                                                "detalle": pd.DataFrame(
                                                    columns=[
                                                        "ELEM",
                                                        "NOMBRE_ELEMENTO",
                                                        "stock_actual",
                                                        "consumo_diario_proyectado",
                                                        "dias_agotamiento",
                                                        "estado"
                                                    ]
                                                )
                                            }
        self.kpi10_nivel_inventario =  {
            "cantidad_riesgo_desabastecimiento": 0,
            "detalle": pd.DataFrame(
                [
                    {
                        "ELEM": "",
                        "NOMBRE_ELEMENTO": "",
                        "stock_actual": 0,
                        "consumo_proyectado": 0,
                        "nivel_inventario_proyectado": 0,
                        "estado": "Sin datos suficientes",
                        "dias_agotamiento": None   # <- valor inicial explícito
                    }
                ]
            )
        }
        self.kpi_distribucion_abc_valor = {
                                            "A": 0.0,
                                            "B": 0.0,
                                            "C": 0.0
                                        }
        self.cantidad_repuestos_registrados =0
        

    
    #====================================================================
    #RUTA DE ARCHIVO
    #===================================================================
    def seleccionar_archivo_excel(self,ruta_archivo):
        """
        Recibe la ruta del archivo seleccionada desde la vista
        y la envía al ETL.
        """
    
        self.etl_model.establecer_ruta_archivo(ruta_archivo)
        print("Ruta recibida:", self.etl_model.ruta_archivo)
    
    
    
    # =====================================================
    # PASO 1 - CARGA DE DATOS
    # =====================================================

    def cargar_excel(self):
        """
        Ejecuta el ETL, inserta en la Base de Datos Operativa,
        y calcula STOCK_MINIMO/CATEGORIA antes de construir el DW.
        """

        logger.info("PASO 1: Iniciando carga de Excel...")

        from config import STOCK_MINIMO_DEFAULT, CATEGORIA_DEFAULT

        #etl = ETLModel()
        data_maestro, data_movimientos =self.etl_model.tratamiento_datos() #etl.tratamiento_datos()

        self.inventory_model = InventarioModel()

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

        datos_movimientos = [
            tuple(fila) for _, fila in data_movimientos.iterrows()
        ]

        self.inventory_model.insertar_maestro_repuestos(datos_maestro)
        self.inventory_model.insertar_movimientos(datos_movimientos)
        self.inventory_model.calcular_stock_minimo_por_consumo()
        self.inventory_model.calcular_clasificacion_abc()
        self.inventory_model.actualizar_clasificacion_abc()
        self.inventory_model.cerrar()

        logger.info("PASO 1: Carga de Excel completada correctamente.")

    # =====================================================
    # PASO 2 - ACTUALIZAR DATA WAREHOUSE
    # =====================================================

    def actualizar_datawarehouse(self):
        """
        Reconstruye el Data Warehouse a partir de la base
        de datos operativa ya actualizada.
        """

        logger.info("PASO 2: Actualizando Data Warehouse...")

        self.datawarehouse_model = DataWarehouseModel()
        self.datawarehouse_model.actualizar_datawarehouse()

        logger.info("PASO 2: Data Warehouse actualizado correctamente.")

    # =====================================================
    # PASO 3 - CARGAR DATAFRAMES
    # =====================================================

    def cargar_datawarehouse(self):
        """
        Carga las tablas del Data Warehouse en DataFrames de
        pandas, reutilizando los métodos ya existentes en
        DataWarehouseModel, y construye AnalyticsModels con ellos.
        """

        logger.info("PASO 3: Cargando DataFrames del Data Warehouse...")

        dw = DataWarehouseModel()

        try:
            self.dim_producto = dw._obtener_dim_producto()
            self.dim_tiempo = dw._obtener_dim_tiempo()
            self.fact_movimientos = dw._obtener_fact_movimientos()

            self.analytics_model = AnalyticsModels(
                self.dim_producto,
                self.dim_tiempo,
                self.fact_movimientos
            )

            logger.info("PASO 3: DataFrames del Data Warehouse cargados correctamente.")

        finally:
            dw.cerrar()
            

    # =====================================================
    # PASO 4 - CALCULAR KPIs
    # =====================================================

    def calcular_kpis(self):
        """
        Calcula los diez KPIs de la aplicación y los almacena
        en caché como atributos del controlador.
        """

        if self.analytics_model is None:
            raise RuntimeError(
                "Debes llamar a cargar_datawarehouse() antes de calcular_kpis()."
            )

        logger.info("PASO 4: Calculando los 10 KPIs...")

        self.kpi1_clasificacion_abc = self.analytics_model.calcular_clasificacion_abc()

        self.kpi2_valorizacion_total = self.analytics_model.calcular_valorizacion_total_inventario()
        
        self.kpi_distribucion_abc_valor =self.analytics_model.calcular_distribucion_abc()
        self.kpi3_alertas_stock = self.analytics_model.calcular_alertas_stock()

        self.kpi4_menor_cobertura = self.analytics_model.calcular_top10_menor_cobertura()
        self.kpi5_costo_reposicion = self.analytics_model.calcular_costo_proyectado_reposicion()
        self.kpi6_obsolescencia = self.analytics_model.calcular_indicador_obsolescencia()
        self.kpi7_tendencia_consumo = self.analytics_model.calcular_tendencia_consumo()

        self.kpi8_pronostico_consumo = self.analytics_model.calcular_pronostico_consumo_mensual()

        self.kpi9_pronostico_agotamiento = self.analytics_model.calcular_pronostico_agotamiento(
            pronostico_previo=self.kpi8_pronostico_consumo
        )

        self.kpi10_nivel_inventario = self.analytics_model.calcular_nivel_inventario_proyectado(
            pronostico_previo=self.kpi8_pronostico_consumo
        )
        
        self.cantidad_repuestos_registrados =len(self.analytics_model.dim_producto)
        
        if self.main_view is not None:
            self.main_view.mostrar_registros()

        logger.info("PASO 4: Los 10 KPIs se calcularon correctamente.")

    #==========================================================
    # =====================================================
    # REPUESTOS
    # =====================================================

    def obtener_lista_repuestos(self):
        # """
        # Retorna la lista de repuestos para autocompletar.
        # """

        # if self.dim_producto is None:
        #     return []

        # return (
        #     self.dim_producto["NOMBRE_ELEMENTO"]
        #     .dropna()
        #     .sort_values()
        #     .tolist()
        # )
        
        """
        Retorna la lista de repuestos para el autocompletado.
        Incluye el código (ELEM) y el nombre del repuesto.
        """

        if self.dim_producto is None:
            return []

        return (
            self.dim_producto[
                ["ELEM", "NOMBRE_ELEMENTO"]
            ]
            .dropna(subset=["NOMBRE_ELEMENTO"])
            .sort_values("NOMBRE_ELEMENTO")
            .to_dict("records")
        )
    
    
    
    # =====================================================
    # ACTUALIZAR STOCK MÍNIMO
    # =====================================================

    def actualizar_stock_minimo(self, elem, nuevo_stock):
        """
        Actualiza el stock mínimo de un repuesto.
        """
        print("========================================================================")
        print("SOY EL METODO actualizar _stock_minimo ME ENCUENTROEN EN EL CONTROLADOR")

        self.datawarehouse_model.actualizar_stock_minimo(
            elem,
            nuevo_stock
        )
        
        # Recalcular KPIs
        self.recalcular_kpis_stock_minimo()
       
        # Recargar DW
        self.cargar_datawarehouse()
        
        # Recalcular KPIs
        self.calcular_kpis()
        
        # if self.main_view is not None:
        #     self.main_view.actualizar_vistas()

        print(
            f"Stock mínimo actualizado para {elem}"
        )

        
        
     
     
    # =====================================================
    # RECALCULAR KPIs POR CAMBIO DE STOCK MÍNIMO
    # =====================================================

    def recalcular_kpis_stock_minimo(self):
        """
        Recalcula únicamente los KPIs afectados por el cambio
        del stock mínimo.
        """
        print("LLAMANDO AL METODO :calcular_alertas_stock()")
        self.kpi3_alertas_stock = (
            self.analytics_model.calcular_alertas_stock()
        )

        # self.kpi4_menor_cobertura = (
        #     self.analytics_model.calcular_menor_cobertura()
        # )

        print("KPIs  recalculdos  correctamente.")   
        
    #========================================================
    # devuelve los kpis 
    #===========================================================
    
    def obtener_kpi(self,nombre):
       kpis= {
        "clasificacion_abc": self.kpi1_clasificacion_abc,
        "valorizacion_total": self.kpi2_valorizacion_total,
        "calcular_distribucion":self.kpi_distribucion_abc_valor,
        "alertas_stock": self.kpi3_alertas_stock,
        "menor_cobertura": self.kpi4_menor_cobertura,
        "costo_reposicion": self.kpi5_costo_reposicion,
        "obsolescencia": self.kpi6_obsolescencia,
        "tendencia_consumo": self.kpi7_tendencia_consumo,
        "pronostico_consumo": self.kpi8_pronostico_consumo,
        "pronostico_agotamiento": self.kpi9_pronostico_agotamiento,
        "nivel_inventario": self.kpi10_nivel_inventario,
        "cantidad_repuestos_registrados":self.cantidad_repuestos_registrados,
        }
       return kpis.get(nombre)
       
    # =====================================================
    # PASO 5 - CERRAR APLICACIÓN
    # =====================================================
    
    

    def cerrar(self):
        """
        Libera los recursos utilizados por la aplicación
        (conexiones abiertas a la base de datos).
        """

        logger.info("PASO 5: Liberando recursos...")

        if self.inventory_model is not None:
            self.inventory_model.bd.cerrar()

        if self.datawarehouse_model is not None:
            self.datawarehouse_model.bd.cerrar()

        logger.info("PASO 5: Recursos liberados correctamente.")

    
    
    
    
    # # =====================================================
    # # FLUJO COMPLETO (opcional, ejecuta los 5 pasos en orden)
    # # =====================================================

    # def ejecutar_flujo_completo(self):
    #     """
    #     Ejecuta los 5 pasos del pipeline en el orden correcto.
    #     Útil para pruebas rápidas o para una ejecución automática
    #     sin control manual de cada paso.
    #     """

    #     self.cargar_excel()
    #     self.actualizar_datawarehouse()
    #     self.cargar_datawarehouse()
    #     self.calcular_kpis()
    #     self.cerrar()

    #     logger.info("Flujo completo ejecutado correctamente.")
