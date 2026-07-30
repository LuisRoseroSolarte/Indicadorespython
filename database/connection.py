"""
------------------------------------------------------------
Archivo      : connection.py
Proyecto     : Sistema de Gestión de Inventarios
Descripción  : Administra la conexión con la base de datos SQLite.
Autor        : Luis Alfonso Rosero
Arquitectura : MVC
------------------------------------------------------------
"""

import sqlite3
from config import DATABASE_PATH
from utils.logger import logger

class ConexionBaseDatos:
    def __init__(self):
        self.conexion = None
        
    def conectar(self):
        
        try:
       
            if self.conexion is None:
                self.conexion=sqlite3.connect(DATABASE_PATH)
                logger.info("se realizo la conexion correcta a la DB ")
            return self.conexion
        except sqlite3.Error as error:
            logger.error(f"no se pudo realizar la conexion a la DB {error}")
            return None
                   

    def cerrar(self):
        try:
    
            if self.conexion is not None:
                self.conexion.close()
                self.conexion = None
                logger.info("cerrada correctamentela conexion a la DB")
        except sqlite3.Error as error:
            logger.error(f"error al cerrar la base de dato {error}")
            



