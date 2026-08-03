import customtkinter as ctk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DepletionChart(ctk.CTkFrame):
    """
    Top 10 repuestos con menor tiempo estimado
    para agotarse.
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

        df = df.dropna(subset=["dias_agotamiento"])

        df = (
            df.sort_values(
                by="dias_agotamiento",
                ascending=True
            )
            .head(self.top_n)
        )

        # Barra mínima para que los ceros sean visibles
        df["dias_grafica"] = df["dias_agotamiento"].clip(lower=0.20)

        figura = Figure(
        figsize=(8,4),
        dpi=100
         )

        ax = figura.add_subplot(111)

        barras = ax.barh(
        df["NOMBRE_ELEMENTO"],
        df["dias_grafica"]
        )

        # Mostrar primero el más crítico
        ax.invert_yaxis()

        # Etiqueta con días
        for barra, dias in zip(
            barras,
            df["dias_agotamiento"]
            ):

            ax.text(
                barra.get_width() + 0.10,
                barra.get_y() + barra.get_height()/2,
                f"{dias:.2f} días",
                va="center",
                fontsize=9
            )

        # ax.set_title(
        #     "Top 10 Riesgo de Agotamiento",
        #     fontsize=12,
        #     fontweight="bold"
        # )

        ax.set_xlabel(
            "Días estimados para agotarse"
        )

        ax.grid(
            axis="x",
            alpha=0.30
        )

        figura.subplots_adjust(
            left=0.45,
            right=0.97,
            top=0.92,
            bottom=0.10
             )
        
        canvas = FigureCanvasTkAgg(
            figura,
            self
        )
        
        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )