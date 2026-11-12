# Journal du binôme

## TP01
- Délai de changement observé : premier commit 14 h 12, fusion 14 h 41 (29 min).
- Indépendant de GitHub : configuration Git, signature SSH, branches, rebase, pre-commit,
  commits conventionnels. Dépendant : commandes `gh`, règles de protection, interface de PR.
- Signer les commits : l'auteur d'un commit est une chaîne libre ; la forge vérifie qui *pousse*,
  pas qui a *écrit*. Un miroir ou une migration perd l'information de push ; la signature suit le commit.
- Ce qui a pris le plus de temps : …

## TP02
- Secret trouvé par `gitleaks git --verbose --redact .` : règle `github-pat`, fichier
  `app/old_settings.py` ligne 2, commit `<sha>` (« chore: paramètres temporaires »),
  auteur Formateur <formateur@exemple.fr>, date `<date>`. Retiré au commit suivant, donc
  absent de l'arborescence mais présent dans l'historique.
- Rotation : un vrai jeton GitHub aurait été révoqué dans Settings → Developer settings →
  Personal access tokens, recréé avec le moindre privilège et stocké dans un secret de dépôt.
  Historique non réécrit (dépôt déjà partagé, secret déjà exposé) ; empreinte ajoutée à `.gitleaksignore`.
- Q1. Règles qui auraient bloqué le secret : revue obligatoire (humaine) ; gitleaks en pre-commit,
  gitleaks en CI comme contrôle requis, push protection GitHub (automatiques). La plus fiable :
  le contrôle côté serveur (CI requise, push protection), qui ne dépend pas du poste.
- Q2. Non : pre-commit est local. Il faut `pre-commit run --all-files` (ou `gitleaks git`) dans
  le pipeline et ce check requis par le ruleset.
- Q3. Quelques secondes à quelques minutes. GitHub Secret Scanning révoque automatiquement
  certains jetons partenaires (PAT GitHub, AWS, Azure, Slack, Stripe…) et prévient l'émetteur.
