# CODE_INDEX — Cartographie du code

Projet : **Génome Réunion — Validation Pipeline**  
Rôle : permettre à Codex, ChatGPT ou un développeur de localiser rapidement les fichiers, fonctions et zones d'erreur.

Ce fichier doit être mis à jour à chaque création, déplacement, renommage ou suppression d'un module important.

---

## 1. Lecture rapide avant intervention

À lire dans cet ordre avant toute modification :

1. `AGENTS.md` — règles obligatoires de développement et de sécurité.
2. `docs/DEV_TRACKING.md` — décisions, problèmes ouverts et prochaines étapes.
3. Le fichier concerné par la modification.
4. Les tests associés dans `tests/`.

---

## 2. Carte générale des dossiers

| Chemin | Rôle | À modifier quand |
|---|---|---|
| `web/` | Interface web Flask | Routes, templates, statics (front vanilla), endpoints JSON de statut |
| `web/routes.py` | Routes Flask + endpoints JSON | Ajout/modif d'une route ou d'un endpoint de statut |
| `web/templates/`, `web/static/` | Templates HTML + front vanilla (CSS/JS) | Modification UX, polling, styles |
| `src/genorun_validation/core/` | Algorithmes purs et testables | QC, PCA, ADMIXTURE, S_div, sélection, imputation |
| `src/genorun_validation/external/` | Wrappers sécurisés des outils externes | PLINK, KING, ADMIXTURE, bcftools, SHAPEIT4, BEAGLE |
| `src/genorun_validation/jobs/` | Création, suivi et exécution des jobs locaux | Statuts, manifests, worker, reprise d'erreur |
| `src/genorun_validation/orchestration/` | Ordre logique du pipeline | Enchaînement des étapes et contexte de run |
| `src/genorun_validation/database/` | Modèles SQL et sessions | Métadonnées, runs, fichiers, rapports, métriques |
| `src/genorun_validation/services/` | Logique applicative entre interface, core, jobs et base | Cas d'usage métier transversaux |
| `src/genorun_validation/storage/` | Gestion des chemins, checksums et registres fichiers | Sécurité fichiers et traçabilité |
| `src/genorun_validation/parsers/` | Lecture des sorties d'outils externes | Parsers PLINK/KING/ADMIXTURE/ROH/imputation |
| `src/genorun_validation/reporting/` | Génération de rapports | HTML, PDF, Markdown, templates |
| `src/genorun_validation/utils/` | Fonctions génériques | Configuration, logs, validation, constantes |
| `scripts/` | Commandes d'administration et worker CLI | Lancement manuel, init DB, démo, export |
| `config/` | Paramètres scientifiques et techniques | Seuils, chemins, outils, stratégies |
| `docs/` | Documentation vivante | Architecture, sécurité, méthode, suivi |
| `tests/` | Tests unitaires et intégration | Toute logique testable |
| `work/runs/` | Dossiers de jobs locaux | Généré à l'exécution, ne pas versionner les résultats réels |
| `data/` | Données locales contrôlées | Ne jamais y ajouter de données génétiques réelles dans Git |
| `results/` | Sorties consolidées | Tables, figures, métriques, sélections |
| `reports/` | Rapports exportés | HTML/PDF/Markdown |
| `logs/` | Logs applicatifs et outils | Debug et audit |

---

## 3. Points d'entrée principaux

| Fichier | Fonction / classe | Rôle |
|---|---|---|
| `web/wsgi.py` | point d'entrée WSGI | Cible gunicorn : `gunicorn web.wsgi:app` |
| `web/routes.py` | routes Flask | Crée un job (POST), met en file, expose le statut JSON pour le polling |
| `src/genorun_validation/cli.py` | `app`, `jobs_app` | CLI Typer principale |
| `src/genorun_validation/cli.py` | `create_job()` | Crée un job local depuis la CLI |
| `src/genorun_validation/cli.py` | `run_worker()` | Exécute un job local depuis la CLI |
| `scripts/create_demo_job.py` | `main()` | Crée un job de démonstration |
| `scripts/run_worker.py` | `main()` | Lance le worker local pour un `job_id` |

---

## 4. Gestion des jobs

| Fichier | Élément | Rôle |
|---|---|---|
| `src/genorun_validation/jobs/schemas.py` | `JobStatus` | Enum des statuts : created, queued, running, completed, failed, cancelled |
| `src/genorun_validation/jobs/schemas.py` | `PipelineJob` | Dataclass centrale d'un job local |
| `src/genorun_validation/jobs/schemas.py` | `PipelineJob.to_dict()` | Sérialisation JSON du job |
| `src/genorun_validation/jobs/schemas.py` | `PipelineJob.from_dict()` | Reconstruction depuis `status.json` |
| `src/genorun_validation/jobs/schemas.py` | `utc_now_iso()` | Horodatage UTC ISO-8601 |
| `src/genorun_validation/jobs/manager.py` | `DEFAULT_STEPS` | Liste ordonnée des étapes du MVP |
| `src/genorun_validation/jobs/manager.py` | `JobManager` | Création, sauvegarde, lecture et liste des jobs |
| `src/genorun_validation/jobs/manager.py` | `JobManager.create_job()` | Crée `run_dir`, `config.yaml`, `manifest.json`, `status.json` |
| `src/genorun_validation/jobs/manager.py` | `JobManager.get_job()` | Charge un job existant |
| `src/genorun_validation/jobs/manager.py` | `JobManager.save_job()` | Sauvegarde atomique de `status.json` |
| `src/genorun_validation/jobs/manager.py` | `JobManager.update_status()` | Change le statut principal |
| `src/genorun_validation/jobs/manager.py` | `JobManager.update_step()` | Change le statut d'une étape |
| `src/genorun_validation/jobs/manager.py` | `JobManager.list_jobs()` | Liste les jobs récents |
| `src/genorun_validation/jobs/manager.py` | `JobManager.tail_log()` | Lit les dernières lignes du log |
| `src/genorun_validation/jobs/manager.py` | `find_project_root()` | Localise la racine du projet |
| `src/genorun_validation/jobs/manager.py` | `get_default_job_manager()` | Factory utilisée par l'interface et les scripts |
| `src/genorun_validation/jobs/worker.py` | `LocalPipelineWorker` | Worker local sécurisé |
| `src/genorun_validation/jobs/worker.py` | `LocalPipelineWorker.run()` | Exécute les étapes d'un job |

---

## 5. Exécution d'outils externes

| Fichier | Élément | Rôle |
|---|---|---|
| `src/genorun_validation/external/command_runner.py` | `ALLOWED_EXECUTABLES` | Liste blanche des exécutables autorisés |
| `src/genorun_validation/external/command_runner.py` | `CommandResult` | Résultat normalisé d'une commande |
| `src/genorun_validation/external/command_runner.py` | `run_command()` | Exécute une commande avec `shell=False`, stdout/stderr et validation |
| `src/genorun_validation/external/plink.py` | `run_command()` placeholder | Futur wrapper PLINK |
| `src/genorun_validation/external/plink2.py` | `run_command()` placeholder | Futur wrapper PLINK2 |
| `src/genorun_validation/external/king.py` | `run_command()` placeholder | Futur wrapper KING |
| `src/genorun_validation/external/admixture_tool.py` | `run_command()` placeholder | Futur wrapper ADMIXTURE |
| `src/genorun_validation/external/bcftools.py` | `run_command()` placeholder | Futur wrapper bcftools |
| `src/genorun_validation/external/beagle.py` | `run_command()` placeholder | Futur wrapper BEAGLE |
| `src/genorun_validation/external/shapeit4.py` | `run_command()` placeholder | Futur wrapper SHAPEIT4 |

Règle : toute vraie commande PLINK/KING/ADMIXTURE doit passer par un wrapper dans `external/`, jamais directement depuis `web/`.

---

## 6. Modules scientifiques à compléter

Les fichiers suivants existent comme points d'ancrage. Ils sont encore minimalistes dans le scaffold et devront être progressivement remplacés par des fonctions testées.

| Fichier | Rôle attendu |
|---|---|
| `src/genorun_validation/core/qc.py` | QC SNP : taux manquants, MAF, HWE, sexe, duplication |
| `src/genorun_validation/core/ld_pruning.py` | Pruning LD pour PCA/ADMIXTURE |
| `src/genorun_validation/core/pca.py` | PCA globale, projections, exports coordonnées |
| `src/genorun_validation/core/admixture.py` | Lancement/lecture ADMIXTURE, CV-error, K optimal |
| `src/genorun_validation/core/kinship.py` | KING/IBD, exclusion apparentés, score indépendance |
| `src/genorun_validation/core/roh.py` | ROH, longueurs cumulées, scores fondateurs |
| `src/genorun_validation/core/sdiv.py` | Calcul S_div, normalisation locale, pondération |
| `src/genorun_validation/core/selection.py` | Sélection WGS, quotas, maximin, bras découverte |
| `src/genorun_validation/core/imputation.py` | Simulation ou vraie étape d'imputation |
| `src/genorun_validation/core/evaluation.py` | Comparaison de stratégies et métriques de validation |
| `src/genorun_validation/core/simulation_profiles.py` | Profils A/C/D de validation méthodologique |

---

## 7. Interface web (Flask + vanilla)

| Fichier | Rôle |
|---|---|
| `web/__init__.py` | Factory Flask `create_app()` |
| `web/wsgi.py` | Point d'entrée gunicorn |
| `web/routes.py` | Tableau de bord, création de job (POST), statut JSON, détail de run |
| `web/templates/dashboard.html` | Tableau de bord + lancement (vanilla) |
| `web/templates/run_detail.html` | Détail d'un run : étapes, logs |
| `web/static/js/app.js` | Soumission + polling du statut (vanilla) |
| `web/static/css/app.css` | Styles (palette teal/navy/coral) |
| (à venir) | Graphiques PCA/ADMIXTURE/ROH rendus en SVG côté serveur |

---

## 8. Localiser une erreur par symptôme

| Symptôme | Fichiers à inspecter en priorité |
|---|---|
| Le bouton « Lancer l'analyse » ne crée pas de job | `web/routes.py` (`POST /api/jobs`), `web/static/js/app.js`, `src/genorun_validation/jobs/manager.py` |
| Le job est créé mais n'avance pas | `scripts/run_worker.py`, `src/genorun_validation/jobs/worker.py`, `work/runs/<run_id>/status.json` |
| Statut incohérent ou non sauvegardé | `src/genorun_validation/jobs/schemas.py`, `src/genorun_validation/jobs/manager.py` |
| Les logs ne s'affichent pas | `JobManager.tail_log()`, `web/routes.py` (`run_detail`), `work/runs/<run_id>/logs/pipeline.log` |
| Une commande externe est refusée | `src/genorun_validation/external/command_runner.py`, `ALLOWED_EXECUTABLES` |
| Une commande externe échoue | `stderr` du run, wrapper dans `src/genorun_validation/external/`, manifest du run |
| Un chemin est introuvable | `config/paths.yaml`, `JobManager`, `storage/`, racine projet |
| Les résultats ne sont pas trouvés | `work/runs/<run_id>/outputs/`, `results/`, parser concerné |
| Erreur sur QC | `core/qc.py`, `external/plink.py`, parser QC, tests QC |
| Erreur PCA | `core/pca.py`, `core/ld_pruning.py`, wrappers PLINK/Python PCA |
| Erreur ADMIXTURE | `core/admixture.py`, `external/admixture_tool.py`, parser ADMIXTURE |
| Erreur KING/IBD | `core/kinship.py`, `external/king.py`, parser KING |
| Erreur ROH | `core/roh.py`, `external/plink.py`, parser ROH |
| Erreur S_div ou quotas | `core/sdiv.py`, `core/selection.py`, `config/strategies.yaml` |
| Erreur rapport | `reporting/`, `reports/`, templates HTML/Markdown/PDF |
| Erreur base SQL | `database/models.py`, `database/session.py`, `database/init_db.py` |
| Tests qui échouent après changement de jobs | `tests/test_jobs.py`, `tests/test_command_runner.py` |

---

## 9. Fichiers de configuration importants

| Fichier | Rôle |
|---|---|
| `config/database.yaml` | Configuration base de données |
| `config/tools.yaml` | Chemins/paramètres des outils externes |
| `config/paths.yaml` | Racines de stockage et dossiers de travail |
| `config/validation.yaml` | Paramètres de validation méthodologique |
| `config/demo_chr22.yaml` | Configuration de démonstration chr22 |
| `config/profiles.yaml` | Profils de population simulés |
| `config/strategies.yaml` | Stratégies de sélection et poids |

---

## 10. Tests existants

| Fichier | Cible |
|---|---|
| `tests/test_command_runner.py` | Sécurité d'exécution externe |
| `tests/test_jobs.py` | Création, sauvegarde et worker de jobs |
| `tests/test_config.py` | Chargement configuration |
| `tests/test_database.py` | Modèles/session DB |
| `tests/test_pipeline_runner.py` | Runner/orchestration |
| `tests/test_pca.py` | Module PCA |
| `tests/test_qc.py` | Module QC |
| `tests/test_report.py` | Génération rapport |
| `tests/test_sdiv.py` | Calcul S_div |
| `tests/test_selection.py` | Sélection WGS |
| `tests/test_storage.py` | Stockage et chemins |

Commandes à lancer avant livraison :

```bash
python -m compileall src scripts web
pytest -q
```

---

## 11. Contrats à ne pas casser

- L'interface crée des jobs ; elle ne lance pas de shell libre.
- `work/runs/<run_id>/config.yaml`, `manifest.json`, `status.json`, `logs/`, `outputs/`, `report/` doivent rester la structure de base d'un run.
- Les commandes externes doivent utiliser `shell=False`.
- Les données génétiques réelles ne doivent jamais être ajoutées au dépôt.
- Les résultats simulés doivent rester clairement identifiés comme simulés ou dry-run.
- Toute évolution de structure doit être reportée dans ce fichier.

---

## Mise à jour v5 — PostgreSQL, Docker et worker externe

### Configuration centrale

| Besoin | Fichier | Rôle |
|---|---|---|
| Lire les variables d'environnement | `src/genorun_validation/settings.py` | Centralise `GENORUN_DATABASE_URL`, `GENORUN_ENABLE_DATABASE`, chemins racine, mode worker. |
| Exemple d'environnement | `.env.example` | Configuration type Docker/PostgreSQL. |

### Base de données PostgreSQL

| Besoin | Fichier | Rôle |
|---|---|---|
| Base SQLAlchemy | `src/genorun_validation/database/base.py` | Déclare `Base`. |
| Modèles | `src/genorun_validation/database/models.py` | Tables projets, cohortes, samples, fichiers, jobs, étapes, logs, audits, scores, rapports. |
| Sessions | `src/genorun_validation/database/session.py` | Crée engine/session depuis `GENORUN_DATABASE_URL`. |
| Repositories | `src/genorun_validation/database/repositories.py` | Isole l'accès SQL pour les jobs, l'audit et la file PostgreSQL. |
| Initialisation rapide | `scripts/init_database.py` | Crée les tables pour le scaffold. |
| Migrations | `alembic/` | Migrations versionnées. |

### Jobs et workers

| Besoin | Fichier | Rôle |
|---|---|---|
| Créer un job | `src/genorun_validation/jobs/manager.py` | Écrit config/manifest/statut + indexe en base si activée. |
| Exécuter un job unique | `scripts/run_worker.py` | Lance un job précis. |
| Exécuter en boucle | `scripts/run_worker_loop.py` | Worker Docker/serveur qui lit les jobs runnable via `JobManager.list_runnable_jobs()`. |
| Interface lancement | `web/routes.py` (`POST /api/jobs`) | Crée un job et le met en file (worker externe). |

### Docker

| Besoin | Fichier | Rôle |
|---|---|---|
| Image applicative | `Dockerfile` | Environnement conda + outils bioinfo. |
| Services | `docker-compose.yml` | `genorun-app`, `genorun-worker`, `genorun-db`. |
| Exclusions build | `.dockerignore` | Exclut données génétiques, runs, logs et résultats. |
| Dev Container | `.devcontainer/devcontainer.json` | Ouverture future dans VS Code Dev Containers. |

### Guides

| Besoin | Fichier |
|---|---|
| Débuter avec Docker | `docs/DOCKER_GUIDE_BEGINNER.md` |
| Débuter avec PostgreSQL | `docs/POSTGRESQL_GUIDE_BEGINNER.md` |
| Structure base | `docs/05_structure_base_donnees.md` |

### Localiser une erreur

| Symptôme | Fichiers à inspecter |
|---|---|
| PostgreSQL non joignable | `.env.example`, `docker-compose.yml`, `src/genorun_validation/database/session.py` |
| Job créé mais non exécuté | `scripts/run_worker_loop.py`, `work/runs/<job_id>/status.json`, `docker compose logs genorun-worker` |
| Job non visible dans la base | `GENORUN_ENABLE_DATABASE`, `src/genorun_validation/jobs/manager.py`, `src/genorun_validation/database/repositories.py` |
| Problème de migration | `alembic/env.py`, `alembic/versions/`, `src/genorun_validation/database/models.py` |
| Chemin absolu persistant | `src/genorun_validation/database/repositories.py`, `src/genorun_validation/settings.py` |

---

## Ajouts durcissement architecture (v5.1)

### Qualité, CI et règles agents

| Besoin | Fichier | Rôle |
|---|---|---|
| Règles agent Claude Code | `CLAUDE.md` | Guide opérationnel Claude (défère à `AGENTS.md` pour l'autorité). |
| Feuille de route | `docs/ROADMAP.md` | Phases 0→9 avec portes de test ("étape à tester avant la suivante"). |
| Graphe de la roadmap | `docs/ROADMAP_graph.svg` | Visualisation autonome du chemin socle → déploiement. |
| Lint & format | `pyproject.toml` `[tool.ruff]` | Règles ruff (E,F,I,UP,B,SIM,PTH). |
| Typage | `pyproject.toml` `[tool.mypy]` | Strict sur `core/` et `contracts`, permissif ailleurs. |
| Couverture | `pyproject.toml` `[tool.coverage]` | Mesure de couverture (seuil relevé phase par phase). |
| Hooks pré-commit | `.pre-commit-config.yaml` | ruff, anti-gros-fichiers, détection de clé privée. |
| Intégration continue | `.github/workflows/ci.yml` | compileall + ruff + pytest sur chaque PR. |

### Orchestration et contrats

| Besoin | Fichier | Rôle |
|---|---|---|
| Frontières typées | `src/genorun_validation/contracts.py` | Protocoles + dataclasses d'IO entre `core`/`external`/`parsers`. |
| Ordre des étapes | `src/genorun_validation/orchestration/steps.py` | Source unique de l'ordre du pipeline (`PIPELINE`). |
| Statuts d'étape | `src/genorun_validation/orchestration/status.py` | `StepStatus` + transitions autorisées. |
| Exceptions | `src/genorun_validation/orchestration/exceptions.py` | Hiérarchie d'erreurs typées du pipeline. |
| Contexte de run | `src/genorun_validation/orchestration/run_context.py` | Chemins canoniques figés d'un run. |
| Runner | `src/genorun_validation/orchestration/runner.py` | Enchaînement des étapes (dry-run, arrêt sur échec bloquant). |
| Compat libellés | `src/genorun_validation/orchestration/pipeline.py` | `PIPELINE_STEPS` dérivé de `steps.PIPELINE`. |

### Sécurité / validation

| Besoin | Fichier | Rôle |
|---|---|---|
| Validation entrées | `src/genorun_validation/utils/validators.py` | Identifiants sûrs, anti-remontée de chemin, allowlist d'extensions, poids normalisés. |
| Tests validation | `tests/test_validators.py` | Cas normaux + cas d'erreur des validateurs. |

### Interface web (Flask + front vanilla)

| Besoin | Fichier | Rôle |
|---|---|---|
| Factory Flask | `web/__init__.py` | `create_app()` : configure l'app, enregistre le blueprint. |
| Point d'entrée WSGI | `web/wsgi.py` | Cible gunicorn : `gunicorn web.wsgi:app`. |
| Routes | `web/routes.py` | `/`, `POST /api/jobs`, `GET /api/jobs/<id>/status`, `/runs/<id>`. |
| Templates | `web/templates/` | `base.html`, `dashboard.html`, `run_detail.html` (HTML vanilla). |
| Styles | `web/static/css/app.css` | CSS vanilla, palette teal/navy/coral. |
| Front | `web/static/js/app.js` | JS vanilla : soumission + polling du statut. |


---

## Mise à jour v5.4 — corrections infrastructure

| Zone | Fichiers | Décision |
|---|---|---|
| Interface web | `web/` | Toutes les références actives à l'ancien dossier `app/` ont été remplacées par `web/`. |
| Docker | `Dockerfile` | Ajout de `pip install -e .` et de `PYTHONPATH=/app/src` pour garantir les imports du package dans le conteneur. |
| Docker Compose | `docker-compose.yml`, `.env.example` | Les identifiants de développement passent par variables d'environnement ; les vrais secrets ne doivent jamais être versionnés. |
| Migrations | `alembic/versions/0001_initial_schema.py` | Migration initiale rendue explicite table par table, au lieu de `Base.metadata.create_all()`. |
| Worker | `src/genorun_validation/jobs/manager.py`, `database/repositories.py`, `scripts/run_worker_loop.py` | PostgreSQL devient la file officielle quand la base est activée ; filesystem reste fallback local. |

### Localiser une erreur v5.4

| Symptôme | Inspecter |
|---|---|
| Docker démarre mais `genorun_validation` est introuvable | `Dockerfile`, commande `pip install -e .`, `PYTHONPATH=/app/src` |
| Le worker ne prend pas les jobs en Docker | `scripts/run_worker_loop.py`, `JobManager.list_runnable_jobs()`, table `analysis_jobs` |
| Alembic échoue au démarrage | `alembic/versions/0001_initial_schema.py`, `src/genorun_validation/database/models.py` |
| Les tests/lint cherchent encore `app/` | `.github/workflows/ci.yml`, `pyproject.toml`, `README.md`, `AGENTS.md` |
