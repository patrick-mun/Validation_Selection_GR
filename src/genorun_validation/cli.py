"""CLI principale du pipeline Génome Réunion."""
from __future__ import annotations

import typer

from genorun_validation.jobs.manager import JobManager
from genorun_validation.jobs.worker import LocalPipelineWorker
from genorun_validation.utils.launch_parameters import (
    DEFAULT_DATASET,
    DEFAULT_PROFILE,
    DEFAULT_STRATEGY,
    LaunchParameters,
    validate_launch_parameters,
)
from genorun_validation.utils.validators import ValidationError, validate_identifier

app = typer.Typer(help="Génome Réunion Validation Pipeline")
jobs_app = typer.Typer(help="Gestion des jobs locaux")
app.add_typer(jobs_app, name="jobs")


@app.command()
def run(config: str = "config/demo_chr22.yaml") -> None:
    """Explique le flux sécurisé attendu pour lancer un pipeline."""
    typer.echo(f"Commande historique informative pour la configuration : {config}")
    typer.echo("Aucun pipeline n'est lancé directement par cette commande.")
    typer.echo("Flux sécurisé : `genorun-validation jobs create`, puis worker dédié.")


@jobs_app.command("create")
def create_job(
    dataset: str = DEFAULT_DATASET,
    profile: str = DEFAULT_PROFILE,
    strategy: str = DEFAULT_STRATEGY,
) -> None:
    """Crée un job local sans l'exécuter."""
    launch_parameters = _validate_cli_launch_parameters(dataset=dataset, profile=profile, strategy=strategy)
    job = JobManager().create_job(
        dataset=launch_parameters.dataset,
        profile=launch_parameters.profile,
        strategy=launch_parameters.strategy,
        parameters={"created_from": "cli"},
    )
    typer.echo(job.job_id)


@jobs_app.command("worker")
def run_worker(job_id: str, delay: float = 0.2) -> None:
    """Exécute un job local par son identifiant."""
    try:
        validate_identifier(job_id, field_name="job_id")
    except ValidationError as exc:
        raise typer.BadParameter(str(exc), param_hint="job_id") from exc
    worker = LocalPipelineWorker(manager=JobManager(), delay_seconds=delay)
    job = worker.run(job_id)
    typer.echo(f"{job.job_id}: {job.status.value}")


@jobs_app.command("list")
def list_jobs(limit: int = 10) -> None:
    """Liste les derniers jobs locaux."""
    for job in JobManager().list_jobs(limit=limit):
        typer.echo(f"{job.job_id}\t{job.status.value}\t{job.dataset}\t{job.strategy}")


def _validate_cli_launch_parameters(dataset: str, profile: str, strategy: str) -> LaunchParameters:
    """Convertit les erreurs de validation métier en erreurs CLI lisibles."""
    try:
        return validate_launch_parameters(dataset=dataset, profile=profile, strategy=strategy)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc)) from exc


if __name__ == "__main__":
    app()
