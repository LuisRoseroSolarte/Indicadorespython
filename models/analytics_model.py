from utils.logger import logger
from config import FACTOR_STOCK_MAXIMO,MINIMO_PUNTOS_TENDENCIA,MINIMO_MESES_PRONOSTICO,DIAS_MES_APROX,UMBRAL_NIP_CERO
import pandas as pd
import numpy as np






class AnalyticsModels:
    
    def __init__(self,dim_producto, dim_tiempo,fact_movimientos):
       self.dim_producto =dim_producto
       self.dim_tiempo = dim_tiempo
       self.fact_movimientos = fact_movimientos
       
       # Estado actual del inventario
       self.estado_actual_inventario = self._construir_estado_actual_inventario()
       
       # ==========================================================
        # CONSTRUIR ESTADO ACTUAL DEL INVENTARIO
        # ==========================================================

    def _construir_estado_actual_inventario(self):
        """
        Construye un DataFrame con el estado actual del inventario.

        Retorna
        -------
        pandas.DataFrame
        """

        logger.info("Construyendo estado actual del inventario...")

        # ======================================================
        # OBTENER EL ÚLTIMO MOVIMIENTO DE CADA REPUESTO
        # ======================================================

        ultimo_movimiento = (
            self.fact_movimientos
            .sort_values("ID")
            .groupby("ELEM", as_index=False)
            .last()
        )

        # ======================================================
        # UNIR DIM_PRODUCTO CON FACT_MOVIMIENTOS
        # ======================================================

        estado_actual = self.dim_producto.merge(
            ultimo_movimiento,
            on="ELEM",
            how="inner"
        )

        logger.info(
            f"Estado actual construido correctamente. "
            f"Registros: {len(estado_actual)}"
        )

        return estado_actual
    
    
    # ==========================================================
    #  KPI 1 - ordena lor repuestopor categoria  y retorna  ABC POR VALOR DEL INVENTARIO
    # ==========================================================

    def calcular_clasificacion_abc(self):
        """
        Obtiene la clasificación ABC de los repuestos.

        Retorna
        -------
        pandas.DataFrame
        """

        logger.info("Calculando KPI 1 - Clasificación ABC.")

        dataframeABC = self.estado_actual_inventario.copy()

        # ======================================================
        # ORDEN DE LAS CATEGORÍAS
        # ======================================================

        orden_categoria = {
            "A": 1,
            "B": 2,
            "C": 3
        }

        dataframeABC["ORDEN"] = dataframeABC["CATEGORIA"].map(
            orden_categoria
        )

        # ======================================================
        # ORDENAR RESULTADOS
        # ======================================================

        dataframeABC = (
            dataframeABC
            .sort_values(
                by=["ORDEN", "ACUM_VALOR"],
                ascending=[True, False]
            )
            .drop(columns="ORDEN")
            .reset_index(drop=True)
        )

        logger.info(
            "KPI 1 calculado correctamente."
        )

        return dataframeABC
    
    # ==========================================================
    # KPI 2 - VALORIZACIÓN TOTAL DEL INVENTARIO
    # ==========================================================

    def calcular_valorizacion_total_inventario(self):
        """
        Calcula el capital total inmovilizado en inventario.

        Retorna
        -------
        float
            Valor total del inventario.
        """

        logger.info("Calculando KPI 2 - Valorización total del inventario.")

        valorizacion_total = (
            self.estado_actual_inventario["ACUM_VALOR"]
            .sum()
        )

        logger.info(
            f"Capital inmovilizado: ${valorizacion_total:,.2f}"
        )
        
       

        return float(valorizacion_total)
    #*******************************************************************************************
    def calcular_distribucion_abc(self):
        """
        Calcula la distribución ABC en porcentaje del valor total.

        Retorna
        -------
        dict
            {"A": porcentaje, "B": porcentaje, "C": porcentaje}
        """

        # 1. Obtener DataFrame con clasificación ABC
        df_abc = self.calcular_clasificacion_abc()
        
        # 2. Obtener valorización total
        total_valor = self.calcular_valorizacion_total_inventario()

        # 3. Agrupar por categoría y sumar
        resumen = df_abc.groupby("CATEGORIA")["ACUM_VALOR"].sum()

        # 4. Convertir a porcentajes
        distribucion = {
            categoria: (valor / total_valor) * 100
            for categoria, valor in resumen.items()
        }

        return distribucion
    
    # ==========================================================
    # KPI 3 - ALERTAS DE STOCK
    # ==========================================================

    def calcular_alertas_stock(self):
        """
        Calcula la cantidad de repuestos que presentan:

        - Stock bajo (ACUM_CANTIDAD < STOCK_MINIMO)
        - Sobrestock (ACUM_CANTIDAD > LIMITE_MAXIMO)

        Retorna
        -------
        pandas.DataFrame
        """

        logger.info("Calculando KPI 3 - Alertas de Stock.")

        # ======================================================
        # COPIAR EL ESTADO ACTUAL DEL INVENTARIO
        # ======================================================

        datos = self.estado_actual_inventario.copy()
        
        
        # ======================================================
        # CALCULAR ALERTAS DE STOCK BAJO
        # ======================================================
        print("PRUEBA ACTUALIZACION STOCK MINIMO")
        
        # print(
        #             datos.loc[
        #                 datos["ELEM"] == 40003,
        #                 ["ELEM", "ACUM_CANTIDAD", "STOCK_MINIMO"]
        #             ]
        #         )

        total_stock_bajo = (
            datos["ACUM_CANTIDAD"] < datos["STOCK_MINIMO"]
        ).sum()
        
        
        # ======================================================
        # CALCULAR ALERTAS DE SOBRESTOCK
        # ======================================================
        
        datos["LIMITE_MAXIMO"] = datos["STOCK_MINIMO"]*FACTOR_STOCK_MAXIMO

        total_sobrestock = (
            datos["ACUM_CANTIDAD"] > datos["LIMITE_MAXIMO"]
        ).sum()

        # ======================================================
        # CONSTRUIR DATAFRAME RESULTADO
        # ======================================================

        resultado = pd.DataFrame({

            "INDICADOR": [
                "Stock Bajo",
                "Sobrestock"
            ],

            "CANTIDAD": [
                total_stock_bajo,
                total_sobrestock
            ]

        })

        logger.info("KPI 3 calculado correctamente.")

        return resultado
    
    
    
    # ==========================================================
    # KPI 4 - Lista de Ítems con Menor Cobertura (Top 10 de Riesgo Temporal)
    # ==========================================================
    
    def calcular_top10_menor_cobertura(self):
        """
        Calcula los 10 repuestos con menor cantidad de días de
        autonomía (cobertura), según su consumo diario promedio
        y su stock actual, utilizando el Data Warehouse.

        Devuelve un DataFrame con: ELEM, NOMBRE_ELEMENTO, stock_actual,
        consumo_diario_promedio, dias_cobertura.
        """

        logger.info("Calculando Top 10 de menor cobertura (desde el Data Warehouse)...")

        movimientos = self.fact_movimientos[["ELEM", "FECHA", "SALIDAS", "ACUM_CANTIDAD"]].copy()
        movimientos["FECHA"] = pd.to_datetime(movimientos["FECHA"], errors="coerce")

        # =====================================================
        # FASE 1: CONSUMO DIARIO PROMEDIO
        # =====================================================
        resumen = movimientos.groupby("ELEM").agg(
            total_salidas=("SALIDAS", "sum"),
            fecha_min=("FECHA", "min"),
            fecha_max=("FECHA", "max")
        ).reset_index()

        resumen["dias_historial"] = (resumen["fecha_max"] - resumen["fecha_min"]).dt.days

        resumen = resumen[resumen["dias_historial"] > 0].copy()

        resumen["consumo_diario_promedio"] = (
            resumen["total_salidas"] / resumen["dias_historial"]
        )

        resumen = resumen[resumen["consumo_diario_promedio"] >= 1].copy()

        # =====================================================
        # OBTENER STOCK ACTUAL (último ACUM_CANTIDAD de cada producto)
        # =====================================================
        

        ultimo_movimiento = (
            movimientos.reset_index()
            .sort_values(["FECHA", "index"])
            .groupby("ELEM")
            .tail(1)[["ELEM", "ACUM_CANTIDAD"]]
            .rename(columns={"ACUM_CANTIDAD": "stock_actual"})
            )

        resumen = resumen.merge(ultimo_movimiento, on="ELEM", how="inner")
        
        # =====================================================
        # FILTRAR REPUESTOS SIN STOCK (stock_actual = 0)
        # =====================================================
        resumen = resumen[resumen["stock_actual"] > 0].copy()
        
        # =====================================================
        # FASE 2: DÍAS DE COBERTURA
        # =====================================================
        resumen["dias_cobertura"] = (
            resumen["stock_actual"] / resumen["consumo_diario_promedio"]
        )
        resumen["dias_cobertura"] = np.floor(resumen["dias_cobertura"]).astype(int)
        # =====================================================
        # FASE 3: TOP 10 ASCENDENTE (menor cobertura = más crítico)
        # =====================================================
        top10 = resumen.sort_values("dias_cobertura", ascending=True).head(10)

        nombres = self.dim_producto[["ELEM", "NOMBRE_ELEMENTO"]].copy()
        top10 = top10.merge(nombres, on="ELEM", how="left")

        resultado = top10[[
            "ELEM", "NOMBRE_ELEMENTO", "stock_actual",
            "consumo_diario_promedio", "dias_cobertura"
        ]].copy()
        
        # =====================================================
        # REDONDEAR CONSUMO_DIARIO_PROMEDIO PARA VISUALIZACIÓN
        # =====================================================
        resultado["consumo_diario_promedio"] = (
            resultado["consumo_diario_promedio"].round(0).astype(int)
        )

        resultado = resultado.reset_index(drop=True)

        logger.info(f"Top 10 de menor cobertura calculado. {len(resultado)} productos encontrados.")

        return resultado
    
    # =====================================================
    # KPI 5: Costo Proyectado de Reposición diccionario 
    # =====================================================
    def calcular_costo_proyectado_reposicion(self, dias_proyeccion=90):
        """
        Calcula el costo proyectado de reposición del inventario para
        el próximo periodo (por defecto, 90 días / próximo trimestre).

        Paso 1: para cada repuesto, se ajusta una regresión lineal del
        UNITARIO en función del tiempo (V_u,i(t) = beta0 + beta1 * t),
        usando su historial de movimientos en FACT_MOVIMIENTOS.

        Paso 2: se proyecta el valor unitario 'dias_proyeccion' días
        después de la última fecha registrada, y se multiplica por
        Qrep,i para obtener el costo proyectado por producto, y se
        suma sobre todos los repuestos.

        SUPUESTO: Qrep,i se toma como la cantidad actual en inventario
        (ACUM_CANTIDAD del último movimiento). Si prefieres usar el
        promedio histórico de ENTRADAS, dímelo y se ajusta.

        Devuelve:
            {
                "costo_total_proyectado": float,
                "detalle": pd.DataFrame con columnas
                    ELEM, NOMBRE_ELEMENTO, unitario_actual,
                    unitario_proyectado, cantidad_a_reponer, costo_proyectado
            }
        """

        logger.info("Calculando KPI 5 - Costo proyectado de reposición...")

        movimientos = self.fact_movimientos[
            ["ELEM", "FECHA", "UNITARIO", "ACUM_CANTIDAD"]
        ].copy()
        movimientos["FECHA"] = pd.to_datetime(movimientos["FECHA"], errors="coerce")
        movimientos = movimientos.dropna(subset=["FECHA"])

        # =====================================================
        # CONVERTIR FECHA A UNA VARIABLE NUMÉRICA (días desde el inicio)
        # =====================================================
        fecha_referencia = movimientos["FECHA"].min()
        movimientos["t_dias"] = (movimientos["FECHA"] - fecha_referencia).dt.days

        resultados = []

        for elem, grupo in movimientos.groupby("ELEM"):

            grupo = grupo.sort_values("t_dias")

            # Cantidad a reponer: stock actual (último ACUM_CANTIDAD)
            cantidad_a_reponer = grupo["ACUM_CANTIDAD"].iloc[-1]

            puntos_distintos = grupo["t_dias"].nunique()

            # =================================================
            # PASO 1: REGRESIÓN LINEAL DEL PRECIO EN EL TIEMPO
            # =================================================
            if puntos_distintos >= 2:
                beta1, beta0 = np.polyfit(grupo["t_dias"], grupo["UNITARIO"], 1)
            else:
                # Sin suficientes puntos para estimar tendencia:
                # se asume precio constante (pendiente = 0)
                beta1 = 0.0
                beta0 = grupo["UNITARIO"].iloc[-1]

            t_futuro = grupo["t_dias"].iloc[-1] + dias_proyeccion
            unitario_proyectado = beta0 + beta1 * t_futuro

            # No permitir precios proyectados negativos
            unitario_proyectado = max(unitario_proyectado, 0)

            # =================================================
            # PASO 2: COSTO PROYECTADO POR PRODUCTO
            # =================================================
            costo_proyectado = unitario_proyectado * cantidad_a_reponer

            resultados.append({
                "ELEM": elem,
                "unitario_actual": grupo["UNITARIO"].iloc[-1],
                "unitario_proyectado": unitario_proyectado,
                "cantidad_a_reponer": cantidad_a_reponer,
                "costo_proyectado": costo_proyectado
            })

        detalle = pd.DataFrame(resultados)

        # # Agregar nombre del producto
        # nombres = self.dim_producto[["ELEM", "NOMBRE_ELEMENTO"]].copy()
        # detalle = detalle.merge(nombres, on="ELEM", how="left")

        # detalle = detalle[[
        #     "ELEM", "NOMBRE_ELEMENTO", "unitario_actual",
        #     "unitario_proyectado", "cantidad_a_reponer", "costo_proyectado"
        # ]].reset_index(drop=True)

        # # =====================================================
        # # SUMA SOBRE TODOS LOS REPUESTOS (Cproy)
        # # =====================================================
        # costo_total_proyectado = detalle["costo_proyectado"].sum()
        # costo_total_proyectado =f"{costo_total_proyectado:,.2f}"

        # logger.info(
        #     f"KPI 5 calculado correctamente. "
        #     f"Costo total proyectado: {costo_total_proyectado}"
        # )

        # return {
        #     "costo_total_proyectado": costo_total_proyectado,
        #     "detalle": detalle
        # }
                
         # =====================================================
        # AGREGAR NOMBRE DEL PRODUCTO
        # =====================================================

        nombres = self.dim_producto[
            ["ELEM", "NOMBRE_ELEMENTO"]
        ].copy()

        detalle = detalle.merge(
            nombres,
            on="ELEM",
            how="left"
        )

        # =====================================================
        # AGREGAR CATEGORÍA ABC
        # =====================================================

        clasificacion = self.estado_actual_inventario[
            ["ELEM", "CATEGORIA"]
        ].copy()

        detalle = detalle.merge(
            clasificacion,
            on="ELEM",
            how="left"
        )

        # =====================================================
        # COSTO ACTUAL POR PRODUCTO
        # =====================================================

        detalle["costo_actual"] = (
            detalle["unitario_actual"] *
            detalle["cantidad_a_reponer"]
        )

        # =====================================================
        # ORGANIZAR COLUMNAS
        # =====================================================

        detalle = detalle[
            [
                "ELEM",
                "NOMBRE_ELEMENTO",
                "CATEGORIA",
                "unitario_actual",
                "unitario_proyectado",
                "cantidad_a_reponer",
                "costo_actual",
                "costo_proyectado"
            ]
        ].reset_index(drop=True)

        # =====================================================
        # DATOS PARA LA GRÁFICA
        # =====================================================

        grafica = (
            detalle
            .groupby("CATEGORIA", as_index=False)
            .agg(
                costo_actual=("costo_actual", "sum"),
                costo_proyectado=("costo_proyectado", "sum")
            )
        )

        # Orden A, B, C

        orden = {
            "A": 1,
            "B": 2,
            "C": 3
        }

        grafica["ORDEN"] = grafica["CATEGORIA"].map(orden)

        grafica = (
            grafica
            .sort_values("ORDEN")
            .drop(columns="ORDEN")
            .reset_index(drop=True)
        )

        # =====================================================
        # SUMA TOTAL
        # =====================================================

        costo_total_proyectado = detalle["costo_proyectado"].sum()

        costo_total_proyectado = f"{costo_total_proyectado:,.2f}"

        logger.info(
            f"KPI 5 calculado correctamente. "
            f"Costo total proyectado: {costo_total_proyectado}"
        )

        return {
            "costo_total_proyectado": costo_total_proyectado,
            "detalle": detalle,
            "grafica": grafica
        }       
    # =====================================================            
    #KPI 6: Indicador de Obsolescencia Predictivo diccionario
    # =====================================================     
    def calcular_indicador_obsolescencia(self, fecha_referencia=None):
        """
        Calcula la probabilidad de obsolescencia de cada repuesto,
        según su tiempo sin movimiento (T_sin, en meses) y su
        categoría ABC.

        Reglas por categoría (meses sin movimiento):
            Categoría A: Baja <=1 | Media (1, 12) | Alta >=12
            Categoría B: Baja <=1 | Media (1, 6)  | Alta >=6
            Categoría C (y sin categoría): Baja <=1 | Media (1, 6) | Alta >=6

        NOTA: el rango original dejaba un vacío entre 1 y 3 meses;
        aquí se resolvió extendiendo "Media" desde >1 mes hasta el
        umbral de "Alta" de cada categoría.

        fecha_referencia: fecha usada como "hoy" para calcular T_sin.
        Si no se especifica, se usa la fecha máxima registrada en
        FACT_MOVIMIENTOS.

        Devuelve:
            {
                "cantidad_alta_probabilidad": int,
                "detalle": pd.DataFrame con columnas
                    ELEM, NOMBRE_ELEMENTO, CATEGORIA,
                    meses_sin_movimiento, probabilidad_obsolescencia
            }
        """

        logger.info("Calculando KPI 6 - Indicador de obsolescencia predictivo...")

        movimientos = self.fact_movimientos[["ELEM", "FECHA"]].copy()
        movimientos["FECHA"] = pd.to_datetime(movimientos["FECHA"], errors="coerce")
        movimientos = movimientos.dropna(subset=["FECHA"])

        if fecha_referencia is None:
            fecha_referencia = movimientos["FECHA"].max()
        else:
            fecha_referencia = pd.to_datetime(fecha_referencia)

        # =====================================================
        # ÚLTIMO MOVIMIENTO POR PRODUCTO
        # =====================================================
        ultimo_movimiento = (
            movimientos.groupby("ELEM")["FECHA"]
            .max()
            .reset_index()
            .rename(columns={"FECHA": "ultima_fecha"})
        )

        ultimo_movimiento["meses_sin_movimiento"] = (
            (fecha_referencia - ultimo_movimiento["ultima_fecha"]).dt.days / 30
        )

        # =====================================================
        # UNIR CON CATEGORÍA (DIM_PRODUCTO)
        # =====================================================
        productos = self.dim_producto[["ELEM", "NOMBRE_ELEMENTO", "CATEGORIA"]].copy()
        datos = productos.merge(ultimo_movimiento, on="ELEM", how="inner")

        # =====================================================
        # FUNCIÓN f(): ASIGNA PROBABILIDAD SEGÚN CATEGORÍA Y T_sin
        # =====================================================
        def clasificar_obsolescencia(fila):
            t_sin = fila["meses_sin_movimiento"]
            categoria = fila["CATEGORIA"]

            if categoria == "A":
                umbral_alta = 3#12
            elif categoria == "B":
                umbral_alta =2# 6
            else:
                # Categoría C, o cualquier valor no reconocido
                # (ej. "SIN CATEGORIA"), se trata con el criterio
                # más conservador (igual que C).
                umbral_alta = 6

            if t_sin <= 1:
                return "Baja"
            elif t_sin < umbral_alta:
                return "Media"
            else:
                return "Alta"

        datos["probabilidad_obsolescencia"] = datos.apply(clasificar_obsolescencia, axis=1)

        # =====================================================
        # ADVERTIR SOBRE CATEGORÍAS NO RECONOCIDAS
        # =====================================================
        categorias_validas = {"A", "B", "C"}
        categorias_encontradas = set(datos["CATEGORIA"].unique())
        no_reconocidas = categorias_encontradas - categorias_validas

        if no_reconocidas:
            logger.warning(
                f"Se encontraron categorías no reconocidas ({no_reconocidas}); "
                f"se evaluaron con el criterio de categoría C."
            )

        # detalle = datos[[
        #     "ELEM", "NOMBRE_ELEMENTO", "CATEGORIA",
        #     "meses_sin_movimiento", "probabilidad_obsolescencia"
        # ]].sort_values("meses_sin_movimiento", ascending=False).reset_index(drop=True)

        # cantidad_alta_probabilidad = (detalle["probabilidad_obsolescencia"] == "Alta").sum()

        # logger.info(
        #     f"KPI 6 calculado correctamente. "
        #     f"Repuestos con alta probabilidad de obsolescencia: {cantidad_alta_probabilidad}"
        # )

        # return {
        #     "cantidad_alta_probabilidad": int(cantidad_alta_probabilidad),
        #     "detalle": detalle
        # }
        # =====================================================
        # ORGANIZAR DETALLE
        # =====================================================

        detalle = datos[
            [
                "ELEM",
                "NOMBRE_ELEMENTO",
                "CATEGORIA",
                "meses_sin_movimiento",
                "probabilidad_obsolescencia"
            ]
        ].sort_values(
            "meses_sin_movimiento",
            ascending=False
        ).reset_index(drop=True)

        # =====================================================
        # REPUESTOS CON ALTA PROBABILIDAD
        # =====================================================

        detalle_alta = detalle[
            detalle["probabilidad_obsolescencia"] == "Alta"
        ].copy()

        cantidad_alta_probabilidad = len(detalle_alta)

        # =====================================================
        # PORCENTAJE DEL INVENTARIO
        # =====================================================

        total_repuestos = len(detalle)

        porcentaje_alta_probabilidad = (
            cantidad_alta_probabilidad / total_repuestos * 100
            if total_repuestos > 0 else 0
        )

        # =====================================================
        # DATOS PARA LA TARJETA (ABC)
        # =====================================================

        abc = (
            detalle_alta
            .groupby("CATEGORIA")
            .size()
            .reindex(["A", "B", "C"], fill_value=0)
        )

        grafica = {
            "A": int(abc["A"]),
            "B": int(abc["B"]),
            "C": int(abc["C"])
        }

        logger.info(
            f"KPI 6 calculado correctamente. "
            f"Alta probabilidad: {cantidad_alta_probabilidad}"
        )

        return {

            "cantidad_alta_probabilidad": int(cantidad_alta_probabilidad),

            "porcentaje": round(
                porcentaje_alta_probabilidad,
                2
            ),

            "grafica": grafica,

            "detalle": detalle

        }
    
    #==========================================================0
    #KPI 7: Tendencia del Consumo-diccionario
    #==============================================================
    def calcular_tendencia_consumo(self, umbral_estable=0.05) :
        """
        Estima la tendencia de consumo (creciente, decreciente o estable)
        de cada repuesto, mediante una regresión lineal de SALIDAS en
        función del tiempo.

        TC_i se determina según la pendiente (beta) de la regresión:
            beta > umbral_estable   -> "Creciente"
            beta < -umbral_estable  -> "Decreciente"
            |beta| <= umbral_estable -> "Estable"

        Productos con menos de MINIMO_PUNTOS_TENDENCIA fechas distintas
        de historial se clasifican como "Sin datos suficientes", en vez
        de forzarlos a "Estable", para no mezclar consumo genuinamente
        estable con la simple ausencia de datos.

        umbral_estable: tolerancia para considerar la pendiente
        "aproximadamente cero". Por defecto 0.05 (unidades por día).

        Devuelve:
            {
                "creciente": int,
                "decreciente": int,
                "estable": int,
                "sin_datos_suficientes": int,
                "detalle": pd.DataFrame con columnas
                    ELEM, NOMBRE_ELEMENTO, pendiente_beta, tendencia
            }
        """

        logger.info("Calculando KPI 7 - Tendencia del consumo...")

        movimientos = self.fact_movimientos[["ELEM", "FECHA", "SALIDAS"]].copy()
        movimientos["FECHA"] = pd.to_datetime(movimientos["FECHA"], errors="coerce")
        movimientos = movimientos.dropna(subset=["FECHA"])

        fecha_referencia = movimientos["FECHA"].min()
        movimientos["t_dias"] = (movimientos["FECHA"] - fecha_referencia).dt.days

        resultados = []

        for elem, grupo in movimientos.groupby("ELEM"):

            grupo = grupo.sort_values("t_dias")

            puntos_distintos = grupo["t_dias"].nunique()

            # =================================================
            # REGRESIÓN LINEAL DE SALIDAS EN FUNCIÓN DEL TIEMPO
            # =================================================
            if puntos_distintos >= MINIMO_PUNTOS_TENDENCIA:

                beta, intercepto = np.polyfit(grupo["t_dias"], grupo["SALIDAS"], 1)

                if beta > umbral_estable:
                    tendencia = "Creciente"
                elif beta < -umbral_estable:
                    tendencia = "Decreciente"
                else:
                    tendencia = "Estable"

            else:
                # Sin suficientes puntos para estimar una tendencia confiable
                beta = np.nan
                tendencia = "Sin datos suficientes"

            resultados.append({
                "ELEM": elem,
                "pendiente_beta": beta,
                "tendencia": tendencia
            })

        detalle = pd.DataFrame(resultados)

        # Agregar nombre del producto
        nombres = self.dim_producto[["ELEM", "NOMBRE_ELEMENTO"]].copy()
        detalle = detalle.merge(nombres, on="ELEM", how="left")

        detalle = detalle[[
            "ELEM", "NOMBRE_ELEMENTO", "pendiente_beta", "tendencia"
        ]].sort_values("pendiente_beta", ascending=False).reset_index(drop=True)

        conteo = detalle["tendencia"].value_counts()

        logger.info(
            f"KPI 7 calculado correctamente. "
            f"Creciente: {conteo.get('Creciente', 0)} | "
            f"Decreciente: {conteo.get('Decreciente', 0)} | "
            f"Estable: {conteo.get('Estable', 0)} | "
            f"Sin datos suficientes: {conteo.get('Sin datos suficientes', 0)}"
        )

        return {
            "creciente": int(conteo.get("Creciente", 0)),
            "decreciente": int(conteo.get("Decreciente", 0)),
            "estable": int(conteo.get("Estable", 0)),
            "sin_datos_suficientes": int(conteo.get("Sin datos suficientes", 0)),
            "detalle": detalle
        }
        
    #========================================    
    #KPI 8: Pronóstico de Consumo Mensual - diccionario
    #========================================
    def calcular_pronostico_consumo_mensual(self):
        """
        Estima la cantidad de unidades que se espera consumir de cada
        repuesto durante el próximo mes, mediante una regresión lineal
        sobre el historial mensual de SALIDAS.

        PCM_i = Y_hat(i, t+1), proyectado a partir de la tendencia
        mensual histórica de consumo de cada repuesto.

        Productos con menos de MINIMO_MESES_PRONOSTICO meses distintos
        de historial se excluyen del pronóstico numérico y se marcan
        como "Sin datos suficientes".

        Devuelve:
            {
                "total_pronosticado": float,
                "productos_sin_datos_suficientes": int,
                "detalle": pd.DataFrame con columnas
                    ELEM, NOMBRE_ELEMENTO, meses_historial,
                    pronostico_proximo_mes
            }
        """

        logger.info("Calculando KPI 8 - Pronóstico de consumo mensual...")

        movimientos = self.fact_movimientos[["ELEM", "FECHA", "SALIDAS"]].copy()
        movimientos["FECHA"] = pd.to_datetime(movimientos["FECHA"], errors="coerce")
        movimientos = movimientos.dropna(subset=["FECHA"])

        # =====================================================
        # AGRUPAR CONSUMO POR MES (periodo YYYY-MM)
        # =====================================================
        movimientos["periodo_mes"] = movimientos["FECHA"].dt.to_period("M")

        consumo_mensual = (
            movimientos.groupby(["ELEM", "periodo_mes"])["SALIDAS"]
            .sum()
            .reset_index()
        )

        # =====================================================
        # CONVERTIR EL PERIODO A UN ÍNDICE NUMÉRICO SECUENCIAL
        # (necesario para ajustar la regresión lineal)
        # =====================================================
        consumo_mensual = consumo_mensual.sort_values(["ELEM", "periodo_mes"])
        consumo_mensual["indice_mes"] = (
            consumo_mensual.groupby("ELEM").cumcount()
        )

        resultados = []

        for elem, grupo in consumo_mensual.groupby("ELEM"):

            meses_historial = grupo["periodo_mes"].nunique()

            # =================================================
            # REGRESIÓN LINEAL: SALIDAS MENSUALES vs. ÍNDICE DE MES
            # =================================================
            if meses_historial >= MINIMO_MESES_PRONOSTICO:

                beta, intercepto = np.polyfit(
                    grupo["indice_mes"], grupo["SALIDAS"], 1
                )

                siguiente_indice = grupo["indice_mes"].max() + 1
                pronostico = beta * siguiente_indice + intercepto

                # No permitir pronósticos negativos
                pronostico = max(pronostico, 0)

            else:
                pronostico = np.nan

            resultados.append({
                "ELEM": elem,
                "meses_historial": meses_historial,
                "pronostico_proximo_mes": pronostico
            })

        detalle = pd.DataFrame(resultados)

        # Agregar nombre del producto
        nombres = self.dim_producto[["ELEM", "NOMBRE_ELEMENTO"]].copy()
        detalle = detalle.merge(nombres, on="ELEM", how="left")

        detalle = detalle[[
            "ELEM", "NOMBRE_ELEMENTO", "meses_historial", "pronostico_proximo_mes"
        ]].sort_values("pronostico_proximo_mes", ascending=False).reset_index(drop=True)

        productos_sin_datos = detalle["pronostico_proximo_mes"].isna().sum()
        total_pronosticado = detalle["pronostico_proximo_mes"].sum(skipna=True)

        logger.info(
            f"KPI 8 calculado correctamente. "
            f"Total pronosticado próximo mes: {total_pronosticado:,.2f} unidades. "
            f"Productos sin datos suficientes: {productos_sin_datos}"
        )

        return {
            "total_pronosticado": float(total_pronosticado),
            "productos_sin_datos_suficientes": int(productos_sin_datos),
            "detalle": detalle
        }
        
    #=====================================================0    
    #KPI 9: Pronóstico de Agotamiento del Inventario -diccionario
    #======================================================
    def calcular_pronostico_agotamiento(self, umbral_critico_dias=30,pronostico_previo=None):
        """
        Estima los días que le quedan a cada repuesto antes de agotar
        su inventario, con base en el stock actual y el consumo diario
        proyectado (derivado del pronóstico de consumo mensual, KPI 8).

        PAI_i = Stock_actual_i / CP_i
        CP_i = pronostico_proximo_mes_i / DIAS_MES_APROX

        Casos especiales:
            - CP_i = 0 (no se proyecta consumo)  -> "Sin riesgo" (PAI = inf)
            - Sin pronóstico disponible (KPI 8)  -> "Sin datos suficientes"

        umbral_critico_dias: días por debajo de los cuales un producto
        se considera crítico (por defecto 30).

        Devuelve:
            {
                "cantidad_criticos": int,
                "detalle": pd.DataFrame con columnas
                    ELEM, NOMBRE_ELEMENTO, stock_actual,
                    consumo_diario_proyectado, dias_agotamiento, estado
            }
        """

        logger.info("Calculando KPI 9 - Pronóstico de agotamiento del inventario...")
        
        # =====================================================
        # REUTILIZAR EL PRONÓSTICO MENSUAL YA CALCULADO (KPI 8)
        # Si no se pasa uno ya calculado, se calcula aquí.
        # =====================================================
        resultado_kpi8 = pronostico_previo if pronostico_previo is not None else self.calcular_pronostico_consumo_mensual()

        pronostico = resultado_kpi8["detalle"][
            ["ELEM", "pronostico_proximo_mes"]
        ].copy()
        
        
        # =====================================================
        # OBTENER STOCK ACTUAL (último ACUM_CANTIDAD por producto)
        # =====================================================
        movimientos = self.fact_movimientos[["ELEM", "FECHA", "ACUM_CANTIDAD"]].copy()
        movimientos["FECHA"] = pd.to_datetime(movimientos["FECHA"], errors="coerce")
        
        

        stock_actual = (
            movimientos.sort_values("FECHA")
            .groupby("ELEM")
            .tail(1)[["ELEM", "ACUM_CANTIDAD"]]
            .rename(columns={"ACUM_CANTIDAD": "stock_actual"})
        )

        datos = pronostico.merge(stock_actual, on="ELEM", how="inner")
        
        # =====================================================
        # NUEVO: FILTRAR ÚNICAMENTE PRODUCTOS CON STOCK MAYOR A 0
        # =====================================================
        datos = datos[datos["stock_actual"] > 0].copy()

        # =====================================================
        # CONSUMO DIARIO PROYECTADO
        # =====================================================
        datos["consumo_diario_proyectado"] = (
            datos["pronostico_proximo_mes"] / DIAS_MES_APROX
        )

        # =====================================================
        # CLASIFICAR CADA PRODUCTO Y CALCULAR DÍAS DE AGOTAMIENTO
        # =====================================================
        def calcular_fila(fila):
            if pd.isna(fila["pronostico_proximo_mes"]):
                return pd.Series({"dias_agotamiento": np.nan, "estado": "Sin datos suficientes"})

            if fila["consumo_diario_proyectado"] == 0:
                return pd.Series({"dias_agotamiento": np.inf, "estado": "Sin riesgo (sin consumo proyectado)"})

            dias = fila["stock_actual"] / fila["consumo_diario_proyectado"]
            #redondeo hacia abajo=======================================================
            dias_entero =int(round(dias))
            estado = "Crítico" if dias_entero <= umbral_critico_dias else "Normal"
            return pd.Series({"dias_agotamiento": dias_entero, "estado": estado})

        # se cambio por esto:datos[["dias_agotamiento", "estado"]] = datos.apply(calcular_fila, axis=1)
        # Si tras el filtro no quedan filas, se evita un error en la aplicación
        if datos.empty:
            datos["dias_agotamiento"] = pd.Series(dtype=float)
            datos["estado"] = pd.Series(dtype=str)
        else:
            datos[["dias_agotamiento", "estado"]] = datos.apply(calcular_fila, axis=1)
            
        # Agregar nombre del producto
        nombres = self.dim_producto[["ELEM", "NOMBRE_ELEMENTO"]].copy()
        datos = datos.merge(nombres, on="ELEM", how="left")

        detalle = datos[[
            "ELEM", "NOMBRE_ELEMENTO", "stock_actual",
            "consumo_diario_proyectado", "dias_agotamiento", "estado"
        ]].sort_values("dias_agotamiento", ascending=True, na_position="last").reset_index(drop=True)

        cantidad_criticos = (detalle["estado"] == "Crítico").sum()

        logger.info(
            f"KPI 9 calculado correctamente. "
            f"Productos críticos (<= {umbral_critico_dias} días): {cantidad_criticos}"
        )

        return {
            "cantidad_criticos": int(cantidad_criticos),
            "detalle": detalle
        }
    #=======================================    
    #KPI 10: Nivel de Inventario Proyectado-dicionario
    #=========================================
    def calcular_nivel_inventario_proyectado(self,pronostico_previo=None):
        """
        Estima el nivel de inventario que tendrá cada repuesto al
        finalizar el siguiente período, considerando el stock actual
        y el consumo proyectado (derivado del pronóstico de consumo
        mensual, KPI 8).

        NIP_i = S_i - CP_i

        Interpretación:
            NIP > umbral            -> "Suficiente"
            -umbral <= NIP <= umbral -> "Justo"
            NIP < -umbral           -> "Riesgo de desabastecimiento"

        Productos sin pronóstico disponible (KPI 8) se marcan como
        "Sin datos suficientes".

        Devuelve:
            {
                "cantidad_riesgo_desabastecimiento": int,
                "detalle": pd.DataFrame con columnas
                    ELEM, NOMBRE_ELEMENTO, stock_actual,
                    consumo_proyectado, nivel_inventario_proyectado, estado
            }
        """

        logger.info("Calculando KPI 10 - Nivel de inventario proyectado...")
        
        resultado_kpi8 = pronostico_previo if pronostico_previo is not None else self.calcular_pronostico_consumo_mensual()

        pronostico = resultado_kpi8["detalle"][
            ["ELEM", "pronostico_proximo_mes"]
        ].copy()


        # =====================================================
        # REUTILIZAR EL PRONÓSTICO MENSUAL YA CALCULADO (KPI 8)
        # =====================================================
        #resultado_kpi8 = self.calcular_pronostico_consumo_mensual()
        pronostico = resultado_kpi8["detalle"][
            ["ELEM", "pronostico_proximo_mes"]
        ].copy()

        # =====================================================
        # OBTENER STOCK ACTUAL (último ACUM_CANTIDAD por producto)
        # =====================================================
        movimientos = self.fact_movimientos[["ELEM", "FECHA", "ACUM_CANTIDAD"]].copy()
        movimientos["FECHA"] = pd.to_datetime(movimientos["FECHA"], errors="coerce")

        stock_actual = (
            movimientos.sort_values("FECHA")
            .groupby("ELEM")
            .tail(1)[["ELEM", "ACUM_CANTIDAD"]]
            .rename(columns={"ACUM_CANTIDAD": "stock_actual"})
        )

        datos = pronostico.merge(stock_actual, on="ELEM", how="inner")

        # =====================================================
        # NIVEL DE INVENTARIO PROYECTADO
        # =====================================================
        datos["nivel_inventario_proyectado"] = (
            datos["stock_actual"] - datos["pronostico_proximo_mes"]
        )

        def clasificar(fila):
            if pd.isna(fila["pronostico_proximo_mes"]):
                return "Sin datos suficientes"

            nip = fila["nivel_inventario_proyectado"]

            if nip > UMBRAL_NIP_CERO:
                return "Suficiente"
            elif nip < -UMBRAL_NIP_CERO:
                return "Riesgo de desabastecimiento"
            else:
                return "Justo"

        datos["estado"] = datos.apply(clasificar, axis=1)

        # Agregar nombre del producto
        nombres = self.dim_producto[["ELEM", "NOMBRE_ELEMENTO"]].copy()
        datos = datos.merge(nombres, on="ELEM", how="left")

        detalle = datos.rename(
            columns={"pronostico_proximo_mes": "consumo_proyectado"}
        )[[
            "ELEM", "NOMBRE_ELEMENTO", "stock_actual",
            "consumo_proyectado", "nivel_inventario_proyectado", "estado"
        ]].sort_values("nivel_inventario_proyectado", ascending=True).reset_index(drop=True)

        cantidad_riesgo = (detalle["estado"] == "Riesgo de desabastecimiento").sum()

        logger.info(
            f"KPI 10 calculado correctamente. "
            f"Productos en riesgo de desabastecimiento: {cantidad_riesgo}"
        )

        return {
            "cantidad_riesgo_desabastecimiento": int(cantidad_riesgo),
            "detalle": detalle
        }
    
    # ==========================================================
    # TABLA REPUESTOS REPRESENTATIVOS ABC
    # ==========================================================

    def obtener_tabla_repuestos_abc(self):
        """
        Retorna una tabla con:

        - Top 10 repuestos categoría A.
        - Top 10 repuestos categoría B.
        - Top 5 repuestos categoría C.

        Columnas:
            - NOMBRE_ELEMENTO
            - CATEGORIA
            - ACUM_CANTIDAD
        """

        logger.info("Construyendo tabla de repuestos representativos ABC...")
        
        

        df = self.calcular_clasificacion_abc()
        
        # -----------------------------
        # Categoría A
        # -----------------------------
        categoria_a = (
            df[df["CATEGORIA"] == "A"]
            .sort_values("ACUM_CANTIDAD")
            .head(20)
        )

        # -----------------------------
        # Categoría B
        # -----------------------------
        categoria_b = (
            df[df["CATEGORIA"] == "B"]
            .sort_values("ACUM_CANTIDAD")
            .head(20)
        )

        # -----------------------------
        # Categoría C
        # -----------------------------
        categoria_c = (
            df[df["CATEGORIA"] == "C"]
            .sort_values("ACUM_CANTIDAD")
            .head(20)
        )

        # -----------------------------
        # Unir resultados
        # -----------------------------
        resultado = pd.concat(
            [
                categoria_a,
                categoria_b,
                categoria_c
            ],
            ignore_index=True
        )

        # -----------------------------
        # Seleccionar columnas
        # -----------------------------
        resultado = resultado[
            [
                "NOMBRE_ELEMENTO",
                "CATEGORIA",
                "ACUM_CANTIDAD"
            ]
        ].rename(
            columns={
                "NOMBRE_ELEMENTO": "REPUESTO",
                "ACUM_CANTIDAD": "STOCK"
            }
        )
        
        # -----------------------------
        # Ordenar de menor a mayor stock
        # -----------------------------
        resultado = resultado.sort_values("STOCK", ascending=True).reset_index(drop=True)


        logger.info(
            f"Tabla ABC construida correctamente. "
            f"Registros: {len(resultado)}"
        )
        
        return resultado    
        


            