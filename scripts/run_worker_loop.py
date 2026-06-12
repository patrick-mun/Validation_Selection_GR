#!/usr/bin/env python
"""Worker local en boucle pour Docker ou serveur.

Il surveille les jobs `created` ou `queued` dans `work/runs/` et les exécute
séquentiellement. Ce mode reste simple pour le MVP ; il pourra être remplacé
plus tard par Celery/RQ/Nextflow selon l'infrastructure DSIO/HPC retenue.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from genorun_validation.jobs.manager import JobManager  # noqa: E402
from genorun_validation.jobs.worker import LocalPipelineWorker  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Worker loop Génome Réunion")
    parser.add_argument("--poll-seconds", type=float, default=2.0, help="Délai entre deux scans de jobs")
    parser.add_argument("--delay", type=float, default=0.2, help="Délai dry-run par étape")
    args = parser.parse_args()

    manager = JobManager(project_root=PROJECT_ROOT)
    worker = LocalPipelineWorker(manager=manager, delay_seconds=args.delay)

    while True:
        # PostgreSQL sert de file officielle quand la base est activée ; sinon
        # le worker retombe sur le scan filesystem des status.json.
        runnable_jobs = manager.list_runnable_jobs(limit=100)
        for job in runnable_jobs:
            try:
                worker.run(job.job_id)
            except Exception as exc:  # pragma: no cover - protection worker long-running
                print(f"[WORKER_LOOP_FAILED] {job.job_id}: {exc}", file=sys.stderr)
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
