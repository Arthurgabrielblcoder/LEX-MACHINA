import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ENGINE = Path(__file__).resolve().parents[1]
ROOT = ENGINE.parent
MASS = ENGINE / "CC_MASS_MATERIALIZATION"
DISCOVERY = ENGINE / "CC_MASS_DISCOVERY"
sys.path[:0] = [str(ENGINE), str(ENGINE / "firmware_multinorm"), str(ROOT / "JURISPRUDENCE_AUDIT")]

import generic_packager as P
import juris_types as JT
import multinorm_sim as S


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class CCMassMaterializationPreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checkpoint = load(DISCOVERY / "CC_MASS_PREFLIGHT_CHECKPOINT.json")
        cls.summary = cls.checkpoint["summary"]
        cls.hosts = {name: load(MASS / name / "host/PREFLIGHT_RESULT.json") for name in ("HIGH_AUTHORITY", "TURMA", "COMBINED")}
        cls.manifests = {name: load(MASS / name / "SHA256_MANIFEST.json") for name in cls.hosts}
        cls.ratification = load(DISCOVERY / "CC_MASS_RATIFICATION_RECORD.json")
        cls.groups = load(DISCOVERY / "CC_MASS_RATIFICATION_GROUPS.json")
        combined = MASS / "COMBINED/candidate/SD" / P.LAYER
        card = load(ENGINE / "CC_J2_PHYSICAL_DEPLOY/sd_manifest_post_full.json")["entries"]
        fichas = {Path(path).name for path in card if path.startswith(P.CONTENT + "/")}
        fichas |= {path.name for path in (MASS / "SHARED_CONTENT").glob("*.TXT")}
        cls.package = S.Package((combined / "JUR_LOOKUP.IDX").read_bytes(), (combined / "JURISPRUDENCIA.IDX").read_bytes(), fichas)
        cls.group_items = {item["id"]: (group["group_id"], item) for group in cls.groups["groups"] for item in group["items"]}

    def test_authoritative_partition_and_projection(self):
        s = self.summary
        self.assertEqual((s["approved_relations"], s["held_relations"], s["high_relations"], s["turma_relations"]), (653, 28, 94, 559))
        self.assertEqual((s["new_targets"], self.checkpoint["cc_ratified_projection"]), (597, "702/636"))
        self.assertEqual((self.checkpoint["cc_physical"], self.checkpoint["cf_adct_physical"], self.checkpoint["new_physical"]), ("49/39", "315/198", 0))

    def test_group_f_absent_from_every_candidate(self):
        held_ids = {item["id"] for item in self.ratification["relations"] if item["group_id"] == "GROUP_F"}
        self.assertEqual(len(held_ids), 28)
        for host in self.hosts.values():
            ids = {item["id"] for item in host["relation_manifest"]}
            self.assertFalse(ids & held_ids)
            self.assertEqual(host["checks"]["group_f_relations"], 0)

    def test_candidate_counts_and_distinct_precedents(self):
        expected = {"HIGH_AUTHORITY": (94, 70), "TURMA": (559, 504), "COMBINED": (653, 574)}
        for name, (relations, precedents) in expected.items():
            checks = self.hosts[name]["checks"]
            self.assertEqual((checks["approved_relations_input"], checks["distinct_precedents"]), (relations, precedents))
            self.assertEqual(checks["approved_relations_visible"], f"{relations}/{relations}")

    def test_targets_cache_and_capacity(self):
        c = self.hosts["COMBINED"]["checks"]
        self.assertEqual((self.summary["invalid_targets"], c["duplicate_query_keys"], c["lookup_lost_relations"]), (0, 0, 0))
        self.assertEqual((c["lookup_entries"], c["lookup_max"]), (833, 4096))
        self.assertEqual((c["max_relations_on_single_target"], c["targets_over_relation_limit"]), (17, 0))
        self.assertLess(c["psram_estimate_bytes"], 8 * 1024 * 1024)

    def test_current_cc_and_cf_are_preserved(self):
        s = self.summary
        self.assertEqual((s["current_cc_relations_preserved"], s["current_cc_targets_preserved"]), ("49/49", "39/39"))
        self.assertEqual((s["cf_relations_preserved"], s["cf_targets_preserved"]), ("315/315", "198/198"))

    def test_group_e_uses_only_replacement_for_replaced_target(self):
        combined = {(row["target"], row["precedent"]): row for row in self.hosts["COMBINED"]["relation_manifest"]}
        group_e = [row for row in self.ratification["relations"] if row["group_id"] == "GROUP_E"]
        self.assertEqual(len(group_e), 76)
        for row in group_e:
            publication = row["replacement_publication"]
            self.assertIn((row["target"], publication["publish_precedent"]), combined)
            self.assertNotIn((row["target"], publication["superseded_candidate"]), combined)
            self.assertFalse(publication["publish_superseded_candidate"])
        self.assertEqual(self.summary["replacement_publication_errors"], 0)

    def test_extended_schema_is_optional_and_complete_for_turma(self):
        layer = load(MASS / "COMBINED/candidate/SD" / P.LAYER / "MULTINORM_MANIFEST.json")
        extension = layer["optional_display_extension"]
        self.assertEqual(extension["fields"], ["ORGAO", "DATA", "NATUREZA"])
        self.assertTrue(extension["backward_compatible"])
        self.assertEqual(self.summary["missing_display_metadata"], 0)

    def _state_for(self, item):
        key = P.query_key(item["target"]).split("|")
        return S.carregar(self.package, "/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt", *key[1:])

    def test_turma_display_fixtures_and_back(self):
        approved = [(group, item) for rel_id, (group, item) in self.group_items.items()
                    if self.ratification["relations"][[x["id"] for x in self.ratification["relations"]].index(rel_id)]["decision"] == "HUMAN_APPROVED"]
        fixtures = {
            "third": next(item for group, item in approved if group in {"GROUP_C", "GROUP_D", "GROUP_E"} and item["orgao"] == "TERCEIRA TURMA"),
            "fourth": next(item for group, item in approved if group in {"GROUP_C", "GROUP_D", "GROUP_E"} and item["orgao"] == "QUARTA TURMA"),
            "aresp": next(item for group, item in approved if group in {"GROUP_C", "GROUP_D", "GROUP_E"} and item["classe"] == "ARESP"),
            "group_c": next(item for group, item in approved if group == "GROUP_C"),
            "group_d": next(item for group, item in approved if group == "GROUP_D"),
            "group_e": next(item for group, item in approved if group == "GROUP_E"),
        }
        for item in fixtures.values():
            state = self._state_for(item)
            filename = JT.ficha(item["precedent"])
            index = next(i for i, row in enumerate(state["relations"]) if row["arquivo"] == filename)
            relation = state["relations"][index]
            self.assertTrue(relation["label"].startswith("STJ "))
            self.assertNotIn("OUTRO", relation["label"])
            self.assertLessEqual(len(relation["label"]), 34)
            self.assertTrue(S.open_and_back(self.package, state, index)["opened"])
            ficha = (MASS / "SHARED_CONTENT" / filename).read_text(encoding="utf-8")
            for field in ("TRIBUNAL:", "ÓRGÃO JULGADOR:", "CLASSE:", "NÚMERO:", "DATA:", "NATUREZA:"):
                self.assertIn(field, ficha)
            self.assertIn("PERSUASIVA — NÃO VINCULANTE", ficha)
            self.assertNotIn("HUMAN_APPROVED", ficha)

    def test_turma_reader_notes_preserve_group_semantics(self):
        c_note = next(item["reader_note"] for group in self.groups["groups"] if group["group_id"] == "GROUP_C" for item in group["items"])
        d_note = next(item["reader_note"] for group in self.groups["groups"] if group["group_id"] == "GROUP_D" for item in group["items"])
        all_fichas = "\n".join(path.read_text(encoding="utf-8") for path in (MASS / "SHARED_CONTENT").glob("*.TXT"))
        self.assertIn(c_note, all_fichas)
        self.assertIn(d_note, all_fichas)

    def test_high_authority_is_data_only_compatible(self):
        records = (MASS / "HIGH_AUTHORITY/candidate/SD" / P.LAYER / "JURISPRUDENCIA.IDX").read_text(encoding="utf-8").splitlines()[1:]
        new_ids = {row["precedent"] for row in self.hosts["HIGH_AUTHORITY"]["relation_manifest"]}
        for line in records:
            fields = line.split("|")
            if fields[6] in new_ids:
                self.assertFalse(JT.label(fields[1], fields[2], fields[3]).startswith("OUTRO"))
        self.assertTrue(self.summary["high_authority_data_only_ready"])

    def test_manifests_cover_files_and_shared_content(self):
        for name, manifest in self.manifests.items():
            root = MASS / name
            for relative, metadata in manifest["files"].items():
                path = root / relative
                self.assertEqual(hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(), metadata["sha256"])
            for _, metadata in manifest["shared_content_refs"].items():
                path = MASS / metadata["repository_path"]
                self.assertEqual(hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(), metadata["sha256"])

    def test_rollback_and_normalized_replace_set(self):
        self.assertEqual(self.summary["normalized_files_to_replace"], 4)
        for host in self.hosts.values():
            paths = host["checks"]["files_to_replace"]
            self.assertEqual(len(paths), 4)
            self.assertTrue(all(path.startswith(P.LAYER + "/") for path in paths))
        report = (DISCOVERY / "CC_MASS_ROLLBACK_PLAN.md").read_text(encoding="utf-8")
        self.assertIn("CC `49/39`", report)
        self.assertIn("Não executado", report)

    def test_firmware_compile_and_margin(self):
        report = load(ENGINE / "firmware_turma_display/TURMA_DISPLAY_FIRMWARE_BUILD.json")
        self.assertFalse(report["flashed"])
        self.assertTrue(report["schema"]["backward_compatible"])
        self.assertGreater(report["after"]["app_partition_free"], 0)
        binary = ENGINE / "firmware_turma_display" / report["candidate"]["binary"]
        self.assertEqual(hashlib.sha256(binary.read_bytes()).hexdigest(), report["candidate"]["binary_sha256"])
        self.assertEqual(self.checkpoint["firmware_candidate_sha256"], report["candidate"]["binary_sha256"])

    def test_builders_are_deterministic_across_hash_seeds(self):
        script = ENGINE / "build_cc_mass_materialization.py"
        for seed in ("1", "777"):
            env = dict(os.environ, PYTHONHASHSEED=seed)
            result = subprocess.run([sys.executable, "-X", "utf8", str(script), "--check"], cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual((result.returncode, result.stdout.strip()), (0, "UP_TO_DATE"), result.stderr[-2000:])
        firmware = subprocess.run([sys.executable, "-X", "utf8", str(ENGINE / "firmware_turma_display/build_turma_display_candidate.py"), "--check"],
                                  cwd=ROOT, capture_output=True, text=True)
        self.assertEqual((firmware.returncode, firmware.stdout.strip()), (0, "UP_TO_DATE"), firmware.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
