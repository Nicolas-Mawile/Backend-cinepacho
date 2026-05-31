from io import BytesIO

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


COLOR_PRIMARIO = "#5143A5"   # Morado CinePacho
COLOR_SECUNDARIO = "#E58A1F" # Naranja CinePacho


class GraficasReportes:

    @staticmethod
    def crear_grafica_barras(
        labels: list[str],
        valores: list[float],
        titulo: str,
        xlabel: str = "",
        ylabel: str = "",
    ) -> BytesIO:

        buffer = BytesIO()

        pares = sorted(
            zip(labels, valores),
            key=lambda x: x[1],
            reverse=True
        )

        labels = [p[0] for p in pares]
        valores = [p[1] for p in pares]

        plt.figure(figsize=(10, 5))

        barras = plt.bar(
            labels,
            valores,
            color=COLOR_PRIMARIO
        )

        plt.title(
            titulo,
            fontsize=16,
            fontweight="bold"
        )

        if xlabel:
            plt.xlabel(xlabel)

        if ylabel:
            plt.ylabel(ylabel)

        for barra in barras:

            altura = barra.get_height()

            plt.text(
                barra.get_x() + barra.get_width()/2,
                altura,
                f"{altura:,.0f}",
                ha="center",
                va="bottom"
            )

        plt.tight_layout()

        plt.savefig(
            buffer,
            format="png",
            bbox_inches="tight"
        )

        buffer.seek(0)

        plt.close()

        return buffer

    @staticmethod
    def crear_grafica_pie(
        labels: list[str],
        valores: list[float],
        titulo: str,
    ) -> BytesIO:

        buffer = BytesIO()

        if sum(valores) == 0:
            valores = [1]
            labels = ["Sin datos"]

        plt.figure(figsize=(8, 8))

        plt.pie(
            valores,
            labels=labels,
            autopct="%1.1f%%",
            colors=[
                COLOR_PRIMARIO,
                COLOR_SECUNDARIO,
                "#6E5FD6",
                "#F2B15A",
            ]
        )

        plt.title(
            titulo,
            fontsize=16,
            fontweight="bold"
        )

        plt.tight_layout()

        plt.savefig(
            buffer,
            format="png",
            bbox_inches="tight"
        )

        buffer.seek(0)

        plt.close()

        return buffer

    @staticmethod
    def crear_histograma(
        valores: list[float],
        titulo: str,
        xlabel: str = "",
        ylabel: str = "Frecuencia",
        bins: int = 10,
    ) -> BytesIO:

        buffer = BytesIO()

        if not valores:
            valores = [0]

        plt.figure(figsize=(10, 5))

        plt.hist(
            valores,
            bins=bins,
            color=COLOR_PRIMARIO
        )

        plt.title(
            titulo,
            fontsize=16,
            fontweight="bold"
        )

        if xlabel:
            plt.xlabel(xlabel)

        if ylabel:
            plt.ylabel(ylabel)

        plt.tight_layout()

        plt.savefig(
            buffer,
            format="png",
            bbox_inches="tight"
        )

        buffer.seek(0)

        plt.close()

        return buffer