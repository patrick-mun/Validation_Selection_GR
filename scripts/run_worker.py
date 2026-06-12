#!/usr/bin/env python
"""Lance le worker local pour un job existant.

Exemple :
    python scripts/run_worker.py --job-id run_2026...
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Permet l'exécution depuis le scaffold sans installation editable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from genorun_validation.jobs.manager import JobManager  # noqa: E402
from genorun_validation.jobs.worker import LocalPipelineWorker  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Worker local Génome Réunion")
    parser.add_argument("--job-id", required=True, help="Identifiant du job à exécuter")
    parser.add_argument("--delay", type=float, default=0.2, help="Délai dry-run par étape, en secondes")
    args = parser.parse_args()

    manager = JobManager(project_root=PROJECT_ROOT)
    worker = LocalPipelineWorker(manager=manager, delay_seconds=args.delay)
    worker.run(args.job_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
