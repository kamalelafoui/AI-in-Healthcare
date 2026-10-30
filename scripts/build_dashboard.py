"""Génère dashboard/index.html : injecte les règles des secteurs, les Agent Cards et un instantané des exécutions.
Servi par l'API sur http://localhost:8001 ; reste utilisable en ouvrant le fichier seul (mode hors ligne)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config, governance, sectors, stats  # noqa: E402

TEMPLATE = Path(__file__).with_name("dashboard_template.html").read_text(encoding="utf-8")


def main():
    cfg = governance.config_active()
    execs = stats.charger_executions()
    data = {
        "secteurs": {k: {"nom": v["nom"], "agent": v["agent"], "id": v["id"],
                         "indicateurs": [list(i) for i in v["indicateurs"]], "drapeau": list(v["drapeau"])}
                     for k, v in sectors.SECTEURS.items()},
        "cartes": governance.lire_json(config.GOV / "agent_cards.json", []),
        "snapshot": {"version": cfg["version"], "seuil_hitl": cfg["seuil_hitl"],
                     "kill_switch": governance.etat_kill_switch(), "kpi": stats.kpi(execs),
                     "categories": stats.repartition(execs, "categorie"), "secteurs": stats.repartition(execs, "secteur"),
                     "routes": stats.repartition(execs, "route"), "executions": execs[-60:][::-1],
                     "alertes": stats.calculer_alertes(execs), "audit": governance.lire_audit(20)},
    }
    html = TEMPLATE.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    (config.DASHBOARD / "index.html").write_text(html, encoding="utf-8")
    print("dashboard/index.html généré")


if __name__ == "__main__":
    main()
