# Cartographie de la chaîne d'outils (atelier A1)

*(Copier ici la grille remplie par le binôme pendant l'atelier A1. Exemple de structure.)*

| Étape | Outil retenu | Alternative vue en atelier | Dépend de la forge ? |
|---|---|---|---|
| Versionner | Git 2.56, signature SSH | — | non |
| Collaborer | GitHub (PR, revue, squash) | GitLab, Gitea, Forgejo | oui |
| Contrôler avant commit | pre-commit + ruff | — | non |
| Intégrer (TP03) | GitHub Actions | GitLab CI, Woodpecker | oui (workflows portables sur Gitea/Forgejo) |
| Empaqueter (TP04) | Docker | Podman, buildah | non |
| Observer | Prometheus (`/metrics`) | — | non |
