"""Paramètres autorisés pour lancer un job phase 0."""
from __future__ import annotations

from dataclasses import dataclass

from genorun_validation.utils.validators import ValidationError, validate_identifier


@dataclass(frozen=True, slots=True)
class LaunchChoice:
    """Décrit une option affichable et son identifiant technique sûr."""

    value: str
    label: str


@dataclass(frozen=True, slots=True)
class LaunchParameters:
    """Paramètres validés pour créer un job depuis le web ou le CLI."""

    dataset: str
    profile: str
    strategy: str


DATASET_CHOICES: tuple[LaunchChoice, ...] = (
    LaunchChoice(value="1000G_chr22", label="1000G chr22"),
)
PROFILE_CHOICES: tuple[LaunchChoice, ...] = (
    LaunchChoice(value="profil_C", label="Profil C"),
)
STRATEGY_CHOICES: tuple[LaunchChoice, ...] = (
    LaunchChoice(value="geo_ancestrale_decouverte", label="Géo-ancestrale + découverte"),
    LaunchChoice(value="geo_ancestrale", label="Géo-ancestrale"),
)

DEFAULT_DATASET = DATASET_CHOICES[0].value
DEFAULT_PROFILE = PROFILE_CHOICES[0].value
DEFAULT_STRATEGY = STRATEGY_CHOICES[0].value


def validate_launch_parameters(dataset: str, profile: str, strategy: str) -> LaunchParameters:
    """Valide les paramètres métier phase 0 avant création d'un job."""
    dataset = _validate_choice(dataset, DATASET_CHOICES, field_name="dataset")
    profile = _validate_choice(profile, PROFILE_CHOICES, field_name="profile")
    strategy = _validate_choice(strategy, STRATEGY_CHOICES, field_name="strategy")
    return LaunchParameters(dataset=dataset, profile=profile, strategy=strategy)


def _validate_choice(value: str, choices: tuple[LaunchChoice, ...], *, field_name: str) -> str:
    """Valide un identifiant sûr et présent dans l'allowlist phase 0."""
    safe_value = validate_identifier(value, field_name=field_name)
    allowed_values = {choice.value for choice in choices}
    if safe_value not in allowed_values:
        raise ValidationError(
            f"{field_name} inconnu : {safe_value!r}. Valeurs autorisées : {', '.join(sorted(allowed_values))}."
        )
    return safe_value
