#!/usr/bin/env bash
set -euo pipefail
TOOLS=(bcftools tabix plink plink2 admixture king beagle shapeit4)
for tool in "${TOOLS[@]}"; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "[OK] $tool"
  else
    echo "[MISSING] $tool"
  fi
done
