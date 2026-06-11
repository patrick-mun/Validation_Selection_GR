#!/usr/bin/env bash
set -euo pipefail
for tool in bcftools tabix plink2 admixture king; do
  if command -v "$tool" >/dev/null 2>&1; then echo "[OK] $tool"; else echo "[MISSING] $tool"; fi
done
