"""Tests de l'API (nécessitent fastapi + httpx : pip install -r requirements-dev.txt)."""
import unittest

try:
    from fastapi.testclient import TestClient
    from app import api, config
    HAS_FASTAPI = True
except ImportError:  # pragma: no cover
    HAS_FASTAPI = False

from tests.base import BaseTemp

OK = {"secteur": "sante", "entite_id": "PAT-900",
      "indicateurs": {"spo2": 85, "temperature": 39.8, "frequence_cardiaque": 145, "douleur": 9, "comorbidites": "oui"}}


@unittest.skipUnless(HAS_FASTAPI, "fastapi non installé")
class TestAPI(BaseTemp):
    def setUp(self):
        super().setUp()
        self.client = TestClient(api.app)
        config.ADMIN_TOKEN = "secret-test"

    def tearDown(self):
        config.ADMIN_TOKEN = ""
        super().tearDown()

    def test_health(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["statut"], "ok")

    def test_dashboard_servi(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_analyse_retourne_correlation_id(self):
        r = self.client.post("/api/analyze", json=OK)
        self.assertEqual(r.status_code, 201)
        corps = r.json()
        self.assertTrue(corps["correlation_id"].startswith("CID-"))
        self.assertEqual(corps["categorie"], "Risque élevé")
        self.assertEqual(len(corps["detail"]), 5)

    def test_validation_entree(self):
        self.assertEqual(self.client.post("/api/analyze", json={**OK, "secteur": "x"}).status_code, 422)
        self.assertEqual(self.client.post("/api/analyze", json={**OK, "entite_id": "a b"}).status_code, 422)
        r = self.client.post("/api/analyze", json={**OK, "indicateurs": {"spo2": 90}})
        self.assertEqual(r.status_code, 422)

    def test_stats_et_cartes(self):
        self.client.post("/api/analyze", json=OK)
        s = self.client.get("/api/stats").json()
        self.assertEqual(s["kpi"]["executions"], 1)
        self.assertEqual(len(self.client.get("/api/agent-cards").json()["cartes"]), 8)

    def test_admin_protege(self):
        corps = {"actif": True, "raison": "test"}
        self.assertEqual(self.client.post("/api/admin/kill-switch", json=corps).status_code, 403)
        r = self.client.post("/api/admin/kill-switch", json=corps, headers={"X-Admin-Token": "secret-test"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.post("/api/analyze", json=OK).json()["statut"], "Suspendu (kill switch)")
        r = self.client.post("/api/admin/rollback", json={"version": "1.0.0", "raison": "test"},
                             headers={"X-Admin-Token": "secret-test"})
        self.assertEqual(r.status_code, 200)
