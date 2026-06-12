"""Création, persistance et suivi des jobs locaux."""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

import yaml
from genorun_validation.settings import get_settings

from .schemas import JobStatus, PipelineJob, utc_now_iso

DEFAULT_STEPS = [
    "QC",
    "LD pruning",
    "PCA",
    "ADMIXTURE",
    "KING/IBD",
    "ROH",
    "Sélection WGS",
    "Imputation",
    "Rapport",
]


class JobManager:
    """Gestionnaire de jobs : fichiers de run + persistance PostgreSQL optionnelle.

    Le dossier `work/runs/<job_id>/` reste la source reproductible des configs,
    manifests, logs longs et sorties. PostgreSQL indexe les métadonnées, statuts
    et événements d'audit lorsque `GENORUN_ENABLE_DATABASE=true`.
    """

    def __init__(
        self,
        project_root: Path | str | None = None,
        runs_root: Path | str | None = None,
        *,
        database_enabled: bool | None = None,
        session_factory: Any | None = None,
    ) -> None:
        settings = get_settings(project_root=project_root)
        self.project_root = Path(project_root or settings.project_root).resolve()
        self.runs_root = Path(runs_root or settings.runs_root).resolve()
        self.runs_root.mkdir(parents=True, exist_ok=True)
        self.database_enabled = settings.enable_database if database_enabled is None else database_enabled
        self.session_factory = session_factory
        self._job_parameters: dict[str, dict[str, Any]] = {}

    def create_job(self, dataset: str, profile: str, strategy: str, parameters: dict[str, Any] | None = None) -> PipelineJob:
        """Crée un job, son dossier de run, sa config figée et son manifest."""
        job_id = self._new_job_id()
        run_dir = self.runs_root / job_id
        logs_dir = run_dir / "logs"
        outputs_dir = run_dir / "outputs"
        report_dir = run_dir / "report"
        for directory in (logs_dir, outputs_dir, report_dir):
            directory.mkdir(parents=True, exist_ok=True)

        job = PipelineJob(
            job_id=job_id,
            dataset=dataset,
            profile=profile,
            strategy=strategy,
            run_dir=run_dir,
            status=JobStatus.CREATED,
            config_path=run_dir / "config.yaml",
            manifest_path=run_dir / "manifest.json",
            status_path=run_dir / "status.json",
            log_path=logs_dir / "pipeline.log",
            outputs_dir=outputs_dir,
            report_dir=report_dir,
            steps=[{"name": step, "status": "pending"} for step in DEFAULT_STEPS],
            message="Job créé. En attente de lancement du worker.",
        )

        config = {
            "job_id": job.job_id,
            "dataset": dataset,
            "profile": profile,
            "strategy": strategy,
            "execution": {
                "mode": "dry_run",
                "shell_allowed": False,
                "worker": "local",
            },
            "parameters": parameters or {},
            "steps": DEFAULT_STEPS,
        }
        self._write_yaml(job.config_path, config)

        manifest = {
            "job_id": job.job_id,
            "created_at": job.created_at,
            "project": "Génome Réunion — Validation Pipeline",
            "dataset": dataset,
            "profile": profile,
            "strategy": strategy,
            "run_dir": str(run_dir),
            "config_path": str(job.config_path),
            "rules": {
                "no_real_genetic_data_in_git": True,
                "web_executes_no_raw_shell": True,
                "commands_must_use_shell_false": True,
            },
        }
        self._write_json(job.manifest_path, manifest)
        self._job_parameters[job.job_id] = parameters or {}
        self.save_job(job)
        self._persist_job_to_database(job, event_type="job_created", parameters=parameters or {})
        return job

    def get_job(self, job_id: str) -> PipelineJob:
        """Charge un job existant depuis `status.json`."""
        status_path = self.runs_root / job_id / "status.json"
        if not status_path.exists():
            raise FileNotFoundError(f"Job introuvable : {job_id}")
        return PipelineJob.from_dict(json.loads(status_path.read_text(encoding="utf-8")))

    def save_job(self, job: PipelineJob) -> None:
        """Persiste l'état du job de manière atomique."""
        job.updated_at = utc_now_iso()
        if not job.status_path:
            job.status_path = job.run_dir / "status.json"
        self._write_json(job.status_path, job.to_dict())

    def update_status(self, job: PipelineJob, status: JobStatus, message: str | None = None) -> PipelineJob:
        """Met à jour le statut principal d'un job."""
        job.status = status
        job.message = message
        if status == JobStatus.RUNNING and not job.started_at:
            job.started_at = utc_now_iso()
        if status in {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}:
            job.ended_at = utc_now_iso()
        self.save_job(job)
        self._persist_job_to_database(job, event_type=f"job_status_{status.value}")
        return job

    def update_step(self, job: PipelineJob, step_name: str, status: str, message: str | None = None) -> PipelineJob:
        """Met à jour le statut d'une étape."""
        found = False
        for step in job.steps:
            if step["name"] == step_name:
                step["status"] = status
                step["updated_at"] = utc_now_iso()
                if message:
                    step["message"] = message
                found = True
                break
        if not found:
            job.steps.append({"name": step_name, "status": status, "message": message, "updated_at": utc_now_iso()})
        self.save_job(job)
        self._persist_job_to_database(job, event_type=f"step_{status}")
        return job

    def list_runnable_jobs(self, limit: int = 100) -> list[PipelineJob]:
        """Liste les jobs prêts à être exécutés par le worker.

        Lorsque PostgreSQL est activé, la base sert de file de jobs officielle.
        Le dossier `work/runs/` reste nécessaire : il contient le `status.json`,
        le manifest, la configuration figée et les sorties reproductibles.
        """
        statuses = [JobStatus.CREATED.value, JobStatus.QUEUED.value]
        if self.database_enabled:
            from genorun_validation.database.repositories import JobRepository
            from genorun_validation.database.session import SessionLocal

            session_factory = self.session_factory or SessionLocal
            with session_factory() as session:
                repository = JobRepository(session=session, project_root=self.project_root)
                job_ids = repository.list_job_uids_by_status(statuses=statuses, limit=limit)
            runnable_jobs: list[PipelineJob] = []
            for job_id in job_ids:
                try:
                    runnable_jobs.append(self.get_job(job_id))
                except FileNotFoundError:
                    # SAFETY: la base référence un job dont le run_dir n'est plus
                    # disponible. Le worker ignore le job ; l'audit manuel doit
                    # ensuite corriger ou archiver l'enregistrement SQL.
                    continue
            return runnable_jobs

        return [
            job for job in self.list_jobs(limit=limit)
            if job.status in {JobStatus.CREATED, JobStatus.QUEUED}
        ]

    def list_jobs(self, limit: int = 20) -> list[PipelineJob]:
        """Liste les jobs les plus récents."""
        jobs: list[PipelineJob] = []
        for status_path in self.runs_root.glob("*/status.json"):
            try:
                jobs.append(PipelineJob.from_dict(json.loads(status_path.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
        jobs.sort(key=lambda item: item.created_at, reverse=True)
        return jobs[:limit]

    def tail_log(self, job: PipelineJob, max_lines: int = 80) -> str:
        """Retourne les dernières lignes du log pipeline."""
        if not job.log_path or not job.log_path.exists():
            return ""
        lines = job.log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-max_lines:])

    def _persist_job_to_database(self, job: PipelineJob, event_type: str, parameters: dict[str, Any] | None = None) -> None:
        """Indexe le job en base quand PostgreSQL est activé.

        Les fichiers de run restent écrits avant la base afin que le job demeure
        traçable même si l'index SQL est temporairement indisponible.
        """
        if not self.database_enabled:
            return
        try:
            # Import tardif : le mode filesystem reste testable même si SQLAlchemy
            # n'est pas installé dans l'environnement courant.
            from genorun_validation.database.repositories import JobRepository
            from genorun_validation.database.session import SessionLocal

            session_factory = self.session_factory or SessionLocal
            with session_factory() as session:
                repository = JobRepository(session=session, project_root=self.project_root)
                repository.upsert_job(job, parameters=parameters or self._job_parameters.get(job.job_id))
                repository.add_audit_event(
                    event_type=event_type,
                    job_uid=job.job_id,
                    message=job.message or f"Événement {event_type}",
                    payload={"status": job.status.value, "dataset": job.dataset, "strategy": job.strategy},
                )
                session.commit()
        except Exception as exc:
            # SAFETY: si la base est activée, l'erreur est importante et doit
            # être visible. On l'écrit dans le log du run avant de la remonter.
            if job.log_path:
                job.log_path.parent.mkdir(parents=True, exist_ok=True)
                with job.log_path.open("a", encoding="utf-8") as handle:
                    handle.write(f"{utc_now_iso()} [DATABASE_FAILED] {exc}\n")
            raise

    def _new_job_id(self) -> str:
        return f"run_{utc_now_iso().replace(':', '').replace('+', 'Z')}_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)

    @staticmethod
    def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
        os.replace(tmp, path)


def find_project_root(start: Path | str | None = None) -> Path:
    """Trouve la racine du projet à partir du fichier courant ou du cwd."""
    candidates: list[Path] = []
    if start:
        candidates.append(Path(start).resolve())
    candidates.append(Path.cwd().resolve())
    candidates.append(Path(__file__).resolve())

    for candidate in candidates:
        for path in [candidate, *candidate.parents]:
            if (path / "pyproject.toml").exists() and (path / "src" / "genorun_validation").exists():
                return path
    return Path.cwd().resolve()


def get_default_job_manager() -> JobManager:
    """Factory utilisée par l'interface et les scripts."""
    return JobManager()
