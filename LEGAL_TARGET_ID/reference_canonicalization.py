"""CF-REF-A2: normalize existing CF references to canonical target_ids (derived catalogs; originals untouched).

Every source record receives exactly one class:
  AUTO_MEMBER_MATCH             legacy key is already a canonical subdivision target present in the index
  ARTICLE_VS_CAPUT_RESOLVABLE   legacy article-level key; decided by provenance -> MIGRATED_TO_CAPUT | KEPT_AS_ARTICLE | NEEDS_REVIEW
  AMBIGUOUS_V2_COLLISION        legacy key collapsed by the old V2 parser; resolved only with documentary evidence, else quarantined
  INVALID_TARGET                key absent from the index; corrected only with documentary evidence, else quarantined
  OTHER_REVIEW_REQUIRED         valid target but the source evidence contradicts it (e.g. citation of another norm)
Only records that pass validate_reference_record() enter the canonical catalog (fail closed).

Usage: python reference_canonicalization.py <out_dir> <report_json>
"""
import collections
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import structure_parser as SP  # noqa: E402
import target_id as T  # noqa: E402

CF_SOURCE = REPO / 'updater/backup_catalogos/catalogo_mestre_20260913_145217/1- CONSTITUI#U00c7#U00c3O FEDERAL/cf.txt'
OPERATIONAL = REPO / 'updater/saida/1- CONSTITUIÇÃO FEDERAL/constituicao_federal_1988.txt'
END = ('Brasília, 5 de outubro de 1988',)
INDEX = HERE / 'derived/CF88_TARGET_INDEX.json'
V2 = REPO / 'LEX_MACHINA_REFERENCIAS_V2'
REL_DIR = REPO / 'LEX-MACHINA_ETAPA_2E6_SD_TESTE/montador_sd/SD_PRONTO/99_RELATIONS_V2/05_INDICES_ESP32_V2'
REL_GLOBAL = REPO / 'LEX-MACHINAETAPA_2E41/etapa2e4_work/saida/PACOTE_FUSAO_CF_2E4/99_RELATIONS_V2/01_RELACOES_GLOBAIS/RELACOES_CF88.json'
JUR_ARCHIVE = Path(r'C:\LMA\p545e\20260928')
JUR_IDX_DIR = JUR_ARCHIVE / 'LEX_MACHINA_JURIS_CF_J4_6/SD_JURIS_J4_TESTE/99_JURISPRUDENCIA_V2/05_INDICES_ESP32'
JUR_VINCULOS = JUR_ARCHIVE / 'LEX_MACHINA_JURIS_CF_J4/VINCULOS_EXPLICITOS.json'
ART_ONLY = re.compile(r'^[A-Z0-9]+:ART\.[0-9A-Z-]+$')
NOTE_RE = re.compile(r'\s*\((?:Reda|Inclu|Vide|Revog|Acrescid|Renumer|Regulamento|Promulga)[^)]*\)\s*', re.I)
OTHER_NORM_RE = re.compile(r'\b(?:da|do)\s+(?:Lei|LC\b|Lei Complementar|C[óo]digo|Decreto|Medida Provis[óo]ria|Resolu[çc][ãa]o|Regimento|Estatuto)', re.I)
CF_MENTION_RE = re.compile(r'Constitui|\bCF\b|CF/|\bADCT\b|Carta', re.I)
REMNANT_RE = re.compile(r'^\s*-?\s*([A-Z])\s*[.\-–—]\s+(.*)$', re.S)


def norm(s):
    s = unicodedata.normalize('NFC', s or '')
    s = NOTE_RE.sub(' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ targets: full text + validity status
def load_targets():
    idx = json.loads(INDEX.read_text(encoding='utf-8'))
    full, _, _ = SP.parse_structure(CF_SOURCE.read_bytes().decode('utf-8-sig'), 'CF88', end_markers=END, preview_len=10 ** 7)
    text = {t['target_id']: norm(t['preview']) for t in full}
    assert [t['target_id'] for t in full] == [t['target_id'] for t in idx['targets']], 'index drift'
    return idx, {t['target_id']: t for t in idx['targets']}, text


def build_status(tg, text):
    op_targets, _, _ = SP.parse_structure(OPERATIONAL.read_bytes().decode('utf-8-sig'), 'CF88', end_markers=END)
    op_ids = {t['target_id'] for t in op_targets}
    op_text = norm(' '.join(OPERATIONAL.read_text(encoding='utf-8').splitlines()))
    status = {}
    for tid, t in tg.items():
        if t['kind'] in ('NORMA', 'NAMESPACE', 'ARTIGO'):
            st, why = 'STRUCTURAL', 'estrutura (norma, namespace ou artigo-unidade)'
        elif t['namespace'] != 'CF88':
            st, why = 'UNKNOWN_VALIDITY', 'texto operacional vigente nao contem o ADCT'
        elif tid in op_ids:
            st, why = 'CURRENT', 'rotulo presente no texto operacional vigente (Senado)'
        elif len(text.get(tid, '')) >= 30 and text[tid][:80] in op_text:
            art = tid.split(':PAR.')[0].split(':INC.')[0].split(':CAPUT')[0]
            same = sorted(x for x in op_ids if x != tid and x.startswith(art + ':') and text.get(x, '')[:80] == text[tid][:80])
            if same:
                st, why = 'HISTORICAL_ONLY', 'rotulo renumerado: o mesmo texto esta no vigente sob ' + ', '.join(same)
            else:
                st, why = 'CURRENT', 'texto presente no texto operacional vigente (rotulo com formatacao divergente)'
        else:
            st, why = 'HISTORICAL_ONLY', 'rotulo e texto ausentes do texto operacional vigente; existe so no compilado historico'
        status[tid] = dict(status=st, reason=why, revoked_marker=bool(re.match(r'^\(?\s*Revogad', text.get(tid, ''), re.I)),
                           present_in_operational_text=tid in op_ids)
    return status


# ------------------------------------------------------------------ evidence rules
def article_vs_caput_from_text(key, evaluated_text, text):
    """Legacy V2 article key: compare the text the legacy system actually evaluated with the canonical caput text."""
    cap = key + ':CAPUT'
    ev, ct = norm(evaluated_text), text.get(cap, '')
    if not ev or not ct:
        return 'NEEDS_REVIEW', None, 'LEGACY_TEXT_UNAVAILABLE'
    if ev == ct:
        return 'MIGRATED_TO_CAPUT', cap, 'LEGACY_V2_ARTICLE_KEY_REPRESENTED_CAPUT'
    if ev.startswith(ct) and len(ev) > len(ct):
        return 'KEPT_AS_ARTICLE', key, 'LEGACY_V2_TEXT_INCLUDED_CHILD_DEVICES'
    if ct.startswith(ev) and len(ev) >= 40:
        return 'MIGRATED_TO_CAPUT', cap, 'LEGACY_V2_ARTICLE_KEY_REPRESENTED_CAPUT (texto avaliado truncado, prefixo do caput)'
    return 'NEEDS_REVIEW', None, 'LEGACY_TEXT_DIFFERS_FROM_CAPUT'


def resolve_collision(key, legacy_text, text):
    """Collapsed V2 key: the stored text starts with the suffix remnant ('-A.', 'B -'). Resolve only if the remnant names
    an existing suffixed sibling whose canonical text matches the remaining text."""
    m = REMNANT_RE.match(legacy_text or '')
    if not m:
        return None, 'NO_SUFFIX_REMNANT_IN_LEGACY_TEXT'
    cand = key + '-' + m.group(1)
    rest, ct = norm(m.group(2)), text.get(cand, '')
    if cand in text and len(rest) >= 40 and (ct.startswith(rest) or rest.startswith(ct)):
        return cand, f'LEGACY_TEXT_STARTS_WITH_SUFFIX_REMNANT_{m.group(1)}_AND_MATCHES_{cand}'
    return None, 'REMNANT_DOES_NOT_MATCH_CANDIDATE_TEXT'


def validate_reference_record(rec, tg):
    """Gate for the canonical catalog: fail closed."""
    ok, err = T.validate_target_id(rec.get('target_id'))
    if not ok:
        raise T.TargetIdError('CATALOG_INVALID_TARGET_ID', f"{rec.get('reference_id')}: {err}")
    if rec['target_id'] not in tg:
        raise T.TargetIdError('CATALOG_TARGET_NOT_IN_INDEX', f"{rec.get('reference_id')}: {rec['target_id']}")
    for f in ('reference_id', 'target_scope', 'reference_type', 'source_record_id', 'migration_status', 'validation_status'):
        if not rec.get(f):
            raise T.TargetIdError('CATALOG_MISSING_FIELD', f"{rec.get('reference_id')}: {f}")
    return True


def scope_of(tid, tg):
    return tg[tid]['kind']


# ------------------------------------------------------------------ source loaders (read-only)
def v2_segment_texts():
    d = json.loads((REPO / 'CF_SEGMENTADA_V2/CF_DISPOSITIVOS_LIMPOS.json').read_text(encoding='utf-8'))
    return {x['chave_dispositivo']: x['texto'] for x in d['dispositivos']}


def v2_device_inventory():
    occ = collections.defaultdict(set)
    for p in sorted(V2.rglob('*.json')):
        if '09_CATALOGO_EXPANSAO_200' in p.parts:
            continue
        for k in re.findall(r'"device_id"\s*:\s*"([^"]+)"', p.read_text(encoding='utf-8', errors='ignore')):
            occ[k].add(p.relative_to(REPO).as_posix())
    return occ


def pipe_rows(path):
    rows = []
    raw = path.read_bytes().decode('utf-8-sig')
    offset = 0
    for n, line in enumerate(raw.split('\n'), 1):
        if line and not line.startswith('#'):
            rows.append((n, line.rstrip('\r').split('|')))
    return rows


def lines_at_offsets(path):
    """byte offset of each line start -> line text (for LOOKUP -> target file joins)."""
    b = path.read_bytes()
    out, pos = {}, 0
    for line in b.split(b'\n'):
        out[pos] = line.decode('utf-8', errors='replace').rstrip('\r')
        pos += len(line) + 1
    return out


def main(out_dir, report_path):
    out_dir = Path(out_dir)
    idx, tg, text = load_targets()
    status = build_status(tg, text)
    v2seg = v2_segment_texts()
    records = []

    def src(layer, rid, file, key, provenance, raw=None, fields=None, extra=None):
        f = fields or {}
        records.append(dict(source_record_id=rid, source_file=file, source_layer=layer, original_device_key=key,
                            original_article=f.get('artigo'), original_paragraph=f.get('paragrafo'), original_inciso=f.get('inciso'),
                            original_alinea=f.get('alinea'), provenance=provenance, raw=raw, extra=extra or {}))

    def fields_of(key):
        try:
            t = T.parse_target_id(key)
            return dict(artigo=t['article'], paragrafo=t['paragraph'], inciso=t['inciso'], alinea=t['alinea'])
        except T.TargetIdError:
            return {}

    # 1-2. RC2 / RC1 references
    for layer, rel in (('V2_RC2_REFERENCES', '08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC2_HUMAN_REVIEWED/REFERENCIAS_RC2.json'),
                       ('V2_RC1_REFERENCES', '08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC1/REFERENCIAS_RC1.json')):
        f = 'LEX_MACHINA_REFERENCIAS_V2/' + rel
        for r in json.loads((REPO / f).read_text(encoding='utf-8'))['references']:
            src(layer, r['reference_id'], f, r['device_id'], dict(system='V2 Engine R1D1 + revisao humana' if 'RC2' in layer else 'V2 Engine R1D1 (RC1, superado pelo RC2)',
                                                                  work_id=r['work_id'], obra=r['obra'], tipo=r['tipo'], decisao_humana=r.get('decisao_humana')),
                raw=r, fields=fields_of(r['device_id']), extra=dict(evaluated_text=r.get('texto_dispositivo', '')))
    # 3. V2 distinct device ids
    inv = v2_device_inventory()
    for k in sorted(inv):
        src('V2_ALL_DISTINCT_DEVICE_IDS', 'V2DEV:' + k, sorted(inv[k])[0], k, dict(system='V2 (inventario de device_id)', files=sorted(inv[k]), file_count=len(inv[k])),
            fields=fields_of(k), extra=dict(evaluated_text=v2seg.get(k, '')))
    # 4. SD relations lookup (+ join to RELACOES.IDX and 2E41 editorial scope)
    rel_lines = lines_at_offsets(REL_DIR / 'RELACOES.IDX')
    rel_global = json.loads(REL_GLOBAL.read_text(encoding='utf-8'))
    rel_global = rel_global if isinstance(rel_global, list) else next(v for v in rel_global.values() if isinstance(v, list))
    f_rel = str((REL_DIR / 'REL_LOOKUP.IDX').relative_to(REPO)).replace('\\', '/')
    for n, r in pipe_rows(REL_DIR / 'REL_LOOKUP.IDX'):
        off, qty = int(r[5]), int(r[6])
        pos = sorted(p for p in rel_lines if p >= off)
        joined = [rel_lines[p].split('|') for p in pos[:qty]]
        scopes = sorted({g.get('origem_scope_editorial') for g in rel_global
                         for j in joined if j[6] == g.get('destino_norma') and r[1] in (g.get('origem_caminhos') or [])} - {None})
        src('SD_RELATIONS_REL_LOOKUP', f'REL_LOOKUP:L{n}', f_rel, '|'.join(r[:5]), dict(system='Relations V2 (pacote 2E4.1 -> SD teste 2E6)',
            relacoes=[j[5] for j in joined], destinos=[j[6] for j in joined], origem_scope_editorial=scopes),
            raw='|'.join(r), fields=dict(artigo=r[1], paragrafo=r[2] or None, inciso=r[3] or None, alinea=r[4] or None), extra=dict(scopes=scopes))
    # 5-6. jurisprudence J4_6 (read-only archive) + J4 explicit links evidence
    vinc = {v['vinculo_id']: v for v in json.loads(JUR_VINCULOS.read_text(encoding='utf-8'))}
    jur_lines = lines_at_offsets(JUR_IDX_DIR / 'JURISPRUDENCIA.IDX')
    f_jl = 'archive:LEX_MACHINA_JURIS_CF_J4_6/SD_JURIS_J4_TESTE/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX'
    for n, r in pipe_rows(JUR_IDX_DIR / 'JUR_LOOKUP.IDX'):
        off, qty = int(r[5]), int(r[6])
        pos = sorted(p for p in jur_lines if p >= off)
        ids = [jur_lines[p].split('|')[0] for p in pos[:qty]]
        src('SD_JURIS_J4_6_JUR_LOOKUP', f'JUR_LOOKUP:L{n}', f_jl, '|'.join(r[:5]), dict(system='Jurisprudencia CF J4 -> SD teste J4_6', vinculos=ids),
            raw='|'.join(r), fields=dict(artigo=r[1], paragrafo=r[2] or None, inciso=r[3] or None, alinea=r[4] or None),
            extra=dict(evidence=[vinc.get(i, {}).get('evidencia_vinculo', {}).get('referencia_detectada') for i in ids], vinculos=ids,
                       trechos=[vinc.get(i, {}).get('evidencia_vinculo', {}).get('trecho') for i in ids]))
    f_jid = 'archive:LEX_MACHINA_JURIS_CF_J4_6/SD_JURIS_J4_TESTE/99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX'
    for n, r in pipe_rows(JUR_IDX_DIR / 'JURISPRUDENCIA.IDX'):
        jid = r[0]
        v = vinc.get(jid, {})
        ev = v.get('evidencia_vinculo', {})
        src('SD_JURIS_J4_6_IDS', jid, f_jid, ':'.join(jid.split(':')[3:]), dict(system='Jurisprudencia CF J4 (VINCULOS_EXPLICITOS)', tribunal=r[2], tipo=r[1],
            numero=r[3], titulo=r[5], fonte=r[7] if len(r) > 7 else None, metodo=ev.get('metodo'), classe_vinculo=v.get('classe_vinculo')),
            raw='|'.join(r), fields=dict(artigo=v.get('origem_artigo'), paragrafo=v.get('origem_paragrafo'), inciso=v.get('origem_inciso'), alinea=v.get('origem_alinea')),
            extra=dict(evidence=[ev.get('referencia_detectada')], trecho=ev.get('trecho'), titulo=r[5]))

    # ---------------------------------------------------------- classification
    # V2 keys collapsed by the old parser: a suffixed sibling exists and the V2 stored text differs from the canonical text
    collided = set()
    for k, vt in v2seg.items():
        tid = k + ':CAPUT' if ART_ONLY.match(k) else k
        if any(x.startswith(tid + '-') for x in tg) and norm(vt) != text.get(tid):
            collided.add(k)
    v2_layers = ('V2_RC2_REFERENCES', 'V2_RC1_REFERENCES', 'V2_ALL_DISTINCT_DEVICE_IDS')
    out = []
    for rec in records:
        layer = rec['source_layer']
        c = dict(rec, classification=None, target_id=None, migration_status=None, migration_reason=None, candidate_targets=[], evidence=None, error=None)
        try:
            key = rec['original_device_key']
            if layer in ('SD_RELATIONS_REL_LOOKUP', 'SD_JURIS_J4_6_JUR_LOOKUP'):
                p = key.split('|')
                key = T.from_pipe_fields(*p[:5])
            elif layer == 'SD_JURIS_J4_6_IDS':
                key = T.from_colon_fields(key)
            c['legacy_target_key'] = key
        except T.TargetIdError as e:
            c.update(classification='INVALID_TARGET', migration_status='QUARANTINED', migration_reason='UNPARSEABLE_KEY', error=e.code)
            out.append(c)
            continue
        ev_text = rec['extra'].get('evaluated_text', '')
        if layer in v2_layers and key in collided:
            c['classification'] = 'AMBIGUOUS_V2_COLLISION'
            legacy = ev_text or v2seg.get(key, '')
            target, why = resolve_collision(key, legacy, text)
            c['candidate_targets'] = sorted(x for x in tg if x == key or x.startswith(key + '-'))
            c['evidence'] = dict(legacy_text=legacy[:240], legacy_text_source='texto_dispositivo' if ev_text else 'CF_SEGMENTADA_V2', rule=why)
            if target:
                c.update(target_id=target, migration_status='RESOLVED_WITH_EVIDENCE', migration_reason=why)
            else:
                c.update(migration_status='QUARANTINED', migration_reason=why)
        elif key not in tg:
            c['classification'] = 'INVALID_TARGET'
            evid = ' || '.join(x for x in rec['extra'].get('evidence', []) + rec['extra'].get('trechos', []) + [rec['extra'].get('trecho')] if x) if layer.startswith('SD_JURIS') else ''
            c['evidence'] = dict(citation=evid[:400])
            t0 = T.parse_target_id(key)
            m = re.search(r'art(?:igo)?\.?\s*(\d+)[^|]{0,40}?\bdo\s+ADCT\b', evid)
            adct = T.format_target_id('ADCT', t0['article'], paragraph=t0['paragraph'], inciso=t0['inciso'], alinea=t0['alinea']) if m else None
            if adct and adct in tg and m.group(1) == t0['article']:
                c.update(target_id=adct, migration_status='RESOLVED_WITH_EVIDENCE', migration_reason='CITATION_EXPLICITLY_NAMES_ADCT (namespace perdido na extracao)',
                         invalid_category='A_EXTRACTION_ERROR_NAMESPACE')
            else:
                cat = 'C_OTHER_NORM_CITED' if OTHER_NORM_RE.search(evid) else 'E_INVALID_DATA'
                c.update(migration_status='QUARANTINED', migration_reason='TARGET_DOES_NOT_EXIST_IN_CF88_INDEX', invalid_category=cat)
        elif ART_ONLY.match(key):
            c['classification'] = 'ARTICLE_VS_CAPUT_RESOLVABLE'
            if layer in v2_layers:
                st, tid, why = article_vs_caput_from_text(key, ev_text, text)
            elif layer == 'SD_RELATIONS_REL_LOOKUP':
                scopes = rec['extra'].get('scopes', [])
                art = key.split('.')[-1]
                if scopes and all(re.fullmatch(re.escape(art) + r',\s*caput', s.strip(), re.I) for s in scopes):
                    st, tid, why = 'MIGRATED_TO_CAPUT', key + ':CAPUT', 'SOURCE_EDITORIAL_SCOPE_SAYS_CAPUT (' + '; '.join(scopes) + ')'
                elif scopes and all(s.strip() == art for s in scopes):
                    st, tid, why = 'KEPT_AS_ARTICLE', key, 'SOURCE_EDITORIAL_SCOPE_IS_WHOLE_ARTICLE'
                else:
                    st, tid, why = 'NEEDS_REVIEW', None, 'EDITORIAL_SCOPE_MISSING_OR_MIXED: ' + '; '.join(scopes)
            else:
                cites = [x for x in rec['extra'].get('evidence', []) if x]
                if cites and all(re.search(r'\bcaput\b', x, re.I) for x in cites):
                    st, tid, why = 'MIGRATED_TO_CAPUT', key + ':CAPUT', 'CITATION_NAMES_CAPUT'
                elif cites and not any(re.search(r'\bcaput\b|§|par[aá]grafo|inciso', x, re.I) for x in cites):
                    st, tid, why = 'KEPT_AS_ARTICLE', key, 'CITATION_NAMES_ARTICLE_WITHOUT_SUBDIVISION'
                else:
                    st, tid, why = 'NEEDS_REVIEW', None, 'CITATION_EVIDENCE_MISSING_OR_MIXED'
            c.update(migration_status=st, target_id=tid, migration_reason=why)
            c['evidence'] = dict(evaluated_text=norm(ev_text)[:200], caput_text=text.get(key + ':CAPUT', '')[:200],
                                 citations=rec['extra'].get('evidence'), scopes=rec['extra'].get('scopes'))
        else:
            c.update(classification='AUTO_MEMBER_MATCH', target_id=key, migration_status='AUTO_MEMBER_MATCH', migration_reason='LEGACY_KEY_IS_CANONICAL_SUBDIVISION')
        # other-norm contradiction on otherwise valid jurisprudence links
        if c['target_id'] and layer == 'SD_JURIS_J4_6_IDS':
            cite = ' '.join(x for x in rec['extra'].get('evidence', []) if x)
            if OTHER_NORM_RE.search(cite) and not CF_MENTION_RE.search(cite):
                c.update(classification='OTHER_REVIEW_REQUIRED', migration_status='NEEDS_REVIEW', target_id=None,
                         migration_reason='CITATION_NAMES_ANOTHER_NORM_WITHOUT_CF_MENTION', evidence=dict(citation=cite[:400]))
        out.append(c)

    # ---------------------------------------------------------- catalogs
    types = dict(V2_RC2_REFERENCES='WORK_REFERENCE', V2_RC1_REFERENCES='WORK_REFERENCE_SUPERSEDED', V2_ALL_DISTINCT_DEVICE_IDS='V2_DEVICE_MENTION',
                 SD_RELATIONS_REL_LOOKUP='CORRELATA_INDEX_ENTRY', SD_JURIS_J4_6_JUR_LOOKUP='JURISPRUDENCE_INDEX_ENTRY', SD_JURIS_J4_6_IDS='JURISPRUDENCE_LINK')
    roles = dict(V2_RC2_REFERENCES='PRODUCT_REFERENCE_RC2', V2_RC1_REFERENCES='SUPERSEDED_BY_RC2', V2_ALL_DISTINCT_DEVICE_IDS='AUDIT_INVENTORY',
                 SD_RELATIONS_REL_LOOKUP='SD_TEST_INDEX', SD_JURIS_J4_6_JUR_LOOKUP='SD_TEST_INDEX', SD_JURIS_J4_6_IDS='SD_TEST_JURISPRUDENCE')
    catalog, quarantine = [], []
    for c in out:
        valid_status = c['migration_status'] in ('AUTO_MEMBER_MATCH', 'MIGRATED_TO_CAPUT', 'KEPT_AS_ARTICLE', 'RESOLVED_WITH_EVIDENCE') and c['target_id']
        if valid_status:
            raw = c['raw'] if isinstance(c['raw'], dict) else {}
            label = raw.get('obra') or c['extra'].get('titulo') or c['original_device_key']
            rec = dict(reference_id=f"CFREF:{c['source_layer']}:{c['source_record_id']}", target_id=c['target_id'], target_scope=scope_of(c['target_id'], tg),
                       target_status=status[c['target_id']]['status'], target_present_in_operational_text=status[c['target_id']]['present_in_operational_text'],
                       reference_type=types[c['source_layer']], catalog_role=roles[c['source_layer']], label=label, source_layer=c['source_layer'],
                       source_file=c['source_file'], source_record_id=c['source_record_id'], original_device_key=c['original_device_key'],
                       provenance=c['provenance'], migration_status=c['migration_status'], migration_reason=c['migration_reason'],
                       validation_status='TARGET_STRUCTURALLY_VALID', subject_id=raw.get('work_id') or (':'.join(c['source_record_id'].split(':')[:3]) if c['source_layer'] == 'SD_JURIS_J4_6_IDS' else None))
            if isinstance(c['raw'], dict):
                rec['legal_fields_preserved'] = {k: v for k, v in c['raw'].items() if k not in ('device_id', 'dispositivo')}
            validate_reference_record(rec, tg)
            catalog.append(rec)
        else:
            quarantine.append(dict(record_original=dict(source_layer=c['source_layer'], source_file=c['source_file'], source_record_id=c['source_record_id'],
                                                        original_device_key=c['original_device_key'], raw=c['raw'] if not isinstance(c['raw'], dict) else
                                                        {k: c['raw'][k] for k in ('reference_id', 'device_id', 'work_id', 'obra', 'tipo') if k in c['raw']}),
                                   classification=c['classification'], reason_code=c['migration_reason'], invalid_category=c.get('invalid_category'),
                                   candidate_targets=c['candidate_targets'], evidence=c['evidence'], manual_review_required=True))
    # ---------------------------------------------------------- duplicates
    by_key = collections.defaultdict(list)
    for r in catalog:
        by_key[(r['source_layer'], r['target_id'], r['reference_type'], r.get('subject_id'))].append(r)
    exact = possible = 0
    for k, rs in by_key.items():
        ids = [r['source_record_id'] for r in rs]
        if len(ids) != len(set(ids)):
            exact += len(ids) - len(set(ids))
        if k[3] and len(set(ids)) > 1:
            possible += len(set(ids)) - 1
            for r in rs:
                r['duplicate_class'] = 'SEMANTIC_POSSIBLE_DUPLICATE'
    for r in catalog:
        r.setdefault('duplicate_class', 'DISTINCT')
    # ---------------------------------------------------------- write
    out_dir.mkdir(parents=True, exist_ok=True)

    def dump(name, obj):
        (out_dir / name).write_bytes((json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False) + '\n').encode('utf-8'))

    stat_counts = collections.Counter(s['status'] for s in status.values())
    dump('CF88_TARGET_STATUS.json', dict(schema_version=1, index_sha256=idx['target_index_sha256'], structural_source=str(CF_SOURCE.relative_to(REPO)).replace('\\', '/'),
                                         operational_source=str(OPERATIONAL.relative_to(REPO)).replace('\\', '/'), counts=dict(sorted(stat_counts.items())),
                                         targets={k: status[k] for k in sorted(status)}))
    dump('CF88_REFERENCES_CANONICAL.json', dict(schema_version=1, index_sha256=idx['target_index_sha256'], gate='validate_reference_record()', total=len(catalog), records=catalog))
    dump('CF88_REFERENCES_QUARANTINE.json', dict(schema_version=1, total=len(quarantine), records=quarantine))
    cls = collections.Counter(c['classification'] for c in out)
    mig = collections.Counter(c['migration_status'] for c in out)
    avc = collections.Counter(c['migration_status'] for c in out if c['classification'] == 'ARTICLE_VS_CAPUT_RESOLVABLE')
    layer_cls = collections.defaultdict(collections.Counter)
    for c in out:
        layer_cls[c['source_layer']][c['classification'] + '/' + c['migration_status']] += 1
    tgt_status = collections.Counter(status[r['target_id']]['status'] for r in catalog)
    rep = dict(TOTAL_SOURCE_REFERENCES=len(out), classification=dict(sorted(cls.items())), migration=dict(sorted(mig.items())),
               article_vs_caput=dict(sorted(avc.items())), per_layer={k: dict(sorted(v.items())) for k, v in sorted(layer_cls.items())},
               VALID_CANONICAL_REFERENCES=len(catalog), QUARANTINE=len(quarantine), DUPLICATES_EXACT=exact, POSSIBLE_DUPLICATES=possible,
               catalog_target_status=dict(sorted(tgt_status.items())), target_status_counts=dict(sorted(stat_counts.items())),
               collisions=[dict(key=c['legacy_target_key'], layer=c['source_layer'], result=c['migration_status'], target=c['target_id'], rule=c['migration_reason'],
                                candidates=c['candidate_targets'], legacy_text=(c['evidence'] or {}).get('legacy_text')) for c in out if c['classification'] == 'AMBIGUOUS_V2_COLLISION'],
               invalid=[dict(record=c['source_record_id'], layer=c['source_layer'], key=c.get('legacy_target_key'), result=c['migration_status'], target=c['target_id'],
                             category=c.get('invalid_category'), citation=((c['evidence'] or {}).get('citation') or '')[:200]) for c in out if c['classification'] == 'INVALID_TARGET'],
               other_review=[dict(record=c['source_record_id'], key=c.get('legacy_target_key'), citation=((c['evidence'] or {}).get('citation') or '')[:200])
                             for c in out if c['classification'] == 'OTHER_REVIEW_REQUIRED'],
               article_examples={s: [dict(record=c['source_record_id'], layer=c['source_layer'], key=c['legacy_target_key'], target=c['target_id'], reason=c['migration_reason'])
                                     for c in out if c['classification'] == 'ARTICLE_VS_CAPUT_RESOLVABLE' and c['migration_status'] == s][:6] for s in avc},
               files={n: sha((out_dir / n).read_bytes()) for n in ('CF88_TARGET_STATUS.json', 'CF88_REFERENCES_CANONICAL.json', 'CF88_REFERENCES_QUARANTINE.json')})
    Path(report_path).write_bytes((json.dumps(rep, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in rep.items() if k not in ('collisions', 'invalid', 'other_review', 'article_examples', 'per_layer')}, ensure_ascii=False, indent=1))
    return rep


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
