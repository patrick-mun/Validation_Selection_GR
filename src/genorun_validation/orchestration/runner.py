"""Runner principal du pipeline.

# WHY: le runner orchestre l'ENCHAÎNEMENT des étapes (ordre, statut, arrêt sur
# échec bloquant). Il ne contient aucun algorithme scientifique ni aucune
# commande shell : il délègue à `core/` et aux wrappers `external/`.

État actuel : squelette d'architecture. L'exécution réelle de chaque étape est
branchée progressivement (voir docs/ROADMAP.md, Phase 4). Tant qu'une étape
`core/` n'est pas implémentée, le runner la marque `skipped` au lieu de planter.
"""
from __future__ import annotations

from collections.abc import Callable

from .exceptions import StepExecutionError, StepNotImplementedError
from .run_context import RunContext
from .status import StepStatus
from .steps import PIPELINE, StepDefinition

# Signature d'un callback de progression : (clé d'étape, statut, message).
ProgressCallback = Callable[[str, StepStatus, str], None]


def run_pipeline(
    context: RunContext,
    *,
    on_progress: ProgressCallback | None = None,
    dry_run: bool = True,
) -> dict[str, StepStatus]:
    """Exécute le pipeline pour un run donné et renvoie le statut de chaque étape.

    Parameters
    ----------
    context:
        Contexte figé du run (chemins canoniques).
    on_progress:
        Callback optionnel appelé à chaque changement de statut d'étape.
    dry_run:
        Si vrai, aucune étape n'exécute d'outil réel (mode de validation
        d'architecture). À retirer étape par étape en Phase 4.

    Notes
    -----
    Une étape bloquante en échec arrête le pipeline. Une étape non bloquante en
    échec est journalisée mais le pipeline continue.
    """
    results: dict[str, StepStatus] = {}
    for step in PIPELINE:
        results[step.key] = _run_single_step(step, context, on_progress=on_progress, dry_run=dry_run)
        if results[step.key] is StepStatus.FAILED and step.is_blocking:
            break
    return results


def _run_single_step(
    step: StepDefinition,
    context: RunContext,
    *,
    on_progress: ProgressCallback | None,
    dry_run: bool,
) -> StepStatus:
    """Exécute une étape unique en gérant statut et erreurs."""
    _notify(on_progress, step.key, StepStatus.RUNNING, f"Démarrage de l'étape {step.label}.")
    try:
        if dry_run:
            # SAFETY: en dry-run on ne touche à aucune donnée réelle (voir worker).
            _notify(on_progress, step.key, StepStatus.SKIPPED, "Dry-run : étape non exécutée.")
            return StepStatus.SKIPPED

        # TODO[DEV_TRACKING]: brancher l'exécution réelle via core/ + external/ (Phase 4).
        raise StepNotImplementedError(f"Étape non encore branchée : {step.key}")

    except StepNotImplementedError as exc:
        _notify(on_progress, step.key, StepStatus.SKIPPED, str(exc))
        return StepStatus.SKIPPED
    except Exception as exc:  # noqa: BLE001 - converti en erreur typée ci-dessous
        message = f"Échec de l'étape {step.key} : {exc}"
        _notify(on_progress, step.key, StepStatus.FAILED, message)
        if step.is_blocking:
            raise StepExecutionError(message) from exc
        return StepStatus.FAILED


def _notify(callback: ProgressCallback | None, key: str, status: StepStatus, message: str) -> None:
    if callback is not None:
        callback(key, status, message)
