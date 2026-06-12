"""Point d'entrée WSGI pour gunicorn : `gunicorn web.wsgi:app`."""
from __future__ import annotations

from . import create_app

app = create_app()
