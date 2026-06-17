from pathlib import Path

from typer.testing import CliRunner

from genorun_validation.cli import app


def test_cli_help_lists_job_commands():
    runner = CliRunner()

    result = runner.invoke(app, ["jobs", "--help"])

    assert result.exit_code == 0
    assert "create" in result.output
    assert "worker" in result.output
    assert "list" in result.output


def test_cli_create_and_list_use_safe_phase0_identifiers(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("GENORUN_RUNS_ROOT", str(tmp_path / "runs"))
    runner = CliRunner()

    create_result = runner.invoke(app, ["jobs", "create"])

    assert create_result.exit_code == 0
    job_id = create_result.output.strip()
    assert job_id.startswith("run_")

    list_result = runner.invoke(app, ["jobs", "list", "--limit", "5"])

    assert list_result.exit_code == 0
    assert job_id in list_result.output
    assert "1000G_chr22" in list_result.output
    assert "geo_ancestrale_decouverte" in list_result.output


def test_cli_create_rejects_unknown_dataset(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("GENORUN_RUNS_ROOT", str(tmp_path / "runs"))
    runner = CliRunner()

    result = runner.invoke(app, ["jobs", "create", "--dataset", "dataset_inconnu"])

    assert result.exit_code != 0
    assert "dataset inconnu" in result.output
    assert not (tmp_path / "runs").exists()


def test_cli_worker_rejects_unsafe_job_id():
    runner = CliRunner()

    result = runner.invoke(app, ["jobs", "worker", "../bad"])

    assert result.exit_code != 0
    assert "job_id invalide" in result.output
