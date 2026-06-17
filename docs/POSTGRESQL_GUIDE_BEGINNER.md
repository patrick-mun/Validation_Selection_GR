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

Connexion depuis le terminal du Mac, via le port exposé par Docker :

```bash
PGPASSWORD=change-me-local-dev psql -h localhost -p 55432 -U genorun -d genorun_validation
```

Connexion DBeaver :

```text
Host: localhost
Port: 55432
Database: genorun_validation
Username: genorun
Password: change-me-local-dev
```

Le port `5432` peut déjà être utilisé par PostgreSQL Homebrew sur le Mac. Pour
éviter cette confusion, le Docker Compose de développement expose PostgreSQL sur
`55432` côté machine hôte, tout en gardant `5432` comme port interne entre
conteneurs.

Lister les tables :

```sql
\dt
```

Voir les jobs :

```sql
SELECT job_uid, dataset_name, strategy_name, status, created_at FROM analysis_jobs ORDER BY created_at DESC;
```

Voir les étapes de jobs :

```sql
SELECT step_name, status, message, updated_at
FROM analysis_steps
ORDER BY updated_at DESC
LIMIT 20;
```

Voir les événements d'audit :

```sql
SELECT event_type, job_uid, message, created_at
FROM audit_events
ORDER BY created_at DESC
LIMIT 20;
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
POSTGRES_PORT=55432
GENORUN_DATABASE_URL=postgresql+psycopg://genorun:<mot-de-passe-local>@genorun-db:5432/genorun_validation
```

En local hors Docker, l'hôte de l'URL devient généralement `localhost` au lieu de
`genorun-db`, et le port externe est celui publié par Docker (`55432` dans le
scaffold local).

## Diagnostic rapide DBeaver

| Message | Cause probable | Correction |
|---|---|---|
| `role "genorun" does not exist` | DBeaver se connecte au PostgreSQL local du Mac sur `5432`. | Utiliser le port `55432` ou arrêter PostgreSQL Homebrew. |
| `Connection refused` sur `55432` | Docker n'a pas appliqué le port de `.env`. | Vérifier `.env`, puis `docker compose down && docker compose up -d`. |
| Tables absentes | Les migrations Alembic ne sont pas passées. | Lire `docker compose logs -f genorun-app`, puis relancer `python -m alembic upgrade head` dans `genorun-app`. |

Vérifier le port publié :

```bash
docker compose port genorun-db 5432
```

Résultat attendu en développement local :

```text
0.0.0.0:55432
```

## File de jobs

Quand `GENORUN_ENABLE_DATABASE=true`, PostgreSQL devient la file officielle des jobs : le worker lit les jobs `created` ou `queued` dans `analysis_jobs`.

Le dossier `work/runs/<job_id>/` reste indispensable : il conserve la configuration figée, le manifest, le statut JSON, les logs longs, les sorties et les rapports.
