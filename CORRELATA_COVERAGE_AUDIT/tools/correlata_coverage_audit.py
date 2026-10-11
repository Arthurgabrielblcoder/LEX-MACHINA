"""CF88_CORRELATA_COVERAGE_AUDIT_C0 — coverage map and gaps of the CORRELATA layer (legislacao correlata) of CF/88 + ADCT.

DIAGNOSTIC ONLY. Reads versioned files + the evidence pin (inputs/CORRELATA_EVIDENCE_PIN.json) and writes the C0 artifacts of
CORRELATA_COVERAGE_AUDIT/. It never writes the Reference Engine catalogs/overlays, REF_LOOKUP/REF_PAYLOAD, the SD, firmware, ENTENDA
or the Lei Seca, and it promotes nothing (every candidate stays a candidate for human review).

Universe: the device runtime (DEVICE_INTEGRATION/runtime/CF88_RUNTIME.txt, the same bytes as the card) parsed by the approved parser;
legal status from the runtime itself (REVOKED/CURRENT, as CF88_TARGETS.IDX), engine status from LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS.
ART.n and ART.n:CAPUT are ONE presentation unit (the device shows both on the ART.n line): one audit row (ART.n), never two candidates.
Signals (kept separate, see SIGNALS): S1 legislative reservation in the constitutional text, S2 nominal remission in the constitutional
text, S3 approved ENTENDA (signal only), S4 acervo (reverse remission in corpus texts + availability), S5 Relations V2 legacy.
Classification: relation nature, confidence A/B/C/D, priority HIGH/MEDIUM/LOW, acervo/device status, coverage status per target.
Usage: python correlata_coverage_audit.py            (writes the artifacts; builds twice in memory and checks determinism)
       python correlata_coverage_audit.py --check    (rebuilds in memory and compares with the committed artifacts)
"""
import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
ROOT = AUDIT.parent
for p in ('LEGAL_TARGET_ID', 'DEVICE_INTEGRATION/tools', 'ENTENDA_ENGINE', 'updater'):
    sys.path.insert(0, str(ROOT / p))
import reference_engine as RE  # noqa: E402
import runtime_targets as RT  # noqa: E402
import target_id as T  # noqa: E402

MISSION = 'CF88_CORRELATA_COVERAGE_AUDIT_C0'
BASELINE = dict(branch_from='device-entenda-810', head='44ef69ba3957d9c55a6b4b5fe9f9f68fcd77efef',
                physical_tag='lex-device-v1-entenda-810-physical-approved-2026-10-11',
                legal_reconciliation='fa9719a6bd335275252473a5f154e4e11f5532f4')
PIN = AUDIT / 'inputs/CORRELATA_EVIDENCE_PIN.json'
RUNTIME = ROOT / 'DEVICE_INTEGRATION/runtime/CF88_RUNTIME.txt'
D = ROOT / 'LEGAL_TARGET_ID/derived'
RUN3 = D / 'export_test/run3'
RUN3_FILES = ('CF88_REFERENCES_EXPORT.json', 'REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX')
OPERATIONAL_FILES = ('LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json', 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS.json',
                     'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json', 'LEGAL_TARGET_ID/derived/export_test/run3/REF_LOOKUP.IDX',
                     'LEGAL_TARGET_ID/derived/export_test/run3/REF_PAYLOAD.IDX', 'LEGAL_TARGET_ID/derived/export_test/run3/CF88_REFERENCES_EXPORT.json',
                     'LEGAL_TARGET_ID/engine_config.json', 'LEGAL_TARGET_ID/reference_engine.py')
T1_CATALOG = ROOT / 'ENTENDA_ENGINE/editorial/T1_EXTERNAL_CATALOG.json'
BACKLOGS = ('ENTENDA_ENGINE/derived/production_batch_07_macro/BACKLOG_INPUT.json', 'ENTENDA_ENGINE/derived/production_batch_08_macro/BACKLOG_INPUT.json')
OUT = dict(baseline='CF88_CORRELATA_CURRENT_BASELINE.json', universe='CF88_CORRELATA_TARGET_UNIVERSE.json', candidates='CF88_CORRELATA_CANDIDATES.json',
           matrix='CF88_CORRELATA_COVERAGE_MATRIX.csv', queue='CF88_CORRELATA_REVIEW_QUEUE.json', report='CF88_CORRELATA_C0_REPORT.md')

SIGNALS = {
    'S1_RESERVA_LEGAL': 'remissao generica a lei no texto constitucional do proprio target (nunca vira norma especifica sozinha)',
    'S2_REMISSAO_NOMINAL': 'lei/LC/decreto citado por numero no texto constitucional do proprio target',
    'S2_NOTA_EDITORIAL_VIDE': "nota editorial 'Vide a Lei ...' da compilacao do Senado: sinal fraco (C), nao conta como familia independente",
    'S3_ENTENDA': 'mencao a norma no ENTENDA aprovado (conteudo + camadas externas), T1_EXTERNAL_CATALOG e backlog ENTENDA (sinal, nunca fonte)',
    'S4_ACERVO_REVERSO': 'norma do acervo (principal ou externa no cartao) que cita literalmente o dispositivo (citation_parser, fail closed)',
    'S5_RELATIONS_V2_LEGADO': 'registros das etapas 2D4..2E4 do Relations V2 (Camara leginfra / varredura reversa antiga): evidencia, nunca autoridade',
}
RELATION_TYPES = ('REGULAMENTA', 'COMPLEMENTA', 'IMPLEMENTA', 'PROCEDIMENTO', 'CONDIÇÃO_OU_EXCEÇÃO', 'ORGANIZA_INSTITUIÇÃO',
                  'EXECUTA_POLÍTICA_CONSTITUCIONAL', 'TOPICAL_ONLY', 'GENERIC_LEGISLATIVE_RESERVATION', 'NO_CORRELATA_RELEVANTE_IDENTIFICADA')
CONFIDENCE = {'A': 'EXPLICIT', 'B': 'DIRECT', 'C': 'PLAUSIBLE_REVIEW', 'D': 'TOPICAL_ONLY_REJECT'}
COVERAGE = ('HAS_VALIDATED_CORRELATA', 'HAS_CORRELATA_CANDIDATE', 'GENERIC_LEGISLATIVE_RESERVATION', 'NO_CORRELATA_RELEVANT', 'NEEDS_HUMAN_REVIEW',
            'HISTORICAL_OR_REVOKED_EXCLUDED', 'TECHNICAL_TARGET_EXCLUDED')
RANK = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
PRIO_RANK = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
RECENT_REFORM_NORMS = ('EC:132/2023', 'EC:136/2025', 'EC:137/2025', 'EC:138/2025', 'EC:139/2026', 'LC:214/2025', 'LC:227/2026')
PROCEDURAL = {'MS2009', 'ACAOPOP1965', 'CPC2015', 'CPP1941', 'JEC1995', 'JEF2001', 'JEFAZ2009', 'EXECFISC1980', 'PAF1999'}


class AuditError(RuntimeError):
    pass


def sha_b(b):
    return hashlib.sha256(b).hexdigest()


def sha(p):
    return sha_b(Path(p).read_bytes())


def clip(s, n=260):
    s = ' '.join(str(s or '').split())
    return s if len(s) <= n else s[:n - 1] + '…'


def jdump(o):
    return (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


# ===================================================================================================== norms
TYPE_NAMES = {'LEI': 'Lei', 'LC': 'Lei Complementar', 'DL': 'Decreto-Lei', 'DEC': 'Decreto', 'DLEG': 'Decreto Legislativo', 'MP': 'Medida Provisória',
              'EC': 'Emenda Constitucional', 'LDEL': 'Lei Delegada'}
NUM = r'(\d{1,3}(?:\.\d{3})+|\d{1,6})'
YEAR_TAIL = r'(?:\s*/\s*(\d{4})\b|,?\s*de\s+\d{1,2}(?:º|°|o)?(?:\s*\.)?\s+de\s+[a-zç]+\s+de\s+(\d{4})|,\s*de\s+(\d{4})\b|\s+de\s+(\d{4})\b)?'
MENTION = re.compile(r'\b(?P<t>Lei\s+Complementar|LC|Decreto-Lei|Decreto\s+Legislativo|Decreto|Medida\s+Provis[óo]ria|Emenda\s+Constitucional|EC|'
                     r'Lei\s+Delegada|Lei)\s*(?:n(?:º|°|o|\.º)?\.?\s*)?' + NUM + YEAR_TAIL, re.I)
TYPE_OF = {'lei complementar': 'LC', 'lc': 'LC', 'decreto-lei': 'DL', 'decreto legislativo': 'DLEG', 'decreto': 'DEC', 'medida provisória': 'MP',
           'medida provisoria': 'MP', 'emenda constitucional': 'EC', 'ec': 'EC', 'lei delegada': 'LDEL', 'lei': 'LEI'}
LEGACY_ID = re.compile(r'^(?:EXT_)?(LEI|LC|DEC|DL|DLEG|MP|EC|LCP)(\d+)_(\d{4})$')


def nkey(typ, num, year):
    return f'{typ}:{int(str(num).replace(".", ""))}/{year}' if year else f'{typ}:{int(str(num).replace(".", ""))}/?'


def nlabel(key):
    typ, rest = key.split(':', 1)
    num, year = rest.split('/')
    n = int(num)
    shown = f'{n:,}'.replace(',', '.') if typ in ('LEI', 'DL', 'DEC') and n >= 1000 else str(n)
    return f"{TYPE_NAMES[typ]} nº {shown}" + (f'/{year}' if year != '?' else '')


def mentions(text):
    """Every numbered norm mention in `text`: [(key, typ, matched_text, start, end)]; key year '?' when the text gives no year."""
    out = []
    for m in MENTION.finditer(text or ''):
        typ = TYPE_OF[' '.join(m.group('t').lower().split())]
        if typ == 'LEI' and re.match(r'\s*complementar', text[m.end('t'):], re.I):
            continue
        num = m.group(2)
        year = next((y for y in m.groups()[2:] if y), None)
        if typ in ('EC', 'LC') and m.group('t') in ('EC', 'LC') and not re.search(r'\d', num):
            continue
        out.append((nkey(typ, num, year), typ, m.group(0), m.start(), m.end()))
    return out


class Norms:
    """Norm identities known locally: main catalog (72), external norms on the card (20) and legacy destination ids (Relations V2)."""

    def __init__(self, pin):
        self.info = {}
        self.catalog_key = {}
        for c in pin['main_corpus']:
            if c['id'] == 'CF88':
                continue                                       # the Constitution itself is the origin, never a correlata destination
            m = re.match(r'^(Lei Complementar|Decreto-Lei|Decreto|Lei)\s+([\d.]+)/(\d{4})\s*-\s*(.+)$', c['nome'])
            if not m:
                raise AuditError(f"CATALOG_NAME_NOT_PARSED {c['id']}")
            key = nkey(TYPE_OF[m.group(1).lower()], m.group(2), m.group(3))
            self.catalog_key[c['id']] = key
            self._add(key, name=c['nome'], acervo='IN_MAIN_CORPUS', acervo_id=c['id'], on_card=bool(c.get('on_card')),
                      card_identical=bool(c.get('card_identical')), alias=m.group(4).strip(), validity='ACERVO_LOCAL_TEXTO_COMPILADO')
        self.ext = {}
        for n in pin['relations_v2_package']['ext_normas']:
            m = LEGACY_ID.match(n['id'])
            key = nkey(m.group(1), m.group(2), m.group(3))
            self.ext[n['id']] = key
            self._add(key, name=nlabel(key), acervo='EXTERNAL_ALREADY_INGESTED', acervo_id=n['id'], ementa=n.get('ementa'),
                      on_card=True, card_identical=bool(n['file_present']), indexed_articles=n['indexed_articles'],
                      validity='ACERVO_LOCAL_TEXTO_COMPILADO')
        for r in pin['legacy_relations']['records']:
            key = self.from_legacy(r['destino_norma'])
            if key and key not in self.info:
                self._add(key, name=nlabel(key), acervo='INGESTION_REQUIRED', acervo_id=None)
            if key and r.get('ementa') and not self.info[key].get('ementa'):
                self.info[key]['ementa'] = r['ementa']
            if key and r.get('vigencia_status'):
                self.info[key].setdefault('legacy_validity', set()).add(r['vigencia_status'])
        self.by_num = defaultdict(set)
        for k in self.info:
            typ, rest = k.split(':')
            self.by_num[(typ, rest.split('/')[0])].add(k)

    def _add(self, key, **kw):
        self.info.setdefault(key, {}).update(kw)

    def from_legacy(self, dest):
        if dest in self.catalog_key:
            return self.catalog_key[dest]
        if dest in self.ext:
            return self.ext[dest]
        m = LEGACY_ID.match(dest or '')
        if m:
            return nkey('LC' if m.group(1) == 'LCP' else m.group(1), m.group(2), m.group(3))
        return None

    def resolve_year(self, key):
        """'LEI:11417/?' -> the only known norm with that type and number (else unchanged: year unresolved)."""
        if not key.endswith('/?'):
            return key, None
        typ, rest = key.split(':')
        ks = self.by_num.get((typ, rest.split('/')[0]), set())
        if len(ks) == 1:
            return next(iter(ks)), 'YEAR_RESOLVED_BY_UNIQUE_LOCAL_NUMBER'
        return key, 'NORM_YEAR_NOT_IDENTIFIED'

    def acervo(self, key):
        if key is None or key.endswith('/?'):
            return dict(acervo_status='NOT_IDENTIFIED', device_status='NOT_IDENTIFIED', device_resolvable_now=False, acervo_id=None)
        i = self.info.get(key, {})
        a = i.get('acervo', 'INGESTION_REQUIRED')
        if a == 'EXTERNAL_ALREADY_INGESTED':
            ok = bool(i.get('card_identical') and i.get('indexed_articles'))
            return dict(acervo_status=a, device_status='DEVICE_RESOLVABLE_NOW' if ok else 'INGESTION_REQUIRED', device_resolvable_now=ok,
                        acervo_id=i['acervo_id'])
        if a == 'IN_MAIN_CORPUS':
            return dict(acervo_status=a, device_status='MAIN_CORPUS_ROUTE_REQUIRED', device_resolvable_now=False, acervo_id=i['acervo_id'])
        return dict(acervo_status='INGESTION_REQUIRED', device_status='INGESTION_REQUIRED', device_resolvable_now=False, acervo_id=None)

    def validity(self, key):
        i = self.info.get(key or '', {})
        if i.get('validity'):
            return i['validity']
        lv = i.get('legacy_validity') or set()
        if 'REVOGADA' in lv and 'SEM_REVOGACAO_EXPRESSA' in lv:
            return 'CONFLITO_NO_LEGADO'                          # -> EXTERNAL_VERIFICATION_REQUIRED, never excluded silently
        if 'REVOGADA' in lv:
            return 'REVOGADA_SEGUNDO_LEGADO'
        if 'SEM_REVOGACAO_EXPRESSA' in lv:
            return 'CAMARA_LEGADO_SEM_REVOGACAO_EXPRESSA'
        return 'SEM_EVIDENCIA_LOCAL'

    def name(self, key):
        return self.info.get(key, {}).get('name') or (nlabel(key) if key else None)


# catalog aliases (identity = the local master catalog). Only Estatuto da Magistratura is outside it (auditor knowledge, flagged).
CATALOG_SYNONYMS = {'CLT': 'CLT1943', 'Consolidação das Leis do Trabalho': 'CLT1943', 'ECA': 'ECA1990', 'CDC': 'CDC1990', 'CTN': 'CTN1966',
                    'Lei de Responsabilidade Fiscal': 'LRF2000', 'LGPD': 'LGPD2018', 'Lei Geral de Proteção de Dados': 'LGPD2018',
                    'Lei de Acesso à Informação': 'LAI2011', 'Estatuto do Idoso': 'IDOSO2003', 'Estatuto da Pessoa Idosa': 'IDOSO2003',
                    'Lei de Licitações': 'LIC2021', 'Lei de Improbidade': 'LIA1992', 'Lei de Improbidade Administrativa': 'LIA1992',
                    'Lei de Greve': 'GREVE1989', 'Lei de Execução Penal': 'LEP1984', 'Lei dos Crimes Hediondos': 'HEDIONDOS1990',
                    'Lei de Crimes Hediondos': 'HEDIONDOS1990', 'Lei de Inelegibilidade': 'INELEG1990', 'Lei das Inelegibilidades': 'INELEG1990',
                    'Lei das Eleições': 'ELEICOES1997', 'Lei dos Partidos Políticos': 'PARTIDOS1995', 'Lei de Drogas': 'DROGAS2006',
                    'Lei Maria da Penha': 'MARIA2006', 'Marco Civil da Internet': 'MCI2014', 'Estatuto da Cidade': 'CIDADE2001',
                    'Estatuto da Terra': 'TERRA1964', 'Código de Mineração': 'MINER1967', 'Estatuto do Desarmamento': 'ARMAS2003',
                    'Código Civil': 'CC2002', 'Código Penal': 'CP1940', 'Código de Processo Civil': 'CPC2015', 'Código de Processo Penal': 'CPP1941',
                    'Código Tributário Nacional': 'CTN1966', 'Código Eleitoral': 'CE1965', 'Código de Defesa do Consumidor': 'CDC1990',
                    'Estatuto da Criança e do Adolescente': 'ECA1990', 'Lei de Execução Fiscal': 'EXECFISC1980', 'Lei do Inquilinato': 'INQUIL1991',
                    'Lei de Arbitragem': 'ARBIT1996', 'Lei do Mandado de Segurança': 'MS2009', 'Lei da Ação Popular': 'ACAOPOP1965',
                    'Código Brasileiro de Aeronáutica': 'CBA1986', 'Lei de Tortura': 'TORTURA1997', 'Lei de Abuso de Autoridade': 'ABUSO2019'}
AUDITOR_ALIASES = {'Estatuto da Magistratura': 'LC:35/1979'}
GENERIC_HINT = re.compile(r'legisla[çc][ãa]o\s+(?:penal|civil|tribut[áa]ria|eleitoral|trabalhista|previdenci[áa]ria|espec[íi]fica|infraconstitucional|'
                          r'complementar|federal|ordin[áa]ria|processual|ambiental|financeira|urban[íi]stica)|lei\s+(?:complementar|espec[íi]fica|ordin[áa]ria|'
                          r'regulamentadora)\b|\bregulamenta[çc][ãa]o\b', re.I)


def alias_mentions(text, norms):
    out = []
    names = {**{a: ('CATALOG', norms.catalog_key[i]) for a, i in CATALOG_SYNONYMS.items()},
             **{i['alias']: ('CATALOG', k) for k, i in norms.info.items() if i.get('alias')},
             **{a: ('AUDITOR', k) for a, k in AUDITOR_ALIASES.items()}}
    for a in sorted(names, key=len, reverse=True):
        for m in re.finditer(r'(?<![\wÀ-ú])' + re.escape(a) + r'(?![\wÀ-ú])', text or ''):
            if any(s <= m.start() < e for _, _, _, s, e in out):
                continue
            src, k = names[a]
            out.append((k, src, a, m.start(), m.end()))
    return out


# ===================================================================================================== constitutional text
RESERVATION = (
    ('LEI_COMPLEMENTAR', re.compile(r'\blei(?:s)?\s+complementar(?:es)?\b', re.I)),
    ('LEI_ESPECIFICA', re.compile(r'\blei\s+espec[íi]fica\b', re.I)),
    ('LEI_FEDERAL', re.compile(r'\blei\s+federal\b', re.I)),
    ('LEI_LOCAL', re.compile(r'\blei(?:s)?\s+(?:estadua(?:l|is)|municipa(?:l|is)|distrita(?:l|is))\b|\blei\s+org[âa]nica\b', re.I)),
    ('LEI_ORCAMENTARIA', re.compile(r'\blei(?:s)?\s+or[çc]ament[áa]ri\w+|\blei\s+de\s+diretrizes\s+or[çc]ament[áa]rias|\bplano\s+plurianual\b', re.I)),
    ('LEI_GENERICA', re.compile(r'\bna\s+forma\s+d[ae]\s+lei\b|\bnos\s+termos\s+d[ae]\s+lei\b|\bna\s+forma\s+da\s+legisla[çc][ãa]o|\bnos\s+termos\s+da\s+legisla[çc][ãa]o|'
                                r'\b(?:a|da)\s+lei\b|\bem\s+lei\b|\bpor\s+lei\b|\bmediante\s+lei\b|\blei\s+ordin[áa]ria\b|\bde\s+lei\b|\blei\s+(?:dispor|regular|'
                                r'definir|estabelecer|fixar|criar|assegurar|punir|disciplinar|instituir|organizar|determinar|garantir|considerar|poder)\w*', re.I)),
)
VIDE_LINE = re.compile(r'^\s*\(?\s*Vide\b', re.I)
VIDE_INLINE = re.compile(r'\(\s*Vide\b[^()]*\)', re.I)
NOT_RESERVATION = re.compile(r'\bperante\s+a\s+lei\b|\bigualdade\s+(?:de\s+todos\s+)?perante\s+a\s+lei\b', re.I)
HISTORIC_CONTEXT = re.compile(r'revogad|extint|anterior\s+(?:à|a)\s+promulga|vigente\s+(?:à|na)\s+data|ficam?\s+mantid|prorrogad|at[ée]\s+\d{4}', re.I)


def reservations(text):
    t = NOT_RESERVATION.sub(' ', text)
    t = MENTION.sub(' ', t)                                   # nominal remissions are S2, not a generic reservation
    found = []
    for k, rx in RESERVATION:
        m = rx.search(t)
        if m:
            found.append((k, clip(t[max(0, m.start() - 60):m.end() + 60], 160)))
    if any(k != 'LEI_GENERICA' for k, _ in found):
        found = [f for f in found if f[0] != 'LEI_GENERICA' or not any(
            g[0] in ('LEI_COMPLEMENTAR', 'LEI_ESPECIFICA', 'LEI_FEDERAL', 'LEI_LOCAL', 'LEI_ORCAMENTARIA') for g in found)]
    return found


def display(tid):
    p = T.parse_target_id(tid)
    s = ('CF' if p['namespace'] == 'CF88' else 'ADCT') + (f" art. {p['article']}" if p['article'] else '')
    if p.get('caput'):
        s += ', caput'
    if p['paragraph']:
        s += ', p.u.' if p['paragraph'] == 'UNICO' else f", § {p['paragraph']}"
    if p['inciso']:
        s += f", {p['inciso']}"
    if p['alinea']:
        s += f", {p['alinea']})"
    return s


# ===================================================================================================== audit
class Audit:
    def __init__(self):
        self.pin = json.loads(PIN.read_text(encoding='utf-8'))
        self.norms = Norms(self.pin)
        self.notes = []

    # ----------------------------------------------------------------- preservation (operational files never touched)
    def preservation(self):
        dev = self.pin['device_tables']
        phys = self.pin['physical_sd']['files']
        reg = RE.TargetRegistry()
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / 'run3'
            RE.export('CF88', RE.build_links('CF88', reg), out, RE.link_exclusions('CF88', reg), RE.work_reference_additions('CF88', reg))
            rebuilt = {f: sha(out / f) for f in RUN3_FILES}
        committed = {f: sha(RUN3 / f) for f in RUN3_FILES}
        checks = dict(
            run3_rebuilt_in_temp_dir_byte_identical=rebuilt == committed,
            run3_ref_files_equal_card={f: committed[f] == phys[f'99_LEX_V1/20_REFERENCES/{f}']['sha256'] for f in RUN3_FILES[1:]},
            device_tables_equal_card=all(dev['sha256'][k] == phys[k]['sha256'] for k in dev['sha256']),
            runtime_sha_equals_device_targets_source=sha(RUNTIME) == dev['targets_header'][2].split('|')[1],
            operational_files_sha256={p: sha(ROOT / p) for p in OPERATIONAL_FILES})
        if not (checks['run3_rebuilt_in_temp_dir_byte_identical'] and all(checks['run3_ref_files_equal_card'].values())
                and checks['device_tables_equal_card'] and checks['runtime_sha_equals_device_targets_source']):
            raise AuditError(f'PRESERVATION_CHECK_FAILED {json.dumps(checks)[:600]}')
        checks['run3_sha256'] = committed
        return checks

    # ----------------------------------------------------------------- universe
    def build_universe(self):
        idx = RT.build_runtime_index(RUNTIME)
        self.idx = idx
        lines = RUNTIME.read_text(encoding='utf-8').split('\n')
        order = sorted(idx['targets'], key=lambda t: t['line_start'])
        starts = sorted({t['line_start'] for t in order})
        nxt = {s: (starts[i + 1] if i + 1 < len(starts) else len(lines)) for i, s in enumerate(starts)}
        # constitutional text of the target (its line block) WITHOUT the source's editorial notes ('Vide a Lei nº ...' lines and
        # '(Vide ...)' asides): notes are kept apart (self.vide) and never read as a remission of the constitutional text
        self.text, self.vide = {}, {}
        for t in idx['targets']:
            block = lines[t['line_start'] - 1:nxt[t['line_start']] - 1]
            notes = [l.strip() for l in block if VIDE_LINE.match(l)]
            body = ' '.join(l for l in block if not VIDE_LINE.match(l))
            notes += [m.group(0) for m in VIDE_INLINE.finditer(body)]
            self.text[t['target_id']] = ' '.join(VIDE_INLINE.sub(' ', body).split())
            self.vide[t['target_id']] = notes
        self.rt = {t['target_id']: t for t in idx['targets']}
        self.order = {t['target_id']: i for i, t in enumerate(idx['targets'])}
        self.legal = RT.runtime_status(idx)
        dev = self.pin['device_tables']
        self.dev_targets = dev['targets']
        self.text_map = set(dev['text_map_targets'])
        self.entenda_lookup = dev['entenda_lookup']
        if any(self.legal[t] != self.dev_targets[t]['legal_status'] for t in self.dev_targets):
            raise AuditError('RUNTIME_LEGAL_STATUS_DIVERGES_FROM_DEVICE_TARGETS')
        self.engine_idx = {t['target_id']: t for t in json.loads((D / 'CF88_TARGET_INDEX.json').read_text(encoding='utf-8'))['targets']}
        self.engine_status = json.loads((D / 'CF88_TARGET_STATUS.json').read_text(encoding='utf-8'))['targets']
        self.children = defaultdict(list)
        for t in idx['targets']:
            if t['parent_id']:
                self.children[t['parent_id']].append(t['target_id'])
        rows, excluded = {}, []
        for tid, t in self.rt.items():
            kind, ns = t['kind'], t['namespace']
            est = self.engine_status.get(tid, {}).get('status', 'NOT_IN_ENGINE_INDEX')
            base = dict(target_id=tid, namespace=ns, kind=kind, legal_status=self.legal[tid], engine_status=est)
            if kind in ('NORMA', 'NAMESPACE'):
                excluded.append(dict(base, coverage_status='TECHNICAL_TARGET_EXCLUDED', reason='NORMA_OU_NAMESPACE'))
            elif kind == 'CAPUT':
                excluded.append(dict(base, coverage_status='TECHNICAL_TARGET_EXCLUDED', reason='PRESENTATION_EQUIVALENCE_ART_CAPUT',
                                     folded_into=tid[:-len(':CAPUT')]))
            elif self.legal[tid] == 'REVOKED':
                excluded.append(dict(base, coverage_status='HISTORICAL_OR_REVOKED_EXCLUDED', reason='REVOGADO_NO_RUNTIME_MONOVIGENTE'))
            else:
                reach = tid in self.text_map
                rows[tid] = dict(base, audit_class='STRUCTURAL' if kind == 'ARTIGO' else 'CURRENT', display_target=display(tid),
                                 reachable_device=reach, presentation_pair=f'{tid}:CAPUT' if kind == 'ARTIGO' else None,
                                 engine_overlay_eligible=est in RE.ADDITION_TARGET_STATUS)
                if not reach:
                    raise AuditError(f'AUDITABLE_TARGET_NOT_REACHABLE {tid}')
        for tid, t in self.engine_idx.items():
            if tid in self.rt:
                continue
            est = self.engine_status.get(tid, {}).get('status')
            excluded.append(dict(target_id=tid, namespace=t['namespace'], kind=t['kind'], legal_status='NOT_IN_RUNTIME', engine_status=est,
                                 coverage_status='TECHNICAL_TARGET_EXCLUDED' if t['kind'] in ('NORMA', 'NAMESPACE') else 'HISTORICAL_OR_REVOKED_EXCLUDED',
                                 reason='AUSENTE_DO_RUNTIME (somente no indice legado; o aparelho nao consulta)'))
        self.rows = rows
        self.excluded = sorted(excluded, key=lambda r: (r['target_id'] not in self.order, self.order.get(r['target_id'], 0), r['target_id']))

    def row_of(self, tid):
        """Audit row of a target: ART.n:CAPUT -> ART.n (presentation unit); None when the target is not auditable."""
        if tid.endswith(':CAPUT'):
            tid = tid[:-len(':CAPUT')]
        return tid if tid in self.rows else None

    def has_subdivisions(self, art_tid):
        return any(not c.endswith(':CAPUT') for c in self.children.get(art_tid, [])) or any(self.children.get(f'{art_tid}:CAPUT', []))

    # ----------------------------------------------------------------- current baseline (44 visible + hidden)
    def build_baseline(self):
        exp = json.loads((RUN3 / RUN3_FILES[0]).read_text(encoding='utf-8'))
        links = [l for ls in exp['references'].values() for l in ls if l['reference_type'] == 'CORRELATA']
        rel = self.pin['relations_v2_package']
        relacoes = {r['relacao_id']: r for r in rel['relacoes']}
        ext = {n['id']: n for n in rel['ext_normas']}
        legacy = {r['relacao_id']: r for r in self.pin['legacy_relations']['records'] if r['set'] == '2E4_RELACOES_CF88'}
        rev = self._reverse_index()
        by_rel = defaultdict(list)
        for l in links:
            by_rel[l['source_reference_id']].append(l['target_id'])
        out = []
        for l in links:
            tid, rid, dest = l['target_id'], l['source_reference_id'], l['source_id']
            r = relacoes.get(rid)
            n = ext.get(dest)
            key = self.norms.ext.get(dest)
            in_rt = tid in self.rt
            reach = tid in self.text_map or (tid.endswith(':CAPUT') and tid[:-6] in self.text_map)
            flags_dev = self.dev_targets.get(tid if not tid.endswith(':CAPUT') else tid[:-6], {}).get('flags', '')
            cites = rev.get(key, {})
            if tid in cites:
                cite = 'DESTINO_CITA_O_TARGET'
            elif any(c.startswith(tid + ':') for c in cites):
                cite = 'DESTINO_CITA_SUBDIVISAO_DO_TARGET'
            elif any(c.rsplit(':', 1)[0] == tid.rsplit(':', 1)[0] and c != tid for c in cites):
                cite = 'DESTINO_CITA_SO_DISPOSITIVO_IRMAO'
            elif any(tid.startswith(c + ':') for c in cites):
                cite = 'DESTINO_CITA_O_DISPOSITIVO_SUPERIOR'
            else:
                cite = 'DESTINO_NAO_CITA_O_TARGET'
            flags = []
            if l['visibility'] != 'CURRENT_VISIBLE':
                flags.append('HIDDEN_HISTORICAL_TARGET (alvo HISTORICAL_ONLY; nao aparece no aparelho)')
            if len(by_rel[rid]) > 1:
                flags.append(f'FAN_OUT_MESMA_RELACAO_EM_{len(by_rel[rid])}_TARGETS (revisar especificidade)')
            if tid in self.rows and self.rows[tid]['kind'] == 'ARTIGO' and self.has_subdivisions(tid):
                flags.append('ARTICLE_LEVEL_LINK (artigo com subdivisoes: revisar target mais especifico)')
            if cite == 'DESTINO_CITA_SO_DISPOSITIVO_IRMAO':
                flags.append('DESTINO_REGULA_DISPOSITIVO_IRMAO (texto da norma cita outro dispositivo do mesmo nivel)')
            note = AUDITOR_FLAGS.get((tid, dest))
            if note:
                flags.append(f'INCONSISTENCIA_EVIDENTE_PARA_REVISAO: {note}')
            positive = AUDITOR_POSITIVE.get((tid, dest))
            if positive:
                flags.append(f'NOTA_DO_AUDITOR: {positive}')
            sibling = cite == 'DESTINO_CITA_SO_DISPOSITIVO_IRMAO'
            lc_res = any(r_[0] == 'LEI_COMPLEMENTAR' for r_ in reservations(self.text.get(tid, ''))) and (key or '').startswith('LC:')
            if sibling and lc_res:
                flags.append('CITA_IRMAO_MAS_O_TARGET_EXIGE_LC_E_O_DESTINO_E_LC (sem inconsistencia evidente)')
            plaus = ('OBSOLETE_HIDDEN' if l['visibility'] != 'CURRENT_VISIBLE' else 'NEEDS_REVIEW' if note or (sibling and not lc_res and not positive)
                     else 'PLAUSIBLE_STRONG' if cite in ('DESTINO_CITA_O_TARGET', 'DESTINO_CITA_SUBDIVISAO_DO_TARGET') else 'PLAUSIBLE_NOT_VERIFIED')
            lg = legacy.get(rid, {})
            out.append(dict(
                reference_id=l['reference_id'], target_id=tid, display_target=display(tid), relation_id=rid, destination_norm_id=dest,
                destination_norm_key=key, destination_norm_name=nlabel(key) if key else None, label=l['label'],
                provenance=dict(engine=l['provenance'], migration=l['migration'], legacy_relation_2e4=dict(
                    urls=lg.get('urls'), destino_artigos=lg.get('destino_artigos'), bindings=lg.get('bindings'))),
                target_engine_status=l['status'], target_runtime_status=self.legal.get(tid, 'NOT_IN_RUNTIME'), visibility=l['visibility'],
                reachable_device_v1=bool(in_rt and reach and l['visibility'] == 'CURRENT_VISIBLE'), device_target_flags=flags_dev or None,
                device_flag_C=('C' in flags_dev[1:2]) if flags_dev else False,
                relation_row_on_card=bool(r), relation_mode=r['modo'] if r else None, relation_dest_articles=r['artigos_destino'] if r else None,
                dest_articles_indexed=all(a in rel['ext_artigos'].get(dest, []) for a in (r['artigos_destino'] if r else [])),
                destination_in_ext_normas=bool(n), destination_file_on_card=bool(n and n['file_present']),
                destination_text_citation=cite, destination_cites=sorted(cites)[:12], plausibility=plaus, review_flags=flags,
                destination_ementa=clip((n or {}).get('ementa'), 300)))
        out.sort(key=lambda b: (self.order.get(b['target_id'], 10 ** 6), b['label'], b['reference_id']))
        self.baseline = out
        self.current_by_row = defaultdict(list)
        for b in out:
            if b['visibility'] == 'CURRENT_VISIBLE':
                rw = self.row_of(b['target_id'])
                if rw:
                    self.current_by_row[rw].append(b)
        return out

    def _reverse_index(self):
        """norm key -> {cited target ids} from the pinned reverse remissions (status OK only)."""
        out = defaultdict(set)
        for h in self.pin['reverse_remissions']['records']:
            if h['status'] != 'OK':
                continue
            key = self.norms.catalog_key.get(h['source_norm']) or self.norms.ext.get(h['source_norm'])
            for t in h['targets']:
                out[key].add(t)
        return out

    # ----------------------------------------------------------------- signals
    def collect_signals(self):
        sig = []
        self.reserv = {}
        self.s2_excluded = []
        # S1 + S2: constitutional text of the target itself
        for tid in self.rt:
            text = self.text[tid]
            res = reservations(text)
            rw = self.row_of(tid)
            if res and rw:
                self.reserv.setdefault(rw, [])
                self.reserv[rw] += [dict(target_id=tid, type=k, excerpt=e) for k, e in res]
            for src, body in (('RUNTIME_TEXT', text), ('RUNTIME_EDITORIAL_VIDE', ' | '.join(self.vide[tid]))):
                for key, typ, raw, s, e in mentions(body):
                    ctx = body[max(0, s - 140):e + 140]
                    if typ == 'EC':
                        self.s2_excluded.append(dict(target_id=tid, mention=raw, source=src,
                                                     reason='EMENDA_CONSTITUCIONAL (norma constitucional, nao correlata)'))
                        continue
                    key, yr = self.norms.resolve_year(key)
                    hist = bool(HISTORIC_CONTEXT.search(ctx)) or tid.startswith('ADCT:')
                    vide = src == 'RUNTIME_EDITORIAL_VIDE'
                    flags = [yr, 'ADCT_OU_CONTEXTO_TRANSITORIO_HISTORICO (vigencia/funcao a confirmar)' if hist and not vide else None,
                             'NOTA_EDITORIAL_VIDE (anotacao da fonte, nao texto constitucional; nunca vira vinculo automaticamente)' if vide else None]
                    sig.append(dict(family='S2_NOTA_EDITORIAL_VIDE' if vide else 'S2_REMISSAO_NOMINAL', source=src, source_ref=tid, raw_target=tid, scope='DEVICE', caput=False,
                                    norm=key, norm_label=raw, relation_type='COMPLEMENTA', confidence='C' if (hist or vide) else 'A',
                                    evidence=clip(ctx), flags=[f for f in flags if f]))
        # S3: approved ENTENDA (signal only)
        import build_sd_staging as S
        import entenda_engine as E
        prof = S.PROFILES['FULL_CF_ENTENDA_810']
        ent = [r for _, g in S.approved_entenda_chain(E.NormContext('CF88'), prof['chain']) for r in g]
        self.entenda_records = len(ent)
        self.entenda_hints = defaultdict(list)
        for r in ent:
            tid = r['target_id']
            role = r['granularity'].get('role')
            covered = r['granularity'].get('covered_targets', [])
            prov = (r.get('human_review') or {}).get('content_provenance')
            parts = [('content', _flat(r['content']))] + [('external_layer_notes', n) for n in r['external_layer_notes']]
            for where, text in parts:
                for key, typ, raw, s, e in mentions(text):
                    if typ == 'EC':
                        continue
                    key, yr = self.norms.resolve_year(key)
                    flags = [f for f in (yr, f'ENTENDA_{role}' if role != 'AUTONOMOUS' else None,
                                         'ENTENDA_BLOCK_ANCHOR (a norma pode pertencer a um target coberto)' if covered else None) if f]
                    if key in RECENT_REFORM_NORMS and prov != 'HUMAN_REVIEW_EXTERNAL_OFFICIAL_SOURCE':
                        flags.append('EXTERNAL_VERIFICATION_REQUIRED (norma recente; sem proveniencia oficial no registro)')
                    sig.append(dict(family='S3_ENTENDA', source=f"ENTENDA:{r['explanation_id']}:{where}", source_ref=r['explanation_id'], raw_target=tid,
                                    scope='ARTICLE' if (covered or role == 'OVERVIEW') else 'DEVICE', caput=False, norm=key, norm_label=raw,
                                    relation_type='REGULAMENTA' if re.search(r'regulament|disciplin', text[max(0, s - 90):e + 90], re.I) else 'COMPLEMENTA',
                                    confidence='B', evidence=clip(text[max(0, s - 150):e + 150]), flags=flags, provenance=prov))
                for key, src, raw, s, e in alias_mentions(text, self.norms):
                    flags = [f'ENTENDA_{role}' if role != 'AUTONOMOUS' else None, 'ENTENDA_BLOCK_ANCHOR (a norma pode pertencer a um target coberto)' if covered else None]
                    if src == 'AUDITOR':
                        flags.append('NORM_IDENTITY_FROM_AUDITOR_ALIAS + EXTERNAL_VERIFICATION_REQUIRED')
                    sig.append(dict(family='S3_ENTENDA', source=f"ENTENDA:{r['explanation_id']}:{where}:NOME", source_ref=r['explanation_id'], raw_target=tid,
                                    scope='ARTICLE' if (covered or role == 'OVERVIEW') else 'DEVICE', caput=False, norm=key, norm_label=raw,
                                    relation_type='ORGANIZA_INSTITUIÇÃO' if raw.startswith('Estatuto') else 'COMPLEMENTA', confidence='C',
                                    evidence=clip(text[max(0, s - 150):e + 150]), flags=[f for f in flags if f], provenance=prov))
                for m in GENERIC_HINT.finditer(text):
                    self.entenda_hints[tid].append(clip(text[max(0, m.start() - 80):m.end() + 80], 200))
        cat = json.loads(T1_CATALOG.read_text(encoding='utf-8'))
        for e in cat['entries']:
            if e['kind'] not in ('EXTERNAL_LAW', 'TRANSITION_RULE'):
                continue
            for key, typ, raw, s, en in mentions(e['label']):
                if typ == 'EC':
                    continue
                key, yr = self.norms.resolve_year(key)
                for tid in e['applies_to_targets']:
                    sig.append(dict(family='S3_ENTENDA', source=f"T1_EXTERNAL_CATALOG:{e['id']}", source_ref=e['id'], raw_target=tid, scope='DEVICE', caput=False,
                                    norm=key, norm_label=raw, relation_type='REGULAMENTA' if e['kind'] == 'EXTERNAL_LAW' else 'CONDIÇÃO_OU_EXCEÇÃO',
                                    confidence='B', evidence=clip(e['label']), flags=[f for f in (yr, f"T1_{e['status']}") if f]))
        for bf in BACKLOGS:
            for it in json.loads((ROOT / bf).read_text(encoding='utf-8'))['items']:
                tid = it.get('target')
                if not tid or not T.validate_target_id(tid)[0]:
                    continue                                   # backlog item about a round/process, not a target
                for key, typ, raw, s, e in mentions(f"{it.get('detail', '')} {it.get('action', '')}"):
                    if typ == 'EC' or not tid:
                        continue
                    key, yr = self.norms.resolve_year(key)
                    sig.append(dict(family='S3_ENTENDA', source=f"BACKLOG:{it['id']}", source_ref=it['id'], raw_target=tid, scope='DEVICE', caput=False,
                                    norm=key, norm_label=raw, relation_type='COMPLEMENTA', confidence='C', evidence=clip(it.get('detail')),
                                    flags=[f for f in (yr, 'BACKLOG_ENTENDA') if f]))
        # S4: reverse remission in the acervo (main corpus + external norms on the card)
        for h in self.pin['reverse_remissions']['records']:
            if h['status'] != 'OK':
                continue
            key = self.norms.catalog_key.get(h['source_norm']) or self.norms.ext.get(h['source_norm'])
            found = h['region'] in ('EMENTA', 'ART1')
            v = h['verb_class']
            # a norm older than 1988 may cite an earlier Constitution ('art. 180 da Constituicao' = 1937): never more than C
            pre88 = int(key.split('/')[1]) < 1988 and '1988' not in (h.get('marker') or '')
            for tid in h['targets']:
                if v == 'INCIDENTAL':
                    conf, rtype = 'D', 'TOPICAL_ONLY'
                elif found and not pre88:
                    conf, rtype = 'B', {'REGULAMENTA': 'REGULAMENTA', 'IMPLEMENTA': 'IMPLEMENTA'}.get(v, 'COMPLEMENTA')
                else:
                    conf, rtype = 'C', 'COMPLEMENTA'
                if h['source_norm'] in PROCEDURAL and rtype != 'REGULAMENTA' and conf != 'D':
                    rtype = 'PROCEDIMENTO'
                sig.append(dict(family='S4_ACERVO_REVERSO', source=f"ACERVO:{h['source_norm']}:art.{h['source_article'] or '-'}:{h['region']}",
                                source_ref=h['source_norm'], raw_target=tid, scope='ARTICLE' if T.parse_target_id(tid)['paragraph'] is None
                                and T.parse_target_id(tid)['inciso'] is None and ':CAPUT' not in tid and tid.count(':') == 1 else 'DEVICE',
                                caput=tid.endswith(':CAPUT'), norm=key, norm_label=self.norms.name(key), relation_type=rtype, confidence=conf,
                                evidence=h['snippet'], flags=[f"REVERSE_{h['region']}_{v}"] + (
                                    ['SOURCE_NORM_PRE_1988 (pode citar Constituicao anterior; confirmar)'] if pre88 else [])))
        # S5: Relations V2 legacy (evidence, never authority)
        for r in self.pin['legacy_relations']['records']:
            if r['set'] == '2E4_RELACOES_CF88':
                continue                                       # origin of the current links: inventoried in the baseline
            key = self.norms.from_legacy(r['destino_norma'])
            hist = (r['role'] == 'HISTORICO_LEGADO' or r.get('vigencia_status') == 'REVOGADA'
                    or any(re.search(r'Situa[çc][ãa]o oficial:\s*REVOGADA(?![A-Z_])', str(x)) for x in r.get('motivos') or []))
            cam = r.get('secao_camara')
            cls = r.get('classe') or ''
            if hist:
                conf = 'HIST'
            elif cls == 'D_FRACA':
                conf = 'D'
            elif 'CORRELATA_REVERSA' in r['tipos']:
                conf = 'C'
            elif cam in ('COMPLEMENTAR', 'ORDINARIA') or cls in ('A_EXPRESSA', 'B_REGULAMENTACAO_OFICIAL'):
                # official Camara listing = B only when the norm is current by local evidence (acervo text or 'sem revogacao expressa')
                local = self.norms.acervo(key)['acervo_status'] in ('IN_MAIN_CORPUS', 'EXTERNAL_ALREADY_INGESTED') if key else False
                conf = 'B' if (local or r.get('vigencia_status') == 'SEM_REVOGACAO_EXPRESSA') else 'C'
            else:
                conf = 'C'
            rtype = 'REGULAMENTA' if cam == 'COMPLEMENTAR' or 'REGULAMENTACAO' in r['tipos'] and cam != 'ORDINARIA' else 'COMPLEMENTA'
            if 'CORRELATA_REVERSA' in r['tipos']:
                rtype = 'COMPLEMENTA'
            for tid, scope in self._legacy_targets(r['origem']):
                sig.append(dict(family='S5_RELATIONS_V2_LEGADO', indep='S4_ACERVO_REVERSO' if 'CORRELATA_REVERSA' in r['tipos'] else None,
                                source=f"LEGADO:{r['legacy_id']}", source_ref=r['legacy_id'], raw_target=tid, scope=scope,
                                caput=False, norm=key, norm_label=self.norms.name(key) or r['destino_norma'], relation_type=rtype, confidence=conf,
                                evidence=clip(r.get('evidencia')), flags=[f for f in (f"LEGADO_{r['set']}", f"classe={cls or '-'}", f"secao_camara={cam or '-'}",
                                                                                     f"vigencia={r.get('vigencia_status') or '-'}") if f],
                                urls=r.get('urls')))
        self.signals = sig
        return sig

    def _legacy_targets(self, o):
        art = o['artigo']
        if not art:
            return []
        pars = [('UNICO' if p.lower() in ('unico', 'único', 'pu', 'parágrafo único') else re.sub(r'[º°o]$', '', p)) for p in o['paragrafos']]
        incs = [i.upper() for i in o['incisos']]
        als = [a.lower() for a in o['alineas']]

        def f(**kw):
            try:
                return T.format_target_id('CF88', art, **kw)
            except Exception:  # noqa: BLE001 - invalid legacy key: recorded by consolidation as TARGET_NOT_FOUND
                return f'CF88:ART.{art}:INVALID'
        if incs:
            if len(pars) > 1:
                return [(f(), 'ARTICLE')]
            p = pars[0] if pars else None
            if als and len(incs) == 1:
                return [(f(paragraph=p, inciso=incs[0], alinea=a), 'DEVICE') for a in als]
            return [(f(paragraph=p, inciso=i), 'DEVICE') for i in incs]
        if pars:
            return [(f(paragraph=p), 'DEVICE') for p in pars]
        return [(f(), 'ARTICLE')]

    # ----------------------------------------------------------------- consolidation
    def consolidate(self):
        cands, rejected = {}, []
        for s in self.signals:
            tid = s['raw_target']
            if tid not in self.rt:
                st = self.engine_status.get(tid, {}).get('status')
                rejected.append(dict(s, rejection='TARGET_NOT_IN_RUNTIME' + (f' (indice legado: {st})' if st else ' (target inexistente)')))
                continue
            rw = self.row_of(tid)
            excluded = None
            if rw is None:
                excluded = 'TECHNICAL' if self.rt[tid]['kind'] in ('NORMA', 'NAMESPACE') else 'REVOKED'
                rw = tid
            k = (rw, s['norm'] or f"UNIDENTIFIED:{s['norm_label']}")
            c = cands.setdefault(k, dict(row=rw, norm=s['norm'], norm_labels=set(), signals=[], excluded_target=excluded, caput=False))
            c['signals'].append(s)
            c['norm_labels'].add(s['norm_label'] or '')
            c['caput'] |= bool(s['caput'])
        # anti-noise: article-level evidence of a norm that also has device-level candidates in the same article is merged into them
        by_norm_art = defaultdict(list)
        for k, c in cands.items():
            by_norm_art[(c['norm'], ':'.join(c['row'].split(':')[:2]))].append(k)
        for (norm, art), ks in by_norm_art.items():
            art_k = (art, norm) if norm else None
            if not norm or art_k not in cands:
                continue
            specific = [k for k in ks if k[0] != art]
            if specific:
                a = cands.pop(art_k)
                for k in specific:
                    cands[k]['signals'] += [dict(s, flags=s['flags'] + ['ARTICLE_LEVEL_EVIDENCE_MERGED']) for s in a['signals']]
        out = []
        for (rw, nk), c in cands.items():
            out.append(self._classify(rw, c))
        out.sort(key=lambda c: (self.order.get(c['target_id'], 10 ** 6), c['norm_key'] or '~', c['candidate_id']))
        self.candidates = out
        self.rejected = rejected
        return out

    def _classify(self, rw, c):
        sigs = sorted(c['signals'], key=lambda s: (RANK.get(s['confidence'], 9), s['family'], s['source']))
        fams = sorted({s['family'] for s in sigs if s['confidence'] != 'HIST'})
        # independent evidence families (a Vide note is not independent; the legacy reverse scan repeats the acervo reverse remission)
        indep = sorted({s.get('indep') or s['family'] for s in sigs if s['confidence'] != 'HIST' and s['family'] != 'S2_NOTA_EDITORIAL_VIDE'})
        live = [s for s in sigs if s['confidence'] != 'HIST']
        best = min((s['confidence'] for s in live), key=lambda x: RANK[x], default='HIST')
        key = c['norm']
        identified = bool(key) and not key.endswith('/?')
        canonical = rw
        if c['caput'] and rw in self.rows and self.rows[rw]['kind'] == 'ARTIGO':
            canonical = f'{rw}:CAPUT'
        flags = sorted({f for s in sigs for f in s['flags'] if f})
        art_level = all(s['scope'] == 'ARTICLE' for s in live) if live else False
        if rw in self.rows and self.rows[rw]['kind'] == 'ARTIGO' and art_level and self.has_subdivisions(rw):
            flags.append('SPECIFICITY_REVIEW_REQUIRED (evidencia so no nivel do artigo; nao herdar para paragrafo/inciso)')
        acervo = self.norms.acervo(key if identified else None)
        validity = self.norms.validity(key) if identified else 'NOT_IDENTIFIED'
        ext_ver = any('EXTERNAL_VERIFICATION_REQUIRED' in f for f in flags) or (identified and validity in ('SEM_EVIDENCIA_LOCAL', 'CONFLITO_NO_LEGADO'))
        if identified and validity in ('SEM_EVIDENCIA_LOCAL', 'CONFLITO_NO_LEGADO'):
            flags.append(f'EXTERNAL_VERIFICATION_REQUIRED (vigencia da norma: {validity})')
        historical_norm = validity == 'REVOGADA_SEGUNDO_LEGADO' or best == 'HIST'
        rtypes = Counter(s['relation_type'] for s in live)
        top = Counter(s['relation_type'] for s in live if s['confidence'] == best and s['relation_type'] != 'TOPICAL_ONLY')
        # the nature comes from the strongest evidence level (a D citation never names the nature of a B/C candidate)
        rtype = (sorted(top, key=lambda t: (-top[t], RELATION_TYPES.index(t)))[0] if top else 'TOPICAL_ONLY')
        if best in ('A', 'B') and rtype == 'TOPICAL_ONLY':
            rtype = next((s['relation_type'] for s in live if s['confidence'] == best), 'COMPLEMENTA')
        if best == 'D':
            rtype = 'TOPICAL_ONLY'
        if key and acervo['acervo_id'] in PROCEDURAL and rtype == 'COMPLEMENTA':
            rtype = 'PROCEDIMENTO'
        name = self.norms.name(key) if identified else None
        if identified and re.search(r'\bPlano Nacional|Pol[íi]tica Nacional', (self.norms.info.get(key, {}).get('ementa') or '') + ' ' + (name or ''), re.I) \
                and rtype in ('COMPLEMENTA', 'IMPLEMENTA'):
            rtype = 'EXECUTA_POLÍTICA_CONSTITUCIONAL'
        current = [b for b in self.current_by_row.get(rw, []) if b['destination_norm_key'] == key]
        res_types = {r['type'] for r in self.reserv.get(rw, [])}
        pre88 = any(f.startswith('SOURCE_NORM_PRE_1988') for f in flags)
        if best == 'D' and 'C' not in {s['confidence'] for s in live} and res_types and rtypes.get('TOPICAL_ONLY') == len(live) and not pre88:
            # reverse citation only, but the constitution itself asks for law here: plausible, never more
            best, rtype = 'C', 'CONDIÇÃO_OU_EXCEÇÃO'
            flags.append('UPGRADED_D_TO_C_BY_LEGISLATIVE_RESERVATION')
        excluded = c['excluded_target']
        promotable = bool(identified and not excluded and not historical_norm and best in ('A', 'B', 'C') and not current)
        if not promotable:
            prio = None
        elif best == 'A':
            prio = 'HIGH'
        elif best == 'B':
            strong = (('LEI_COMPLEMENTAR' in res_types and key.startswith('LC:'))
                      or any(s['family'] == 'S3_ENTENDA' and s['confidence'] == 'B' for s in live)
                      or len(indep) >= 2 or rtype == 'ORGANIZA_INSTITUIÇÃO')
            prio = 'HIGH' if strong else 'MEDIUM'
        else:
            prio = 'MEDIUM' if len(indep) >= 2 else 'LOW'
        # article-level evidence on an article with subdivisions: one level down, unless the norm itself declares the article link
        declared = any(s['family'] == 'S4_ACERVO_REVERSO' and s['confidence'] == 'B' for s in live) or best == 'A'
        if prio and prio != 'LOW' and any(f.startswith('SPECIFICITY_REVIEW_REQUIRED') for f in flags) and not declared:
            prio = {'HIGH': 'MEDIUM', 'MEDIUM': 'LOW'}[prio]
        status = ('ALREADY_CURRENT_LINK' if current else 'EXCLUDED_TARGET_' + excluded if excluded else 'HISTORICAL_NORM_EXCLUDED' if historical_norm
                  else 'NOT_IDENTIFIED_NORM' if not identified else 'TOPICAL_ONLY_REJECTED' if best == 'D' else 'CANDIDATE_FOR_HUMAN_REVIEW')
        cid = 'CORRC0-' + hashlib.sha1(f'{rw}|{key or sorted(c["norm_labels"])[0]}'.encode('utf-8')).hexdigest()[:12].upper()
        return dict(
            candidate_id=cid, target_id=rw, canonical_target_id=canonical, display_target=display(canonical) if canonical in self.rt else rw,
            namespace=rw.split(':')[0], target_legal_status=self.legal.get(rw), target_engine_status=self.engine_status.get(rw, {}).get('status', 'NOT_IN_ENGINE_INDEX'),
            target_auditable=rw in self.rows, norm_key=key if identified else None, norm_name=name, norm_labels_seen=sorted(c['norm_labels'])[:6],
            norm_identified=identified, norm_validity_local=validity, relation_type=rtype, confidence=best, confidence_label=CONFIDENCE.get(best, 'HISTORICAL'),
            review_priority=prio, promotable_to_human_review=promotable, candidate_status=status,
            already_current_link=[b['reference_id'] for b in current], signal_families=fams, independent_signal_families=indep, signal_count=len(sigs),
            acervo_status=acervo['acervo_status'], acervo_id=acervo['acervo_id'], device_status=acervo['device_status'],
            device_resolvable_now=acervo['device_resolvable_now'],
            engine_overlay_eligible_now=bool(self.rows.get(rw, {}).get('engine_overlay_eligible')),
            external_verification_required=ext_ver, art_caput_merged=bool(c['caput']), flags=flags,
            signals=[dict(family=s['family'], source=s['source'], confidence=s['confidence'], relation_type=s['relation_type'], raw_target=s['raw_target'],
                          scope=s['scope'], evidence=s['evidence'], flags=s['flags'], **({'urls': s['urls']} if s.get('urls') else {})) for s in sigs][:12],
            signals_truncated=max(0, len(sigs) - 12))

    # ----------------------------------------------------------------- matrix
    def coverage(self):
        by_row = defaultdict(list)
        for c in self.candidates:
            by_row[c['target_id']].append(c)
        s2_by_row = defaultdict(set)
        for s in self.signals:
            if s['family'] == 'S2_REMISSAO_NOMINAL' and self.row_of(s['raw_target']):
                s2_by_row[self.row_of(s['raw_target'])].add(s['norm_label'])
        out = []
        for rw in sorted(self.rows, key=lambda t: self.order[t]):
            r = self.rows[rw]
            cur = self.current_by_row.get(rw, [])
            cs = by_row.get(rw, [])
            prom = [c for c in cs if c['promotable_to_human_review']]
            res = self.reserv.get(rw, [])
            explicit = s2_by_row.get(rw, [])
            hints = self.entenda_hints.get(rw, []) + self.entenda_hints.get(f'{rw}:CAPUT', [])
            unident = [c for c in cs if not c['norm_identified']]
            topical = [c for c in cs if c['candidate_status'] == 'TOPICAL_ONLY_REJECTED']
            if cur:
                status, reason = 'HAS_VALIDATED_CORRELATA', 'vinculo CORRELATA visivel no Reference Engine RUN3 (validado estruturalmente; revisao juridica C1)'
            elif prom:
                status, reason = 'HAS_CORRELATA_CANDIDATE', 'candidato com norma identificada (A/B/C) aguardando revisao humana'
            elif res:
                status, reason = 'GENERIC_LEGISLATIVE_RESERVATION', 'a Constituicao remete a lei, sem norma especifica identificada com seguranca'
            elif unident or hints:
                status, reason = 'NEEDS_HUMAN_REVIEW', 'sinal de legislacao sem norma identificada (ENTENDA/mencao sem numero)'
            elif topical:
                status, reason = 'NEEDS_HUMAN_REVIEW', 'somente citacoes tematicas/incidentais (TOPICAL_ONLY) no acervo'
            else:
                status, reason = 'NEEDS_HUMAN_REVIEW', 'NO_AUTOMATED_SIGNAL: busca automatica sem sinal; ausencia ainda nao confirmada por revisao'
            ent = self.entenda_lookup.get(rw) or self.entenda_lookup.get(f'{rw}:CAPUT')
            best_c = min((c['confidence'] for c in prom), key=lambda x: RANK[x], default='')
            best_p = min((c['review_priority'] for c in prom), key=lambda x: PRIO_RANK[x], default='')
            dev = sorted({c['device_status'] for c in prom})
            out.append(dict(
                target_id=rw, namespace=r['namespace'], kind=r['kind'], audit_class=r['audit_class'], display_target=r['display_target'],
                legal_status=r['legal_status'], engine_status=r['engine_status'], entenda_resolution=ent['resolution'] if ent else 'NONE',
                current_correlata_count=len(cur), current_correlata_ids=';'.join(b['reference_id'] for b in cur),
                current_link_review=';'.join(sorted({b['plausibility'] for b in cur})),
                explicit_legal_remission=';'.join(sorted({x['type'] for x in res} | {f'NOMINAL:{e}' for e in explicit})),
                editorial_vide_notes=' | '.join(self.vide.get(rw, []) + self.vide.get(f'{rw}:CAPUT', [])),
                candidate_count=len(prom), candidate_norms=';'.join(c['norm_key'] for c in prom),
                candidate_relation_types=';'.join(sorted({c['relation_type'] for c in prom})), confidence=best_c, device_status=';'.join(dev),
                review_priority=best_p, coverage_status=status, coverage_reason=reason,
                topical_only_rejected=len(topical), unidentified_signals=len(unident), entenda_generic_hints=len(hints),
                engine_overlay_eligible_now=r['engine_overlay_eligible']))
        self.matrix = out
        return out

    # ----------------------------------------------------------------- outputs
    def build(self):
        pres = self.preservation()
        self.build_universe()
        self.build_baseline()
        self.collect_signals()
        self.consolidate()
        self.coverage()
        return self.render(pres)

    def render(self, pres):
        visible = [b for b in self.baseline if b['visibility'] == 'CURRENT_VISIBLE']
        new = [c for c in self.candidates if c['promotable_to_human_review']]
        prio = Counter(c['review_priority'] for c in new)
        cov = Counter(r['coverage_status'] for r in self.matrix)
        ns = lambda rows, n: [r for r in rows if r['namespace'] == n]  # noqa: E731
        excl = Counter((e['coverage_status'], e['reason']) for e in self.excluded)
        rt_counts = Counter((t['namespace'], t['kind'], self.legal[t['target_id']]) for t in self.idx['targets'])
        summary = dict(
            current_visible_correlata_links=len(visible), current_hidden_correlata_links=len(self.baseline) - len(visible),
            current_correlata_links_total=len(self.baseline), targets_with_current_correlata=len({b['target_id'] for b in visible}),
            audit_rows_with_current_correlata=sum(1 for r in self.matrix if r['current_correlata_count']),
            runtime_targets=len(self.rt), runtime_current_or_structural=sum(1 for t in self.rt if self.legal[t] == 'CURRENT'),
            runtime_current_kind_counts=dict(sorted(Counter(self.rt[t]['kind'] for t in self.rt if self.legal[t] == 'CURRENT').items())),
            excluded_technical=sum(1 for e in self.excluded if e['coverage_status'] == 'TECHNICAL_TARGET_EXCLUDED'),
            excluded_technical_norma_namespace=sum(1 for e in self.excluded if e['reason'] == 'NORMA_OU_NAMESPACE'),
            excluded_presentation_caput_folded=sum(1 for e in self.excluded if e['reason'] == 'PRESENTATION_EQUIVALENCE_ART_CAPUT'),
            excluded_historical_or_revoked=sum(1 for e in self.excluded if e['coverage_status'] == 'HISTORICAL_OR_REVOKED_EXCLUDED'),
            excluded_revoked_runtime=sum(1 for e in self.excluded if e['reason'] == 'REVOGADO_NO_RUNTIME_MONOVIGENTE'),
            excluded_not_in_runtime=sum(1 for e in self.excluded if e['legal_status'] == 'NOT_IN_RUNTIME'),
            auditable_targets=len(self.matrix), auditable_cf=len(ns(self.matrix, 'CF88')), auditable_adct=len(ns(self.matrix, 'ADCT')),
            auditable_structural_articles=sum(1 for r in self.matrix if r['audit_class'] == 'STRUCTURAL'),
            auditable_current_devices=sum(1 for r in self.matrix if r['audit_class'] == 'CURRENT'),
            candidate_records_total=len(self.candidates), new_candidates=len(new), new_candidates_cf=len(ns(new, 'CF88')), new_candidates_adct=len(ns(new, 'ADCT')),
            high=prio['HIGH'], medium=prio['MEDIUM'], low=prio['LOW'],
            topical_only_rejected=sum(1 for c in self.candidates if c['candidate_status'] == 'TOPICAL_ONLY_REJECTED'),
            historical_candidates_excluded=sum(1 for c in self.candidates if c['candidate_status'] in ('HISTORICAL_NORM_EXCLUDED',) or c['candidate_status'].startswith('EXCLUDED_TARGET')),
            not_identified_candidates=sum(1 for c in self.candidates if c['candidate_status'] == 'NOT_IDENTIFIED_NORM'),
            corroborating_current_links=sum(1 for c in self.candidates if c['candidate_status'] == 'ALREADY_CURRENT_LINK'),
            generic_legislative_reservation=cov['GENERIC_LEGISLATIVE_RESERVATION'],
            generic_legislative_reservation_cf=sum(1 for r in ns(self.matrix, 'CF88') if r['coverage_status'] == 'GENERIC_LEGISLATIVE_RESERVATION'),
            generic_legislative_reservation_adct=sum(1 for r in ns(self.matrix, 'ADCT') if r['coverage_status'] == 'GENERIC_LEGISLATIVE_RESERVATION'),
            ingestion_required=sum(1 for c in new if c['device_status'] == 'INGESTION_REQUIRED'),
            ingestion_required_norms=len({c['norm_key'] for c in new if c['device_status'] == 'INGESTION_REQUIRED'}),
            device_resolvable_now=sum(1 for c in new if c['device_resolvable_now']),
            device_resolvable_now_norms=len({c['norm_key'] for c in new if c['device_resolvable_now']}),
            main_corpus_route_required=sum(1 for c in new if c['device_status'] == 'MAIN_CORPUS_ROUTE_REQUIRED'),
            main_corpus_route_required_norms=len({c['norm_key'] for c in new if c['device_status'] == 'MAIN_CORPUS_ROUTE_REQUIRED'}),
            external_verification_required=sum(1 for c in new if c['external_verification_required']),
            engine_overlay_blocked_adct=sum(1 for c in new if not c['engine_overlay_eligible_now']),
            coverage_status_counts={k: cov.get(k, 0) for k in COVERAGE[:5]},
            needs_human_review_targets=cov['NEEDS_HUMAN_REVIEW'],
            no_automated_signal_targets=sum(1 for r in self.matrix if r['coverage_reason'].startswith('NO_AUTOMATED_SIGNAL')),
            needs_human_review_total_items=len(new) + sum(1 for b in visible if b['plausibility'] == 'NEEDS_REVIEW') + cov['NEEDS_HUMAN_REVIEW'],
            current_links_needing_review=sum(1 for b in visible if b['plausibility'] == 'NEEDS_REVIEW'),
            current_links_plausibility=dict(sorted(Counter(b['plausibility'] for b in self.baseline).items())),
            entenda_records_scanned=self.entenda_records, signals_total=len(self.signals),
            signals_by_family=dict(sorted(Counter(s['family'] for s in self.signals).items())),
            signals_rejected_invalid_target=len(self.rejected))
        ranking = Counter(c['norm_key'] for c in new)
        rank = [dict(norm_key=k, norm_name=self.norms.name(k), targets=v, acervo_status=self.norms.acervo(k)['acervo_status'],
                     device_status=self.norms.acervo(k)['device_status'], high=sum(1 for c in new if c['norm_key'] == k and c['review_priority'] == 'HIGH'))
                for k, v in sorted(ranking.items(), key=lambda kv: (-kv[1], kv[0]))]
        reform = [c for c in self.candidates if (c['norm_key'] in RECENT_REFORM_NORMS) or re.match(r'^(CF88:ART\.(14[5-9]|15\d|16[0-2])(-[A-C])?|ADCT:ART\.(1[2-3]\d))(\b|:)', c['target_id'])]
        common = dict(mission=MISSION, baseline=BASELINE, diagnostic_only=True, promoted=0, pin=dict(path=PIN.relative_to(ROOT).as_posix(), sha256=sha(PIN)))
        files = {}
        files[OUT['baseline']] = jdump(dict(common, schema_version=1, artifact='CF88_CORRELATA_CURRENT_BASELINE',
                                            derivation='LEGAL_TARGET_ID/derived/export_test/run3/CF88_REFERENCES_EXPORT.json (reference_type=CORRELATA; '
                                                       'camada SD_RELATIONS_REL_LOOKUP do engine_config) x RELACOES/EXT_NORMAS/EXT_ARTIGOS do cartao (pin)',
                                            counts=dict(total=len(self.baseline), visible=len(visible), hidden=len(self.baseline) - len(visible),
                                                        targets_visible=summary['targets_with_current_correlata'],
                                                        relations_distinct=len({b['relation_id'] for b in self.baseline}),
                                                        destination_norms=len({b['destination_norm_id'] for b in self.baseline}),
                                                        plausibility=summary['current_links_plausibility']),
                                            preservation=pres, links=self.baseline))
        files[OUT['universe']] = jdump(dict(common, schema_version=1, artifact='CF88_CORRELATA_TARGET_UNIVERSE',
                                            sources=dict(runtime=dict(path=RUNTIME.relative_to(ROOT).as_posix(), sha256=sha(RUNTIME)),
                                                         target_index=dict(path='LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json', sha256=sha(D / 'CF88_TARGET_INDEX.json')),
                                                         target_status=dict(path='LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS.json', sha256=sha(D / 'CF88_TARGET_STATUS.json')),
                                                         text_map=dict(path='/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX (cartao, via pin)',
                                                                       sha256=self.pin['device_tables']['sha256']['99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX'])),
                                            rules=UNIVERSE_RULES,
                                            counts=dict(runtime_targets=len(self.rt), engine_index_targets=len(self.engine_idx),
                                                        runtime_by_namespace_kind_status={f'{a}|{b}|{c}': v for (a, b, c), v in sorted(rt_counts.items())},
                                                        engine_status_counts=dict(sorted(Counter(v['status'] for v in self.engine_status.values()).items())),
                                                        engine_status_of_auditable=dict(sorted(Counter(r['engine_status'] for r in self.rows.values()).items())),
                                                        excluded=dict(sorted({f'{a}|{b}': v for (a, b), v in excl.items()}.items())),
                                                        auditable=len(self.rows), auditable_cf=summary['auditable_cf'], auditable_adct=summary['auditable_adct'],
                                                        auditable_by_class=dict(sorted(Counter(r['audit_class'] for r in self.rows.values()).items()))),
                                            auditable=[dict(target_id=r['target_id'], namespace=r['namespace'], kind=r['kind'], audit_class=r['audit_class'],
                                                            legal_status=r['legal_status'], engine_status=r['engine_status'], presentation_pair=r['presentation_pair'],
                                                            engine_overlay_eligible=r['engine_overlay_eligible']) for r in sorted(self.rows.values(), key=lambda r: self.order[r['target_id']])],
                                            excluded=self.excluded))
        files[OUT['candidates']] = jdump(dict(common, schema_version=1, artifact='CF88_CORRELATA_CANDIDATES', signals=SIGNALS, relation_types=RELATION_TYPES,
                                              confidence=CONFIDENCE, policy=CANDIDATE_POLICY,
                                              counts=dict(records=len(self.candidates), by_status=dict(sorted(Counter(c['candidate_status'] for c in self.candidates).items())),
                                                          by_confidence=dict(sorted(Counter(c['confidence'] for c in self.candidates).items())),
                                                          signals_by_family=summary['signals_by_family'], rejected_signals=len(self.rejected)),
                                              candidates=self.candidates,
                                              constitutional_amendment_mentions_excluded=self.s2_excluded,
                                              rejected_signals=[dict(raw_target=s['raw_target'], family=s['family'], source=s['source'], norm=s['norm'],
                                                                     rejection=s['rejection']) for s in self.rejected]))
        buf = io.StringIO()
        cols = list(self.matrix[0].keys())
        w = csv.DictWriter(buf, fieldnames=cols, lineterminator='\n')
        w.writeheader()
        for r in self.matrix:
            w.writerow(r)
        files[OUT['matrix']] = buf.getvalue().encode('utf-8')
        q = sorted(new, key=lambda c: (PRIO_RANK[c['review_priority']], RANK[c['confidence']], self.order.get(c['target_id'], 0), c['norm_key']))
        files[OUT['queue']] = jdump(dict(common, schema_version=1, artifact='CF88_CORRELATA_REVIEW_QUEUE', policy=QUEUE_POLICY,
                                         counts=dict(total=len(q), high=prio['HIGH'], medium=prio['MEDIUM'], low=prio['LOW'],
                                                     current_link_review=summary['current_links_needing_review']),
                                         HIGH=[_qitem(c) for c in q if c['review_priority'] == 'HIGH'],
                                         MEDIUM=[_qitem(c) for c in q if c['review_priority'] == 'MEDIUM'],
                                         LOW=[_qitem(c) for c in q if c['review_priority'] == 'LOW'],
                                         CURRENT_LINK_REVIEW=[dict(reference_id=b['reference_id'], target_id=b['target_id'], display_target=b['display_target'],
                                                                   destination=b['destination_norm_name'], plausibility=b['plausibility'], flags=b['review_flags'],
                                                                   destination_text_citation=b['destination_text_citation'])
                                                              for b in self.baseline if b['plausibility'] in ('NEEDS_REVIEW', 'OBSOLETE_HIDDEN')]))
        files[OUT['report']] = report(self, summary, rank, reform, pres).encode('utf-8')
        self.summary = summary
        return files, summary


def _flat(o):
    if isinstance(o, dict):
        return ' '.join(_flat(v) for v in o.values())
    if isinstance(o, list):
        return ' '.join(_flat(v) for v in o)
    return str(o or '')


def _qitem(c):
    return dict(candidate_id=c['candidate_id'], target_id=c['canonical_target_id'], display_target=c['display_target'], norm_key=c['norm_key'],
                norm_name=c['norm_name'], relation_type=c['relation_type'], confidence=c['confidence'], signal_families=c['signal_families'],
                acervo_status=c['acervo_status'], device_status=c['device_status'], external_verification_required=c['external_verification_required'],
                engine_overlay_eligible_now=c['engine_overlay_eligible_now'], flags=c['flags'],
                evidence=[dict(family=s['family'], source=s['source'], evidence=s['evidence']) for s in c['signals'][:3]],
                decision=None, decision_options=['APPROVE', 'REJECT', 'RETARGET', 'NEEDS_SOURCE'])


UNIVERSE_RULES = dict(
    source='CF88_RUNTIME (Compilacao Monovigente, CF88 + ADCT) = bytes do cartao; parser aprovado (runtime_targets.build_runtime_index)',
    legal_status='runtime_targets.runtime_status: (Revogado)/(Suprimido) -> REVOKED; demais -> CURRENT (identico ao CF88_TARGETS.IDX do cartao)',
    included=['CURRENT: paragrafo, paragrafo unico, inciso, alinea vigentes e alcancaveis (linha propria no TEXT_MAP)',
              'STRUCTURAL: ART.n vigente (unidade de apresentacao ART.n <-> ART.n:CAPUT; status STRUCTURAL no motor)'],
    excluded=['TECHNICAL_TARGET_EXCLUDED/NORMA_OU_NAMESPACE: CF88, ADCT',
              'TECHNICAL_TARGET_EXCLUDED/PRESENTATION_EQUIVALENCE_ART_CAPUT: ART.n:CAPUT dobrado na linha de ART.n (unica equivalencia permitida)',
              'HISTORICAL_OR_REVOKED_EXCLUDED/REVOGADO_NO_RUNTIME_MONOVIGENTE: (Revogado)/(Suprimido) no runtime',
              'HISTORICAL_OR_REVOKED_EXCLUDED/AUSENTE_DO_RUNTIME: target so do indice legado (HISTORICAL_ONLY, renumerado, ADCT do cf.txt antigo)'],
    no_inheritance='nenhuma heranca automatica artigo->paragrafo->inciso ou caput->descendente; cada candidato fica no target da evidencia',
    engine_status_note='o status do motor (CF88_TARGET_STATUS) marca o ADCT como UNKNOWN_VALIDITY (texto operacional antigo sem ADCT): '
                       'o overlay atual do Reference Engine so aceita CURRENT/STRUCTURAL -> candidatos ADCT exigem regra de status no overlay futuro')
CANDIDATE_POLICY = ('Candidato = (target auditavel, norma). Nada e promovido nesta missao. Sem norma identificada (tipo+numero+ano) o candidato nao e '
                    'promovivel. TOPICAL_ONLY (D) nao entra na fila. Targets revogados/historicos e normas revogadas ficam registrados como '
                    'excluidos, nunca visiveis. Frequencia de uma norma nao e prova juridica.')
QUEUE_POLICY = ('Fila de revisao humana (nenhuma decisao tomada). HIGH: remissao expressa, LC exigida + LC identificada, ENTENDA aprovado citando '
                'a norma, multiplas familias de sinal, estatuto/lei organica. MEDIUM: relacao direta (B) ou C corroborado. LOW: C isolado. '
                'CURRENT_LINK_REVIEW: vinculos atuais com inconsistencia evidente (nao removidos).')

# Evident inconsistencies of current links, for human review only (text of the target x ementa of the destination, both in this audit's
# outputs). Not removals: the 44 links stay byte-identical until a human decision.
AUDITOR_FLAGS = {
    ('CF88:ART.155:PAR.1:INC.III', 'EXT_LC87_1996'): 'o § 1º trata do imposto do inciso I (ITCMD); a LC 87/1996 e a lei do ICMS (inciso II)',
    ('CF88:ART.195:INC.II', 'EXT_LC70_1991'): 'LC 70/1991 institui a COFINS (contribuicao do empregador/empresa, inciso I); inciso II e a contribuicao do trabalhador',
    ('CF88:ART.195:PAR.1', 'EXT_LC70_1991'): '§ 1º trata das receitas de Estados/DF/Municipios nos orcamentos; a ementa da LC 70/1991 nao trata disso',
    ('CF88:ART.195:PAR.2', 'EXT_LC70_1991'): '§ 2º trata da proposta orcamentaria da seguridade; a ementa da LC 70/1991 nao trata disso',
    ('CF88:ART.201:INC.I', 'EXT_LEI7998_1990'): 'Lei 7.998/1990 regula seguro-desemprego/abono (inciso III); inciso I e incapacidade e idade avancada',
    ('CF88:ART.201:INC.II', 'EXT_LEI7998_1990'): 'Lei 7.998/1990 regula seguro-desemprego/abono (inciso III); inciso II e protecao a maternidade',
    ('CF88:ART.201:INC.IV', 'EXT_LEI7998_1990'): ('a Lei 7.998/1990 cita "inciso IV do art. 201" na numeracao de 1990; no texto vigente o inciso IV e '
                                                   'salario-familia/auxilio-reclusao e o desemprego involuntario esta no inciso III (renumeracao: confirmar)'),
    ('CF88:ART.201:INC.V', 'EXT_LEI7998_1990'): 'Lei 7.998/1990 regula seguro-desemprego/abono (inciso III); inciso V e pensao por morte',
    ('CF88:ART.182', 'EXT_LEI13425_2017'): 'Lei 13.425/2017 (prevencao de incendios) no artigo inteiro; vinculo tematico/estreito para a politica urbana',
    ('CF88:ART.43:PAR.1:INC.I', 'EXT_LC112_2001'): 'LC 112/2001 cria uma RIDE especifica (Grande Teresina): instancia, nao a lei geral do inciso',
    ('CF88:ART.43:PAR.1:INC.II', 'EXT_LC112_2001'): 'LC 112/2001 cria uma RIDE especifica (Grande Teresina): instancia, nao a lei geral do inciso',
    ('CF88:ART.161:INC.I', 'EXT_LC62_1989'): 'inciso I (valor adicionado do art. 158, § 1º, I) e materia da LC 63/1990; a LC 62/1989 trata dos fundos (inciso II)',
    ('CF88:ART.153:PAR.4:INC.II', 'EXT_LEI11250_2005'): 'Lei 11.250/2005 "Regulamenta o inciso III do § 4º do art. 153" (ementa): nao o inciso II',
    ('CF88:ART.153:PAR.4:INC.II', 'EXT_LEI8981_1995'): 'Lei 8.981/1995 "Altera a legislacao tributaria federal": vinculo amplo, sem relacao direta demonstrada',
    ('CF88:ART.153:PAR.4:INC.III', 'EXT_LEI8981_1995'): 'Lei 8.981/1995 "Altera a legislacao tributaria federal": vinculo amplo, sem relacao direta demonstrada',
    ('CF88:ART.153:PAR.4:INC.III', 'EXT_LEI9393_1996'): 'Lei 9.393/1996 (ITR) e a lei do imposto; o inciso III trata da opcao municipal (Lei 11.250/2005)',
    ('CF88:ART.37:PAR.3:INC.II', 'EXT_LEI13460_2017'): 'inciso II (acesso a registros/informacoes) e regulado pela LAI (Lei 12.527/2011, ementa); Lei 13.460/2017 e o inciso I',
    ('CF88:ART.20:PAR.1', 'EXT_LEI9984_2000'): 'Lei 9.984/2000 cria a ANA; a participacao/compensacao financeira do § 1º nao e o objeto da ementa',
}


# Positive notes (the automatic sibling rule would flag them): local evidence that the link is coherent.
AUDITOR_POSITIVE = {
    ('CF88:ART.201:INC.III', 'EXT_LEI7998_1990'): ('texto vigente do inciso III = desemprego involuntario, objeto da Lei 7.998/1990 (ementa: seguro-desemprego); '
                                                   'a lei cita o "inciso IV" pela numeracao anterior'),
}


def report(a, s, rank, reform, pres):
    L = []
    add = L.append
    add('# CF88_CORRELATA_COVERAGE_AUDIT_C0 — cobertura da camada CORRELATA (CF/88 + ADCT)')
    add('')
    add('**Missão diagnóstica.** Nenhum vínculo foi adicionado, removido ou promovido. Os arquivos operacionais do Reference Engine, o microSD, o firmware, '
        'o ENTENDA e a Lei Seca não foram alterados.')
    add('')
    add('## Baseline')
    add('')
    add(f"- Branch criada de `{BASELINE['branch_from']}` @ `{BASELINE['head']}`.")
    add(f"- Tag física: `{BASELINE['physical_tag']}`.")
    add(f"- Reconciliação jurídica: `{BASELINE['legal_reconciliation']}`: 810 HUMAN_APPROVED_T1 ACTIVE, 0 pendentes.")
    add(f"- No lookup físico, as 810 explicações aprovadas viram {len(a.entenda_lookup)} linhas: "
        f"{sum(1 for v in a.entenda_lookup.values() if v['resolution'] == 'DIRECT')} DIRECT e "
        f"{sum(1 for v in a.entenda_lookup.values() if v['resolution'] == 'COVERED_BY_BLOCK')} COVERED_BY_BLOCK.")
    add('- Os 810 **não** são o universo de targets.')
    add(f"- Evidência local congelada em `{PIN.relative_to(ROOT).as_posix()}` (sha256 `{sha(PIN)[:16]}…`).")
    add('  - Ela reúne o Relations V2 legado, o acervo do cartão, as remissões reversas e as tabelas físicas.')
    add('  - Cada fonte tem sha256 próprio.')
    add('')
    add('## Preservação (verificada pela própria auditoria)')
    add('')
    add('- **RUN3:** reconstruído em diretório temporário. É byte-idêntico ao versionado: '
        f"`{pres['run3_rebuilt_in_temp_dir_byte_identical']}`.")
    add('- **REF_LOOKUP/REF_PAYLOAD:** idênticos aos do cartão: '
        f"`{all(pres['run3_ref_files_equal_card'].values())}`.")
    add('- **Tabelas do aparelho** (TARGETS, TEXT_MAP, ENTENDA_LOOKUP e REF): conferidas contra o manifesto físico: '
        f"`{pres['device_tables_equal_card']}`.")
    add('- **Arquivos operacionais:** os sha256 de `CF88_REFERENCES_CANONICAL.json`, `CF88_LINK_EXCLUSIONS.json`, '
        '`CF88_WORK_REFERENCE_ADDITIONS.json`, dos três arquivos do RUN3 e do `engine_config.json` ficam registrados no baseline.')
    add('  - Os testes os comparam com o commit de origem.')
    add('')
    add('## Números (CF permanente × ADCT)')
    add('')
    cf = lambda f: sum(1 for r in a.matrix if r['namespace'] == 'CF88' and f(r))  # noqa: E731
    ad = lambda f: sum(1 for r in a.matrix if r['namespace'] == 'ADCT' and f(r))  # noqa: E731
    newc = [c for c in a.candidates if c['promotable_to_human_review']]
    cc = lambda ns, f: sum(1 for c in newc if c['namespace'] == ns and f(c))  # noqa: E731
    add('| Medida | CF | ADCT | Total |')
    add('|---|---:|---:|---:|')
    rt_cur = Counter(a.rt[t]['namespace'] for t in a.rt if a.legal[t] == 'CURRENT' and a.rt[t]['kind'] not in ('NORMA', 'NAMESPACE'))
    add(f"| Targets do runtime CURRENT/STRUCTURAL (sem NORMA/NAMESPACE; caput contado à parte) | {rt_cur['CF88']} | {rt_cur['ADCT']} | {sum(rt_cur.values())} |")
    ex_t = Counter(e['namespace'] for e in a.excluded if e['coverage_status'] == 'TECHNICAL_TARGET_EXCLUDED')
    add(f"| Excluídos por motivo técnico: NORMA/NAMESPACE + caput dobrado em ART | {ex_t['CF88']} | {ex_t['ADCT']} | {s['excluded_technical']} |")
    ex_h = Counter(e['namespace'] for e in a.excluded if e['coverage_status'] == 'HISTORICAL_OR_REVOKED_EXCLUDED')
    add(f"| Excluídos por serem históricos ou revogados (revogados no runtime + ausentes do runtime) | {ex_h['CF88']} | {ex_h['ADCT']} | {s['excluded_historical_or_revoked']} |")
    add(f"| **Targets auditáveis** | {s['auditable_cf']} | {s['auditable_adct']} | **{s['auditable_targets']}** |")
    add(f"| … artigos (STRUCTURAL, ART ↔ CAPUT) | {cf(lambda r: r['audit_class'] == 'STRUCTURAL')} | {ad(lambda r: r['audit_class'] == 'STRUCTURAL')} | {s['auditable_structural_articles']} |")
    add(f"| … dispositivos (CURRENT) | {cf(lambda r: r['audit_class'] == 'CURRENT')} | {ad(lambda r: r['audit_class'] == 'CURRENT')} | {s['auditable_current_devices']} |")
    add(f"| Targets com CORRELATA atual visível | {cf(lambda r: r['current_correlata_count'] > 0)} | {ad(lambda r: r['current_correlata_count'] > 0)} | {s['audit_rows_with_current_correlata']} |")
    add(f"| **Novos candidatos** (target × norma, promovíveis à revisão) | {s['new_candidates_cf']} | {s['new_candidates_adct']} | **{s['new_candidates']}** |")
    for p in ('HIGH', 'MEDIUM', 'LOW'):
        add(f"| … {p} | {cc('CF88', lambda c: c['review_priority'] == p)} | {cc('ADCT', lambda c: c['review_priority'] == p)} | {s[p.lower()]} |")
    tor = Counter(c['namespace'] for c in a.candidates if c['candidate_status'] == 'TOPICAL_ONLY_REJECTED')
    add(f"| TOPICAL_ONLY rejeitados (fora da fila) | {tor['CF88']} | {tor['ADCT']} | {s['topical_only_rejected']} |")
    add(f"| Targets em GENERIC_LEGISLATIVE_RESERVATION | {s['generic_legislative_reservation_cf']} | {s['generic_legislative_reservation_adct']} | {s['generic_legislative_reservation']} |")
    add(f"| Candidatos INGESTION_REQUIRED | {cc('CF88', lambda c: c['device_status'] == 'INGESTION_REQUIRED')} | {cc('ADCT', lambda c: c['device_status'] == 'INGESTION_REQUIRED')} | {s['ingestion_required']} |")
    add(f"| Candidatos DEVICE_RESOLVABLE_NOW | {cc('CF88', lambda c: c['device_resolvable_now'])} | {cc('ADCT', lambda c: c['device_resolvable_now'])} | {s['device_resolvable_now']} |")
    add(f"| Candidatos com texto no acervo principal (MAIN_CORPUS_ROUTE_REQUIRED) | {cc('CF88', lambda c: c['device_status'] == 'MAIN_CORPUS_ROUTE_REQUIRED')} | {cc('ADCT', lambda c: c['device_status'] == 'MAIN_CORPUS_ROUTE_REQUIRED')} | {s['main_corpus_route_required']} |")
    add(f"| Targets em NEEDS_HUMAN_REVIEW | {cf(lambda r: r['coverage_status'] == 'NEEDS_HUMAN_REVIEW')} | {ad(lambda r: r['coverage_status'] == 'NEEDS_HUMAN_REVIEW')} | {s['needs_human_review_targets']} |")
    add('')
    add('**Leitura dos números**')
    add('')
    add(f"- **CORRELATAs atuais:** {s['current_correlata_links_total']} links no export RUN3, dos quais {s['current_visible_correlata_links']} visíveis e "
        f"{s['current_hidden_correlata_links']} ocultos (alvo HISTORICAL_ONLY).")
    add(f"  - Os {s['current_visible_correlata_links']} visíveis estão em {s['targets_with_current_correlata']} targets e vêm de "
        f"{len({b['relation_id'] for b in a.baseline})} relações e {len({b['destination_norm_id'] for b in a.baseline})} normas externas.")
    add('  - O número foi derivado do export, não de relatório.')
    add(f"- **Itens de revisão humana:** {s['new_candidates']} candidatos, mais {s['current_links_needing_review']} vínculos atuais com inconsistência evidente, "
        f"mais {s['needs_human_review_targets']} targets em NEEDS_HUMAN_REVIEW.")
    add(f"  - Destes targets, {s['no_automated_signal_targets']} não tiveram nenhum sinal automático. É ausência não confirmada, não ausência comprovada.")
    add('- **NO_CORRELATA_RELEVANT = 0, por desenho.** A busca textual sem sinal não basta para afirmar que um target não tem correlata.')
    add('  - Esse estado exige confirmação humana, prevista para C1.')
    add(f"- **Contagens de dispositivo** (por candidato target × norma):")
    add(f"  - DEVICE_RESOLVABLE_NOW: {s['device_resolvable_now']} candidatos, em {s['device_resolvable_now_norms']} normas.")
    add('    - O texto e o índice de artigos já estão no cartão (EXT_NORMAS/EXT_ARTIGOS).')
    add('    - Falta só a relação aprovada e a linha RELACOES.')
    add(f"  - INGESTION_REQUIRED: {s['ingestion_required']} candidatos, em {s['ingestion_required_norms']} normas sem texto no cartão.")
    add(f"  - MAIN_CORPUS_ROUTE_REQUIRED: {s['main_corpus_route_required']} candidatos, em {s['main_corpus_route_required_norms']} normas.")
    add('    - O texto já está no cartão como norma principal, mas a rota CORRELATA → norma principal nunca foi exercitada no DEVICE V1.')
    add('    - O botão 1 resolve por `RELACOES.IDX`, e o salto de artigo usa `EXT_ARTIGOS`, que só existe para as externas.')
    add(f"- **EXTERNAL_VERIFICATION_REQUIRED:** {s['external_verification_required']} candidatos, por um destes motivos:")
    add('  - vigência sem evidência local;')
    add('  - norma recente sem proveniência oficial;')
    add('  - identidade vinda de alias do auditor.')
    add(f"- **Overlay bloqueado no ADCT:** {s['engine_overlay_blocked_adct']} candidatos estão em targets com status do motor fora de CURRENT/STRUCTURAL (ADCT = UNKNOWN_VALIDITY).")
    add('  - O overlay atual do Reference Engine rejeitaria esses candidatos. Ver a seção de arquitetura.')
    add('')
    add('## Os vínculos atuais (inventário em `CF88_CORRELATA_CURRENT_BASELINE.json`)')
    add('')
    add('| Target | Norma destino | Visível | Citação no texto da norma | Avaliação C0 |')
    add('|---|---|---|---|---|')
    for b in a.baseline:
        add(f"| {b['display_target']} | {b['destination_norm_name']} | {'sim' if b['visibility'] == 'CURRENT_VISIBLE' else 'não'} | "
            f"{b['destination_text_citation']} | {b['plausibility']} |")
    add('')
    add('**Leitura da tabela**')
    add('')
    add('- **PLAUSIBLE_STRONG:** o texto da norma de destino cita literalmente o target.')
    add('- **PLAUSIBLE_NOT_VERIFIED:** nenhuma evidência contrária, mas sem prova local.')
    add('- **NEEDS_REVIEW:** inconsistência evidente, como dispositivo irmão, ementa alheia ou fan-out. As razões estão em `review_flags` e na fila `CURRENT_LINK_REVIEW`.')
    add('- **OBSOLETE_HIDDEN:** vínculo sobre target HISTORICAL_ONLY, oculto no aparelho. Exemplo: art. 40, § 4º, II/III × LC 144/2014, após a EC 103/2019.')
    add('- **Revalidação externa:** nenhum vínculo foi revalidado por pesquisa externa nesta C0.')
    add('')
    add('## Ranking diagnóstico das normas candidatas (planejamento de ingestão; frequência NÃO é prova jurídica)')
    add('')
    add('| # | Norma | Targets candidatos | HIGH | Acervo | Dispositivo |')
    add('|---:|---|---:|---:|---|---|')
    for i, r in enumerate(rank[:40], 1):
        add(f"| {i} | {r['norm_name']} (`{r['norm_key']}`) | {r['targets']} | {r['high']} | {r['acervo_status']} | {r['device_status']} |")
    add('')
    add(f"_{len(rank)} normas distintas entre os candidatos. Lista completa em `CF88_CORRELATA_CANDIDATES.json`._")
    add('')
    add('## Reforma tributária e áreas recentes (EC 132/2023, EC 136–139, LC 214/2025, LC 227/2026)')
    add('')
    add('- **Recorte:** arts. 145 a 162 da CF (inclui 149-A a 149-C e 156-A), arts. 120 a 139 do ADCT e as normas recentes listadas.')
    add('- **Base:** só o estado jurídico já registrado no projeto.')
    rr = Counter(c['candidate_status'] for c in reform)
    add(f"- **Registros no recorte:** {len(reform)}. Por estado: " + ', '.join(f'{k} {v}' for k, v in sorted(rr.items())) + '.')
    lc = [c for c in reform if c['norm_key'] in RECENT_REFORM_NORMS]
    add(f"- **Candidatos com LC 214/2025, LC 227/2026 ou EC recentes como norma:** {len(lc)}.")
    add('  - Vêm do ENTENDA aprovado.')
    add('  - A vigência e o encaixe no dispositivo exigem EXTERNAL_VERIFICATION_REQUIRED quando o registro não tem proveniência oficial.')
    add('  - Essas normas não estão no cartão (INGESTION_REQUIRED).')
    for c in lc[:20]:
        add(f"  - {c['display_target']} × {c['norm_name']}: {c['candidate_status']}, {c['confidence']}, {c['review_priority'] or '—'}, "
            f"{c['device_status']}{', EXTERNAL_VERIFICATION_REQUIRED' if c['external_verification_required'] else ''}.")
    add('- **Afirmações novas:** nada foi afirmado sem base local. Status novo de norma ou vigência pós-2026 fica como EXTERNAL_VERIFICATION_REQUIRED.')
    add('')
    add('## Classes incluídas e excluídas')
    add('')
    for k, v in UNIVERSE_RULES.items():
        if isinstance(v, list):
            add(f'- **{k}:**')
            for x in v:
                add(f'  - {x}')
        else:
            add(f'- **{k}:** {v}')
    add('')
    add('## Sinais (mantidos separados em cada candidato)')
    add('')
    for k, v in SIGNALS.items():
        if k == 'S1_RESERVA_LEGAL':
            nres = sum(len(v_) for v_ in a.reserv.values())
            add(f"- **{k}** ({nres} reservas em {len(a.reserv)} linhas de auditoria; nao geram candidato por si): {v}")
            continue
        add(f"- **{k}** ({s['signals_by_family'].get(k, 0)} sinais): {v}")
    add(f"- **Rejeitados:** {s['signals_rejected_invalid_target']} sinais apontavam para target inexistente ou ausente do runtime.")
    add('  - Exemplo: chaves legadas de redação revogada.')
    add('  - Ficam listados em `rejected_signals` e nunca viram candidato.')
    add('- **Emendas constitucionais citadas no texto:** são registradas como norma constitucional, não como correlata.')
    add('')
    add('## Arquitetura futura (somente recomendação; nada implementado)')
    add('')
    add('**Recomendação: overlay `LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json`**, análogo a `CF88_WORK_REFERENCE_ADDITIONS.json`.')
    add('')
    add('- **Catálogo importado:** o `CF88_REFERENCES_CANONICAL.json` legado nunca é editado. As exclusões continuam em `CF88_LINK_EXCLUSIONS.json`.')
    add('- **Schema por registro:**')
    add('  - `relation_id` e `target_id` (canônico; ART × CAPUT decidido no registro);')
    add('  - `destination_norm_id` e `relation_type`, com a taxonomia desta C0;')
    add('  - `legal_basis` (dispositivo e fundamento) e `source/provenance`;')
    add('  - `review_status`, com valor `HUMAN_APPROVED_CORRELATA_V1`;')
    add('  - `reviewer` e `decision_id`;')
    add('  - `device_route`: `EXT_NORMAS` ou `MAIN_CORPUS`, com `artigos_destino`.')
    add('- **Comportamento fail closed**, espelhando `work_reference_additions()`:')
    add('  - campo ausente, status não aprovado, norma fora do registro ou duplicata (target, norma) param o build;')
    add('  - target revogado ou histórico para o build.')
    add('- **Pontos a decidir antes de C2:**')
    add('  1. **Regra de status para o ADCT.** O motor marca o ADCT como UNKNOWN_VALIDITY. O overlay deveria usar o status do runtime (CF88_TARGETS.IDX) ou consolidar a errata.')
    add('  2. **Rota de dispositivo para normas do acervo principal.** Hoje o botão 1 só abre RELACOES → EXT_NORMAS.')
    add(f"  3. **Limites do cache legado.** São {a.pin['relations_v2_package']['cache_limits_firmware']['MAX_LOOKUP_V2_CACHE']} linhas de lookup e "
        f"{a.pin['relations_v2_package']['cache_limits_firmware']['MAX_NORMAS_V2_CACHE']} normas, com truncamento silencioso.")
    add('     - Ver `DEVICE_INTEGRATION/RELATIONS_V2_LEGACY_64_LINE_LIMIT.md`.')
    add(f"     - Hoje há {len(a.pin['relations_v2_package']['ext_normas'])} normas externas no cartão. A expansão precisa da correção antes de passar de 32 normas.")
    add('  4. **Relação nova no cartão.** Cada relação aprovada precisa de uma linha RELACOES no cartão, porque o firmware resolve o item pelo `relacao_id`.')
    add('')
    add('## Próximos passos sugeridos')
    add('')
    add('- **C1:** revisão humana.')
    add('  - Primeiro a fila HIGH, depois os vínculos atuais com NEEDS_REVIEW.')
    add('  - Depois a confirmação de ausência nos targets sem sinal.')
    add('- **C2:** overlay CORRELATA_ADDITIONS, com o schema acima, e RUN4 em candidato.')
    add('- **C3:** ingestão das normas INGESTION_REQUIRED aprovadas e da rota do acervo principal.')
    add('')
    add('## Artefatos')
    add('')
    for k, v in OUT.items():
        add(f'- `CORRELATA_COVERAGE_AUDIT/{v}`')
    add('- `CORRELATA_COVERAGE_AUDIT/inputs/CORRELATA_EVIDENCE_PIN.json`: evidência local congelada.')
    add('- `CORRELATA_COVERAGE_AUDIT/tools/`: o pin e a auditoria.')
    add('- `CORRELATA_COVERAGE_AUDIT/tests/`: os testes.')
    add('')
    return '\n'.join(L) + '\n'


def build_files():
    files, summary = Audit().build()
    return files, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    files, summary = build_files()
    files2, _ = build_files()
    if files != files2:
        raise AuditError('AUDIT_NOT_DETERMINISTIC ' + str([k for k in files if files[k] != files2.get(k)]))
    if a.check:
        diff = [k for k, v in files.items() if not (AUDIT / k).is_file() or (AUDIT / k).read_bytes().replace(b'\r\n', b'\n') != v]
        print(json.dumps(dict(check='OK' if not diff else 'DIFF', diff=diff), indent=1))
        sys.exit(1 if diff else 0)
    for k, v in files.items():
        (AUDIT / k).write_bytes(v)
    print(json.dumps(dict(files={k: dict(sha256=sha_b(v), bytes=len(v)) for k, v in files.items()}, summary=summary), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
