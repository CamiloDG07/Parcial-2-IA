"""Genera las tablas y los valores numericos del informe desde los .json.

Ninguna cifra de los resultados se escribe a mano en el .tex: todo se
lee de outputs y se escribe en informe/tablas.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "outputs"
TABLAS = RAIZ / "informe" / "tablas"
MACROS = []


def cargar(nombre):
    ruta = SALIDA / f"{nombre}_resultados.json"
    return json.loads(ruta.read_text(encoding="utf-8"))


def num(valor, decimales=4):
    """Numero con coma decimal, en modo matematico."""
    texto = f"{abs(valor):.{decimales}f}".replace(".", "{,}")
    signo = "-" if valor < 0 and float(f"{abs(valor):.{decimales}f}") else ""
    return f"${signo}{texto}$"


def entero(valor):
    return f"${valor}$"


def cientifico(valor, decimales=2):
    """Notacion cientifica con coma decimal."""
    mantisa, exponente = f"{valor:.{decimales}e}".split("e")
    mantisa = mantisa.replace(".", "{,}")
    return f"${mantisa}\\times10^{{{int(exponente)}}}$"


def porcentaje(valor, decimales=1):
    texto = f"{100 * valor:.{decimales}f}".replace(".", "{,}")
    return f"${texto}$\\,\\%"


def macro(nombre, valor):
    """Define un macro; los numeros usan ensuremath (texto o formula)."""
    if valor.startswith("$") and valor.endswith("$"):
        valor = f"\\ensuremath{{{valor[1:-1]}}}"
    MACROS.append(f"\\newcommand{{\\{nombre}}}{{{valor}}}")


def tabla(nombre, encabezados, filas, caption, etiqueta, formato=None,
          tamano="\\small", espaciado=1.15, separacion=6):
    """Escribe una tabla con cuadricula visible y pie debajo."""
    columnas = formato or "|" + "c|" * len(encabezados)
    lineas = [
        "\\begin{table}[H]", "\\centering", tamano,
        f"\\setlength{{\\tabcolsep}}{{{separacion}pt}}",
        f"\\renewcommand{{\\arraystretch}}{{{espaciado}}}",
        f"\\begin{{tabular}}{{{columnas}}}", "\\hline",
        " & ".join(f"\\textbf{{{h}}}" for h in encabezados) + " \\\\",
        "\\hline",
    ]
    for fila in filas:
        lineas.append(" & ".join(str(c) for c in fila) + " \\\\")
        lineas.append("\\hline")
    lineas += ["\\end{tabular}", f"\\caption{{{caption}}}",
               f"\\label{{{etiqueta}}}", "\\end{table}"]
    (TABLAS / f"{nombre}.tex").write_text(
        "\n".join(lineas) + "\n", encoding="utf-8")


def en_bloques(filas, bloques):
    """Reparte filas en columnas de bloques para tablas compactas."""
    alto = -(-len(filas) // bloques)
    resultado = []
    for i in range(alto):
        fila = []
        for b in range(bloques):
            j = b * alto + i
            ancho = len(filas[0])
            fila += filas[j] if j < len(filas) else [""] * ancho
        resultado.append(fila)
    return resultado


def texttt(texto):
    return f"\\texttt{{{texto}}}"


def punto1(a, b):
    tabla("p1_a_ruleta",
          ["Cromosoma", "$x$", "$f(x)$", "Probabilidad de ruleta"],
          [[texttt(c), entero(x), entero(f), num(p)]
           for c, x, f, p in zip(a["cromosomas"], a["x"], a["aptitud"],
                                 a["probabilidad"])]
          + [["Suma", "", entero(a["suma"]), num(sum(a["probabilidad"]))]],
          "Decodificación, aptitud y probabilidad de selección por ruleta "
          "de la población inicial.", "tab:p1a-ruleta")
    tabla("p1_a_cruce",
          ["Individuo", "Cromosoma", "$x$", "$f(x)$"],
          [["Padre 1", texttt("01100"), entero(12), entero(144)],
           ["Padre 2", texttt("11001"), entero(25), entero(625)],
           ["Descendiente 1", texttt(a["hijo1"]), entero(a["x_hijo1"]),
            entero(a["aptitud_hijo1"])],
           ["Descendiente 2", texttt(a["hijo2"]), entero(a["x_hijo2"]),
            entero(a["aptitud_hijo2"])],
           ["Descendiente 1 mutado", texttt(a["mutado"]),
            entero(a["x_mutado"]), entero(a["aptitud_mutado"])]],
          "Cruce de un punto tras el segundo bit y mutación del último bit "
          "del primer descendiente.", "tab:p1a-cruce")
    assert a["x_hijo1"] ** 2 > a["aptitud_mutado"], "la mutacion empeora"
    assert a["con_cuarto_bit_uno"] == ["10010"]
    assert not a["optimo_en_un_cruce"]
    assert a["optimo_alcanzable_solo_cruce"]

    hist = b["historial_mejor_aptitud"]
    pob = b["poblaciones"]
    assert all(x <= y for x, y in zip(hist, hist[1:])), "elitismo"
    tabla("p1_b_resumen",
          ["Mejor cromosoma", "$x$", "Aptitud", "Máximo posible",
           "Óptimo hallado"],
          [[texttt(b["mejor_cromosoma"]), entero(b["mejor_x"]),
            entero(b["mejor_aptitud"]), entero(b["optimo_global"]),
            "Sí" if b["encontro_optimo"] else "No"]],
          "Mejor individuo de la población final (generación 20).",
          "tab:p1b-resumen")
    filas = [[entero(g), entero(v)] for g, v in enumerate(hist)]
    tabla("p1_b_historial", ["Gen.", "Mejor aptitud"] * 3,
          en_bloques(filas, 3),
          "Historial de la mejor aptitud por generación (la generación 0 "
          "es la población inicial).", "tab:p1b-historial",
          tamano="\\footnotesize", separacion=4)
    filas = [[entero(g), " ".join(texttt(c) for c in p),
              entero(len(set(p)))] for g, p in enumerate(pob)]
    tabla("p1_b_poblaciones",
          ["Gen.", "Población", "Distintos"] * 2,
          en_bloques(filas, 2),
          "Población de cada generación y número de cromosomas distintos.",
          "tab:p1b-poblaciones", tamano="\\footnotesize", separacion=3,
          formato="|c|l|c|c|l|c|")
    macro("PunoMejor", texttt(b["mejor_cromosoma"]))
    macro("PunoX", entero(b["mejor_x"]))
    macro("PunoAptitud", entero(b["mejor_aptitud"]))
    macro("PunoOptimo", entero(b["optimo_global"]))
    meseta = hist[1]
    primera = hist.index(b["optimo_global"])
    assert all(v == meseta for v in hist[1:primera])
    macro("PunoMeseta", entero(meseta))
    macro("PunoPrimeraGen", entero(primera))
    macro("PunoGenAntes", entero(primera - 1))
    macro("PunoInicial", entero(hist[0]))
    sin_bit = [g for g, p in enumerate(pob)
               if all(c[3] == "0" for c in p)]
    assert sin_bit == list(range(1, primera)), sin_bit
    assert any(c[3] == "1" for c in pob[0])
    assert any(c[3] == "1" for c in pob[primera])
    macro("PunoDistintosFinal", entero(len(set(b["poblacion_final"]))))
    assert "10010" not in pob[1]
    meseta_distintos = max(len(set(p)) for p in pob[3:primera])
    assert meseta_distintos == 2
    macro("PunoMaxDistintosMeseta", entero(meseta_distintos))
    unicos_uno = sum(1 for p in pob[1:] if len(set(p)) == 1)
    macro("PunoGenUniformes", entero(unicos_uno))
    # Probabilidad de formar 11111 desde 11101 solo por mutacion
    p_hijo = 0.05 * 0.95 ** 4
    p_gen = 1 - (1 - p_hijo) ** 3
    macro("PunoProbHijo", num(p_hijo))
    macro("PunoProbGen", num(p_gen))
    macro("PunoProbSinExito", num((1 - p_gen) ** 20))
    macro("PunoProbSinExitoPorc", porcentaje((1 - p_gen) ** 20))
    macro("PunoProbGenPorc", porcentaje(p_gen))
    macro("PunoProbHijoPorc", porcentaje(p_hijo))
    macro("PunoSuma", entero(a["suma"]))
    macro("PunoProbMax", num(a["probabilidad"][3]))


def punto2(a, b):
    valores = b["valores"]
    locales = b["maximos_locales"]
    glob = b["maximo_global"]
    filas = []
    for x, v in enumerate(valores):
        vecinos = [w for w in (x - 1, x + 1) if 0 <= w < len(valores)]
        if x == glob:
            tipo = "Máximo global"
        elif x in locales:
            tipo = "Máximo local"
        else:
            tipo = "Ninguno"
        filas.append([entero(x), entero(v), ", ".join(
            f"${w}$" for w in vecinos), tipo])
    tabla("p2_a_clasificacion",
          ["$x$", "$f(x)$", "Vecinos", "Clasificación"], filas,
          "Clasificación de los nueve estados del espacio.",
          "tab:p2a-clasificacion")
    flecha = " $\\to$ ".join
    tabla("p2_a_trazas",
          ["Inicio $x_0$", "Estados visitados", "Estado final", "$f$ final"],
          [[entero(0), flecha(f"${s}$" for s in a["desde0"]["trayectoria"]),
            entero(a["desde0"]["final"]), entero(a["valor_local_2"])],
           [entero(4), flecha(f"${s}$" for s in a["desde4"]["trayectoria"]),
            entero(a["desde4"]["final"]), entero(a["valor_global_6"])]],
          "Ascenso de colinas calculado desde $x_0=0$ y desde $x_0=4$.",
          "tab:p2a-trazas")
    tabla("p2_b_trayectorias",
          ["Estado inicial", "Trayectoria", "Estado final", "Valor final",
           "¿Global?"],
          [[entero(f["inicio"]),
            flecha(f"${s}$" for s in f["trayectoria"]),
            entero(f["final"]), entero(f["valor_final"]),
            "Sí" if f["llega_global"] else "No"] for f in b["filas"]],
          "Resultado del ascenso de colinas desde los nueve estados "
          "iniciales.", "tab:p2b-trayectorias")
    tabla("p2_b_reinicios",
          ["Reinicios $k$", "$P(\\text{al menos un éxito})$"],
          [[entero(f["k"]), num(f["prob_al_menos_un_exito"])]
           for f in b["reinicios"]],
          "Probabilidad de alcanzar el máximo global con $k$ reinicios "
          "independientes desde un estado uniforme.", "tab:p2b-reinicios")
    macro("PdosExitos", entero(b["exitos"]))
    macro("PdosTotal", entero(b["total"]))
    macro("PdosProporcion", porcentaje(b["proporcion"]))
    macro("PdosFallo", num(1 - b["proporcion"]))
    macro("PdosFrac", f"${b['exitos']}/{b['total']}$")
    macro("PdosFalloFrac", f"${b['total'] - b['exitos']}/{b['total']}$")
    macro("PdosProbTres", num(b["reinicios"][2]["prob_al_menos_un_exito"]))
    macro("PdosProbCinco", num(b["reinicios"][3]["prob_al_menos_un_exito"]))
    macro("PdosProbUno", num(b["reinicios"][0]["prob_al_menos_un_exito"]))
    macro("PdosProbDos", num(b["reinicios"][1]["prob_al_menos_un_exito"]))
    inicios_local = [f["inicio"] for f in b["filas"] if not f["llega_global"]]
    assert inicios_local == [0, 1, 2, 3]
    assert [f["inicio"] for f in b["filas"] if f["llega_global"]] == [
        4, 5, 6, 7, 8]


def punto3(a, b):
    tabla("p3_a_casos",
          ["Caso", "Actual", "Candidato", "$T$", "$u$", "$\\Delta E$",
           "$P(\\text{aceptar})$", "Decisión"],
          [[c["caso"], entero(c["actual"]), entero(c["candidato"]),
            entero(c["T"]), num(c["u"], 2), entero(c["delta"]),
            num(c["p"]), "Acepta" if c["acepta"] else "Rechaza"]
           for c in a["casos"]],
          "Aceptación de cada transición analizada de forma independiente.",
          "tab:p3a-casos")
    hist = b["historial"]
    tabla("p3_b_resumen",
          ["Estado inicial", "Mejor solución", "Energía mínima",
           "Estado final", "Energía final"],
          [[entero(b["estado_inicial"]), entero(b["mejor_solucion"]),
            entero(b["energia_minima"]), entero(b["estado_final"]),
            entero(b["energia_final"])]],
          "Resultado del temple simulado tras 100 iteraciones.",
          "tab:p3b-resumen")
    filas = [[entero(f["iteracion"]), num(f["temperatura"], 4)]
             for f in hist]
    tabla("p3_b_temperatura", ["Iter.", "$T$"] * 5,
          en_bloques(filas, 5),
          "Historial de la temperatura usada en cada iteración.",
          "tab:p3b-temperatura", tamano="\\scriptsize", separacion=3)
    filas = [[entero(f["iteracion"]), entero(f["energia_actual"]),
              entero(f["mejor_energia"])] for f in hist]
    tabla("p3_b_energia", ["Iter.", "Actual", "Mejor"] * 4,
          en_bloques(filas, 4),
          "Historial de la energía del estado actual y de la mejor "
          "energía acumulada.", "tab:p3b-energia", tamano="\\scriptsize",
          separacion=3)
    mejor_it = next(f["iteracion"] for f in hist
                    if f["mejor_energia"] == b["energia_minima"])
    salida = next(f["iteracion"] for f in hist
                  if f["iteracion"] > mejor_it
                  and f["energia_actual"] > b["energia_minima"])
    peor_que_mejor = sum(1 for f in hist
                         if f["energia_actual"] > f["mejor_energia"])
    propuestas = [f for f in hist if f["delta"] > 0]
    aceptados = [f for f in propuestas if f["aceptado"]]
    assert len(aceptados) == b["peores_aceptados"]
    ultimo = max(f["iteracion"] for f in aceptados)
    assert b["final_coincide_con_mejor"]
    macro("PtresEnergiaMaxima", entero(max(
        f["energia_actual"] for f in hist if f["iteracion"] > mejor_it)))
    ultima_positiva = max(
        f["iteracion"] for f in hist if f["energia_actual"] > 0)
    assert all(f["energia_actual"] == 0 for f in hist[ultima_positiva:])
    macro("PtresDesdeFijo", entero(ultima_positiva + 1))
    macro("PtresMejor", entero(b["mejor_solucion"]))
    macro("PtresEnergia", entero(b["energia_minima"]))
    macro("PtresFinal", entero(b["estado_final"]))
    macro("PtresPeores", entero(b["peores_aceptados"]))
    macro("PtresPropuestasPeores", entero(len(propuestas)))
    macro("PtresIterMejor", entero(mejor_it))
    macro("PtresIterSalida", entero(salida))
    macro("PtresPeorQueMejor", entero(peor_que_mejor))
    macro("PtresUltimoPeor", entero(ultimo))
    macro("PtresTempUltimoPeor", num(
        next(f["temperatura"] for f in hist if f["iteracion"] == ultimo), 2))
    macro("PtresTempFinal", cientifico(hist[-1]["temperatura"], 2))
    macro("PtresTempInicial", num(hist[0]["temperatura"], 1))
    macro("PtresEnergiaInicial", entero(b["energia_inicial"]))
    macro("PtresEnergiaSalida", entero(next(
        f["energia_actual"] for f in hist if f["iteracion"] == salida)))
    macro("PtresPeoresMitad", entero(sum(
        1 for f in aceptados if f["iteracion"] <= 50)))
    macro("PtresPropuestasMitad", entero(sum(
        1 for f in propuestas if f["iteracion"] <= 50)))
    macro("PtresPropuestasSegunda", entero(sum(
        1 for f in propuestas if f["iteracion"] > 50)))


def punto4(a, b):
    nombres = ["$A\\to B$", "$A\\to C$", "$A\\to D$"]
    tabla("p4_a_pesos",
          ["Arista", "$d$", "$\\tau$", "Peso $\\tau\\eta^2$",
           "Probabilidad"],
          [[nombres[i], entero(int(a["distancia"][i])),
            entero(int(a["tau"][i])), num(a["pesos"][i]),
            num(a["probabilidad"][i])] for i in range(3)]
          + [["Suma", "", "", num(a["suma"]),
              num(sum(a["probabilidad"]))]],
          "Peso y probabilidad de elección desde el nodo $A$.",
          "tab:p4a-pesos")
    tabla("p4_a_feromonas",
          ["Arista", "$\\tau$ actual", "$(1-\\rho)\\tau$", "$\\Delta\\tau$",
           "$\\tau$ nueva"],
          [[nombres[i], num(a["tau"][i], 1), num(0.8 * a["tau"][i], 1),
            num(a["deposito"][i], 1), num(a["tau_nueva"][i], 1)]
           for i in range(3)],
          "Actualización de la feromona tras una hormiga con $L=10$ que "
          "usa $A\\to B$.", "tab:p4a-feromonas")
    rutas = list(b["rutas"])
    total = b["decisiones"]
    tabla("p4_b_frecuencias",
          ["Ruta", "Longitud", "Frecuencia", "Proporción"],
          [[rutas[i], entero(int(b["longitudes"][i])),
            entero(b["frecuencias_totales"][i]),
            porcentaje(b["frecuencias_totales"][i] / total)]
           for i in range(3)]
          + [["Total", "", entero(total), porcentaje(1.0)]],
          "Frecuencia total de elección de cada ruta en las 200 decisiones.",
          "tab:p4b-frecuencias")
    tabla("p4_b_feromonas",
          ["Ruta", "Feromona inicial", "Feromona final",
           "Probabilidad final"],
          [[rutas[i], entero(1), num(b["feromonas_finales"][i], 4),
            num(b["probabilidades_finales"][i])] for i in range(3)],
          "Feromona de cada ruta al terminar la iteración 20 y "
          "probabilidad de elección que implicaría.", "tab:p4b-feromonas")
    reg = b["registro"]
    filas = [[entero(f["iteracion"])] + [entero(c) for c in f["conteo"]]
             for f in reg]
    tabla("p4_b_conteo", ["Iter."] + rutas + ["Iter."] + rutas,
          en_bloques(filas, 2),
          "Elecciones de cada ruta por iteración (diez hormigas).",
          "tab:p4b-conteo", formato="|c|c|c|c|c|c|c|c|")
    filas = [[entero(f["iteracion"])] + [num(p) for p in f["probabilidades"]]
             for f in reg]
    tabla("p4_b_probabilidades", ["Iter."] + rutas + ["Iter."] + rutas,
          en_bloques(filas, 2),
          "Probabilidad de elección de cada ruta al inicio de cada "
          "iteración.", "tab:p4b-probabilidades",
          formato="|c|c|c|c|c|c|c|c|")
    assert b["mejor_ruta_observada"] == "A-B-Z"
    p0, pf = reg[0]["probabilidades"], reg[-1]["probabilidades"]
    for i, sufijo in enumerate(["B", "C", "D"]):
        macro(f"Pcuatro{sufijo}Ini", num(p0[i]))
        macro(f"Pcuatro{sufijo}Fin", num(pf[i]))
        macro(f"Pcuatro{sufijo}Frec", entero(b["frecuencias_totales"][i]))
        macro(f"Pcuatro{sufijo}Porc", porcentaje(
            b["frecuencias_totales"][i] / total))
        macro(f"Pcuatro{sufijo}Fer", num(b["feromonas_finales"][i], 2))
        macro(f"Pcuatro{sufijo}Dep", num(10.0 / b["longitudes"][i], 2))
        macro(f"Pcuatro{sufijo}Dos", num(reg[1]["probabilidades"][i]))
        macro(f"Pcuatro{sufijo}Cinco", num(reg[4]["probabilidades"][i]))
    todas = next(f["iteracion"] for f in reg if f["conteo"][0] == 10)
    assert all(f["conteo"][0] == 10 for f in reg[todas - 1:])
    macro("PcuatroIterTodas", entero(todas))
    macro("PcuatroPrimeraB", entero(reg[0]["conteo"][0]))
    macro("PcuatroPrimeraC", entero(reg[0]["conteo"][1]))
    macro("PcuatroPrimeraD", entero(reg[0]["conteo"][2]))
    macro("PcuatroUltimaC", entero(max(
        f["iteracion"] for f in reg if f["conteo"][1] > 0)))
    macro("PcuatroUltimaD", entero(max(
        f["iteracion"] for f in reg if f["conteo"][2] > 0)))
    macro("PcuatroPicoC", num(max(f["feromonas"][1] for f in reg), 2))
    macro("PcuatroIterPicoC", entero(max(
        reg, key=lambda f: f["feromonas"][1])["iteracion"]))
    macro("PcuatroDecisiones", entero(total))
    iter_pico_d = max(reg, key=lambda f: f["feromonas"][2])["iteracion"]
    macro("PcuatroIterPicoD", entero(iter_pico_d))
    macro("PcuatroPesoB", num(a["pesos"][0]))
    macro("PcuatroProbA", num(a["probabilidad"][0]))
    macro("PcuatroProbAPorc", porcentaje(a["probabilidad"][0], 2))
    macro("PcuatroSumaPesos", num(a["suma"], 3))


def punto5(a, b):
    tabla("p5_a_terminos",
          ["Concepto", "Expresión", "Valor"],
          [["Inercia", "$w\\,v=0{,}5\\cdot(-1)$", num(a["inercia"], 2)],
           ["Cognitivo",
            "$c_1r_1(p_{best}-x)=1{,}5\\cdot0{,}4\\cdot(2-4)$",
            num(a["cognitivo"], 2)],
           ["Social",
            "$c_2r_2(g_{best}-x)=1{,}5\\cdot0{,}6\\cdot(1-4)$",
            num(a["social"], 2)],
           ["Nueva velocidad", "inercia + cognitivo + social",
            num(a["v_nueva"], 2)],
           ["Nueva posición", "$x+v_{nuevo}=4+(-4{,}4)$",
            num(a["x_nueva"], 2)],
           ["Aptitud", "$f(-0{,}4)$", num(a["f_nueva"], 2)]],
          "Cálculo de un paso de la partícula con $r_1=0{,}4$ y "
          "$r_2=0{,}6$.", "tab:p5a-terminos",
          formato="|l|l|c|")
    tabla("p5_a_memorias",
          ["Memoria", "Aptitud actual", "Aptitud nueva", "¿Se actualiza?"],
          [["$p_{best}$", num(a["f_pbest"], 2), num(a["f_nueva"], 2),
            "Sí" if a["actualiza_pbest"] else "No"],
           ["$g_{best}$", num(a["f_gbest"], 2), num(a["f_nueva"], 2),
            "Sí" if a["actualiza_gbest"] else "No"]],
          "Actualización de las memorias personal y global.",
          "tab:p5a-memorias")
    tabla("p5_b_resumen",
          ["Mejor posición $(x,y)$", "$f(x,y)$", "Distancia al origen"],
          [[f"$({cientifico(b['mejor_posicion'][0], 3)[1:-1]},\\;"
            f"{cientifico(b['mejor_posicion'][1], 3)[1:-1]})$",
            cientifico(b["mejor_aptitud"], 3),
            cientifico(b["distancia_al_origen"], 3)]],
          "Mejor posición global tras 30 iteraciones.", "tab:p5b-resumen")
    hist = b["historial_mejor_aptitud"]
    filas = [[entero(i), cientifico(v, 3)] for i, v in enumerate(hist)]
    tabla("p5_b_historial", ["Iter.", "Mejor aptitud global"] * 3,
          en_bloques(filas, 3),
          "Historial de la mejor aptitud global (la iteración 0 es la "
          "población inicial).", "tab:p5b-historial", tamano="\\footnotesize",
          separacion=4)
    assert all(x >= y for x, y in zip(hist, hist[1:]))
    macro("PcincoX", cientifico(b["mejor_posicion"][0], 3))
    macro("PcincoY", cientifico(b["mejor_posicion"][1], 3))
    macro("PcincoF", cientifico(b["mejor_aptitud"], 3))
    macro("PcincoDist", cientifico(b["distancia_al_origen"], 3))
    macro("PcincoFInicial", num(hist[0], 3))
    macro("PcincoFUno", num(hist[1], 3))
    macro("PcincoDistMedia", cientifico(b["distancia_media_finales"], 3))
    macro("PcincoRapidez", cientifico(b["rapidez_media_final"], 3))
    mejora = max(i for i in range(1, len(hist)) if hist[i] < hist[i - 1])
    macro("PcincoUltimaMejora", entero(mejora))
    macro("PcincoSinMejora", entero(len(hist) - 1 - mejora))
    macro("PcincoIteraciones", entero(len(hist) - 1))
    macro("PcincoReduccion", cientifico(hist[0] / hist[-1], 2))
    macro("PcincoIterMenorUno", entero(next(
        i for i, v in enumerate(hist) if v < 1)))
    macro("PcincoIterMenorMilesima", entero(next(
        i for i, v in enumerate(hist) if v < 1e-3)))
    macro("PcincoAptitudMilesima", cientifico(hist[
        next(i for i, v in enumerate(hist) if v < 1e-3)], 2))
    macro("PcincoCuenta", entero(sum(
        1 for i in range(1, len(hist)) if hist[i] < hist[i - 1])))


def main():
    TABLAS.mkdir(parents=True, exist_ok=True)
    parte_a = cargar("parte_a")
    punto1(parte_a["punto1"], cargar("punto1"))
    punto2(parte_a["punto2"], cargar("punto2"))
    punto3(parte_a["punto3"], cargar("punto3"))
    punto4(parte_a["punto4"], cargar("punto4"))
    punto5(parte_a["punto5"], cargar("punto5"))
    (TABLAS / "valores.tex").write_text(
        "\n".join(MACROS) + "\n", encoding="utf-8")
    print("Tablas y valores generados en", TABLAS)


if __name__ == "__main__":
    main()
