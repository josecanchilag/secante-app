"""Aplicación web (Flask) del método de la secante — Métodos Numéricos, UDES."""
import math
from flask import Flask, jsonify, render_template, request

import secante as sec

app = Flask(__name__)


def _num(datos, clave, defecto=None, positivo=False):
    try:
        v = float(datos.get(clave, defecto))
    except (TypeError, ValueError):
        raise sec.ErrorNumerico(f"'{clave}' debe ser un número.")
    if not math.isfinite(v):
        raise sec.ErrorNumerico(f"'{clave}' debe ser un número finito.")
    if positivo and v <= 0:
        raise sec.ErrorNumerico(f"'{clave}' debe ser mayor que 0.")
    return v


def _muestras(f, a, b, n=120):
    pts = []
    for i in range(n + 1):
        x = a + (b - a) * i / n
        try:
            pts.append({"x": x, "y": f(x)})
        except sec.ErrorNumerico:
            pass
    return pts


@app.get("/")
def inicio():
    return render_template("index.html")


@app.post("/api/resolver")
def resolver():
    d = request.get_json(silent=True) or {}
    try:
        x0, x1 = _num(d, "x0"), _num(d, "x1")
        es = _num(d, "es", 1e-6, positivo=True)
        n_max = int(_num(d, "nmax", 100, positivo=True))
        if n_max > 500:
            raise sec.ErrorNumerico("El máximo de iteraciones permitido es 500.")

        if d.get("modo") == "colebrook":
            f = sec.colebrook(_num(d, "re", 1.5e5), _num(d, "rug", 0.0004))
            titulo = "g(f) = 1/√f + 2·log₁₀( (ε/D)/3.7 + 2.51/(Re·√f) ) = 0"
        else:
            expr = str(d.get("expr", "")).strip()
            if not expr:
                raise sec.ErrorNumerico("Escribe la función f(x).")
            f = sec.compilar(expr)
            f(x0), f(x1)  # valida dominio en los puntos iniciales
            titulo = f"f(x) = {expr}"

        filas, raiz, motivo = sec.secante(f, x0, x1, es, n_max)
        ok = motivo == "convergió"
        lo, hi = min(x0, x1, raiz), max(x0, x1, raiz)
        pad = (hi - lo) * 0.15 or 0.5

        comparacion = None
        if ok:
            n_b, r_b, m_b = sec.biseccion(f, min(x0, x1), max(x0, x1), es, n_max)
            n_n, r_n, m_n = sec.newton(f, x1, es, n_max)
            comparacion = {
                "secante": {"iter": len(filas), "evals": len(filas) + 2},
                "biseccion": {"iter": n_b, "nota": m_b},
                "newton": {"iter": n_n, "evals": n_n * 3, "nota": m_n},
            }

        return jsonify(
            ok=ok, motivo=motivo, titulo=titulo, raiz=raiz,
            residuo=abs(f(raiz)), filas=filas, comparacion=comparacion,
            orden=sec.orden_convergencia(filas, raiz) if ok else [],
            curva=_muestras(f, lo - pad, hi + pad),
            x0=x0, x1=x1,
        )
    except sec.ErrorNumerico as e:
        return jsonify(ok=False, error=str(e)), 400


if __name__ == "__main__":
    app.run(debug=True)
