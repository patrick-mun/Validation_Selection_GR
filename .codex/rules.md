# Codex — rappel court

Lire avant toute modification :

1. `AGENTS.md`
2. `docs/CODE_INDEX.md`
3. `docs/DEV_TRACKING.md`
4. les fichiers et tests directement concernés

Règle centrale : l'interface déclenche un job, mais n'exécute pas directement de commande bioinformatique brute. Les commandes passent par `src/genorun_validation/jobs/` et `src/genorun_validation/external/` avec `shell=False`, logs, statuts et manifest.

Base de données : PostgreSQL est la cible officielle. SQLite n'est accepté que pour des tests unitaires isolés. Aucun fichier génétique lourd ne doit être stocké en base.

Docker : le projet doit rester utilisable localement, mais aussi déployable via `docker compose` avec `genorun-app`, `genorun-worker` et `genorun-db`. Ne jamais ajouter de vrai secret dans Git ; utiliser `.env`.

Règles de code :

- noms de variables explicites ;
- fonctions courtes à responsabilité unique ;
- commentaires utiles et localisables : `# WHY:`, `# SAFETY:`, `# METHOD:`, `# TODO[DEV_TRACKING]:`, `# FIXME[DEV_TRACKING]:` ;
- aucun `TODO`/`FIXME` sans entrée dans `docs/DEV_TRACKING.md` ;
- mise à jour de `docs/CODE_INDEX.md` si un fichier important bouge ;
- mise à jour de `docs/DEV_TRACKING.md` si une décision, une dette ou une erreur connue apparaît ;
- migration Alembic obligatoire si un modèle SQL change ; si la logique de file de jobs change, vérifier `JobManager.list_runnable_jobs()` et le worker Docker.

Avant toute proposition :

```bash
python -m compileall src scripts web
pytest -q
```
