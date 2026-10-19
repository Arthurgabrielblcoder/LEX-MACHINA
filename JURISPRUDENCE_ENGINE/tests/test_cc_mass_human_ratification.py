import hashlib
import json
import unittest
from pathlib import Path

import sys


ENGINE = Path(__file__).resolve().parents[1]
OUT = ENGINE / "CC_MASS_DISCOVERY"
sys.path.insert(0, str(ENGINE))

import build_cc_mass_ratification as B


EXPECTED_HASHES = {
    "GROUP_A": "f10770801f7ff6360d064c675886114f1ae551a738a6453bcafcaf9f072cfa9d",
    "GROUP_B": "e4b56d26f9d044bfcdb2d593a1402c0193d803937b83e024bea64e71721ee07d",
    "GROUP_C": "313efdaa924640c5075bea9b9d7bac5fa627fa07bda004558b7b11c25266a709",
    "GROUP_D": "8605bbfeda8d892494e7deda619a0ee2ca17f9626ef518bbc740d9b2d979accf",
    "GROUP_E": "1a312f49fa62e9532d942ce5012283767ad245629598d979c6a41027a74b7929",
    "GROUP_F": "5d386498f6846d7f0c34eb5c09084964a2d9825d2cc5359c32523210889189c1",
}


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def sha(name):
    raw = (OUT / name).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(raw).hexdigest()


class TestCcMassHumanRatification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups_doc = load("CC_MASS_RATIFICATION_GROUPS.json")
        cls.record = load("CC_MASS_RATIFICATION_RECORD.json")
        cls.checkpoint = load("CC_MASS_RATIFICATION_CHECKPOINT.json")
        cls.replacements = load("CC_MASS_REPLACEMENT_AUDIT.json")
        cls.preparation_metrics = load("CC_MASS_RATIFICATION_PREPARATION_METRICS.json")
        cls.groups = {group["group_id"]: group for group in cls.groups_doc["groups"]}
        cls.record_groups = {group["group_id"]: group for group in cls.record["groups"]}
        cls.relations = cls.record["relations"]

    def test_provenance_and_frozen_baselines(self):
        self.assertEqual(self.record["audit_commit"], "9e1febc")
        self.assertEqual(self.record["decision_board_commit"], "aeb769d")
        self.assertEqual(self.record["baseline"], "MULTINORM_FROZEN_CF315_198_CC49_39")
        self.assertEqual(self.record["unchanged_physical_baselines"]["cc"], {"relations": 49, "targets": 39})
        self.assertEqual(self.record["unchanged_physical_baselines"]["cf"], {"relations": 315, "targets": 198})
        self.assertEqual(self.preparation_metrics["CURRENT_CC_BASELINE"], "49/39")
        self.assertEqual(self.preparation_metrics["CURRENT_CF_BASELINE"], "315/198")

    def test_all_six_composition_hashes_match(self):
        self.assertTrue(self.record["group_hash_required"])
        for group_id, expected in EXPECTED_HASHES.items():
            source = self.groups[group_id]
            recorded = self.record_groups[group_id]
            self.assertEqual(source["sha256"], expected)
            self.assertEqual(source["sha256"], B.group_hash(group_id, source["relation_ids"], source["version"]))
            self.assertEqual(recorded["group_sha256"], expected)
            self.assertIs(recorded["hash_match"], True)

    def test_exact_group_decisions(self):
        approved = {"GROUP_A", "GROUP_B", "GROUP_C", "GROUP_D", "GROUP_E"}
        held = {"GROUP_F"}
        self.assertEqual({key for key, value in self.record_groups.items() if value["decision"] == "APPROVE_GROUP"}, approved)
        self.assertEqual({key for key, value in self.record_groups.items() if value["decision"] == "HOLD_GROUP"}, held)

    def test_every_source_id_is_explicitly_covered_once(self):
        source_ids = [item["id"] for group in self.groups.values() for item in group["items"]]
        record_ids = [item["id"] for item in self.relations]
        self.assertEqual(len(record_ids), 681)
        self.assertEqual(len(set(record_ids)), 681)
        self.assertEqual(set(record_ids), set(source_ids))

    def test_reconciled_decision_counts(self):
        decisions = [item["decision"] for item in self.relations]
        self.assertEqual(decisions.count("HUMAN_APPROVED"), 653)
        self.assertEqual(decisions.count("HOLD_INDIVIDUAL_REVIEW"), 28)
        self.assertEqual(len(decisions), 681)
        self.assertEqual(self.record["reconciliation"]["approved_relations"], 653)
        self.assertEqual(self.record["reconciliation"]["held_relations"], 28)

    def test_group_f_has_no_approval(self):
        group_f = [item for item in self.relations if item["group_id"] == "GROUP_F"]
        self.assertEqual(len(group_f), 28)
        self.assertTrue(all(item["decision"] == "HOLD_INDIVIDUAL_REVIEW" for item in group_f))
        self.assertEqual(self.record["reconciliation"]["group_f_approved_relations"], 0)
        self.assertEqual(self.record_groups["GROUP_F"]["exceptions"], self.groups["GROUP_F"]["relation_ids"])

    def test_approved_target_reconciliation_and_projection(self):
        approved = [item for group_id in "GROUP_A GROUP_B GROUP_C GROUP_D GROUP_E".split() for item in self.groups[group_id]["items"]]
        self.assertEqual(len({item["target"] for item in approved}), 610)
        self.assertEqual(len({item["target"] for item in approved if item["new_target"]}), 597)
        self.assertEqual(self.record["reconciliation"]["new_distinct_targets_approved"], 597)
        self.assertEqual(self.record["ratified_projection"]["cc"], {"relations": 702, "targets": 636})

    def test_turma_relations_remain_persuasive(self):
        turma = [item for item in self.relations if item["decision"] == "HUMAN_APPROVED" and item["authority_class"] == "TURMA_ACORDAO"]
        self.assertEqual(len(turma), 559)
        self.assertEqual(self.record["reconciliation"]["turma_relations_ratified"], 559)
        for group_id in ("GROUP_C", "GROUP_D", "GROUP_E"):
            self.assertIn("PERSUASIVE_NON_BINDING", self.record_groups[group_id]["authority_policy"])
        self.assertIn("CORROBORATED != BINDING", self.record["policies"]["corroborated_turma"])
        self.assertIn("decisão isolada", self.record["policies"]["direct_turma"])

    def test_no_authority_escalation(self):
        source = {item["id"]: item for group in self.groups.values() for item in group["items"]}
        self.assertEqual(self.record["reconciliation"]["authority_escalations"], 0)
        self.assertTrue(all(item["authority_class"] == source[item["id"]]["authority_class"] for item in self.relations))

    def test_replacement_publication_is_exact(self):
        expected = {item["old_candidate_id"]: item for item in self.replacements["items"]}
        group_e = [item for item in self.relations if item["group_id"] == "GROUP_E"]
        group_f = [item for item in self.relations if item["group_id"] == "GROUP_F"]
        self.assertEqual(len(group_e), 76)
        self.assertEqual(set(expected) & {item["id"] for item in group_e}, {item["id"] for item in group_e})
        for item in group_e:
            publication = item["replacement_publication"]
            audit = expected[item["id"]]
            self.assertEqual(publication["publish_precedent"], audit["replacement_process"])
            self.assertEqual(publication["superseded_candidate"], audit["old_process"])
            self.assertIs(publication["publish_superseded_candidate"], False)
            self.assertTrue(all(publication["checks"].values()))
        held_replacements = [item for item in group_f if item["id"] in expected]
        self.assertEqual(len(held_replacements), 5)
        self.assertTrue(all(item["decision"] == "HOLD_INDIVIDUAL_REVIEW" for item in held_replacements))
        self.assertTrue(all("replacement_publication" not in item for item in held_replacements))
        self.assertEqual(self.record["reconciliation"]["replacement_publication_errors"], 0)

    def test_tracks_partition_approved_and_held(self):
        tracks = self.record["tracks"]
        self.assertEqual(tracks["TRACK_1_HIGH_AUTHORITY"]["relations"], 94)
        self.assertEqual(tracks["TRACK_2_TURMA"]["relations"], 559)
        self.assertEqual(tracks["TRACK_3_HOLD"]["relations"], 28)
        self.assertEqual(94 + 559, 653)

    def test_display_and_materialization_gates_remain_closed(self):
        gates = self.record["gates"]
        self.assertEqual(gates["turma_display_gate"], "PENDING")
        self.assertEqual(gates["mass_materialization_preflight"], "NOT_RUN")
        self.assertEqual(gates["new_materialized"], 0)
        self.assertIs(gates["sd_changed"], False)
        self.assertIs(gates["firmware_changed"], False)

    def test_checkpoint_hashes_and_counts(self):
        self.assertEqual(self.checkpoint["files"]["CC_MASS_RATIFICATION_RECORD.json"], sha("CC_MASS_RATIFICATION_RECORD.json"))
        self.assertEqual(self.checkpoint["files"]["CC_MASS_RATIFICATION_RECORD.md"], sha("CC_MASS_RATIFICATION_RECORD.md"))
        self.assertIs(self.checkpoint["checks"]["all_group_hashes_match"], True)
        self.assertIs(self.checkpoint["checks"]["physical_baselines_unchanged"], True)
        self.assertEqual(self.checkpoint["checks"]["projected_cc"], "702/636")


if __name__ == "__main__":
    unittest.main()
