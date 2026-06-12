# Structure cible — Pipeline + Interface + Base de données

## 1. Objectif

Transformer le pipeline bioinformatique du projet **Génome Réunion** en application de recherche utilisable via une interface web.

Le système doit être :

- pilotable ;
- traçable ;
- reproductible ;
- visuel ;
- extensible ;
- compatible avec 1000G puis avec les données EGA/DAC autorisées.

## 2. Principe d’architecture

```text
web/                → interface web (Flask + vanilla)
src/core/           → logique scientifique
src/external/       → wrappers des outils externes
src/jobs/           → création, suivi et exécution locale des jobs
src/orchestration/  → moteur de pipeline
src/database/       → modèles SQLAlchemy
src/services/       → couche applicative
src/storage/        → gestion des chemins et fichiers
src/parsers/        → import des sorties outils
src/reporting/      → génération de rapports
config/             → fichiers YAML de configuration
scripts/            → commandes utilitaires
data/               → données locales hors GitHub
work/               → fichiers intermédiaires
results/            → tableaux / figures / métriques
reports/            → rapports finaux
logs/               → logs applicatifs et pipeline
```

## 3. Règle centrale

La base de données ne stocke pas les génotypes complets. Elle stocke uniquement les projets, datasets, métadonnées, chemins, statuts, métriques résumées et résultats utilisables par l’interface.

## 4. Tables prévues

V1 minimale :

```text
projects
datasets
files
pipeline_runs
pipeline_steps
qc_metrics
reports
```

Tables évolutives :

```text
samples
pca_results
admixture_runs
admixture_proportions
kinship_pairs
roh_segments
selection_strategies
selected_samples
imputation_metrics
```

## 5. Déroulé d’un run

MVP local retenu :

```text
1. L’utilisateur choisit un dataset, un profil et une stratégie dans l'interface web.
2. L'interface web valide les paramètres.
3. L'interface web appelle JobManager.create_job().
4. Un dossier work/runs/<run_id>/ est créé.
5. config.yaml, manifest.json et status.json sont figés.
6. Le worker exécute scripts/run_worker.py avec subprocess.Popen(..., shell=False).
7. Le worker exécute les étapes autorisées.
8. Les logs, statuts et sorties sont écrits dans le dossier du run.
9. L’interface relit status.json et pipeline.log pour afficher progression, résultats ou erreur.
```

Évolution serveur possible : le même modèle de job pourra être branché sur SQLAlchemy, Celery/RQ, Redis, Nextflow/Snakemake ou un cluster.

La règle centrale reste inchangée : l’interface déclenche l’analyse, mais ne construit jamais de commande shell libre.

## 6. Image de référence

![Interface de référence](../web/static/img/interface_reference.png)

## 7. Positionnement

Cette interface est une interface de recherche interne, pas un outil clinique, pas un dispositif médical, pas un SaaS commercial finalisé.
