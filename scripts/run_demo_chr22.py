"""Lance le pipeline de démonstration chr22 (mode dry-run sécurisé).

# SAFETY: aucune donnée génétique réelle n'est utilisée ici.
"""
from __future__ import annotations

from pathlib import Path

from genorun_validation.orchestration.run_context import RunContext
from genorun_validation.orchestration.runner import run_pipeline


def main() -> None:
    context = RunContext(run_id="demo_chr22", run_dir=Path("work/runs/demo_chr22"))
    run_pipeline(
        context,
        on_progress=lambda key, status, msg: print(f"[{status}] {key} — {msg}"),
        dry_run=True,
    )


if __name__ == "__main__":
    main()
