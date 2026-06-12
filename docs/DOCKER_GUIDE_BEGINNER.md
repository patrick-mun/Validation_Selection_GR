# Guide Docker débutant — Génome Réunion Validation

## Objectif

Docker n'est pas obligatoire pour comprendre le code, mais il devient la cible propre pour reproduire et déployer le logiciel.

Le scaffold prévoit trois services :

```text
genorun-app       interface web (Flask + vanilla)
genorun-worker    exécution des jobs
genorun-db        PostgreSQL
```

## Préparation

```bash
cp .env.example .env
# Modifier POSTGRES_PASSWORD et GENORUN_SECRET_KEY dans .env avant un vrai déploiement.
```

## Commandes de base

```bash
docker --version
docker compose up --build
docker compose down
docker compose logs -f
docker compose logs -f genorun-app
docker compose logs -f genorun-worker
docker compose logs -f genorun-db
```

L'interface sera disponible sur :

```text
http://localhost:8000
```

## Initialiser la base dans Docker

L’image applicative exécute `alembic upgrade head` au démarrage de `genorun-app`.

Pour relancer explicitement les migrations :

```bash
docker compose exec genorun-app conda run -n genorun-validation alembic upgrade head
```

Pour une initialisation rapide hors Alembic, réservée au développement :

```bash
docker compose exec genorun-app conda run -n genorun-validation python scripts/init_database.py
```

## Mode de fonctionnement

1. L'utilisateur clique sur `Lancer l'analyse`.
2. L'interface web crée un job dans `work/runs/<job_id>/`.
3. L'interface web met le job au statut `queued`.
4. Le service `genorun-worker` surveille les jobs et exécute le run.
5. PostgreSQL indexe les statuts, paramètres et événements d'audit.
6. Les gros fichiers restent dans les volumes `data/`, `work/`, `results/`, `reports/`, `logs/`.

## Règle importante

Ne jamais copier de vraies données génétiques dans l'image Docker. Les données sont montées en volumes et doivent rester hors Git.

## Vérifications utiles

```bash
docker compose ps
docker compose logs -f genorun-app
docker compose logs -f genorun-worker
docker compose exec genorun-app conda run -n genorun-validation python -c "import genorun_validation; print(genorun_validation.__version__)"
```

La commande d'import ci-dessus vérifie que le package `src/genorun_validation` a bien été installé en mode éditable dans l'image Docker.
