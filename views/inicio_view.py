import customtkinter as ctk
from views.components.kpi_card import KPICard
from views.components.abc_distribution import ABCDistribution


class HomeView(ctk.CTkFrame):
    """
    Vista principal de la aplicación.

    En esta vista se mostrarán los indicadores principales
    del sistema de inventarios.
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

        self.grid_columnconfigure(
            0,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=0
        )

        self.grid_rowconfigure(
            1,
            weight=0
        )

        self.grid_rowconfigure(
            2,
            weight=1
        )

        # =====================================================
        # CONSTRUIR INTERFAZ
        # =====================================================

        self.crear_titulo()

        self.crear_metricas()

        self.crear_estado_bodega()
        
        #self.actualizar()
        
        
    # =====================================================
    # TÍTULO
    # =====================================================

    def crear_titulo(self):

            frame = ctk.CTkFrame(
                self,
                fg_color="transparent"
            )

            frame.grid(
                row=0,
                column=0,
                sticky="ew",
                padx=25,
                pady=(20,10)
            )

            titulo = ctk.CTkLabel(
                frame,
                text="PANEL DE INICIO",
                font=("Arial",22,"bold"),
                text_color="#183A8F"
            )

            titulo.pack(
                anchor="w"
            )

            subtitulo = ctk.CTkLabel(
                frame,
                text="MÉTRICAS",
                font=("Arial",14,"bold"),
                text_color="#183A8F"
            )

            subtitulo.pack(
                anchor="w"
            )

    # =====================================================
    # MÉTRICAS
    # =====================================================

    def crear_metricas(self):
        """
        Crea las tarjetas de indicadores principales.
        """

        # =====================================================
        # FRAME CONTENEDOR
        # =====================================================
        
      

        self.frame_metricas = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.frame_metricas.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=25,
            pady=10
        )

        self.frame_metricas.grid_columnconfigure(0, weight=1)

        # =====================================================
        # KPI 2
        # Valorización Total del Inventario
        # =====================================================

        self.kpi_valorizacion = KPICard(
            parent=self.frame_metricas,
            titulo="VALORIZACIÓN TOTAL",
            valor=f"${self.controlador.kpi2_valorizacion_total:,.1f}" or 0,
            #valor= f"${self.controlador.obtener_kpi('valorizacion_total'):,.1f}" or 0,
            descripcion="Capital Inmovilizado"
        )
        
        # =====================================================
        # KPI 3 - Alertas de Stock
        # =====================================================

        alertas = self.controlador.kpi3_alertas_stock

        if alertas is None or alertas.empty:
            bajo, sobre = 0, 0
        else:
            bajo = alertas.loc[alertas["INDICADOR"] == "Stock Bajo", "CANTIDAD"].values[0]
            sobre = alertas.loc[alertas["INDICADOR"] == "Sobrestock", "CANTIDAD"].values[0]
            
        self.kpi_alertas = KPICard(
            parent=self.frame_metricas,
            titulo="ALERTAS STOCK",
            valor=f"{bajo} / {sobre}",
            descripcion="Bajo / Sobrestock"
        )

        self.kpi_alertas.grid(
            row=0,
            column=1,
            padx=15,
            pady=10,
            sticky="ew"
        )

        self.kpi_valorizacion.grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=10
        )
        
        
    # =====================================================
    # ESTADO DE BODEGA
    # =====================================================

    def crear_estado_bodega(self):
        """
        Crea la sección Estado de Bodega.
        """

        # =====================================================
        # FRAME CONTENEDOR
        # =====================================================

        self.frame_estado = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.frame_estado.grid(
            row=2,
            column=0,
            padx=25,
            pady=(15, 20),
            sticky="nsew"
        )
        
        # Dos columnas codigo nuevo
        self.frame_estado.grid_columnconfigure(0, weight=1)
        self.frame_estado.grid_columnconfigure(1, weight=1)


        # =====================================================
        # TITULO
        # =====================================================

        self.lbl_estado = ctk.CTkLabel(
            self.frame_estado,
            text="ESTADO DE BODEGA",
            font=("Arial", 16, "bold")
        )

        self.lbl_estado.grid(
            row=0,
            column=0,
            columnspan=2,#codigo nuevo
            sticky="w",
            pady=(0, 10)
        )

        # =====================================================
        # DATOS DEL KPI 1
        # =====================================================

        datos_abc = self.controlador.kpi_distribucion_abc_valor

        if datos_abc is None:

            datos_abc = {
                "A": 0,
                "B": 0,
                "C": 0
            }
        # =====================================================
        # GRAFICA codigo nuevo
        # =====================================================

        self.distribucion_abc = ABCDistribution(
            parent=self.frame_estado,
            datos=datos_abc
        )

        self.distribucion_abc.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(0,15)
        )
        
         # =====================================================
        # NUEVO CONTENEDOR TABLA
        # =====================================================

        self.frame_tabla_abc = ctk.CTkFrame(
            self.frame_estado
        )

        self.frame_tabla_abc.grid(
            row=1,
            column=1,
            sticky="nsew"
        )
        
        #crear nueva tabla
        self.crear_tabla_repuestos_abc()

        # =====================================================
        # COMPONENTE DISTRIBUCIÓN ABC codigo viejo desabilitado 
        # =====================================================

        # self.distribucion_abc = ABCDistribution(
        #     parent=self.frame_estado,
        #     datos=datos_abc
        # )

        # self.distribucion_abc.grid(
        #     row=1,
        #     column=0,
        #     sticky="ew"
        # )
        
    
    # =====================================================
    # TABLA REPUESTOS REPRESENTATIVOS ABC
    # =====================================================

    def crear_tabla_repuestos_abc(self):
        
       
        datos = self.controlador.tabla_repuestos_abc

        # -------------------------------------------------
        # Título
        # -------------------------------------------------

        ctk.CTkLabel(
            self.frame_tabla_abc,
            text="Repuestos Representativos ABC",
            font=("Arial",14,"bold")
        ).pack(
            anchor="w",
            padx=10,
            pady=(10,5)
        )

        # -------------------------------------------------
        # Encabezados
        # -------------------------------------------------

        frame_header = ctk.CTkFrame(
            self.frame_tabla_abc,
            fg_color="#E5E5E5"
        )

        frame_header.pack(
            fill="x",
            padx=10
        )

        frame_header.grid_columnconfigure(0, weight=5)
        frame_header.grid_columnconfigure(1, weight=1)
        frame_header.grid_columnconfigure(2, weight=2)

        ctk.CTkLabel(
            frame_header,
            text="Repuesto",
            font=("Arial",11,"bold")
        ).grid(row=0,column=0,padx=5,pady=5,sticky="w")

        ctk.CTkLabel(
            frame_header,
            text="Cat.",
            font=("Arial",11,"bold")
        ).grid(row=0,column=1,padx=5,pady=5)

        ctk.CTkLabel(
            frame_header,
            text="Stock",
            font=("Arial",11,"bold")
        ).grid(row=0,column=2,padx=5,pady=5)

        # -------------------------------------------------
        # Scroll
        # -------------------------------------------------

        scroll = ctk.CTkScrollableFrame(
            self.frame_tabla_abc,
            height=260
        )

        scroll.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(5,10)
        )
        
        
        # -------------------------------------------------
        # Filas
        # -------------------------------------------------

        # for _, fila in datos.iterrows():

        #     fila_frame = ctk.CTkFrame(
        #         scroll,
        #         fg_color="transparent"
        #     )

        #     fila_frame.pack(
        #         fill="x",
        #         pady=1
        #     )

        #     fila_frame.grid_columnconfigure(0, weight=5)
        #     fila_frame.grid_columnconfigure(1, weight=1)
        #     fila_frame.grid_columnconfigure(2, weight=2)

        #     ctk.CTkLabel(
        #         fila_frame,
        #         text=fila["REPUESTO"][:30],
        #         anchor="w",
        #         font=("Arial",12)# cambiar tamaño nombre 
        #     ).grid(
        #         row=0,
        #         column=0,
        #         sticky="w",
        #         padx=5
        #     )
            
        #     #=================================================================
        #     #contenedor para categoria 
        #     #===============================================
        #     frame_categoria = ctk.CTkFrame(
        #         fila_frame,
        #         fg_color="transparent"
        #     )
    
        #     frame_categoria.grid(
        #         row=0,
        #         column=1,
        #         sticky="nsew"
        #     )
            

        #     ctk.CTkLabel(
        #         #fila_frame,
        #         frame_categoria,
        #         text=fila["CATEGORIA"],
        #         font=("Arial",10,"bold"),
        #         # anchor="center",
        #         # justify="center",
        #         # width=60#40s
        #     ).pack(expand=True)
            
        #     # grid(
        #     #     row=0,
        #     #     column=1,
        #     #     padx=5,
        #     #     sticky="nsew"
        #     # )

        #     ctk.CTkLabel(
        #         fila_frame,
        #         text=f"{fila['STOCK']:.2f}",
        #         font=("Arial",10)
        #     ).grid(
        #         row=0,
        #         column=2
        #     )
        for _, fila in datos.iterrows():
            
            fila_frame = ctk.CTkFrame(
                scroll,
                fg_color="transparent"
            )

            fila_frame.pack(
                fill="x",
                pady=1
            )

            # -----------------------------
            # REPUESTO
            # -----------------------------
            ctk.CTkLabel(
                fila_frame,
                text=fila["REPUESTO"][:32],
                font=("Arial",11),
                anchor="w",
                width=320
            ).pack(
                side="left",
                padx=(5,0)
            )

            # -----------------------------
            # CATEGORIA
            # -----------------------------
            ctk.CTkLabel(
                fila_frame,
                text=fila["CATEGORIA"],
                font=("Arial",11,"bold"),
                width=40
            ).pack(
                side="left"
            )

            # -----------------------------
            # STOCK
            # -----------------------------
            ctk.CTkLabel(
                fila_frame,
                text=f"{fila['STOCK']:.2f}",
                font=("Arial",11),
                width=80
            ).pack(
                side="right",
                padx=(0,5)
            )            
   
    def actualizar(self):
        """
        Actualiza la información de la vista Inicio.
        """

        # Elimina todos los componentes actuales
        for widget in self.winfo_children():
            widget.destroy()

        # Vuelve a construir la interfaz con los nuevos datos
        self.crear_titulo()
        self.crear_metricas()
        self.crear_graficas()
        
        
        
    # =====================================================
    # ACTUALIZAR DATOS
    # =====================================================

    def actualizar_datos(self):
        """
        Actualiza las tarjetas del Inicio sin reconstruir la vista.
        """

        # Eliminar todas las tarjetas actuales
        for widget in self.frame_metricas.winfo_children():
            widget.destroy()

        # Volver a construirlas con los nuevos valores
        self.crear_metricas()