import customtkinter as ctk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ProjectedInventoryChart(ctk.CTkFrame):
    """
    Top 10 menor nivel de inventario proyectado.
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

        df = df.dropna(
            subset=["nivel_inventario_proyectado"]
        )

        df = (
            df.sort_values(
                by="nivel_inventario_proyectado",
                ascending=True
            )
            .head(self.top_n)
        )

        # Nombres cortos
        df["NOMBRE_CORTO"] = (
            df["NOMBRE_ELEMENTO"]
            .str.slice(0, 15)
        )

        df.loc[
            df["NOMBRE_ELEMENTO"].str.len() > 15,
            "NOMBRE_CORTO"
        ] += "..."

        figura = Figure(
            figsize=(6,3),
            dpi=100
        )

        ax = figura.add_subplot(111)

        barras = ax.bar(
            df["NOMBRE_CORTO"],
            df["nivel_inventario_proyectado"]
        )

        # Etiquetas sobre cada barra
        for barra, valor in zip(
            barras,
            df["nivel_inventario_proyectado"]
        ):

            ax.text(
                barra.get_x() + barra.get_width()/2,
                barra.get_height(),
                f"{valor:.0f}",
                ha="center",
                va="bottom",
                fontsize=9
            )

        # ax.set_title(
        #     "Top 10 Menor Inventario Proyectado",
        #     fontsize=12,
        #     fontweight="bold"
        # )

        ax.set_ylabel(
            "Unidades"
        )

        ax.tick_params(
            axis="x",
            labelsize=5,#6, 
            rotation=45
        )

        ax.grid(
            axis="y",
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