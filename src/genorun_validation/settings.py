"""Configuration centrale du logiciel Génome Réunion Validation.

La configuration est volontairement simple et lisible pour le scaffold.
Elle lit les variables d'environnement, puis fournit des valeurs par défaut
compatibles avec le déploiement Docker + PostgreSQL.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bool_from_env(value: str | None, default: bool = False) -> bool:
    """Convertit une variable d'environnement en booléen robuste."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def find_project_root(start: Path | str | None = None) -> Path:
    """Retourne la racine du projet à partir d'un chemin ou du cwd."""
    candidates: list[Path] = []
    if start is not None:
        candidates.append(Path(start).resolve())
    candidates.append(Path.cwd().resolve())
    candidates.append(Path(__file__).resolve())

    for candidate in candidates:
        for path in [candidate, *candidate.parents]:
            if (path / "pyproject.toml").exists() and (path / "src" / "genorun_validation").exists():
                return path
    return Path.cwd().resolve()


@dataclass(frozen=True, slots=True)
class Settings:
    """Paramètres applicatifs partagés par l'interface, le worker et les scripts."""

    project_root: Path
    database_url: str
    enable_database: bool
    runs_root: Path
    inputs_root: Path
    outputs_root: Path
    reports_root: Path
    logs_root: Path
    job_backend: str = "filesystem_plus_postgresql"

    @classmethod
    def from_env(cls, project_root: Path | str | None = None) -> "Settings":
        """Construit la configuration depuis l'environnement courant."""
        root = find_project_root(project_root)
        default_database_url = "postgresql+psycopg://genorun:genorun@localhost:5432/genorun_validation"
        database_url = os.getenv("GENORUN_DATABASE_URL") or os.getenv("DATABASE_URL") or default_database_url

        return cls(
            project_root=root,
            database_url=database_url,
            enable_database=_bool_from_env(os.getenv("GENORUN_ENABLE_DATABASE"), default=False),
            runs_root=Path(os.getenv("GENORUN_RUNS_ROOT", root / "work" / "runs")).resolve(),
            inputs_root=Path(os.getenv("GENORUN_INPUTS_ROOT", root / "data" / "inputs")).resolve(),
            outputs_root=Path(os.getenv("GENORUN_OUTPUTS_ROOT", root / "results")).resolve(),
            reports_root=Path(os.getenv("GENORUN_REPORTS_ROOT", root / "reports")).resolve(),
            logs_root=Path(os.getenv("GENORUN_LOGS_ROOT", root / "logs")).resolve(),
            job_backend=os.getenv("GENORUN_JOB_BACKEND", "filesystem_plus_postgresql"),
        )


def get_settings(project_root: Path | str | None = None) -> Settings:
    """Factory légère pour éviter une configuration globale difficile à tester."""
    return Settings.from_env(project_root=project_root)


def relative_to_project(path: Path, project_root: Path | None = None) -> str:
    """Retourne un chemin relatif à la racine du projet.

    Les chemins absolus personnels ne doivent pas être persistés en base.
    En cas de chemin hors projet, on refuse explicitement l'opération.
    """
    root = (project_root or find_project_root()).resolve()
    resolved_path = Path(path).resolve()
    try:
        return str(resolved_path.relative_to(root))
    except ValueError as exc:
        raise ValueError(f"Chemin hors projet interdit pour la base : {resolved_path}") from exc
