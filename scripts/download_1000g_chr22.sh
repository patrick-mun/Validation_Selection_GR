#!/usr/bin/env bash
set -euo pipefail
BASE_URL="https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20220422_3202_phased_SNV_INDEL_SV"
OUT_DIR="data/reference_panels/1000G_high_coverage/chr22"
mkdir -p "${OUT_DIR}"
echo "Téléchargement 1000G chr22..."
wget -c -P "${OUT_DIR}" "${BASE_URL}/1kGP_high_coverage_Illumina.chr22.filtered.SNV_INDEL_SV_phased_panel.vcf.gz"
wget -c -P "${OUT_DIR}" "${BASE_URL}/1kGP_high_coverage_Illumina.chr22.filtered.SNV_INDEL_SV_phased_panel.vcf.gz.tbi"
echo "Terminé."
