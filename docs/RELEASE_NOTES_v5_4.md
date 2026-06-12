# Notes de version — v5.4 infrastructure

## Objet

Cette version corrige les points d'infrastructure relevés lors de l'audit objectif de la version v5.3.
Elle ne modifie pas encore les algorithmes scientifiques ; elle stabilise le socle logiciel avant l'implémentation QC/PCA/ADMIXTURE/KING/ROH/S_div.

## Corrections réalisées

### Interface et commandes de qualité

- Remplacement des références actives à l'ancien dossier `app/` par `web/`.
- Mise à jour de la CI, du README, de `AGENTS.md`, de `.codex/rules.md`, de `CLAUDE.md`, de `CODE_INDEX.md` et de la roadmap.
- Commande officielle :

```bash
python -m compileall src scripts web
ruff check src scripts web tests
ruff format --check src scripts web tests
pytest -q
```

### Docker

- Le `Dockerfile` installe désormais le package avec `pip install -e .`.
- `PYTHONPATH=/app/src` est défini dans l'image.
- `genorun-app` applique `alembic upgrade head` avant de lancer Gunicorn.
- `docker-compose.yml` utilise des variables d'environnement et des valeurs par défaut de développement.
- `.env.example` contient les variables Docker/PostgreSQL à copier en `.env`.

### PostgreSQL / Alembic

- La migration initiale est devenue explicite table par table.
- `Base.metadata.create_all()` n'est plus utilisé dans la migration Alembic.
- PostgreSQL sert de file officielle des jobs lorsque `GENORUN_ENABLE_DATABASE=true`.
- `work/runs/<job_id>/` reste la trace reproductible des runs.

### Worker

- Ajout de `JobRepository.list_job_uids_by_status()`.
- Ajout de `JobManager.list_runnable_jobs()`.
- `scripts/run_worker_loop.py` utilise désormais cette méthode commune au lieu de scanner directement les statuts.

### Tests

- Ajout d'un test filesystem pour les jobs exécutables.
- Ajout d'un test PostgreSQL/SQLAlchemy conditionnel pour la file de jobs.

## Vérifications réalisées dans le sandbox

```bash
python -m compileall src scripts web
PYTHONPATH=src pytest -q
```

Résultat : 26 tests passés.

## À tester hors sandbox

- `docker compose up --build`
- `docker compose exec genorun-app conda run -n genorun-validation alembic upgrade head`
- création d'un job depuis l'interface Flask ;
- prise en charge du job par `genorun-worker` ;
- vérification de la table `analysis_jobs` dans PostgreSQL.
