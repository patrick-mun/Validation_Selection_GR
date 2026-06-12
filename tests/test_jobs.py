from pathlib import Path

from genorun_validation.jobs.manager import JobManager
from genorun_validation.jobs.schemas import JobStatus
from genorun_validation.jobs.worker import LocalPipelineWorker


def test_create_job_writes_audit_files(tmp_path: Path):
    manager = JobManager(project_root=tmp_path, runs_root=tmp_path / "runs")
    job = manager.create_job("1000G chr22", "Profil C", "Géo-ancestrale + découverte")

    assert job.status == JobStatus.CREATED
    assert job.config_path.exists()
    assert job.manifest_path.exists()
    assert job.status_path.exists()
    assert job.log_path.parent.exists()


def test_worker_completes_dry_run(tmp_path: Path):
    manager = JobManager(project_root=tmp_path, runs_root=tmp_path / "runs")
    job = manager.create_job("1000G chr22", "Profil C", "Géo-ancestrale + découverte")

    worker = LocalPipelineWorker(manager=manager, delay_seconds=0)
    completed = worker.run(job.job_id)

    assert completed.status == JobStatus.COMPLETED
    assert (completed.outputs_dir / "summary_metrics.json").exists()
    assert (completed.report_dir / "rapport_demo.md").exists()


def test_list_runnable_jobs_filesystem_mode(tmp_path: Path):
    manager = JobManager(project_root=tmp_path, runs_root=tmp_path / "runs", database_enabled=False)
    runnable = manager.create_job("1000G chr22", "Profil C", "Géo-ancestrale + découverte")
    completed = manager.create_job("1000G chr22", "Profil C", "Géo-ancestrale + découverte")
    manager.update_status(completed, JobStatus.COMPLETED, "Déjà terminé")

    job_ids = {job.job_id for job in manager.list_runnable_jobs(limit=20)}

    assert runnable.job_id in job_ids
    assert completed.job_id not in job_ids
