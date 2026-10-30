# AI in Healthcare : orchestrateur multi-agents par secteur (mini-projet final)

Architecture multi-agents spécialisée par secteur (**santé**, mines, automobile, finance, énergie, e-Gov) avec un **agent de monitoring**, des tests automatisés (GitHub Actions), une image Docker et un déploiement sur Render. Données fictives ; aide à la décision, aucune décision médicale finale.

## Critères de validation

| Critère | Où le vérifier |
| --- | --- |
| Observabilité : Correlation ID sur chaque exécution | `python main.py` affiche « Correlation ID présent sur 27/27 » ; `tests/test_pipeline.py` |
| Tests exécutés avec succès | `python -m pytest -q` ; workflow `.github/workflows/ci.yml` |
| Gouvernance : Agent Card complète et à jour | `governance/agent_cards.json` (8 cartes) ; `tests/test_governance.py` |
| Conteneurisation et déploiement : API accessible | `Dockerfile`, `docker-compose.yml`, `render.yaml` ; `GET /api/health` |
| Incident : runbook appliqué | `docs/RUNBOOK.md`, `python scripts/simulate_incident.py` |
| Documentation technique + démo vidéo | `docs/Documentation_AI_in_Healthcare.docx`, `docs/SCENARIO_VIDEO.md` |

## Contenu

| Fichier | Rôle |
| --- | --- |
| `main.py` | lot de test (27 demandes) et `--check` (config + non-régression) |
| `app/` | `api.py` (FastAPI), `pipeline.py` (orchestrateur + monitoring), `sectors.py` (6 agents), `governance.py`, `stats.py` |
| `dashboard/index.html` | tableau de bord : http://localhost:8001 (logo, menu, formulaire, graphiques) |
| `workflow/AI_in_Healthcare_final.json` | flux multi-agents (JSON final) |
| `notebooks/analyse_executions.ipynb` | analyse des exécutions et de l'incident |
| `governance/` | version active, versions, demandes de changement, cas golden, Agent Cards, kill switch |
| `docs/` | architecture, runbook, documentation docx, présentation pptx |

## Lancer

```
pip install -r requirements-dev.txt
python main.py --check
python main.py
python -m pytest -q
python scripts/simulate_incident.py
python scripts/build_dashboard.py          # régénère le dashboard après un nouveau lot
python -m uvicorn app.api:app --port 8001  # http://localhost:8001  (docs API : /docs)
```

Docker : `cp .env.example .env` puis `docker compose up --build` (http://localhost:8001).
Lot dans Docker : `docker compose --profile batch run batch`.

## API

`GET /api/health` · `GET /api/sectors` · `POST /api/analyze` · `GET /api/executions` · `GET /api/stats` · `GET /api/agent-cards` · `GET /api/versions` · `GET /api/audit` · `POST /api/admin/kill-switch` et `/api/admin/rollback` (en-tête `X-Admin-Token`).

```
curl -X POST localhost:8001/api/analyze -H "Content-Type: application/json" \
  -d '{"secteur":"sante","entite_id":"PAT-100","indicateurs":{"spo2":85,"temperature":39.8,"frequence_cardiaque":145,"douleur":9,"comorbidites":"oui"}}'
```

## Déploiement Render

1. Pousser le dépôt sur GitHub (la CI doit être verte).
2. Render : New + → Blueprint → sélectionner le dépôt (`render.yaml`).
3. Renseigner `ADMIN_TOKEN` dans Render (jamais dans le dépôt).
4. Vérifier `https://<service>.onrender.com/api/health`.

## Limites

Latences, tokens et coûts sont **simulés** (aucun modèle appelé) ; Slack simulé ; règles de scoring pédagogiques à valider par un expert métier ; données fictives uniquement. Le JSON de workflow est un schéma simplifié, pas un export Langflow natif.
