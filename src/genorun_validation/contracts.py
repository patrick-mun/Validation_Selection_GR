"""Contrats d'interface du pipeline.

# WHY: figer ici les frontières (seams) entre `core/`, `external/` et `parsers/`
# AVANT d'implémenter les algorithmes permet de développer chaque couche
# indépendamment, de mocker proprement les voisines dans les tests, et d'éviter
# les réécritures en cascade quand une signature change (voir docs/ROADMAP.md, Phase 0.4).

Ce module ne contient AUCUN algorithme scientifique : uniquement des protocoles
(interfaces structurelles) et des dataclasses d'entrée/sortie typées.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    # WHY: imports lourds réservés au typage statique pour garder l'import runtime léger.
    import pandas as pd


# ---------------------------------------------------------------------------
# Schémas d'entrée/sortie partagés
# ---------------------------------------------------------------------------


@dataclass(slots=True, frozen=True)
class StepInput:
    """Entrée standard d'une étape de pipeline.

    `work_dir` est le dossier de travail isolé de l'étape. `params` contient les
    paramètres déjà validés (jamais de valeur non validée ne doit arriver ici).
    """

    work_dir: Path
    params: dict[str, Any] = field(default_factory=dict)
    inputs: dict[str, Path] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class StepOutput:
    """Sortie standard d'une étape de pipeline.

    `metrics` ne contient que des scalaires synthétiques destinés à la base SQL.
    `artifacts` pointe vers les fichiers produits (jamais stockés en base).
    """

    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: dict[str, Path] = field(default_factory=dict)
    tables: dict[str, "pd.DataFrame"] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ToolInvocation:
    """Commande externe prête à exécuter (jamais une chaîne shell libre)."""

    args: list[str]
    stdout_path: Path
    stderr_path: Path
    cwd: Path


# ---------------------------------------------------------------------------
# Protocoles (interfaces structurelles)
# ---------------------------------------------------------------------------


@runtime_checkable
class CoreStep(Protocol):
    """Étape scientifique pure : transforme des données en données.

    Une implémentation de `core/` NE DOIT PAS exécuter d'outil externe ni toucher
    à la base SQL ni importer la couche web. Elle doit être testable en isolation.
    """

    name: str

    def run(self, step_input: StepInput) -> StepOutput:  # pragma: no cover - protocole
        ...


@runtime_checkable
class ExternalToolWrapper(Protocol):
    """Wrapper d'outil bioinformatique externe.

    Construit une `ToolInvocation` validée (exécutable autorisé, chemins contrôlés)
    puis délègue l'exécution à `external/command_runner.py`. Jamais de `shell=True`.
    """

    executable: str

    def build_invocation(self, step_input: StepInput) -> ToolInvocation:  # pragma: no cover
        ...


@runtime_checkable
class OutputParser(Protocol):
    """Parseur de sortie d'outil : fichier brut -> structure Python typée."""

    def parse(self, path: Path) -> StepOutput:  # pragma: no cover - protocole
        ...
