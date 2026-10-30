import unittest

from app import sectors


class TestScoring(unittest.TestCase):
    def test_patient_stable_risque_faible(self):
        s, _ = sectors.calculer_score("sante", {"spo2": 98, "temperature": 36.8, "frequence_cardiaque": 72,
                                                "douleur": 1, "comorbidites": "non"})
        self.assertEqual(s, 0)
        self.assertEqual(sectors.categoriser(s, 70), "Risque faible")

    def test_patient_critique_risque_eleve(self):
        s, _ = sectors.calculer_score("sante", {"spo2": 85, "temperature": 39.8, "frequence_cardiaque": 145,
                                                "douleur": 9, "comorbidites": "oui"})
        self.assertEqual(s, 100)
        self.assertEqual(sectors.categoriser(s, 70), "Risque élevé")

    def test_score_borne_0_100_pour_tous_les_secteurs(self):
        for secteur, cfg in sectors.SECTEURS.items():
            extreme = {i[0]: (1e6 if i[3] == "haut" else -1e6) for i in cfg["indicateurs"]}
            extreme[cfg["drapeau"][0]] = "oui"
            s, _ = sectors.calculer_score(secteur, extreme)
            self.assertEqual(s, 100, secteur)
            neutre = {i[0]: i[4] for i in cfg["indicateurs"]}
            neutre[cfg["drapeau"][0]] = "non"
            self.assertEqual(sectors.calculer_score(secteur, neutre)[0], 0, secteur)

    def test_poids_somme_100(self):
        for secteur, cfg in sectors.SECTEURS.items():
            self.assertEqual(sum(i[6] for i in cfg["indicateurs"]) + cfg["drapeau"][2], 100, secteur)

    def test_entrees_invalides(self):
        with self.assertRaises(ValueError):
            sectors.calculer_score("inconnu", {})
        with self.assertRaises(ValueError):
            sectors.calculer_score("sante", {"spo2": "n/a", "temperature": 37, "frequence_cardiaque": 80, "douleur": 2})
        with self.assertRaises(ValueError):
            sectors.calculer_score("finance", {"montant_ratio": 3})
        with self.assertRaises(ValueError):
            sectors.calculer_score("sante", {"spo2": 95, "temperature": 37, "frequence_cardiaque": 80,
                                             "douleur": 2, "comorbidites": "peut-être"})
