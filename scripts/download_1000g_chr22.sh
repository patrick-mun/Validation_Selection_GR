#!/usr/bin/env bash
set -euo pipefail
mkdir -p data/raw/1000g/vcf data/raw/1000g/metadata data/raw/1000g/manifest
BASE_URL="https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working"
PANEL_URL="${BASE_URL}/20220422_3202_phased_SNV_INDEL_SV"
CHR=22
wget -c "${PANEL_URL}/1kGP_high_coverage_Illumina.chr${CHR}.filtered.SNV_INDEL_SV_phased_panel.vcf.gz" -O "data/raw/1000g/vcf/chr${CHR}.vcf.gz"
wget -c "${PANEL_URL}/1kGP_high_coverage_Illumina.chr${CHR}.filtered.SNV_INDEL_SV_phased_panel.vcf.gz.tbi" -O "data/raw/1000g/vcf/chr${CHR}.vcf.gz.tbi"
wget -c "${PANEL_URL}/20220804_manifest.txt" -O "data/raw/1000g/manifest/20220804_manifest.txt"
wget -c "${BASE_URL}/1kGP.3202_samples.pedigree_info.txt" -O "data/raw/1000g/metadata/1kGP.3202_samples.pedigree_info.txt"
