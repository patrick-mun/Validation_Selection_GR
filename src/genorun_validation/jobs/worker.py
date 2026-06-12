"""Worker local d'exécution du pipeline."""
from __future__ import annotations

import json
import time
from pathlib import Path

from .manager import JobManager
from .schemas import JobStatus, PipelineJob, utc_now_iso


class LocalPipelineWorker:
    """Worker local minimal.

    Le worker exécute pour l'instant un mode `dry_run` sécurisé afin de valider
    l'architecture : statuts, logs, manifest, sorties et reprise d'erreur.
    Les commandes PLINK/KING/ADMIXTURE doivent être ajoutées ensuite via les
    wrappers `external/` et non dans l'interface web (Flask + vanilla).
    """

    def __init__(self, manager: JobManager | None = None, delay_seconds: float = 0.2) -> None:
        self.manager = manager or JobManager()
        self.delay_seconds = delay_seconds

    def run(self, job_id: str) -> PipelineJob:
        """Exécute un job local à partir de son identifiant."""
        job = self.manager.get_job(job_id)
        try:
            self.manager.update_status(job, JobStatus.RUNNING, "Worker local démarré.")
            self._log(job, f"[START] Job {job.job_id}")
            self._log(job, f"[CONFIG] dataset={job.dataset} profile={job.profile} strategy={job.strategy}")

            for step in job.steps:
                step_name = step["name"]
                self.manager.update_step(job, step_name, "running", "Étape en cours.")
                self._log(job, f"[RUNNING] {step_name}")
                self._run_dry_step(job, step_name)
                self.manager.update_step(job, step_name, "completed", "Étape terminée.")
                self._log(job, f"[COMPLETED] {step_name}")

            self._write_demo_outputs(job)
            self.manager.update_status(job, JobStatus.COMPLETED, "Analyse terminée avec succès.")
            self._log(job, "[DONE] Analyse terminée avec succès.")
        except Exception as exc:  # pragma: no cover - sécurité d'exécution
            self.manager.update_status(job, JobStatus.FAILED, f"Erreur worker : {exc}")
            self._log(job, f"[FAILED] {exc}")
            raise
        return self.manager.get_job(job_id)

    def _run_dry_step(self, job: PipelineJob, step_name: str) -> None:
        """Simule une étape sans exécuter d'outil externe."""
        time.sleep(self.delay_seconds)
        if not job.outputs_dir:
            raise RuntimeError("outputs_dir absent du job")
        safe_name = step_name.lower().replace("/", "_").replace(" ", "_").replace("é", "e")
        marker = job.outputs_dir / f"{safe_name}.done"
        marker.write_text(f"{utc_now_iso()}\t{step_name}\tcompleted\n", encoding="utf-8")

    def _write_demo_outputs(self, job: PipelineJob) -> None:
        """Écrit des sorties synthétiques clairement marquées comme démo."""
        if not job.outputs_dir or not job.report_dir:
            raise RuntimeError("Dossiers de sortie absents du job")
        summary = {
            "job_id": job.job_id,
            "status": "completed",
            "mode": "dry_run",
            "warning": "Sortie de démonstration : aucune donnée génétique réelle analysée.",
            "metrics": {
                "selected_wgs": 350,
                "discovery_arm": 35,
                "s_div_mean": 0.152,
                "imputation_r2_placeholder": 0.924,
            },
        }
        (job.outputs_dir / "summary_metrics.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        (job.report_dir / "rapport_demo.md").write_text(
            "# Rapport démo\n\n"
            "Ce rapport est généré par le worker local en mode dry-run. "
            "Il valide le flux interface → job → worker → résultats, sans analyser de données réelles.\n",
            encoding="utf-8",
        )

    def _log(self, job: PipelineJob, message: str) -> None:
        """Ajoute une ligne horodatée au log du job."""
        if not job.log_path:
            raise RuntimeError("log_path absent du job")
        job.log_path.parent.mkdir(parents=True, exist_ok=True)
        with job.log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{utc_now_iso()} {message}\n")
