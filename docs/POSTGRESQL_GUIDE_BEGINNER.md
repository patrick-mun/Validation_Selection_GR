# Guide PostgreSQL débutant — Génome Réunion Validation

## Pourquoi PostgreSQL dès le départ ?

Le logiciel doit suivre des cohortes, échantillons, jobs, logs, statuts, paramètres, scores, sélections WGS et rapports. PostgreSQL est plus robuste que SQLite pour ce type de suivi.

## Ce que PostgreSQL stocke

```text
projets
cohortes
échantillons anonymisés
métadonnées de fichiers
jobs
statuts
paramètres
scores
rapports
audit
```

## Ce que PostgreSQL ne stocke jamais

```text
VCF / BCF
BAM / CRAM
BED / BIM / FAM
PED / MAP
fichiers WGS lourds
logs très volumineux
```

La base conserve seulement les chemins relatifs, tailles, checksums, types de fichiers et statuts.

## Connexion dans Docker

```bash
docker compose exec genorun-db psql -U genorun -d genorun_validation
```

Lister les tables :

```sql
\dt
```

Voir les jobs :

```sql
SELECT job_uid, dataset_name, strategy_name, status, created_at FROM analysis_jobs ORDER BY created_at DESC;
```

## Migrations Alembic

Appliquer les migrations :

```bash
alembic upgrade head
```

Créer une migration après modification des modèles :

```bash
alembic revision --autogenerate -m "message clair"
```

Toute modification du modèle de données doit être documentée dans `docs/DEV_TRACKING.md` et vérifiée par un test.


## Variables .env

Le fichier `.env.example` doit être copié en `.env` avant Docker :

```bash
cp .env.example .env
```

Variables principales :

```text
POSTGRES_DB=genorun_validation
POSTGRES_USER=genorun
POSTGRES_PASSWORD=<mot-de-passe-local>
GENORUN_DATABASE_URL=postgresql+psycopg://genorun:<mot-de-passe-local>@genorun-db:5432/genorun_validation
```

En local hors Docker, l'hôte de l'URL devient généralement `localhost` au lieu de `genorun-db`.

## File de jobs

Quand `GENORUN_ENABLE_DATABASE=true`, PostgreSQL devient la file officielle des jobs : le worker lit les jobs `created` ou `queued` dans `analysis_jobs`.

Le dossier `work/runs/<job_id>/` reste indispensable : il conserve la configuration figée, le manifest, le statut JSON, les logs longs, les sorties et les rapports.
