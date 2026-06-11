#!/usr/bin/env bash
set -euo pipefail
mkdir -p data/interim/filtered_vcf data/interim/plink data/processed/pca results/tables results/figures results/reports
bcftools view -r 22:20000000-22000000 data/raw/1000g/vcf/chr22.vcf.gz -Oz -o data/interim/filtered_vcf/chr22.region_test.vcf.gz
tabix -p vcf data/interim/filtered_vcf/chr22.region_test.vcf.gz
plink2 --vcf data/interim/filtered_vcf/chr22.region_test.vcf.gz --snps-only just-acgt --max-alleles 2 --geno 0.05 --maf 0.01 --make-pgen --out data/interim/plink/chr22_region_test
plink2 --pfile data/interim/plink/chr22_region_test --indep-pairwise 200 50 0.2 --out data/interim/plink/chr22_region_test.prune
plink2 --pfile data/interim/plink/chr22_region_test --extract data/interim/plink/chr22_region_test.prune.prune.in --pca 20 approx --out data/processed/pca/chr22_region_test
echo "MVP chr22 terminé."
