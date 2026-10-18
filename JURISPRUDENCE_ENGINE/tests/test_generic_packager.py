"""Generic multinorm packager: reproduces the CF J2I baseline (315/198) semantically in a normalized layer with ZERO duplicate query keys,
handles CF88 + ADCT + CC2002, shares one ficha across norms, fails closed. Host-only; the legacy J2I files are never touched."""
import collections
import hashlib
import json
import sys
import unittest
from pathlib import Path

ENG = Path(__file__).resolve().parents[1]
ROOT = ENG.parent
sys.path[:0] = [str(ENG), str(ENG / 'firmware_multinorm'), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import generic_packager as P  # noqa: E402
import multinorm_sim as S  # noqa: E402
import juris_types as JT  # noqa: E402
import build_j2_batch as G  # noqa: E402

CC_FILE = '/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'
CF_FILE = '/1- CONSTITUIÇÃO FEDERAL/cf.txt'


def parse(files):
    look = [l.split('|') for l in files[P.LAYER + '/JUR_LOOKUP.IDX'].decode('utf-8').split('\n')[1:] if l]
    return look, files[P.LAYER + '/JURISPRUDENCIA.IDX']


def sim_pkg(files, card):
    return S.Package(files[P.LAYER + '/JUR_LOOKUP.IDX'], files[P.LAYER + '/JURISPRUDENCIA.IDX'],
                     card | {k.split('/')[-1] for k in files if k.startswith(P.CONTENT)})


class CFReproduction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rels, cls.prec = P.cf_fixture()
        cls.card = P.card_fichas()
        cls.files = P.package(cls.rels, cls.prec, cls.card, provisional_ids=P.provisional_ids(), known_targets=P.known_targets())
        cls.look, cls.records = parse(cls.files)
        cls.pkg = sim_pkg(cls.files, cls.card)

    def test_zero_duplicate_keys_and_counts(self):
        keys = [tuple(l[:5]) for l in self.look]
        self.assertEqual(len(keys), len(set(keys)))                                     # DUPLICATE_QUERY_KEYS_IN_OUTPUT = 0
        m = json.loads(self.files[P.LAYER + '/MULTINORM_MANIFEST.json'])
        self.assertEqual(m['totals']['DUPLICATE_QUERY_KEYS'], 0)
        self.assertEqual(sum(v['relations'] for v in m['norms'].values()), 315)          # CF_RELATIONS_REPRODUCED 315/315
        self.assertEqual(sum(v['targets_with_j'] for v in m['norms'].values()), 198)      # CF_TARGETS_REPRODUCED 198/198
        self.assertEqual(sorted(m['norms']), ['ADCT', 'CF88'])
        self.assertEqual(m['totals']['fichas_new'], 0)                                   # CF_FICHAS_IDENTICAL: every ficha already on the card

    def test_every_relation_reachable_with_identical_label_and_ficha(self):
        legacy = P.legacy_records()
        for r in self.rels:
            norma, art, par, inc, ali = P.query_key(r['target_id']).split('|')
            st = S.carregar(self.pkg, CF_FILE if norma == 'CF88' else S.CF_RUNTIME, art, par, inc, ali, in_adct=norma == 'ADCT')
            if norma == 'ADCT':                                  # ADCT: served by LEXV1 on the device; the normalized layer still holds it
                hit = self.pkg.exact('ADCT', art, par, inc, ali)
                rows = [S.relation(l, '') for l in self.pkg.rows(*hit)]
            else:
                rows = st['relations']
            match = [x for x in rows if x['arquivo'] == JT.ficha(r['precedent_id'])]
            self.assertEqual(len(match), 1, r)
            lg = legacy[r['precedent_id']]
            self.assertEqual(match[0]['label'], JT.label(lg['tipo'], lg['tribunal'], lg['numero']))    # CF_LABELS_IDENTICAL (device label)
            self.assertIn(match[0]['arquivo'], self.card)
        recs = [l.split('|') for l in self.records.decode('utf-8').split('\n')[1:] if l]
        self.assertEqual(sorted(x[5] for x in recs), sorted(r['ref_label'] for r in self.rels))     # titles identical to the J2I REF_PAYLOAD

    def test_back_identical_and_only_documented_merge(self):
        by_key = collections.defaultdict(list)
        for r in self.rels:
            by_key[P.query_key(r['target_id'])].append(r)
        merged = {k: sorted({r['target_id'] for r in v}) for k, v in by_key.items() if len({r['target_id'] for r in v}) > 1}
        self.assertEqual(merged, {'CF88|62|||': ['CF88:ART.62', 'CF88:ART.62:CAPUT']})   # article unit + caput share the reading position
        for k, v in by_key.items():
            norma, art, par, inc, ali = k.split('|')
            if norma != 'CF88':
                continue
            st = S.carregar(self.pkg, CF_FILE, art, par, inc, ali)
            self.assertEqual([x['arquivo'] for x in st['relations']], [JT.ficha(r['precedent_id']) for r in v])   # LEXV1 order kept
            self.assertEqual(S.carregar(self.pkg, CF_FILE, art, par, inc, ali)['relations'], st['relations'])     # BACK -> same list

    def test_legacy_files_untouched(self):
        self.assertEqual(hashlib.sha256(G.J2I_PAYLOAD.read_bytes()).hexdigest(), G.J2I_PAYLOAD_SHA)
        self.assertFalse([k for k in self.files if '05_INDICES_ESP32' in k])


class Multinorm(unittest.TestCase):
    def test_cf_adct_cc_shared_ficha_and_failures(self):
        rels, prec = P.cf_fixture()
        prec = dict(prec)
        prec['STJ:SUMULA:403'] = dict(tipo='sumula', tribunal='STJ', numero='403', status='vigente', titulo='Súmula 403 STJ', fonte='https://x')
        cc = [dict(norm='CC2002', target_id='CC2002:ART.927:PAR.UNICO', precedent_id='STF:RG:932'),
              dict(norm='CC2002', target_id='CC2002:ART.186', precedent_id='STJ:SUMULA:403'),
              dict(norm='CC2002', target_id='CC2002:ART.927', precedent_id='STJ:SUMULA:403'),
              dict(norm='CC2002', target_id='CC2002:ART.186', precedent_id='STJ:SUMULA:403')]          # repeated link counts once
        card = P.card_fichas()
        files = P.package(rels + cc, prec, card, new_fichas={'STJ_SUMULA_403.TXT': 'SÚMULA 403 DO STJ\n'}, known_targets=P.known_targets())
        m = json.loads(files[P.LAYER + '/MULTINORM_MANIFEST.json'])
        self.assertEqual((m['norms']['CC2002']['relations'], m['norms']['CC2002']['targets_with_j'], m['norms']['CC2002']['fichas']), (3, 3, 2))
        self.assertEqual((m['norms']['CF88']['relations'], m['norms']['ADCT']['relations']), (311, 4))
        self.assertIn('STF_RG_932.TXT', m['fichas_shared_across_norms'])                  # 1 record, N targets, N norms
        self.assertEqual([k for k in files if k.startswith(P.CONTENT)], [P.CONTENT + '/STJ_SUMULA_403.TXT'])   # one ficha for two targets
        pkg = sim_pkg(files, card)
        a = S.carregar(pkg, CF_FILE, '7', inc='XXVIII')
        b = S.carregar(pkg, CC_FILE, '927', par='unico')
        c = S.carregar(pkg, CC_FILE, '186')
        d = S.carregar(pkg, CF_FILE, '7', inc='XXVIII')
        self.assertEqual(a, d)                                                             # CC -> CF: unchanged
        self.assertEqual([x['label'] for x in b['relations']], ['RG TEMA 932'])
        self.assertEqual(b['relations'][0]['arquivo'], [x for x in a['relations'] if x['numero'] == '932'][0]['arquivo'])
        self.assertEqual([x['label'] for x in c['relations']], ['Súmula 403 STJ'])
        self.assertEqual(S.carregar(pkg, '/3-CÓDIGO PROCESSO CIVIL/codigo_processo_civil.txt', '1')['branch'], 'PREVIOUS_FLOW')
        bad = [dict(target_id='CC2002:ART.9999', precedent_id='STF:RG:932')]
        with self.assertRaises(P.PackagerError):
            P.package(bad, prec, card, known_targets=P.known_targets())                    # target inexistente
        with self.assertRaises(P.PackagerError):
            P.package([dict(target_id='CC2002:ART.1', precedent_id='XXX:ADI:1')], dict(prec, **{'XXX:ADI:1': dict(prec['STF:RG:932'], tribunal='XXX')}), card)
        with self.assertRaises(P.PackagerError):
            P.package([dict(target_id='CC2002:ART.1', precedent_id='STJ:SUMULA:403')], prec, card)                    # ficha ausente


if __name__ == '__main__':
    unittest.main()
