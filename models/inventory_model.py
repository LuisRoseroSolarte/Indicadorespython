"""
------------------------------------------------------------
Archivo      : inventory_model.py
Proyecto     : Sistema de Gestión de Inventarios
Descripción  : Gestiona las operaciones CRUD de las tablas
                MAESTRO_REPUESTOS y MOVIMIENTOS_INVENTARIO.
Autor        : Luis Alfonso Rosero
Arquitectura : MVC
------------------------------------------------------------
"""
from database.connection import ConexionBaseDatos
from utils.logger import logger
import sqlite3


class InventarioModel:
    
    def __init__(self):
        self.bd = ConexionBaseDatos()
        self.conexion = self.bd.conectar()
        
        if self.conexion is None:
            raise ConnectionError("falla en la conexion con la BD")
        self.cursor =self.conexion.cursor()
    # ==========================================================
    #  INSERTAR MAESTRO DE REPUESTOS
    # ==========================================================
        
    def insertar_maestro_repuestos(self,datos):
        try:
            self.cursor.executemany("""
                                INSERT OR IGNORE INTO MAESTRO_REPUESTOS(
                                ELEM,
                                NOMBRE_ELEMENTO,
                                UNIDAD,
                                STOCK_MINIMO,
                                CATEGORIA
                                )
                                VALUES(?,?,?,?,?)
                                """,datos)
            self.conexion.commit()
            logger.info(f"se insertaron: {self.cursor.rowcount} elementos")
            return self.cursor.rowcount
        
        except sqlite3.Error as error:
            self.conexion.rollback()
            logger.error(f"fallo al insertar los datos en la tabla maestro repuestos: {error}")
            raise
        
        
        
    def obtener_maestro_repuestos(self):
        
        try:
            self.cursor.execute("""
                                SELECT *FROM MAESTRO_REPUESTOS
                                
                                """)
            
            return self.cursor.fetchall()
            
        except sqlite3.Error as error:
            logger.error(f"error al consultar la tabla MAESTRO_REPUESTOS :{error}")
            raise
        
    def actualizar_stock_minimo(self,elem,stock_minimo):
        try:
            self.cursor.execute("""
                                UPDATE MAESTRO_REPUESTOS SET STOCK_MINIMO =?
                                WHERE ELEM = ?
                                """,(stock_minimo,elem))
            self.conexion.commit()
            logger.info(f"se actualiso stock minimo :{elem}")
            
        except sqlite3.Error as error:
            self.conexion.rollback()
            logger.error(f"error al actualizar stock_minimo:{error}")
            raise
               
               
    # ==========================================================
    # MOVIMIENTOS DE INVENTARIO
    # ==========================================================
    def insertar_movimientos(self,datos):
        try:
            self.cursor.executemany("""
                                    INSERT OR IGNORE INTO MOVIMIENTOS_INVENTARIO(
                                    ELEM,
                                    FECHA,
                                    UNITARIO,
                                    ENTRADAS,
                                    SALIDAS,
                                    ACUM_CANTIDAD,
                                    ACUM_VALOR
                                    )
                                     VALUES(?,?,?,?,?,?,?)""",datos)
            
            self.conexion.commit()
            logger.info(f"se insertaron : {self.cursor.rowcount} elementos ")
            return self.cursor.rowcount
            
        except sqlite3.Error as error:
            self.conexion.rollback()
            logger.error(f"error al insertar datos en la tabla Moviientos Inventario:{error}")
            raise
    
    def obtener_movimientos(self):
        try:
            self.cursor.execute("""
                                SELECT * FROM MOVIMIENTOS_INVENTARIO
                                """)
            self.conexion.commit()
            return self.cursor.fetchall()# devuelve una lista de tuplas 
        except sqlite3.Error as error:
            logger.error(f"error al consultar movimientos:{error}")
            raise
            
    # ==========================================================
    # CIERRE DE CONEXIÓN
    # ==========================================================
    def cerrar(self):
        self.bd.cerrar()