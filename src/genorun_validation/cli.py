"""CLI principale du pipeline Génome Réunion."""
from __future__ import annotations

import typer

from genorun_validation.jobs.manager import JobManager
from genorun_validation.jobs.worker import LocalPipelineWorker

app = typer.Typer(help="Génome Réunion Validation Pipeline")
jobs_app = typer.Typer(help="Gestion des jobs locaux")
app.add_typer(jobs_app, name="jobs")


@app.command()
def run(config: str = "config/demo_chr22.yaml") -> None:
    """Point d'entrée historique du pipeline."""
    typer.echo(f"Lancement du pipeline avec la configuration : {config}")
    typer.echo("Utiliser `genorun-validation jobs create` puis `jobs worker` pour le flux sécurisé.")


@jobs_app.command("create")
def create_job(
    dataset: str = "1000G chr22",
    profile: str = "Profil C",
    strategy: str = "Géo-ancestrale + découverte",
) -> None:
    """Crée un job local sans l'exécuter."""
    job = JobManager().create_job(dataset=dataset, profile=profile, strategy=strategy, parameters={"created_from": "cli"})
    typer.echo(job.job_id)


@jobs_app.command("worker")
def run_worker(job_id: str, delay: float = 0.2) -> None:
    """Exécute un job local par son identifiant."""
    worker = LocalPipelineWorker(manager=JobManager(), delay_seconds=delay)
    job = worker.run(job_id)
    typer.echo(f"{job.job_id}: {job.status.value}")


@jobs_app.command("list")
def list_jobs(limit: int = 10) -> None:
    """Liste les derniers jobs locaux."""
    for job in JobManager().list_jobs(limit=limit):
        typer.echo(f"{job.job_id}\t{job.status.value}\t{job.dataset}\t{job.strategy}")


if __name__ == "__main__":
    app()
