"""Punto 2: ascenso de colinas sobre un espacio discreto."""
import json
from pathlib import Path

VALORES = [1, 4, 7, 5, 3, 6, 9, 8, 5]
REINICIOS = [1, 2, 3, 5]
CARPETA_SALIDA = Path(__file__).resolve().parent.parent / "outputs"


def ascenso_colinas(valores, inicio):
    """Devuelve el estado final y la trayectoria."""
    actual = inicio
    trayectoria = [actual]
    while True:
        vecinos = [v for v in (actual - 1, actual + 1)
                   if 0 <= v < len(valores)]
        mejor_vecino = max(vecinos, key=lambda v: valores[v])
        if valores[mejor_vecino] <= valores[actual]:
            return actual, trayectoria
        actual = mejor_vecino
        trayectoria.append(actual)


def maximos_locales(valores):
    """Estados sin ningun vecino de valor estrictamente mayor."""
    resultado = []
    for x, valor in enumerate(valores):
        vecinos = [v for v in (x - 1, x + 1) if 0 <= v < len(valores)]
        if all(valores[v] <= valor for v in vecinos):
            resultado.append(x)
    return resultado


def ejecutar():
    """Corre el ascenso desde los nueve estados y calcula los reinicios."""
    global_x = max(range(len(VALORES)), key=lambda x: VALORES[x])
    filas = []
    for inicio in range(len(VALORES)):
        final, trayectoria = ascenso_colinas(VALORES, inicio)
        filas.append({
            "inicio": inicio,
            "trayectoria": trayectoria,
            "final": final,
            "valor_final": VALORES[final],
            "llega_global": final == global_x,
        })
    exitos = sum(fila["llega_global"] for fila in filas)
    p_exito = exitos / len(VALORES)
    return {
        "valores": VALORES,
        "maximos_locales": maximos_locales(VALORES),
        "maximo_global": global_x,
        "filas": filas,
        "exitos": exitos,
        "total": len(VALORES),
        "proporcion": p_exito,
        "reinicios": [
            {"k": k, "prob_al_menos_un_exito": 1 - (1 - p_exito) ** k}
            for k in REINICIOS
        ],
    }


def main():
    resultados = ejecutar()
    CARPETA_SALIDA.mkdir(exist_ok=True)
    ruta = CARPETA_SALIDA / "punto2_resultados.json"
    ruta.write_text(json.dumps(resultados, indent=2), encoding="utf-8")
    for fila in resultados["filas"]:
        print(fila["inicio"], fila["trayectoria"], fila["final"],
              fila["valor_final"])
    print("Proporcion al global:", resultados["exitos"], "de",
          resultados["total"], resultados["proporcion"])
    for fila in resultados["reinicios"]:
        print("k =", fila["k"], fila["prob_al_menos_un_exito"])


if __name__ == "__main__":
    main()
