# Sécurité des données et de l'exécution

## Données génétiques

Les données génétiques réelles ne doivent jamais être versionnées dans Git. Sont exclues :

- VCF / BCF ;
- fichiers PLINK `.bed/.bim/.fam/.ped/.map/.pgen/.pvar/.psam` ;
- BAM / CRAM ;
- bases SQLite locales ;
- logs et résultats générés.

La base SQL ne doit conserver que des métadonnées, chemins contrôlés, checksums, métriques, statuts et rapports.

## Exécution des commandes

Toute commande externe doit passer par un wrapper sécurisé.

Règle obligatoire :

```python
subprocess.run(["plink", "--bfile", "input", "--make-bed", "--out", "output"], shell=False)
```

Interdit :

```python
subprocess.run("plink --bfile " + user_input, shell=True)
```

## Interface

L'interface peut lancer une analyse, mais uniquement via la création d'un job et le démarrage d'un worker local.

## Audit minimal d'un run

Chaque run doit produire :

- `config.yaml` ;
- `manifest.json` ;
- `status.json` ;
- `logs/pipeline.log` ;
- un dossier `outputs/` ;
- un dossier `report/`.

## Données simulées

Toute sortie de démonstration doit être explicitement marquée comme `dry_run`, `demo` ou `simulation`.
