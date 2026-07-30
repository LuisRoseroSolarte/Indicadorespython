"""
------------------------------------------------------------
Archivo      : schema.py
Proyecto     : Sistema de Gestión de Inventarios
Descripción  : Crea la estructura de la base de datos.
Autor        : Luis Alfonso Rosero
Arquitectura : MVC
------------------------------------------------------------
"""
from database.connection import ConexionBaseDatos
from utils.logger import logger
import sqlite3


class EsquemaBaseDatos:
    
    def __init__(self):
        self.bd = ConexionBaseDatos()
        self.conexion = self.bd.conectar()
        
        if self.conexion is None:
            raise ConnectionError("error critico, no se pudo conectar a la aabse de datos")
        
        
        self.cursor = self.conexion.cursor()
        
        
        
    def crearTablas(self):
        
        try:
            self._crear_tabla_maestro_repuestos()
            self._crear_tabla_movimientos_inventarios()
            self.conexion.commit()
            self.conexion.close()
            logger.info("se crearon las tablas correctamente")
        except sqlite3.Error as error:
            logger.error(f"no se crearon las tablas :{error}")
            raise
        
        
    #*******************************************************************
    # BASE DE DATOS OPERATIVA
    # ***************************************************************** 
         
    def _crear_tabla_maestro_repuestos(self):
        
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS MAESTRO_REPUESTOS (
                            ELEM TEXT PRIMARY KEY,
                            NOMBRE_ELEMENTO TEXT NOT NULL,
                            UNIDAD TEXT,
                            STOCK_MINIMO REAL,
                            CATEGORIA TEXT
                                ); 
                            
                            """     
                             )
        logger.info("Tabla MAESTRO_REPUESTOS creada.")
        
    
    def _crear_tabla_movimientos_inventarios(self):
        self.cursor.execute("""
                        CREATE TABLE IF NOT EXISTS MOVIMIENTOS_INVENTARIO(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            ELEM TEXT NOT NULL,
                            FECHA TEXT,
                            UNITARIO REAL,
                            ENTRADAS REAL,
                            SALIDAS REAL,
                            ACUM_CANTIDAD REAL,
                            ACUM_VALOR REAL,
                            FOREIGN KEY (ELEM) REFERENCES MAESTRO_REPUESTOS(ELEM),
                            UNIQUE (ELEM, FECHA, UNITARIO, ENTRADAS, SALIDAS, ACUM_CANTIDAD, ACUM_VALOR)
                                )
                        """)
        logger.info("Tabla MOVIMIENTOS_INVENTARIO creada.")
        
    #*******************************************************************
    # DATAWAREHOUSE-BASE DE DATO DE ANALISIS
    # *****************************************************************   
    
    def _crear_dim_producto(self):
        """
        Crea la dimensión de productos.
        """

        self.cursor.execute("""
            CREATE TABLE DIM_PRODUCTO (
            ELEM VARCHAR(50) PRIMARY KEY,
            NOMBRE_ELEMENTO VARCHAR(200) NOT NULL,
            UNIDAD VARCHAR(50) NOT NULL,
            STOCK_MINIMO FLOAT,
            CATEGORIA VARCHAR(100)
            )
        """)

        logger.info("Tabla 'dim_producto' verificada.")

    def _crear_dim_tiempo(self):
        """
        Crea la dimensión de tiempo.
        """

        self.cursor.execute("""
            CREATE TABLE DIM_TIEMPO (
            FECHA DATE PRIMARY KEY,
            DIA INT NOT NULL,
            SEMANA INT NOT NULL,
            MES INT NOT NULL,
            ANO INT NOT NULL
            )
        """)

        logger.info("Tabla 'dim_tiempo' verificada.")

    def _crear_fact_movimientos(self):
        """
        Crea la tabla de hechos.
        """

        self.cursor.execute("""
            CREATE TABLE FACT_MOVIMIENTOS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ELEM VARCHAR(50) NOT NULL,
            FECHA DATE NOT NULL,
            UNITARIO FLOAT,
            ENTRADAS FLOAT,
            SALIDAS FLOAT,
            ACUM_CANTIDAD FLOAT,
            ACUM_VALOR FLOAT,
            CONSTRAINT FK_MOV_PRODUCTO FOREIGN KEY (ELEM) REFERENCES DIM_PRODUCTO(ELEM),
            CONSTRAINT FK_MOV_TIEMPO FOREIGN KEY (FECHA) REFERENCES DIM_TIEMPO(FECHA),
            CONSTRAINT UQ_MOVIMIENTO UNIQUE (ELEM, FECHA)
            )
        """)

        logger.info("Tabla 'fact_movimientos' verificada.")
        
    
    