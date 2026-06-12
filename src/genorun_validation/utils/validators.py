"""Validation stricte des entrées : chemins, identifiants et paramètres.

# SAFETY: ce module est la première ligne de défense avant qu'un paramètre
# n'atteigne le worker ou un wrapper d'outil externe. Aucun chemin non validé
# ne doit franchir cette frontière (voir docs/ROADMAP.md, Phase 0.6 et 4.3).
"""
from __future__ import annotations

import re
from pathlib import Path

# Identifiants sûrs : lettres, chiffres, tiret, underscore, point. Pas d'espace ni de séparateur.
_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9._-]+$")

# Extensions génétiques attendues en entrée (allowlist). Tout autre format est refusé.
ALLOWED_INPUT_EXTENSIONS: frozenset[str] = frozenset(
    {".vcf", ".gz", ".bcf", ".bed", ".bim", ".fam", ".pgen", ".pvar", ".psam", ".txt", ".tsv", ".csv"}
)


class ValidationError(ValueError):
    """Erreur de validation d'entrée, explicite et actionnable."""


def validate_identifier(value: str, *, field_name: str = "identifiant") -> str:
    """Valide un identifiant simple (dataset, profile, strategy, job_id).

    Refuse les chaînes vides, les espaces et les caractères pouvant servir à
    une injection de chemin ou de commande.
    """
    if not value or not _SAFE_IDENTIFIER.match(value):
        raise ValidationError(
            f"{field_name} invalide : {value!r}. Attendu : lettres, chiffres, '.', '-' ou '_'."
        )
    return value


def ensure_within_base(candidate: Path | str, base_dir: Path | str) -> Path:
    """Garantit qu'un chemin résolu reste à l'intérieur de `base_dir`.

    # SAFETY: bloque les remontées de répertoire (``../``), les liens symboliques
    # sortants et les chemins absolus pointant hors du périmètre autorisé.

    Returns
    -------
    Path
        Le chemin résolu et confirmé à l'intérieur de la base.

    Raises
    ------
    ValidationError
        Si le chemin sort de `base_dir`.
    """
    base_resolved = Path(base_dir).resolve()
    candidate_resolved = (base_resolved / Path(candidate)).resolve() if not Path(candidate).is_absolute() else Path(candidate).resolve()
    if base_resolved != candidate_resolved and base_resolved not in candidate_resolved.parents:
        raise ValidationError(
            f"Chemin hors périmètre autorisé : {candidate!r} sort de {base_resolved}."
        )
    return candidate_resolved


def validate_input_file(path: Path | str, *, base_dir: Path | str, must_exist: bool = True) -> Path:
    """Valide un fichier d'entrée : périmètre, extension autorisée, existence.

    Combine `ensure_within_base` et le contrôle d'extension (allowlist).
    """
    resolved = ensure_within_base(path, base_dir)
    suffix = resolved.suffix.lower()
    if suffix not in ALLOWED_INPUT_EXTENSIONS:
        raise ValidationError(
            f"Extension non autorisée : {suffix!r}. Autorisées : {sorted(ALLOWED_INPUT_EXTENSIONS)}."
        )
    if must_exist and not resolved.is_file():
        raise ValidationError(f"Fichier d'entrée introuvable : {resolved}.")
    return resolved


def validate_weights_sum(weights: dict[str, float], *, tolerance: float = 1e-6) -> dict[str, float]:
    """Valide qu'un jeu de poids (ex. S_div) somme bien à 1.0.

    # METHOD: les poids du score S_div doivent être normalisés (AGENTS.md §13.8).
    """
    total = sum(weights.values())
    if abs(total - 1.0) > tolerance:
        raise ValidationError(f"Poids non normalisés : somme={total}, attendu=1.0 (±{tolerance}).")
    return weights
