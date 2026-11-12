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

## TP 03 — Premier pipeline d'intégration continue

### 1. Mesures du pipeline et cache `pip`
* **Référence (avant matrice, sans cache, Python 3.13) :** `53s`
* **Avec matrice `["3.12", "3.13"]` et `cache: "pip"` :**
  * **1re exécution (`cache miss`, run `43226469105`) :** `test (py3.12)` en **49s**, `test (py3.13)` en **49s** (total : `53s` en parallèle).
  * **2e exécution (`cache hit` — `Cache restored`, rerun `43226469105`) :** `test (py3.12)` en **1m01s**, `test (py3.13)` en **1m00s**.
  * **Analyse :** le cache `pip` est restauré en ~1s (clé calculée sur `pyproject.toml` + OS + version Python), mais la majorité du temps (~35–40s) provient de l'installation des environnements isolés `pre-commit` (`ruff`, `gitleaks`), qui ne sont pas mis en cache par `setup-python`.
* **Checks requis dans le ruleset (`27099639`) :** `test (py3.12)` et `test (py3.13)` (PR #13 bloquée sur échec `test_version_header`, puis débloquée par commit correctif).

### 2. Exécution locale avec `act`
* **Configuration :** `~/.actrc` avec l'image Medium `catthehacker/ubuntu:act-latest` (`--container-architecture linux/amd64`), montage du bundle CA du proxy dans le conteneur.
* **Comportement :** `checkout`, `setup-python`, `pip install`, `pre-commit`, `ruff` et `pytest` réussissent comme sur GitHub.
* **Échecs/limites en local :**
  * `actions/upload-artifact@v4` échoue (`Unable to get the ACTIONS_RUNTIME_TOKEN env variable`) car il n'y a pas de serveur d'artefacts GitHub Actions en local (sauf en passant `--artifact-server-path`).
  * Le cache cloud `setup-python` (`cache: "pip"`) n'est pas persisté entre conteneurs éphémères sans serveur de cache local.

### 3. Questions d'observation
* **Pourquoi le workflow se déclenche sur la PR avant d'être sur `main` ?** GitHub Actions lit le fichier `.github/workflows/ci.yml` depuis le commit de fusion virtuel (*merge commit*) de la branche source de la PR.
* **Couverture : faut-il échouer sous un seuil ? Pourquoi pas 100 % ?** Oui via `--cov-fail-under` (ex. **80 %** pour bloquer les régressions majeures sans freiner le développement). Viser **100 %** pousse à écrire des tests artificiels sur du code trivial ou défensif au lieu de tester les vrais cas limites métiers.
* **Matrice : combien de checks apparaissent et lesquels exiger dans le ruleset ?** **2 checks** (`test (py3.12)` et `test (py3.13)`). Il faut exiger **les deux** dans le ruleset pour garantir la compatibilité sur toutes les versions supportées.
* **Que se passe-t-il si un admin coche « bypass » ? Qui doit l'avoir et comment est-ce tracé ?** La PR peut être fusionnée malgré un check rouge ou l'absence de revue. Ce droit doit être réservé aux **administrateurs/leads** en cas d'urgence uniquement, et il est enregistré dans l'**Audit Log** de l'organisation/dépôt ainsi que sur la PR.
* **act remplace-t-il GitHub Actions ? Quand est-il indispensable ?** **Non**, il ne reproduit ni les règles de protection, ni les secrets/permissions cloud, ni les environnements managés complets. Il est indispensable pour **déboguer rapidement un workflow complexe en local** sans polluer l'historique de commits/PR, ou pour tester sur **runner auto-hébergé / environnement restreint**.
* **Q1 — Durée et étape la plus coûteuse :** ~50–60s par job ; l'installation des dépendances et surtout l'initialisation des hooks `pre-commit` prennent la majorité du temps (le test `pytest` lui-même dure < 1s).
* **Q2 — Qu'est-ce qui empêche un membre de contourner le pipeline ?** Le **ruleset** sur `main` (PR obligatoire + `required_status_checks` + suppression des droits de bypass).
* **Q3 — Adaptations pour GitLab CI ou Gitea Actions :** pour **Gitea Actions**, quasi aucun changement (syntaxe compatible dans `.gitea/workflows/`) ; pour **GitLab CI**, réécriture complète en `.gitlab-ci.yml` (`stages`, `image`, `cache`, `artifacts`, `parallel:matrix`), en conservant exactement les mêmes étapes.
