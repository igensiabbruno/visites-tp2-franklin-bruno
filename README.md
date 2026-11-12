# Visites — API de comptage de visites

Application fil rouge du module Intro DevOps : une API FastAPI qui compte les visites dans Redis
et expose des métriques Prometheus.

## Endpoints
- `GET /` — incrémente et renvoie le compteur ; en-tête `X-Visites-Version`.
- `POST /reset` — remet le compteur à zéro.
- `GET /health` — `{"status": "ok"}` ou 503 si Redis est injoignable.
- `GET /metrics` — métriques Prometheus (`http_requests_total`, `http_request_duration_seconds`).

## Démarrer en local
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
docker run -d --name redis -p 6379:6379 redis:8-alpine
uvicorn app.main:app --reload
curl -s localhost:8000/
```

## Tests
```bash
pytest -q                 # unitaires (fakeredis)
pytest -m integration     # contre le Redis réel (REDIS_URL, défaut redis://localhost:6379/0)
```

## Contribuer
Voir [CONTRIBUTING.md](CONTRIBUTING.md).
