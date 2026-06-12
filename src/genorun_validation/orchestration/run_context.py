"""Contexte d'exécution figé d'un run.

# WHY: regrouper les chemins canoniques d'un run dans un seul objet évite que
# chaque étape recalcule ses dossiers et garantit la reproductibilité
# (config.yaml + manifest.json figés par run, voir AGENTS.md §10).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class RunContext:
    """Chemins canoniques d'un run identifié par `run_id`."""

    run_id: str
    run_dir: Path

    @property
    def config_path(self) -> Path:
        return self.run_dir / "config.yaml"

    @property
    def manifest_path(self) -> Path:
        return self.run_dir / "manifest.json"

    @property
    def status_path(self) -> Path:
        return self.run_dir / "status.json"

    @property
    def logs_dir(self) -> Path:
        return self.run_dir / "logs"

    @property
    def outputs_dir(self) -> Path:
        return self.run_dir / "outputs"

    @property
    def report_dir(self) -> Path:
        return self.run_dir / "report"

    def work_dir_for(self, step_key: str) -> Path:
        """Dossier de travail isolé d'une étape."""
        return self.run_dir / "work" / step_key
