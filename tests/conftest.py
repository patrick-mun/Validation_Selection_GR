"""Configuration pytest locale pour le scaffold non installé."""
from __future__ import annotations

import os
from pathlib import Path
import sys

# Les tests unitaires ne doivent pas nécessiter un PostgreSQL lancé.
os.environ.setdefault("GENORUN_DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("GENORUN_ENABLE_DATABASE", "false")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
