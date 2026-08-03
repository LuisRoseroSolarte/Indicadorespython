"""
------------------------------------------------------------
Archivo      : config.py
Proyecto     : Sistema de Gestión de Inventarios
Descripción  : Configuración global de la aplicación.
Autor        : Luis Alfonso Rosero
Arquitectura : MVC
------------------------------------------------------------
"""
import sys
import os
# ==========================
# INFORMACIÓN DE LA APLICACIÓN
# ==========================
STOCK_MINIMO_DEFAULT = 0.0
CATEGORIA_DEFAULT = "SIN CATEGORIA"
APP_NAME = ...
APP_VERSION = ...
APP_AUTHOR = ...
APP_COMPANY = ...

# ==========================
# RUTAS DEL PROYECTO
# ==========================

BASE_DIR = "D:\\PromineralesFinal"
DATABASE_DIR =...
DATABASE_PATH = os.path.join(BASE_DIR, "database", "prominerales.db")
INPUT_DIR = ...
OUTPUT_DIR = ...
RUTA_ARCHIVO_EXCEL ="D:\\PromineralesFinal\\Inventarios_2026_SIMULADO.xlsx"

# ==========================
# CONFIGURACIÓN DE LA INTERFAZ
# ==========================

WINDOW_TITLE = ...
WINDOW_WIDTH = ...
WINDOW_HEIGHT = ...
THEME = ...
COLOR_THEME = ...

# ==========================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ==========================

DATABASE_NAME = ...
DATABASE_VERSION = ...

# ==========================
# CONFIGURACIÓN DEL ETL
# ==========================

SUPPORTED_EXTENSIONS = ...
REQUIRED_COLUMNS = ...
NULL_VALUES = ...
DATE_FORMAT = ...

# ==========================
# CONFIGURACIÓN DE LOS KPIs
# ==========================

ABC_PERCENTAGES = ...
TOP_ITEMS = ...
OBSOLESCENCE_MONTHS = ...
FORECAST_PERIODS = ...

# ==========================================================
# PARÁMETROS DE INVENTARIO
# ==========================================================
STOCK_MINIMO_POR_DEFECTO =12
# Valor por defecto del stock mínimo para nuevos repuestos
DIAS_COBERTURA = 15  # días de consumo que el stock mínimo debe cubrir

FACTOR_STOCK_MAXIMO =3
MINIMO_PUNTOS_TENDENCIA = 4  # mínimo de observaciones distintas para calcular una tendencia confiable
MINIMO_MESES_PRONOSTICO = 3  # mínimo de meses con historial para proyectar consumo del siguiente mes
DIAS_MES_APROX = 30  # días usados para convertir el pronóstico mensual (KPI 8) a consumo diario
UMBRAL_NIP_CERO = 5  # unidades; rango alrededor de 0 considerado "inventario justo"
