# Architecture d'exécution locale — Interface, jobs et worker

## Décision validée

L'interface doit permettre à l'utilisateur de lancer les analyses. Le bouton **Lancer l'analyse** reste donc le point d'entrée principal.

La contrainte d'architecture est différente : l'interface ne doit pas exécuter directement des commandes shell bioinformatiques libres ou bloquantes. Elle crée une demande d'analyse, appelée **job**, puis délègue son exécution à un worker local.

## Flux cible

```text
Utilisateur
  ↓ clic "Lancer l'analyse"
Interface web (Flask + vanilla)
  ↓ validation dataset / profil / stratégie
Job Manager local
  ↓ création work/runs/<run_id>/
  ├── config.yaml
  ├── manifest.json
  ├── status.json
  ├── logs/pipeline.log
  ├── outputs/
  └── report/
Worker local
  ↓ exécution contrôlée des étapes
Pipeline bioinformatique
  ↓
Résultats affichés dans l'interface
```

## Rôle de chaque couche

### Interface

L'interface :

- collecte les paramètres utilisateur ;
- les valide ;
- crée un job ;
- démarre un worker local ;
- affiche le statut, les logs, les résultats ou les erreurs.

Elle ne doit pas contenir de logique PLINK, KING, ADMIXTURE, ROH ou imputation.

### Job Manager

Le Job Manager :

- attribue un identifiant unique ;
- crée le dossier de run ;
- écrit la configuration figée ;
- écrit le manifest d'audit ;
- maintient `status.json` ;
- centralise les chemins de logs et sorties.

### Worker

Le worker :

- lit le job ;
- exécute les étapes autorisées ;
- met à jour les statuts ;
- écrit les logs ;
- arrête proprement le pipeline en cas d'erreur ;
- prépare les fichiers nécessaires à l'interface et au rapport.

## Statuts standard

```text
created   : job créé, pas encore lancé
queued    : job prêt à être exécuté
running   : analyse en cours
failed    : analyse interrompue avec erreur
completed : analyse terminée avec succès
cancelled : analyse annulée manuellement
```

## Sécurité

Les commandes externes doivent être construites sous forme de listes d'arguments :

```python
["plink", "--bfile", "input", "--geno", "0.02", "--make-bed", "--out", "output"]
```

Interdit :

```python
"plink --bfile " + user_input + " --make-bed"
```

Le worker doit utiliser `subprocess.run(..., shell=False)` ou équivalent.

## MVP retenu

Pour une première version locale :

```text
Interface web (Flask)
  → Job Manager fichiers JSON
  → Worker Python local
  → subprocess sécurisé
  → logs texte
  → outputs structurés
```

La base SQL pourra ensuite reprendre les mêmes concepts pour un suivi multi-utilisateur ou serveur.

## Évolution possible

Quand le projet deviendra plus lourd :

```text
Flask (front vanilla)
  → API FastAPI/Django
  → Celery/RQ + Redis
  → workers bioinformatiques
  → Nextflow/Snakemake
  → serveur ou cluster
```

La logique métier ne doit pas dépendre de l'interface web afin de faciliter cette migration.
