
r"""Modul-Deklaration für das Projekt als oberster Namensraum bei Imports.

Das Basis-Verzeichnis `inventory` (direkt unter `src`) wird durch `__init__.py` als Modul
für das Projekt deklariert, damit `inventory` als oberster Namensraum bei den Imports
verwendet werden kann.

Außerdem kann mit dem Package Manager _uv_ das Modul als Skript aufgerufen werden:
`uv run inventory`. Siehe `project.scripts` in `pyproject.toml`.

Desweiteren wird für _uvicorn_ die 'Package-Level' Variable `app` initialisiert.
Dann lautet der Aufruf:

```powershell
uv run uvicorn src.inventory:app --ssl-certfile=src\inventory\config\resources\tls\certificate.crt --ssl-keyfile=src\inventory\config\resources\tls\key.pem
```

Alternativ kann auch die virtuelle Umgebung für _venv_ aktiviert werden und uvicorn
direkt aufgerufen werden:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn src.inventory:app --ssl-certfile=src\inventory\config\resources\tls\certificate.crt --ssl-keyfile=src\inventory\config\resources\tls\key.pem
```

Eine weitere Alternative ist das CLI von FastAPI, das intern _uvicorn_ mit Port _8000_
aufruft - aber _ohne TLS_. Mit dem CLI von FastAPI hat man beim Entwickeln u.a. den
Vorteil, dass ein _Watch-Modus_ im Hinblick auf Dateiänderungen untersützt wird:

```powershell
uv run fastapi dev src\inventory
```
"""  # noqa: E501

from inventory.asgi_server import run
from inventory.fastapi_app import app

__all__ = ["app", "main"]


def main():
    """main-Funktion, damit das Modul als Skript aufgerufen werden kann."""
    run()
