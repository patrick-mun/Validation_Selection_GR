"""Compatibilité historique : liste plate des étapes du pipeline.

# WHY: l'ordre canonique vit désormais dans `steps.py` (source unique de vérité).
# Ce module ne fait que dériver l'ancienne liste de libellés pour ne pas casser
# le code existant, tout en évitant deux définitions divergentes de l'ordre.
"""
from __future__ import annotations

from .steps import PIPELINE

# Libellés des étapes, dérivés de la définition canonique.
PIPELINE_STEPS: list[str] = [step.label for step in PIPELINE]
