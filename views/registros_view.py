import customtkinter as ctk
import tkinter as tk
from views.components.kpi_card import KPICard
from tkinter import filedialog,messagebox
import os


class InventoryView(ctk.CTkFrame):
    """
    Vista Registros.

    En esta vista se mostrarán los registros del inventario,
    permitiendo consultar, filtrar y visualizar los movimientos
    de los repuestos.
    """

    def __init__(self, parent, controlador):
        """
        Inicializa la vista de registros.
        """
        super().__init__(parent)
        
        
        
        # =====================================================
        # REFERENCIAS
        # =====================================================
        self.controlador = controlador
        self.elem_seleccionado = None

        # =====================================================
        # CONFIGURACIÓN DEL FRAME
        # =====================================================
        self.configure(fg_color="#F3F5F9")

        # =====================================================
        # CONSTRUIR INTERFAZ
        # =====================================================
      
        self.crear_titulo()
        
        self.crear_metricas()

        self.crear_frame_inferior()

        self.crear_importar_excel()
        
        #self.seleccionar_archivo()
        
        self.crear_configuracion()
        
    # =====================================================
    # FRAME INFERIOR
    # =====================================================
    def crear_frame_inferior(self):
        """
        Contenedor inferior donde se ubican los dos paneles.
        """

        self.frame_inferior = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.frame_inferior.pack(
            fill="x",
            padx=25,
            pady=(10,20)
        )
        
        
    # =====================================================
    # TÍTULO
    # =====================================================
    def crear_titulo(self):
        """
        Crea el título de la vista.
        """
        titulo = ctk.CTkLabel(
            self,
            text="REGISTROS",
            font=("Arial", 24, "bold"),
            text_color="#183A8F"
        )
        titulo.pack(
            anchor="nw",
            padx=25,
            pady=20
        )
    
    # =====================================================
    # MÉTRICAS
    # =====================================================
    def crear_metricas(self):
        """
        Crea las métricas principales del módulo de registros.
        """
        # FRAME CONTENEDOR
        self.frame_metricas = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.frame_metricas.pack(
            fill="x",
            padx=25,
            pady=15
        )

        # KPI 1 - REPUESTOS REGISTRADOS
        total_repuestos = self.controlador.cantidad_repuestos_registrados
        if total_repuestos is None:
            total_repuestos = 0

        self.kpi_repuestos = KPICard(
            parent=self.frame_metricas,
            titulo="REPUESTOS REGISTRADOS",
            valor=total_repuestos,
            descripcion="en maestro"
        )
        self.kpi_repuestos.pack(
            side="left",
            padx=10,
            pady=10,
            expand=True,
            fill="both"
        )

        # KPI 2 - STOCK BAJO
        alertas = self.controlador.kpi3_alertas_stock
        if alertas is None or alertas.empty:
            bajo, sobre = 0, 0
        else:
            bajo = alertas.loc[alertas["INDICADOR"] == "Stock Bajo", "CANTIDAD"].values[0]
            sobre = alertas.loc[alertas["INDICADOR"] == "Sobrestock", "CANTIDAD"].values[0]

        self.kpi_stock_bajo = KPICard(
            parent=self.frame_metricas,
            titulo="REPUESTOS BAJO STOCK",
            valor=f"{bajo}",
            descripcion="requieren pedido"
        )
        self.kpi_stock_bajo.pack(
            side="left",
            padx=10,
            pady=10,
            expand=True,
            fill="both"
        )


  
    # =====================================================
    # IMPORTAR ARCHIVO EXCEL
    # =====================================================
    def crear_importar_excel(self):
        """
        Crea el contenedor para importar el archivo Excel.
        """

        # =====================================================
        # CONTENEDOR PRINCIPAL
        # =====================================================

        self.frame_importar = ctk.CTkFrame(
            self.frame_inferior,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#CFCFCF",
            width=420,
            height=260
            )

        self.frame_importar.pack(
            side="left",
            expand=True,
            fill="both",
            padx=(0,10)
            )

        self.frame_importar.pack_propagate(False)

        # =====================================================
        # TÍTULO
        # =====================================================

        self.lbl_titulo_importar = ctk.CTkLabel(
            self.frame_importar,
            text="IMPORTAR ARCHIVO EXCEL",
            font=("Arial", 14, "bold")
        )

        self.lbl_titulo_importar.pack(
            anchor="w",
            padx=15,
            pady=(12, 10)
        )

        # =====================================================
        # ÁREA CENTRAL (VACÍA POR AHORA)
        # =====================================================

        self.frame_dragdrop = ctk.CTkFrame(
            self.frame_importar,
            fg_color="#F5F5F5",
            border_width=1,
            border_color="#BDBDBD",
            corner_radius=6,
            height=140
        )

        self.frame_dragdrop.pack(
            fill="both",
            expand=True,
            padx=15
        )
        
        
        # =====================================================
        # BOTÓN SUBIR ARCHIVO
        # =====================================================

        self.btn_subir_archivo = ctk.CTkButton(
        self.frame_dragdrop,
        text="SUBIR ARCHIVO XLS",
        width=220,
        height=45,
        font=("Arial", 13, "bold"),
        command=self.seleccionar_archivo
            )

        self.btn_subir_archivo.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
            )

        # =====================================================
        # ARCHIVO CARGADO
        # =====================================================

        self.lbl_archivo = ctk.CTkLabel(
            self.frame_importar,
            text="Archivo cargado: Ninguno",
            font=("Arial", 11)
        )

        self.lbl_archivo.pack(
            anchor="w",
            padx=15,
            pady=(8, 12)
        )
        
     
    # =====================================================
    # SELECCIONAR ARCHIVO EXCEL
    # =====================================================

    def seleccionar_archivo(self):
        """
        Permite seleccionar un archivo Excel y ejecutar
        automáticamente todo el proceso de carga.
        """

        ruta = filedialog.askopenfilename(
            title="Seleccione un archivo Excel",
            filetypes=[
                ("Archivos Excel", "*.xlsx *.xls")
            ]
        )

        if not ruta:
            return

        try:

            # =====================================================
            # Mostrar nombre del archivo
            # =====================================================

            nombre = os.path.basename(ruta)

            self.lbl_archivo.configure(
                text=f"Archivo cargado: {nombre}"
            )

            # =====================================================
            # Enviar ruta al controlador
            # =====================================================

            self.controlador.seleccionar_archivo_excel(ruta)
            
            messagebox.showinfo(
                           
                           "Archivo Cargado",
                             "Desea analizar el archivo cargado?."
                        )
            
            # =====================================================
            # Mensaje intermedio (no bloqueante, se cierra solo)
            # =====================================================
            ventana_temp = tk.Toplevel(self)
            ventana_temp.title("Analizando archivo")
            ventana_temp.geometry("300x100")
            tk.Label(ventana_temp, text="Analizando archivo...").pack(expand=True, pady=20)

            # Forzar que se muestre inmediatamente
            ventana_temp.update()

            # Cerrar automáticamente después de 2 segundos
            ventana_temp.after(2000, ventana_temp.destroy)
            

            # =====================================================
            # Ejecutar todo el proceso automáticamente
            # =====================================================

            self.controlador.cargar_excel()
            
            self.controlador.actualizar_datawarehouse()

            self.controlador.cargar_datawarehouse()

            self.controlador.calcular_kpis()
            
            

            # =====================================================
            # Mensaje de éxito
            # =====================================================

            messagebox.showinfo(
                "Proceso finalizado",
                "El archivo fue procesado correctamente."
            )
            
        except Exception as error:

            messagebox.showerror(
                "Error",
                f"Ocurrió un error:\n\n{error}"
            )
   # =====================================================
   # CONFIGURACIONES BÁSICAS
   # =====================================================
    def crear_configuracion(self):
        """
        Crea el panel de configuraciones básicas.
        """

        # =====================================================
        # CONTENEDOR PRINCIPAL
        # =====================================================

        self.frame_configuracion = ctk.CTkFrame(
            self.frame_inferior,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#CFCFCF",
            width=420,
            height=260
            )

        self.frame_configuracion.pack(
            side="left",
            expand=True,
            fill="both",
            padx=(10,0)
             )
        self.frame_configuracion.pack_propagate(False)

        # =====================================================
        # TÍTULO
        # =====================================================

        self.lbl_titulo_config = ctk.CTkLabel(
            self.frame_configuracion,
            text="CONFIGURACIONES BÁSICAS",
            font=("Arial", 14, "bold")
        )

        self.lbl_titulo_config.pack(
            anchor="w",
            padx=15,
            pady=(12, 12)
        )

        # =====================================================
        # BUSCAR
        # =====================================================

        self.lbl_buscar = ctk.CTkLabel(
            self.frame_configuracion,
            text="BUSCAR"
        )

        self.lbl_buscar.pack(
            anchor="w",
            padx=15
        )

        self.entry_buscar = ctk.CTkEntry(
            self.frame_configuracion,
            placeholder_text="Código o Nombre del Repuesto"
        )

        self.entry_buscar.pack(
            fill="x",
            padx=15,
            pady=(5, 15)
        )

        # Lista completa de repuestos
        self.lista_repuestos = self.controlador.obtener_lista_repuestos()

        # Ventana emergente (inicialmente no existe)
        self.popup_busqueda = None

        # Buscar mientras escribe
        self.entry_buscar.bind(
            "<KeyRelease>",
            self.buscar_repuesto
        )

        # Ocultar al perder el foco
        self.entry_buscar.bind(
            "<FocusOut>",
            lambda e: self.after(150, self.ocultar_popup)
        )
        # =====================================================
        # STOCK MÍNIMO
        # =====================================================

        self.lbl_stock = ctk.CTkLabel(
            self.frame_configuracion,
            text="NUEVO STOCK MÍNIMO"
        )

        self.lbl_stock.pack(
            anchor="w",
            padx=15
        )

        self.entry_stock = ctk.CTkEntry(
            self.frame_configuracion
        )

        self.entry_stock.pack(
            fill="x",
            padx=15,
            pady=(5, 20)
        )

        # =====================================================
        # BOTONES
        # =====================================================

        self.frame_botones = ctk.CTkFrame(
            self.frame_configuracion,
            fg_color="transparent"
        )

        self.frame_botones.pack(
            # fill="x",
            # padx=15
            pady=(10,15)
        )
        
        # =====================================================
        # BOTÓN ACTUALIZAR
        # =====================================================

        self.btn_actualizar = ctk.CTkButton(
        #self.frame_configuracion,
        self.frame_botones,
        text="ACTUALIZAR",
        width=140,
        command=self.actualizar_stock_minimo
         )
        
        self.btn_actualizar.pack(
            side="left",
            #expand=True,
            padx=10#(0, 5)
        )
        
        # =====================================================
        # BOTÓN CANCELAR
        # =====================================================

        self.btn_cancelar = ctk.CTkButton(
            self.frame_botones,
            text="CANCELAR",
            width=140,
            fg_color="#7A7A7A",
            hover_color="#5F5F5F",
            command=self.limpiar_formulario
            )

        self.btn_cancelar.pack(
            side="left",
            #expand=True,
            #padx=(5, 0)
            padx=10
        )
        
        
        
    def buscar_repuesto(self, event=None):
    
        texto = self.entry_buscar.get().strip().lower()

        if texto == "":
            self.ocultar_popup()
            return

        encontrados = [
        repuesto
        for repuesto in self.lista_repuestos
        if texto in repuesto["NOMBRE_ELEMENTO"].lower()
                     ]

        if not encontrados:
            self.ocultar_popup()
            return

        self.mostrar_popup(encontrados[:20])
                    
    
    
    def mostrar_popup(self, resultados):
    
        self.ocultar_popup()

        self.popup_busqueda = tk.Toplevel(self)

        self.popup_busqueda.overrideredirect(True)

        self.popup_busqueda.configure(
            bg="white"
        )

        # Posición del Entry
        x = self.entry_buscar.winfo_rootx()
        y = (
            self.entry_buscar.winfo_rooty()
            + self.entry_buscar.winfo_height()
        )

        ancho = self.entry_buscar.winfo_width()

        self.popup_busqueda.geometry(
            f"{ancho}x220+{x}+{y}"
        )

        frame = ctk.CTkScrollableFrame(
            self.popup_busqueda,
            fg_color="white",
            corner_radius=0
        )

        frame.pack(
            fill="both",
            expand=True
        )

        for repuesto in resultados:
    
            boton = ctk.CTkButton(
                frame,
                text=repuesto["NOMBRE_ELEMENTO"],
                anchor="w",
                fg_color="transparent",
                hover_color="#D6EAF8",
                text_color="black",
                corner_radius=0,
                command=lambda r=repuesto: self.seleccionar_repuesto(r)
            )

            boton.pack(
                fill="x",
                padx=2,
                pady=1
            )
                
        
                
    def seleccionar_repuesto(self, repuesto):
        """
        Guarda el repuesto seleccionado.
        """

        # Guardar el código del repuesto
        self.elem_seleccionado = repuesto["ELEM"]

        # Mostrar el nombre en el Entry
        self.entry_buscar.delete(0, "end")
        self.entry_buscar.insert(
            0,
            repuesto["NOMBRE_ELEMENTO"]
        )

        # Ocultar la ventana emergente
        self.ocultar_popup()
            
        
    def ocultar_popup(self):
    
        if self.popup_busqueda is not None:

            if self.popup_busqueda.winfo_exists():

                self.popup_busqueda.destroy()

        self.popup_busqueda = None
        
        
    def actualizar_stock_minimo(self):
        """
        Envía al controlador el repuesto seleccionado
        y el nuevo stock mínimo.
        """

        # Verificar que haya un repuesto seleccionado
        if self.elem_seleccionado is None:
            messagebox.showwarning(
                "Advertencia",
                "Debe seleccionar un repuesto."
            )
            return

        # Obtener el nuevo stock
        nuevo_stock = self.entry_stock.get().strip()

        if nuevo_stock == "":
            messagebox.showwarning(
                "Advertencia",
                "Debe ingresar el nuevo stock mínimo."
            )
            return

        try:
            nuevo_stock = int(nuevo_stock)

        except ValueError:

            messagebox.showerror(
                "Error",
                "El stock mínimo debe ser un número entero."
            )
            return

        # Enviar al controlador
        self.controlador.actualizar_stock_minimo(
            self.elem_seleccionado,
            nuevo_stock
        )
        
        
    # =====================================================
    # ACTUALIZAR DATOS
    # =====================================================

    def actualizar_datos(self):
        """
        Actualiza la vista de registros.
        """

        # Limpiar selección
        self.elem_seleccionado = None

        # Limpiar buscador
        self.entry_buscar.delete(0, "end")

        # Limpiar stock
        self.entry_stock.delete(0, "end")

        # Volver a cargar la lista de repuestos
        self.lista_repuestos = self.controlador.obtener_lista_repuestos()

        # Ocultar popup si está abierto
        self.ocultar_popup()
        
        
    def limpiar_formulario(self):
    
        self.entry_buscar.delete(0, "end")
        self.entry_stock.delete(0, "end")

        self.elem_seleccionado = None

        self.ocultar_popup()