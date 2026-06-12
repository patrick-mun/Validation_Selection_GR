# ROADMAP — Génome Réunion Validation Pipeline

Feuille de route du **point de départ** (scaffold : infrastructure réelle, cœur scientifique en stubs) jusqu'au **déploiement**.

Principe : on remplit les couches **du socle vers le sommet**. Entre chaque phase et chaque sous-étape, une **porte de test** ferme le passage. Règle d'or répétée à chaque porte :

> **« Étape à tester avant la suivante. »** On ne franchit pas une porte tant que ses tests ne sont pas verts, documentés et reproductibles.

Vérification minimale à chaque porte (en plus des tests spécifiques) :

```bash
python -m compileall src scripts web
pytest -q
```

Statuts (voir `docs/DEV_TRACKING.md`) : `TODO` `IN_PROGRESS` `BLOCKED` `REVIEW` `DONE` `DEFERRED`.

---

## Vue d'ensemble

```text
Phase 0  Socle & durcissement        ─┐
Phase 1  Wrappers outils externes     │  Construction du moteur bioinfo
Phase 2  Parsers de sorties           │
Phase 3  Cœur scientifique           ─┘
Phase 4  Orchestration & worker réel ─┐  Intégration & exécution
Phase 5  Persistance SQL ↔ jobs      ─┘
Phase 6  Reporting                   ─┐
Phase 7  Interface web          │  Livraison
Phase 8  Recette V3.5 end-to-end      │
Phase 9  Déploiement                 ─┘
```

Chaque flèche du graphe = une porte de test. **Étape à tester avant la suivante.**

---

## Modèle Claude conseillé par phase

Heuristique de départ par palier (correspondance palier → modèle concret dans `CLAUDE.md` §17). À ajuster par tâche : monter d'un cran si la difficulté l'exige, et revoir les chemins critiques au palier T3 minimum.

| Phase | Palier par défaut | Pourquoi |
|---|---|---|
| 0 Socle & durcissement | T2, sauf contrats (0.4) en **T3** | Outillage/CI/fixtures standards ; les contrats engagent toute l'archi |
| 1 Wrappers externes | T2, 1er wrapper de référence en **T3** | Modèle à concevoir une fois, puis répliquer ; trivial → T1 |
| 2 Parsers | T2, format fixe simple → **T1** | Lecture structurée routinière |
| 3 Cœur scientifique | **T3** (T4 pour sélection + sensibilité de bout en bout) | Correction scientifique critique |
| 4 Orchestration & worker | T2, conception échec/concurrence en **T3** | Câblage standard, design d'état délicat |
| 5 Persistance SQL ↔ jobs | T2, schéma & migrations en **T3** | CRUD standard, design de schéma sensible |
| 6 Reporting | T2, retouches templates → **T1** | Rendu déterministe |
| 7 Interface Flask + vanilla | T2, retouches CSS/HTML/JS → **T1** | Routes/templates standards |
| 8 Recette V3.5 end-to-end | **T3** | Traduire des règles scientifiques en tests d'acceptation est subtil |
| 9 Déploiement | T2, sécurité/runbook en **T3** | Docker standard, raisonnement sécurité |

Défaut quotidien recommandé : `opusplan` (Opus planifie, Sonnet implémente).

---

## Phase 0 — Socle & durcissement (focus actuel, sans code scientifique)

Objectif : rendre le développement **entouré, sécurisé, maintenable** avant d'écrire la moindre ligne de bioinfo.

Sous-étapes :

- **0.1 Gouvernance** — `AGENTS.md`, `CLAUDE.md`, `docs/CODE_INDEX.md`, `docs/DEV_TRACKING.md`, ce `ROADMAP.md` cohérents et à jour.
  - *Porte 0.1 — test :* relecture croisée, aucun lien mort, aucune contradiction entre fichiers. **Étape à tester avant la suivante.**
- **0.2 Outillage qualité** — `ruff` (lint + format), `mypy` (optionnel ciblé `core/`), `pre-commit`, config `pytest` + `coverage`, ajout aux deps + justification.
  - *Porte 0.2 — test :* `ruff check` vert, `pre-commit run --all-files` vert. **Étape à tester avant la suivante.**
- **0.3 CI/CD** — workflow (GitHub Actions) : `compileall` + `ruff` + `pytest` + seuil de couverture ; bloque la fusion si rouge.
  - *Porte 0.3 — test :* pipeline CI vert sur une PR de démonstration. **Étape à tester avant la suivante.**
- **0.4 Contrats d'interface** — figer les *seams* avant de remplir : dataclasses / modèles Pydantic / `Protocol` pour les entrées-sorties de `core/`, `external/`, `parsers/`. Définir `CommandResult`, schémas de métriques, schéma de sélection.
  - *Porte 0.4 — test :* `compileall` vert, tests de validation de schéma (cas valide + cas rejeté). **Étape à tester avant la suivante.**
- **0.5 Harnais de test & données synthétiques** — `conftest.py`, fixtures, jeu démo chr22 **synthétique** (jamais de données réelles), factories de jobs.
  - *Porte 0.5 — test :* les fixtures se chargent, le job démo se crée, le worker dry-run tourne de bout en bout. **Étape à tester avant la suivante.**
- **0.6 Sécurité socle** — validation stricte des chemins (`utils/validators.py`, `storage/`), allowlist exécutables, secrets via env, `.env.example`, scan secrets (CI), refus `shell=True`.
  - *Porte 0.6 — test :* tests refusant chemin hors périmètre, exécutable non autorisé, fichier absent. **Étape à tester avant la suivante.**

**Definition of Done Phase 0 :** CI verte, lint vert, contrats compilés et testés, fixtures opérationnelles, garde-fous sécurité testés. Aucune donnée réelle. `CODE_INDEX` et `DEV_TRACKING` à jour.

> **Porte de phase 0 → 1 : étape à tester avant la suivante.**

---

## Phase 1 — Wrappers outils externes (`external/`)

Objectif : un wrapper sûr par outil, sans toucher à l'algorithmie.

Sous-étapes (une porte de test par wrapper) :

- **1.0 `command_runner` durci** — timeout, capture de version d'outil, codes retour normalisés, logs stdout/stderr.
- **1.1 `plink` / 1.2 `plink2` / 1.3 `king` / 1.4 `admixture_tool` / 1.5 `bcftools` (+ `tabix`) / 1.6 `beagle` / 1.7 `shapeit4`** — chaque wrapper : construction d'arguments en **liste**, validation chemins entrée/sortie, jamais de chaîne shell libre.
  - *Porte par wrapper — test :* test de **génération d'arguments** (commande attendue) + test de **refus** (exécutable hors allowlist, chemin invalide). Aucune exécution d'outil réel requise. **Étape à tester avant la suivante.**

**DoD Phase 1 :** tous les wrappers testés (args + refus), `external/` n'importe jamais la couche web, `DEV_TRACKING` ISSUE-002 → `DONE`.

> **Porte de phase 1 → 2 : étape à tester avant la suivante.**

---

## Phase 2 — Parsers de sorties (`parsers/`)

Objectif : transformer les sorties d'outils en structures Python typées.

Sous-étapes :

- **2.1 `plink_parser` / 2.2 `king_parser` / 2.3 `pca_parser` / 2.4 `admixture_parser` / 2.5 `roh_parser` / 2.6 `imputation_parser`** — fichier de sortie → `dataclass` / DataFrame ; erreurs explicites sur format inattendu.
  - *Porte par parser — test :* parsing sur **fixture figée** (sortie réelle anonymisée stockée dans `tests/`) + cas d'erreur de format. **Étape à tester avant la suivante.**

**DoD Phase 2 :** chaque parser couvert par fixture + cas d'erreur ; types documentés.

> **Porte de phase 2 → 3 : étape à tester avant la suivante.**

---

## Phase 3 — Cœur scientifique (`core/`)

Objectif : algorithmes purs, testables **sans** interface, **sans** SQL, **sans** outil réel. Ordre méthodologique imposé.

Sous-étapes (chacune avec sa porte) :

- **3.1 QC SNP** → **3.2 LD pruning** → **3.3 PCA** → **3.4 ADMIXTURE** → **3.5 KING / IBD** → **3.6 ROH** → **3.7 S_div** → **3.8 Sélection WGS hybride** (noyau géo-ancestral + bras découverte + quotas secteurs + contraintes IBD + poids S_div) → **3.9 Imputation / simulation** → **3.10 Évaluation des stratégies**.
  - *Porte par sous-étape — test :* test unitaire **cas normal + cas d'erreur contrôlé** sur données synthétiques ; pour les calculs de score/quota, vérifier invariants (somme des poids = 1, total WGS conservé, exclusions IBD respectées). **Étape à tester avant la suivante.**

**DoD Phase 3 :** chaque module remplace son `NotImplementedError` par du code testé ; hypothèses dans les docstrings ; aucune fréquence WGS présentée comme définitive sans annotation d'incertitude (AGENTS §6) ; ISSUE-003 → `DONE`.

> **Porte de phase 3 → 4 : étape à tester avant la suivante.**

---

## Phase 4 — Orchestration & worker réel

Objectif : sortir du dry-run, exécuter de vraies étapes contrôlées.

Sous-étapes :

- **4.1 Orchestration** — remplir `orchestration/runner.py`, `steps.py`, `status.py` : ordre, dépendances, statut par étape.
  - *Porte 4.1 — test :* enchaînement simulé des étapes, propagation d'état. **Étape à tester avant la suivante.**
- **4.2 Worker réel** — brancher au moins une vraie étape via wrappers ; statut `failed` si étape critique échoue ; reprise.
  - *Porte 4.2 — test :* test du **chemin d'échec** (étape qui échoue → job `failed`, logs cohérents) + chemin nominal. **Étape à tester avant la suivante.**
- **4.3 Validation d'entrée stricte** — refuser chemins dangereux, formats inattendus, fichiers absents en amont du worker.
  - *Porte 4.3 — test :* batterie de rejets + acceptation d'un jeu valide. **Étape à tester avant la suivante.**

**DoD Phase 4 :** run démo chr22 synthétique de bout en bout via orchestration réelle ; ISSUE-001 et ISSUE-006 → `DONE`.

> **Porte de phase 4 → 5 : étape à tester avant la suivante.**

---

## Phase 5 — Persistance SQL ↔ jobs

Objectif : synchroniser métadonnées/scores/statuts/audit sans stocker de fichier brut.

Sous-étapes :

- **5.1 Services & repositories** — écrire dans `projects/cohorts/samples/analysis_jobs/.../selection_scores/wgs_selection/reports`.
  - *Porte 5.1 — test :* tests d'intégration DB (SQLite **isolé** pour l'unitaire, PostgreSQL pour l'intégration) ; vérifier qu'aucun VCF/BED n'entre en base. **Étape à tester avant la suivante.**
- **5.2 Migrations Alembic** — toute évolution de `models.py` accompagnée d'une migration.
  - *Porte 5.2 — test :* `alembic upgrade head` puis `downgrade` propres sur base de test. **Étape à tester avant la suivante.**

**DoD Phase 5 :** flux job ↔ SQL cohérent, migrations réversibles ; ISSUE-007 → `DONE`.

> **Porte de phase 5 → 6 : étape à tester avant la suivante.**

---

## Phase 6 — Reporting (`reporting/`)

Objectif : rapport reproductible depuis un run figé (`work/runs/<id>/`).

Sous-étapes :

- **6.1 `markdown_report` → 6.2 `html_report` → 6.3 `pdf_report`** — rendu déterministe ; conventions `/report-formater` + `/stop-slop`, palette teal/navy/coral, Paged.js.
  - *Porte par format — test :* **snapshot test** (même run figé → même rapport) ; toute incertitude annotée. **Étape à tester avant la suivante.**

**DoD Phase 6 :** rapport généré identique à l'identique depuis un run de référence ; ISSUE-005 → `DONE`.

> **Porte de phase 6 → 7 : étape à tester avant la suivante.**

---

## Phase 7 — Interface web Flask + front vanilla (`web/`)

Objectif : interface web cohérente en Flask (templates server-side) + HTML/CSS/JS vanilla. L'interface déclenche des jobs, n'exécute jamais de bioinfo, ne bloque pas la requête HTTP.

Sous-étapes :

- **7.1 Routes & templates** — tableau de bord, détail de run, données, comparaison, rapports ; provenance (run_id, hash config, versions outils) en tête.
- **7.2 Endpoints JSON + polling vanilla** — `GET /api/jobs/<id>/status` consommé par `web/static/js/app.js` ; états incluant `failed`.
- **7.3 Graphiques en SVG côté serveur** — PCA, ADMIXTURE rendus via le pipeline de reporting et injectés dans les templates (pas de lib de charting front).
- **7.4 Viewer de logs** filtrable par étape, stdout/stderr, statut.
  - *Porte par vue — test :* smoke test via le client de test Flask (`app.test_client()`) + test de validation des paramètres avant création de job + test que la route ne lance aucun sous-processus bioinfo. **Étape à tester avant la suivante.**

**DoD Phase 7 :** aucun seuil scientifique en dur dans l'interface ; front strictement vanilla (pas de framework, pas de build) ; ISSUE-004 et ISSUE-008 → `DONE`.

> **Porte de phase 7 → 8 : étape à tester avant la suivante.**

---

## Phase 8 — Recette V3.5 end-to-end

Objectif : transformer les règles de sélection V3.5 en tests d'acceptation et valider un run complet.

Sous-étapes :

- **8.1 Tests d'acceptation** — quotas par secteur, bras découverte, contraintes IBD, poids S_div, analyses de sensibilité (seeds/poids/scénarios).
- **8.2 Run end-to-end** sur jeu démo synthétique : interface → job → worker → SQL → rapport.
  - *Porte 8 — test :* tous les tests d'acceptation verts + run E2E reproductible. **Étape à tester avant la suivante.**

**DoD Phase 8 :** ISSUE-009 → `DONE` ; comportement scientifique conforme à la méthodologie documentée.

> **Porte de phase 8 → 9 : étape à tester avant la suivante.**

---

## Phase 9 — Déploiement

Objectif : déployable de façon reproductible et sûre.

Sous-étapes :

- **9.1 Images Docker** `genorun-app`, `genorun-worker`, `genorun-db` + `docker compose` ; aucune donnée génétique dans l'image.
- **9.2 Init base & secrets** — `.env` prod, `GENORUN_DATABASE_URL` via env, init/migrations.
- **9.3 Smoke test déploiement** — healthchecks, file de jobs en mode Docker (interface met en file, worker exécute).
- **9.4 Doc déploiement & runbook** — démarrage, sauvegarde, restauration, rotation des logs, incident, note proxy SSL CHU.
  - *Porte 9 — test :* `docker compose up` sain, smoke test E2E en conteneurs, runbook relu. **Étape à tester avant la suivante.**

**DoD Phase 9 :** stack démarrée et vérifiée, runbook complet, aucun secret ni donnée réelle dans l'image.

> **Porte finale → mise en production : étape à tester avant la mise en service.**

---

## Règles transverses (valables à chaque phase)

- Une porte non verte **bloque** la phase suivante : pas de contournement.
- Tout `TODO[DEV_TRACKING]` / `FIXME[DEV_TRACKING]` ouvert pendant une phase doit avoir sa ligne dans `docs/DEV_TRACKING.md`.
- Toute structure de code qui bouge → `docs/CODE_INDEX.md` mis à jour dans le même lot.
- Jamais de donnée génétique réelle, de secret ou de chemin personnel, à aucune phase, y compris dans les tests et fixtures.
