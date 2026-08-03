import customtkinter as ctk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ForecastChart(ctk.CTkFrame):
    """
    Gráfico de Pronóstico de Consumo Mensual.

    Muestra:

    - Consumo histórico.
    - Línea de tendencia.
    - Pronóstico del siguiente mes.
    """

    def __init__(
        self,
        parent,
        historico,
        tendencia,
        pronostico
    ):

        super().__init__(parent)

        self.configure(
            fg_color="transparent"
        )

        self.historico = historico
        self.tendencia = tendencia
        self.pronostico = pronostico

        self.crear_grafica()

    # =====================================================
    # GRÁFICA
    # =====================================================

    def crear_grafica(self):

        figura = Figure(
            figsize=(6, 3.8),
            dpi=100
        )

        ax = figura.add_subplot(111)

        # ==========================================
        # HISTÓRICO
        # ==========================================

        meses = self.historico["PERIODO_MES"].astype(str)

        consumo = self.historico["SALIDAS"]

        ax.plot(
            meses,
            consumo,
            marker="o",
            linewidth=2,
            label="Consumo histórico"
        )

        # ==========================================
        # TENDENCIA
        # ==========================================

        ax.plot(
            meses,
            self.tendencia,
            linestyle="--",
            linewidth=2,
            label="Tendencia"
        )

        # ==========================================
        # PRONÓSTICO
        # ==========================================

        ultimo_mes = len(meses)

        ax.scatter(
            ultimo_mes,
            self.pronostico,
            s=90,
            marker="o",
            label="Pronóstico"
        )

        ax.text(
            ultimo_mes,
            self.pronostico,
            f"{self.pronostico:.1f}",
            fontsize=9,
            ha="left",
            va="bottom"
        )

        # ==========================================
        # Etiqueta del próximo mes
        # ==========================================

        etiquetas = list(meses)

        etiquetas.append("Próximo")

        posiciones = list(range(len(etiquetas)))

        ax.set_xticks(posiciones)

        ax.set_xticklabels(
            etiquetas,
            rotation=45
        )

        # ==========================================

        ax.set_title(
            "Pronóstico de Consumo Mensual",
            fontsize=12,
            fontweight="bold"
        )

        ax.set_ylabel(
            "Consumo"
        )

        ax.grid(
            alpha=0.3
        )

        ax.legend()

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