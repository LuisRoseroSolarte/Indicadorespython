import logging
from pathlib import Path

# ==========================
# CARPETA DE LOGS
# ==========================
CARPETA_LOGS = Path("logs")
CARPETA_LOGS.mkdir(exist_ok=True)


# ==========================
# CONFIGURACIÓN DEL LOGGER
# ==========================
logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s | NIVEL: %(levelname)s | ORIGEN: %(name)s | MENSAJE: %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",  # Formato de fecha y hora
    handlers=[
        logging.FileHandler(CARPETA_LOGS/ "inventario.log", encoding="utf-8"),  # Guardar en archivo
        logging.StreamHandler()  # Mostrar también en consola
    ]
)
# ==========================
# LOGGER DE LA APLICACIÓN
# ==========================
logger = logging.getLogger("inventarioAAp")


# logger.info("Conexión establecida correctamente.")

# logger.warning("El archivo Excel no contiene datos.")

# logger.error(f"Error al conectar con la base de datos: {error}")

# logger.critical("No fue posible iniciar la aplicación.")