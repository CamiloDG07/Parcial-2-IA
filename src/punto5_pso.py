"""Punto 5: PSO para minimizar f(x, y) = x^2 + y^2 en [-5, 5]^2."""
import json
from pathlib import Path

import numpy as np

PARTICULAS = 10
DIMENSIONES = 2
LIMITE = 5.0
INERCIA = 0.5
C1 = 1.5
C2 = 1.5
ITERACIONES = 30
SEMILLA = 42
CARPETA_SALIDA = Path(__file__).resolve().parent.parent / "outputs"


def funcion(posiciones):
    """f(x, y) = x^2 + y^2 para cada fila de posiciones."""
    return np.sum(posiciones ** 2, axis=1)


def pso():
    """Ejecuta las 30 iteraciones y devuelve el registro completo."""
    generador = np.random.default_rng(SEMILLA)
    posiciones = generador.uniform(
        -LIMITE, LIMITE, size=(PARTICULAS, DIMENSIONES))
    velocidades = np.zeros((PARTICULAS, DIMENSIONES))
    posiciones_iniciales = posiciones.copy()
    mejores_personales = posiciones.copy()
    aptitud_personal = funcion(posiciones)
    indice = int(np.argmin(aptitud_personal))
    mejor_global = mejores_personales[indice].copy()
    aptitud_global = float(aptitud_personal[indice])
    historial = [aptitud_global]
    for _ in range(ITERACIONES):
        r1 = generador.uniform(0.0, 1.0, size=(PARTICULAS, DIMENSIONES))
        r2 = generador.uniform(0.0, 1.0, size=(PARTICULAS, DIMENSIONES))
        velocidades = (INERCIA * velocidades
                       + C1 * r1 * (mejores_personales - posiciones)
                       + C2 * r2 * (mejor_global - posiciones))
        posiciones = posiciones + velocidades
        fuera = np.abs(posiciones) > LIMITE
        posiciones = np.clip(posiciones, -LIMITE, LIMITE)
        velocidades[fuera] = 0.0
        aptitudes = funcion(posiciones)
        mejora = aptitudes < aptitud_personal
        mejores_personales[mejora] = posiciones[mejora]
        aptitud_personal[mejora] = aptitudes[mejora]
        indice = int(np.argmin(aptitud_personal))
        if aptitud_personal[indice] < aptitud_global:
            aptitud_global = float(aptitud_personal[indice])
            mejor_global = mejores_personales[indice].copy()
        historial.append(aptitud_global)
    return {
        "semilla": SEMILLA,
        "posiciones_iniciales": posiciones_iniciales.tolist(),
        "posiciones_finales": posiciones.tolist(),
        "velocidades_finales": velocidades.tolist(),
        "historial_mejor_aptitud": historial,
        "mejor_posicion": mejor_global.tolist(),
        "mejor_aptitud": aptitud_global,
        "distancia_al_origen": float(np.linalg.norm(mejor_global)),
        "distancia_media_finales": float(
            np.mean(np.linalg.norm(posiciones, axis=1))),
        "rapidez_media_final": float(
            np.mean(np.linalg.norm(velocidades, axis=1))),
    }


def main():
    resultados = pso()
    CARPETA_SALIDA.mkdir(exist_ok=True)
    ruta = CARPETA_SALIDA / "punto5_resultados.json"
    ruta.write_text(json.dumps(resultados, indent=2), encoding="utf-8")
    print("Mejor posicion:", resultados["mejor_posicion"])
    print("Mejor aptitud:", resultados["mejor_aptitud"])
    print("Distancia al origen:", resultados["distancia_al_origen"])
    print("Historial:", resultados["historial_mejor_aptitud"])


if __name__ == "__main__":
    main()
