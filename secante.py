"""Núcleo numérico: método de la secante, bisección y Newton-Raphson.

Módulo sin dependencias externas (solo la biblioteca estándar).
"""
import ast
import math

EPS_PENDIENTE = 1e-14  # salvaguarda contra división por cero
N_MAX_DEFECTO = 100


class ErrorNumerico(Exception):
    """Error controlado con mensaje entendible para el usuario."""


# ---------- Evaluador seguro de f(x) escrita por el usuario ----------
_FUNCIONES = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan, "exp": math.exp,
    "log": math.log, "ln": math.log, "log10": math.log10, "sqrt": math.sqrt,
    "abs": abs, "atan": math.atan, "sinh": math.sinh, "cosh": math.cosh,
    "tanh": math.tanh,
}
_CONSTANTES = {"pi": math.pi, "e": math.e}
_BINARIOS = {
    ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b,
}


def compilar(expresion, variable="x", parametros=None):
    """Convierte un texto como 'x**3 - 2*x - 5' en una función segura."""
    expresion = expresion.replace("^", "**")
    if len(expresion) > 200:
        raise ErrorNumerico("La expresión es demasiado larga (máx. 200 caracteres).")
    try:
        arbol = ast.parse(expresion, mode="eval")
    except SyntaxError:
        raise ErrorNumerico("No se pudo interpretar la expresión. Revisa paréntesis y operadores.")
    extras = parametros or {}

    def ev(n, v):
        if isinstance(n, ast.Expression):
            return ev(n.body, v)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Name):
            if n.id == variable:
                return v
            if n.id in extras:
                return extras[n.id]
            if n.id in _CONSTANTES:
                return _CONSTANTES[n.id]
            raise ErrorNumerico(f"Símbolo desconocido: '{n.id}'. Usa '{variable}'.")
        if isinstance(n, ast.BinOp) and type(n.op) in _BINARIOS:
            a, b = ev(n.left, v), ev(n.right, v)
            if isinstance(n.op, ast.Pow) and abs(b) > 100:
                raise ErrorNumerico("Exponente demasiado grande.")
            return _BINARIOS[type(n.op)](a, b)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            r = ev(n.operand, v)
            return -r if isinstance(n.op, ast.USub) else r
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id in _FUNCIONES and len(n.args) == 1 and not n.keywords):
            return _FUNCIONES[n.func.id](ev(n.args[0], v))
        raise ErrorNumerico("La expresión contiene elementos no permitidos.")

    def f(x):
        try:
            r = ev(arbol, x)
            if isinstance(r, complex):
                raise ValueError
            return float(r)
        except ErrorNumerico:
            raise
        except (ValueError, ZeroDivisionError, OverflowError):
            raise ErrorNumerico(f"f({x:g}) no está definida (fuera del dominio).")

    return f


def colebrook(re, rug_rel):
    """g(f) = 1/sqrt(f) + 2*log10( (e/D)/3.7 + 2.51/(Re*sqrt(f)) )  ->  g(f)=0."""
    if re <= 4000:
        raise ErrorNumerico("Colebrook-White aplica a flujo turbulento: Re > 4000.")
    if rug_rel < 0:
        raise ErrorNumerico("La rugosidad relativa debe ser ≥ 0.")

    def g(f):
        if f <= 0:
            raise ErrorNumerico("El factor de fricción f debe ser positivo.")
        s = math.sqrt(f)
        return 1 / s + 2 * math.log10(rug_rel / 3.7 + 2.51 / (re * s))
    return g


# ---------- Métodos ----------
def secante(f, x0, x1, es=1e-6, n_max=N_MAX_DEFECTO):
    """Devuelve (filas, raiz, motivo). Cada fila: k, x_{k-1}, x_k, x_{k+1}, g, error %."""
    if x0 == x1:
        raise ErrorNumerico("x0 y x1 deben ser distintos.")
    filas, a, b = [], x0, x1
    fa, fb = f(a), f(b)
    for k in range(1, n_max + 1):
        if abs(fb - fa) < EPS_PENDIENTE:
            return filas, b, "pendiente nula: f(x_k) ≈ f(x_{k-1}). Cambia los valores iniciales."
        c = b - fb * (b - a) / (fb - fa)
        fc = f(c)
        ea = abs((c - b) / c) * 100 if c != 0 else abs(c - b) * 100
        filas.append({"k": k, "x_prev": a, "x": b, "x_next": c, "g": fc, "ea": ea,
                      "fa": fa, "fb": fb})
        if ea < es or fc == 0:
            return filas, c, "convergió"
        a, b, fa, fb = b, c, fb, fc
    return filas, b, f"se alcanzó el máximo de {n_max} iteraciones sin cumplir la tolerancia."


def biseccion(f, a, b, es=1e-6, n_max=N_MAX_DEFECTO):
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        return None, None, "no hay cambio de signo en [a, b]"
    c_ant, n = a, 0
    for n in range(1, n_max + 1):
        c = (a + b) / 2
        fc = f(c)
        if c != 0 and abs((c - c_ant) / c) * 100 < es and n > 1:
            return n, c, "convergió"
        if fa * fc < 0:
            b = c
        else:
            a, fa = c, fc
        c_ant = c
    return n, c, "máximo de iteraciones"


def newton(f, x0, es=1e-6, n_max=N_MAX_DEFECTO):
    """Newton-Raphson con derivada numérica central (referencia de comparación)."""
    x = x0
    for n in range(1, n_max + 1):
        h = 1e-7 * max(1.0, abs(x))
        d = (f(x + h) - f(x - h)) / (2 * h)
        if abs(d) < EPS_PENDIENTE:
            return n, x, "derivada nula"
        xn = x - f(x) / d
        if xn != 0 and abs((xn - x) / xn) * 100 < es:
            return n, xn, "convergió"
        x = xn
    return n, x, "máximo de iteraciones"


def referencia(f, a, b):
    """Raíz de referencia de alta precisión: bisección hasta el límite de la máquina."""
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        return None
    for _ in range(200):
        c = (a + b) / 2
        fc = f(c)
        if fa * fc <= 0:
            b = c
        else:
            a, fa = c, fc
    return (a + b) / 2


def orden_convergencia(filas, raiz):
    """Estima p con e_{k+1} ≈ C·e_k^p usando el error real |x - r|."""
    e = [abs(r["x_next"] - raiz) for r in filas]
    ps = []
    for i in range(1, len(e) - 1):
        if e[i - 1] > 1e-13 and e[i] > 1e-13 and e[i + 1] > 1e-15 and e[i - 1] != e[i]:
            try:
                ps.append(math.log(e[i + 1] / e[i]) / math.log(e[i] / e[i - 1]))
            except (ValueError, ZeroDivisionError):
                pass
    return ps
