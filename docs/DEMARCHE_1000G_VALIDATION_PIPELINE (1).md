# Démarche 1000 Genomes pour la validation du pipeline Génome Réunion

**Projet :** Génome Réunion  
**Objet :** démarrage de la validation méthodologique et du pipeline informatique avec les données publiques 1000 Genomes / IGSR  
**Statut :** version de travail pour création d’un futur dépôt GitHub  
**Date :** 2026-06-11

---

## 1. Positionnement scientifique

L’objectif est de démarrer immédiatement la mise au point du pipeline informatique sans attendre les autorisations EGA/DAC.

Les données **1000 Genomes high-coverage / IGSR** doivent être utilisées comme :

- ressource publique de démarrage ;
- jeu de test reproductible ;
- support de développement des scripts internes ;
- support de validation technique des étapes PCA, ADMIXTURE, KING/IBD, ROH, imputation et sélection WGS ;
- sanity-check méthodologique ;
- base pour simuler une situation “puce SNP → WGS complet”.

Elles ne remplacent pas les futurs panels EGA prioritaires, notamment les panels plus proches de l’histoire réunionnaise : Madagascar, océan Indien, Afrique de l’Est / Afrique australe, Inde, Asie du Sud-Est, populations admixées continues.

Dans le protocole de validation, 1000G doit donc être présenté comme un **socle public de validation technique et de non-régression**, tandis que les panels EGA serviront ensuite à tester la transférabilité sur des populations plus proches ou plus complexes.

---

## 2. Sources de données 1000G à récupérer

### 2.1 Page officielle IGSR

```text
https://www.internationalgenome.org/data-portal/data-collection/1000genomes_30x
```

### 2.2 Répertoire FTP officiel high-coverage

```text
https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/
```

### 2.3 Panel phasé SNV / INDEL / SV recommandé pour le pipeline

```text
https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20220422_3202_phased_SNV_INDEL_SV/
```

Fichiers autosomiques :

```text
1kGP_high_coverage_Illumina.chr1.filtered.SNV_INDEL_SV_phased_panel.vcf.gz
1kGP_high_coverage_Illumina.chr1.filtered.SNV_INDEL_SV_phased_panel.vcf.gz.tbi
...
1kGP_high_coverage_Illumina.chr22.filtered.SNV_INDEL_SV_phased_panel.vcf.gz
1kGP_high_coverage_Illumina.chr22.filtered.SNV_INDEL_SV_phased_panel.vcf.gz.tbi
```

Patron d’URL :

```bash
BASE_URL="https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20220422_3202_phased_SNV_INDEL_SV"
CHR=22
VCF="${BASE_URL}/1kGP_high_coverage_Illumina.chr${CHR}.filtered.SNV_INDEL_SV_phased_panel.vcf.gz"
TBI="${VCF}.tbi"
```

Chromosome X :

```text
1kGP_high_coverage_Illumina.chrX.filtered.SNV_INDEL_SV_phased_panel.v2.vcf.gz
1kGP_high_coverage_Illumina.chrX.filtered.SNV_INDEL_SV_phased_panel.v2.vcf.gz.tbi
```

Remarque : pour la première version du pipeline, il est préférable de commencer par **chr22 uniquement**, puis d’élargir aux autosomes 1–22 après validation des scripts.

### 2.4 Manifest MD5

```text
https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20220422_3202_phased_SNV_INDEL_SV/20220804_manifest.txt
```

### 2.5 Métadonnées échantillons / pedigree

```text
https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/1kGP.3202_samples.pedigree_info.txt
```

### 2.6 README du panel

```text
https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20220422_3202_phased_SNV_INDEL_SV/README_1kGP_phased_panel_110722.pdf
```

---

## 3. Stratégie de récupération des données

### 3.1 Principe

Ne jamais versionner les données brutes dans GitHub.

Le dépôt GitHub doit contenir :

- le code ;
- les scripts de téléchargement ;
- les fichiers de configuration ;
- les modèles de rapports ;
- les tests unitaires ;
- la documentation ;
- éventuellement de très petits fichiers jouets anonymes.

Les données VCF, PLINK, BGEN, PGEN, résultats lourds et logs volumineux doivent rester hors Git.

### 3.2 Arborescence locale des données

```text
data/
├── raw/
│   └── 1000g/
│       ├── vcf/
│       ├── tbi/
│       ├── metadata/
│       └── manifest/
├── interim/
│   ├── plink/
│   ├── filtered_vcf/
│   └── chip_masked/
├── processed/
│   ├── pca/
│   ├── admixture/
│   ├── king/
│   ├── roh/
│   ├── selections/
│   └── evaluation/
└── external/
    └── ega_pending/
```

---

## 4. Commandes minimales de démarrage

### 4.1 Télécharger chr22 pour prototype

```bash
mkdir -p data/raw/1000g/vcf
mkdir -p data/raw/1000g/metadata
mkdir -p data/raw/1000g/manifest

BASE_URL="https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working"
PANEL_URL="${BASE_URL}/20220422_3202_phased_SNV_INDEL_SV"
CHR=22

wget -c "${PANEL_URL}/1kGP_high_coverage_Illumina.chr${CHR}.filtered.SNV_INDEL_SV_phased_panel.vcf.gz" \
  -O "data/raw/1000g/vcf/chr${CHR}.vcf.gz"

wget -c "${PANEL_URL}/1kGP_high_coverage_Illumina.chr${CHR}.filtered.SNV_INDEL_SV_phased_panel.vcf.gz.tbi" \
  -O "data/raw/1000g/vcf/chr${CHR}.vcf.gz.tbi"

wget -c "${PANEL_URL}/20220804_manifest.txt" \
  -O "data/raw/1000g/manifest/20220804_manifest.txt"

wget -c "${BASE_URL}/1kGP.3202_samples.pedigree_info.txt" \
  -O "data/raw/1000g/metadata/1kGP.3202_samples.pedigree_info.txt"
```

### 4.2 Contrôle rapide VCF

```bash
bcftools index -t data/raw/1000g/vcf/chr22.vcf.gz
bcftools view -h data/raw/1000g/vcf/chr22.vcf.gz | head
bcftools query -l data/raw/1000g/vcf/chr22.vcf.gz | head
```

### 4.3 Extraire une région test

```bash
mkdir -p data/interim/filtered_vcf

bcftools view \
  -r 22:20000000-22000000 \
  data/raw/1000g/vcf/chr22.vcf.gz \
  -Oz \
  -o data/interim/filtered_vcf/chr22.region_test.vcf.gz

tabix -p vcf data/interim/filtered_vcf/chr22.region_test.vcf.gz
```

### 4.4 Conversion vers PLINK 2

```bash
mkdir -p data/interim/plink

plink2 \
  --vcf data/interim/filtered_vcf/chr22.region_test.vcf.gz \
  --make-pgen \
  --out data/interim/plink/chr22_region_test
```

---

## 5. Outils bioinformatiques à installer

### 5.1 Outils système

```text
bcftools
htslib / tabix
plink2
plink 1.9
KING
ADMIXTURE
beagle 5.4 ou GLIMPSE2, optionnel pour la suite
```

### 5.2 Librairies Python

```text
pandas
numpy
scipy
scikit-learn
pyyaml
matplotlib
plotly
jinja2
click
rich
pytest
```

---

## 6. Structure proposée du futur dépôt GitHub

Nom proposé :

```text
genome-reunion-validation-pipeline
```

Structure :

```text
genome-reunion-validation-pipeline/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── config/
│   ├── validation.yaml
│   ├── tools.yaml
│   ├── panels_1000g.yaml
│   └── strategies.yaml
├── docs/
│   ├── DEMARCHE_1000G_VALIDATION_PIPELINE.md
│   ├── DATA_ACCESS.md
│   ├── PIPELINE_SPECIFICATION.md
│   └── DECISION_RULES.md
├── scripts/
│   ├── download_1000g_chr22.sh
│   ├── download_1000g_autosomes.sh
│   ├── run_mvp_chr22.sh
│   └── check_tools.sh
├── src/
│   └── genorun_validation/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── runner.py
│       ├── download.py
│       ├── metadata.py
│       ├── qc.py
│       ├── convert.py
│       ├── pca.py
│       ├── admixture.py
│       ├── kinship.py
│       ├── roh.py
│       ├── chip_mask.py
│       ├── scores.py
│       ├── selection.py
│       ├── evaluation.py
│       ├── report.py
│       └── utils.py
├── tests/
│   ├── test_config.py
│   ├── test_scores.py
│   ├── test_selection.py
│   └── test_metadata.py
├── notebooks/
│   └── 00_exploration_chr22.ipynb
├── results/
│   ├── tables/
│   ├── figures/
│   └── reports/
└── data/
    ├── raw/
    ├── interim/
    ├── processed/
    └── external/
```

---

## 7. Architecture fonctionnelle du pipeline

### 7.1 Étape A — Inventaire des panels

Modules :

```text
src/genorun_validation/download.py
src/genorun_validation/metadata.py
```

Livrables :

```text
results/tables/reference_panel_inventory.tsv
results/tables/sample_metadata_1000g.tsv
```

Objectifs :

- télécharger ou pointer les fichiers 1000G ;
- vérifier l’existence des fichiers VCF/TBI ;
- charger les métadonnées ;
- identifier les populations d’intérêt ;
- documenter la version des données.

### 7.2 Étape B — Prétraitement VCF

Modules :

```text
src/genorun_validation/qc.py
src/genorun_validation/convert.py
```

Objectifs :

- filtrer autosomes ;
- conserver SNV bialléliques pour PCA/ADMIXTURE ;
- retirer variants ambigus A/T et C/G si nécessaire ;
- filtrer missingness ;
- filtrer MAF selon analyse ;
- convertir VCF vers PGEN ou BED.

Exemple PLINK 2 :

```bash
plink2 \
  --vcf data/raw/1000g/vcf/chr22.vcf.gz \
  --snps-only just-acgt \
  --max-alleles 2 \
  --geno 0.05 \
  --maf 0.01 \
  --make-pgen \
  --out data/interim/plink/chr22.qc
```

### 7.3 Étape C — LD pruning

```bash
plink2 \
  --pfile data/interim/plink/chr22.qc \
  --indep-pairwise 200 50 0.2 \
  --out data/interim/plink/chr22.prune

plink2 \
  --pfile data/interim/plink/chr22.qc \
  --extract data/interim/plink/chr22.prune.prune.in \
  --make-pgen \
  --out data/interim/plink/chr22.pruned
```

### 7.4 Étape D — PCA

Module :

```text
src/genorun_validation/pca.py
```

Commande :

```bash
plink2 \
  --pfile data/interim/plink/chr22.pruned \
  --pca 20 approx \
  --out data/processed/pca/chr22
```

### 7.5 Étape E — ADMIXTURE

Module :

```text
src/genorun_validation/admixture.py
```

Principe : tester K = 3 à 10, lancer plusieurs seeds, conserver le CV-error, produire Q/P matrices et documenter le label switching.

```bash
plink2 \
  --pfile data/interim/plink/chr22.pruned \
  --make-bed \
  --out data/interim/plink/chr22.pruned_bed

for K in 3 4 5 6 7 8 9 10
do
  admixture --cv data/interim/plink/chr22.pruned_bed.bed ${K} \
    | tee results/tables/admixture_chr22_K${K}.log
done
```

### 7.6 Étape F — KING / IBD

Module :

```text
src/genorun_validation/kinship.py
```

Option PLINK 2 :

```bash
plink2 \
  --pfile data/interim/plink/chr22.pruned \
  --make-king-table \
  --out data/processed/king/chr22
```

### 7.7 Étape G — ROH

Module :

```text
src/genorun_validation/roh.py
```

Commande indicative :

```bash
plink \
  --bfile data/interim/plink/chr22.pruned_bed \
  --homozyg \
  --homozyg-kb 1000 \
  --homozyg-snp 50 \
  --out data/processed/roh/chr22
```

### 7.8 Étape H — Simulation puce SNP

Module :

```text
src/genorun_validation/chip_mask.py
```

Objectif : simuler une puce SNP à partir du WGS 1000G, conserver uniquement les SNP présents dans une liste de puce cible, puis comparer sélection sur version “puce” et performance mesurée sur WGS complet.

Livrable :

```text
results/tables/chip_to_wgs_audit.tsv
```

### 7.9 Étape I — Score S_div

Module :

```text
src/genorun_validation/scores.py
```

Formule de départ :

```text
S_div = 0.30 × PCA_score
      + 0.30 × ADMIX_score
      + 0.25 × IBD_score
      + 0.15 × ROH_score
```

Important : les poids sont des valeurs initiales. Ils devront être testés par analyse de sensibilité.

### 7.10 Étape J — Sélection WGS simulée

Module :

```text
src/genorun_validation/selection.py
```

Stratégies à comparer :

```text
random
population_stratified
pca_maximin
admixture_maximin
sdiv_global
sdiv_geoancestry_proxy
hybrid_discovery
```

Dans 1000G, l’équivalent d’un secteur géographique réunionnais peut être simulé par :

```text
population 1000G × cluster ADMIXTURE
```

Limite : cette structure est artificiellement plus nette que La Réunion.

### 7.11 Étape K — Évaluation

Module :

```text
src/genorun_validation/evaluation.py
```

Métriques :

```text
- couverture de diversité PCA ;
- couverture des composantes ADMIXTURE ;
- nombre de variants observés dans la sélection ;
- proportion de variants rares captés ;
- stabilité multi-seed ;
- non-régression contre random ;
- concordance sélection puce vs sélection WGS complet ;
- performance par population 1000G ;
- audit de sensibilité des poids.
```

### 7.12 Étape L — Rapport

Module :

```text
src/genorun_validation/report.py
```

Livrables :

```text
results/reports/validation_chr22_mvp.html
results/reports/validation_chr22_mvp.md
results/tables/selection_comparison.tsv
results/tables/metrics_summary.tsv
results/figures/pca_selection_overlay.png
results/figures/admixture_barplot.png
```

---

## 8. Configuration YAML initiale

Fichier :

```text
config/validation.yaml
```

```yaml
project:
  name: genome-reunion-validation-pipeline
  version: 0.1.0
  reference_build: GRCh38

data:
  source: 1000G_high_coverage_IGSR
  start_mode: chr22_mvp
  chromosomes: [22]
  raw_dir: data/raw/1000g/vcf
  metadata_dir: data/raw/1000g/metadata

download:
  base_url: "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working"
  panel_url: "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20220422_3202_phased_SNV_INDEL_SV"
  autosome_pattern: "1kGP_high_coverage_Illumina.chr{chr}.filtered.SNV_INDEL_SV_phased_panel.vcf.gz"
  chrX_file: "1kGP_high_coverage_Illumina.chrX.filtered.SNV_INDEL_SV_phased_panel.v2.vcf.gz"
  pedigree_file: "1kGP.3202_samples.pedigree_info.txt"
  manifest_file: "20220804_manifest.txt"

qc:
  snps_only: true
  biallelic_only: true
  geno: 0.05
  maf: 0.01
  hwe: 1e-6
  remove_ambiguous_snps: true
  ld_pruning:
    window_kb: 200
    step: 50
    r2: 0.2

pca:
  n_components: 20
  approx: true

admixture:
  k_min: 3
  k_max: 10
  seeds: [42, 101, 202, 303, 404]

selection:
  n_select: 350
  strategies:
    - random
    - population_stratified
    - pca_maximin
    - admixture_maximin
    - sdiv_global
    - sdiv_geoancestry_proxy
  sdiv_weights:
    pca: 0.30
    admixture: 0.30
    ibd: 0.25
    roh: 0.15

evaluation:
  random_replicates: 100
  primary_criterion: non_regression_vs_random
  chip_to_wgs_threshold: 0.05
```

---

## 9. README.md proposé

```markdown
# Genome Réunion Validation Pipeline

Pipeline de recherche pour la validation méthodologique de la sélection WGS dans le projet Génome Réunion.

## Objectif

Ce dépôt sert à développer et valider un pipeline bioinformatique interne permettant :

- le contrôle qualité de panels de référence ;
- les analyses PCA et ADMIXTURE ;
- les analyses KING/IBD et ROH ;
- le calcul du score de diversité `S_div` ;
- la comparaison de stratégies de sélection WGS ;
- l’audit puce SNP vers WGS complet ;
- la production de rapports reproductibles.

## Données de démarrage

La première version utilise les données publiques 1000 Genomes high-coverage / IGSR.

Les données brutes ne sont pas stockées dans GitHub.

## Installation

```bash
git clone https://github.com/<user>/genome-reunion-validation-pipeline.git
cd genome-reunion-validation-pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Prototype chr22

```bash
bash scripts/download_1000g_chr22.sh
bash scripts/run_mvp_chr22.sh
```
```

---

## 10. `.gitignore` proposé

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
venv/
.env

# Jupyter
.ipynb_checkpoints/

# Logs
logs/
*.log

# Data - never commit human genetic data
data/raw/
data/interim/
data/processed/
data/external/

# Genomic formats
*.vcf
*.vcf.gz
*.vcf.gz.tbi
*.bcf
*.bcf.csi
*.bed
*.bim
*.fam
*.pgen
*.pvar
*.psam
*.bgen
*.sample
*.king
*.genome
*.hom
*.hh
*.qfam
*.eigenvec
*.eigenval

# Results can be regenerated
results/tables/
results/figures/
results/reports/

# OS
.DS_Store
Thumbs.db
```

---

## 11. `requirements.txt` proposé

```text
pandas>=2.2
numpy>=1.26
scipy>=1.12
scikit-learn>=1.4
pyyaml>=6.0
matplotlib>=3.8
plotly>=5.20
jinja2>=3.1
click>=8.1
rich>=13.7
pytest>=8.0
```

---

## 12. Ordre de développement recommandé

### MVP 1 — Technique pure

```text
download_1000g_chr22.sh
↓
bcftools index/view/query
↓
plink2 conversion PGEN
↓
test Python metadata
```

### MVP 2 — PCA / ADMIXTURE

```text
QC
↓
LD pruning
↓
PCA
↓
ADMIXTURE K=3..10
↓
figures
```

### MVP 3 — Scores

```text
PCA_score
ADMIX_score
IBD_score
ROH_score
↓
S_div
↓
classement individus
```

### MVP 4 — Sélection

```text
random
population_stratified
pca_maximin
admixture_maximin
sdiv_global
sdiv_geoancestry_proxy
```

### MVP 5 — Audit puce → WGS

```text
WGS complet 1000G
↓
masquage SNP type puce
↓
calcul S_div sur version puce
↓
sélection 350
↓
évaluation sur WGS complet
↓
chip_to_wgs_audit.tsv
```

---

## 13. Commandes Git pour initialiser le dépôt

```bash
mkdir genome-reunion-validation-pipeline
cd genome-reunion-validation-pipeline

git init

mkdir -p config docs scripts src/genorun_validation tests notebooks results/tables results/figures results/reports

touch README.md .gitignore requirements.txt pyproject.toml

git add .
git commit -m "Initial structure for Genome Reunion validation pipeline"
```

Créer le dépôt GitHub, puis :

```bash
git branch -M main
git remote add origin https://github.com/<user>/genome-reunion-validation-pipeline.git
git push -u origin main
```

---

## 14. Règle de prudence

1000G est excellent pour :

```text
développement pipeline + sanity-check + reproductibilité + démarrage rapide
```

mais insuffisant seul pour :

```text
preuve finale de transférabilité vers La Réunion
```

La validation finale devra intégrer, quand les autorisations seront obtenues :

```text
EPIGEN-Brasil
MGUA / Madagascar
GenomeAsia
MAGE
Angola / Mozambique
autres panels EGA selon accès
```

---

## 15. Livrable immédiat attendu

À la fin de la première étape, le dépôt doit être capable de produire :

```text
results/tables/reference_panel_inventory.tsv
results/tables/sample_metadata_1000g.tsv
results/tables/qc_chr22_summary.tsv
results/tables/admixture_cv_errors.tsv
results/tables/sdiv_chr22.tsv
results/tables/selection_comparison_chr22.tsv
results/reports/validation_chr22_mvp.md
```

Critère de réussite MVP :

```text
Le pipeline doit tourner de bout en bout sur chr22, avec données publiques 1000G, sans intervention manuelle entre les étapes principales.
```
