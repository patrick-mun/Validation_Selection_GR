"""Modèles SQLAlchemy principaux du pipeline.

La base stocke les métadonnées, statuts, scores, chemins relatifs et audits.
Elle ne stocke jamais les gros fichiers génétiques bruts.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def utc_now() -> datetime:
    """Horodatage UTC naïf compatible PostgreSQL/SQLite pour le scaffold."""
    return datetime.utcnow()


class Project(Base):
    """Projet scientifique ou instance de validation."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class Cohort(Base):
    """Cohorte ou panel de référence utilisé par une analyse."""

    __tablename__ = "cohorts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cohort_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    genome_build: Mapped[str | None] = mapped_column(String(50), nullable=True)
    n_samples_expected: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="registered", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class Sample(Base):
    """Échantillon anonymisé ou pseudonymisé rattaché à une cohorte."""

    __tablename__ = "samples"
    __table_args__ = (UniqueConstraint("cohort_id", "sample_code", name="uq_samples_cohort_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cohort_id: Mapped[int] = mapped_column(ForeignKey("cohorts.id"), nullable=False)
    sample_code: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sex: Mapped[str | None] = mapped_column(String(30), nullable=True)
    inclusion_status: Mapped[str] = mapped_column(String(50), default="eligible", nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class InputFile(Base):
    """Fichier d'entrée ou de sortie enregistré par le pipeline.

    `relative_path` doit rester relatif à la racine projet ou au stockage déclaré.
    """

    __tablename__ = "input_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    cohort_id: Mapped[int | None] = mapped_column(ForeignKey("cohorts.id"), nullable=True)
    job_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    file_role: Mapped[str] = mapped_column(String(100), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    relative_path: Mapped[str] = mapped_column(Text, nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validation_status: Mapped[str] = mapped_column(String(50), default="registered", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class AnalysisJob(Base):
    """Job d'analyse créé par l'interface ou la CLI."""

    __tablename__ = "analysis_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_uid: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    cohort_id: Mapped[int | None] = mapped_column(ForeignKey("cohorts.id"), nullable=True)
    dataset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    strategy_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="created", nullable=False, index=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameters_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    run_dir: Mapped[str] = mapped_column(Text, nullable=False)
    config_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    manifest_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    log_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AnalysisStep(Base):
    """Étape d'un job d'analyse."""

    __tablename__ = "analysis_steps"
    __table_args__ = (UniqueConstraint("analysis_job_id", "step_name", name="uq_analysis_step_job_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_job_id: Mapped[int] = mapped_column(ForeignKey("analysis_jobs.id"), nullable=False)
    step_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    log_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class JobLog(Base):
    """Entrée courte de log. Les logs longs restent en fichiers."""

    __tablename__ = "job_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_job_id: Mapped[int | None] = mapped_column(ForeignKey("analysis_jobs.id"), nullable=True)
    job_uid: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(30), default="INFO", nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class SoftwareVersion(Base):
    """Version d'un outil ou paquet utilisé dans un run."""

    __tablename__ = "software_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_job_id: Mapped[int | None] = mapped_column(ForeignKey("analysis_jobs.id"), nullable=True)
    tool_name: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    command: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class AuditEvent(Base):
    """Événement d'audit reproductible."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    job_uid: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    actor: Mapped[str] = mapped_column(String(120), default="system", nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class QCMetric(Base):
    """Métriques synthétiques de contrôle qualité."""

    __tablename__ = "qc_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_uid: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    n_samples_before: Mapped[int | None] = mapped_column(Integer, nullable=True)
    n_samples_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    n_variants_before: Mapped[int | None] = mapped_column(Integer, nullable=True)
    n_variants_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    call_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class PCAResult(Base):
    """Coordonnées PCA ou résumé PCA."""

    __tablename__ = "pca_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_uid: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    sample_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pc_values_json: Mapped[dict[str, float] | None] = mapped_column(JSON, nullable=True)


class AdmixtureResult(Base):
    """Résultat ADMIXTURE par échantillon ou résumé de modèle K."""

    __tablename__ = "admixture_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_uid: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    sample_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    k_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    q_values_json: Mapped[dict[str, float] | None] = mapped_column(JSON, nullable=True)
    cv_error: Mapped[float | None] = mapped_column(Float, nullable=True)


class ROHResult(Base):
    """Résumé ROH par échantillon."""

    __tablename__ = "roh_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_uid: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    sample_code: Mapped[str] = mapped_column(String(255), nullable=False)
    n_roh: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_roh_length_mb: Mapped[float | None] = mapped_column(Float, nullable=True)


class IBDResult(Base):
    """Résumé IBD/KING par paire ou métrique d'indépendance."""

    __tablename__ = "ibd_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_uid: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    sample_a: Mapped[str] = mapped_column(String(255), nullable=False)
    sample_b: Mapped[str | None] = mapped_column(String(255), nullable=True)
    kinship: Mapped[float | None] = mapped_column(Float, nullable=True)
    relationship: Mapped[str | None] = mapped_column(String(100), nullable=True)


class SelectionScore(Base):
    """Scores de sélection WGS par échantillon."""

    __tablename__ = "selection_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_uid: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    sample_code: Mapped[str] = mapped_column(String(255), nullable=False)
    pca_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    admixture_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ibd_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    roh_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    s_div: Mapped[float | None] = mapped_column(Float, nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class WGSSelection(Base):
    """Décision finale de sélection WGS."""

    __tablename__ = "wgs_selection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_uid: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    sample_code: Mapped[str] = mapped_column(String(255), nullable=False)
    selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    selection_arm: Mapped[str | None] = mapped_column(String(120), nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)


class Report(Base):
    """Rapport généré par un job."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_uid: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    relative_path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="created", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


# Compatibilité avec les anciens noms du scaffold v4.
Dataset = Cohort
FileRecord = InputFile
PipelineRun = AnalysisJob
PipelineStep = AnalysisStep
