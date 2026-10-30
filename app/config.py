"""Chemins et paramètres d'environnement. Aucun secret dans le dépôt."""
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
OUTPUTS = Path(os.getenv("OUTPUTS_DIR", BASE / "outputs"))
LOGS = Path(os.getenv("LOGS_DIR", BASE / "logs"))
GOV = Path(os.getenv("GOV_DIR", BASE / "governance"))
DASHBOARD = BASE / "dashboard"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
PORT = int(os.getenv("PORT", "8001"))
