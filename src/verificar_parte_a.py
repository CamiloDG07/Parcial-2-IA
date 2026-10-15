"""Calcula por codigo la parte A de los cinco puntos y la compara con el
desarrollo manual. Guarda los valores en outputs/parte_a_resultados.json."""
import itertools
import json
import math
from pathlib import Path

from punto2_ascenso_colinas import VALORES, ascenso_colinas, maximos_locales

CARPETA_SALIDA = Path(__file__).resolve().parent.parent / "outputs"


def cerca(valor, esperado, decimales=4):
    """Compara contra un valor redondeado a mano."""
    return round(valor, decimales) == esperado


def cierre_por_cruce(poblacion):
    """Cromosomas alcanzables solo con cruces de un punto, sin mutacion."""
    alcanzables = set(poblacion)
    generaciones = [set(poblacion)]
    while True:
        nuevos = set(alcanzables)
        for a, b in itertools.product(alcanzables, repeat=2):
            for punto in range(1, len(a)):
                nuevos.add(a[:punto] + b[punto:])
        if nuevos == alcanzables:
            return alcanzables, generaciones
        alcanzables = nuevos
        generaciones.append(set(nuevos))


def punto1():
    poblacion = ["00101", "01100", "10010", "11001"]
    xs = [int(c, 2) for c in poblacion]
    aptitudes = [x ** 2 for x in xs]
    suma = sum(aptitudes)
    probabilidades = [a / suma for a in aptitudes]
    assert xs == [5, 12, 18, 25]
    assert aptitudes == [25, 144, 324, 625]
    assert suma == 1118
    assert [round(p, 4) for p in probabilidades] == [
        0.0224, 0.1288, 0.2898, 0.5590]
    padre1, padre2, punto = "01100", "11001", 2
    hijo1 = padre1[:punto] + padre2[punto:]
    hijo2 = padre2[:punto] + padre1[punto:]
    assert (hijo1, hijo2) == ("01001", "11100")
    assert (int(hijo1, 2), int(hijo1, 2) ** 2) == (9, 81)
    assert (int(hijo2, 2), int(hijo2, 2) ** 2) == (28, 784)
    mutado = hijo1[:-1] + ("1" if hijo1[-1] == "0" else "0")
    assert (mutado, int(mutado, 2), int(mutado, 2) ** 2) == ("01000", 8, 64)
    unos_por_bit = [sum(c[i] == "1" for c in poblacion) for i in range(5)]
    cromosomas_con_cuarto_bit = [c for c in poblacion if c[3] == "1"]
    assert cromosomas_con_cuarto_bit == ["10010"]
    alcanzables, generaciones = cierre_por_cruce(poblacion)
    return {
        "cromosomas": poblacion,
        "x": xs,
        "aptitud": aptitudes,
        "suma": suma,
        "probabilidad": probabilidades,
        "hijo1": hijo1,
        "hijo2": hijo2,
        "x_hijo1": int(hijo1, 2),
        "x_hijo2": int(hijo2, 2),
        "aptitud_hijo1": int(hijo1, 2) ** 2,
        "aptitud_hijo2": int(hijo2, 2) ** 2,
        "mutado": mutado,
        "x_mutado": int(mutado, 2),
        "aptitud_mutado": int(mutado, 2) ** 2,
        "unos_por_posicion": unos_por_bit,
        "con_cuarto_bit_uno": cromosomas_con_cuarto_bit,
        "optimo_alcanzable_solo_cruce": "11111" in alcanzables,
        "optimo_en_un_cruce": "11111" in {
            a[:p] + b[p:] for a in poblacion for b in poblacion
            for p in range(1, 5)},
        "alcanzables_solo_cruce": len(alcanzables),
        "generaciones_cierre": len(generaciones),
    }


def punto2():
    desde0 = ascenso_colinas(VALORES, 0)
    desde4 = ascenso_colinas(VALORES, 4)
    assert desde0 == (2, [0, 1, 2])
    assert desde4 == (6, [4, 5, 6])
    assert maximos_locales(VALORES) == [2, 6]
    assert max(range(9), key=lambda x: VALORES[x]) == 6
    return {
        "desde0": {"final": desde0[0], "trayectoria": desde0[1]},
        "desde4": {"final": desde4[0], "trayectoria": desde4[1]},
        "maximos_locales": maximos_locales(VALORES),
        "valor_local_2": VALORES[2],
        "valor_global_6": VALORES[6],
    }


def punto3():
    casos = [("A", 3, 2, 5, 0.70), ("B", 2, 3, 5, 0.30),
             ("C", 2, 3, 1, 0.30)]
    filas = []
    for nombre, actual, candidato, t, u in casos:
        delta = candidato ** 2 - actual ** 2
        p = 1.0 if delta <= 0 else math.exp(-delta / t)
        filas.append({"caso": nombre, "actual": actual,
                      "candidato": candidato, "T": t, "u": u,
                      "delta": delta, "p": p, "acepta": u < p})
    assert [f["delta"] for f in filas] == [-5, 5, 5]
    assert cerca(filas[0]["p"], 1.0)
    assert cerca(filas[1]["p"], 0.3679)
    assert cerca(filas[2]["p"], 0.0067)
    assert [f["acepta"] for f in filas] == [True, True, False]
    return {"casos": filas}


def punto4():
    d = [2.0, 4.0, 5.0]
    tau = [1.0, 2.0, 1.0]
    alfa, beta = 1.0, 2.0
    pesos = [t ** alfa * (1.0 / x) ** beta for t, x in zip(tau, d)]
    suma = sum(pesos)
    probabilidades = [w / suma for w in pesos]
    assert [round(w, 4) for w in pesos] == [0.25, 0.125, 0.04]
    assert round(suma, 4) == 0.415
    assert [round(p, 4) for p in probabilidades] == [0.6024, 0.3012, 0.0964]
    rho, q, longitud = 0.2, 10.0, 10.0
    deposito = [q / longitud, 0.0, 0.0]
    nuevas = [(1 - rho) * t + dt for t, dt in zip(tau, deposito)]
    assert [round(t, 4) for t in nuevas] == [1.8, 1.6, 0.8]
    longitudes = [6.0, 8.0, 10.0]
    pesos_b = [(1.0 / x) ** beta for x in longitudes]
    p_b = [w / sum(pesos_b) for w in pesos_b]
    assert [round(p, 4) for p in p_b] == [0.5202, 0.2926, 0.1873]
    return {
        "distancia": d, "tau": tau, "pesos": pesos, "suma": suma,
        "probabilidad": probabilidades, "deposito": deposito,
        "tau_nueva": nuevas, "probabilidades_modelo_b": p_b,
    }


def punto5():
    w, c1, c2, r1, r2 = 0.5, 1.5, 1.5, 0.4, 0.6
    x, v, pbest, gbest = 4.0, -1.0, 2.0, 1.0
    inercia = w * v
    cognitivo = c1 * r1 * (pbest - x)
    social = c2 * r2 * (gbest - x)
    v_nueva = inercia + cognitivo + social
    x_nueva = x + v_nueva
    f_nueva = x_nueva ** 2
    assert [round(t, 4) for t in (inercia, cognitivo, social)] == [
        -0.5, -1.2, -2.7]
    assert round(v_nueva, 4) == -4.4
    assert round(x_nueva, 4) == -0.4
    assert round(f_nueva, 4) == 0.16
    assert (pbest ** 2, gbest ** 2) == (4.0, 1.0)
    assert f_nueva < pbest ** 2 and f_nueva < gbest ** 2
    return {
        "inercia": inercia, "cognitivo": cognitivo, "social": social,
        "v_nueva": v_nueva, "x_nueva": x_nueva, "f_nueva": f_nueva,
        "f_pbest": pbest ** 2, "f_gbest": gbest ** 2,
        "actualiza_pbest": f_nueva < pbest ** 2,
        "actualiza_gbest": f_nueva < gbest ** 2,
    }


def main():
    resultados = {
        "punto1": punto1(), "punto2": punto2(), "punto3": punto3(),
        "punto4": punto4(), "punto5": punto5(),
    }
    CARPETA_SALIDA.mkdir(exist_ok=True)
    ruta = CARPETA_SALIDA / "parte_a_resultados.json"
    ruta.write_text(json.dumps(resultados, indent=2), encoding="utf-8")
    print("Parte A verificada: todos los valores coinciden con el manual.")
    p1 = resultados["punto1"]
    print("Unos por posicion de bit:", p1["unos_por_posicion"])
    print("11111 en un solo cruce:", p1["optimo_en_un_cruce"])
    print("11111 alcanzable solo con cruces repetidos:",
          p1["optimo_alcanzable_solo_cruce"])


if __name__ == "__main__":
    main()
