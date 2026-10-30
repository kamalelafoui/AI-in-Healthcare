# Scénario de la démo vidéo (5 min)

1. (0:00) Contexte : énoncé, 6 secteurs, agent de monitoring, critères de validation.
2. (0:30) Architecture : `docs/architecture.png`.
3. (1:00) Terminal : `python main.py --check` puis `python main.py` : montrer « Correlation ID présent sur 27/27 ».
4. (1:45) `python -m pytest -q` : tests verts ; onglet GitHub Actions vert.
5. (2:15) Dashboard `localhost:8001` : vue d'ensemble, formulaire santé (cas critique → escalade HITL, Correlation ID affiché), journal d'exécutions.
6. (3:00) Gouvernance : Agent Cards, version active, journal d'audit.
7. (3:20) Incident : `python scripts/simulate_incident.py` ; kill switch → rollback → redéploiement refusé par golden.
8. (4:20) Docker et Render : `docker compose up`, puis URL Render `/api/health`.
9. (4:45) Limites et suites.
