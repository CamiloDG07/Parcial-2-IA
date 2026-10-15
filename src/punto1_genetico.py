"""Punto 1: algoritmo genetico para maximizar f(x) = x^2, x en 0..31."""
import json
import random
from pathlib import Path

POBLACION_INICIAL = ["00101", "01100", "10010", "11001"]
PROB_CRUCE = 0.8
PROB_MUTACION = 0.05
GENERACIONES = 20
SEMILLA = 42
OPTIMO = 31 ** 2
CARPETA_SALIDA = Path(__file__).resolve().parent.parent / "outputs"


def decodificar(cromosoma):
    """Valor entero de un cromosoma binario."""
    return int(cromosoma, 2)


def aptitud(cromosoma):
    """Aptitud f(x) = x^2."""
    return decodificar(cromosoma) ** 2


def ruleta(poblacion, generador):
    """Selecciona un individuo con probabilidad proporcional a su aptitud."""
    aptitudes = [aptitud(c) for c in poblacion]
    umbral = generador.random() * sum(aptitudes)
    acumulado = 0
    for cromosoma, valor in zip(poblacion, aptitudes):
        acumulado += valor
        if umbral < acumulado:
            return cromosoma
    return poblacion[-1]


def cruce_un_punto(padre1, padre2, generador):
    """Cruce de un punto con probabilidad PROB_CRUCE."""
    if generador.random() < PROB_CRUCE:
        punto = generador.randint(1, len(padre1) - 1)
        return (padre1[:punto] + padre2[punto:],
                padre2[:punto] + padre1[punto:])
    return padre1, padre2


def mutar(cromosoma, generador):
    """Invierte cada bit de forma independiente con PROB_MUTACION."""
    bits = []
    for bit in cromosoma:
        if generador.random() < PROB_MUTACION:
            bit = "1" if bit == "0" else "0"
        bits.append(bit)
    return "".join(bits)


def nueva_generacion(poblacion, generador):
    """Elitismo mas tres descendientes por ruleta, cruce y mutacion."""
    siguiente = [max(poblacion, key=aptitud)]
    while len(siguiente) < len(poblacion):
        padre1 = ruleta(poblacion, generador)
        padre2 = ruleta(poblacion, generador)
        hijo1, hijo2 = cruce_un_punto(padre1, padre2, generador)
        siguiente.append(mutar(hijo1, generador))
        if len(siguiente) < len(poblacion):
            siguiente.append(mutar(hijo2, generador))
    return siguiente


def algoritmo_genetico():
    """Ejecuta las 20 generaciones y devuelve el registro completo."""
    generador = random.Random(SEMILLA)
    poblacion = list(POBLACION_INICIAL)
    poblaciones = [list(poblacion)]
    historial = [max(aptitud(c) for c in poblacion)]
    for _ in range(GENERACIONES):
        poblacion = nueva_generacion(poblacion, generador)
        poblaciones.append(list(poblacion))
        historial.append(max(aptitud(c) for c in poblacion))
    mejor = max(poblacion, key=aptitud)
    return {
        "semilla": SEMILLA,
        "poblaciones": poblaciones,
        "historial_mejor_aptitud": historial,
        "distintos_por_generacion": [len(set(p)) for p in poblaciones],
        "poblacion_final": poblacion,
        "aptitudes_finales": [aptitud(c) for c in poblacion],
        "mejor_cromosoma": mejor,
        "mejor_x": decodificar(mejor),
        "mejor_aptitud": aptitud(mejor),
        "optimo_global": OPTIMO,
        "encontro_optimo": aptitud(mejor) == OPTIMO,
    }


def main():
    resultados = algoritmo_genetico()
    CARPETA_SALIDA.mkdir(exist_ok=True)
    ruta = CARPETA_SALIDA / "punto1_resultados.json"
    ruta.write_text(json.dumps(resultados, indent=2), encoding="utf-8")
    print("Mejor cromosoma final:", resultados["mejor_cromosoma"])
    print("x =", resultados["mejor_x"])
    print("Aptitud =", resultados["mejor_aptitud"])
    print("Historial:", resultados["historial_mejor_aptitud"])
    print("Poblacion final:", resultados["poblacion_final"])
    print("Encontro el optimo:", resultados["encontro_optimo"])


if __name__ == "__main__":
    main()
