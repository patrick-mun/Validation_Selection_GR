"""Schémas simples pour les jobs locaux."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any


class JobStatus(StrEnum):
    """Statuts standard d'un job local."""

    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class PipelineJob:
    """Représentation persistable d'un job pipeline."""

    job_id: str
    dataset: str
    profile: str
    strategy: str
    run_dir: Path
    status: JobStatus = JobStatus.CREATED
    created_at: str = field(default_factory=lambda: utc_now_iso())
    updated_at: str = field(default_factory=lambda: utc_now_iso())
    started_at: str | None = None
    ended_at: str | None = None
    message: str | None = None
    config_path: Path | None = None
    manifest_path: Path | None = None
    status_path: Path | None = None
    log_path: Path | None = None
    outputs_dir: Path | None = None
    report_dir: Path | None = None
    steps: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convertit le job en dictionnaire JSON-sérialisable."""
        return {
            "job_id": self.job_id,
            "dataset": self.dataset,
            "profile": self.profile,
            "strategy": self.strategy,
            "run_dir": str(self.run_dir),
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "message": self.message,
            "config_path": str(self.config_path) if self.config_path else None,
            "manifest_path": str(self.manifest_path) if self.manifest_path else None,
            "status_path": str(self.status_path) if self.status_path else None,
            "log_path": str(self.log_path) if self.log_path else None,
            "outputs_dir": str(self.outputs_dir) if self.outputs_dir else None,
            "report_dir": str(self.report_dir) if self.report_dir else None,
            "steps": self.steps,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PipelineJob":
        """Reconstruit un job à partir d'un dictionnaire JSON."""
        return cls(
            job_id=payload["job_id"],
            dataset=payload["dataset"],
            profile=payload["profile"],
            strategy=payload["strategy"],
            run_dir=Path(payload["run_dir"]),
            status=JobStatus(payload.get("status", JobStatus.CREATED)),
            created_at=payload.get("created_at", utc_now_iso()),
            updated_at=payload.get("updated_at", utc_now_iso()),
            started_at=payload.get("started_at"),
            ended_at=payload.get("ended_at"),
            message=payload.get("message"),
            config_path=_optional_path(payload.get("config_path")),
            manifest_path=_optional_path(payload.get("manifest_path")),
            status_path=_optional_path(payload.get("status_path")),
            log_path=_optional_path(payload.get("log_path")),
            outputs_dir=_optional_path(payload.get("outputs_dir")),
            report_dir=_optional_path(payload.get("report_dir")),
            steps=payload.get("steps", []),
        )


def utc_now_iso() -> str:
    """Horodatage UTC ISO-8601."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _optional_path(value: str | None) -> Path | None:
    return Path(value) if value else None
