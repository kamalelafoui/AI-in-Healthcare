"""API FastAPI + tableau de bord de supervision : http://localhost:8001"""
import hmac
import random
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import VERSION, config, governance, pipeline, sectors, stats

app = FastAPI(title="AI in Healthcare - Orchestrateur multi-agents", version=VERSION)
app.mount("/assets", StaticFiles(directory=config.DASHBOARD / "assets"), name="assets")


class Demande(BaseModel):
    secteur: Literal["sante", "mines", "automobile", "finance", "energie", "egov"] = "sante"
    entite_id: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    indicateurs: dict[str, float | str]


class KillSwitchEntree(BaseModel):
    actif: bool
    raison: str = Field(min_length=3, max_length=200)


class RollbackEntree(BaseModel):
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    raison: str = Field(min_length=3, max_length=200)


def verifier_admin(jeton):
    if not config.ADMIN_TOKEN:
        raise HTTPException(503, "administration désactivée (ADMIN_TOKEN non défini)")
    if not hmac.compare_digest(jeton or "", config.ADMIN_TOKEN):
        raise HTTPException(403, "jeton d'administration invalide")


@app.get("/", include_in_schema=False)
def tableau_de_bord():
    return FileResponse(config.DASHBOARD / "index.html")


@app.get("/api/health")
def sante():
    cfg = governance.config_active()
    return {"statut": "ok", "version": cfg["version"], "kill_switch": governance.kill_switch_actif(),
            "secteurs": list(sectors.SECTEURS)}


@app.get("/api/sectors")
def secteurs():
    return {k: {"nom": v["nom"], "agent": v["agent"], "id": v["id"],
                "champs": [{"champ": c[0], "libelle": c[1], "unite": c[2]} for c in v["indicateurs"]]
                + [{"champ": v["drapeau"][0], "libelle": v["drapeau"][1], "unite": "oui/non"}]}
            for k, v in sectors.SECTEURS.items()}


@app.post("/api/analyze", status_code=201)
def analyser(demande: Demande):
    cfg = governance.config_active()
    res, evts = pipeline.executer(demande.secteur, demande.entite_id, demande.indicateurs, cfg, random.Random())
    pipeline.persister(res, evts)
    if res["statut"] == "Échec":
        raise HTTPException(422, {"correlation_id": res["correlation_id"], "erreur": evts[-1]["detail"]})
    _, detail = sectors.calculer_score(demande.secteur, demande.indicateurs)
    return {**res, "detail": detail}


@app.get("/api/executions")
def executions(limite: int = Query(default=50, ge=1, le=500)):
    return stats.charger_executions()[-limite:][::-1]


@app.get("/api/stats")
def statistiques():
    cfg = governance.config_active()
    execs = stats.charger_executions()
    return {
        "version": cfg["version"], "seuil_hitl": cfg["seuil_hitl"],
        "kill_switch": governance.etat_kill_switch(),
        "kpi": stats.kpi(execs),
        "categories": stats.repartition(execs, "categorie"),
        "secteurs": stats.repartition(execs, "secteur"),
        "routes": stats.repartition(execs, "route"),
        "latences": [{"correlation_id": e["correlation_id"], "latence_ms": e["latence_ms"], "secteur": e["secteur"]}
                     for e in execs[-20:]],
        "alertes": stats.calculer_alertes(execs),
    }


@app.get("/api/agent-cards")
def agent_cards():
    cartes = governance.lire_json(config.GOV / "agent_cards.json", [])
    return {"version_active": governance.config_active()["version"], "cartes": cartes}


@app.get("/api/versions")
def versions():
    return {"active": governance.config_active(), "disponibles": governance.versions_disponibles()}


@app.get("/api/audit")
def audit(limite: int = Query(default=50, ge=1, le=500)):
    return governance.lire_audit(limite)


@app.post("/api/admin/kill-switch")
def kill_switch(entree: KillSwitchEntree, x_admin_token: str | None = Header(default=None)):
    verifier_admin(x_admin_token)
    return governance.definir_kill_switch(entree.actif, entree.raison, "api-admin")


@app.post("/api/admin/rollback")
def rollback(entree: RollbackEntree, x_admin_token: str | None = Header(default=None)):
    verifier_admin(x_admin_token)
    try:
        return governance.rollback(entree.version, "api-admin", entree.raison)
    except ValueError as erreur:
        raise HTTPException(404, str(erreur))
