"""Tests des validateurs de sécurité (chemins, identifiants, poids)."""
from __future__ import annotations

from pathlib import Path

import pytest

from genorun_validation.utils.validators import (
    ValidationError,
    ensure_within_base,
    validate_identifier,
    validate_input_file,
    validate_weights_sum,
)


def test_validate_identifier_accepte_valeur_propre() -> None:
    assert validate_identifier("demo_chr22-v5.1") == "demo_chr22-v5.1"


@pytest.mark.parametrize("bad", ["", "a/b", "../x", "nom avec espace", "x;rm -rf"])
def test_validate_identifier_refuse_valeurs_dangereuses(bad: str) -> None:
    with pytest.raises(ValidationError):
        validate_identifier(bad)


def test_ensure_within_base_accepte_chemin_interne(tmp_path: Path) -> None:
    cible = tmp_path / "inputs" / "data.vcf"
    cible.parent.mkdir(parents=True)
    cible.write_text("x", encoding="utf-8")
    resolved = ensure_within_base("inputs/data.vcf", tmp_path)
    assert resolved == cible.resolve()


def test_ensure_within_base_refuse_remontee(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        ensure_within_base("../../etc/passwd", tmp_path)


def test_validate_input_file_refuse_extension(tmp_path: Path) -> None:
    mauvais = tmp_path / "script.sh"
    mauvais.write_text("echo", encoding="utf-8")
    with pytest.raises(ValidationError):
        validate_input_file("script.sh", base_dir=tmp_path)


def test_validate_input_file_refuse_absent(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        validate_input_file("inputs/manquant.vcf", base_dir=tmp_path)


def test_validate_weights_sum_ok() -> None:
    assert validate_weights_sum({"a": 0.5, "b": 0.5})


def test_validate_weights_sum_refuse_non_normalise() -> None:
    with pytest.raises(ValidationError):
        validate_weights_sum({"a": 0.5, "b": 0.4})
