# Contribuer

## Flux de travail
1. Partir de `main` à jour : `git switch main && git pull`.
2. Créer une branche courte : `git switch -c feat/<sujet>` (préfixes : feat, fix, docs, chore, ci).
3. Commits conventionnels (https://www.conventionalcommits.org/fr/v1.0.0/), signés (SSH).
4. Ouvrir une pull request ; un membre du binôme relit et approuve ; le pipeline doit être vert.
5. Fusion par squash, suppression de la branche.
6. Conflit : `git rebase origin/main`, résoudre, `git add --resolved`, `git rebase --continue`,
   `git push --force-with-lease`.

## Qualité
- `pip install -e ".[dev]"` puis `pre-commit install`.
- Tests : `pytest -q` (unitaires), `pytest -m integration` (Redis réel sur localhost:6379).
- Lint et format : `ruff check . && ruff format .` (exécutés par pre-commit).

## Versions
- SemVer. `feat` → mineure, `fix` → correctif, `!`/`BREAKING CHANGE` → majeure.
- Tag signé par un mainteneur : `git tag -s vX.Y.Z -m "…" && git push origin vX.Y.Z`.
