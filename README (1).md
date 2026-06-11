# Genome Réunion Validation Pipeline

Pipeline de recherche pour la validation méthodologique de la sélection WGS dans le projet Génome Réunion.

## Objectif

Ce dépôt sert à développer et valider un pipeline bioinformatique interne pour QC, PCA, ADMIXTURE, KING/IBD, ROH, calcul S_div, comparaison de stratégies de sélection WGS et audit puce SNP vers WGS complet.

## Données de démarrage

Première version : données publiques 1000 Genomes high-coverage / IGSR. Les données brutes ne sont pas stockées dans GitHub.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Prototype chr22

```bash
bash scripts/download_1000g_chr22.sh
bash scripts/run_mvp_chr22.sh
```
