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

Par défaut, l'exemple expose PostgreSQL Docker sur le port `55432` côté Mac afin
d'éviter un conflit avec un PostgreSQL local Homebrew souvent présent sur
`5432`. Le port interne au réseau Docker reste `5432`.

## Première utilisation locale

Depuis la racine du dépôt :

```bash
docker compose up --build -d
docker compose ps
open http://localhost:8000
```

Services attendus :

```text
genorun-app       Up   interface web sur http://localhost:8000
genorun-worker    Up   worker dry-run en boucle
genorun-db        Up   PostgreSQL healthy, exposé sur localhost:55432
```

Vérifier les ports :

```bash
docker compose port genorun-db 5432
nc -zv localhost 55432
curl -I http://localhost:8000
```

La commande `docker compose port genorun-db 5432` doit afficher
`0.0.0.0:55432` si `.env` reprend l'exemple du dépôt.

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

Arrêter proprement sans supprimer les données PostgreSQL du volume Docker :

```bash
docker compose down
```

Supprimer aussi le volume PostgreSQL de développement local, uniquement si l'on
veut repartir d'une base vide :

```bash
docker compose down -v
```

L'interface sera disponible sur :

```text
http://localhost:8000
```

## Initialiser la base dans Docker

L’image applicative exécute `python -m alembic upgrade head` au démarrage de `genorun-app`.
Le worker peut afficher temporairement `[WORKER_QUEUE_WAIT]` si PostgreSQL est
joignable mais que les migrations ne sont pas encore terminées ; il réessaie
ensuite sans quitter.

Pour relancer explicitement les migrations :

```bash
docker compose exec genorun-app conda run -n genorun-validation python -m alembic upgrade head
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

## CLI Typer phase 0

Le CLI est disponible dans le conteneur applicatif sous la commande
`genorun-validation`. Il sert à tester le flux job/worker dry-run sans passer
par le navigateur.

Afficher les commandes :

```bash
docker compose exec genorun-app conda run -n genorun-validation genorun-validation --help
docker compose exec genorun-app conda run -n genorun-validation genorun-validation jobs --help
```

Créer un job avec les paramètres phase 0 validés :

```bash
docker compose exec genorun-app conda run -n genorun-validation genorun-validation jobs create
```

Lister les jobs :

```bash
docker compose exec genorun-app conda run -n genorun-validation genorun-validation jobs list --limit 5
```

Exécuter manuellement un job précis :

```bash
docker compose exec genorun-app conda run -n genorun-validation genorun-validation jobs worker <job_id>
```

Paramètres autorisés en phase 0 :

```text
dataset   1000G_chr22
profile   profil_C
strategy  geo_ancestrale_decouverte ou geo_ancestrale
```

## Règle importante

Ne jamais copier de vraies données génétiques dans l'image Docker. Les données sont montées en volumes et doivent rester hors Git.

## Vérifications utiles

```bash
docker compose ps
docker compose logs -f genorun-app
docker compose logs -f genorun-worker
docker compose exec genorun-app conda run -n genorun-validation python -c "import genorun_validation; print(genorun_validation.__version__)"
docker compose exec -T genorun-app conda run --no-capture-output -n genorun-validation pytest -q
```

La commande d'import ci-dessus vérifie que le package `src/genorun_validation` a bien été installé en mode éditable dans l'image Docker.

## Diagnostic rapide

| Symptôme | Vérification | Correction probable |
|---|---|---|
| `http://localhost:8000` ne répond pas | `docker compose ps` puis `docker compose logs -f genorun-app` | Redémarrer `docker compose up -d` et vérifier que `genorun-app` est `Up`. |
| DBeaver affiche `role "genorun" does not exist` | `docker compose port genorun-db 5432` | DBeaver pointe probablement vers PostgreSQL Homebrew sur `5432`; utiliser `localhost:55432`. |
| `localhost:55432` refuse la connexion | `sed -n '1,30p' .env` | Vérifier que `.env` contient `POSTGRES_PORT=55432`, puis relancer `docker compose down && docker compose up -d`. |
| `WORKER_QUEUE_WAIT` apparaît au démarrage | `docker compose logs -f genorun-worker` | Message temporaire pendant les migrations ; il ne doit pas faire quitter le conteneur. |
