"""Hiérarchie d'exceptions de l'orchestration.

# WHY: des exceptions typées permettent au worker de réagir précisément
# (passer un job en `failed`, distinguer une erreur de validation d'une erreur
# d'outil externe) plutôt que d'attraper un `Exception` générique.
"""
from __future__ import annotations


class PipelineError(Exception):
    """Erreur de base du pipeline."""


class StepValidationError(PipelineError):
    """Paramètres ou entrées d'étape invalides (échec avant exécution)."""


class StepExecutionError(PipelineError):
    """Échec pendant l'exécution d'une étape (outil externe, calcul)."""


class StepNotImplementedError(PipelineError):
    """Étape déclarée dans le pipeline mais pas encore implémentée.

    # WHY: distinct de `NotImplementedError` standard pour que le worker puisse
    # marquer l'étape `skipped` proprement pendant la montée en charge du scaffold.
    """
