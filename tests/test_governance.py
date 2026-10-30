import json

from app import config, governance
from tests.base import BaseTemp


class TestGouvernance(BaseTemp):
    def test_agent_cards_completes(self):
        cartes = json.loads((config.GOV / "agent_cards.json").read_text(encoding="utf-8"))
        self.assertEqual(len(cartes), 8)  # orchestrateur + monitoring + 6 secteurs
        for c in cartes:
            for champ in ("identifiant", "nom", "description", "proprietaire_metier", "responsable_technique",
                          "garde_fous", "limites", "version", "date_derniere_revue", "prochaine_revue"):
                self.assertTrue(c.get(champ), f"{c.get('identifiant')} : {champ} manquant")
        self.assertEqual(len({c["identifiant"] for c in cartes}), 8)

    def test_version_active_semver(self):
        self.assertTrue(governance.SEMVER_OK(governance.config_active()["version"]))

    def test_golden_passe_en_v1_0_0(self):
        self.assertEqual(governance.verifier_non_regression(governance.config_active()), [])

    def test_golden_detecte_la_regression_v1_1_0(self):
        cfg = governance.lire_json(config.GOV / "versions" / "v1.1.0.json")
        ecarts = governance.verifier_non_regression(cfg)
        self.assertTrue(any(e["cas"] == "G3-seuil-70-89" for e in ecarts))

    def test_deploiement_exige_deux_roles(self):
        with self.assertRaises(PermissionError):
            governance.deployer("1.0.0", "test", ["responsable_technique", "responsable_technique"])

    def test_deploiement_refuse_si_non_regression(self):
        with self.assertRaises(RuntimeError):
            governance.deployer("1.1.0", "test", ["responsable_clinique", "responsable_technique"])
        self.assertEqual(governance.config_active()["version"], "1.0.0")

    def test_rollback(self):
        governance.ecrire_json(config.GOV / "active_config.json", governance.lire_json(config.GOV / "versions" / "v1.1.0.json"))
        self.assertEqual(governance.config_active()["seuil_hitl"], 90)
        governance.rollback("1.0.0", "test", "retour stable")
        self.assertEqual(governance.config_active()["seuil_hitl"], 70)
        with self.assertRaises(ValueError):
            governance.rollback("9.9.9", "test", "inconnue")

    def test_audit(self):
        governance.definir_kill_switch(True, "raison test", "tester")
        self.assertEqual(governance.lire_audit(1)[0]["action"], "kill_switch_on")
