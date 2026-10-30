"""Gouvernance : version active, kill switch, rollback, non-régression, audit."""
import json
from datetime import datetime

from app import config

SEMVER_OK = lambda v: len(v.split(".")) == 3 and all(p.isdigit() for p in v.split("."))


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def lire_json(chemin, defaut=None):
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return defaut


def ecrire_json(chemin, donnees):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def config_active():
    return lire_json(config.GOV / "active_config.json")


def versions_disponibles():
    return sorted(p.stem.lstrip("v") for p in (config.GOV / "versions").glob("v*.json"))


def etat_kill_switch():
    return lire_json(config.GOV / "kill_switch.json", {"actif": False, "raison": "", "date": ""})


def kill_switch_actif():
    return bool(etat_kill_switch().get("actif"))


def auditer(action, acteur, detail):
    config.LOGS.mkdir(parents=True, exist_ok=True)
    ligne = {"horodatage": _now(), "action": action, "acteur": acteur, "detail": detail}
    with open(config.LOGS / "audit.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")


def lire_audit(limite=50):
    chemin = config.LOGS / "audit.jsonl"
    if not chemin.exists():
        return []
    lignes = [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]
    return lignes[-limite:][::-1]


def definir_kill_switch(actif, raison, acteur):
    etat = {"actif": bool(actif), "raison": raison, "date": _now(), "acteur": acteur}
    ecrire_json(config.GOV / "kill_switch.json", etat)
    auditer("kill_switch_on" if actif else "kill_switch_off", acteur, raison)
    return etat


def verifier_non_regression(cfg):
    """Rejoue les cas golden avec la configuration donnée. Retourne la liste des écarts."""
    from app import sectors
    ecarts = []
    for cas in lire_json(config.GOV / "golden_cases.json", []):
        score, _ = sectors.calculer_score(cas["secteur"], cas["entree"])
        cat = sectors.categoriser(score, cfg["seuil_hitl"])
        if cat != cas["categorie_attendue"]:
            ecarts.append({"cas": cas["id"], "attendu": cas["categorie_attendue"], "obtenu": cat, "score": score})
    return ecarts


def rollback(version, acteur, raison):
    if version not in versions_disponibles():
        raise ValueError(f"version inconnue : {version}")
    cfg = lire_json(config.GOV / "versions" / f"v{version}.json")
    ecrire_json(config.GOV / "active_config.json", cfg)
    auditer("rollback", acteur, f"vers {version} : {raison}")
    return cfg


def deployer(version, acteur, approbateurs):
    """Déploie une version si deux rôles distincts l'ont approuvée et si la non-régression passe."""
    if version not in versions_disponibles():
        raise ValueError(f"version inconnue : {version}")
    if len(set(approbateurs)) < 2:
        raise PermissionError("approbation à deux rôles distincts requise")
    cfg = lire_json(config.GOV / "versions" / f"v{version}.json")
    ecarts = verifier_non_regression(cfg)
    if ecarts:
        auditer("deploiement_refuse", acteur, f"{version} : {len(ecarts)} écart(s) golden")
        raise RuntimeError(f"non-régression en échec : {ecarts}")
    ecrire_json(config.GOV / "active_config.json", cfg)
    auditer("deploiement", acteur, f"{version} approuvé par {', '.join(sorted(set(approbateurs)))}")
    return cfg
