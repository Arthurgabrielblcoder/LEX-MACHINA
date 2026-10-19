"""Gates da preparação para ratificação humana em massa das 681 relações do CC."""
import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
OUT = ENG / "CC_MASS_DISCOVERY"
sys.path.insert(0, str(ENG))
import build_cc_mass_ratification as B  # noqa: E402
import cc_mass_ratification_validator as V  # noqa: E402


class CCMassRatification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups_raw = (OUT / "CC_MASS_RATIFICATION_GROUPS.json").read_bytes()
        cls.doc = json.loads(cls.groups_raw)
        cls.groups = {group["group_id"]: group for group in cls.doc["groups"]}
        cls.items = [item for group in cls.groups.values() for item in group["items"]]
        cls.ids = [item["id"] for item in cls.items]
        cls.template = json.loads((OUT / "CC_MASS_RATIFICATION_DECISION_TEMPLATE.json").read_text(encoding="utf-8"))
        cls.metrics = json.loads((OUT / "CC_MASS_RATIFICATION_PREPARATION_METRICS.json").read_text(encoding="utf-8"))
        cls.replacements = json.loads((OUT / "CC_MASS_REPLACEMENT_AUDIT.json").read_text(encoding="utf-8"))
        cls.audit_rows = [json.loads(line) for line in (OUT / "CC_MASS_AUDIT_ALL_932.jsonl").read_text(encoding="utf-8").splitlines() if line]

    def test_681_reconciled_once(self):
        self.assertEqual((len(self.ids), len(set(self.ids))), (681, 681))
        ready = {r["id"] for r in self.audit_rows if r["editorial_state"] in B.READY_STATES}
        self.assertEqual(set(self.ids), ready)

    def test_no_hold_or_reject_in_groups(self):
        states = {r["id"]: r["editorial_state"] for r in self.audit_rows}
        self.assertTrue(all(states[item_id] in B.READY_STATES for item_id in self.ids))

    def test_all_decisions_pending(self):
        self.assertTrue(all(item["current_human_decision"] == "PENDING" for item in self.items))
        self.assertTrue(all(group["decision"] == "PENDING" for group in self.template["groups"]))
        self.assertEqual(self.template["id_actions"], [])

    def test_group_hashes_and_hash_required(self):
        self.assertIs(self.doc["group_hash_required"], True)
        for group in self.groups.values():
            self.assertEqual(group["sha256"], B.group_hash(group["group_id"], group["relation_ids"], group["version"]))

    def test_composition_change_changes_hash(self):
        group = self.groups["GROUP_A"]
        changed = group["relation_ids"][:-1]
        self.assertNotEqual(group["sha256"], B.group_hash("GROUP_A", changed, group["version"]))

    def test_validator_rejects_wrong_hash(self):
        altered = copy.deepcopy(self.template)
        altered["groups"][0]["group_sha256"] = "0" * 64
        errors = V.validate(self.doc, altered, self.groups_raw)
        self.assertTrue(any("hash de decisão divergente" in error for error in errors))

    def test_validator_accepts_pending_template(self):
        self.assertEqual(V.validate(self.doc, self.template, self.groups_raw), [])

    def test_turma_remains_persuasive(self):
        turma = [item for item in self.items if item["authority_class"] == "TURMA_ACORDAO"]
        self.assertEqual(len(turma), 579)
        self.assertTrue(all("persuasiv" in item["reader_note"].lower() for item in turma))
        self.assertTrue(all(item["classe"] not in {"REPETITIVO", "IAC", "SUMULA"} for item in turma))

    def test_replacements_use_replacement_precedent(self):
        self.assertEqual((self.replacements["replacement_relations"], self.replacements["replacement_identity_errors"]), (81, 0))
        by_id = {item["id"]: item for item in self.items}
        for entry in self.replacements["items"]:
            item = by_id[entry["old_candidate_id"]]
            self.assertEqual(item["precedent"], entry["replacement_process"])
            self.assertEqual(item["substituted_from"], entry["old_process"])
            self.assertNotEqual(entry["old_process"], entry["replacement_process"])
            self.assertTrue(all(entry["checks"].values()))

    def test_no_leading_case_duplicates(self):
        ready = [r for r in self.audit_rows if r["editorial_state"] in B.READY_STATES]
        self.assertFalse(any(r["leading_case_duplicate"] for r in ready))
        pairs = [(item["target"], item["precedent"]) for item in self.items]
        self.assertEqual(len(pairs), len(set(pairs)))

    def test_stf_contextual_false_positives_do_not_return(self):
        precedents = {item["precedent"] for item in self.items}
        self.assertFalse({"STF:RG:581", "STF:ADC:29", "STF:ADI:3890"} & precedents)

    def test_tier_a_reconciled_without_auto_approval(self):
        tier_a = [row for row in self.audit_rows if row["tier"] == "A"]
        counts = {}
        for row in tier_a:
            counts[row["editorial_state"]] = counts.get(row["editorial_state"], 0) + 1
        self.assertEqual(counts, {"READY_FOR_BLOCK_DECISION": 13, "READY_WITH_QUALIFICATION": 15, "REJECT_RECOMMENDED": 1})
        self.assertTrue(all(item["current_human_decision"] == "PENDING" for item in self.items))

    def test_projections_are_deduplicated(self):
        projections = self.metrics["projections"]
        self.assertEqual(projections["PROJECTED_ALL_READY"]["relations"], 730)
        self.assertEqual(projections["PROJECTED_ALL_READY"]["targets"], 663)
        for projection in projections.values():
            self.assertEqual(projection["targets"], 39 + projection["new_targets"])

    def test_frozen_baselines(self):
        self.assertEqual(self.metrics["CURRENT_CC_BASELINE"], "49/39")
        self.assertEqual(self.metrics["CURRENT_CF_BASELINE"], "315/198")
        self.assertEqual(self.doc["baseline"], B.BASELINE)
        check = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", "JURISPRUDENCE_ENGINE/CC_J2_MATERIALIZATION_CANDIDATE", "JURISPRUDENCE_ENGINE/CC_J2_PHYSICAL_DEPLOY", "DEVICE_INTEGRATION/staging_article_index_cc", "firmware"],
            cwd=ROOT,
        )
        self.assertEqual(check.returncode, 0)

    def test_special_exceptions_are_material(self):
        group = self.groups["GROUP_F"]
        self.assertGreater(group["relation_count"], 0)
        self.assertTrue(all(item["special_reasons"] for item in group["items"]))
        self.assertEqual(group["exceptions"], group["relation_ids"])

    def test_corrobated_is_not_binding(self):
        group = self.groups["GROUP_C"]
        self.assertIn("CORROBORATED != BINDING", group["authority_policy"])
        self.assertTrue(all(item["authority_class"] == "TURMA_ACORDAO" for item in group["items"]))

    def test_output_is_up_to_date(self):
        run = subprocess.run([sys.executable, "-B", str(ENG / "build_cc_mass_ratification.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual((run.returncode, run.stdout.strip()), (0, "UP_TO_DATE"), run.stderr)

    def test_deterministic_across_hash_seeds(self):
        digests = []
        for seed in ("1", "777"):
            env = os.environ.copy()
            env["PYTHONHASHSEED"] = seed
            run = subprocess.run([sys.executable, "-B", str(ENG / "build_cc_mass_ratification.py"), "--print-digest"], cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            digests.append(run.stdout.strip())
        self.assertEqual(digests[0], digests[1])


if __name__ == "__main__":
    unittest.main()
