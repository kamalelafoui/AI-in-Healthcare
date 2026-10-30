"""Orchestrateur multi-agents + agent de monitoring (Correlation ID sur chaque exécution)."""
import json
import time
import uuid
from datetime import datetime
from pathlib import Path

from app import config, governance, sectors

PRIX_TOKEN_USD = 0.5 / 1_000_000  # tarif indicatif


def horodatage():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def nouveau_correlation_id():
    return f"CID-{uuid.uuid4().hex[:10]}"


class AgentMonitoring:
    """Trace chaque étape d'une exécution sous un même Correlation ID."""

    def __init__(self, correlation_id):
        self.correlation_id = correlation_id
        self.evenements = []

    def trace(self, etape, composant, statut, duree_ms, tokens=0, detail=""):
        self.evenements.append({
            "horodatage": horodatage(), "correlation_id": self.correlation_id,
            "etape": etape, "composant": composant, "statut": statut,
            "duree_ms": round(duree_ms, 1), "tokens": tokens,
            "cout_usd": round(tokens * PRIX_TOKEN_USD, 8), "detail": detail,
        })


def _latence_simulee(rng):
    duree = rng.randint(250, 700)
    if rng.random() < 0.12:
        duree += 4700  # pic de latence simulé
    return duree


def executer(secteur, entite_id, entree, cfg, rng, correlation_id=None):
    """Traite une demande. Retourne (résultat, événements de monitoring)."""
    cid = correlation_id or nouveau_correlation_id()
    mon = AgentMonitoring(cid)
    secteur_cfg = sectors.SECTEURS.get(secteur)
    res = {
        "correlation_id": cid, "date_heure": horodatage(), "version_agent": cfg["version"],
        "secteur": secteur, "agent": secteur_cfg["agent"] if secteur_cfg else "(inconnu)",
        "entite_id": entite_id, "score": "", "categorie": "", "route": "",
        "statut": "", "latence_ms": 0, "tokens_total": 0, "cout_usd": 0.0,
    }

    def fin():
        res["latence_ms"] = round(sum(e["duree_ms"] for e in mon.evenements))
        res["tokens_total"] = sum(e["tokens"] for e in mon.evenements)
        res["cout_usd"] = round(sum(e["cout_usd"] for e in mon.evenements), 8)
        return res, mon.evenements

    if governance.kill_switch_actif():
        mon.trace("garde-fou", "Kill switch", "ACTIF", 0, detail="traitement suspendu")
        res.update(route="Revue manuelle", statut="Suspendu (kill switch)")
        return fin()

    mon.trace("routage", "Orchestrateur", "OK", 2, detail=f"secteur={secteur}")
    t0 = time.perf_counter()
    try:
        score, detail = sectors.calculer_score(secteur, entree)
    except ValueError as erreur:
        mon.trace("scoring", secteur_cfg["agent"] if secteur_cfg else "Orchestrateur", "ÉCHEC",
                  (time.perf_counter() - t0) * 1000, detail=str(erreur))
        res.update(route="Revue manuelle", statut="Échec")
        return fin()

    duree = _latence_simulee(rng)
    tokens = 180 + len(json.dumps(entree)) // 4
    mon.trace("scoring", secteur_cfg["agent"], "OK", duree, tokens, detail=f"score={score}")
    categorie = sectors.categoriser(score, cfg["seuil_hitl"])
    res.update(score=score, categorie=categorie)
    if categorie == "Risque élevé":
        res.update(route="Escalade HITL (Slack simulé)", statut="En attente de décision humaine")
        mon.trace("escalade", "Notification Slack (simulée)", "SIMULÉ", rng.randint(80, 200),
                  detail="aucune donnée personnelle transmise")
    else:
        res.update(route="Sortie automatique", statut="Succès")
    return fin()


def persister(resultat, evenements):
    config.OUTPUTS.mkdir(parents=True, exist_ok=True)
    config.LOGS.mkdir(parents=True, exist_ok=True)
    with open(config.OUTPUTS / "executions.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(resultat, ensure_ascii=False) + "\n")
    with open(config.LOGS / "execution_log.jsonl", "a", encoding="utf-8") as f:
        for e in evenements:
            f.write(json.dumps({**e, "version_agent": resultat["version_agent"]}, ensure_ascii=False) + "\n")


def reinitialiser():
    for chemin in (config.OUTPUTS / "executions.jsonl", config.LOGS / "execution_log.jsonl"):
        Path(chemin).unlink(missing_ok=True)


def charger_lot(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)
