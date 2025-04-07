
"""CLI für das Projekt, damit das Modul als Python-Skript ausgeführt werden kann.

Der Aufruf `python -m inventory` ist dadurch möglich, falls folgende Voraussetzungen
erfüllt sind:
- Die virtuelle Umgebung für _venv_ ist aktiviert
- `sys.path` enthält das Verzeichnis `src` (ggf. die Umgebungsvariable `PYTHONPATH` auf
  `src` setzen)
Diese Möglichkeit sollte in einem Docker-Image genutzt werden, so dass der Package
Manager _uv_ zur Laufzeit nicht benötigt wird und deshalb das Image klein gehalten
werden kann.
"""

from inventory.asgi_server import run

__all__ = ["run"]

if __name__ == "__main__":
    run()
