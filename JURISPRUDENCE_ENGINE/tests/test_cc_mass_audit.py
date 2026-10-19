"""CC mass audit: the 932 relations reconciled one by one; READY never holds a relation without merits, with an invalid target, a known
conflict, the CC/1916 read as CC/2002 or a Turma acórdão labelled as a qualified precedent; human status always pending; frozen baselines
intact; outputs reproducible."""
import collections
import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
OUT = ENG / 'CC_MASS_DISCOVERY'
sys.path.insert(0, str(ENG))
import batch_engine as E  # noqa: E402
import build_cc_mass_audit as A  # noqa: E402

LOCAL = [ENG / 'stj/_local/STJ_ESPELHOS_TURMAS_CC2002_INDEX.json', OUT / '_local/CC_MASS_DISCOVERY_RAW_FULL.jsonl', A.CC_TEXT]
READY = ('READY_FOR_BLOCK_DECISION', 'READY_WITH_QUALIFICATION')


def jl(p):
    return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]


class CCMassAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = jl(OUT / 'CC_MASS_AUDIT_ALL_932.jsonl')
        cls.q = jl(OUT / 'CC_MASS_DISCOVERY_QUALIFIED.jsonl')
        cls.m = json.loads((OUT / 'CC_MASS_AUDIT_METRICS.json').read_text(encoding='utf-8'))
        cls.ready = json.loads((OUT / 'CC_MASS_RATIFICATION_READY.json').read_text(encoding='utf-8'))
        cls.index = {t['target_id'] for t in json.loads((ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json')
                                                        .read_text(encoding='utf-8'))['targets']}

    @unittest.skipUnless(all(p.is_file() for p in LOCAL), 'dados locais não versionados ausentes (índice das Turmas / RAW completo / corpus do CC)')
    def test_up_to_date(self):
        r = subprocess.run([sys.executable, '-B', str(ENG / 'build_cc_mass_audit.py'), '--check'], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, 'UP_TO_DATE'), r.stderr[-1500:])

    def test_932_reconciled(self):
        ids = [r['id'] for r in self.rows]
        self.assertEqual(len(ids), 932)
        self.assertEqual(len(set(ids)), 932)                                   # no id duplicated
        self.assertEqual(set(ids), {x['id'] for x in self.q})                  # no id lost
        self.assertEqual((self.m['INPUT_RELATIONS'], self.m['RECONCILED_RELATIONS']), (932, 932))
        self.assertEqual(sum(self.m[s] for s in A.STATES), 932)
        for r in self.rows:
            self.assertIn(r['editorial_state'], A.STATES, r['id'])

    def test_sources_and_identity(self):
        for r in self.rows:
            self.assertTrue(r['identity']['source_hashes'], r['id'])
            self.assertTrue(all(A.official(u) for u in r['identity']['url']), r['id'])
        man = json.loads((OUT / 'CC_MASS_AUDIT_SHA256.json').read_text(encoding='utf-8'))
        for k, h in man['outputs'].items():
            self.assertEqual(hashlib.sha256((OUT / k).read_bytes().replace(b'\r\n', b'\n')).hexdigest(), h, k)

    def test_ready_is_safe(self):
        for r in self.rows:
            if r['editorial_state'] not in READY:
                continue
            c = r['checks']
            self.assertIn(r['published_pair']['target'], self.index, r['id'])           # no invalid target in READY
            sub = (r.get('turma') or {}).get('substitution')
            merits, temporal = (sub['proposed_merits'], sub['proposed_temporal']) if r['published_pair']['precedent'] != r['precedent'] else                 (c['MERITS'], c['TEMPORAL'])                                         # the relation that would be published
            self.assertEqual(merits, 'MERITS', r['id'])                                # no decision without merits
            self.assertNotIn(temporal, ('PRE_CC2002', 'POSSIBLE_CC1916', 'AMBIGUOUS_CODE_NAMESPACE', 'ALTERED_AFTER_JUDGMENT'), r['id'])
            t = r.get('turma')
            if t:
                self.assertNotIn(t['classification'], ('POTENTIAL_DIVERGENCE', 'SUPERIOR_AUTHORITY_CONFLICT'), r['id'])   # no known conflict ignored
            if r['editorial_state'] == 'READY_FOR_BLOCK_DECISION':
                self.assertIn(r['authority'], ('QUALIFIED_PRECEDENT', 'SUMULA_STJ', 'CONCENTRATED_REVIEW'), r['id'])
                self.assertNotEqual(c['TEMPORAL'], 'CC1916_CORRESPONDENCE', r['id'])   # the old code never goes in the block

    def test_cc1916_never_read_as_cc2002(self):
        cases = [("A aplicação do art. 1178, parágrafo único do CC, no sentido de subsistir a doação. Interpretação do parágrafo único do art. 1178, "
                  "do CC16 (atual art. 551 do CC/2002).", 'CC2002:ART.1178'),
                 ("Não configura violação ao art. 1.521, inciso I, do antigo Código Civil.", 'CC2002:ART.1521'),
                 ("a letra do art. 1.132 do Código Civil de 1.916.", 'CC2002:ART.1132'),
                 ("art. 1.611, § 1º, do Código Civil revogado", 'CC2002:ART.1611'),
                 ("do art. 1.287 do Código civil de 1916. Interpretação com a norma do art. 633 do mesmo diploma legal", 'CC2002:ART.633'),
                 ("pela lei francesa (art. 488 do Código Civil Francês)", 'CC2002:ART.488'),
                 ("arts. 119 a 123 do Código de Processo Civil/2015", 'CC2002:ART.119'),
                 ("Na linha do EAREsp n. 600.811/SP, prevalece a última decisão", 'CC2002:ART.600')]
        for text, target in cases:
            self.assertEqual([z for z, _ in A.locate(text, target) if z not in ('CLAIM', 'QUESTION')], [], text)
        self.assertEqual(A.locate('nos termos do art. 202, VI, do Código Civil.', 'CC2002:ART.202')[0][0], 'HOLDING')
        for r in self.rows:
            if r['checks']['TEMPORAL'] == 'CC1916_CORRESPONDENCE' and r['editorial_state'] in READY:
                self.assertTrue(any('Código Civil de 1916' in n or 'norma anterior' in n for n in r['reader_notes']), r['id'])

    def test_claims_questions_and_bars(self):
        self.assertEqual(A.locate('O recorrente alegou violação ao art. 692 do Código Civil.', 'CC2002:ART.692')[0][0], 'CLAIM')
        self.assertEqual(A.locate('Fica prejudicada a análise autônoma do art. 844 do Código Civil.', 'CC2002:ART.844')[0][0], 'CLAIM')
        self.assertEqual(A.locate('Cinge-se a controvérsia ao quórum exigido no art. 1.061 do Código Civil.', 'CC2002:ART.1061')[0][0], 'QUESTION')
        self.assertEqual(A.locate('Há duas questões em discussão: (i) saber se houve omissão; (ii) a penhora de quotas contraria os arts. 805 do CPC e '
                                  '1.026 do CC.', 'CC2002:ART.1026')[0][0], 'QUESTION')
        self.assertEqual(A.locate('Qualificada a causa como lesão (art. 171, II, do CC), incide o prazo quadrienal; a pretensão de reenquadramento '
                                  'demanda revolvimento fático-probatório.', 'CC2002:ART.171')[0][0], 'HOLDING')

    def test_turma_identity_and_labels(self):
        for r in self.rows:
            is_turma = r['sources'] == ['STJ_ESPELHOS_TURMAS']
            self.assertEqual(r['authority'] == 'TURMA_ACORDAO', is_turma, r['id'])
            if is_turma:
                self.assertIn(r['identity']['orgao'], ('TERCEIRA TURMA', 'QUARTA TURMA'), r['id'])
                self.assertNotIn(r['identity']['classe'], A.QUALIFIED_KINDS | {'SUMULA'}, r['id'])   # never a repetitivo by mistake
                if r['editorial_state'] in READY:
                    self.assertEqual(r['editorial_state'], 'READY_WITH_QUALIFICATION', r['id'])
                    self.assertTrue(any('Turma' in n and 'persuasiva' in n for n in r['reader_notes']), r['id'])

    def test_human_status_pending(self):
        for r in self.rows:
            self.assertEqual((r['human_decision'], r['human_approved']), ('PENDING', False), r['id'])
        for i in self.ready['items']:
            self.assertEqual(i['DECISAO_HUMANA'], 'PENDING')
        self.assertEqual((self.m['RATIFIED_NEW_RELATIONS'], self.m['DEPLOYED_NEW_RELATIONS']), (0, 0))

    def test_reader_notes_have_no_internal_metadata(self):
        for i in self.ready['items']:
            self.assertFalse(re.search(r'TIER|READY|PROVISIONAL|BLOCKED|NEEDS_|sha256|hash|score|flag', i['NOTA_NECESSARIA'], re.I), i['ID'])

    def test_packets(self):
        ids_ready = {i['ID'] for i in self.ready['items']}
        seen = collections.Counter()
        files = sorted(OUT.glob('CC_MASS_RATIFICATION_PACKET_*.md'))
        self.assertEqual(len(files), self.m['RATIFICATION_PACKET_COUNT'])
        for n, f in enumerate(files, 1):
            rows = [l for l in f.read_text(encoding='utf-8').splitlines() if l.startswith('| CCMD-')]
            self.assertLessEqual(len(rows), 200, f.name)
            turma = sum('persuasivo de Turma' in l for l in rows)
            self.assertIn(turma, (0, len(rows)), f.name)                       # never mixes Turma with qualified precedents
            for l in rows:
                seen[l.split('|')[1].strip()] += 1
                self.assertTrue(l.rstrip().endswith('| PENDING |'), l[:40])
        self.assertEqual(set(seen), ids_ready)
        self.assertEqual(max(seen.values()), 1)

    def test_deep_sample_design(self):
        d = json.loads((OUT / 'CC_MASS_DEEP_AUDIT_SAMPLE.json').read_text(encoding='utf-8'))
        sam = {s['id'] for s in d['sample']}
        q = {x['id']: x for x in self.q}
        self.assertGreaterEqual(len(sam), 200)
        self.assertTrue({i for i, x in q.items() if x['tier'] == 'A'} <= sam)
        self.assertTrue({i for i, x in q.items() if x['tribunal'] == 'STF'} <= sam)
        self.assertGreaterEqual(sum(1 for i in sam if q[i]['sources'] == ['STJ_ESPELHOS_TURMAS']), 120)
        self.assertGreaterEqual(sum(1 for i in sam if q[i]['sources'] != ['STJ_ESPELHOS_TURMAS']), 50)
        self.assertEqual([v['n'] for v in self.m['VALIDATION']], [40, 30])

    def test_frozen_baselines(self):
        self.assertEqual((self.m['CURRENT_CC_PHYSICAL'], self.m['CURRENT_CF_PHYSICAL'], self.m['CF_REGRESSION'], self.m['CC_J1_J2_REGRESSION'],
                          self.m['FROZEN_LAYER_CHANGES'], self.m['SD_CHANGED'], self.m['FIRMWARE_CHANGED']), ('49/39', '315/198', 0, 0, 0, 'NO', 'NO'))
        _, _, rows = E.physical_layer(ENG / 'CC_J2_MATERIALIZATION_CANDIDATE/candidate/SD')
        cc = {(r['target_id'], r['precedent_id']) for r in rows if r['target_id'].startswith('CC2002:')}
        self.assertEqual((len(cc), len({t for t, _ in cc})), (49, 39))
        self.assertEqual(len(rows) - len(cc), 315)
        r = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', 'JURISPRUDENCE_ENGINE/CC_J2_MATERIALIZATION_CANDIDATE', 'JURISPRUDENCE_ENGINE/CC_J2_PHYSICAL_DEPLOY',
                            'DEVICE_INTEGRATION/staging_article_index_cc', 'firmware'], cwd=ROOT)
        self.assertEqual(r.returncode, 0)


if __name__ == '__main__':
    unittest.main()
