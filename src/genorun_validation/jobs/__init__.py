"""Gestion locale des jobs d'analyse.

Ce package fournit le MVP d'orchestration locale : l'interface crée un job,
puis un worker dédié exécute le pipeline et écrit les statuts/logs/résultats.
"""

from .manager import JobManager, get_default_job_manager
from .schemas import JobStatus, PipelineJob

__all__ = ["JobManager", "get_default_job_manager", "JobStatus", "PipelineJob"]
