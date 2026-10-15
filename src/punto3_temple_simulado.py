"""Punto 3: temple simulado para minimizar E(x) = x^2, x en -5..5."""
import json
import math
import random
from pathlib import Path

LIMITE = 5
ESTADO_INICIAL = 5
TEMPERATURA_INICIAL = 10.0
FACTOR_ENFRIAMIENTO = 0.90
ITERACIONES = 100
SEMILLA = 42
CARPETA_SALIDA = Path(__file__).resolve().parent.parent / "outputs"


def energia(x):
    """Energia E(x) = x^2."""
    return x ** 2


def prob_aceptacion(delta, temperatura):
    """1 si delta <= 0; exp(-delta / T) si delta > 0."""
    if delta <= 0:
        return 1.0
    return math.exp(-delta / temperatura)


def temple_simulado():
    """Ejecuta 100 iteraciones y devuelve el registro completo.

    La fila 0 del historial es el estado inicial; no decide nada.
    """
    generador = random.Random(SEMILLA)
    actual = ESTADO_INICIAL
    mejor = actual
    temperatura = TEMPERATURA_INICIAL
    historial = [{
        "iteracion": 0,
        "temperatura": None,
        "candidato": None,
        "delta": None,
        "probabilidad": None,
        "u": None,
        "aceptado": None,
        "estado_actual": actual,
        "energia_actual": energia(actual),
        "mejor_estado": mejor,
        "mejor_energia": energia(mejor),
    }]
    for iteracion in range(1, ITERACIONES + 1):
        vecinos = [v for v in (actual - 1, actual + 1)
                   if -LIMITE <= v <= LIMITE]
        if len(vecinos) == 1:
            candidato = vecinos[0]
        else:
            candidato = generador.choice(vecinos)
        u = generador.random()
        delta = energia(candidato) - energia(actual)
        probabilidad = prob_aceptacion(delta, temperatura)
        aceptado = u < probabilidad
        if aceptado:
            actual = candidato
        if energia(actual) < energia(mejor):
            mejor = actual
        historial.append({
            "iteracion": iteracion,
            "temperatura": temperatura,
            "candidato": candidato,
            "delta": delta,
            "probabilidad": probabilidad,
            "u": u,
            "aceptado": aceptado,
            "estado_actual": actual,
            "energia_actual": energia(actual),
            "mejor_estado": mejor,
            "mejor_energia": energia(mejor),
        })
        temperatura *= FACTOR_ENFRIAMIENTO
    return {
        "semilla": SEMILLA,
        "estado_inicial": ESTADO_INICIAL,
        "energia_inicial": energia(ESTADO_INICIAL),
        "historial": historial,
        "estado_final": actual,
        "energia_final": energia(actual),
        "mejor_solucion": mejor,
        "energia_minima": energia(mejor),
        "peores_aceptados": sum(
            1 for fila in historial if fila["aceptado"] and fila["delta"] > 0
        ),
        "final_coincide_con_mejor": actual == mejor,
    }


def main():
    resultados = temple_simulado()
    CARPETA_SALIDA.mkdir(exist_ok=True)
    ruta = CARPETA_SALIDA / "punto3_resultados.json"
    ruta.write_text(json.dumps(resultados, indent=2), encoding="utf-8")
    print("Mejor solucion:", resultados["mejor_solucion"])
    print("Energia minima:", resultados["energia_minima"])
    print("Estado final:", resultados["estado_final"])
    print("Peores aceptados:", resultados["peores_aceptados"])
    print("Estados:", [f["estado_actual"] for f in resultados["historial"]])


if __name__ == "__main__":
    main()
