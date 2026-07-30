"""
------------------------------------------------------------
Archivo      : datawarehouse_model.py
Proyecto     : Sistema de Gestión de Inventarios
Descripción  : Construye y actualiza el Data Warehouse
               a partir de la Base de Datos Operativa.
Autor        : Luis Alfonso Rosero
Arquitectura : MVC
------------------------------------------------------------
"""
import sqlite3
from utils.logger import logger
from database.connection import ConexionBaseDatos


class DataWarehouseModel:

    def __init__(self):
        self.bd= ConexionBaseDatos()
        self.conexion = self.bd.conectar()
        
        if self.conexion is None:
            raise ("no fue posible conectarse a la base de datos ")
        
        self.cursor = self.conexion.cursor()
        logger.info("se realizo correctamente la comunicacion con la base de datos")
        

    def actualizar_datawarehouse(self): 
        """
        Reconstruye completamente el Data Warehouse.

        Proceso:
            1. Inicia una transacción.
            2. Vacía las tablas del Data Warehouse.
            3. Reinicia el AUTOINCREMENT de FACT_MOVIMIENTOS.
            4. Construye las dimensiones.
            5. Construye la tabla de hechos.
            6. Confirma la transacción.
        """
        try:
            # Vaciar el Data Warehouse

            self._vaciar_datawarehouse()

            # Reiniciar AUTOINCREMENT

            self._reiniciar_autoincremento()

            # Construir dimensiones

            self._cargar_dim_producto()

            self._cargar_dim_tiempo()

            # Construir tabla de hechos

            self._cargar_fact_movimientos()

            # Confirmar cambios

            self.conexion.commit()

            logger.info("Data Warehouse actualizado correctamente.")
        except sqlite3.Error as error:
            self.conexion.rollback()
            logger.error(f"se produjo un error en la sentencia SQL:{error}")
            raise
          
    def _vaciar_datawarehouse(self):
        """
        Elimina todos los registros del Data Warehouse.

        El orden de eliminación respeta la integridad referencial:
            1. FACT_MOVIMIENTOS
            2. DIM_PRODUCTO
            3. DIM_TIEMPO
        """

        logger.info("Vaciando tablas del Data Warehouse...")

    # ==========================================
    # Eliminar tablas datawarehouse
    # ==========================================
    
        tablas =["FACT_MOVIMIENTOS","DIM_PRODUCTO","DIM_TIEMPO"]
    
        for tabla in tablas:
            self.cursor.execute(f"DELETE FROM {tabla}")
        
    

    def _cargar_dim_producto(self):
        """
        Construye la dimensión de productos a partir de la tabla
        MAESTRO_REPUESTOS de la Base de Datos Operativa.
        """

        logger.info("Construyendo DIM_PRODUCTO...")
        query="""
                INSERT INTO DIM_PRODUCTO(ELEM, NOMBRE_ELEMENTO, UNIDAD, STOCK_MINIMO, CATEGORIA)
                SELECT ELEM, NOMBRE_ELEMENTO, UNIDAD, STOCK_MINIMO, CATEGORIA
                FROM MAESTRO_REPUESTOS
                ORDER BY ELEM
        
              """
        self.cursor.execute(query)
        
        logger.info(
                    "elementos cargados correctamente en DIM_PRODUCTO"
                    
                    f"registros insertados: {self.cursor.rowcount}"
                    )
        
        
        

    def _cargar_dim_tiempo(self):
        
        """
        Construye la dimensión de tiempo a partir de las fechas
        registradas en la tabla MOVIMIENTOS_INVENTARIO.
        """
        logger.info("Construyendo DIM_TIEMPO")
        
        query="""
              INSERT INTO DIM_TIEMPO(FECHA,DIA,MES,ANIO)
              SELECT DISTINCT FECHA,
              CAST(strftime(%d,FECHA) AS INTEGER ) AS DIA
              CAST(strftime(%m,FECHA) AS INTEGER ) AS MES
              CAST(strftime(%Y,FECHA) AS INTEGER ) AS ANIO
              FROM MOVIMIENTOS_INVENTARIO
              WHERE FECHA IS NOT NULL
              ORDER BY FECHA
              """
        self.cursor.execute(query)
        logger.info("fecha cargada correctamente n DIM_TIEMPO")
        

    def _cargar_fact_movimientos(self):
        self.cursor.execute()

    def _reiniciar_autoincremento(self):
        """
        Reinicia el contador AUTOINCREMENT de la tabla
        FACT_MOVIMIENTOS.

        Esto permite que, después de reconstruir el Data Warehouse,
        los identificadores vuelvan a comenzar desde 1.
        """

        logger.info("Reiniciando AUTOINCREMENT de FACT_MOVIMIENTOS...")
        
        self.cursor.execute("""
                            DELETE FROM sqlite_sequence WHERE name ='FACT_MOVIMIENTOS'
                            """)
        logger.info("Autoincrement reiniciado correctamente")

    def cerrar(self):
        self.cursor.execute()