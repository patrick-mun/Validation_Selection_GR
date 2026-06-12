"""Routes de l'application web.

Contrat d'architecture (AGENTS.md §2) :
- une vue VALIDE les paramètres puis crée un job ; elle n'exécute JAMAIS de
  commande bioinformatique ni de shell, et ne bloque pas sur l'analyse ;
- l'exécution est faite par le worker ; le front interroge le statut en JSON.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from genorun_validation.jobs.manager import get_default_job_manager
from genorun_validation.jobs.schemas import JobStatus
from genorun_validation.utils.validators import ValidationError, validate_identifier

bp = Blueprint("main", __name__)


@bp.get("/")
def dashboard():
    """Tableau de bord : liste des derniers runs."""
    manager = get_default_job_manager()
    jobs = manager.list_jobs(limit=20)
    return render_template("dashboard.html", jobs=jobs)


@bp.post("/api/jobs")
def create_job():
    """Crée un job d'analyse et le met en file (délégué au worker).

    # SAFETY: chaque paramètre est validé avant toute création de job.
    """
    payload = request.get_json(silent=True) or request.form
    try:
        dataset = validate_identifier(str(payload.get("dataset", "")), field_name="dataset")
        profile = validate_identifier(str(payload.get("profile", "")), field_name="profile")
        strategy = validate_identifier(str(payload.get("strategy", "")), field_name="strategy")
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    manager = get_default_job_manager()
    job = manager.create_job(dataset=dataset, profile=profile, strategy=strategy)
    # WHY: l'interface met le job en file ; le worker externe l'exécutera.
    manager.update_status(job, JobStatus.QUEUED, "Job mis en file depuis l'interface web.")
    return jsonify({"job_id": job.job_id, "status": job.status.value}), 201


@bp.get("/api/jobs/<job_id>/status")
def job_status(job_id: str):
    """Renvoie l'état d'un job au format JSON (consommé par le polling vanilla)."""
    try:
        validate_identifier(job_id, field_name="job_id")
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400

    manager = get_default_job_manager()
    try:
        job = manager.get_job(job_id)
    except (FileNotFoundError, KeyError):
        return jsonify({"error": "Job introuvable."}), 404

    return jsonify(
        {
            "job_id": job.job_id,
            "status": job.status.value,
            "message": job.message,
            "steps": job.steps,
            "updated_at": job.updated_at,
        }
    )


@bp.get("/runs/<run_id>")
def run_detail(run_id: str):
    """Détail d'un run (métriques, étapes, logs)."""
    try:
        validate_identifier(run_id, field_name="run_id")
    except ValidationError:
        return render_template("dashboard.html", jobs=[]), 404

    manager = get_default_job_manager()
    try:
        job = manager.get_job(run_id)
    except (FileNotFoundError, KeyError):
        return render_template("dashboard.html", jobs=[]), 404
    log_tail = manager.tail_log(job, max_lines=80)
    return render_template("run_detail.html", job=job, log_tail=log_tail)
