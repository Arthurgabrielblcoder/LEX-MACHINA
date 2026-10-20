import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_cc_post_gate_a as B
import cc_transactional_deploy as D


class PostGateAArtifactsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs, cls.summary = B.build()
        cls.fixture = cls.summary["fixture"]
        cls.fixture_profile = cls.summary["fixture_profile"]
        cls.mass_profile = cls.summary["mass_profile"]

    def test_gate_a_scope(self):
        doc = json.loads(self.outputs[B.GATE / "TURMA_DISPLAY_PHYSICAL_GATE_A_APPROVAL.json"])
        self.assertEqual(doc["FIRMWARE_GATE_A_PHYSICAL"], "APPROVED")
        self.assertEqual(doc["TURMA_DISPLAY_PHYSICAL"], "PENDING_PHASE_B")
        self.assertEqual(doc["user_validation"], "20/20 PASS")

    def test_firmware_hash(self):
        self.assertEqual(self.fixture_profile["firmware_requirement"]["sha256"], B.FIRMWARE_SHA)
        self.assertEqual(self.mass_profile["firmware_requirement"]["sha256"], B.FIRMWARE_SHA)

    def test_fixture_counts(self):
        self.assertEqual((self.fixture["relations_added"], self.fixture["targets_added"], self.fixture["projected_CC"]), (6, 6, "55/45"))

    def test_fixture_groups(self):
        groups = {x["GROUP"] for x in self.fixture["fixtures"]}
        self.assertEqual(groups, {"GROUP_C", "GROUP_D", "GROUP_E"})

    def test_fixture_display_coverage(self):
        rows = self.fixture["fixtures"]
        self.assertTrue({"TERCEIRA TURMA", "QUARTA TURMA"} <= {x["ORGAO"] for x in rows})
        self.assertTrue({"RESP", "ARESP"} <= {x["CLASSE"] for x in rows})
        self.assertEqual(sum(x["GROUP"] == "GROUP_E" and bool(x["REPLACEMENT_FROM"]) for x in rows), 2)

    def test_fixture_all_new_targets(self):
        self.assertEqual(len({x["TARGET"] for x in self.fixture["fixtures"]}), 6)

    def test_mass_counts(self):
        self.assertEqual(self.mass_profile["post_state"]["semantic"], {"cc_relations": 702, "cc_targets": 636,
            "cf_adct_normalized_relations": 315, "cf_adct_normalized_targets": 197, "lookup_entries": 833})
        self.assertEqual(len(self.mass_profile["content_files"]), 572)

    def test_mass_two_authorized_pre_states(self):
        self.assertEqual(set(self.mass_profile["allowed_pre_states"]), {"CLEAN_BASELINE", "POST_FIXTURE_VALIDATED"})

    def test_lookup_last(self):
        self.assertTrue(self.mass_profile["aggregate_order"][-1].endswith("JUR_LOOKUP.IDX"))

    def test_confirmation_tokens_distinct(self):
        self.assertEqual(self.fixture_profile["confirmation_token"], "CC_TURMA_FIXTURE_B")
        self.assertEqual(self.mass_profile["confirmation_token"], "CC_MASS_653")

    def test_group_f_review(self):
        counts = self.summary["group_f"]
        self.assertEqual(sum(counts.values()), 28)

    def test_group_f_never_approved(self):
        doc = json.loads(self.outputs[HERE / "CC_GROUP_F_DEEP_REVIEW.json"])
        self.assertEqual(doc["HUMAN_APPROVED"], 0)
        self.assertTrue(all(not x["HUMAN_APPROVED"] for x in doc["cases"]))

    def test_adi_4277_direct_object_conclusion(self):
        doc = json.loads(self.outputs[HERE / "CC_GROUP_F_DEEP_REVIEW.json"])
        adi = next(x for x in doc["cases"] if x["ID"] == "CCMD-72D7D2A523")
        self.assertIn("objeto direto", adi["MATERIAL_RELATION"])

    def test_no_external_research(self):
        doc = json.loads(self.outputs[HERE / "CC_GROUP_F_DEEP_REVIEW.json"])
        self.assertEqual(doc["EXTERNAL_RESEARCH_COUNT"], 0)

    def test_mock_evidence_passes(self):
        fixture = json.loads((HERE / "CC_TURMA_PHYSICAL_FIXTURE/host/MOCK_RESULT.json").read_text(encoding="utf-8"))
        mass = json.loads((HERE / "CC_MASS_DEPLOY_653/host/MOCK_RESULT.json").read_text(encoding="utf-8"))
        self.assertEqual((fixture["result"], mass["result"], mass["failure_injection_result"]), ("PASS", "PASS", "PASS"))
        self.assertEqual(len(mass["failure_injection"]), 5)

    def test_builder_is_deterministic(self):
        again, _ = B.build()
        self.assertEqual(self.outputs, again)

    def test_real_destination_never_inferred(self):
        self.assertNotIn("D:", Path(HERE / "cc_transactional_deploy.py").read_text(encoding="utf-8"))

    def test_profile_schema(self):
        D.load_profile(HERE / "CC_MASS_DEPLOY_653/DEPLOY_PROFILE.json")


if __name__ == "__main__":
    unittest.main()
