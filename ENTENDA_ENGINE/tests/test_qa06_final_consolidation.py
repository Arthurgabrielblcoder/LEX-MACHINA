import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
OUT = HERE / "derived/qa06_subdivision_material_audit"
FINAL = OUT / "QA06_FINAL_CONSOLIDATION.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class QA06FinalConsolidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = load(FINAL)

    def test_cardinalities_and_authoritative_queues(self):
        self.assertEqual(self.doc["authorized_inventory"], {
            "targets": 2017, "subdivisions": 3790, "auditable": 3752, "excluded": 38,
            "sha256": "7fe41b6b6e7755e17174551b56ea684fbbd8a399e95641f7f47e729f55ef5c82",
        })
        self.assertEqual(self.doc["front_b"]["final_disposition_counts"], {
            "INDETERMINADO": 10, "JA_CORRIGIDO": 1,
            "NAO_CONFIRMADO": 566, "PENDENTE_CORRECAO": 461,
        })
        self.assertEqual(self.doc["front_b"]["pending_severity_counts"], {"ALTO": 41, "MÉDIO": 420})

    def test_candidate_and_checkpoints(self):
        self.assertEqual((self.doc["front_a"]["records"], self.doc["front_a"]["active"],
                          self.doc["front_a"]["historical"]), (2313, 2017, 296))
        self.assertEqual(len(self.doc["checkpoints"]), 41)
        self.assertEqual(sum(item["targets"] for item in self.doc["checkpoints"]), 2017)
        self.assertEqual(len({item["checkpoint"] for item in self.doc["checkpoints"]}), 41)

    def test_states_do_not_overclaim(self):
        states = self.doc["states"]
        self.assertTrue(states["subdivision_audit_complete"])
        for key in ("subdivision_findings_resolved", "full_corpus_legally_approved",
                    "human_approved", "production_index_modified", "deployed",
                    "firmware_accessed", "microsd_accessed", "esp32_accessed"):
            self.assertFalse(states[key])

    def test_final_consolidation_is_deterministic(self):
        before = sha(FINAL)
        subprocess.run([sys.executable, "-X", "utf8", str(HERE / "qa06_finalize.py")],
                       cwd=ROOT, check=True, capture_output=True)
        self.assertEqual(before, sha(FINAL))


if __name__ == "__main__":
    unittest.main()
