"""Statuts d'étape de pipeline et transitions autorisées.

# WHY: centraliser ici l'état d'une étape évite que chaque module réinvente ses
# propres chaînes de statut, source classique d'incohérences entre worker, base
# et interface.
"""
from __future__ import annotations

from enum import StrEnum


class StepStatus(StrEnum):
    """Statut d'une étape individuelle du pipeline."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# Transitions autorisées. Toute transition hors de cette table est un bug.
ALLOWED_TRANSITIONS: dict[StepStatus, set[StepStatus]] = {
    StepStatus.PENDING: {StepStatus.RUNNING, StepStatus.SKIPPED},
    StepStatus.RUNNING: {StepStatus.COMPLETED, StepStatus.FAILED},
    StepStatus.COMPLETED: set(),
    StepStatus.FAILED: set(),
    StepStatus.SKIPPED: set(),
}


def can_transition(current: StepStatus, target: StepStatus) -> bool:
    """Indique si passer de `current` à `target` est autorisé."""
    return target in ALLOWED_TRANSITIONS[current]
