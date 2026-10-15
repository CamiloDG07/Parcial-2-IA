"""Genera las figuras del informe a partir de los .json de outputs."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "outputs"
AZUL = "#1f5f99"
NARANJA = "#d9731a"
VERDE = "#2e8b57"
GRIS = "#6b6b6b"
COLORES_RUTAS = [AZUL, NARANJA, VERDE]

plt.rcParams.update({
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
})


def coma(eje):
    """Muestra el separador decimal como coma en un eje lineal."""
    eje.xaxis.set_major_formatter(FuncFormatter(
        lambda v, _: f"{v:g}".replace(".", ",")))
    eje.yaxis.set_major_formatter(FuncFormatter(
        lambda v, _: f"{v:g}".replace(".", ",")))


def cargar(nombre):
    ruta = SALIDA / f"{nombre}_resultados.json"
    return json.loads(ruta.read_text(encoding="utf-8"))


def guardar(figura, nombre):
    figura.savefig(SALIDA / f"{nombre}.png")
    plt.close(figura)


def figuras_punto1(datos):
    historial = datos["historial_mejor_aptitud"]
    figura, eje = plt.subplots(figsize=(6.0, 3.3))
    eje.step(range(len(historial)), historial, where="post", color=AZUL,
             marker="o", markersize=4, label="Mejor aptitud")
    eje.axhline(datos["optimo_global"], color=NARANJA, linestyle="--",
                label="Máximo posible f(31) = 961")
    eje.set_xlabel("Generación")
    eje.set_ylabel("Mejor aptitud")
    eje.set_xticks(range(0, len(historial), 2))
    eje.legend(loc="lower right", frameon=False)
    coma(eje)
    guardar(figura, "p1_historial")

    final = datos["poblacion_final"]
    aptitudes = datos["aptitudes_finales"]
    etiquetas = [f"Individuo {i + 1}\n{c}" for i, c in enumerate(final)]
    figura, eje = plt.subplots(figsize=(6.0, 3.3))
    barras = eje.bar(etiquetas, aptitudes, color=AZUL, width=0.55)
    eje.bar_label(barras, padding=2)
    eje.axhline(datos["optimo_global"], color=NARANJA, linestyle="--",
                label="Máximo posible f(31) = 961")
    eje.set_ylabel("Aptitud")
    eje.set_ylim(0, max(aptitudes + [datos["optimo_global"]]) * 1.3)
    eje.legend(loc="upper center", ncol=1, frameon=False)
    eje.grid(axis="x", visible=False)
    guardar(figura, "p1_poblacion_final")


def figuras_punto2(datos):
    valores = datos["valores"]
    xs = list(range(len(valores)))
    local, global_ = datos["maximos_locales"], datos["maximo_global"]
    figura, eje = plt.subplots(figsize=(6.0, 3.3))
    eje.plot(xs, valores, color=GRIS, marker="o", markersize=4)
    for x in local:
        if x != global_:
            eje.plot(x, valores[x], "D", color=NARANJA, markersize=8,
                     label="Máximo local")
    eje.plot(global_, valores[global_], "*", color=VERDE, markersize=14,
             label="Máximo global")
    eje.set_xlabel("Estado x")
    eje.set_ylabel("f(x)")
    eje.set_xticks(xs)
    eje.legend(loc="lower center", frameon=False, ncol=2)
    guardar(figura, "p2_funcion")

    figura, eje = plt.subplots(figsize=(6.0, 3.6))
    eje.plot(xs, valores, color="#bbbbbb", zorder=1)
    for fila in datos["filas"]:
        color = VERDE if fila["llega_global"] else NARANJA
        camino = fila["trayectoria"]
        for a, b in zip(camino[:-1], camino[1:]):
            giro = 0.35 if fila["inicio"] % 2 == 0 else -0.35
            eje.add_patch(FancyArrowPatch(
                (a, valores[a]), (b, valores[b]), color=color,
                arrowstyle="-|>", mutation_scale=9, linewidth=1.2,
                connectionstyle=f"arc3,rad={giro}", zorder=2))
        inicio = fila["inicio"]
        eje.plot(inicio, valores[inicio], "o", color=color, markersize=7,
                 zorder=3)
        eje.annotate(f"$x_0={inicio}$", (inicio, valores[inicio]),
                     textcoords="offset points", xytext=(0, -15),
                     ha="center", fontsize=7, color=color)
    eje.plot([], [], "o-", color=VERDE, label="Llega al máximo global")
    eje.plot([], [], "o-", color=NARANJA, label="Termina en máximo local")
    eje.set_xlabel("Estado x (círculo: estado inicial)")
    eje.set_ylabel("f(x)")
    eje.set_xticks(xs)
    eje.set_ylim(0, max(valores) + 2.5)
    eje.legend(loc="lower center", frameon=False, ncol=2)
    guardar(figura, "p2_trayectorias")


def figuras_punto3(datos):
    historial = datos["historial"]
    iteraciones = [f["iteracion"] for f in historial]
    figura, eje = plt.subplots(figsize=(6.0, 3.3))
    eje.semilogy(iteraciones, [f["temperatura"] for f in historial],
                 color=AZUL)
    eje.set_xlabel("Iteración")
    eje.set_ylabel("Temperatura (escala logarítmica)")
    guardar(figura, "p3_temperatura")

    figura, eje = plt.subplots(figsize=(6.0, 3.3))
    eje.step(iteraciones, [f["energia_actual"] for f in historial],
             where="post", color=AZUL, label="Energía del estado actual")
    eje.step(iteraciones, [f["mejor_energia"] for f in historial],
             where="post", color=NARANJA, linestyle="--",
             label="Mejor energía acumulada")
    eje.set_xlabel("Iteración")
    eje.set_ylabel("Energía E(x)")
    eje.legend(loc="upper right", frameon=False)
    guardar(figura, "p3_energia")


def figuras_punto4(datos):
    registro = datos["registro"]
    iteraciones = [f["iteracion"] for f in registro]
    probabilidad = np.array([f["probabilidades"] for f in registro])
    feromona = np.array([f["feromonas"] for f in registro])
    figura, eje = plt.subplots(figsize=(6.0, 3.3))
    for i, ruta in enumerate(datos["rutas"]):
        eje.plot(iteraciones, probabilidad[:, i], color=COLORES_RUTAS[i],
                 marker="o", markersize=3, label=f"Ruta {ruta}")
    eje.set_xlabel("Iteración")
    eje.set_ylabel("Probabilidad de elección")
    eje.set_xticks(range(0, 21, 2))
    eje.legend(loc="center right", frameon=False)
    coma(eje)
    guardar(figura, "p4_probabilidades")

    figura, eje = plt.subplots(figsize=(6.0, 3.3))
    for i, ruta in enumerate(datos["rutas"]):
        eje.semilogy(iteraciones, feromona[:, i], color=COLORES_RUTAS[i],
                     marker="o", markersize=3, label=f"Ruta {ruta}")
    eje.set_xlabel("Iteración (feromona al final de la iteración)")
    eje.set_ylabel("Feromona (escala logarítmica)")
    eje.set_xticks(range(0, 21, 2))
    eje.legend(loc="center right", frameon=False)
    guardar(figura, "p4_feromonas")

    figura, eje = plt.subplots(figsize=(6.0, 3.3))
    barras = eje.bar(datos["rutas"], datos["frecuencias_totales"],
                     color=COLORES_RUTAS, width=0.5)
    eje.bar_label(barras, padding=2)
    eje.set_xlabel("Ruta")
    eje.set_ylabel("Veces elegida (de 200 decisiones)")
    eje.grid(axis="x", visible=False)
    guardar(figura, "p4_frecuencias")


def figuras_punto5(datos):
    historial = datos["historial_mejor_aptitud"]
    figura, eje = plt.subplots(figsize=(6.0, 3.3))
    eje.semilogy(range(len(historial)), historial, color=AZUL, marker="o",
                 markersize=3)
    eje.set_xlabel("Iteración")
    eje.set_ylabel("Mejor aptitud global (escala logarítmica)")
    guardar(figura, "p5_historial")

    inicial = np.array(datos["posiciones_iniciales"])
    final = np.array(datos["posiciones_finales"])
    mejor = datos["mejor_posicion"]
    malla = np.linspace(-5, 5, 300)
    X, Y = np.meshgrid(malla, malla)
    figura, eje = plt.subplots(figsize=(5.0, 4.6))
    contorno = eje.contour(X, Y, X ** 2 + Y ** 2,
                           levels=[1, 4, 9, 16, 25, 36], colors="#999999",
                           linewidths=0.7)
    eje.clabel(contorno, fmt=lambda v: f"{v:g}", fontsize=7)
    eje.scatter(inicial[:, 0], inicial[:, 1], color=NARANJA, s=28,
                label="Posiciones iniciales")
    eje.scatter([mejor[0]], [mejor[1]], color=VERDE, marker="*", s=220,
                zorder=4, label="gbest final")
    eje.scatter(final[:, 0], final[:, 1], color=AZUL, marker="x", s=40,
                linewidths=1.2, zorder=5, label="Posiciones finales")
    eje.set_xlabel("x")
    eje.set_ylabel("y")
    eje.set_xlim(-5.2, 5.2)
    eje.set_ylim(-5.2, 5.2)
    eje.set_aspect("equal")
    eje.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=3,
               frameon=False, fontsize=8)
    coma(eje)
    guardar(figura, "p5_curvas_nivel")


def main():
    figuras_punto1(cargar("punto1"))
    figuras_punto2(cargar("punto2"))
    figuras_punto3(cargar("punto3"))
    figuras_punto4(cargar("punto4"))
    figuras_punto5(cargar("punto5"))
    print("Figuras generadas en", SALIDA)


if __name__ == "__main__":
    main()
