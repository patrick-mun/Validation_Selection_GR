# Données 1000 Genomes

1000G sert de socle public de démarrage : développement du pipeline, sanity-check, test PCA/ADMIXTURE, test de sélection et simulation puce → WGS.

## Adresse principale IGSR / 1000 Genomes high coverage

```text
https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/
```

## Dossier VCF phasés 3202 échantillons

```text
https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/20220422_3202_phased_SNV_INDEL_SV/
```

## MVP conseillé

Commencer par le chromosome 22 :

```bash
bash scripts/download_1000g_chr22.sh
```
