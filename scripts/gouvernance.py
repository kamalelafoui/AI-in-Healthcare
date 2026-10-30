"""CLI de gouvernance : statut, approbation/déploiement, kill switch, rollback."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import governance  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("statut")
    d = sp.add_parser("deployer")
    d.add_argument("version")
    d.add_argument("--approbateurs", nargs="+", required=True, help="rôles ayant approuvé (2 distincts minimum)")
    k = sp.add_parser("kill-switch")
    k.add_argument("etat", choices=["on", "off"])
    k.add_argument("--raison", required=True)
    r = sp.add_parser("rollback")
    r.add_argument("--vers", required=True)
    r.add_argument("--raison", required=True)
    a = p.parse_args()
    try:
        if a.cmd == "statut":
            print(json.dumps({"active": governance.config_active(), "kill_switch": governance.etat_kill_switch(),
                              "versions": governance.versions_disponibles()}, ensure_ascii=False, indent=2))
        elif a.cmd == "deployer":
            print("Déployé :", governance.deployer(a.version, "cli", a.approbateurs)["version"])
        elif a.cmd == "kill-switch":
            print(governance.definir_kill_switch(a.etat == "on", a.raison, "cli"))
        else:
            print("Rollback vers", governance.rollback(a.vers, "cli", a.raison)["version"])
    except (ValueError, PermissionError, RuntimeError) as e:
        print("Refusé :", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
