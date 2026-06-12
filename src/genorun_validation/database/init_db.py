"""Initialisation de la base de données."""
from __future__ import annotations

from . import models  # noqa: F401 - charge les modèles pour metadata
from .base import Base
from .session import engine


def init_database() -> None:
    """Crée les tables déclarées par SQLAlchemy.

    En production, préférer Alembic (`alembic upgrade head`). Cette fonction
    reste utile pour les tests rapides et le scaffold.
    """
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_database()
    print("Base de données initialisée.")
