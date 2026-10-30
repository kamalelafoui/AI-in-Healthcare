"""Simulation d'incident (runbook) : seuil HITL relevé à 90 -> patients à risque non escaladés.

Détection -> contention (kill switch) -> remédiation (rollback) -> rétablissement.
Travaille dans un répertoire temporaire : le dépôt n'est pas modifié, sauf outputs/incident/rapport_incident.json.
"""
import json
import random
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config, governance, pipeline  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent


def anomalies(cfg):
    """Nombre de patients critiques (golden G2/G3) non escaladés avec la configuration donnée."""
    n = 0
    rng = random.Random(3)
    for cas in governance.lire_json(config.GOV / "golden_cases.json"):
        if cas["categorie_attendue"] == "Risque élevé":
            res, _ = pipeline.executer(cas["secteur"], cas["id"], cas["entree"], cfg, rng)
            if not res["route"].startswith("Escalade") and res["statut"] != "Suspendu (kill switch)":
                n += 1
    return n


def main():
    tmp = Path(tempfile.mkdtemp())
    shutil.copytree(config.GOV, tmp / "governance")
    config.GOV, config.OUTPUTS, config.LOGS = tmp / "governance", tmp / "outputs", tmp / "logs"
    etapes = []

    cfg_stable = governance.config_active()
    cfg_cr002 = governance.lire_json(config.GOV / "versions" / "v1.1.0.json")
    governance.ecrire_json(config.GOV / "active_config.json", cfg_cr002)  # déploiement CR-002 contourné
    governance.auditer("deploiement", "ci-bypass", "1.1.0 (CR-002) déployé sans non-régression")
    a_avant = anomalies(governance.config_active())
    etapes.append(f"1. Détection : version 1.1.0 active, {a_avant} patient(s) critique(s) non escaladé(s)")

    governance.definir_kill_switch(True, "patients à risque non escaladés après CR-002", "astreinte")
    res, _ = pipeline.executer("sante", "PAT-X", {"spo2": 85, "temperature": 39.8, "frequence_cardiaque": 145,
                                                   "douleur": 9, "comorbidites": "oui"}, governance.config_active(), random.Random(1))
    etapes.append(f"2. Contention : kill switch actif -> statut « {res['statut']} »")

    governance.rollback("1.0.0", "astreinte", "retour à la version stable (cause : CR-002)")
    a_apres = anomalies(governance.config_active())
    etapes.append(f"3. Remédiation : rollback vers 1.0.0 -> {a_apres} anomalie(s)")

    governance.definir_kill_switch(False, "retour à la normale", "astreinte")
    bloque = False
    try:
        governance.deployer("1.1.0", "astreinte", ["responsable_clinique", "responsable_technique"])
    except RuntimeError:
        bloque = True
    etapes.append(f"4. Rétablissement : kill switch off ; nouveau déploiement de 1.1.0 refusé par la non-régression : {bloque}")

    rapport = {"scenario": "CR-002 : seuil HITL 70 -> 90", "anomalies_avant_rollback": a_avant,
               "anomalies_apres_rollback": a_apres, "redeploiement_bloque_par_golden": bloque,
               "version_finale": governance.config_active()["version"], "etapes": etapes,
               "audit": governance.lire_audit(10)[::-1]}
    sortie = RACINE / "outputs" / "incident"
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "rapport_incident.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n".join(etapes))
    shutil.rmtree(tmp, ignore_errors=True)
    return 0 if (a_avant > 0 and a_apres == 0 and bloque) else 1


if __name__ == "__main__":
    sys.exit(main())
