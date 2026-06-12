#!/usr/bin/env python
"""Crée un job démo sans lancer le worker."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from genorun_validation.jobs.manager import JobManager  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Création d'un job local de démonstration")
    parser.add_argument("--dataset", default="1000G chr22")
    parser.add_argument("--profile", default="Profil C")
    parser.add_argument("--strategy", default="Géo-ancestrale + découverte")
    args = parser.parse_args()

    job = JobManager(project_root=PROJECT_ROOT).create_job(
        dataset=args.dataset,
        profile=args.profile,
        strategy=args.strategy,
        parameters={"created_from": "scripts/create_demo_job.py"},
    )
    print(job.job_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
