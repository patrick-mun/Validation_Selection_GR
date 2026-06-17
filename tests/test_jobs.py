from pathlib import Path

import pytest

from genorun_validation.jobs.manager import JobManager
from genorun_validation.jobs.schemas import JobStatus
from genorun_validation.jobs.worker import LocalPipelineWorker
from genorun_validation.utils.validators import ValidationError


def test_create_job_writes_audit_files(tmp_path: Path):
    manager = JobManager(project_root=tmp_path, runs_root=tmp_path / "runs")
    job = manager.create_job("1000G_chr22", "profil_C", "geo_ancestrale_decouverte")

    assert job.status == JobStatus.CREATED
    assert job.config_path.exists()
    assert job.manifest_path.exists()
    assert job.status_path.exists()
    assert job.log_path.parent.exists()


def test_worker_completes_dry_run(tmp_path: Path):
    manager = JobManager(project_root=tmp_path, runs_root=tmp_path / "runs")
    job = manager.create_job("1000G_chr22", "profil_C", "geo_ancestrale_decouverte")

    worker = LocalPipelineWorker(manager=manager, delay_seconds=0)
    completed = worker.run(job.job_id)

    assert completed.status == JobStatus.COMPLETED
    assert (completed.outputs_dir / "summary_metrics.json").exists()
    assert (completed.report_dir / "rapport_demo.md").exists()


def test_list_runnable_jobs_filesystem_mode(tmp_path: Path):
    manager = JobManager(project_root=tmp_path, runs_root=tmp_path / "runs", database_enabled=False)
    runnable = manager.create_job("1000G_chr22", "profil_C", "geo_ancestrale_decouverte")
    completed = manager.create_job("1000G_chr22", "profil_C", "geo_ancestrale_decouverte")
    manager.update_status(completed, JobStatus.COMPLETED, "Déjà terminé")

    job_ids = {job.job_id for job in manager.list_runnable_jobs(limit=20)}

    assert runnable.job_id in job_ids
    assert completed.job_id not in job_ids


def test_create_job_rejects_unknown_phase0_parameters(tmp_path: Path):
    manager = JobManager(project_root=tmp_path, runs_root=tmp_path / "runs")

    with pytest.raises(ValidationError, match="strategy inconnu"):
        manager.create_job("1000G_chr22", "profil_C", "strategie_inconnue")
