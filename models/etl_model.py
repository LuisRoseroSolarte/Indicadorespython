"""
------------------------------------------------------------
Archivo      : etl_model.py
Proyecto     : Sistema de Gestión de Inventarios
Descripción  : Lee el archivo Excel, realiza el proceso ETL
               (Extracción, Transformación y Carga lógica)
               y prepara los DataFrames para ser enviados
               al InventarioModel.
Autor        : Luis Alfonso Rosero
Arquitectura : MVC
------------------------------------------------------------
"""

import pandas as pd
import numpy as np


#from config import RUTA_ARCHIVO_EXCEL
from utils.logger import logger


class ETLModel:
    """
    Realiza el proceso ETL de los movimientos de inventario.
    """

    def __init__(self):

        self.ruta_archivo =None #RUTA_ARCHIVO_EXCEL
        #self.ruta_archivo=RUTA_ARCHIVO_EXCEL

    
    #*******************************************************
    def establecer_ruta_archivo(self, ruta_archivo):
        """
    Guarda la ruta del archivo Excel seleccionada
    por el usuario.
    """

        self.ruta_archivo = ruta_archivo
    
    
    # ==========================================================
    # MÉTODO PRINCIPAL
    # ==========================================================

    def tratamiento_datos(self):
        """
        Ejecuta el proceso ETL completo.

        Retorna:
            data_maestro
            data_movimiento_repuestos
        """

        try:

            logger.info("Iniciando proceso ETL.")

            # =====================================================
            # LECTURA DEL ARCHIVO EXCEL
            # =====================================================

            datos = self._leer_excel()

            # =====================================================
            # LIMPIEZA GENERAL DE COLUMNAS
            # =====================================================

            datos.columns = (
                datos.columns
                .astype(str)
                .str.strip()
                .str.replace("  ", " ", regex=False)
                .str.upper()
            )

            # =====================================================
            # FILTRAR SOLO REPUESTOS
            # =====================================================

            datos_filtrados = datos[datos["LIN"] == 900].copy()

            filas, columnas = datos_filtrados.shape

            logger.info(
                f"Registros filtrados correctamente. "
                f"Filas: {filas} | Columnas: {columnas}"
            )

            # =====================================================
            # SELECCIONAR COLUMNAS NECESARIAS
            # =====================================================

            datos_proyecto = datos_filtrados[
                [
                    "ELEM",
                    "NOMBRE ELEMENTO",
                    "UNIDAD",
                    "FECHA",
                    "UNITARIO",
                    "ENTRADAS",
                    "SALIDAS",
                    "ACUM CANTIDAD",
                    "ACUM VALOR",
                ]
            ].copy()

            # =====================================================
            # LIMPIEZA GENERAL
            # =====================================================

            datos_proyecto = self._limpiar_valores_basura(datos_proyecto)

            # =====================================================
            # COMPLETAR FECHAS VACÍAS
            # =====================================================

            mascara = datos_proyecto["NOMBRE ELEMENTO"].notna()

            datos_proyecto.loc[mascara, "FECHA"] = (
                datos_proyecto.loc[mascara, "FECHA"].ffill()
            )

            # =====================================================
            # ELIMINAR VALORES NEGATIVOS
            # =====================================================

            columnas_calculo = [
                "UNITARIO",
                "ENTRADAS",
                "SALIDAS",
                "ACUM CANTIDAD",
                "ACUM VALOR",
            ]

            datos_proyecto[columnas_calculo] = (
                datos_proyecto[columnas_calculo]
                .apply(
                    lambda columna:
                    columna.map(lambda valor: 0 if valor < 0 else valor)
                )
            )

            # =====================================================
            # ELIMINAR FILAS COMPLETAMENTE VACÍAS
            # =====================================================

            datos_proyecto = datos_proyecto.dropna(how="all")

            # =====================================================
            # CONTINÚA EN LA PARTE 2
            # =====================================================

            datos_proyecto = self._convertir_tipos_datos(datos_proyecto)

            datos_proyecto = self._normalizar_unidades(datos_proyecto)

            data_maestro, data_movimiento_repuestos = (
                self._separar_dataframe(datos_proyecto)
            )

            logger.info("Proceso ETL finalizado correctamente.")

            return data_maestro, data_movimiento_repuestos

        except FileNotFoundError:

            logger.error(
                f"No se encontró el archivo Excel: {self.ruta_archivo}"
            )
            raise

        except Exception as error:

            logger.error(f"Error durante el proceso ETL: {error}")
            raise


    # ==========================================================
    # LECTURA DEL ARCHIVO EXCEL
    # ==========================================================

    def _leer_excel(self):
        """
        Lee el archivo Excel de inventario.
        """

        logger.info("Leyendo archivo Excel...")

        datos = pd.read_excel(
            self.ruta_archivo,
            header=6
        )

        logger.info("Archivo leído correctamente.")

        return datos


    # ==========================================================
    # LIMPIEZA GENERAL
    # ==========================================================

    def _limpiar_valores_basura(self, datos):
        """
        Reemplaza valores inválidos por NaN.
        """

        valores_basura = [
            "",
            " ",
            "none",
            "null",
            "nan",
            "-",
            "undefined",
            "error",
        ]

        datos = datos.replace(
            valores_basura,
            np.nan,
            regex=False
        )

        datos = datos.replace(
            r"^\s*$",
            np.nan,
            regex=True
        )

        return datos
    
    
    # ==========================================================
    # CONVERSIÓN DE TIPOS DE DATOS
    # ==========================================================

    def _convertir_tipos_datos(self, datos):
        """
        Convierte las columnas al tipo de dato adecuado para SQLite.
        """

        # =====================================
        # FECHA
        # =====================================

        datos["FECHA"] = pd.to_datetime(
            datos["FECHA"],
            errors="coerce"
        )

        # Si después del ffill todavía queda alguna fecha vacía
        # (por ejemplo, la primera fila del archivo), se rellena
        # con la fecha más antigua encontrada en todo el archivo.
        fecha_minima = datos["FECHA"].min()
        datos["FECHA"] = datos["FECHA"].fillna(fecha_minima)

        datos["FECHA"] = datos["FECHA"].dt.strftime("%Y-%m-%d")

        # =====================================
        # ELEM
        # =====================================

        datos["ELEM"] = (
            datos["ELEM"]
            .astype("string")
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
        )

        # =====================================
        # NOMBRE ELEMENTO
        # =====================================

        datos["NOMBRE ELEMENTO"] = (
            datos["NOMBRE ELEMENTO"]
            .astype("string")
            .str.strip()
        )

        # =====================================
        # UNIDAD
        # =====================================

        datos["UNIDAD"] = (
            datos["UNIDAD"]
            .astype("string")
            .str.strip()
            .replace("","UNID") #CADENAS VACIAS 
            .fillna("UNID") # VALORES NULOS
        )
        
        
        # =====================================
        # COLUMNAS NUMÉRICAS
        # =====================================

        columnas_numericas = [
            "UNITARIO",
            "ENTRADAS",
            "SALIDAS",
            "ACUM CANTIDAD",
            "ACUM VALOR"
        ]

        for columna in columnas_numericas:

            datos[columna] = self._convertir_a_float(
                datos[columna]
            )

        logger.info("Conversión de tipos de datos completada.")

        return datos


    # ==========================================================
    # CONVERSIÓN A FLOAT
    # ==========================================================

    def _convertir_a_float(self, columna):
        """
        Convierte una columna a tipo float.
        """

        columna = pd.to_numeric(
            columna
                .astype(str)
                .str.strip()
                .str.replace(",", "", regex=False)
                .str.replace(
                    r"\((.*)\)",
                    r"-\1",
                    regex=True
                )
                .replace("", "0"),
            errors="coerce"
        )

        return columna


    # ==========================================================
    # NORMALIZACIÓN DE UNIDADES
    # ==========================================================

    def _normalizar_unidades(self, datos):
        """
        Estandariza las unidades de medida.
        """

        datos["UNIDAD"] = datos["UNIDAD"].replace(
            ["nan", ""],
            "INDETERMINADO"
        )

        datos["UNIDAD"] = datos["UNIDAD"].str.upper()

        mapeo_unidades = {

            # Unidades
            "UN": "UND",
            "UNI": "UND",
            "UND": "UND",
            "NU": "UND",

            # Longitud
            "MTS": "METROS",
            "MTR": "METROS",
            "MT": "METROS",
            "M": "METROS",
            "MTC": "METROS",
            "MTK": "METROS",

            # Líquidos
            "LT": "LITROS",
            "LTR": "LITROS",
            "GL": "GALON",

            # Otros
            "PAR": "PAR",
            "PR": "PAR",
            "KGM": "KILO",
            "LB": "LIBRA",
            "KIT": "KIT",
            "JGO": "JUEGO"

        }

        datos["UNIDAD"] = (
            datos["UNIDAD"]
            .map(mapeo_unidades)
            .fillna(datos["UNIDAD"])
        )

        logger.info("Unidades normalizadas correctamente.")

        return datos
    
    # ==========================================================
    # SEPARACIÓN DE DATAFRAMES
    # ==========================================================
    def _separar_dataframe(self, datos):
        """
    Separa la información en dos DataFrames:
    1. Maestro de repuestos.
    2. Movimientos de inventario.
    """

    # =====================================================
    # RENOMBRAR COLUMNAS
    # =====================================================

        datos = datos.rename(
            columns={
                "NOMBRE ELEMENTO": "NOMBRE_ELEMENTO",
                "ACUM CANTIDAD": "ACUM_CANTIDAD",
                "ACUM VALOR": "ACUM_VALOR"
            }
        )

        # =====================================================
        # DATAFRAME MAESTRO DE REPUESTOS
        # =====================================================

        data_maestro = datos[
            [
                "ELEM",
                "NOMBRE_ELEMENTO",
                "UNIDAD"
            ]
        ].copy()

        # Eliminar repuestos repetidos

        data_maestro = data_maestro.drop_duplicates(
            subset="ELEM"
        )

        # =====================================================
        # DATAFRAME MOVIMIENTOS
        # =====================================================

        data_movimiento_repuestos = datos[
            [
                "ELEM",
                "FECHA",
                "UNITARIO",
                "ENTRADAS",
                "SALIDAS",
                "ACUM_CANTIDAD",
                "ACUM_VALOR"
            ]
        ].copy()

        logger.info(
            f"Maestro de repuestos: {len(data_maestro)} registros."
        )

        logger.info(
            f"Movimientos de inventario: {len(data_movimiento_repuestos)} registros."
        )

        return data_maestro, data_movimiento_repuestos

    # ==========================================================
    # INFORMACIÓN DEL PROCESO ETL
    # ==========================================================

    def obtener_resumen(self, data_maestro, data_movimiento_repuestos):
        """
        Devuelve un resumen del proceso ETL.
        """

        resumen = {

            "total_repuestos": len(data_maestro),

            "total_movimientos": len(data_movimiento_repuestos),

            "columnas_maestro": list(data_maestro.columns),

            "columnas_movimientos": list(data_movimiento_repuestos.columns)

        }

        return resumen
    