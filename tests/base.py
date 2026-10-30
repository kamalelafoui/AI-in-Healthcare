"""Base commune : répertoires temporaires pour ne pas toucher aux vrais journaux."""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from app import config


class BaseTemp(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(config.GOV, self.tmp / "governance")
        self._old = (config.GOV, config.OUTPUTS, config.LOGS)
        config.GOV, config.OUTPUTS, config.LOGS = self.tmp / "governance", self.tmp / "outputs", self.tmp / "logs"

    def tearDown(self):
        config.GOV, config.OUTPUTS, config.LOGS = self._old
        shutil.rmtree(self.tmp, ignore_errors=True)
