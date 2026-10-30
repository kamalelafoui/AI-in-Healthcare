# Runbook d'incident : agents « AI in Healthcare »

Objectif : réduire le temps de résolution, limiter l'impact et garantir une réponse cohérente.

## 1. Détection
Déclencheurs :
- patient à risque élevé non escaladé, ou score absent ;
- appel d'outil inattendu (notification hors escalade) ;
- KPI dégradés : taux d'échec > 20 %, latence > 5 000 ms, taux de succès < 80 %.

Contrôles :
```
python scripts/gouvernance.py statut
python main.py --check          # non-régression sur les cas golden
```
API : `GET /api/stats` (alertes), `GET /api/audit`. Chaque exécution porte un Correlation ID : le retrouver dans `logs/execution_log.jsonl`.

## 2. Contention
1. `python scripts/gouvernance.py kill-switch on --raison "<anomalie>"` ou `POST /api/admin/kill-switch` (en-tête `X-Admin-Token`).
2. Vérifier : les nouvelles demandes reçoivent « Suspendu (kill switch) » et partent en revue manuelle.
3. Prévenir le responsable clinique et le responsable technique.

## 3. Remédiation
1. Analyser `logs/execution_log.jsonl`, `logs/audit.jsonl`, `outputs/executions.jsonl` (filtrer par Correlation ID).
2. Identifier la cause (scénario : CR-002, seuil HITL 70 -> 90).
3. `python scripts/gouvernance.py rollback --vers 1.0.0 --raison "retour stable"`.
4. Vérifier : `anomalies_apres_rollback = 0` dans `outputs/incident/rapport_incident.json`.

## 4. Rétablissement
1. `python scripts/gouvernance.py kill-switch off --raison "retour à la normale"`.
2. Surveillance renforcée 48 h (taux d'échec, latence, escalades).
3. Nouvelle demande de changement, approbation à deux rôles, non-régression obligatoire.

## Retour d'expérience (scénario simulé)
| Élément | Constat |
| --- | --- |
| Cause | CR-002 relève le seuil HITL à 90 : les patients au score 70-89 ne sont plus escaladés. |
| Pourquoi ce n'était pas détecté | Aucun cas golden dans la zone 70-89. |
| Correction | Cas G3 (score 77) ajouté aux cas golden ; le redéploiement de 1.1.0 est désormais refusé. |
| Prévention | Toute modification de seuil exige validation clinique et passage de la non-régression. |

Simulation : `python scripts/simulate_incident.py` (rapport dans `outputs/incident/`).
