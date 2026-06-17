"""Configuration pytest locale pour le scaffold non installé."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

# WHY: même dans le conteneur Docker, pytest ne doit pas écrire dans la file
# PostgreSQL de développement ni dans `work/runs/` partagé.
os.environ["GENORUN_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["GENORUN_ENABLE_DATABASE"] = "false"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def pytest_configure(config: pytest.Config) -> None:
    """Ajoute les marqueurs de tests documentés pour éviter les avertissements."""
    config.addinivalue_line(
        "markers",
        "uses_dev_database: test autorisé à utiliser explicitement une base externe.",
    )


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Refuse l'usage implicite de la base PostgreSQL partagée en test."""
    if item.get_closest_marker("uses_dev_database"):
        return
    os.environ["GENORUN_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
    os.environ["GENORUN_ENABLE_DATABASE"] = "false"
    os.environ["GENORUN_RUNS_ROOT"] = str(Path(tempfile.mkdtemp(prefix="genorun_pytest_")) / "runs")
