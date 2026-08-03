import customtkinter as ctk
from CTkTable import CTkTable
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure



class DashboardView(ctk.CTkFrame):
    """
    Vista Dashboard.

    En esta vista se mostrarán los gráficos e indicadores
    principales del sistema.
    """

    def __init__(self, parent, controlador):

        super().__init__(parent)

        # =====================================================
        # REFERENCIAS
        # =====================================================

        self.controlador = controlador

        # =====================================================
        # CONFIGURACIÓN DEL FRAME
        # =====================================================

        self.configure(
            fg_color="#F3F5F9"
        )

        # =====================================================
        # GRID PRINCIPAL
        # =====================================================

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # =====================================================
        # CONSTRUIR INTERFAZ
        # =====================================================

        self.crear_titulo()
        self.crear_contenedores()
        self.crear_tabla_menor_cobertura()
        self.crear_grafica_costo_reposicion()
        self.crear_indicador_obsolescencia()
        self.crear_tendencia_consumo()

    # =====================================================
    # TÍTULO
    # =====================================================

    def crear_titulo(self):

        titulo = ctk.CTkLabel(
            self,
            text="DASHBOARD ANALITICO",
            font=("Arial", 24, "bold"),
            text_color="#183A8F"
        )

        titulo.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=25,
            pady=(20,15)
        )
        
    #=======================================================
    # CONTENEDORES
    #=======================================================

    def crear_contenedores(self):

        #---------------------------------------------------
        # KPI 4
        #---------------------------------------------------

        self.frame_kpi4 = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=8
        )

        self.frame_kpi4.grid(
            row=1,
            column=0,
            padx=(25,10),
            pady=(0,15),
            sticky="nsew"
        )

        ctk.CTkLabel(
            self.frame_kpi4,
            text="TOP 10 MENOR COBERTURA",
            font=("Arial",15,"bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        #---------------------------------------------------
        # KPI 5
        #---------------------------------------------------

        self.frame_kpi5 = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=8
        )

        self.frame_kpi5.grid(
            row=1,
            column=1,
            padx=(10,25),
            pady=(0,15),
            sticky="nsew"
        )

        ctk.CTkLabel(
            self.frame_kpi5,
            text="COSTO PROYECTADO DE REPOSICIÓN",
            font=("Arial",15,"bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        #---------------------------------------------------
        # KPI 6
        #---------------------------------------------------

        self.frame_kpi6 = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=8
        )

        self.frame_kpi6.grid(
            row=2,
            column=0,
            padx=(25,10),
            pady=(0,20),
            sticky="nsew"
        )

        ctk.CTkLabel(
            self.frame_kpi6,
            text="INDICADOR DE OBSOLESCENCIA PREDICTIVO",
            font=("Arial",15,"bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        #---------------------------------------------------
        # KPI 7
        #---------------------------------------------------

        self.frame_kpi7 = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=8
        )

        self.frame_kpi7.grid(
            row=2,
            column=1,
            padx=(10,25),
            pady=(0,20),
            sticky="nsew"
        )

        ctk.CTkLabel(
            self.frame_kpi7,
            text="TENDENCIA DEL CONSUMO",
            font=("Arial",15,"bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )
        
        
    # =====================================================
    # TABLA TOP 10 MENOR COBERTURA
    # =====================================================
    def crear_tabla_menor_cobertura(self):
        """
        Muestra el Top 10 de ítems con menor cobertura.
        """

        dataframe = self.controlador.kpi4_menor_cobertura

        encabezados = [
            "Código",
            "Repuesto",
            "Stock",
            "Consumo",
            "Cobertura"
        ]

        datos = [encabezados]

        if dataframe is not None and not dataframe.empty:

            for _, fila in dataframe.iterrows():

                datos.append([
                    fila["ELEM"],
                    fila["NOMBRE_ELEMENTO"],
                    int(fila["stock_actual"]),
                    int(round(fila["consumo_diario_promedio"])),
                    round(fila["dias_cobertura"], 1)
                ])

        self.tabla_top10 = CTkTable(
            master=self.frame_kpi4,
            values=datos
        )

        self.tabla_top10.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0,15)
        )
        
    #==============================================================
    # GRAFICO COSTO REPOSICION
    #===============================================================
    
    def crear_grafica_costo_reposicion(self):
        """
        Gráfico de barras:
        Costo Actual vs Costo Proyectado
        agrupado por categoría ABC.
        """

        datos = self.controlador.kpi5_costo_reposicion["grafica"]
        #print(self.controlador.kpi5_costo_reposicion["grafica"])

        categorias = datos["CATEGORIA"]

        costo_actual = datos["costo_actual"]

        costo_proyectado = datos["costo_proyectado"]

        #==========================================
        # FIGURA
        #==========================================

        figura = plt.Figure(
            figsize=(5.5,3.8),
            dpi=100
        )

        ax = figura.add_subplot(111)

        ancho = 0.35

        posiciones = range(len(categorias))

        #==========================================
        # BARRAS
        #==========================================

        ax.bar(
            [i-ancho/2 for i in posiciones],
            costo_actual,
            width=ancho,
            label="Costo Actual"
        )

        ax.bar(
            [i+ancho/2 for i in posiciones],
            costo_proyectado,
            width=ancho,
            label="Costo Proyectado"
        )

        #==========================================
        # CONFIGURACIÓN
        #==========================================

        ax.set_xticks(list(posiciones))

        ax.set_xticklabels(categorias)

        ax.set_ylabel("Costo")

        ax.set_xlabel("Categoría ABC")

        ax.set_title(
            "Costo Actual vs Proyectado"
        )

        ax.legend()

        ax.grid(
            axis="y",
            linestyle="--",
            alpha=0.4
        )

        figura.tight_layout()

        #==========================================
        # MOSTRAR EN TKINTER
        #==========================================

        canvas = FigureCanvasTkAgg(
            figura,
            master=self.frame_kpi5
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0,10)
        )   

   
    # =====================================================
    # KPI 6 - INDICADOR DE OBSOLESCENCIA
    # =====================================================
    def crear_indicador_obsolescencia(self):
        """
        Muestra el indicador de obsolescencia predictivo.
        """

        datos = self.controlador.kpi6_obsolescencia

        cantidad = datos["cantidad_alta_probabilidad"]
        porcentaje = datos["porcentaje"]

        categoria_a = datos["grafica"]["A"]
        categoria_b = datos["grafica"]["B"]
        categoria_c = datos["grafica"]["C"]

        # =====================================================
        # TARJETA PRINCIPAL
        # =====================================================

        self.frame_alerta = ctk.CTkFrame(
            self.frame_kpi6,
            fg_color="#FFE8E8",
            corner_radius=8
        )

        self.frame_alerta.pack(
            fill="x",
            padx=15,
            pady=(10,15)
        )

        ctk.CTkLabel(
            self.frame_alerta,
            text="⚠ REPUESTOS EN RIESGO",
            font=("Arial",16,"bold"),
            text_color="#B00020"
        ).pack(
            pady=(15,5)
        )

        ctk.CTkLabel(
            self.frame_alerta,
            text=str(cantidad),
            font=("Arial",34,"bold"),
            text_color="#D32F2F"
        ).pack()

        ctk.CTkLabel(
            self.frame_alerta,
            text=f"{porcentaje:.2f}% del inventario",
            font=("Arial",14)
        ).pack(
            pady=(5,15)
        )

        # =====================================================
        # TÍTULO DISTRIBUCIÓN
        # =====================================================

        ctk.CTkLabel(
            self.frame_kpi6,
            text="Distribución por Categoría ABC",
            font=("Arial",14,"bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(5,10)
        )

        # =====================================================
        # CONTENEDOR ABC
        # =====================================================

        self.frame_abc = ctk.CTkFrame(
            self.frame_kpi6,
            fg_color="transparent"
        )

        self.frame_abc.pack(
            fill="x",
            padx=15
        )

        self.frame_abc.grid_columnconfigure((0,1,2), weight=1)

        # =====================================================
        # A
        # =====================================================

        frame_a = ctk.CTkFrame(self.frame_abc)

        frame_a.grid(
            row=0,
            column=0,
            padx=5,
            sticky="nsew"
        )

        ctk.CTkLabel(
            frame_a,
            text="Categoría A",
            font=("Arial",13,"bold")
        ).pack(
            pady=(10,5)
        )

        ctk.CTkLabel(
            frame_a,
            text=str(categoria_a),
            font=("Arial",28,"bold"),
            text_color="#D32F2F"
        ).pack(
            pady=(0,10)
        )

        # =====================================================
        # B
        # =====================================================

        frame_b = ctk.CTkFrame(self.frame_abc)

        frame_b.grid(
            row=0,
            column=1,
            padx=5,
            sticky="nsew"
        )

        ctk.CTkLabel(
            frame_b,
            text="Categoría B",
            font=("Arial",13,"bold")
        ).pack(
            pady=(10,5)
        )

        ctk.CTkLabel(
            frame_b,
            text=str(categoria_b),
            font=("Arial",28,"bold"),
            text_color="#F57C00"
        ).pack(
            pady=(0,10)
        )

        # =====================================================
        # C
        # =====================================================

        frame_c = ctk.CTkFrame(self.frame_abc)

        frame_c.grid(
            row=0,
            column=2,
            padx=5,
            sticky="nsew"
        )

        ctk.CTkLabel(
            frame_c,
            text="Categoría C",
            font=("Arial",13,"bold")
        ).pack(
            pady=(10,5)
        )

        ctk.CTkLabel(
            frame_c,
            text=str(categoria_c),
            font=("Arial",28,"bold"),
            text_color="#1976D2"
        ).pack(
            pady=(0,10)
        )
    
    # =====================================================
    # KPI 7 - INDICADOR DE TENDENCIA DE CONSUMO
    # =====================================================
           
        
    def crear_tendencia_consumo(self):
        """
        Muestra un gráfico de barras con la distribución de la
        tendencia del consumo.
        """

        datos = self.controlador.kpi7_tendencia_consumo

        categorias = [
            "Creciente",
            "Estable",
            "Decreciente",
            "Sin datos"
        ]

        valores = [
            datos["creciente"],
            datos["estable"],
            datos["decreciente"],
            datos["sin_datos_suficientes"]
        ]

        # ===========================================
        # FIGURA
        # ===========================================

        figura = Figure(figsize=(5, 3.2), dpi=100)

        ax = figura.add_subplot(111)

        barras = ax.bar(
            categorias,
            valores,
            width=0.55
        )

        ax.set_title(
            "Tendencia del Consumo",
            fontsize=12,
            fontweight="bold"
        )

        ax.set_ylabel("Cantidad de Repuestos")

        ax.grid(
            axis="y",
            linestyle="--",
            alpha=0.4
        )

        # ===========================================
        # MOSTRAR EL VALOR SOBRE CADA BARRA
        # ===========================================

        for barra in barras:

            altura = barra.get_height()

            ax.text(
                barra.get_x() + barra.get_width()/2,
                altura,
                f"{int(altura)}",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold"
            )

        figura.tight_layout()

        canvas = FigureCanvasTkAgg(
            figura,
            master=self.frame_kpi7
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )