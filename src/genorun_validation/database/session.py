"""Session SQLAlchemy et configuration PostgreSQL.

PostgreSQL est la base cible du projet. Pour les tests unitaires, le code peut
recevoir explicitement une URL SQLite en mémoire, sans changer l'architecture de
production.
"""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from genorun_validation.settings import get_settings


def build_engine(database_url: str | None = None, echo: bool = False) -> Engine:
    """Construit un moteur SQLAlchemy.

    `database_url` est injectable pour les tests. L'URL par défaut est lue dans
    l'environnement via `GENORUN_DATABASE_URL` ou `DATABASE_URL`.
    """
    url = database_url or get_settings().database_url
    connect_args: dict[str, Any] = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, echo=echo, future=True, pool_pre_ping=not url.startswith("sqlite"), connect_args=connect_args)


engine = build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


@contextmanager
def session_scope(session_factory: sessionmaker[Session] = SessionLocal) -> Iterator[Session]:
    """Ouvre une session transactionnelle puis commit/rollback automatiquement."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
