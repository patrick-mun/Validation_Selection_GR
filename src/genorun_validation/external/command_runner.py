"""Exécution sécurisée des outils externes.

Règle de sécurité : aucune commande shell libre. Les commandes sont des listes
argumentées et sont exécutées avec `shell=False`.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

ALLOWED_EXECUTABLES = {
    "plink",
    "plink2",
    "king",
    "admixture",
    "bcftools",
    "tabix",
    "beagle",
    "shapeit4",
}


@dataclass(slots=True)
class CommandResult:
    """Résultat normalisé d'une commande externe."""

    args: list[str]
    returncode: int
    stdout_path: Path
    stderr_path: Path


def run_command(args: Sequence[str], cwd: Path | str, stdout_path: Path | str, stderr_path: Path | str) -> CommandResult:
    """Exécute une commande autorisée avec logs stdout/stderr.

    Parameters
    ----------
    args:
        Liste d'arguments. Le premier élément doit être l'exécutable.
    cwd:
        Dossier de travail isolé du run.
    stdout_path, stderr_path:
        Fichiers de logs.
    """
    if not args:
        raise ValueError("Commande vide")
    executable = Path(args[0]).name
    if executable not in ALLOWED_EXECUTABLES:
        raise ValueError(f"Exécutable non autorisé : {executable}")

    cwd_path = Path(cwd).resolve()
    if not cwd_path.exists():
        raise FileNotFoundError(f"Dossier de travail introuvable : {cwd_path}")

    stdout = Path(stdout_path)
    stderr = Path(stderr_path)
    stdout.parent.mkdir(parents=True, exist_ok=True)
    stderr.parent.mkdir(parents=True, exist_ok=True)

    with stdout.open("w", encoding="utf-8") as out_handle, stderr.open("w", encoding="utf-8") as err_handle:
        completed = subprocess.run(
            list(args),
            cwd=str(cwd_path),
            stdout=out_handle,
            stderr=err_handle,
            text=True,
            shell=False,
            check=False,
        )

    return CommandResult(args=list(args), returncode=completed.returncode, stdout_path=stdout, stderr_path=stderr)
