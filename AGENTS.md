# Règles Codex — Génome Réunion Validation Pipeline

Ce fichier est prioritaire pour tout agent IA ou développeur intervenant sur ce dépôt. Il définit les règles non négociables du logiciel de validation et de sélection WGS du projet **Génome Réunion**.

## 1. Mission du logiciel

Le logiciel sert à piloter, valider et auditer une sélection d'échantillons ADN pour un référentiel génomique réunionnais de première génération.

Il doit permettre :

- de charger des jeux de données SNP / panels de référence ;
- d'exécuter un pipeline bioinformatique reproductible ;
- de comparer plusieurs stratégies de sélection ;
- de produire une sélection WGS justifiée individu par individu ;
- de générer des rapports scientifiques et techniques ;
- de conserver une traçabilité complète des paramètres, commandes, versions logicielles, logs et résultats.

Le logiciel ne réalise aucun diagnostic clinique et ne doit jamais être présenté comme un dispositif médical.

## 2. Règle d'architecture centrale

L'utilisateur peut lancer les analyses depuis l'interface.

Cependant, l'interface ne doit jamais exécuter directement des commandes shell libres ou bloquantes dans son propre processus. Elle doit créer un **job local sécurisé, validé, traçable et reproductible**, puis déléguer l'exécution à un worker.

Flux obligatoire :

```text
Interface web (Flask + front vanilla)
        ↓
Validation des paramètres
        ↓
Création d'un job local
        ↓
Écriture config.yaml + manifest.json
        ↓
Worker local dédié
        ↓
Exécution contrôlée des étapes pipeline
        ↓
Logs + statuts + métriques + résultats
        ↓
Interface : progression, résultats ou alerte d'erreur
```

## 3. Interdictions absolues

Ne jamais :

- mettre des données génétiques réelles dans Git ;
- créer un exemple contenant des identifiants patients réels ;
- stocker VCF/BCF/BAM/CRAM/PLINK lourds en base SQL ;
- construire une commande shell par concaténation de chaînes utilisateur ;
- utiliser `shell=True` sauf justification documentée et revue ;
- exécuter PLINK/KING/ADMIXTURE directement depuis une vue/route web ;
- mélanger interface, logique métier et commandes bioinformatiques dans le même fichier ;
- modifier la méthodologie scientifique sans documenter l'impact dans `docs/` ;
- supprimer un contrôle qualité, un log ou un manifest sans remplacement équivalent ;
- faire passer un résultat simulé pour un résultat issu de données réelles.

## 4. Principe de données

La base SQL ne conserve que :

- métadonnées projet / dataset / run ;
- paramètres validés ;
- scores et métriques synthétiques ;
- statuts d'exécution ;
- chemins contrôlés vers fichiers ;
- checksums ;
- rapports et logs.

Les fichiers génétiques bruts restent dans un stockage fichiers contrôlé et exclu de Git.

## 5. Pipeline méthodologique attendu

Ordre logique recommandé :

1. QC SNP ;
2. LD pruning ;
3. PCA globale ;
4. ADMIXTURE global ;
5. KING / IBD ;
6. ROH ;
7. calcul S_div ;
8. sélection WGS ;
9. imputation ou simulation d'imputation ;
10. évaluation des stratégies ;
11. rapport final.

Toute nouvelle étape doit préciser :

- son objectif ;
- ses entrées ;
- ses sorties ;
- ses paramètres ;
- ses logs ;
- ses critères d'échec ;
- ses tests unitaires.

## 6. Sélection WGS : garde-fous scientifiques

Ne jamais décrire la sélection comme un tirage aléatoire simple.

Le panel WGS est un panel hybride :

- noyau géo-ancestral principal ;
- bras découverte contrôlé ;
- recalibrage des fréquences sur la cohorte SNP complète ;
- analyses de sensibilité sur les poids, seeds et scénarios.

Les fréquences observées dans les WGS sélectionnés ne doivent pas être présentées comme des fréquences populationnelles définitives sans pondération, imputation ou annotation d'incertitude.

## 7. Sécurité d'exécution

Tout wrapper d'outil externe doit :

- recevoir une liste d'arguments, jamais une chaîne shell libre ;
- valider l'exécutable contre une liste d'outils autorisés ;
- valider les chemins d'entrée/sortie ;
- écrire stdout et stderr dans des fichiers de logs ;
- retourner un code de sortie ;
- déclencher un statut `failed` en cas d'erreur ;
- conserver la commande exécutée dans un manifest d'audit.

## 8. Structure de code obligatoire

Respecter la séparation suivante :

```text
web/                      Interface web Flask : routes, templates, statics
src/genorun_validation/
  core/                   Algorithmes purs et testables
  external/               Wrappers sécurisés des outils externes
  jobs/                   Création, suivi et exécution des jobs locaux
  orchestration/          Ordre des étapes et coordination pipeline
  database/               Modèles SQL et accès aux métadonnées
  services/               Logique applicative
  storage/                Chemins, checksums, registre fichiers
  parsers/                Lecture des sorties PLINK/KING/etc.
  reporting/              Rapports HTML/PDF/Markdown
  utils/                  Fonctions génériques
scripts/                  Commandes d'administration et worker CLI
docs/                     Décisions d'architecture et méthodologie
tests/                    Tests unitaires et tests d'intégration
```

## 9. Règles de maintenabilité

Chaque nouvelle fonction importante doit avoir :

- un nom explicite ;
- une docstring courte ;
- des types Python ;
- des erreurs explicites ;
- au moins un test si elle transforme des données ou pilote une exécution ;
- aucune dépendance cachée à l'état de l'interface web.

Les modules `core/` ne doivent pas importer la couche web.

Les modules `external/` ne doivent pas importer la couche web.

Les modules `jobs/` peuvent être appelés par la couche web, la CLI ou les tests.

## 10. Règles de configuration

Les paramètres scientifiques doivent être dans `config/*.yaml`, pas codés en dur dans l'interface.

Chaque run doit figer sa propre copie de configuration dans :

```text
work/runs/<run_id>/config.yaml
work/runs/<run_id>/manifest.json
```

## 11. Critères avant merge

Avant de proposer un changement :

```bash
python -m compileall src scripts web
pytest
```

Le changement doit aussi respecter :

- aucune donnée réelle ajoutée ;
- aucun secret ;
- aucun chemin absolu personnel ;
- aucun `shell=True` injustifié ;
- aucun résultat simulé ambigu ;
- documentation mise à jour si l'architecture change.

## 12. Ton et documentation

Les commentaires et documents doivent être écrits en français clair. Les noms de fonctions/classes peuvent rester en anglais si cela améliore la lisibilité technique.

La documentation doit être utile à un développeur compétent qui reprend le projet sans connaître l'historique de la conversation.

## 13. Règles de qualité du code Python

Le code doit être compréhensible par un développeur compétent qui découvre le projet. La priorité est : **exactitude scientifique → sécurité → reproductibilité → lisibilité → performance**.

### 13.1 Lisibilité et découpage

- Une fonction = une responsabilité principale.
- Une fonction métier doit idéalement rester courte ; si elle dépasse environ 40–60 lignes, vérifier si elle doit être découpée.
- Les étapes du pipeline doivent être isolées : QC, pruning, PCA, ADMIXTURE, KING/IBD, ROH, S_div, sélection, imputation, rapport.
- Le code d'interface web (Flask + vanilla) ne doit pas contenir de logique bioinformatique profonde.
- Le code `core/` doit être testable sans interface, sans base SQL et sans outil externe réel.
- Le code `external/` doit uniquement préparer, valider et exécuter des commandes contrôlées.
- Le code `jobs/` doit gérer l'état, les chemins, les manifests, les statuts et les logs.

### 13.2 Nommage des variables

Utiliser des noms explicites, orientés métier.

Préférer :

```python
selected_sample_ids: list[str]
sector_quota: dict[str, int]
plink_bed_path: Path
admixture_k_values: list[int]
roh_total_length_mb: float
sdiv_weights: dict[str, float]
```

Éviter :

```python
x
y
d
tmp
data2
new
res
```

Exceptions acceptées :

- `i`, `j`, `k` uniquement pour de petites boucles très locales ;
- `df` uniquement dans un bloc court et évident ; sinon préférer `samples_df`, `roh_segments_df`, `pca_coordinates_df` ;
- `q_k` accepté pour les proportions ADMIXTURE si le contexte est clair.

### 13.3 Unités, seuils et constantes

Toute variable numérique scientifique doit rendre son unité visible lorsque c'est utile.

Exemples :

```python
min_roh_length_mb = 1.0
ibd_exclusion_threshold = 0.125
max_missing_rate = 0.02
window_size_kb = 1000
```

Les constantes partagées doivent être en majuscules si elles sont stables :

```python
DEFAULT_IBD_THRESHOLD = 0.125
DEFAULT_WGS_TARGET_SIZE = 350
```

Aucun seuil scientifique important ne doit être caché dans une vue web. Il doit être dans `config/*.yaml`, dans un module de configuration, ou clairement documenté dans le manifest du run.

### 13.4 Booléens

Les booléens doivent se lire comme une phrase vraie/fausse.

Préférer :

```python
is_dry_run = True
has_valid_manifest = manifest_path.exists()
should_launch_worker = run_now and job.status == JobStatus.CREATED
```

Éviter :

```python
flag = True
ok = False
launch = 1
```

### 13.5 Fonctions et signatures

Les fonctions importantes doivent avoir :

- des annotations de type ;
- une docstring courte ;
- des paramètres explicites ;
- une valeur de retour claire ;
- des exceptions explicites quand l'échec est attendu.

Exemple attendu :

```python
def compute_sector_quota(sector_counts: dict[str, int], total_wgs: int) -> dict[str, int]:
    """Calcule les quotas WGS par secteur en conservant exactement `total_wgs` individus."""
```

Éviter les fonctions qui prennent des dictionnaires non documentés quand une `dataclass`, un modèle Pydantic ou un schéma clair serait plus sûr.

### 13.6 Commentaires utiles, clairs et localisables

Les commentaires doivent aider à comprendre **pourquoi** une décision existe. Ils ne doivent pas répéter mécaniquement le code.

Mauvais commentaire :

```python
# On ajoute 1
position = index + 1
```

Bon commentaire :

```python
# WHY: PLINK utilise des positions 1-based alors que l'index Python est 0-based.
position = index + 1
```

Utiliser ces préfixes pour rendre les commentaires faciles à retrouver :

- `# WHY:` justification métier, scientifique ou technique ;
- `# SAFETY:` garde-fou sécurité, données, shell, fichiers, RGPD ;
- `# METHOD:` justification méthodologique Génome Réunion ;
- `# TODO[DEV_TRACKING]:` tâche volontairement non terminée et inscrite dans `docs/DEV_TRACKING.md` ;
- `# FIXME[DEV_TRACKING]:` défaut connu qui doit avoir une ligne dans `docs/DEV_TRACKING.md`.

Interdiction : laisser un `TODO` ou un `FIXME` sans entrée correspondante dans `docs/DEV_TRACKING.md`.

### 13.7 Docstrings

Une docstring doit expliquer le rôle de la fonction, pas réécrire son code. Pour les fonctions scientifiques, préciser les hypothèses.

Exemple :

```python
def compute_admixture_entropy(q_matrix: np.ndarray) -> np.ndarray:
    """Calcule l'entropie de Shannon des profils ADMIXTURE.

    Les lignes doivent représenter les individus et les colonnes les composantes K.
    Les proportions doivent être normalisées par individu.
    """
```

### 13.8 Gestion d'erreurs

- Les erreurs doivent être explicites et actionnables.
- Inclure le contexte utile : `job_id`, étape pipeline, chemin logique, paramètre fautif.
- Ne jamais afficher de secret, token, identifiant patient ou chemin sensible non nécessaire.
- Ne pas avaler silencieusement une exception critique.
- Le worker doit passer le job en `failed` si une étape critique échoue.

Exemple :

```python
raise ValueError(
    f"Poids S_div invalides pour job_id={job_id}: somme={weights_sum}, attendu=1.0"
)
```

### 13.9 Imports et dépendances

- Imports standards d'abord, puis dépendances externes, puis imports projet.
- Pas d'import circulaire.
- Pas de dépendance lourde dans une vue web si elle peut être chargée dans `core/` ou `services/`.
- Toute nouvelle dépendance doit être ajoutée à `requirements.txt` ou `environment.yml` avec justification si elle est lourde.

### 13.10 Tests obligatoires

Ajouter ou adapter des tests quand la modification touche :

- calcul de score ;
- quotas ;
- sélection ;
- validation de paramètres ;
- génération de commande externe ;
- gestion de job ;
- écriture de manifest/log/status ;
- parsing de sortie PLINK/KING/ADMIXTURE.

Un test doit vérifier au minimum le cas normal et un cas d'erreur contrôlé.

## 14. Règles documentaires obligatoires

Trois fichiers guident le projet :

```text
AGENTS.md
→ règles d'autorité pour l'IA et les développeurs.

docs/CODE_INDEX.md
→ carte du code pour localiser rapidement les modules, fonctions et zones d'erreur.

docs/DEV_TRACKING.md
→ suivi de conception, problèmes connus, dette technique, corrections et prochaines étapes.
```

Toute modification importante doit respecter ces règles :

- si un fichier important est créé, déplacé, renommé ou supprimé, mettre à jour `docs/CODE_INDEX.md` ;
- si une décision d'architecture est prise, la consigner dans `docs/DEV_TRACKING.md` ;
- si une erreur connue reste ouverte, l'ajouter dans `docs/DEV_TRACKING.md` ;
- si un `TODO[DEV_TRACKING]` ou `FIXME[DEV_TRACKING]` est ajouté dans le code, créer la ligne correspondante dans `docs/DEV_TRACKING.md` ;
- si une dette technique est acceptée temporairement, indiquer pourquoi et comment elle sera corrigée.

## 15. Règles spécifiques Codex / IA

Avant toute modification, l'agent doit lire dans cet ordre :

1. `AGENTS.md` ;
2. `docs/CODE_INDEX.md` ;
3. `docs/DEV_TRACKING.md` ;
4. le ou les fichiers directement concernés.

L'agent doit ensuite :

- modifier le plus petit périmètre possible ;
- éviter les réécritures globales non demandées ;
- conserver les chemins et contrats existants ;
- ajouter des tests si la logique change ;
- mettre à jour `CODE_INDEX.md` et `DEV_TRACKING.md` si nécessaire ;
- annoncer clairement ce qui a été fait et ce qui reste à faire.

## 16. Définition de terminé

Une tâche est considérée terminée uniquement si :

- le code ou la documentation demandée est présent ;
- les règles d'architecture sont respectées ;
- les tests pertinents passent ou l'absence de test est justifiée ;
- `docs/CODE_INDEX.md` est à jour si la structure change ;
- `docs/DEV_TRACKING.md` est à jour si la conception ou les erreurs connues changent ;
- aucune donnée réelle, aucun secret et aucun chemin personnel n'ont été ajoutés.


## 17. Règles PostgreSQL et Docker

PostgreSQL est la base officielle du logiciel. SQLite ne doit pas devenir la base principale du projet ; il peut uniquement servir à des tests unitaires isolés.

Règles obligatoires :

- toute modification du modèle de données passe par `src/genorun_validation/database/models.py` et une migration Alembic ;
- les gros fichiers génétiques ne sont jamais stockés dans PostgreSQL ;
- la base stocke des chemins relatifs, checksums, tailles, statuts, paramètres et audits ;
- `GENORUN_DATABASE_URL` doit être lu depuis l'environnement, jamais codé en dur dans l'interface ;
- les secrets Docker/PostgreSQL doivent passer par `.env` ou variables d'environnement ; `.env.example` ne contient que des valeurs de développement à remplacer ;
- l'image Docker doit installer le package applicatif (`pip install -e .`) afin de garantir les imports en conteneur ;
- quand `GENORUN_ENABLE_DATABASE=true`, PostgreSQL est la file officielle des jobs ; `work/runs/` reste la trace reproductible du run ;
- l'application doit rester compatible avec le mode local simple et le mode Docker ;
- Docker ne doit jamais embarquer de vraies données génétiques dans l'image ;
- les services Docker officiels sont `genorun-app`, `genorun-worker`, `genorun-db` ;
- en mode Docker, l'interface met les jobs en file et le worker externe les exécute.

Avant toute modification touchant la base ou Docker, lire :

```text
docs/05_structure_base_donnees.md
docs/POSTGRESQL_GUIDE_BEGINNER.md
docs/DOCKER_GUIDE_BEGINNER.md
```
