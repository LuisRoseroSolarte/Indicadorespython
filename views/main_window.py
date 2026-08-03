import customtkinter as ctk
from views.inicio_view import HomeView
from views.registros_view import InventoryView
from views.dashboards_view import DashboardView
from views.dashboard2_views import Dashboard2View
from PIL import Image
from datetime import datetime



class MainView:
    """
    Ventana principal de la aplicación.
    """

    def __init__(self, root, controlador):
    
        # ======================================================
        # REFERENCIAS
        # ======================================================

        self.root = root
        self.controlador = controlador
        self.controlador.main_view = self

        # ======================================================
        # CONFIGURACIÓN GENERAL
        # ======================================================

        self.configurar_ventana()

        self.configurar_grid_principal()

        # ======================================================
        # CONSTRUCCIÓN COMPONENTES  DE LA INTERFAZ
        # ======================================================

        self.crear_sidebar()

        self.crear_header()

        self.crear_content_frame()

        # ======================================================
        # NAVEGACIÓN
        # ======================================================

    #     self.configurar_navegacion()

        # ======================================================
        # VISTA INICIAL
        # ======================================================

        self.mostrar_inicio()
        
    # ==========================================================
    # CONFIGURACIÓN DE LA VENTANA
    # ==========================================================

    def configurar_ventana(self):
        """
        Configura la ventana principal.
        """

        self.root.title(
            "PROMINERALES SAS - Sistema Inteligente de Gestión de Inventarios"
        )

        self.root.geometry("1200x700")

        self.root.minsize(
            1200,
            700
        )

        ctk.set_appearance_mode("light")

        ctk.set_default_color_theme("blue")
    # ==========================================================
    # GRID PRINCIPAL
    # ==========================================================

    def configurar_grid_principal(self):
        """
        Configura el layout principal.

                HEADER
        -------------------------
        SIDEBAR | CONTENT FRAME
        """

        # Sidebar (columna izquierda)

        self.root.grid_columnconfigure(
            0,
            weight=0
        )

        # Área de trabajo

        self.root.grid_columnconfigure(
            1,
            weight=1
        )

        # Header

        self.root.grid_rowconfigure(
            0,
            weight=0
        )

        # Contenido

        self.root.grid_rowconfigure(
            1,
            weight=1
        )
    

    # ======================================================
    # COMPONENTES DE LA INTERFAZ
    # ======================================================
    
    def crear_content_frame(self):
        """
        Crea el contenedor donde se cargarán dinámicamente
        las diferentes vistas de la aplicación.
        """

        self.content_frame = ctk.CTkFrame(
            self.root,
            fg_color="#F3F5F9",
            corner_radius=0
        )

        self.content_frame.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        # Permite que las vistas ocupen todo el espacio disponible
        self.content_frame.grid_rowconfigure(
            0,
            weight=1
        )

        self.content_frame.grid_columnconfigure(
            0,
            weight=1
        )
    
    def crear_sidebar(self):
            """
            Crea el menú lateral de navegación.
            """
           
                
            # ======================================================
            # FRAME SIDEBAR
            # ======================================================
    
            self.sidebar = ctk.CTkFrame(
                self.root,
                width=220,
                corner_radius=0,
                fg_color="#F3F5F9"
            )
    
            self.sidebar.grid(
                row=0,
                column=0,
                rowspan=2,
                sticky="nsew"
            )
    
            self.sidebar.grid_propagate(False)
             # ======================================================
             # LOGO
             # ======================================================
 
            logo = ctk.CTkImage(
                 light_image=Image.open(
                     "assets/images/logo_prominerales.jpg"
                 ),
                 size=(150, 90)
             )
 
            self.lbl_logo = ctk.CTkLabel(
                 self.sidebar,
                 image=logo,
                 text=""
             )
 
            self.lbl_logo.image = logo
 
            self.lbl_logo.pack(
                 pady=(20, 25)
             )           
            
    
            # ======================================================
            # TÍTULO
            # ======================================================
    
            titulo = ctk.CTkLabel(
                self.sidebar,
                text="PROMINERALES SAS",
                font=("Arial", 17, "bold"),
                text_color="#0A0A8F"
            )
    
            titulo.pack(
                pady=(30, 40)
            )
    
            # ======================================================
            # BOTÓN INICIO
            # ======================================================
    
            self.btn_inicio = ctk.CTkButton(
                self.sidebar,
                text="Inicio",
                width=180,
                command=self.mostrar_inicio
            )
    
            self.btn_inicio.pack(
                pady=10
            )
    
            # ======================================================
            # BOTÓN DASHBOARD
            # ======================================================
    
            self.btn_dashboard = ctk.CTkButton(
                self.sidebar,
                text="Dashboard",
                width=180,
                command=self.mostrar_dashboard
            )
    
            self.btn_dashboard.pack(
                pady=10
            )
            
            # ======================================================
            # BOTÓN DASHBOARD2
            # ======================================================
                
            self.btn_dashboard2 = ctk.CTkButton(
                            self.sidebar,
                            text="Dashboard 2",
                            width=180,
                            command=self.mostrar_dashboard2
                            )
                
            self.btn_dashboard2.pack(
                   pady=10
                 )
            
    
            # ======================================================
            # BOTÓN REGISTROS
            # ======================================================
    
            self.btn_registros = ctk.CTkButton(
                self.sidebar,
                text="Registros",
                width=180,
                command=self.mostrar_registros
            )
    
            self.btn_registros.pack(
                pady=10
            )
            
            
    def crear_header(self):
        """
        Crea el encabezado superior de la aplicación.
        
        """

        # ======================================================
        # FRAME HEADER
        # ======================================================

        self.header = ctk.CTkFrame(
            self.root,
            height=45,
            fg_color="#0A0A8F",
            corner_radius=0
        )

        self.header.grid(
            row=0,
            column=1,
            sticky="ew"
        )

        self.header.grid_propagate(False)

        # ======================================================
        # GRID DEL HEADER
        # ======================================================

        self.header.grid_columnconfigure(
            0,
            weight=1
        )

        self.header.grid_columnconfigure(
            1,
            weight=0
        )

        # ======================================================
        # INFORMACIÓN DERECHA
        # ======================================================

        fecha_actual = datetime.now().strftime("%d/%m/%Y")

        hora_actual = datetime.now().strftime("%H:%M:%S")

        texto = (
            f"Jefe de Almacén    "
            f"Fecha : {fecha_actual}    "
            f"{hora_actual}"
        )

        self.lbl_info = ctk.CTkLabel(
            self.header,
            text=texto,
            text_color="white",
            font=("Arial", 12, "bold")
        )

        self.lbl_info.grid(
            row=0,
            column=1,
            padx=15,
            pady=10,
            sticky="e"
        )   
     
    # ======================================================
    # MÉTODOS AUXILIARES
    # ======================================================   
    
    def limpiar_content_frame(self):
        """
        Elimina todos los widgets contenidos en el área de trabajo.

        Este método se ejecuta antes de cargar una nueva vista
        (Inicio, Dashboard, Registros, etc.).
        """

        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
            
    # ======================================================
    # NAVEGACIÓN ENTRE VISTAS
    # ======================================================   
    
    def mostrar_inicio(self):
        """
        Muestra la vista de inicio.
        """

        # Limpiar el área de trabajo
        self.limpiar_content_frame()

        # Crear la vista
        self.inicio = HomeView(
            self.content_frame,
            self.controlador
        )

        # Mostrar la vista
        self.inicio.pack(
            fill="both",
            expand=True
        )
        
    def mostrar_dashboard(self):
    
        self.limpiar_content_frame()

        self.dashboard = DashboardView(
            self.content_frame,
            self.controlador
        )

        self.dashboard.pack(
            fill="both",
            expand=True
        )
     
     
    def mostrar_dashboard2(self):
        self.limpiar_content_frame()
        self.dashboard2 = Dashboard2View(
            self.content_frame,
            self.controlador
            )
        
        self.dashboard2.pack(
            fill="both",
            expand=True
            )
      
        
    def mostrar_registros(self):
    
        self.limpiar_content_frame()

        self.registros = InventoryView(
            self.content_frame,
            self.controlador
        )

        self.registros.pack(
            fill="both",
            expand=True
        )
    #********************************************************************+ 
    
    # =====================================================
    # ACTUALIZAR VISTAS
    # =====================================================

    def actualizar_vistas(self):

        if hasattr(self, "inicio"):
            self.inicio.actualizar_datos()

        if hasattr(self, "registros"):
            self.registros.actualizar_datos()
    # =====================================================
    # ACTUALIZAR INICIO
    # =====================================================

    def actualizar_inicio(self):
        """
        Refresca la vista Inicio con los nuevos datos del controlador.
        """

        if hasattr(self, "inicio"):
            self.inicio.actualizar()
            
        