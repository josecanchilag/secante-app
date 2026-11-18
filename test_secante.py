import secante as s


def test_colebrook_tabla1():
    g = s.colebrook(1.5e5, 0.0004)
    filas, raiz, motivo = s.secante(g, 0.015, 0.030)
    assert motivo == "convergió" and len(filas) == 7
    assert abs(raiz - 0.018884) < 1e-6
    assert abs(filas[0]["ea"] - 45.979647) < 1e-5


def test_polinomio():
    f = s.compilar("x**3 - 2*x - 5")
    _, raiz, _ = s.secante(f, 1.5, 2.7)
    assert abs(raiz - 2.0945514815) < 1e-8


def test_pendiente_nula():
    f = s.compilar("5")
    _, _, motivo = s.secante(f, 1, 2)
    assert "pendiente nula" in motivo


def test_expresion_peligrosa():
    try:
        s.compilar("__import__('os').system('ls')")(1.0)
        assert False
    except s.ErrorNumerico:
        pass
