# Parcial 2: Fundamentos de Inteligencia Artificial

Autores:

- Camilo Andrés Díaz García
- Juan David Andradé Gómez
- Mario Jiménez López

Universidad Sergio Arboleda.

Algoritmos genéticos, ascenso de colinas, temple simulado, ACO y PSO.
El enunciado está en `data/Parcial_2_IA.pdf`.

## Preparación

```
python -m venv venv
venv\Scripts\python -m pip install -r requirements.txt
```

## Ejecución (desde la carpeta `src`)

```
python verificar_parte_a.py
python punto1_genetico.py
python punto2_ascenso_colinas.py
python punto3_temple_simulado.py
python punto4_aco.py
python punto5_pso.py
python generar_figuras.py
python generar_tablas.py
```

Cada script de la parte B guarda `outputs/puntoN_resultados.json`.
`generar_figuras.py` escribe las figuras en `outputs/` y
`generar_tablas.py` escribe las tablas y los valores del informe en
`informe/tablas/`. Las semillas son fijas (42), así que las ejecuciones
repetidas producen resultados idénticos.

## Informe

```
cd informe
pdflatex parcial2.tex
pdflatex parcial2.tex
```

## Estilo de código

```
python -m pycodestyle --max-line-length=79 src
```
