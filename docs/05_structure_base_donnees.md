# Structure de base de données

## Décision

PostgreSQL est la base officielle du logiciel dès la première version structurée. SQLite n'est pas la base principale du projet.

## Rôle de PostgreSQL

La base sert à indexer et auditer :

- projets ;
- cohortes ;
- échantillons anonymisés ;
- fichiers d'entrée/sortie sous forme de métadonnées ;
- jobs ;
- étapes de jobs ;
- logs courts ;
- versions logicielles ;
- métriques QC/PCA/ADMIXTURE/ROH/IBD ;
- scores de sélection ;
- sélection WGS finale ;
- rapports ;
- événements d'audit.

## Règle fichiers lourds

Les fichiers génétiques bruts ou volumineux restent hors base :

```text
.bed .bim .fam .ped .map .vcf .vcf.gz .bcf .bam .cram
```

La base conserve uniquement :

```text
chemin relatif
type de fichier
taille
checksum
statut de validation
lien avec cohorte/job
```

## Tables principales

```text
projects
cohorts
samples
input_files
analysis_jobs
analysis_steps
job_logs
software_versions
audit_events
qc_metrics
pca_results
admixture_results
roh_results
ibd_results
selection_scores
wgs_selection
reports
```

## Migrations

Les modèles sont dans :

```text
src/genorun_validation/database/models.py
```

Les migrations sont dans :

```text
alembic/
```

Toute modification du modèle doit passer par une migration Alembic et être notée dans `docs/DEV_TRACKING.md`.
