from pathlib import Path

import pytest

from genorun_validation.external.command_runner import run_command


def test_command_runner_rejects_unknown_executable(tmp_path: Path):
    with pytest.raises(ValueError):
        run_command(["unknown_tool", "--version"], cwd=tmp_path, stdout_path=tmp_path / "out.log", stderr_path=tmp_path / "err.log")
