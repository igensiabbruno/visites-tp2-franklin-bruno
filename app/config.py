# Étape 4 : version de app/config.py à committer pour déclencher le hook gitleaks (règle aws-secret-key).
# Clé d'exemple de la documentation AWS : valeur fictive, 40 caractères.
import os
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    redis_url: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


settings = Settings()
