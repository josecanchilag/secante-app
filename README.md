# Método de la secante — Colebrook-White

Aplicación web en Python (Flask) para resolver ecuaciones no lineales implícitas con el método de la secante.
Proyecto de Métodos Numéricos, Universidad de Santander (UDES).

## Estructura
- `secante.py`: núcleo numérico (secante, bisección, Newton, evaluador seguro de f(x)).
- `app.py`: servidor Flask y API `/api/resolver`.
- `templates/index.html`: interfaz (tabla de iteraciones, gráficas, comparación).
- `test_secante.py`: pruebas (reproducen la Tabla 1 del documento).

## Ejecutar en local
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt pytest
pytest
python app.py                    # http://127.0.0.1:5000
```

## Subir a Git
```bash
git init
git add .
git commit -m "App del método de la secante"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/metodo-secante.git
git push -u origin main
```

## Desplegar en Vercel
1. En vercel.com: Add New → Project → importa el repositorio de GitHub.
2. Vercel detecta Flask (`app.py` con la variable `app`). Deja los ajustes por defecto y pulsa Deploy.
3. Cada `git push` a `main` redespliega automáticamente.
