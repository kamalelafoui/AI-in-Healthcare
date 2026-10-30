"""Lot de test et vérifications : python main.py | python main.py --check"""
import argparse
import csv
import json
import random
import sys

from app import config, governance, pipeline, stats


def ecrire_csv(chemin, lignes, colonnes):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colonnes, delimiter=";")
        w.writeheader()
        w.writerows(lignes)


def verifier():
    cfg = governance.config_active()
    ecarts = governance.verifier_non_regression(cfg)
    print(f"[OK] Version active : {cfg['version']} (seuil HITL = {cfg['seuil_hitl']})")
    print(f"[{'OK' if not ecarts else 'ÉCHEC'}] Non-régression golden : {len(ecarts)} écart(s)")
    print(f"[OK] Kill switch : {'ACTIF' if governance.kill_switch_actif() else 'inactif'}")
    print(f"[OK] Versions disponibles : {', '.join(governance.versions_disponibles())}")
    return 0 if not ecarts else 1


def lot():
    cfg = governance.config_active()
    rng = random.Random(42)
    demandes = pipeline.charger_lot(config.DATA / "lot_demandes.json")
    pipeline.reinitialiser()
    resultats = []
    for d in demandes:
        res, evts = pipeline.executer(d["secteur"], d["entite_id"], d["indicateurs"], cfg, rng)
        pipeline.persister(res, evts)
        resultats.append(res)
    alertes = stats.calculer_alertes(resultats)
    ecrire_csv(config.OUTPUTS / "executions.csv", resultats, list(resultats[0].keys()))
    ecrire_csv(config.OUTPUTS / "alerts.csv", alertes,
               ["date_heure", "type", "correlation_id", "valeur", "seuil", "action"])
    (config.OUTPUTS / "kpi_resume.json").write_text(
        json.dumps({"version": cfg["version"], **stats.kpi(resultats)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    k = stats.kpi(resultats)
    print(f"Version {cfg['version']} | exécutions : {k['executions']} | alertes : {len(alertes)}")
    print(f"Succès {k['taux_succes_pct']} % | échec {k['taux_echec_pct']} % | latence moy. {k['latence_moyenne_ms']} ms "
          f"| escalades HITL {k['escalades_hitl']} | coût {k['cout_total_usd']} USD")
    sans_cid = [r for r in resultats if not r["correlation_id"]]
    print(f"Correlation ID présent sur {len(resultats) - len(sans_cid)}/{len(resultats)} exécutions")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="AI in Healthcare : lot de test et vérifications")
    p.add_argument("--check", action="store_true")
    sys.exit(verifier() if p.parse_args().check else lot())
