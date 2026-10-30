"""Indicateurs, répartitions et alertes du monitoring."""
import json
from collections import Counter

from app import config

SEUIL_LATENCE_MS = 5000
SEUIL_ECHEC = 0.2
TAUX_SUCCES_MIN = 80


def charger_executions():
    chemin = config.OUTPUTS / "executions.jsonl"
    if not chemin.exists():
        return []
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


def kpi(execs):
    n = len(execs)
    if not n:
        return {"executions": 0, "taux_succes_pct": 0.0, "taux_echec_pct": 0.0, "latence_moyenne_ms": 0,
                "latence_p95_ms": 0, "tokens_total": 0, "cout_total_usd": 0.0, "escalades_hitl": 0}
    ok = sum(1 for e in execs if e["statut"] in ("Succès", "En attente de décision humaine"))
    ech = sum(1 for e in execs if e["statut"] == "Échec")
    lat = sorted(e["latence_ms"] for e in execs)
    return {
        "executions": n,
        "taux_succes_pct": round(100 * ok / n, 1),
        "taux_echec_pct": round(100 * ech / n, 1),
        "latence_moyenne_ms": round(sum(lat) / n),
        "latence_p95_ms": lat[min(n - 1, int(0.95 * n))],
        "tokens_total": sum(e["tokens_total"] for e in execs),
        "cout_total_usd": round(sum(e["cout_usd"] for e in execs), 6),
        "escalades_hitl": sum(1 for e in execs if e["route"].startswith("Escalade")),
    }


def repartition(execs, cle):
    return dict(Counter(e[cle] for e in execs if e.get(cle)))


def calculer_alertes(execs):
    alertes = []
    for e in execs:
        if e["latence_ms"] > SEUIL_LATENCE_MS:
            alertes.append({"date_heure": e["date_heure"], "type": "Latence élevée",
                            "correlation_id": e["correlation_id"], "valeur": e["latence_ms"],
                            "seuil": SEUIL_LATENCE_MS, "action": "Surveiller le secteur " + e["secteur"]})
    k = kpi(execs)
    if execs and k["taux_echec_pct"] / 100 > SEUIL_ECHEC:
        alertes.append({"date_heure": execs[-1]["date_heure"], "type": "Taux d'échec", "correlation_id": "-",
                        "valeur": k["taux_echec_pct"], "seuil": SEUIL_ECHEC * 100, "action": "Appliquer le runbook"})
    return alertes
