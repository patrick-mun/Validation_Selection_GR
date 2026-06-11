import subprocess
from pathlib import Path

def run_command(cmd: list[str], cwd: str | Path | None = None):
    return subprocess.run(cmd, cwd=cwd, check=True, text=True)
