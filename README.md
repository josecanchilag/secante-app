# Método de la secante — Colebrook-White

Aplicación web en Python (Flask) para resolver ecuaciones no lineales implícitas con el método de la secante.
Proyecto de Métodos Numéricos, Universidad de Santander (UDES).

## Estructura
- `secante.py`: núcleo numérico (secante, bisección, Newton, evaluador seguro de f(x)).
- `app.py`: servidor Flask y API `/api/resolver`.
- `templates/index.html`: interfaz (tabla de iteraciones, gráficas, comparación).
- `test_secante.py`: pruebas (reproducen la Tabla 1 del documento).

