import customtkinter as ctk


class KPICard(ctk.CTkFrame):
    """
    Tarjeta reutilizable para mostrar un KPI.

    Parámetros
    ----------
    parent : widget padre

    titulo : str
        Nombre del indicador.

    valor : str
        Valor del indicador.

    descripcion : str
        Texto inferior de la tarjeta.
    """

    def __init__(
        self,
        parent,
        titulo,
        valor="0",
        descripcion=""
    ):

        super().__init__(
            parent,
            corner_radius=8,
            fg_color="white",
            border_width=1,
            border_color="#C9C9C9"
        )

        # ==============================================
        # CONFIGURACIÓN
        # ==============================================

        self.configure(
            width=240,
            height=120
        )

        self.grid_propagate(False)

        # ==============================================
        # GRID INTERNO
        # ==============================================

        self.grid_columnconfigure(0, weight=1)

        # ==============================================
        # TÍTULO
        # ==============================================

        self.lbl_titulo = ctk.CTkLabel(
            self,
            text=titulo,
            font=("Arial", 12, "bold"),
            text_color="#4D4D4D"
        )

        self.lbl_titulo.grid(
            row=0,
            column=0,
            pady=(12, 5),
            padx=10
        )

        # ==============================================
        # VALOR
        # ==============================================

        self.lbl_valor = ctk.CTkLabel(
            self,
            text=valor,
            font=("Arial", 28, "bold"),
            text_color="#1A1A1A"
        )

        self.lbl_valor.grid(
            row=1,
            column=0
        )

        # ==============================================
        # DESCRIPCIÓN
        # ==============================================

        self.lbl_descripcion = ctk.CTkLabel(
            self,
            text=descripcion,
            font=("Arial", 11),
            text_color="#808080"
        )

        self.lbl_descripcion.grid(
            row=2,
            column=0,
            pady=(5, 12)
        )

    # ======================================================
    # ACTUALIZAR VALOR
    # ======================================================

    def actualizar_valor(self, valor):
        """
        Actualiza el valor mostrado por la tarjeta.
        """

        self.lbl_valor.configure(
            text=str(valor)
        )

    # ======================================================
    # ACTUALIZAR DESCRIPCIÓN
    # ======================================================

    def actualizar_descripcion(self, descripcion):
        """
        Actualiza el texto inferior.
        """

        self.lbl_descripcion.configure(
            text=descripcion
        )