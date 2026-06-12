# DEV_TRACKING — Suivi de conception, erreurs et dette technique

Projet : **Génome Réunion — Validation Pipeline**  
Rôle : conserver la mémoire de conception entre les sessions IA/Codex et les reprises par développeur.

Ce fichier est volontairement vivant. Il doit être mis à jour lorsqu'une décision, une erreur connue, une dette technique ou une prochaine étape structurante apparaît.

---

## 1. Mode d'emploi

Statuts recommandés :

- `TODO` : à faire ;
- `IN_PROGRESS` : en cours ;
- `BLOCKED` : bloqué par une décision, un accès ou une donnée ;
- `REVIEW` : fait mais à relire/tester ;
- `DONE` : terminé et vérifié ;
- `DEFERRED` : reporté volontairement.

Règles :

- Chaque `TODO[DEV_TRACKING]` ou `FIXME[DEV_TRACKING]` dans le code doit avoir une ligne ici.
- Chaque correction importante doit indiquer le fichier touché et le test associé.
- Chaque décision d'architecture doit être datée.
- Ne pas effacer les décisions anciennes : les déplacer dans l'historique si nécessaire.

---

## 2. Décisions d'architecture validées

| Date | Décision | Justification | Impact |
|---|---|---|---|
| 2026-06-12 | L'interface déclenche des jobs mais n'exécute pas directement les commandes bioinformatiques | Évite le blocage de Streamlit, améliore la sécurité, les logs et la reprise d'erreur | Architecture Interface → JobManager → Worker → Logs/Résultats |
| 2026-06-12 | Le MVP utilise un worker local dry-run | Valider le flux d'exécution avant d'exécuter PLINK/KING/ADMIXTURE sur données réelles | Les sorties actuelles ne doivent pas être interprétées scientifiquement |
| 2026-06-12 | Toute commande externe doit passer par `external/command_runner.py` ou un wrapper contrôlé | Empêche les commandes shell libres et impose `shell=False` | Tous les outils bioinfo doivent être intégrés via wrappers |
| 2026-06-12 | `AGENTS.md` est le fichier d'autorité pour Codex/IA/développeurs | Empêche les dérives de style, d'architecture et de sécurité | À lire avant toute modification |
| 2026-06-12 | `docs/CODE_INDEX.md` devient la carte de localisation du code | Facilite la reprise multi-session et le debug | À mettre à jour si la structure change |
| 2026-06-12 | `docs/DEV_TRACKING.md` devient le journal de conception et d'erreurs | Conserve la mémoire des décisions et de la dette technique | À mettre à jour à chaque session significative |

---

## 3. Problèmes connus ouverts

| ID | Statut | Priorité | Sujet | Fichiers concernés | Critère de résolution |
|---|---|---:|---|---|---|
| ISSUE-001 | TODO | Haute | Le worker est encore en dry-run | `src/genorun_validation/jobs/worker.py`, `external/`, `core/` | Brancher au moins une vraie étape contrôlée, avec logs et test d'échec |
| ISSUE-002 | TODO | Haute | Les wrappers PLINK/KING/ADMIXTURE sont encore des placeholders | `src/genorun_validation/external/*.py` | Créer des fonctions dédiées par outil, testées sans données réelles lourdes |
| ISSUE-003 | TODO | Haute | Les modules scientifiques `core/` contiennent encore des fonctions minimales | `src/genorun_validation/core/*.py` | Implémenter progressivement QC, PCA, ADMIXTURE, S_div, sélection avec tests |
| ISSUE-004 | TODO | Moyenne | Les vues web hors lancement sont encore des stubs | `web/templates/*.html`, `web/static/` | Ajouter affichage cohérent des données, résultats, comparaison et rapports |
| ISSUE-005 | TODO | Moyenne | Les rapports HTML/PDF/Markdown ne sont pas encore finalisés | `src/genorun_validation/reporting/` | Générer un rapport reproductible depuis un run |
| ISSUE-006 | TODO | Haute | Validation stricte des fichiers d'entrée à renforcer | `storage/`, `utils/validators.py`, `jobs/manager.py` | Refuser les chemins dangereux, formats inattendus et fichiers absents |
| ISSUE-007 | TODO | Moyenne | La base SQL n'est pas encore connectée au flux de jobs | `database/`, `jobs/` | Synchroniser métadonnées SQL et fichiers de run sans stocker les données brutes |
| ISSUE-008 | TODO | Moyenne | Pas encore de page dédiée au suivi détaillé des logs | `web/routes.py`, `web/templates/run_detail.html`, `web/static/js/app.js` | Ajouter filtre par étape, stdout/stderr et statut |
| ISSUE-009 | TODO | Haute | Les règles de sélection V3.5 doivent être transformées en tests d'acceptation | `core/selection.py`, `core/sdiv.py`, `tests/` | Tests quotas, bras découverte, contraintes IBD, poids S_div |

---

## 4. Dette technique acceptée temporairement

| ID | Dette | Pourquoi acceptée maintenant | Plan de correction |
|---|---|---|---|
| DEBT-001 | Worker dry-run | Permet de valider architecture et interface avant intégration bioinfo réelle | Remplacer étape par étape par des appels contrôlés aux wrappers |
| DEBT-002 | Vues web minimalistes | Priorité actuelle à l'architecture et à la sécurité | Construire progressivement chaque page avec composants réutilisables |
| DEBT-003 | Fichiers `core/` très courts | Scaffold initial destiné à poser la structure | Implémenter avec tests unitaires au fur et à mesure |
| DEBT-004 | Certains scripts sont encore démonstratifs | Utile pour tester la mécanique job/worker | Stabiliser CLI et scripts d'administration après premiers vrais modules |

---

## 5. Prochaines étapes recommandées

### Phase A — Durcir le socle job/worker

| Statut | Tâche | Fichiers | Tests attendus |
|---|---|---|---|
| TODO | Ajouter validation stricte de `dataset`, `profile`, `strategy` | `jobs/manager.py`, `config/*.yaml` | `tests/test_jobs.py` |
| TODO | Ajouter manifest détaillé par étape | `jobs/worker.py`, `jobs/manager.py` | Vérifier présence paramètres, timestamps, fichiers |
| TODO | Distinguer clairement logs pipeline, stdout outil et stderr outil | `jobs/worker.py`, `external/command_runner.py` | Test retour erreur outil |
| TODO | Ajouter option d'annulation ou verrouillage anti-double lancement | `jobs/manager.py`, `worker.py` | Test job déjà running |

### Phase B — Brancher les premières vraies étapes bioinfo

| Statut | Tâche | Fichiers | Tests attendus |
|---|---|---|---|
| TODO | Wrapper PLINK QC | `external/plink.py`, `core/qc.py` | Génération commande, refus paramètres invalides |
| TODO | Wrapper PLINK LD pruning | `external/plink.py`, `core/ld_pruning.py` | Génération commande contrôlée |
| TODO | Parser PCA/exports | `core/pca.py`, `parsers/` | Lecture fichier démo minimal |
| TODO | Parser KING | `core/kinship.py`, `parsers/king_parser.py` | Détection apparentés sur fixture minimale |

### Phase C — Implémenter la sélection WGS

| Statut | Tâche | Fichiers | Tests attendus |
|---|---|---|---|
| TODO | Quotas géographiques exacts somme = 350 | `core/selection.py` | Tests arrondis et secteurs minoritaires |
| TODO | Score S_div pondéré | `core/sdiv.py` | Tests poids, normalisation, erreurs |
| TODO | Contrainte IBD dure | `core/selection.py`, `core/kinship.py` | Tests exclusion apparentés |
| TODO | Bras découverte contrôlé | `core/selection.py` | Tests scénarios 5/8/10 % |
| TODO | Export justification individuelle | `core/selection.py`, `reporting/` | Chaque individu sélectionné a une raison traçable |

### Phase D — Interface et rapports

| Statut | Tâche | Fichiers | Tests attendus |
|---|---|---|---|
| TODO | Page résultats avec tables et graphiques (template + SVG serveur) | `web/templates/`, `web/routes.py` | Smoke test des vues web (client de test Flask) |
| TODO | Page comparaison stratégies | `web/templates/`, `web/routes.py` | Fixtures métriques |
| TODO | Rapport HTML scientifique | `reporting/html_report.py`, templates | Test génération fichier |
| TODO | Export Markdown/PDF | `reporting/markdown_report.py`, `reporting/pdf_report.py` | Test existence et contenu minimal |

---

## 6. Erreurs corrigées

| Date | ID | Problème | Fichiers | Correction | Test associé |
|---|---|---|---|---|---|
| 2026-06-12 | FIX-001 | Risque de confusion : “l'interface ne lance pas les analyses” | `AGENTS.md`, `docs/09_architecture_jobs_interface_worker.md`, `web/routes.py` | Clarification : l'interface déclenche un job, le worker exécute | `tests/test_jobs.py` |
| 2026-06-12 | FIX-002 | Manque de règles de style/code pour Codex | `AGENTS.md` | Ajout règles variables, commentaires, docstrings, erreurs, tests | Documentation uniquement |
| 2026-06-12 | FIX-003 | Absence de carte de localisation du code | `docs/CODE_INDEX.md` | Création de l'index du code | Documentation uniquement |
| 2026-06-12 | FIX-004 | Absence de suivi multi-session des décisions et erreurs | `docs/DEV_TRACKING.md` | Création du journal de conception et d'erreurs | Documentation uniquement |

---

## 7. Journal de session

### 2026-06-12 — Mise en place des règles de maintenabilité

Modifications réalisées :

- ajout de règles détaillées dans `AGENTS.md` : nommage, variables, commentaires localisables, docstrings, erreurs, tests ;
- création de `docs/CODE_INDEX.md` pour localiser rapidement les modules, fonctions et zones d'erreur ;
- création de `docs/DEV_TRACKING.md` pour suivre les décisions, erreurs connues, dette technique et prochaines étapes ;
- mise à jour du rappel court `.codex/rules.md`.

Points à surveiller à la prochaine session :

- ne pas commencer par coder PLINK directement dans une vue web ;
- brancher les vraies commandes progressivement via wrappers ;
- transformer la méthodologie V3.5 en tests d'acceptation.

---

## 8. Notes pour l'IA lors d'une reprise

Lors d'une nouvelle session, commencer par répondre à ces questions avant de modifier :

1. Quelle tâche précise est demandée ?
2. Quel module est concerné selon `CODE_INDEX.md` ?
3. Existe-t-il une dette ou un problème ouvert dans ce fichier ?
4. Quels tests doivent être lancés ou créés ?
5. Faut-il mettre à jour `CODE_INDEX.md` ou `DEV_TRACKING.md` après modification ?

Ne jamais supposer que la mémoire de conversation suffit : les décisions durables doivent être inscrites ici.

---

## Session v5 — PostgreSQL et Docker dès le départ

### Décisions validées

- PostgreSQL devient la base officielle du logiciel.
- SQLite n'est plus l'architecture cible ; il peut seulement servir ponctuellement aux tests unitaires isolés.
- Docker est prévu dès le départ comme couche de reproductibilité et de déploiement.
- Le mode local simple reste possible pour apprendre et développer sans blocage.
- L'interface peut lancer les analyses, mais en mode Docker elle met les jobs en file pour un worker externe.
- Les fichiers génétiques lourds restent hors base et hors Git.
- PostgreSQL indexe les métadonnées, statuts, paramètres, scores, audits, rapports et chemins relatifs.

### Fichiers ajoutés ou modifiés

| Fichier | Modification |
|---|---|
| `.env.example` | Variables PostgreSQL, worker et chemins. |
| `.dockerignore` | Exclusion des données lourdes et résultats. |
| `docker-compose.yml` | Ajout `genorun-db`, `genorun-app`, `genorun-worker`. |
| `Dockerfile` | Environnement conda reproductible. |
| `.devcontainer/devcontainer.json` | Préparation VS Code Dev Containers. |
| `src/genorun_validation/settings.py` | Configuration centrale. |
| `src/genorun_validation/database/models.py` | Modèle PostgreSQL initial. |
| `src/genorun_validation/database/repositories.py` | Repository jobs/audit. |
| `src/genorun_validation/jobs/manager.py` | Persistance fichiers + PostgreSQL optionnelle. |
| `scripts/run_worker_loop.py` | Worker en boucle pour Docker/serveur. |
| `docs/DOCKER_GUIDE_BEGINNER.md` | Guide débutant Docker. |
| `docs/POSTGRESQL_GUIDE_BEGINNER.md` | Guide débutant PostgreSQL. |
| `alembic/` | Structure de migrations. |

### Dette technique connue

- Le worker est encore en `dry_run`.
- Le worker loop est volontairement simple ; il pourra être remplacé par Celery/RQ/Nextflow plus tard.
- La migration Alembic initiale utilise la metadata SQLAlchemy pour le scaffold ; les migrations suivantes devront être explicites et relues.
- Les vraies commandes PLINK/KING/ADMIXTURE ne sont pas encore branchées aux tables de résultats.

### À faire ensuite

1. Ajouter un vrai module d'import de fichiers PLINK/VCF avec validation de checksum.
2. Ajouter une page web (Flask + vanilla) de visualisation des jobs depuis PostgreSQL.
3. Ajouter un tableau de bord QC basé sur `qc_metrics`.
4. Brancher les wrappers PLINK/KING/ADMIXTURE dans le worker.
5. Ajouter des tests d'intégration PostgreSQL via Docker quand l'environnement sera disponible.

---

## 8. Session 2026-06-12 (soir) — Durcissement de l'architecture (v5.1)

Objectif de la session : améliorer l'architecture pour un développement **entouré, sécurisé, maintenable**, sans coder les algorithmes scientifiques. Réponse aux réserves et points d'attention de la revue d'architecture.

### Décisions d'architecture ajoutées

| Date | Décision | Justification | Impact |
|---|---|---|---|
| 2026-06-12 | `steps.py` devient la **source unique** de l'ordre du pipeline ; `pipeline.py` n'en dérive que les libellés | Évite deux définitions divergentes de l'ordre des étapes | Toute nouvelle étape s'ajoute dans `PIPELINE` uniquement |
| 2026-06-12 | Figer les **contrats d'interface** (`contracts.py`) avant d'implémenter `core/`/`external/`/`parsers/` | Permet de développer et tester chaque couche en isolation, évite les réécritures en cascade | Les implémentations doivent respecter `CoreStep`/`ExternalToolWrapper`/`OutputParser` |
| 2026-06-12 | Outillage qualité imposé : ruff + mypy (strict ciblé) + pytest-cov + pre-commit + CI | Rend les règles `AGENTS.md §13` vérifiables automatiquement | Une PR rouge ne doit pas être fusionnée |
| 2026-06-12 | `runner.py` marque les étapes non branchées `skipped` plutôt que de planter | Permet une montée en charge progressive du dry-run vers l'exécution réelle | Le worker s'appuiera dessus en Phase 4 |
| 2026-06-12 | `CLAUDE.md` ajouté comme guide opérationnel Claude Code, subordonné à `AGENTS.md` | Même exigence que Codex pour les agents Claude | À lire avant toute session Claude |

### Problèmes traités (réserves de la revue)

| ID | Statut | Sujet | Traitement |
|---|---|---|---|
| ISSUE-010 | REVIEW | `orchestration/` était quasi vide | Squelette réel : `steps`, `status`, `exceptions`, `run_context`, `runner` (dry-run testé) |
| ISSUE-011 | REVIEW | Contrats d'interface absents entre couches | `contracts.py` : protocoles + dataclasses d'IO |
| ISSUE-012 | REVIEW | Outillage qualité minimal (pytest seul) | ruff/mypy/coverage/pre-commit/CI ajoutés |
| ISSUE-006 | REVIEW | Validation d'entrée stricte | `utils/validators.py` (anti-remontée de chemin, allowlist, identifiants, poids) + `tests/test_validators.py` |

### Point d'attention restant à traiter (non bloquant maintenant)

| ID | Statut | Priorité | Sujet | Plan |
|---|---|---:|---|---|
| ISSUE-013 | TODO | Moyenne | Pas de verrou anti-double exécution si plusieurs workers | Introduire un statut `claimed` atomique en base (revendication de job) en Phase 5 ; aujourd'hui mono-worker, risque faible. Lié à DEBT existant Phase A. |

### Vérifications passées cette session

- `python -m compileall src scripts web` : OK.
- Import isolé `contracts` + `orchestration.*` + `utils.validators` (stdlib uniquement) : OK.
- `run_pipeline(dry_run=True)` sur 10 étapes : toutes `skipped`, aucun crash.
- Validateurs : cas normaux et cas d'erreur vérifiés.

> Tests complets (`pytest`, ruff, mypy) à exécuter dans l'environnement conda du projet où les dépendances lourdes sont installées.

---

## 9. Session 2026-06-12 (soir, suite) — Choix de la pile interface

### Décision d'architecture

| Date | Décision | Justification | Impact |
|---|---|---|---|
| 2026-06-12 | L'interface passe de Streamlit à **Flask (fine couche serveur) + front HTML/CSS/JS vanilla** | Préférence projet pour le serveur Python sans framework d'UI : plus lisible, connu de tous, maintenable et corrigeable ; supprime les contraintes d'exécution de Streamlit | Dossier `web/` remplace l’ancienne interface Streamlit `app/` (Flask). Reste de l'architecture inchangé. |
| 2026-06-12 | La base reste gérée par **SQLAlchemy + Alembic** ; Django/ORM Django écartés | Éviter une double source de vérité du modèle de données | Flask lit les données via `services/`/`jobs/`, jamais via un ORM concurrent |
| 2026-06-12 | Graphiques rendus **en SVG côté serveur** (réutilisation du pipeline de reporting) | Cohérent avec le front vanilla ; un seul JS minimal (polling) côté client | Pas de bibliothèque de charting front imposée |

### Ce qui change concrètement

- Dépendances : `streamlit` retiré, `flask` + `gunicorn` ajoutés (`pyproject.toml`, `requirements.txt`).
- Docker : image expose le port 8000 ; commande `gunicorn web.wsgi:app` (au lieu de `streamlit run`).
- Nouvelle couche `web/` : `__init__.py` (factory), `wsgi.py`, `routes.py`, `templates/`, `static/{css,js,img}`.
- Règle centrale inchangée : la route `POST /api/jobs` valide les paramètres puis crée un job `QUEUED` ; le worker exécute ; le front fait du polling sur `GET /api/jobs/<id>/status`.
- Gouvernance mise à jour : `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/ROADMAP.md` (Phase 7), `docs/06_interface_web.md` (renommé), `docs/CODE_INDEX.md`.

### Vérifications

- `python -m compileall src scripts web` : OK.
- Factory Flask : les 4 routes (`/`, `/api/jobs`, `/api/jobs/<id>/status`, `/runs/<id>`) s'enregistrent.
- Aucun appel shell ni logique bioinfo dans `web/`.

### Note historique

La décision initiale (section 2) mentionnait Streamlit. Elle est conservée pour mémoire ; la présente section la supersède pour la couche interface. Le motif « éviter le blocage du processus d'interface » reste valable et est désormais porté par le modèle requête → file → worker → polling.

---

## 10. Session 2026-06-12 (soir, suite) — Guide de choix du modèle Claude

| Date | Décision | Justification | Impact |
|---|---|---|---|
| 2026-06-12 | Ajout d'un guide de sélection du modèle Claude par **palier de complexité** (T1→T4) | Régler le compromis qualité/coût en dev (Claude Code) | `CLAUDE.md` §17 (source unique palier → modèle) + table par phase dans `ROADMAP.md` |
| 2026-06-12 | Les noms de modèles concrets vivent dans `CLAUDE.md` uniquement ; le reste référence des paliers | Les versions changent vite ; éviter de figer les noms partout | Mise à jour localisée quand un nouveau modèle sort |

Recommandation pratique : `opusplan` par défaut (Opus planifie, Sonnet implémente) ; escalade au besoin ; revue des chemins critiques (S_div, sélection, sécurité, migrations) au palier T3 minimum.


---

## Session v5.4 — corrections infrastructure

### Décisions/corrections validées

| Date | Décision/correction | Fichiers principaux | Statut |
|---|---|---|---|
| 2026-06-12 | Remplacement des références actives `app/` par `web/` dans CI, README, règles et index | `.github/workflows/ci.yml`, `pyproject.toml`, `README.md`, `AGENTS.md`, `docs/CODE_INDEX.md` | Fait |
| 2026-06-12 | Docker installe le package en mode éditable pour fiabiliser les imports | `Dockerfile` | Fait |
| 2026-06-12 | Docker Compose utilise des variables d'environnement au lieu de figer les identifiants dans la logique applicative | `docker-compose.yml`, `.env.example` | Fait |
| 2026-06-12 | La migration initiale Alembic devient explicite et auditable table par table | `alembic/versions/0001_initial_schema.py` | Fait |
| 2026-06-12 | Le worker en boucle utilise PostgreSQL comme file officielle quand la base est activée | `JobManager.list_runnable_jobs()`, `JobRepository.list_job_uids_by_status()`, `scripts/run_worker_loop.py` | Fait |

### Vérifications réalisées

```bash
python -m compileall src scripts web
PYTHONPATH=src pytest -q
```

Résultat local sandbox : 26 tests passés. Les tests SQLAlchemy restent conditionnés à la présence de la dépendance dans l'environnement.

### Points restant à tester hors sandbox

- `docker compose up --build` avec un vrai Docker local.
- `alembic upgrade head` sur PostgreSQL réel.
- Création d'un job depuis l'interface Flask puis exécution par `genorun-worker`.
