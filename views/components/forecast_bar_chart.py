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

    def crear_grafica(self):

        df = self.detalle.copy()

        # eliminar pronósticos vacíos
        df = df.dropna(subset=["pronostico_proximo_mes"])

        # Top N
        df = (
            df.sort_values(
                "pronostico_proximo_mes",
                ascending=False
            )
            .head(self.top_n)
        )

        figura = Figure(
            figsize=(6,4),
            dpi=100
        )

        ax = figura.add_subplot(111)

        ax.barh(
            df["NOMBRE_ELEMENTO"],
            df["pronostico_proximo_mes"]
        )

        ax.invert_yaxis()

        # ax.set_title(
        #     "Top 10 Consumo Esperado"
        # )

        ax.set_xlabel(
            "Unidades Pronosticadas"
        )

        ax.grid(
            axis="x",
            alpha=0.30
        )

        figura.tight_layout()

        canvas = FigureCanvasTkAgg(
            figura,
            self
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )