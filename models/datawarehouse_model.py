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
import pandas as pd
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
              INSERT INTO DIM_TIEMPO(FECHA,DIA,MES,ANO)
              SELECT DISTINCT FECHA,
                    CAST(strftime('%d',FECHA) AS INTEGER ) AS DIA,
                    CAST(strftime('%m',FECHA) AS INTEGER ) AS MES,
                    CAST(strftime('%Y',FECHA) AS INTEGER ) AS ANO
              FROM MOVIMIENTOS_INVENTARIO
              WHERE FECHA IS NOT NULL
              ORDER BY FECHA
              """
        self.cursor.execute(query)
        logger.info("fecha cargada correctamente n DIM_TIEMPO")
        
    def _cargar_fact_movimientos(self):
        """
    Construye la tabla de hechos FACT_MOVIMIENTOS a partir
    de la tabla MOVIMIENTOS_INVENTARIO, consolidando en una
    sola fila por ELEM + FECHA cuando hay varios movimientos
    el mismo día.
    """
        logger.info("construyendo FACT_MOVIMIENTOS....")

        query = """
            INSERT OR IGNORE INTO FACT_MOVIMIENTOS (ELEM, FECHA, UNITARIO, ENTRADAS, SALIDAS, ACUM_CANTIDAD, ACUM_VALOR)
            SELECT
                agregados.ELEM,
                agregados.FECHA,
                ultimo.UNITARIO,
                agregados.TOTAL_ENTRADAS,
                agregados.TOTAL_SALIDAS,
                ultimo.ACUM_CANTIDAD,
                ultimo.ACUM_VALOR
            FROM (
                SELECT ELEM, FECHA,
                        SUM(ENTRADAS) AS TOTAL_ENTRADAS,
                        SUM(SALIDAS)  AS TOTAL_SALIDAS
                FROM MOVIMIENTOS_INVENTARIO
                GROUP BY ELEM, FECHA
            ) AS agregados
            JOIN (
                SELECT ELEM, FECHA, UNITARIO, ACUM_CANTIDAD, ACUM_VALOR
                FROM (
                    SELECT ELEM, FECHA, UNITARIO, ACUM_CANTIDAD, ACUM_VALOR,
                            ROW_NUMBER() OVER (PARTITION BY ELEM, FECHA ORDER BY ID DESC) AS rn
                    FROM MOVIMIENTOS_INVENTARIO
                )
                WHERE rn = 1
            ) AS ultimo
            ON agregados.ELEM = ultimo.ELEM AND agregados.FECHA = ultimo.FECHA
            ORDER BY agregados.FECHA, agregados.ELEM
            """
        self.cursor.execute(query)
        logger.info(
            f"FACT_MOVIMIENTOS cargado correctamente. "
            f"Registros insertados: {self.cursor.rowcount}"
    )
        

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
        
    def _obtener_dim_producto(self):
        try:
            self.cursor.execute("SELECT * FROM DIM_PRODUCTO")
            filas = self.cursor.fetchall()   # lista de tuplas
            columnas = [desc[0] for desc in self.cursor.description]  # nombres de columnas

            # Convertir a DataFrame
            df = pd.DataFrame(filas, columns=columnas)

            return df

        except sqlite3.Error as error:
            logger.error(f"error al consultar movimientos: {error}")
            raise


    def _obtener_dim_tiempo(self):
            try:
                self.cursor.execute("SELECT * FROM DIM_TIEMPO")
                filas = self.cursor.fetchall()   # lista de tuplas
                columnas = [desc[0] for desc in self.cursor.description]  # nombres de columnas
    
                # Convertir a DataFrame
                df = pd.DataFrame(filas, columns=columnas)
    
                return df
    
            except sqlite3.Error as error:
                logger.error(f"error al consultar movimientos: {error}")
                raise
            
            
    
    def _obtener_fact_movimientos(self):
            try:
                self.cursor.execute("SELECT * FROM FACT_MOVIMIENTOS")
                filas = self.cursor.fetchall()   # lista de tuplas
                columnas = [desc[0] for desc in self.cursor.description]  # nombres de columnas
    
                # Convertir a DataFrame
                df = pd.DataFrame(filas, columns=columnas)
    
                return df
    
            except sqlite3.Error as error:
                logger.error(f"error al consultar movimientos: {error}")
                raise
    
    
    
    # =====================================================
    # ACTUALIZAR STOCK MÍNIMO
    # =====================================================

    def actualizar_stock_minimo(self, elem, nuevo_stock):
        """
        Actualiza el stock mínimo del repuesto
        en la tabla DIM_PRODUCTO.
        """

        try:

            sql = """
            UPDATE DIM_PRODUCTO
            SET STOCK_MINIMO = ?
            WHERE ELEM = ?
            """

            self.cursor.execute(
                sql,
                (
                    nuevo_stock,
                    elem
                )
            )

            self.conexion.commit()

            logger.info(
                f"Stock mínimo actualizado correctamente. "
                f"ELEM={elem} | STOCK_MINIMO={nuevo_stock}"
            )

        except Exception as error:

            self.conexion.rollback()

            logger.error(
                f"Error actualizando STOCK_MINIMO: {error}"
            )

            raise

    def cerrar(self):
         """
         Cierra la conexión con la base de datos.
         """
         self.bd.cerrar()