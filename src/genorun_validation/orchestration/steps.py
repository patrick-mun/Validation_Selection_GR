"""Définition ordonnée des étapes du pipeline.

# METHOD: l'ordre suit la méthodologie Génome Réunion (AGENTS.md §5).
# Ce module décrit QUOI exécuter et DANS QUEL ORDRE, pas COMMENT (l'algorithme
# vit dans `core/`, l'exécution d'outil dans `external/`).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class StepDefinition:
    """Description déclarative d'une étape du pipeline."""

    key: str
    label: str
    # Clé du module `core/` qui porte l'algorithme (référence, pas import direct).
    core_module: str
    # L'étape est-elle bloquante : son échec doit-il stopper le pipeline ?
    is_blocking: bool = True


# Ordre canonique du pipeline. Toute nouvelle étape s'insère ici avec son test.
PIPELINE: tuple[StepDefinition, ...] = (
    StepDefinition("qc", "QC SNP", "genorun_validation.core.qc"),
    StepDefinition("ld_pruning", "LD pruning", "genorun_validation.core.ld_pruning"),
    StepDefinition("pca", "PCA globale", "genorun_validation.core.pca"),
    StepDefinition("admixture", "ADMIXTURE global", "genorun_validation.core.admixture"),
    StepDefinition("kinship", "KING / IBD", "genorun_validation.core.kinship"),
    StepDefinition("roh", "ROH", "genorun_validation.core.roh"),
    StepDefinition("sdiv", "Calcul S_div", "genorun_validation.core.sdiv"),
    StepDefinition("selection", "Sélection WGS", "genorun_validation.core.selection"),
    StepDefinition("imputation", "Imputation / simulation", "genorun_validation.core.imputation"),
    StepDefinition("evaluation", "Évaluation des stratégies", "genorun_validation.core.evaluation"),
)


def step_keys() -> list[str]:
    """Liste ordonnée des clés d'étape."""
    return [step.key for step in PIPELINE]
