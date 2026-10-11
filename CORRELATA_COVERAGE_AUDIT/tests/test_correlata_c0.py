"""CF88_CORRELATA_COVERAGE_AUDIT_C0: determinism, preservation of the current CORRELATA layer, universe and candidate invariants.

Runs on versioned files + inputs/CORRELATA_EVIDENCE_PIN.json only (no SD, no legacy folders)."""
import csv
import io
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1]
ROOT = AUDIT.parent
sys.path.insert(0, str(AUDIT / 'tools'))
import build_correlata_evidence_pin as P  # noqa: E402
import correlata_coverage_audit as A  # noqa: E402

FILES = SUMMARY = AUD = None


def setUpModule():
    global FILES, SUMMARY, AUD
    AUD = A.Audit()
    FILES, SUMMARY = AUD.build()


def load(name):
    return json.loads(FILES[name].decode('utf-8'))


def git_show(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], cwd=ROOT, capture_output=True, check=True).stdout


class Determinism(unittest.TestCase):
    def test_second_build_is_byte_identical(self):
        files2, _ = A.build_files()
        self.assertEqual(sorted(files2), sorted(FILES))
        for k in FILES:
            self.assertEqual(files2[k], FILES[k], k)

    def test_committed_artifacts_are_the_build(self):
        for k, v in FILES.items():
            self.assertEqual((AUDIT / k).read_bytes().replace(b'\r\n', b'\n'), v, k)     # checkout may use autocrlf

    def test_no_clock_in_artifacts(self):
        for k, v in FILES.items():
            self.assertNotRegex(v.decode('utf-8'), r'generated_at|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', k)


class Preservation(unittest.TestCase):
    def test_operational_reference_files_byte_identical_to_baseline_commit(self):
        for p in A.OPERATIONAL_FILES:
            blob = git_show(A.BASELINE['head'], p).replace(b'\r\n', b'\n')
            self.assertEqual((ROOT / p).read_bytes().replace(b'\r\n', b'\n'), blob, p)

    def test_the_44_visible_links_do_not_change(self):
        exp = json.loads((A.RUN3 / 'CF88_REFERENCES_EXPORT.json').read_text(encoding='utf-8'))
        cor = [l for ls in exp['references'].values() for l in ls if l['reference_type'] == 'CORRELATA']
        vis = sorted(l['reference_id'] for l in cor if l['visibility'] == 'CURRENT_VISIBLE')
        self.assertEqual(len(vis), 44)
        self.assertEqual(len(cor), 46)
        base = load(A.OUT['baseline'])
        self.assertEqual(sorted(b['reference_id'] for b in base['links'] if b['visibility'] == 'CURRENT_VISIBLE'), vis)
        self.assertEqual(base['counts']['visible'], 44)
        self.assertEqual(base['counts']['targets_visible'], len({l['target_id'] for l in cor if l['visibility'] == 'CURRENT_VISIBLE'}))

    def test_run3_rebuild_in_temp_dir_and_card_equality(self):
        pres = load(A.OUT['baseline'])['preservation']
        self.assertTrue(pres['run3_rebuilt_in_temp_dir_byte_identical'])
        self.assertTrue(all(pres['run3_ref_files_equal_card'].values()))
        self.assertTrue(pres['device_tables_equal_card'])
        self.assertTrue(pres['runtime_sha_equals_device_targets_source'])

    def test_current_links_resolve_on_the_device(self):
        for b in load(A.OUT['baseline'])['links']:
            self.assertTrue(b['relation_row_on_card'] and b['destination_in_ext_normas'] and b['destination_file_on_card'], b['reference_id'])
            self.assertEqual(b['reachable_device_v1'], b['visibility'] == 'CURRENT_VISIBLE', b['reference_id'])

    def test_nothing_promoted(self):
        for n in (A.OUT['baseline'], A.OUT['universe'], A.OUT['candidates'], A.OUT['queue']):
            self.assertEqual(load(n)['promoted'], 0)
        for sec in ('HIGH', 'MEDIUM', 'LOW'):
            self.assertTrue(all(q['decision'] is None for q in load(A.OUT['queue'])[sec]))


class UniverseAndTargets(unittest.TestCase):
    def test_universe_partition(self):
        u = load(A.OUT['universe'])
        ids = [r['target_id'] for r in u['auditable']] + [r['target_id'] for r in u['excluded']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(AUD.rt) | set(AUD.engine_idx))
        for r in u['auditable']:
            self.assertEqual(r['legal_status'], 'CURRENT', r['target_id'])
            self.assertNotIn(r['kind'], ('CAPUT', 'NORMA', 'NAMESPACE'))
            self.assertIn(r['target_id'], AUD.text_map)                       # reachable: own line in the card TEXT_MAP

    def test_no_invalid_target_in_candidates_or_matrix(self):
        for c in AUD.candidates:
            self.assertIn(c['target_id'], AUD.rt, c['candidate_id'])
            self.assertIn(c['canonical_target_id'], AUD.rt, c['candidate_id'])
        rows = list(csv.DictReader(io.StringIO(FILES[A.OUT['matrix']].decode('utf-8'))))
        self.assertEqual(len(rows), SUMMARY['auditable_targets'])
        for r in rows:
            self.assertIn(r['target_id'], AUD.rows)
            self.assertIn(r['coverage_status'], A.COVERAGE[:5])
        for s in AUD.rejected:
            self.assertNotIn(s['raw_target'], AUD.rt)

    def test_historical_or_revoked_never_visible_candidates(self):
        q = load(A.OUT['queue'])
        queued = [x for sec in ('HIGH', 'MEDIUM', 'LOW') for x in q[sec]]
        for x in queued:
            t = x['target_id'][:-len(':CAPUT')] if x['target_id'].endswith(':CAPUT') else x['target_id']
            self.assertIn(t, AUD.rows, x['candidate_id'])
            self.assertEqual(AUD.legal[x['target_id']], 'CURRENT')
        for c in AUD.candidates:
            if c['candidate_status'].startswith('EXCLUDED_TARGET') or c['candidate_status'] == 'HISTORICAL_NORM_EXCLUDED':
                self.assertFalse(c['promotable_to_human_review'], c['candidate_id'])
                self.assertIsNone(c['review_priority'])


class ArtCaput(unittest.TestCase):
    def test_no_candidate_duplicated_between_art_and_caput(self):
        keys = [(c['target_id'], c['norm_key'] or tuple(c['norm_labels_seen'])) for c in AUD.candidates]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertFalse(any(c['target_id'].endswith(':CAPUT') for c in AUD.candidates))
        for c in AUD.candidates:
            if c['canonical_target_id'] != c['target_id']:
                self.assertEqual(c['canonical_target_id'], c['target_id'] + ':CAPUT')

    def test_matrix_has_no_caput_rows(self):
        rows = list(csv.DictReader(io.StringIO(FILES[A.OUT['matrix']].decode('utf-8'))))
        self.assertFalse(any(r['target_id'].endswith(':CAPUT') for r in rows))
        self.assertEqual(sum(1 for r in rows if r['kind'] == 'ARTIGO'), SUMMARY['auditable_structural_articles'])


class Classification(unittest.TestCase):
    def test_mentions_and_reservations(self):
        m = A.mentions('criado pela Lei Complementar nº 7, de 7 de setembro de 1970, e a Lei nº 9.296/1996 e a EC 132/2023')
        self.assertEqual([k for k, *_ in m], ['LC:7/1970', 'LEI:9296/1996', 'EC:132/2023'])
        self.assertEqual(A.mentions('Lei nº 11.417')[0][0], 'LEI:11417/?')
        self.assertEqual([k for k, _ in A.reservations('Todos são iguais perante a lei')], [])
        self.assertEqual([k for k, _ in A.reservations('§ 1º Lei complementar disporá sobre:')], ['LEI_COMPLEMENTAR'])
        self.assertEqual([k for k, _ in A.reservations('na forma da lei, ressalvadas')], ['LEI_GENERICA'])

    def test_vide_notes_are_not_constitutional_text(self):
        for tid, notes in AUD.vide.items():
            self.assertNotRegex(AUD.text[tid], r'(?i)^\s*\(?\s*vide\b')
        vide = [s for s in AUD.signals if s['source'] == 'RUNTIME_EDITORIAL_VIDE']
        self.assertTrue(vide)
        self.assertTrue(all(s['family'] == 'S2_NOTA_EDITORIAL_VIDE' and s['confidence'] == 'C' for s in vide))

    def test_reverse_remission_parser(self):
        h = P.reverse_remissions('X', 'Regula o acesso a informações previsto no inciso XXXIII do art. 5º , no inciso II do § 3º do art. 37 e no '
                                      '§ 2º do art. 216 da Constituição Federal. Art. 1º Esta Lei dispõe.')
        self.assertEqual(sorted(t for x in h for t in x['targets']), ['CF88:ART.216:PAR.2', 'CF88:ART.37:PAR.3:INC.II', 'CF88:ART.5:INC.XXXIII'])
        self.assertTrue(all(x['region'] == 'EMENTA' and x['verb_class'] == 'REGULAMENTA' for x in h))     # 'Regula ... previsto no'
        amend = P.reverse_remissions('X', 'Art. 1º Esta Lei. Art. 107. A Lei nº 9.029 passa a vigorar com as seguintes alterações: “Art. 1º É proibida, '
                                          'ressalvadas as hipóteses previstas no inciso XXXIII do art. 7º da Constituição Federal.” (NR)')
        self.assertEqual([x['status'] for x in amend], ['IN_AMENDMENT_BLOCK'])

    def test_unidentified_norms_are_not_promotable(self):
        for c in AUD.candidates:
            if not c['norm_identified']:
                self.assertFalse(c['promotable_to_human_review'], c['candidate_id'])
            if c['promotable_to_human_review']:
                self.assertRegex(c['norm_key'], r'^(LEI|LC|DL|DEC|DLEG|MP|LDEL):\d+/\d{4}$')
                self.assertIn(c['confidence'], ('A', 'B', 'C'))
                self.assertIn(c['relation_type'], A.RELATION_TYPES[:7])

    def test_topical_only_never_in_the_queue(self):
        q = load(A.OUT['queue'])
        queued = {x['candidate_id'] for sec in ('HIGH', 'MEDIUM', 'LOW') for x in q[sec]}
        for c in AUD.candidates:
            if c['confidence'] == 'D' or c['relation_type'] == 'TOPICAL_ONLY':
                self.assertNotIn(c['candidate_id'], queued)
                self.assertFalse(c['promotable_to_human_review'])
        self.assertEqual(len(queued), SUMMARY['new_candidates'])

    def test_no_correlata_relevant_never_inferred_from_absence(self):
        self.assertEqual(SUMMARY['coverage_status_counts']['NO_CORRELATA_RELEVANT'], 0)

    def test_current_links_keep_their_status(self):
        rows = {r['target_id']: r for r in csv.DictReader(io.StringIO(FILES[A.OUT['matrix']].decode('utf-8')))}
        for b in load(A.OUT['baseline'])['links']:
            if b['visibility'] == 'CURRENT_VISIBLE':
                t = b['target_id'][:-len(':CAPUT')] if b['target_id'].endswith(':CAPUT') else b['target_id']
                self.assertEqual(rows[t]['coverage_status'], 'HAS_VALIDATED_CORRELATA')

    def test_report_numbers_match_summary(self):
        rep = FILES[A.OUT['report']].decode('utf-8')
        for k in ('auditable_targets', 'new_candidates', 'high', 'medium', 'low', 'generic_legislative_reservation', 'ingestion_required',
                  'device_resolvable_now'):
            self.assertRegex(rep, rf'\|\s*\**{SUMMARY[k]}\**\s*\|', k)


class Pin(unittest.TestCase):
    def test_pin_device_tables_match_the_card_manifest(self):
        pin = AUD.pin
        for rel, h in pin['device_tables']['sha256'].items():
            self.assertEqual(pin['physical_sd']['files'][rel]['sha256'], h, rel)
        self.assertTrue(all(c['card_identical'] for c in pin['relations_v2_package']['files'].values()))
        self.assertEqual(len(pin['relations_v2_package']['ext_normas']), 20)

    def test_pin_sources_have_hashes(self):
        for s in AUD.pin['sources']:
            self.assertRegex(s['sha256'], r'^[0-9a-f]{64}$', s['path'])


if __name__ == '__main__':
    unittest.main()
