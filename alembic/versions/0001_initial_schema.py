"""Initial explicit schema for Génome Réunion Validation.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-12
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crée explicitement les tables du scaffold.

    WHY: la migration initiale ne dépend plus de `Base.metadata.create_all()` afin
    que le schéma versionné reste lisible, auditable et révisable par un
    développeur ou par la DSIO avant déploiement.
    """
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("name", name="uq_projects_name"),
    )

    op.create_table(
        "cohorts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("cohort_type", sa.String(length=100), nullable=True),
        sa.Column("genome_build", sa.String(length=50), nullable=True),
        sa.Column("n_samples_expected", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "samples",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cohort_id", sa.Integer(), sa.ForeignKey("cohorts.id"), nullable=False),
        sa.Column("sample_code", sa.String(length=255), nullable=False),
        sa.Column("sector", sa.String(length=100), nullable=True),
        sa.Column("sex", sa.String(length=30), nullable=True),
        sa.Column("inclusion_status", sa.String(length=50), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("cohort_id", "sample_code", name="uq_samples_cohort_code"),
    )

    op.create_table(
        "input_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("cohort_id", sa.Integer(), sa.ForeignKey("cohorts.id"), nullable=True),
        sa.Column("job_id", sa.String(length=120), nullable=True),
        sa.Column("file_role", sa.String(length=100), nullable=False),
        sa.Column("file_type", sa.String(length=100), nullable=False),
        sa.Column("relative_path", sa.Text(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=128), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("validation_status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_input_files_job_id", "input_files", ["job_id"])

    op.create_table(
        "analysis_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_uid", sa.String(length=120), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("cohort_id", sa.Integer(), sa.ForeignKey("cohorts.id"), nullable=True),
        sa.Column("dataset_name", sa.String(length=255), nullable=False),
        sa.Column("profile_name", sa.String(length=100), nullable=True),
        sa.Column("strategy_name", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("parameters_json", sa.JSON(), nullable=True),
        sa.Column("run_dir", sa.Text(), nullable=False),
        sa.Column("config_path", sa.Text(), nullable=True),
        sa.Column("manifest_path", sa.Text(), nullable=True),
        sa.Column("log_path", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("job_uid", name="uq_analysis_jobs_job_uid"),
    )
    op.create_index("ix_analysis_jobs_job_uid", "analysis_jobs", ["job_uid"])
    op.create_index("ix_analysis_jobs_status", "analysis_jobs", ["status"])

    op.create_table(
        "analysis_steps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("analysis_job_id", sa.Integer(), sa.ForeignKey("analysis_jobs.id"), nullable=False),
        sa.Column("step_name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("log_path", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("analysis_job_id", "step_name", name="uq_analysis_step_job_name"),
    )

    op.create_table(
        "job_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("analysis_job_id", sa.Integer(), sa.ForeignKey("analysis_jobs.id"), nullable=True),
        sa.Column("job_uid", sa.String(length=120), nullable=False),
        sa.Column("level", sa.String(length=30), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_job_logs_job_uid", "job_logs", ["job_uid"])

    op.create_table(
        "software_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("analysis_job_id", sa.Integer(), sa.ForeignKey("analysis_jobs.id"), nullable=True),
        sa.Column("tool_name", sa.String(length=120), nullable=False),
        sa.Column("version", sa.String(length=120), nullable=True),
        sa.Column("command", sa.Text(), nullable=True),
        sa.Column("detected", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("job_uid", sa.String(length=120), nullable=True),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("actor", sa.String(length=120), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_events_job_uid", "audit_events", ["job_uid"])

    op.create_table(
        "qc_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_uid", sa.String(length=120), nullable=False),
        sa.Column("n_samples_before", sa.Integer(), nullable=True),
        sa.Column("n_samples_after", sa.Integer(), nullable=True),
        sa.Column("n_variants_before", sa.Integer(), nullable=True),
        sa.Column("n_variants_after", sa.Integer(), nullable=True),
        sa.Column("call_rate", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_qc_metrics_job_uid", "qc_metrics", ["job_uid"])

    op.create_table(
        "pca_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_uid", sa.String(length=120), nullable=False),
        sa.Column("sample_code", sa.String(length=255), nullable=True),
        sa.Column("pc_values_json", sa.JSON(), nullable=True),
    )
    op.create_index("ix_pca_results_job_uid", "pca_results", ["job_uid"])

    op.create_table(
        "admixture_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_uid", sa.String(length=120), nullable=False),
        sa.Column("sample_code", sa.String(length=255), nullable=True),
        sa.Column("k_value", sa.Integer(), nullable=True),
        sa.Column("q_values_json", sa.JSON(), nullable=True),
        sa.Column("cv_error", sa.Float(), nullable=True),
    )
    op.create_index("ix_admixture_results_job_uid", "admixture_results", ["job_uid"])

    op.create_table(
        "roh_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_uid", sa.String(length=120), nullable=False),
        sa.Column("sample_code", sa.String(length=255), nullable=False),
        sa.Column("n_roh", sa.Integer(), nullable=True),
        sa.Column("total_roh_length_mb", sa.Float(), nullable=True),
    )
    op.create_index("ix_roh_results_job_uid", "roh_results", ["job_uid"])

    op.create_table(
        "ibd_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_uid", sa.String(length=120), nullable=False),
        sa.Column("sample_a", sa.String(length=255), nullable=False),
        sa.Column("sample_b", sa.String(length=255), nullable=True),
        sa.Column("kinship", sa.Float(), nullable=True),
        sa.Column("relationship", sa.String(length=100), nullable=True),
    )
    op.create_index("ix_ibd_results_job_uid", "ibd_results", ["job_uid"])

    op.create_table(
        "selection_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_uid", sa.String(length=120), nullable=False),
        sa.Column("sample_code", sa.String(length=255), nullable=False),
        sa.Column("pca_score", sa.Float(), nullable=True),
        sa.Column("admixture_score", sa.Float(), nullable=True),
        sa.Column("ibd_score", sa.Float(), nullable=True),
        sa.Column("roh_score", sa.Float(), nullable=True),
        sa.Column("s_div", sa.Float(), nullable=True),
        sa.Column("decision_reason", sa.Text(), nullable=True),
    )
    op.create_index("ix_selection_scores_job_uid", "selection_scores", ["job_uid"])

    op.create_table(
        "wgs_selection",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_uid", sa.String(length=120), nullable=False),
        sa.Column("sample_code", sa.String(length=255), nullable=False),
        sa.Column("selected", sa.Boolean(), nullable=False),
        sa.Column("selection_arm", sa.String(length=120), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("justification", sa.Text(), nullable=True),
    )
    op.create_index("ix_wgs_selection_job_uid", "wgs_selection", ["job_uid"])

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_uid", sa.String(length=120), nullable=False),
        sa.Column("report_type", sa.String(length=50), nullable=False),
        sa.Column("relative_path", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_reports_job_uid", "reports", ["job_uid"])


def downgrade() -> None:
    """Supprime les tables dans l'ordre inverse des dépendances."""
    op.drop_index("ix_reports_job_uid", table_name="reports")
    op.drop_table("reports")
    op.drop_index("ix_wgs_selection_job_uid", table_name="wgs_selection")
    op.drop_table("wgs_selection")
    op.drop_index("ix_selection_scores_job_uid", table_name="selection_scores")
    op.drop_table("selection_scores")
    op.drop_index("ix_ibd_results_job_uid", table_name="ibd_results")
    op.drop_table("ibd_results")
    op.drop_index("ix_roh_results_job_uid", table_name="roh_results")
    op.drop_table("roh_results")
    op.drop_index("ix_admixture_results_job_uid", table_name="admixture_results")
    op.drop_table("admixture_results")
    op.drop_index("ix_pca_results_job_uid", table_name="pca_results")
    op.drop_table("pca_results")
    op.drop_index("ix_qc_metrics_job_uid", table_name="qc_metrics")
    op.drop_table("qc_metrics")
    op.drop_index("ix_audit_events_job_uid", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_table("software_versions")
    op.drop_index("ix_job_logs_job_uid", table_name="job_logs")
    op.drop_table("job_logs")
    op.drop_table("analysis_steps")
    op.drop_index("ix_analysis_jobs_status", table_name="analysis_jobs")
    op.drop_index("ix_analysis_jobs_job_uid", table_name="analysis_jobs")
    op.drop_table("analysis_jobs")
    op.drop_index("ix_input_files_job_id", table_name="input_files")
    op.drop_table("input_files")
    op.drop_table("samples")
    op.drop_table("cohorts")
    op.drop_table("projects")
