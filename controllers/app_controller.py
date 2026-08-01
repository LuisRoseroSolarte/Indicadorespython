from models.etl_model import ETLModel
from models.inventory_model import InventarioModel
from models.datawarehouse_model import DataWarehouseModel
from models.analytics_model import AnalyticsModels
from database.connection import ConexionBaseDatos
from utils.logger import logger

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

        # ============================
        # DataFrames del Data Warehouse
        # ============================
        self.dim_producto = None
        self.dim_tiempo = None
        self.fact_movimientos = None

        # ============================
        # KPIs
        # ============================
        self.kpi1_clasificacion_abc = None
        self.kpi2_valorizacion_total = None
        self.kpi3_alertas_stock = None
        self.kpi4_menor_cobertura = None
        self.kpi5_costo_reposicion = None
        self.kpi6_obsolescencia = None
        self.kpi7_tendencia_consumo = None
        self.kpi8_pronostico_consumo = None
        self.kpi9_pronostico_agotamiento = None
        self.kpi10_nivel_inventario = None

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

        etl = ETLModel()
        data_maestro, data_movimientos = etl.tratamiento_datos()

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
        self.inventory_model.actualizar_clasificacion_abc()

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
        pandas, y construye AnalyticsModels con ellos.
        """

        logger.info("PASO 3: Cargando DataFrames del Data Warehouse...")

        conexion_bd = ConexionBaseDatos()
        conexion = conexion_bd.conectar()

        try:
            self.dim_producto = pd.read_sql_query("SELECT * FROM DIM_PRODUCTO", conexion)
            self.dim_tiempo = pd.read_sql_query("SELECT * FROM DIM_TIEMPO", conexion)
            self.fact_movimientos = pd.read_sql_query("SELECT * FROM FACT_MOVIMIENTOS", conexion)

            self.analytics_model = AnalyticsModels(
                self.dim_producto,
                self.dim_tiempo,
                self.fact_movimientos
            )

            logger.info("PASO 3: DataFrames del Data Warehouse cargados correctamente.")

        finally:
            conexion_bd.cerrar()

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

        # self.kpi2_valorizacion_total = ...   # PENDIENTE: confirmar/crear método
        # self.kpi3_alertas_stock = ...        # PENDIENTE: confirmar/crear método

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

        logger.info("PASO 4: Los 10 KPIs se calcularon correctamente.")

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

    # =====================================================
    # FLUJO COMPLETO (opcional, ejecuta los 5 pasos en orden)
    # =====================================================

    def ejecutar_flujo_completo(self):
        """
        Ejecuta los 5 pasos del pipeline en el orden correcto.
        Útil para pruebas rápidas o para una ejecución automática
        sin control manual de cada paso.
        """

        self.cargar_excel()
        self.actualizar_datawarehouse()
        self.cargar_datawarehouse()
        self.calcular_kpis()
        self.cerrar()

        logger.info("Flujo completo ejecutado correctamente.")
