"""BATCH04 + RUN3 CONSOLIDATION (final predeploy): end-to-end on the consolidated SD overlay candidate + the firmware source candidate.

Candidate: DEVICE_INTEGRATION/staging_sd_v1_batch04_run3_candidate (tools/build_batch04_run3_candidate.py; profile BATCH04_RUN3 of
build_sd_staging.py). Physical baseline overlay: staging_sd_v1 (RUN1, 163 ENTENDA). Nothing here touches the ESP32 or the SD card.
Layer 4 = WORK_REFERENCE rows of the query keys of the ACTIVE_TARGET (ART.n -> [ART.n, ART.n:CAPUT]); no inheritance.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(ROOT / 'ENTENDA_ENGINE'))
import build_article_search_index as AI  # noqa: E402
import build_sd_staging as SB  # noqa: E402
import context_parser_port as P  # noqa: E402
import device_lookup_simulator as S  # noqa: E402
import reader_viewport as V  # noqa: E402
import scroll_model as M  # noqa: E402

OUT = DI / 'staging_sd_v1_batch04_run3_candidate'
SDC = OUT / 'SD/99_LEX_V1'
SD1 = DI / 'staging_sd_v1/SD/99_LEX_V1'
RUN3 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run3'
B04 = ROOT / 'ENTENDA_ENGINE/derived/production_batch_04'
FW = ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE'
SRC = DI / 'backups/batch04_run3/src_candidate/LEX_MACHINA_DEVICE_V1_CANDIDATE'
CC_TXT = DI / 'backups/sd_20260929T163407Z/data/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'
CC_IDX = SDC / '10_TARGETS/CC2002_ARTICLE_SEARCH.IDX'
EXPECTED_FILES = ['00_SYS/LEXV1.VER', '00_SYS/LEX_DEVICE_MANIFEST.json', '05_TEXT/CF88_RUNTIME.txt', '10_TARGETS/CC2002_ARTICLE_SEARCH.IDX',
                  '10_TARGETS/CF88_ARTICLE_SEARCH.IDX', '10_TARGETS/CF88_TARGETS.IDX', '10_TARGETS/CF88_TEXT_MAP.IDX',
                  '20_REFERENCES/REF_LOOKUP.IDX', '20_REFERENCES/REF_PAYLOAD.IDX', '30_ENTENDA/ENTENDA_LOOKUP.IDX', '30_ENTENDA/ENTENDA_PAYLOAD.DAT']
SCOPE = ('25', '26', '27', '28', '29', '29-A', '30', '31', '32', '33', '34', '35', '36')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    return [l.split('|') for l in Path(p).read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]


def payload_records(sd):
    """explanation_id -> exact bytes of its ENTENDA payload record (via the lookup offsets)."""
    data = (sd / '30_ENTENDA/ENTENDA_PAYLOAD.DAT').read_bytes()
    return {r[3]: data[int(r[1]):int(r[1]) + int(r[2])] for r in rows(sd / '30_ENTENDA/ENTENDA_LOOKUP.IDX')}


def batch04_active():
    rs = [json.loads(l) for l in (B04 / 'CF88_BATCH_04.entenda.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    return {r['target_id']: r for r in rs if r['status'] == 'ACTIVE'}


@unittest.skipUnless((SDC / '10_TARGETS/CF88_TARGETS.IDX').is_file() and (SD1 / '05_TEXT/CF88_RUNTIME.txt').is_file(),
                     'consolidated staging candidate / physical baseline staging not built')
class ConsolidationEndToEndTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = V.Reader(SDC, artidx=SDC / '10_TARGETS/CF88_ARTICLE_SEARCH.IDX')
        cls.dev = S.Device(SDC)
        cls.b04 = batch04_active()
        cls.payload = payload_records(SDC)

    @classmethod
    def tearDownClass(cls):
        cls.dev.close()

    def land(self, n, suf=0):
        if suf:
            occ = self.r.index.find(int(n), suf, 0)[0]
            st = self.r.state(self.r.land_top(occ))
        else:
            st = self.r.search(n)
        self.assertIsNotNone(st, n)
        self.assertEqual(self.r.scanned_bytes, 0)                                    # indexed: never a text scan
        return st

    def entenda_ok(self, tid):
        e = self.dev.entenda(tid)
        self.assertIsNotNone(e, tid)
        exp = self.b04[tid]
        self.assertEqual(e['explanation_id'], exp['explanation_id'])
        self.assertEqual(e['review'], 'HUMAN_APPROVED_T1')
        self.assertTrue(e['blob'].startswith(f"@{exp['explanation_id']}\n".encode()))
        self.assertIn(exp['content']['o_que_diz'].encode('utf-8'), e['blob'])        # payload = the approved text
        return e

    # ---------------- 1-4: ENTENDA Batch04 ----------------
    def test_01_entenda_art25(self):
        st = self.land(25)
        self.assertEqual(st['active_target'], 'CF88:ART.25')
        self.assertTrue(st['entenda'])
        self.entenda_ok('CF88:ART.25')

    def test_02_entenda_art29A_and_block(self):
        st = self.land(29, suf=1)
        self.assertEqual(st['active_target'], 'CF88:ART.29-A')
        self.entenda_ok('CF88:ART.29-A')
        anchor = self.dev.entenda('CF88:ART.29-A:INC.I')
        for inc in ('II', 'III', 'IV', 'V', 'VI'):                                    # BLOCK: covered targets resolve to the anchor
            e = self.dev.entenda(f'CF88:ART.29-A:INC.{inc}')
            self.assertEqual((e['resolution_type'], e['explanation_id'], e['payload_offset']),
                             ('COVERED_BY_BLOCK', anchor['explanation_id'], anchor['payload_offset']))
        self.assertEqual(self.r.search_structural('29'), self.r.index.find(29, 0, 0)[0])  # keypad "29" -> CF88:ART.29, never 29-A

    def test_03_entenda_art34_cleanup(self):
        st = self.land(34)
        self.assertEqual(st['active_target'], 'CF88:ART.34')
        e = self.entenda_ok('CF88:ART.34')
        self.assertEqual(e['explanation_id'], 'ENTENDA/CF88:ART.34/BASE/3')
        self.assertIn('União restringe temporariamente a autonomia'.encode('utf-8'), e['blob'])
        self.assertNotIn(b'suspende temporariamente', e['blob'])
        e35 = self.entenda_ok('CF88:ART.35')
        self.assertIn('restringe temporariamente a autonomia do Município, nos limites necessários'.encode('utf-8'), e35['blob'])
        self.assertNotIn(b'suspende temporariamente', e35['blob'])

    def test_04_entenda_art36_and_historical(self):
        st = self.land(36)
        self.assertEqual(st['active_target'], 'CF88:ART.36')
        self.entenda_ok('CF88:ART.36')
        q = self.dev.query('CF88.36.IV')                                               # revoked: target exists, no CURRENT content
        self.assertEqual((q['legal_status'], q['entenda_available'], q['flags']), ('REVOKED', False, '------'))
        q = self.dev.query('CF88.28.PU')                                               # historical: not a runtime target at all
        self.assertEqual((q['status'], q['entenda_available']), ('INVALID_OR_UNKNOWN_TARGET', False))
        lookup = {r[0]: r for r in rows(SDC / '30_ENTENDA/ENTENDA_LOOKUP.IDX')}
        self.assertNotIn('CF88:ART.36:INC.IV', lookup)
        self.assertNotIn('CF88:ART.28:PAR.UNICO', lookup)

    def test_strong_sample_arts_25_to_36(self):
        tmap = {r[2] for r in rows(SDC / '10_TARGETS/CF88_TEXT_MAP.IDX')}
        for n in SCOPE:
            num, suf = (n.split('-')[0], 1) if '-' in n else (n, 0)
            st = self.land(num, suf)
            tid = f'CF88:ART.{n}'
            self.assertEqual(st['active_target'], tid, n)                              # landing on the article line, no stale target
            self.assertIn(tid, tmap)
            q = self.dev.query(tid)
            self.assertEqual(q['entenda_available'], tid in self.b04, n)
            if tid in self.b04:
                self.entenda_ok(tid)

    # ---------------- 5-12: References RUN3 ----------------
    def works(self, tid):
        return sorted(self.r.layer4(tid)[1])

    def test_05_ref_art37_no_inheritance(self):
        new = {'Os Donos do Poder', 'Raízes do Brasil'}
        self.assertTrue(new <= set(self.works('CF88:ART.37')))
        for child in ('CF88:ART.37:INC.I', 'CF88:ART.37:PAR.1', 'CF88:ART.37:PAR.6'):
            self.assertFalse(new & set(self.works(child)), child)                       # never inherited by incisos / paragraphs

    def test_06_07_08_ref_art43_and_62(self):
        self.assertIn('Formação Econômica do Brasil', self.works('CF88:ART.43'))
        self.assertIn('Vidas Secas', self.works('CF88:ART.43:PAR.2:INC.IV'))
        self.assertIn('Suzerain', self.works('CF88:ART.62'))
        self.assertIn('Eu, Daniel Blake', self.works('CF88:ART.201:INC.I'))
        self.assertIn('Frostpunk', self.works('CF88:ART.7:INC.XXXIII'))

    def test_09_ref_art193_after_search(self):
        st = self.land(193)
        self.assertEqual((st['active_target'], st['contexto']), ('CF88:ART.193', 'CF88:ART.193'))
        self.assertTrue(st['layer4'])
        self.assertEqual(sorted(st['works']), sorted(['Capital no Século XXI', 'Desigualdade para Todos', 'O Triunfo da Injustiça']))

    def test_10_ref_adct68(self):
        self.assertIn('Torto Arado', self.works('ADCT:ART.68'))

    def test_11_12_reference_gaps(self):
        for n in (98, 202):
            st = self.land(n)
            self.assertEqual(st['active_target'], f'CF88:ART.{n}')
            self.assertFalse(st['layer4'], n)                                          # CONFIRMED_REFERENCE_GAP: expected absence
            self.assertEqual(st['works'], [], n)

    def test_pending_and_rejected_works_stay_out(self):
        titles = {r[6] for r in rows(SDC / '20_REFERENCES/REF_PAYLOAD.IDX') if r[1] == 'WORK_REFERENCE'}
        for t in ('Sicko', 'SOS Saúde', 'Pro Dia Nascer Feliz', 'Borgen', 'Argentina, 1985'):
            self.assertFalse([x for x in titles if t.lower() in x.lower()], t)
        self.assertFalse(self.works('CF88:ART.196:CAPUT') and 'Sicko' in ' '.join(self.works('CF88:ART.196')))

    def test_18_excluded_temas_absent(self):
        refs = {r[4] for r in rows(SDC / '20_REFERENCES/REF_PAYLOAD.IDX')}
        for x in ('JURISPRUDENCE:STF:RG:113:CF88:25:-:-:-@CF88:ART.25', 'JURISPRUDENCE:STF:RG:756:CF88:31:3:-:-@CF88:ART.31:PAR.3'):
            self.assertNotIn(x, refs)
        excl = json.loads((RUN3 / 'CF88_REFERENCES_EXPORT.json').read_text(encoding='utf-8'))['excluded_links']
        self.assertEqual(len(excl), 2)

    def test_run3_counts_recomputed(self):
        pl = rows(SDC / '20_REFERENCES/REF_PAYLOAD.IDX')
        vis = [r for r in pl if r[2] == 'CURRENT_VISIBLE']
        wr = [r for r in vis if r[1] == 'WORK_REFERENCE']
        self.assertEqual(len(pl), 451)
        self.assertEqual(sum(1 for r in vis if r[1] == 'JURISPRUDENCE'), 277)
        self.assertEqual(sum(1 for r in vis if r[1] == 'CORRELATA'), 44)
        self.assertEqual(len(wr), 122)
        self.assertEqual(len(pl) - len(vis), 8)
        self.assertEqual(len({r[0] for r in wr}), 63)
        self.assertEqual(len({r[0].split(':')[1] for r in wr if r[0].startswith('CF88:')}), 33)
        self.assertEqual(len({r[0] for r in wr if r[0].startswith('ADCT:')}), 1)

    # ---------------- 13-17: search, CC, parser, scroll, loader ----------------
    def test_13_cf5_to_adct5(self):
        m = V.ArticleSearchV1(self.r).keys('ENTER', '5', 'ENTER')
        self.assertEqual(m.view()['active_target'], 'CF88:ART.5')
        m.keys('ENTER')
        self.assertEqual((m.buffer, m.repeat_ready), ('5', True))                      # REPEAT_READY
        m.keys('ENTER')
        self.assertEqual(m.view()['active_target'], 'ADCT:ART.5')
        m.keys('ENTER', 'ENTER')
        self.assertEqual(m.messages[-1], 'SEM OUTRA OCORRENCIA')

    @unittest.skipUnless(CC_TXT.is_file(), 'Codigo Civil TXT (local SD backup) not present')
    def test_14_15_cc_art2000_and_parser(self):
        data = CC_TXT.read_bytes()
        ai = AI.ArticleIndex(CC_IDX.read_bytes(), data)
        off = ai.find(2000)[0]
        self.assertEqual(off, 647337)
        c = dict(artigo='', paragrafo='', inciso='', alinea='')
        P.apply_line(c, data[off:data.index(b'\n', off)])
        self.assertEqual(c['artigo'], '2000')                                          # never ART.2
        self.assertEqual(sha(SRC / 'contexto_juridico.h'), sha(FW / 'contexto_juridico.h'))  # same thousands rule in the candidate

    @unittest.skipUnless(CC_TXT.is_file(), 'Codigo Civil TXT (local SD backup) not present')
    def test_16_scroll_deep_cc(self):
        data = CC_TXT.read_bytes()
        r = M.Reader(data, 'new')
        r.open_file()
        r.land_centered(647337)
        first = r.scroll(-1)
        self.assertLess(first['io'], 16 * 1024)
        self.assertEqual(first['perbyte'], 0)
        steps = [r.scroll(-1) for _ in range(30)] + [r.scroll(1) for _ in range(30)]
        self.assertLess(max(s['us'] for s in steps if s and s.get('moved')) / 1000.0, 80.0)
        self.assertNotIn(('2', '', '', ''), set(r.contexts()))

    def test_17_loader_cf_cc_cf(self):
        idx = {f'/99_LEX_V1/10_TARGETS/{p.name}': p.read_bytes() for p in (SDC / '10_TARGETS').glob('*_ARTICLE_SEARCH.IDX')}
        cf = (SDC / '05_TEXT/CF88_RUNTIME.txt').read_bytes()
        texts = {'CF': (len(cf), hashlib.sha256(cf).hexdigest()), 'CC': (660268, 'ad5ba178613b6181e2d8a61919eda0c6223c68feb6e47bef4ea65bc45c13e6ae')}

        def select(t):                                                                 # lexV1ArtIdxPronto: size, then text sha256
            n, h = texts[t]
            hits = [k for k, b in idx.items() if int.from_bytes(b[20:24], 'little') == n and b[24:56].hex() == h]
            return hits[0].rsplit('/', 1)[1] if len(hits) == 1 else None
        self.assertEqual([select(t) for t in ('CF', 'CC', 'CF', 'CC')],
                         ['CF88_ARTICLE_SEARCH.IDX', 'CC2002_ARTICLE_SEARCH.IDX', 'CF88_ARTICLE_SEARCH.IDX', 'CC2002_ARTICLE_SEARCH.IDX'])
        st = self.land(230)
        self.assertEqual(st['active_target'], 'CF88:ART.230')


@unittest.skipUnless((SDC / '00_SYS/LEX_DEVICE_MANIFEST.json').is_file() and (SD1 / '00_SYS/LEX_DEVICE_MANIFEST.json').is_file(),
                     'consolidated staging candidate / physical baseline staging not built')
class ConsolidationStagingTest(unittest.TestCase):
    def test_eleven_files(self):
        files = sorted(p.relative_to(SDC).as_posix() for p in SDC.rglob('*') if p.is_file())
        self.assertEqual(files, sorted(EXPECTED_FILES))
        man = json.loads((SDC / '00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
        for k, v in man['files'].items():
            if k != '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json':
                self.assertEqual(sha(OUT / 'SD' / k), v['sha256'], k)
        host = json.loads((OUT / '_host/STAGING_FILE_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual(host['file_count'], 11)
        self.assertTrue(host['byte_identical_rebuild'])

    def test_unchanged_runtime_and_textmap(self):
        for n in ('05_TEXT/CF88_RUNTIME.txt', '10_TARGETS/CF88_TEXT_MAP.IDX'):          # Lei Seca / CF runtime / ADCT
            self.assertEqual(sha(SDC / n), sha(SD1 / n), n)

    def test_refs_are_run3_and_indexes_are_the_validated_ones(self):
        sums = dict(reversed(l.split('  ', 1)) for l in (RUN3 / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines() if l.strip())
        for n in ('REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX'):
            self.assertEqual(sha(SDC / '20_REFERENCES' / n), sums[n], n)
        self.assertEqual(sha(SDC / '10_TARGETS/CF88_ARTICLE_SEARCH.IDX'), '56e437a0c9cebb113c47f6a7b100ee64363c63207a647eca0456e86d6db27fae')
        self.assertEqual(sha(SDC / '10_TARGETS/CC2002_ARTICLE_SEARCH.IDX'), '674c9971925c29aaca9685fb2d0b9515fe87e4072d644858ea27495c327d3a68')
        cf = (SDC / '10_TARGETS/CF88_ARTICLE_SEARCH.IDX').read_bytes()
        self.assertEqual((int.from_bytes(cf[16:20], 'little'), len(cf)), (424, 5216))
        cc = CC_IDX.read_bytes()
        self.assertEqual((int.from_bytes(cc[16:20], 'little'), len(cc)), (2077, 25036))

    def test_entenda_220_and_previous_byte_identical(self):
        man = json.loads((SDC / '00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual(man['entenda_explanation_count'], 220)                        # 154 sequential (1-24) + 9 pilots + 57 Batch04
        ver = (SDC / '00_SYS/LEXV1.VER').read_text(encoding='utf-8')
        self.assertIn('ENTENDA_COUNT|220\n', ver)
        self.assertIn('ENTENDA_SCOPE|CF88_ARTS_1_36_PLUS_APPROVED_PILOTS\n', ver)
        self.assertTrue(ver.startswith('#LEXMACHINA|DEVICE_VERSION|3\n'))
        old, new = payload_records(SD1), payload_records(SDC)
        self.assertEqual(len(old), 163)
        for eid, blob in old.items():
            self.assertEqual(new.get(eid), blob, eid)                                  # every previous explanation byte-identical
        added = set(new) - set(old)
        self.assertEqual(len(added), 57)
        self.assertEqual(added, {r['explanation_id'] for r in batch04_active().values()})

    def test_rich_header_matches_payload(self):
        hdr = (SRC / 'lex_ref_detail_data.h').read_text(encoding='utf-8')
        self.assertEqual(sha(SRC / 'lex_ref_detail_data.h'), sha(RUN3 / 'device_candidate/lex_ref_detail_data.RUN3_CANDIDATE.h'))
        # C adjacent literals ("Justi\xc3\xa7""a") are joined first; title and type may carry \x escapes
        entries = re.findall(r'\n  \{"([^"|]+)\|([^"]+)", "((?:[^"\\]|\\.)*)", "((?:[^"\\]|\\.)*)", (\d+), (-?\d+),', hdr.replace('""', ''))
        wr = [r for r in rows(SDC / '20_REFERENCES/REF_PAYLOAD.IDX') if r[1] == 'WORK_REFERENCE' and r[2] == 'CURRENT_VISIBLE']
        self.assertEqual(len(entries), 122)
        self.assertEqual(len(wr), 122)
        dec = lambda s: bytes(s, 'latin-1').decode('unicode_escape').encode('latin-1').decode('utf-8')  # noqa: E731
        self.assertEqual(sorted((t, w, dec(ti)) for t, w, ti, *_ in entries), sorted((r[0], r[5], r[6]) for r in wr))
        self.assertIn('#define LEXV1_REF_DETAIL_COUNT 122', hdr)
        with self.subTest('header regenerated'):
            out = subprocess.run([sys.executable, str(DI / 'tools/build_ref_detail_header.py'), '--payload', str(RUN3 / 'REF_PAYLOAD.IDX'),
                                  '--additions', str(ROOT / 'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json'), '--out',
                                  str(DI / '_tmp_hdr_check.h')], capture_output=True)
            try:
                self.assertEqual(out.returncode, 0)
                self.assertEqual(sha(DI / '_tmp_hdr_check.h'), sha(SRC / 'lex_ref_detail_data.h'))
            finally:
                (DI / '_tmp_hdr_check.h').unlink(missing_ok=True)

    def test_firmware_source_candidate(self):
        fw = {p.relative_to(FW).as_posix(): sha(p) for p in FW.rglob('*') if p.is_file()}
        current = {p.relative_to(SRC).as_posix(): sha(p) for p in SRC.rglob('*') if p.is_file()}
        # The approved r2 source remains immutable.  Full-corpus ARTICLE_SEARCH legitimately changes only the gated .ino loader;
        # generated reference headers must remain byte-identical to r2.
        self.assertEqual(set(fw), set(current))
        changed = {name for name in fw if fw[name] != current[name]}
        self.assertEqual({'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino'}, changed)
        ino = (FW / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
        self.assertIn('LEXV1_ARTCAT_CAMINHO', ino)
        self.assertIn('LXARTCT1', ino)
        self.assertIn('#define LEXV1_ARTSEARCH_LOG 0 ', ino)
        self.assertIn('#define LEX_SCROLL_PERF_LOG 0 ', ino)
        self.assertEqual(sha(FW / 'lex_ref_detail_data.h'), '2ca5820a170a3b08ecfa869685d319d65eee5bc94ddf0bfa5854282acce9710b')  # RUN3 (r2)

    def test_boot_diagnostic_cases_on_both_packages(self):
        """The boot self-test table of the candidate sketch must PASS on the candidate SD and on the baseline SD (DIAG fail=0)."""
        ino = (SRC / 'LEX_MACHINA_DEVICE_V1_CANDIDATE.ino').read_text(encoding='utf-8')
        cases = re.findall(r'\{"([A-Z0-9:.]+)",(true|false),LEXV1_RES_(NONE|DIRECT|COVERED_BY_BLOCK),"([A-Z0-9:.]*)",(\d+),(\d+)\}', ino)
        self.assertEqual(len(cases), 10)
        refs_calls = re.findall(r'lexv1References\(refLookup,&rp,"([A-Z0-9:.]+)",([zum])\);', ino)
        self.assertEqual(refs_calls, [('CF88:ART.21:INC.XXIV', 'z'), ('CF88:ART.127', 'u'), ('CF88:ART.37:PAR.6', 'm')])
        for sd in (SDC, SD1):
            dev = S.Device(sd)
            try:
                for tid, exists, res, anchor, refs, visible in cases:
                    q = dev.query(tid.replace(':ART.', '.').replace(':PAR.', '.').replace(':INC.', '.'))
                    self.assertEqual(q['status'] == 'OK', exists == 'true', (sd, tid))
                    self.assertEqual(q['resolution_type'], res, (sd, tid))
                    self.assertEqual(q.get('anchor_target_id') or '', anchor, (sd, tid))
                    rs = dev.references(tid) if exists == 'true' else []
                    self.assertEqual((len(rs), sum(r[2] == 'CURRENT_VISIBLE' for r in rs)), (int(refs), int(visible)), (sd, tid))
                self.assertEqual([len(dev.references(t)) for t, _ in refs_calls], [0, 1, 5], sd)
            finally:
                dev.close()

    def test_deterministic_rebuild(self):
        tmp = DI / '_tmp_consolidation_check'
        try:
            import build_batch04_run3_candidate as C
            SB.build(tmp, ref_dir=RUN3, require_committed_refs=False, reference_engine_version=C.ENGINE_VERSION, profile='BATCH04_RUN3',
                     build_commit=C.BUILD_COMMIT)
            a = {p.relative_to(tmp / 'SD').as_posix(): sha(p) for p in (tmp / 'SD').rglob('*') if p.is_file()}
            b = {p.relative_to(OUT / 'SD').as_posix(): sha(p) for p in (OUT / 'SD').rglob('*') if p.is_file()}
            self.assertEqual(a, b)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
