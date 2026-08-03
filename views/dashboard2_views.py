import customtkinter as ctk
#from views.components.forecast_chart import ForecastChart
from views.components.forecast_bar_chart import ForecastBarChart
from views.components.depletion_chart import DepletionChart
from views.components.projected_inventory_chart import ProjectedInventoryChart






class Dashboard2View(ctk.CTkFrame):
    """
    Dashboard 2.

    En esta vista se mostrarán los indicadores predictivos
    del sistema de inventarios.
    """

    def __init__(self, parent, controlador):

        super().__init__(parent)

        # =====================================================
        # REFERENCIAS
        # =====================================================

        self.controlador = controlador

        # =====================================================
        # CONFIGURACIÓN
        # =====================================================

        self.configure(
            fg_color="#F3F5F9"
        )

        # =====================================================
        # CONSTRUIR INTERFAZ
        # =====================================================

        self.crear_titulo()
        self.crear_contenedores()
        self.crear_pronostico_consumo()
        self.crear_pronostico_agotamiento()
        self.crear_nivel_inventario()
       

    # =====================================================
    # TÍTULO
    # =====================================================

    def crear_titulo(self):

        titulo = ctk.CTkLabel(
            self,
            text="DASHBOARD PREDICTIVO",
            font=("Arial", 24, "bold"),
            text_color="#183A8F"
        )

        titulo.pack(
            anchor="nw",
            padx=25,
            pady=20
        )

    # =====================================================
    # CONTENEDORES
    # =====================================================

    def crear_contenedores(self):

        # -----------------------------------------------------
        # FRAME PRINCIPAL
        # -----------------------------------------------------

        self.frame_dashboard = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.frame_dashboard.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        # Grid del dashboard

        self.frame_dashboard.grid_columnconfigure(
            (0, 1),
            weight=1
        )

        self.frame_dashboard.grid_rowconfigure(
            (0, 1),
            weight=1
        )

        # =====================================================
        # KPI 8
        # =====================================================

        self.frame_kpi8 = ctk.CTkFrame(
            self.frame_dashboard,
            corner_radius=10
        )

        self.frame_kpi8.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="nsew"
        )

        ctk.CTkLabel(
            self.frame_kpi8,
            text="Pronóstico de Consumo Mensual:Top 10 ",
            font=("Arial", 17, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(2,0)
        )

        # =====================================================
        # KPI 9
        # =====================================================

        self.frame_kpi9 = ctk.CTkFrame(
            self.frame_dashboard,
            corner_radius=10
        )

        self.frame_kpi9.grid(
            row=0,
            column=1,
            padx=10,
            pady=(1,4),
            sticky="nsew"
        )

        ctk.CTkLabel(
            self.frame_kpi9,
            text="Nivel de Inventario Proyectado :Top 10 Menor Inventario ",
            
            font=("Arial", 17, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(2,0)
        )

        # =====================================================
        # KPI 10
        # =====================================================

        self.frame_kpi10 = ctk.CTkFrame(
            self.frame_dashboard,
            corner_radius=10
        )

        self.frame_kpi10.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            sticky="nsew"
        )

        ctk.CTkLabel(
            self.frame_kpi10,
            text="Pronóstico de Agotamiento del Inventario :top 10 Riesgo agotamiento",
            
            font=("Arial", 18, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(2,0)
        )
        
        
    def crear_pronostico_consumo(self):
    
        datos = self.controlador.kpi8_pronostico_consumo

        if datos is None:

            ctk.CTkLabel(
                self.frame_kpi8,
                text="No existen datos.",
                font=("Arial",14)
            ).pack(expand=True)

            return

        grafica = ForecastBarChart(
            parent=self.frame_kpi8,
            detalle=datos["detalle"],
            top_n=10
        )

        grafica.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )
        
    def crear_pronostico_agotamiento(self):
        """
        Muestra el Top 10 de repuestos
        con menor tiempo de agotamiento.
        """

        datos = self.controlador.kpi9_pronostico_agotamiento
        

        if datos is None:

            ctk.CTkLabel(
                self.frame_kpi10,
                text="No existen datos.",
                font=("Arial",14)
            ).pack(expand=True)

            return

        grafica = DepletionChart(
            parent=self.frame_kpi10,
            detalle=datos["detalle"]
        )

        grafica.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )
        
        
    def crear_nivel_inventario(self):
        """
        Muestra el Top 10 de menor inventario proyectado.
        """

        datos = self.controlador.kpi10_nivel_inventario

        if datos is None:

            ctk.CTkLabel(
                self.frame_kpi9,
                text="No existen datos.",
                font=("Arial",14)
            ).pack(expand=True)

            return

        grafica = ProjectedInventoryChart(
            parent=self.frame_kpi9,
            detalle=datos["detalle"],
            top_n=10
        )

        grafica.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )