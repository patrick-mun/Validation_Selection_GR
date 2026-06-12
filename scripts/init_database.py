#!/usr/bin/env python
"""Initialise la base SQL du scaffold.

Usage local :
    python scripts/init_database.py

Usage recommandé en production :
    alembic upgrade head
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from genorun_validation.database.init_db import init_database  # noqa: E402


if __name__ == "__main__":
    init_database()
    print("Base initialisée.")
