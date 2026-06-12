from pathlib import Path

import pytest

from genorun_validation.settings import relative_to_project


def test_relative_to_project_accepts_inside_project(tmp_path: Path):
    project_root = tmp_path / "project"
    file_path = project_root / "work" / "runs" / "run_1" / "status.json"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("{}")

    assert relative_to_project(file_path, project_root=project_root) == "work/runs/run_1/status.json"


def test_relative_to_project_rejects_outside_project(tmp_path: Path):
    with pytest.raises(ValueError):
        relative_to_project(tmp_path / "outside.txt", project_root=tmp_path / "project")
