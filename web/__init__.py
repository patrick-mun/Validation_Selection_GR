"""Factory de l'application web Flask.

# WHY: Flask sert ici de FINE couche de présentation au-dessus du backend
# pipeline existant (services/jobs/worker/SQLAlchemy). Aucune logique
# bioinformatique ni commande shell ne vit dans cette couche : les vues
# valident les entrées puis délèguent (voir AGENTS.md §2 et docs/ROADMAP.md
# Phase 7).

Le front est en HTML/CSS/JS vanilla (pas de framework d'interface).
"""
from __future__ import annotations

import os

from flask import Flask


def create_app() -> Flask:
    """Construit et configure l'application Flask."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # SAFETY: la clé de session est lue depuis l'environnement, jamais codée en dur.
    # En production, GENORUN_SECRET_KEY doit être défini.
    app.config["SECRET_KEY"] = os.environ.get("GENORUN_SECRET_KEY", "dev-insecure-change-me")
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # SAFETY: borne la taille des uploads

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)
    return app
