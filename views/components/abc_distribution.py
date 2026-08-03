import customtkinter as ctk


class ABCDistribution(ctk.CTkFrame):
    """
    Componente para mostrar la distribución ABC
    mediante barras de progreso.

    Parámetro
    ---------
    datos : dict

    Ejemplo:
    {
        "A": 60.0,
        "B": 25.0,
        "C": 15.0
    }
    """

    def __init__(self, parent, datos=None):

        super().__init__(
            parent,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#D8D8D8"
        )

        if datos is None:
            datos = {
                "A": 0,
                "B": 0,
                "C": 0
            }

        self.grid_columnconfigure(1, weight=1)

        # =====================================================
        # TITULO
        # =====================================================

        self.lbl_titulo = ctk.CTkLabel(
            self,
            text="DISTRIBUCIÓN ABC (Valor)",
            font=("Arial", 14, "bold")
        )

        self.lbl_titulo.grid(
            row=0,
            column=0,
            columnspan=3,
            padx=15,
            pady=(15, 20),
            sticky="w"
        )

        # =====================================================
        # CATEGORIA A
        # =====================================================

        self.lbl_a = ctk.CTkLabel(
            self,
            text="Categoría A"
        )

        self.lbl_a.grid(
            row=1,
            column=0,
            padx=15,
            pady=8,
            sticky="w"
        )

        self.pb_a = ctk.CTkProgressBar(self)

        self.pb_a.grid(
            row=1,
            column=1,
            padx=10,
            sticky="ew"
        )

        self.lbl_valor_a = ctk.CTkLabel(self)

        self.lbl_valor_a.grid(
            row=1,
            column=2,
            padx=15
        )

        # =====================================================
        # CATEGORIA B
        # =====================================================

        self.lbl_b = ctk.CTkLabel(
            self,
            text="Categoría B"
        )

        self.lbl_b.grid(
            row=2,
            column=0,
            padx=15,
            pady=8,
            sticky="w"
        )

        self.pb_b = ctk.CTkProgressBar(self)

        self.pb_b.grid(
            row=2,
            column=1,
            padx=10,
            sticky="ew"
        )

        self.lbl_valor_b = ctk.CTkLabel(self)

        self.lbl_valor_b.grid(
            row=2,
            column=2,
            padx=15
        )

        # =====================================================
        # CATEGORIA C
        # =====================================================

        self.lbl_c = ctk.CTkLabel(
            self,
            text="Categoría C"
        )

        self.lbl_c.grid(
            row=3,
            column=0,
            padx=15,
            pady=(8,15),
            sticky="w"
        )

        self.pb_c = ctk.CTkProgressBar(self)

        self.pb_c.grid(
            row=3,
            column=1,
            padx=10,
            sticky="ew"
        )

        self.lbl_valor_c = ctk.CTkLabel(self)

        self.lbl_valor_c.grid(
            row=3,
            column=2,
            padx=15
        )

        # ===============================================
        # CARGAR DATOS
        # ===============================================

        self.actualizar(datos)

    # =====================================================
    # ACTUALIZAR GRAFICA
    # =====================================================

    def actualizar(self, datos):

        a = datos.get("A", 0)
        b = datos.get("B", 0)
        c = datos.get("C", 0)

        self.pb_a.set(a / 100)
        self.pb_b.set(b / 100)
        self.pb_c.set(c / 100)

        self.lbl_valor_a.configure(
            text=f"{a:.1f}%"
        )

        self.lbl_valor_b.configure(
            text=f"{b:.1f}%"
        )

        self.lbl_valor_c.configure(
            text=f"{c:.1f}%"
        )