# CLAUDE.md — Guide opérationnel pour Claude Code

## Génome Réunion — Validation Pipeline

Ce fichier est le **point d'entrée de Claude Code** sur ce dépôt. Il définit comment Claude doit travailler, vérifier et livrer, avec le **même niveau d'exigence que `AGENTS.md`**.

> **Hiérarchie d'autorité**
> `AGENTS.md` reste la **source de vérité** pour l'architecture, la science, la sécurité et le style de code.
> En cas de conflit entre ce fichier et `AGENTS.md`, **`AGENTS.md` l'emporte**.
> `CLAUDE.md` ajoute la couche *opérationnelle* (méthode de travail, commandes, environnement, état réel du code) que Claude Code doit appliquer.

---

## 0. Lecture obligatoire avant toute action

Avant **toute** modification, lire dans cet ordre :

1. `AGENTS.md` — règles non négociables ;
2. `docs/CODE_INDEX.md` — carte du code ;
3. `docs/DEV_TRACKING.md` — décisions, dette, erreurs connues, priorités ;
4. la section **§9 (État réel du code)** ci-dessous ;
5. le ou les fichiers + tests directement concernés.

Ne jamais présumer qu'un module est implémenté : vérifier dans §9 ou ouvrir le fichier.

---

## 1. Règle d'architecture centrale (rappel)

L'interface **déclenche** un job, elle **n'exécute jamais** de commande bioinformatique brute.

```text
Navigateur (vanilla) → Flask → validation params → JobManager → work/runs/<run_id>/{config.yaml,manifest.json,status.json}
         → Worker (local/Docker) → wrappers external/ (shell=False) → logs/résultats → PostgreSQL → Interface
```

Toute commande externe passe par `external/command_runner.py` ou un wrapper contrôlé. Jamais `shell=True` sans justification documentée et revue.

---

## 2. Méthode de travail Claude Code (non négociable)

1. **Périmètre minimal.** Modifier le plus petit ensemble de fichiers possible. Pas de réécriture globale non demandée. Conserver chemins, signatures et contrats existants.
2. **Plan d'abord.** Pour toute tâche non triviale, annoncer en 3–6 lignes : fichiers touchés, approche, tests prévus. Puis exécuter.
3. **Édition chirurgicale.** Préférer la modification ciblée à la régénération de fichier entier. Ne pas reformater du code non concerné.
4. **Un sujet = un lot.** Ne pas mélanger refactor, fonctionnalité et correction dans le même lot sans le dire.
5. **Vérifier avant de livrer** (voir §3). Ne jamais affirmer « ça marche » sans avoir lancé `compileall` + `pytest`.
6. **Mettre à jour la doc** (voir §5) dans le même lot que le code.
7. **Annoncer le reste.** Terminer en listant ce qui est fait et ce qui reste (issues `DEV_TRACKING`).
8. **Pas de donnée réelle, pas de secret, pas de chemin personnel absolu.** Jamais. Y compris dans les tests et les exemples.

---

## 3. Vérification avant toute proposition

Commandes de référence (depuis la racine du dépôt) :

```bash
python -m compileall src scripts web      # compilation
pytest -q                                  # tests
```

Si le modèle SQL change :

```bash
alembic revision --autogenerate -m "<description courte>"
alembic upgrade head
```

Régle : **aucun lot livré sans `compileall` vert et `pytest` vert** (ou justification explicite si un test est volontairement laissé rouge avec entrée `DEV_TRACKING`).

> Outillage : seul `pytest` est configuré aujourd'hui (`pyproject.toml`). Si tu ajoutes `ruff`/`black`/`mypy`, ajoute-les à `pyproject.toml` + `requirements.txt` et documente la décision dans `DEV_TRACKING.md` avant de les imposer.

---

## 4. Contrat de qualité de code (rappel condensé de AGENTS §13)

Priorité : **exactitude scientifique → sécurité → reproductibilité → lisibilité → performance**.

- Une fonction = une responsabilité ; viser ≤ 40–60 lignes pour le métier.
- Noms explicites orientés métier (`selected_sample_ids`, `roh_total_length_mb`), pas `x`/`tmp`/`res`.
- Annotations de type + docstring courte + erreurs explicites sur toute fonction importante.
- Booléens lisibles comme une phrase (`has_valid_manifest`, `should_launch_worker`).
- Seuils scientifiques dans `config/*.yaml` ou constantes nommées, **jamais** codés en dur dans l'interface web.
- Unités visibles (`min_roh_length_mb`, `window_size_kb`, `ibd_exclusion_threshold`).
- `core/` et `external/` **n'importent jamais la couche web**.
- Commentaires préfixés et localisables : `# WHY:` `# SAFETY:` `# METHOD:` `# TODO[DEV_TRACKING]:` `# FIXME[DEV_TRACKING]:`.
- **Aucun `TODO`/`FIXME` sans ligne correspondante dans `docs/DEV_TRACKING.md`.**
- Imports : standard → externes → projet. Pas d'import circulaire.

---

## 5. Obligations documentaires (à faire dans le même lot que le code)

- Fichier important créé / déplacé / renommé / supprimé → mettre à jour `docs/CODE_INDEX.md`.
- Décision d'architecture, dette acceptée, erreur connue → mettre à jour `docs/DEV_TRACKING.md` (daté).
- Changement de méthodologie scientifique → documenter l'impact dans `docs/` (et `# METHOD:` dans le code).
- `TODO[DEV_TRACKING]` / `FIXME[DEV_TRACKING]` ajouté → créer la ligne dans `DEV_TRACKING.md`.
- Commentaires et docs en **français clair** ; noms de fonctions/classes en anglais autorisés.

---

## 6. Définition de « terminé » (Definition of Done)

Une tâche n'est terminée que si **toutes** ces conditions sont vraies :

- [ ] le code/la doc demandé est présent et fonctionnel ;
- [ ] les règles d'architecture de `AGENTS.md` sont respectées ;
- [ ] `python -m compileall src scripts web` passe ;
- [ ] `pytest -q` passe (ou exception justifiée + `DEV_TRACKING`) ;
- [ ] tests ajoutés/adaptés si la logique change (cas normal **et** cas d'erreur) ;
- [ ] `docs/CODE_INDEX.md` à jour si la structure change ;
- [ ] `docs/DEV_TRACKING.md` à jour si conception/dette/erreur change ;
- [ ] aucune donnée réelle, aucun secret, aucun chemin personnel ajouté ;
- [ ] aucun `shell=True` injustifié, aucun résultat simulé présenté comme réel.

---

## 7. Tests obligatoires

Ajouter/adapter un test quand la modification touche :
calcul de score, quotas, sélection, validation de paramètres, génération de commande externe, gestion de job, écriture manifest/log/status, parsing de sortie PLINK/KING/ADMIXTURE.

Chaque test couvre **le cas normal + un cas d'erreur contrôlé**. Les tests `core/` doivent tourner **sans** interface, **sans** base SQL réelle, **sans** outil bioinfo réel (utiliser fixtures et sorties figées dans `tests/`).

---

## 8. Environnement & exécution

### Mode local
```bash
conda env create -f environment.yml && conda activate genorun-validation
pip install -e .
bash scripts/check_tools.sh
python scripts/init_database.py
flask --app web run --debug
```
PostgreSQL n'est actif que si `GENORUN_ENABLE_DATABASE=true`. `GENORUN_DATABASE_URL` est lu depuis l'environnement, jamais codé en dur.

### Mode Docker
Services officiels : `genorun-app`, `genorun-worker`, `genorun-db`. L'image n'embarque **jamais** de données génétiques. En Docker, l'interface met les jobs en file, le worker externe les exécute.

### Tester le flux jobs sans interface
```bash
python scripts/create_demo_job.py
python scripts/run_worker.py --job-id <ID>
python scripts/run_worker_loop.py
```

### Réseau CHU (proxy SSL)
Le réseau corporate du CHU pratique l'inspection SSL. Si `pip`/`conda`/Claude Code échouent sur des erreurs de certificat, c'est attendu : `api.anthropic.com` et les miroirs paquets doivent être whitelistés par la DSI. Ne pas désactiver la vérification TLS dans le code ni committer de contournement.

### Skills de rédaction
Pour la prose des rapports et docs, appliquer les skills projet `/stop-slop` (suppression des tics IA) et `/report-formater` (assemblage HTML imprimable, palette teal/navy/coral).

---

## 9. État réel du code (carte à jour — vérifier avant de coder)

> Le scaffold a une **infrastructure réelle** mais un **cœur scientifique encore en stubs**. Ne pas supposer qu'un module fait ce que son nom suggère.

### ✅ Implémenté (couche infrastructure)
- `database/models.py`, `repositories.py`, `session.py`, `init_db.py` — modèle SQL + accès métadonnées ;
- `jobs/manager.py`, `jobs/schemas.py` — création/suivi/statuts/manifest des jobs ;
- `jobs/worker.py` — worker **dry-run** uniquement (écrit marqueurs + sorties démo, n'exécute aucun outil) ;
- `external/command_runner.py` — exécution sécurisée `shell=False` + allowlist d'exécutables ;
- `settings.py`, `cli.py`, Docker/Compose, Alembic, `config/*.yaml`, docs de gouvernance.

### 🔲 Stubs / vides (à implémenter — lèvent `NotImplementedError` ou sont à 1 ligne)
- **`core/`** : `qc`, `ld_pruning`, `pca`, `admixture`, `kinship`, `roh`, `sdiv`, `selection`, `imputation`, `evaluation`, `simulation_profiles` ;
- **`external/`** : `plink`, `plink2`, `king`, `admixture_tool`, `bcftools`, `beagle`, `shapeit4` (wrappers) ;
- **`services/`** : tous (dataset, file, project, report, result, run, sample, selection) ;
- **`parsers/`** : tous (plink, king, pca, admixture, roh, imputation) ;
- **`reporting/`** : `html_report`, `markdown_report`, `pdf_report` ;
- **`orchestration/`** : `runner.py` ne fait qu'afficher les étapes ; `steps.py`, `status.py` vides ;
- **`web/`** : squelette Flask + front vanilla en place (factory, routes, templates, statics) ; pages données/comparaison/rapports et rendu SVG serveur à construire (Phase 7).

> Quand tu implémentes un stub : remplacer `NotImplementedError` par du vrai code **testé**, déplacer l'issue correspondante de `DEV_TRACKING.md` vers `REVIEW`/`DONE`, et mettre à jour `CODE_INDEX.md`.

---

## 10. Priorités d'implémentation (suivre `DEV_TRACKING.md`)

Ordre recommandé, du socle vers le sommet :

1. **Wrappers `external/`** (ISSUE-002) — un wrapper par outil, args en liste, logs, code retour, testés sans données lourdes.
2. **`parsers/`** — lecture des sorties PLINK/KING/ADMIXTURE en structures Python typées (fixtures figées).
3. **Cœur `core/`** (ISSUE-003) — QC → LD pruning → PCA → ADMIXTURE → KING/IBD → ROH → S_div → sélection → imputation → évaluation, chacun pur et testable.
4. **Worker réel** (ISSUE-001) — brancher au moins une vraie étape contrôlée avec test d'échec, sortir du dry-run par étape.
5. **Validation d'entrée stricte** (ISSUE-006) — refuser chemins dangereux, formats inattendus, fichiers absents.
6. **Connexion SQL ↔ jobs** (ISSUE-007) — synchroniser métadonnées sans stocker de fichier brut.
7. **`reporting/`** (ISSUE-005) — rapport reproductible depuis un run.
8. **Vues web** (ISSUE-004) + viewer de logs (ISSUE-008).
9. **Sélection V3.5 → tests d'acceptation** (ISSUE-009) — quotas, bras découverte, contraintes IBD, poids S_div.

---

## 11. Contrats par domaine (à respecter en implémentant)

- **`core/`** : fonctions pures `numpy`/`pandas`, signatures typées, hypothèses dans la docstring, aucune I/O cachée, aucune dépendance à l'interface web ni à un outil externe. Entrée = structures de données ; sortie = structures de données.
- **`external/`** : `prepare → validate → run_command → return CommandResult`. Valider exécutable (allowlist) et chemins. Toujours écrire stdout/stderr. Retourner code de sortie ; déclencher `failed` côté worker si critique.
- **`parsers/`** : transformer un fichier de sortie d'outil en `dataclass`/DataFrame. Tolérer les variations de format avec erreurs explicites. Tests sur fixtures figées dans `tests/`.
- **`services/`** : logique applicative orchestrant `core` + `database` + `storage`. Pas de commande shell ici.
- **`reporting/`** : rendu déterministe depuis un run figé (`work/runs/<id>/`). Annoter toute incertitude ; jamais présenter une fréquence WGS comme définitive sans pondération/annotation (cf. AGENTS §6).
- **`web/`** : Flask + front vanilla uniquement. Validation + appel `services`/`jobs`. Aucune logique bioinfo profonde, aucun seuil scientifique en dur.

---

## 12. Garde-fous scientifiques (rappel AGENTS §6)

La sélection WGS est un **panel hybride** (noyau géo-ancestral + bras découverte contrôlé + recalibrage des fréquences sur la cohorte SNP complète + analyses de sensibilité). Ne jamais la décrire comme un tirage aléatoire simple. Ne jamais faire passer un résultat simulé pour un résultat sur données réelles. Aucun diagnostic clinique, aucun dispositif médical.

---

## 13. Conventions de commit / lot

- Messages en français, impératif court : `feat(core): implémente le calcul S_div` ;
- Préfixes : `feat` `fix` `refactor` `test` `docs` `chore` `db` ;
- Un lot = un sujet cohérent + ses tests + sa mise à jour de doc ;
- Référencer l'issue `DEV_TRACKING` concernée dans le corps quand pertinent.

---

## 14. Interdictions absolues (rappel — voir AGENTS §3)

Ne jamais : committer des données génétiques réelles ou des identifiants patients ; stocker VCF/BCF/BAM/CRAM/PLINK lourds en SQL ; construire une commande par concaténation de chaînes utilisateur ; `shell=True` injustifié ; exécuter PLINK/KING/ADMIXTURE depuis une route/vue web ; mélanger interface + métier + commande dans un fichier ; supprimer un QC/log/manifest sans remplacement ; présenter un résultat simulé comme réel.

---

## 17. Choix du modèle Claude par complexité (Claude Code)

But : régler le compromis qualité / vitesse / coût (consommation de quota) selon la difficulté réelle de la tâche. **Source unique de la correspondance palier → modèle : cette section.** Le `ROADMAP.md` ne référence que les paliers, pas les noms de modèles, pour que toute évolution se modifie ici uniquement.

### Paliers

| Palier | Modèle conseillé (2026) | Pour quel type de tâche |
|---|---|---|
| **T1 — Léger** | `haiku` (Haiku 4.5) | Mécanique, bien spécifié, peu ambigu : éditions en masse, formatage, docstrings, mise à jour de `CODE_INDEX.md`, parseurs à format fixe simple, échafaudage de tests répétitifs, retouches HTML/CSS/JS. |
| **T2 — Standard** *(défaut)* | `sonnet` (Sonnet 4.6) | La majorité de l'implémentation : wrappers, parseurs, services, routes/templates Flask, tests standards, refactors modérés, seuils de QC. |
| **T3 — Avancé** | `opus` (Opus 4.8) | Raisonnement complexe ou correction critique : conception des contrats, **cœur scientifique** (pondération S_div, sélection hybride quotas + IBD + sensibilité), conception worker/échec/concurrence, schéma & migrations, **tests d'acceptation V3.5**, débogage difficile, refactors multi-fichiers, sécurité, et **revue des chemins critiques**. Activer l'effort de raisonnement élevé pour les cas les plus délicats. |
| **T4 — Expert** | `fable` (Fable 5) | Réservé aux tâches les plus lourdes / multi-sessions autonomes, ou quand Opus cale : implémentation de bout en bout du cadre sélection + analyses de sensibilité, grosses migrations transverses. Le plus capable mais le plus coûteux — pas un défaut. |

### Règles d'usage

- **Défaut quotidien :** `opusplan` (Opus planifie, Sonnet implémente) pour tout travail non trivial ; cela colle à la méthode « plan d'abord, puis exécution » (CLAUDE.md §2).
- **Escalade :** commencer au palier le plus bas plausible ; monter d'un cran si le modèle peine ou si l'enjeu est élevé.
- **Revue obligatoire au palier T3 minimum** des chemins critiques quel que soit l'auteur : tout ce qui touche la correction scientifique (S_div, sélection), la sécurité (validation, shell), ou les migrations de base.
- **Reproductibilité :** pour figer une version (audit), utiliser le nom complet (`claude-opus-4-8`) plutôt que l'alias.

### Mécanique Claude Code

```text
/model               liste les modèles disponibles
/model opus          bascule immédiate (garde le contexte)
/model sonnet
/model haiku
/model opusplan      mode hybride : Opus planifie, Sonnet implémente
/status              affiche le modèle actif
```

Permanence (du plus prioritaire au moins) : `/model` en session > `claude --model <m>` au lancement > variable d'environnement `ANTHROPIC_MODEL` > champ `model` dans `~/.claude/settings.json`.
