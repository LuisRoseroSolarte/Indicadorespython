import customtkinter as ctk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ForecastBarChart(ctk.CTkFrame):
    """
    Gráfico Top N del pronóstico de consumo mensual.
    """

    def __init__(
        self,
        parent,
        detalle,
        top_n=10
    ):

        super().__init__(parent)

        self.configure(
            fg_color="transparent"
        )

        self.detalle = detalle
        self.top_n = top_n

        self.crear_grafica()

    # =====================================================
    # GRÁFICA
    # =====================================================

    # def crear_grafica(self):

    #     df = self.detalle.copy()

    #     # eliminar pronósticos vacíos
    #     df = df.dropna(subset=["pronostico_proximo_mes"])

    #     # Top N
    #     df = (
    #         df.sort_values(
    #             "pronostico_proximo_mes",
    #             ascending=False
    #         )
    #         .head(self.top_n)
    #     )

    #     figura = Figure(
    #         figsize=(6,4),
    #         dpi=100
    #     )

    #     ax = figura.add_subplot(111)

    #     ax.barh(
    #         df["NOMBRE_ELEMENTO"],
    #         df["pronostico_proximo_mes"]
    #     )

    #     ax.invert_yaxis()

    #     # ax.set_title(
    #     #     "Top 10 Consumo Esperado"
    #     # )

    #     ax.set_xlabel(
    #         "Unidades Pronosticadas"
    #     )

    #     ax.grid(
    #         axis="x",
    #         alpha=0.30
    #     )

    #     figura.tight_layout()

    #     canvas = FigureCanvasTkAgg(
    #         figura,
    #         self
    #     )

    #     canvas.draw()

    #     canvas.get_tk_widget().pack(
    #         fill="both",
    #         expand=True
    #     )
    def crear_grafica(self):
    
        df = self.detalle.copy()

        # Eliminar pronósticos vacíos
        df = df.dropna(subset=["pronostico_proximo_mes"])

        # Top N
        df = (
            df.sort_values(
                "pronostico_proximo_mes",
                ascending=False
            )
            .head(self.top_n)
            .copy()
        )

        # =====================================================
        # ACORTAR NOMBRES LARGOS
        # =====================================================

        df["NOMBRE_ELEMENTO"] = (
            df["NOMBRE_ELEMENTO"]
            .apply(
                lambda nombre:
                nombre[:20] + "..."
                if len(nombre) > 20
                else nombre
            )
        )

        # =====================================================
        # CREAR FIGURA
        # =====================================================

        figura = Figure(
            figsize=(7, 4),
            dpi=100
        )

        ax = figura.add_subplot(111)

        ax.barh(
            df["NOMBRE_ELEMENTO"],
            df["pronostico_proximo_mes"],
            color="#2F7EB8"
        )

        ax.invert_yaxis()

        ax.set_xlabel(
            "Unidades Pronosticadas",
            fontsize=10
        )

        # Reducir tamaño de las etiquetas
        ax.tick_params(
            axis="y",
            labelsize=8
        )

        ax.tick_params(
            axis="x",
            labelsize=9
        )

        ax.grid(
            axis="x",
            alpha=0.30
        )

        # Dar más espacio al lado izquierdo
        figura.subplots_adjust(left=0.40)

        canvas = FigureCanvasTkAgg(
            figura,
            self
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )