import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
OUT = HERE / "derived/qa07_high_findings_resolution"
FIVE = {"o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis"}


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def sha(name):
    return hashlib.sha256((OUT / name).read_bytes()).hexdigest()


class QA07RecoveredModulesTest(unittest.TestCase):
    def test_high_modules_cover_exactly_41_findings_and_25_targets(self):
        a, b = load("QA07_EDITOR_HIGH_A.json"), load("QA07_EDITOR_HIGH_B.json")
        ids_a = [f["finding_id"] for r in a["records"] for f in r["findings"]]
        ids_b = [f for r in b["records"] for f in r["finding_ids"]]
        targets = [r["target_id"] for r in a["records"] + b["records"]]
        self.assertEqual((len(ids_a), len(ids_b), len(targets)), (21, 20, 25))
        self.assertEqual(len(set(ids_a + ids_b)), 41)
        self.assertEqual(len(set(targets)), 25)
        for row in a["records"] + b["records"]:
            self.assertEqual(set(row["previous_content"]), FIVE)
            self.assertEqual(set(row["proposed_content"]), FIVE)

    def test_indeterminate_decisions_cover_exactly_ten(self):
        doc = load("QA07_INDETERMINATE_DECISIONS.json")
        self.assertEqual(len(doc["records"]), 10)
        self.assertEqual(len({r["finding_id"] for r in doc["records"]}), 10)
        self.assertEqual(dict(Counter(r["decision"] for r in doc["records"])), {
            "COBERTURA_MATERIAL_SUFICIENTE": 2, "CONFIRMADO_PARA_CORRECAO": 8,
        })

    def test_cp02_through_cp05_are_exact(self):
        cp2 = load("QA07_CP02.json")
        self.assertEqual((cp2["records"], cp2["decision_counts"]),
                         (10, {"COBERTURA_MATERIAL_SUFICIENTE": 2, "CONFIRMADO_PARA_CORRECAO": 8}))
        blocks = [load(f"QA07_CP{n:02d}.json") for n in range(3, 6)]
        ids = [fid for block in blocks for fid in block["finding_ids"]]
        self.assertEqual([b["finding_total"] for b in blocks], [14, 14, 13])
        self.assertEqual((len(ids), len(set(ids))), (41, 41))

    def test_recovery_consolidation_is_deterministic(self):
        names = ["QA07_CP02.json", "QA07_CP03.json", "QA07_CP04.json", "QA07_CP05.json"]
        before = [sha(name) for name in names]
        subprocess.run([sys.executable, "-X", "utf8", str(HERE / "qa07_recover_modules.py")],
                       cwd=ROOT, check=True, capture_output=True)
        self.assertEqual(before, [sha(name) for name in names])


if __name__ == "__main__":
    unittest.main()
