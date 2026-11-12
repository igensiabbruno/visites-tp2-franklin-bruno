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

## TP 02 — Protéger le dépôt

### 1. Secret historique identifié et rotation
*(Contexte : dépôt TP02 initialisé sans l'historique du TP01 ; fuite reproduite via PR sur `app/old_settings.py` pour valider la détection et la rotation).*

* **Commits :** `9f49c5f21dc4d03aa8fc66f1eb1696afc101528a` (branche PR) / `44c50cc000b2d8dd2770be93d3a5770445eb9ae6` (`main`)
* **Auteur & Date :** Franklin BECK (`Blockburnb`), `2026-11-12`
* **Fichier & Règle :** `app/old_settings.py` (ligne 2) — règle `github-pat`
* **Décision (rotation sans réécriture d'historique) :**
  * Suppression du fichier via PR (`git rm app/old_settings.py`) plutôt qu'un `git filter-repo` risqué sur un dépôt partagé, et ajout des empreintes dans `.gitleaksignore` (`gitleaks git` retourne désormais `0`).
  * **Justification :** un secret poussé sur une forge est immédiatement compromis (clones, caches, robots). En production, la seule mesure fiable est de **révoquer le jeton côté fournisseur** et d'en générer un nouveau.

### 2. Questions d'observation

* **Pourquoi « Dismiss stale approvals » ?** Révoque les approbations dès qu'un nouveau commit est poussé sur la PR. Évite qu'un auteur fasse valider une PR propre puis ajoute du code malveillant ou un secret juste avant de fusionner.
* **CODEOWNERS : que se passe-t-il si l'unique propriétaire est absent ?** La PR reste bloquée. Il faut désigner une **équipe GitHub** (ex. `@org/team`) ou plusieurs co-propriétaires, et prévoir une *bypass list* administrateur pour les urgences.
* **Dependabot : qui approuve ses PR et pourquoi est-ce utile ?** Un **mainteneur humain** (via la règle de PR + `CODEOWNERS`). Évite de fusionner automatiquement un *breaking change*, une régression ou une dépendance compromise (*supply-chain attack*).
* **gitleaks détecte-t-il grâce au nom de variable ou à la valeur ?** **Les deux :** uniquement sur la **valeur** (regex + entropie) pour les jetons à préfixe connu (`ghp_`, `AKIA`), mais **valeur (entropie) + nom de variable** (`KEY`, `SECRET`, `TOKEN`) pour la règle `generic-api-key` (renommer `AWS_SECRET_ACCESS_KEY` en `MA_VARIABLE_TEST` laisse passer le commit).
* **Q1 — Règles empêchant le secret d'atteindre `main` (humaines vs automatiques, la plus fiable) :**
  * *Humaine :* PR obligatoire avec revue de code.
  * *Automatiques :* `gitleaks` en `pre-commit`, job `gitleaks` en CI (`Required status checks`) et GitHub Push Protection.
  * *La plus fiable :* les **contrôles automatiques côté serveur (CI obligatoire + Push Protection)**, impossibles à contourner par un développeur.
* **Q2 — `pre-commit` protège-t-il un collègue qui ne l'a pas installé ? Que faut-il ajouter ?** **Non**, c'est un contrôle purement local contournable (`--no-verify` ou hook non installé). Il faut ajouter un **job `gitleaks` dans le pipeline CI** en tant que contrôle requis avant fusion.
* **Q3 — Combien de temps un secret reste-t-il privé sur un dépôt public ? Quels jetons GitHub révoque-t-il ?** **Quelques secondes** (bots scannant l'API publique GitHub en continu). **GitHub Secret Scanning** révoque automatiquement les jetons **GitHub** (`ghp_`, `github_pat_`, OAuth) et ceux de ses partenaires (AWS, GCP, Azure, Slack, Stripe, npm, PyPI, OpenAI, etc.).
