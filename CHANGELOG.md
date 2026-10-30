# Changelog (SemVer)

## v1.0.0 — version finale du mini-projet
- Orchestrateur multi-agents : 6 agents sectoriels (santé, mines, automobile, finance, énergie, e-Gov)
- Agent de monitoring : Correlation ID sur chaque exécution, KPI, alertes
- Gouvernance : 8 Agent Cards, kill switch, rollback, non-régression golden, approbation à deux rôles
- API FastAPI + tableau de bord (port 8001), Docker, GitHub Actions, déploiement Render
- Runbook d'incident testé par simulation

## v1.1.0 — retirée (CR-002)
- Seuil HITL 70 -> 90 : patients au score 70-89 non escaladés ; rollback vers 1.0.0
