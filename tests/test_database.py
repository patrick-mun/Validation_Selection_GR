import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from genorun_validation.database.base import Base
from genorun_validation.database.models import AnalysisJob, Project
from genorun_validation.database.session import build_engine


def test_database_engine_and_models_can_create_tables():
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)

    with Session() as session:
        session.add(Project(name="Test Génome Réunion"))
        session.add(AnalysisJob(job_uid="run_test", dataset_name="demo", run_dir="work/runs/run_test"))
        session.commit()

        job = session.scalar(select(AnalysisJob).where(AnalysisJob.job_uid == "run_test"))
        assert job is not None
        assert job.status == "created"
