"""Lance le pipeline sur un run de démonstration (mode dry-run sécurisé).

# WHY: la vraie configuration sera chargée et validée en Phase 4 (docs/ROADMAP.md).
# Pour l'instant ce script valide l'enchaînement des étapes sans données réelles.
"""
from __future__ import annotations

from pathlib import Path

from genorun_validation.orchestration.run_context import RunContext
from genorun_validation.orchestration.runner import run_pipeline


def main() -> None:
    context = RunContext(run_id="cli_demo", run_dir=Path("work/runs/cli_demo"))
    results = run_pipeline(
        context,
        on_progress=lambda key, status, msg: print(f"[{status}] {key} — {msg}"),
        dry_run=True,
    )
    print("Résumé :", {k: str(v) for k, v in results.items()})


if __name__ == "__main__":
    main()
