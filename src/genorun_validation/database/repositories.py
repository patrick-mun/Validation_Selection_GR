"""Repositories SQLAlchemy pour les jobs et l'audit.

Les repositories isolent l'accès SQL de l'interface et du worker. Ils évitent
que l'interface web manipule directement les modèles de base.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from genorun_validation.jobs.schemas import PipelineJob
from genorun_validation.settings import find_project_root

from .models import AnalysisJob, AnalysisStep, AuditEvent, JobLog


def _parse_iso_datetime(value: str | None) -> datetime | None:
    """Convertit une chaîne ISO en datetime naïf ou retourne None."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _relative_or_text(path: Path | None, project_root: Path) -> str | None:
    """Persiste les chemins relatifs quand ils sont dans le projet."""
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(project_root.resolve()))
    except ValueError:
        # SAFETY: on garde le texte sans planter, mais l'AGENTS.md interdit les
        # chemins absolus personnels pour les données réelles. Cette tolérance
        # évite de casser les tests temporaires hors projet.
        return str(path)


class JobRepository:
    """Persistance PostgreSQL/SQLAlchemy des jobs du pipeline."""

    def __init__(self, session: Session, project_root: Path | str | None = None) -> None:
        self.session = session
        self.project_root = Path(project_root or find_project_root()).resolve()

    def upsert_job(self, job: PipelineJob, parameters: dict[str, Any] | None = None) -> AnalysisJob:
        """Crée ou met à jour l'enregistrement SQL d'un job."""
        analysis_job = self.session.scalar(select(AnalysisJob).where(AnalysisJob.job_uid == job.job_id))
        if analysis_job is None:
            analysis_job = AnalysisJob(job_uid=job.job_id, dataset_name=job.dataset, run_dir=str(job.run_dir))
            self.session.add(analysis_job)

        analysis_job.dataset_name = job.dataset
        analysis_job.profile_name = job.profile
        analysis_job.strategy_name = job.strategy
        analysis_job.status = job.status.value
        analysis_job.message = job.message
        analysis_job.parameters_json = parameters or analysis_job.parameters_json
        analysis_job.run_dir = _relative_or_text(job.run_dir, self.project_root) or str(job.run_dir)
        analysis_job.config_path = _relative_or_text(job.config_path, self.project_root)
        analysis_job.manifest_path = _relative_or_text(job.manifest_path, self.project_root)
        analysis_job.log_path = _relative_or_text(job.log_path, self.project_root)
        analysis_job.started_at = _parse_iso_datetime(job.started_at)
        analysis_job.ended_at = _parse_iso_datetime(job.ended_at)
        self.session.flush()

        for step in job.steps:
            self.upsert_step(analysis_job.id, step.get("name", "unknown"), step.get("status", "pending"), step.get("message"))
        return analysis_job

    def update_job_status(self, job: PipelineJob) -> None:
        """Met à jour le statut principal d'un job déjà créé."""
        self.upsert_job(job)

    def upsert_step(self, analysis_job_id: int, step_name: str, status: str, message: str | None = None) -> AnalysisStep:
        """Crée ou met à jour une étape de job."""
        step = self.session.scalar(
            select(AnalysisStep).where(
                AnalysisStep.analysis_job_id == analysis_job_id,
                AnalysisStep.step_name == step_name,
            )
        )
        if step is None:
            step = AnalysisStep(analysis_job_id=analysis_job_id, step_name=step_name)
            self.session.add(step)
        step.status = status
        step.message = message
        self.session.flush()
        return step

    def list_job_uids_by_status(self, statuses: list[str], limit: int = 100) -> list[str]:
        """Retourne les identifiants de jobs selon leur statut.

        Utilisé par le worker en boucle : PostgreSQL devient la file officielle
        quand la base est activée, tandis que `work/runs/` reste le support
        reproductible des configurations, logs longs et sorties.
        """
        statement = (
            select(AnalysisJob.job_uid)
            .where(AnalysisJob.status.in_(statuses))
            .order_by(AnalysisJob.created_at.asc())
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())

    def add_log(self, job_uid: str, message: str, level: str = "INFO") -> None:
        """Ajoute une courte entrée de log indexable en base."""
        analysis_job = self.session.scalar(select(AnalysisJob).where(AnalysisJob.job_uid == job_uid))
        self.session.add(JobLog(analysis_job_id=analysis_job.id if analysis_job else None, job_uid=job_uid, level=level, message=message))

    def add_audit_event(self, event_type: str, message: str, job_uid: str | None = None, payload: dict[str, Any] | None = None) -> None:
        """Ajoute un événement d'audit."""
        self.session.add(AuditEvent(event_type=event_type, job_uid=job_uid, message=message, payload_json=payload, actor="system"))
