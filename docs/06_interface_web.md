# Interface web (Flask + front vanilla)

L'interface est une application web servie par Flask, avec un front en HTML/CSS/JS **vanilla** (aucun framework d'interface, aucune étape de build). Elle reste une couche de présentation et de pilotage : elle ne contient ni logique scientifique, ni commande bioinformatique.

> Choix d'architecture (voir `docs/DEV_TRACKING.md`) : Flask sert de fine couche de présentation au-dessus du backend pipeline existant. La base de données reste gérée par SQLAlchemy + Alembic (pas d'ORM Django).

## Rôle autorisé

L'interface peut : afficher datasets, profils et stratégies ; collecter et valider les paramètres ; créer un job et le mettre en file ; afficher progression, logs, résultats, rapports et alertes via des endpoints JSON interrogés par le front.

## Rôle interdit

L'interface ne doit pas : construire de commandes shell libres ; exécuter directement PLINK, KING, ADMIXTURE, bcftools, Beagle ou SHAPEIT ; contenir la logique scientifique (S_div, sélection) ; contenir les parsers bioinformatiques ; stocker des données génétiques réelles ; bloquer la requête HTTP sur l'analyse.

## Flux de lancement

```text
Front vanilla : bouton « Lancer l'analyse » (fetch POST /api/jobs)
        ↓
Flask : route create_job() — valide les paramètres (utils/validators.py)
        ↓
JobManager.create_job(...)  →  statut QUEUED
        ↓
work/runs/<run_id>/config.yaml + manifest.json + status.json
        ↓
Worker externe (genorun-worker) exécute le job
        ↓
Front : polling GET /api/jobs/<id>/status (JSON) → mise à jour du DOM
```

L'interface ne lance pas le worker dans le processus web : elle met le job en file, et le service `genorun-worker` l'exécute (mode Docker), ou `scripts/run_worker.py`/`run_worker_loop.py` en local.

## Fichiers principaux

```text
web/__init__.py            Factory Flask (create_app)
web/wsgi.py                Point d'entrée gunicorn : gunicorn web.wsgi:app
web/routes.py              Routes : /, /api/jobs (POST), /api/jobs/<id>/status, /runs/<id>
web/templates/             base.html, dashboard.html, run_detail.html (HTML vanilla)
web/static/css/app.css     Styles vanilla (palette teal/navy/coral)
web/static/js/app.js       JS vanilla : soumission + polling du statut
```

Elles s'appuient sur :

```text
src/genorun_validation/jobs/manager.py     (create_job, get_job, list_jobs, tail_log)
src/genorun_validation/utils/validators.py (validation stricte des paramètres)
scripts/run_worker.py / run_worker_loop.py (exécution déléguée)
```

## Démarrage

```bash
# Développement
flask --app web run --debug          # http://127.0.0.1:5000

# Production (et Docker)
gunicorn web.wsgi:app --bind 0.0.0.0:8000 --workers 2
```
