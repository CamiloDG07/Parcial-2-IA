"""Punto 4: modelo simplificado de ACO con tres rutas completas."""
import json
from pathlib import Path

import numpy as np

RUTAS = ["A-B-Z", "A-C-Z", "A-D-Z"]
LONGITUDES = np.array([6.0, 8.0, 10.0])
HORMIGAS = 10
ITERACIONES = 20
ALFA = 1.0
BETA = 2.0
RHO = 0.2
Q = 10.0
SEMILLA = 42
CARPETA_SALIDA = Path(__file__).resolve().parent.parent / "outputs"


def probabilidades(feromonas):
    """p_r = tau^alfa (1/L)^beta normalizado sobre las tres rutas."""
    pesos = feromonas ** ALFA * (1.0 / LONGITUDES) ** BETA
    return pesos / pesos.sum()


def aco():
    """Ejecuta las 20 iteraciones y devuelve el registro completo."""
    generador = np.random.default_rng(SEMILLA)
    feromonas = np.ones(len(RUTAS))
    registro = []
    totales = np.zeros(len(RUTAS), dtype=int)
    for iteracion in range(1, ITERACIONES + 1):
        p = probabilidades(feromonas)
        elegidas = generador.choice(len(RUTAS), size=HORMIGAS, p=p)
        conteo = np.bincount(elegidas, minlength=len(RUTAS))
        feromonas = (1.0 - RHO) * feromonas
        for ruta in elegidas:
            feromonas[ruta] += Q / LONGITUDES[ruta]
        totales += conteo
        registro.append({
            "iteracion": iteracion,
            "probabilidades": p.tolist(),
            "conteo": conteo.tolist(),
            "feromonas": feromonas.tolist(),
        })
    usadas = [i for i in range(len(RUTAS)) if totales[i] > 0]
    mejor_observada = min(usadas, key=lambda i: LONGITUDES[i])
    mas_elegida = int(np.argmax(totales))
    return {
        "semilla": SEMILLA,
        "rutas": RUTAS,
        "longitudes": LONGITUDES.tolist(),
        "probabilidades_iniciales": probabilidades(np.ones(3)).tolist(),
        "registro": registro,
        "frecuencias_totales": totales.tolist(),
        "decisiones": int(totales.sum()),
        "feromonas_finales": feromonas.tolist(),
        "probabilidades_finales": probabilidades(feromonas).tolist(),
        "mejor_ruta_observada": RUTAS[mejor_observada],
        "ruta_mas_elegida": RUTAS[mas_elegida],
    }


def main():
    resultados = aco()
    CARPETA_SALIDA.mkdir(exist_ok=True)
    ruta = CARPETA_SALIDA / "punto4_resultados.json"
    ruta.write_text(json.dumps(resultados, indent=2), encoding="utf-8")
    print("Probabilidades iniciales:", resultados["probabilidades_iniciales"])
    print("Frecuencias totales:", resultados["frecuencias_totales"])
    print("Feromonas finales:", resultados["feromonas_finales"])
    print("Mejor ruta observada:", resultados["mejor_ruta_observada"])
    for fila in resultados["registro"]:
        print(fila["iteracion"], fila["conteo"])


if __name__ == "__main__":
    main()
