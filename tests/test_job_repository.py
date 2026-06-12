from pathlib import Path

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from genorun_validation.database.base import Base
from genorun_validation.database.models import AnalysisJob, AuditEvent
from genorun_validation.database.session import build_engine
from genorun_validation.jobs.manager import JobManager
from genorun_validation.jobs.schemas import JobStatus


def _session_factory():
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


def test_job_manager_can_index_job_in_database(tmp_path: Path):
    Session = _session_factory()
    manager = JobManager(
        project_root=tmp_path,
        runs_root=tmp_path / "runs",
        database_enabled=True,
        session_factory=Session,
    )

    job = manager.create_job("1000G chr22", "Profil C", "Géo-ancestrale + découverte")
    manager.update_status(job, JobStatus.QUEUED, "Test queued")

    with Session() as session:
        db_job = session.scalar(select(AnalysisJob).where(AnalysisJob.job_uid == job.job_id))
        assert db_job is not None
        assert db_job.status == "queued"
        assert db_job.run_dir.endswith(job.job_id)

        audit_events = session.scalars(select(AuditEvent).where(AuditEvent.job_uid == job.job_id)).all()
        assert len(audit_events) >= 2


def test_job_manager_lists_runnable_jobs_from_database(tmp_path: Path):
    Session = _session_factory()
    manager = JobManager(
        project_root=tmp_path,
        runs_root=tmp_path / "runs",
        database_enabled=True,
        session_factory=Session,
    )

    queued = manager.create_job("1000G chr22", "Profil C", "Géo-ancestrale + découverte")
    manager.update_status(queued, JobStatus.QUEUED, "À traiter")
    completed = manager.create_job("1000G chr22", "Profil C", "Géo-ancestrale + découverte")
    manager.update_status(completed, JobStatus.COMPLETED, "Déjà traité")

    job_ids = [job.job_id for job in manager.list_runnable_jobs(limit=20)]

    assert queued.job_id in job_ids
    assert completed.job_id not in job_ids
