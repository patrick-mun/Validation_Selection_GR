#!/usr/bin/env bash
set -euo pipefail
BASE_URL="https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working"
OUT_DIR="data/metadata/1000G"
mkdir -p "${OUT_DIR}"
wget -c -P "${OUT_DIR}" "${BASE_URL}/1kGP.3202_samples.pedigree_info.txt"
echo "Métadonnées 1000G téléchargées."
