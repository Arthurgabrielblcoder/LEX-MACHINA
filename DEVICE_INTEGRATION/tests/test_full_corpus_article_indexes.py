"""End-to-end acceptance tests for the full-corpus ARTICLE_SEARCH indexes.

These tests intentionally use the last read-only physical-SD backup as the corpus
and the candidate staging as the product under test.  Nothing here opens or writes
the physical card.  The suite checks every binary record, not merely file presence.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "DEVICE_INTEGRATION" / "tools"
LT = ROOT / "LEGAL_TARGET_ID"
sys.path[:0] = [str(TOOLS), str(LT), str(ROOT / "updater")]

import article_index_corpus as C  # noqa: E402
import article_index_loader_model as LM  # noqa: E402
import build_article_search_index as AI  # noqa: E402
import build_target_index as BTI  # noqa: E402
import structure_parser as SP  # noqa: E402


STAGING = ROOT / "DEVICE_INTEGRATION" / "staging_article_indexes_full_corpus_candidate"
CORPUS = ROOT / "DEVICE_INTEGRATION" / "backups" / "sd_20260929T163407Z" / "data"
APPROVED = ROOT / "DEVICE_INTEGRATION" / "staging_sd_v1_batch04_run3_candidate"
PHYSICAL_MANIFEST = ROOT / "DEVICE_INTEGRATION" / "backups" / "batch04_run3" / "sd_manifest_post.json"
TARGETS = STAGING / "SD" / C.SD_DIR


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FullCorpusArticleIndexes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((STAGING / "_host" / "ARTICLE_INDEX_MANIFEST.json").read_text(encoding="utf-8"))
        cls.discovery = C.discover(CORPUS)
        cls.located = {d["norma"]: Path(d["path"]) for d in cls.discovery if d["status"] == "LOCATED"}
        cls.located["CF88"] = APPROVED / "SD" / C.RUNTIME_REDIRECT["CF88"]
        cls.rows = {n: r for n, r in cls.manifest["norms"].items() if "index" in r}

    def test_01_discovery_eligibility_and_block(self):
        self.assertEqual(72, len(self.discovery))
        self.assertTrue(all(d["status"] == "LOCATED" for d in self.discovery))
        self.assertEqual(71, self.manifest["summary"]["indexes"])
        self.assertEqual(1, self.manifest["summary"]["BLOCKED"])
        maria = self.manifest["norms"]["MARIA2006"]
        self.assertEqual("SOURCE_NOT_PLAIN_TEXT", maria["blocked"]["reason"])
        self.assertFalse((TARGETS / "MARIA2006_ARTICLE_SEARCH.IDX").exists())

    def test_02_unique_namespaces_and_filenames(self):
        self.assertTrue(self.manifest["summary"]["namespaces_unique"])
        names = [r["index"]["file"] for r in self.rows.values()]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(self.rows), {Path(n).name.removesuffix(C.SUFFIX) for n in names})

    def test_03_manifest_file_sizes_and_hashes(self):
        self.assertEqual(72, len(self.manifest["files"]))  # 71 indexes + catalog
        for rel, expected in self.manifest["files"].items():
            data = (STAGING / "SD" / rel).read_bytes()
            self.assertEqual(expected["bytes"], len(data), rel)
            self.assertEqual(expected["sha256"], digest(data), rel)
        for norma, row in self.rows.items():
            src = self.located[norma].read_bytes()
            self.assertEqual(row["source_bytes"], len(src), norma)
            self.assertEqual(row["source_sha256"], digest(src), norma)

    def test_04_all_records_body_hash_source_binding_and_structure(self):
        checked = 0
        for norma, row in self.rows.items():
            src = self.located[norma].read_bytes()
            blob = TARGETS.joinpath(Path(row["index"]["file"]).name).read_bytes()
            idx = AI.ArticleIndex(blob, src)  # body hash and source size/SHA
            oracle = C.legacy_structural_scan(src)
            expected = {}
            for label, off in oracle:
                expected.setdefault(C._key(label), []).append(off)
            seen = {}
            for num, suffix, ns_i, offset, occurrence, reserved in idx.recs:
                key = (num, suffix)
                self.assertEqual(0, reserved, norma)
                self.assertLess(offset, len(src), norma)
                self.assertTrue(src[offset:offset + 16].decode("utf-8", "replace").lstrip().startswith("Art"), (norma, offset))
                self.assertLess(ns_i, len(idx.ns), norma)
                self.assertIn(idx.ns[ns_i], (norma, "ADCT"), norma)
                self.assertEqual(len(seen.get(key, [])), occurrence, (norma, key))
                seen.setdefault(key, []).append(offset)
                checked += 1
            self.assertEqual(expected, seen, norma)
            self.assertTrue(C.equivalence(blob, src)["ok"], norma)
        self.assertEqual(self.manifest["summary"]["records_total"], checked)

    def test_05_first_middle_last_and_special_cases_every_norm(self):
        for norma, row in self.rows.items():
            src = self.located[norma].read_bytes()
            idx = AI.ArticleIndex(TARGETS.joinpath(Path(row["index"]["file"]).name).read_bytes(), src)
            ordered = sorted(idx.recs, key=lambda r: r[3])
            for rec in (ordered[0], ordered[len(ordered) // 2], ordered[-1]):
                hit = idx.find(rec[0], rec[1], rec[3])
                self.assertIsNotNone(hit, (norma, rec))
                self.assertEqual(rec[3], hit[0], (norma, rec))
            for label in row["audit"].get("suffixed", []):
                key = C._key(label)
                self.assertIsNotNone(idx.find(*key), (norma, label))
            for label in row["audit"].get("repeated_keys", []):
                key = C._key(label)
                first = idx.find(*key)
                self.assertIsNotNone(idx.find(key[0], key[1], first[0] + 1), (norma, label))

    def test_06_thousands_absence_suffix_occurrence_and_ranges(self):
        high = {n for n, r in self.rows.items() if r["audit"].get("has_above_999")}
        self.assertEqual({"CC2002", "CPC2015", "LBI2015"}, high)
        for norma in high:
            row = self.rows[norma]
            src = self.located[norma].read_bytes()
            idx = AI.ArticleIndex(TARGETS.joinpath(Path(row["index"]["file"]).name).read_bytes(), src)
            nums = sorted({r[0] for r in idx.recs if r[1] == 0})
            high_keys = sorted({(r[0], r[1]) for r in idx.recs if r[0] > 999})
            for key in (high_keys[0], high_keys[len(high_keys) // 2], high_keys[-1]):
                self.assertIsNotNone(idx.find(*key), (norma, key))
            for n in (999, 1000):
                self.assertEqual(n in nums, idx.find(n) is not None, (norma, n))
        self.assertEqual(7, sum(len(r["audit"].get("revoked_collective_ranges", [])) for r in self.rows.values()))
        self.assertGreater(sum(len(r["audit"].get("suffixed", [])) for r in self.rows.values()), 900)

    def test_07_parser_opt_in_variants_and_false_remissions(self):
        cases = {
            "Art . 2º. Texto": (2, None),
            "Art. 22A. Texto": (22, "A"),
        }
        for raw, want in cases.items():
            m = SP.ART_RE_CS.match(SP.heading_variant(raw))
            self.assertIsNotNone(m, raw)
            self.assertEqual((int(m.group(1)), m.group(2)), want)
        self.assertEqual(("Art. 4-A. Texto", 2), SP.join_split_heading("Art. 4", ["o", "-A. Texto"]))
        self.assertEqual(("Art. 217.", 1), SP.join_split_heading("Art. 21", ["7"]))
        m = SP.ART_RE_CS.match("Art. 95 da Constituição")
        self.assertEqual("REMISSION_WORD", SP.remission_heading(m, "conforme", "texto"))
        self.assertFalse(SP.ART_RE_CS.match(SP.heading_variant("art. 2º da Lei")))

    def test_08_out_of_order_is_explicit_and_bounded(self):
        rows = {n: r["audit"]["out_of_order_headings"] for n, r in self.rows.items() if r["audit"].get("out_of_order_headings")}
        self.assertEqual(77, sum(rows.values()))
        self.assertEqual(18, rows["LRP1973"])
        self.assertEqual(17, rows["LIC2021"])
        self.assertEqual(11, rows["LBI2015"])
        self.assertEqual(7, rows["HEDIONDOS1990"])

    def test_09_legacy_three_level_classification_totals(self):
        legacy_fp = sum(r["audit"]["legacy_delta"]["legacy_only"] for r in self.rows.values())
        legacy_fn = sum(r["audit"]["legacy_delta"]["index_only"] for r in self.rows.values())
        self.assertEqual(1708, legacy_fp)  # LEGACY_FALSE_POSITIVE
        self.assertEqual(1858, legacy_fn)  # LEGACY_FALSE_NEGATIVE
        self.assertTrue(all(r["audit"]["equivalence"]["ok"] for r in self.rows.values()))  # no INDEX_ERROR

    def test_10_catalog_roundtrip_corruption_and_source_mismatch(self):
        blob = (TARGETS / C.CATALOG_NAME).read_bytes()
        entries = C.read_catalog(blob)
        self.assertEqual(71, len(entries))
        self.assertEqual(sorted((e["source_bytes"], e["source_sha256"], e["norma"]) for e in entries),
                         [(e["source_bytes"], e["source_sha256"], e["norma"]) for e in entries])
        bad = bytearray(blob)
        bad[-1] ^= 1
        with self.assertRaises(C.CorpusError):
            C.read_catalog(bytes(bad))
        cc_blob = (TARGETS / "CC2002_ARTICLE_SEARCH.IDX").read_bytes()
        with self.assertRaises(AI.IndexError_):
            AI.ArticleIndex(cc_blob, self.located["CP1940"].read_bytes())

    def test_11_loader_catalog_wrong_index_rejection_fallback_fd_psram(self):
        files = [(p.name, p.read_bytes()) for p in sorted(TARGETS.iterdir()) if p.is_file()]
        cc = self.located["CC2002"].read_bytes()
        ok = LM.select(files, len(cc), digest(cc), "CATALOG")
        self.assertEqual(("LOADED", "CC2002_ARTICLE_SEARCH.IDX"), (ok["state"], ok["index"]))
        self.assertEqual(1, ok["fd_peak"])
        self.assertEqual(len((TARGETS / ok["index"]).read_bytes()), ok["psram_bytes"])
        wrong = LM.select(files, len(cc), "00" * 32, "CATALOG")
        self.assertNotEqual("LOADED", wrong["state"])
        no_catalog = [(n, b) for n, b in files if n != C.CATALOG_NAME]
        fallback = LM.select(no_catalog, len(cc), digest(cc), "CATALOG")
        self.assertNotEqual("LOADED", fallback["state"])  # fail closed; never a different norm
        corrupt = bytearray(dict(files)[C.CATALOG_NAME]); corrupt[-1] ^= 1
        bad_files = [(n, bytes(corrupt) if n == C.CATALOG_NAME else b) for n, b in files]
        self.assertNotEqual("LOADED", LM.select(bad_files, len(cc), digest(cc), "CATALOG")["state"])

    def test_12_keep_rebuild_add_remove_blocked(self):
        with tempfile.TemporaryDirectory(prefix="lex-artidx-test-") as td:
            base = Path(td)
            corpus = base / "corpus"; corpus.mkdir()
            cc = corpus / "cc.txt"; cp = corpus / "cp.txt"
            cc.write_text("Art. 1º. A\nArt. 2º. B\n", encoding="utf-8")
            cp.write_text("Art. 1º. C\n", encoding="utf-8")
            paths = {"CC2002": cc, "CP1940": cp}
            locator = (lambda root: paths, lambda item, inv: [inv[item["id"]]])
            items = [{"id": "CC2002"}, {"id": "CP1940"}]
            out = base / "out"
            first = C.build_corpus(corpus, out, items=items, locator=locator)
            self.assertEqual(2, first["summary"]["ADD"])
            second = C.build_corpus(corpus, out, previous_dir=out, items=items, locator=locator)
            self.assertEqual(2, second["summary"]["KEEP"])
            cc.write_text("Art. 1º. A alterado\nArt. 2º. B\n", encoding="utf-8")
            third = C.build_corpus(corpus, out, previous_dir=out, items=items, locator=locator)
            self.assertEqual("REBUILD", third["norms"]["CC2002"]["status"])
            fourth = C.build_corpus(corpus, out, previous_dir=out, items=[items[0]], locator=locator)
            self.assertEqual("REMOVE", fourth["norms"]["CP1940"]["status"])
            cc.write_bytes(b"header\n\xff\xfe<\x00h\x00t\x00m\x00l\x00>\x00 A\x00 r\x00 t\x00 .\x00 1\x00")
            fifth = C.build_corpus(corpus, out, previous_dir=out, items=[items[0]], locator=locator)
            self.assertEqual("BLOCKED", fifth["norms"]["CC2002"]["status"])

    def test_13_binary_corruption_is_rejected(self):
        blob = bytearray((TARGETS / "CC2002_ARTICLE_SEARCH.IDX").read_bytes())
        blob[-1] ^= 1
        with self.assertRaises(AI.IndexError_):
            AI.ArticleIndex(bytes(blob), self.located["CC2002"].read_bytes())

    def test_14_approved_cf_and_cc_are_byte_identical(self):
        for norma in ("CF88", "CC2002"):
            candidate = (TARGETS / f"{norma}{C.SUFFIX}").read_bytes()
            approved = (APPROVED / "SD" / C.SD_DIR / f"{norma}{C.SUFFIX}").read_bytes()
            self.assertEqual(digest(approved), digest(candidate), norma)
            self.assertEqual(approved, candidate, norma)

    def test_15_maria_signature_and_no_deceptive_index(self):
        row = self.manifest["norms"]["MARIA2006"]
        data = self.located["MARIA2006"].read_bytes()
        self.assertEqual(215426, len(data))
        self.assertEqual("a560439bfa7bbb6cfa77f42578bf1688183c9047004eb022af0a6444af5e775c", digest(data))
        self.assertIn("ÿþ".encode("utf-8"), data[:1000])
        blob, _, _, blocked = C.build_norm("MARIA2006", self.located["MARIA2006"])
        self.assertIsNone(blob)
        self.assertEqual("SOURCE_NOT_PLAIN_TEXT", blocked["reason"])
        self.assertEqual("BLOCKED", row["status"])

    def test_16_manifest_completeness_and_resource_accounting(self):
        s = self.manifest["summary"]
        self.assertEqual((72, 71, 2, 0, 69, 0, 1),
                         (s["norms_analysed"], s["indexes"], s["KEEP"], s["REBUILD"], s["ADD"], s["REMOVE"], s["BLOCKED"]))
        self.assertEqual(s["index_bytes_max"], s["psram_runtime_worst_bytes"])
        self.assertEqual(s["staging_bytes"], sum(x["bytes"] for x in self.manifest["files"].values()))
        self.assertEqual(1, max(LM.select([(p.name, p.read_bytes()) for p in TARGETS.iterdir() if p.is_file()],
                                         r["source_bytes"], r["source_sha256"], "CATALOG")["fd_peak"]
                                for r in self.rows.values()))

    def test_17_three_complete_generations_are_byte_identical(self):
        with tempfile.TemporaryDirectory(prefix="lex-artidx-determinism-") as td:
            trees = []
            for n in (1, 2, 3):
                out = Path(td) / str(n)
                C.build_corpus(CORPUS, out, previous_dir=APPROVED, physical_manifest=PHYSICAL_MANIFEST)
                trees.append(C.tree(out))
            self.assertEqual(74, len(trees[0]))  # 71 indexes + catalog + two host artifacts
            self.assertEqual(trees[0], trees[1])
            self.assertEqual(trees[0], trees[2])
            self.assertEqual(trees[0], C.tree(STAGING))


if __name__ == "__main__":
    unittest.main(verbosity=2)
