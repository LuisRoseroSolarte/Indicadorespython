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
import math
import pandas as pd
from config import DIAS_COBERTURA,STOCK_MINIMO_POR_DEFECTO


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
 
    def calcular_stock_minimo_por_consumo(self):
        """
        Calcula STOCK_MINIMO para cada producto con base en su
        consumo histórico de SALIDAS, usando la fórmula:
            STOCK_MINIMO = (Total SALIDAS / Días de historial) * DIAS_COBERTURA

        Actualiza la columna STOCK_MINIMO en MAESTRO_REPUESTOS.
        Productos sin suficiente historial (menos de 2 fechas distintas)
        se actualizan con el valor STOCK_MINIMO_POR_DEFECTO.
        """

        logger.info("Calculando STOCK_MINIMO a partir del consumo histórico...")

        try:
            consulta = """
                SELECT ELEM, FECHA, SALIDAS
                FROM MOVIMIENTOS_INVENTARIO
            """

            movimientos = pd.read_sql_query(consulta, self.conexion)

            movimientos["FECHA"] = pd.to_datetime(movimientos["FECHA"], errors="coerce")

            # =====================================================
            # AGRUPAR POR PRODUCTO
            # =====================================================
            resumen = movimientos.groupby("ELEM").agg(
                total_salidas=("SALIDAS", "sum"),
                fecha_min=("FECHA", "min"),
                fecha_max=("FECHA", "max")
            ).reset_index()

            resumen["dias_historial"] = (
                resumen["fecha_max"] - resumen["fecha_min"]
            ).dt.days

            # =====================================================
            # SEPARAR PRODUCTOS CON Y SIN SUFICIENTE HISTORIAL
            # =====================================================
            resumen_valido = resumen[resumen["dias_historial"] > 0].copy()
            sin_historial = resumen[resumen["dias_historial"] <= 0].copy()

            if not sin_historial.empty:
                logger.warning(
                    f"{len(sin_historial)} productos no tienen suficiente "
                    f"historial para calcular STOCK_MINIMO y se les asignará "
                    f"el valor por defecto ({STOCK_MINIMO_POR_DEFECTO})."
                )

            # =====================================================
            # CALCULAR CONSUMO PROMEDIO DIARIO Y STOCK MÍNIMO
            # =====================================================
            resumen_valido["consumo_promedio_diario"] = (
                resumen_valido["total_salidas"] / resumen_valido["dias_historial"]
            )

            resumen_valido["STOCK_MINIMO_CALCULADO"] = (
                resumen_valido["consumo_promedio_diario"] * DIAS_COBERTURA
            )

            # =====================================================
            # ASIGNAR VALOR POR DEFECTO A PRODUCTOS SIN HISTORIAL
            # =====================================================
            sin_historial["STOCK_MINIMO_CALCULADO"] = STOCK_MINIMO_POR_DEFECTO

            # =====================================================
            # UNIR AMBOS GRUPOS PARA ACTUALIZAR MAESTRO_REPUESTOS
            # =====================================================
            resumen_completo = pd.concat(
                [resumen_valido, sin_historial],
                ignore_index=True
            )
            
            # =====================================================
            # REDONDEAR STOCK_MINIMO A ENTERO (siempre hacia arriba)
            # =====================================================
            resumen_completo["STOCK_MINIMO_CALCULADO"] = (
                resumen_completo["STOCK_MINIMO_CALCULADO"]
                .apply(math.ceil)
                .astype(int)
            )

            datos_actualizar = list(zip(
                resumen_completo["STOCK_MINIMO_CALCULADO"],
                resumen_completo["ELEM"]
            ))

            self.cursor.executemany(
                """
                UPDATE MAESTRO_REPUESTOS
                SET STOCK_MINIMO = ?
                WHERE ELEM = ?
                """,
                datos_actualizar
            )

            self.conexion.commit()

            logger.info(
                f"STOCK_MINIMO actualizado para {len(datos_actualizar)} productos "
                f"({len(resumen_valido)} calculados, {len(sin_historial)} con valor por defecto)."
            )
            return datos_actualizar

        except Exception as error:
            self.conexion.rollback()
            logger.error(f"Error al calcular STOCK_MINIMO: {error}")
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
    # CALCULAR CLASIFICACIÓN ABC devuelve el dataframe y el valor total del inventario
    # ==========================================================

    def calcular_clasificacion_abc(self):
        """
        Calcula la clasificación ABC de los repuestos utilizando
        el último valor del inventario (ACUM_VALOR) registrado
        para cada artículo.

        No modifica la base de datos. Devuelve un DataFrame con las
        columnas: ELEM, ACUM_VALOR, PORCENTAJE, PORCENTAJE_ACUMULADO,
        CATEGORIA.
        """

        logger.info("Iniciando cálculo de la clasificación ABC...")

        # ======================================================
        # OBTENER EL ÚLTIMO MOVIMIENTO DE CADA REPUESTO
        # ======================================================

        consulta = """
            SELECT
                MI.ELEM,
                MI.ACUM_VALOR

            FROM MOVIMIENTOS_INVENTARIO MI

            INNER JOIN
            (
                SELECT
                    ELEM,
                    MAX(ID) AS ID
                FROM MOVIMIENTOS_INVENTARIO
                GROUP BY ELEM
            ) ULTIMO

            ON MI.ID = ULTIMO.ID
        """

        datosABC = pd.read_sql_query(
            consulta,
            self.conexion
        )

        # ======================================================
        # VALIDAR SI EXISTEN DATOS
        # ======================================================

        if datosABC.empty:

            logger.warning(
                "No existen datos para calcular la clasificación ABC."
            )

            return datosABC

        # ======================================================
        # ORDENAR POR VALOR DEL INVENTARIO
        # ======================================================

        datosABC = datosABC.sort_values(
            by="ACUM_VALOR",
            ascending=False
        ).reset_index(drop=True)

        # ======================================================
        # CALCULAR EL VALOR TOTAL DEL INVENTARIO
        # ======================================================

        valorTotalInventario = datosABC["ACUM_VALOR"].sum()

        if valorTotalInventario <= 0:

            logger.warning(
                "El valor total del inventario es cero."
            )

            return pd.DataFrame()

        # ======================================================
        # CALCULAR PORCENTAJE DE PARTICIPACIÓN
        # ======================================================

        datosABC["PORCENTAJE"] = (
            datosABC["ACUM_VALOR"] /
            valorTotalInventario
        ) * 100

        # ======================================================
        # CALCULAR PORCENTAJE ACUMULADO
        # ======================================================

        datosABC["PORCENTAJE_ACUMULADO"] = (
            datosABC["PORCENTAJE"].cumsum()
        )

        # ======================================================
        # ASIGNAR CATEGORÍA ABC
        # ======================================================

        categorias = []

        for porcentaje in datosABC["PORCENTAJE_ACUMULADO"]:

            if porcentaje <= 80:
                categorias.append("A")

            elif porcentaje <= 95:
                categorias.append("B")

            else:
                categorias.append("C")

        datosABC["CATEGORIA"] = categorias

        logger.info("Clasificación ABC calculada correctamente.")

        return datosABC
    
    
    # ==========================================================
    # ACTUALIZAR CLASIFICACIÓN ABC
    # ==========================================================

    def actualizar_clasificacion_abc(self):
        """
        Calcula la clasificación ABC y actualiza la columna CATEGORIA
        de la tabla MAESTRO_REPUESTOS con el resultado.
        """

        logger.info("Iniciando actualización de la clasificación ABC...")

        try:

            datosABC = self.calcular_clasificacion_abc()

            if datosABC.empty:
                logger.warning(
                    "No se actualizó la clasificación ABC porque no hay datos."
                )
                return

            # ======================================================
            # ACTUALIZAR LA TABLA MAESTRO_REPUESTOS
            # ======================================================

            datosActualizar = zip(
                datosABC["CATEGORIA"],
                datosABC["ELEM"]
            )

            self.cursor.executemany(
                """
                UPDATE MAESTRO_REPUESTOS
                SET CATEGORIA = ?
                WHERE ELEM = ?
                """,
                datosActualizar
            )

            # ======================================================
            # CONFIRMAR CAMBIOS
            # ======================================================

            self.conexion.commit()

            logger.info(
                "Clasificación ABC actualizada correctamente en MAESTRO_REPUESTOS."
            )

        except Exception as error:

            self.conexion.rollback()

            logger.error(
                f"Error al actualizar la clasificación ABC: {error}"
            )

            raise
                
    # ==========================================================
    # CIERRE DE CONEXIÓN
    # ==========================================================
    def cerrar(self):
        self.bd.cerrar()