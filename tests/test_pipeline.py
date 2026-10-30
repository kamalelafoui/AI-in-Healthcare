import json
import random
import re

from app import config, governance, pipeline, stats
from tests.base import BaseTemp

CRITIQUE = {"spo2": 85, "temperature": 39.8, "frequence_cardiaque": 145, "douleur": 9, "comorbidites": "oui"}


class TestPipeline(BaseTemp):
    def run_one(self, secteur="sante", entree=CRITIQUE):
        cfg = governance.config_active()
        return pipeline.executer(secteur, "PAT-TEST", entree, cfg, random.Random(1))

    def test_correlation_id_sur_chaque_execution_et_chaque_evenement(self):
        res, evts = self.run_one()
        self.assertRegex(res["correlation_id"], r"^CID-[0-9a-f]{10}$")
        self.assertTrue(evts)
        self.assertTrue(all(e["correlation_id"] == res["correlation_id"] for e in evts))

    def test_correlation_ids_uniques(self):
        ids = {self.run_one()[0]["correlation_id"] for _ in range(50)}
        self.assertEqual(len(ids), 50)

    def test_escalade_hitl_pour_risque_eleve(self):
        res, evts = self.run_one()
        self.assertEqual(res["categorie"], "Risque élevé")
        self.assertTrue(res["route"].startswith("Escalade"))
        self.assertIn("escalade", [e["etape"] for e in evts])

    def test_sortie_automatique_pour_risque_faible(self):
        res, _ = self.run_one(entree={"spo2": 98, "temperature": 36.8, "frequence_cardiaque": 72,
                                       "douleur": 1, "comorbidites": "non"})
        self.assertEqual((res["route"], res["statut"]), ("Sortie automatique", "Succès"))

    def test_entree_invalide_revue_manuelle(self):
        res, evts = self.run_one(entree={"spo2": "x"})
        self.assertEqual((res["statut"], res["route"]), ("Échec", "Revue manuelle"))
        self.assertTrue(res["correlation_id"])

    def test_kill_switch_suspend_le_traitement(self):
        governance.definir_kill_switch(True, "test", "pytest")
        res, _ = self.run_one()
        self.assertEqual(res["statut"], "Suspendu (kill switch)")
        self.assertEqual(res["score"], "")
        governance.definir_kill_switch(False, "fin test", "pytest")
        self.assertEqual(self.run_one()[0]["statut"], "En attente de décision humaine")

    def test_aucune_donnee_nominative_dans_les_journaux(self):
        res, evts = self.run_one()
        pipeline.persister(res, evts)
        texte = (config.LOGS / "execution_log.jsonl").read_text(encoding="utf-8")
        self.assertNotRegex(texte, r"@|nom|prenom")

    def test_persistance_et_kpi(self):
        for _ in range(5):
            pipeline.persister(*self.run_one())
        execs = stats.charger_executions()
        self.assertEqual(len(execs), 5)
        self.assertEqual(stats.kpi(execs)["escalades_hitl"], 5)

    def test_lot_complet(self):
        demandes = pipeline.charger_lot(config.DATA / "lot_demandes.json")
        cfg = governance.config_active()
        rng = random.Random(42)
        res = [pipeline.executer(d["secteur"], d["entite_id"], d["indicateurs"], cfg, rng)[0] for d in demandes]
        self.assertEqual(len(res), 27)
        self.assertTrue(all(r["correlation_id"] for r in res))
        self.assertEqual(sum(1 for r in res if r["statut"] == "Échec"), 2)
        self.assertEqual({r["secteur"] for r in res}, {"sante", "mines", "automobile", "finance", "energie", "egov"})
