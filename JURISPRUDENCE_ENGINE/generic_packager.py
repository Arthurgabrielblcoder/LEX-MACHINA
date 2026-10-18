"""JURISPRUDENCE_ENGINE — generic multinorm jurisprudence packager (host-only; never writes to a card).

Input: normalized relations {norm, target_id, precedent_id, origin} + one PRECEDENT RECORD per precedent {tribunal, tipo, numero, status,
titulo, fonte, ficha} + the set of fichas already on the card (+ new ficha texts). Output: the normalized jurisprudence layer of the
multinorm firmware (99_JURISPRUDENCIA_V2/06_NORMALIZADO/):
  JUR_LOOKUP.IDX       ORIGEM_NORMA|ARTIGO|PARAGRAFO|INCISO|ALINEA|OFFSET|QUANTIDADE — ONE line per query key (all links of a key coalesced
                       into one contiguous group: the firmware never depends on "first occurrence wins")
  JURISPRUDENCIA.IDX   same 8 columns as the legacy index; the row ID carries the real namespace of the target (ADCT rows say ADCT)
  03_CONTEUDO/*.TXT    only NEW fichas; one ficha per precedent, shared by every target of every norm (e.g. STF_RG_932.TXT: CF + CC)
  MULTINORM_MANIFEST.json  per-norm counts (relations, targets with J, fichas, distinct precedents, types, tribunals, provisionals)
Nothing is CF-specific: the norm comes from the target namespace (LEGAL_TARGET_ID grammar). The legacy 05_INDICES_ESP32 files are NOT
touched (the J2I CF device keeps them; the LEXV1 layer is unchanged).
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / 'LEGAL_TARGET_ID'), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import target_id as T  # noqa: E402
import juris_types as JT  # noqa: E402

LAYER = '99_JURISPRUDENCIA_V2/06_NORMALIZADO'
CONTENT = '99_JURISPRUDENCIA_V2/03_CONTEUDO'
MAX_GROUP = 255                       # LookupJurisCFCache.quantidade (uint8_t)
MAX_RELACOES_ARTIGO = 32
HEADER_LOOKUP = '#ORIGEM_NORMA|ARTIGO|PARAGRAFO|INCISO|ALINEA|OFFSET|QUANTIDADE\n'
HEADER_RECORDS = '#ID|TIPO|TRIBUNAL|NUMERO|STATUS|TITULO_CURTO|IDENTIFICADOR|FONTE\n'


class PackagerError(ValueError):
    pass


def query_key(target_id):
    """Lookup key exactly as the firmware builds it from the reading context (to_pipe_fields: 'CF88|5||XLIII|', 'CC2002|927|unico||')."""
    return T.to_pipe_fields(target_id)


def record_line(rel, p):
    norm, art, par, inc, ali = query_key(rel['target_id']).split('|')
    tail = ':'.join([norm, art, par.upper() if par else '-', inc or '-', ali or '-'])
    cells = [f"{rel['precedent_id']}:{tail}", p['tipo'], p['tribunal'], p['numero'], p['status'], p['titulo'], rel['precedent_id'], p['fonte']]
    if any('|' in c or '\n' in c for c in cells):
        raise PackagerError(f'FIELD_WITH_SEPARATOR {rel["precedent_id"]}')
    return '|'.join(cells) + '\n'


def package(relations, precedents, card_fichas, new_fichas=None, provisional_ids=(), known_targets=None):
    new_fichas = dict(new_fichas or {})
    seen, groups = set(), collections.OrderedDict()
    for rel in relations:
        t = T.parse_target_id(rel['target_id'])                         # fail closed on any malformed / unknown-namespace target
        if rel.get('norm') and rel['norm'] != t['namespace']:
            raise PackagerError(f'NORM_MISMATCH {rel}')
        if t['article'] is None:
            raise PackagerError(f'TARGET_WITHOUT_ARTICLE {rel["target_id"]}')
        if known_targets is not None and rel['target_id'] not in known_targets:
            raise PackagerError(f'TARGET_NOT_IN_INDEX {rel["target_id"]}')     # exists in the grammar but not in the norm's real index
        p = precedents.get(rel['precedent_id'])
        if p is None:
            raise PackagerError(f'PRECEDENT_WITHOUT_RECORD {rel["precedent_id"]}')
        if not JT.id_accepted(rel['precedent_id'], p['tribunal']):
            raise PackagerError(f'TRIBUNAL_NOT_ACCEPTED {rel["precedent_id"]}')
        key = (rel['target_id'], rel['precedent_id'])
        if key in seen:
            continue                                                     # the same link twice is one link
        seen.add(key)
        groups.setdefault(query_key(rel['target_id']), []).append(rel)
    look, rec = [HEADER_LOOKUP], [HEADER_RECORDS]
    offset = len(HEADER_RECORDS.encode('utf-8'))
    for key, rels in groups.items():
        if len(rels) > MAX_GROUP or len(rels) > MAX_RELACOES_ARTIGO:
            raise PackagerError(f'GROUP_TOO_LARGE {key} {len(rels)}')
        lines = [record_line(r, precedents[r['precedent_id']]) for r in rels]
        look.append(f'{key}|{offset}|{len(rels)}\n')
        rec += lines
        offset += sum(len(l.encode('utf-8')) for l in lines)
    fichas_needed = {JT.ficha(r['precedent_id']) for rels in groups.values() for r in rels}
    missing = sorted(f for f in fichas_needed if f not in card_fichas and f not in new_fichas)
    if missing:
        raise PackagerError(f'FICHA_MISSING {missing[:5]}')
    files = {f'{LAYER}/JUR_LOOKUP.IDX': ''.join(look).encode('utf-8'), f'{LAYER}/JURISPRUDENCIA.IDX': ''.join(rec).encode('utf-8')}
    files.update({f'{CONTENT}/{k}': v.encode('utf-8') for k, v in sorted(new_fichas.items()) if k in fichas_needed and k not in card_fichas})
    files[f'{LAYER}/MULTINORM_MANIFEST.json'] = (json.dumps(manifest(groups, precedents, fichas_needed, card_fichas, provisional_ids, files),
                                                             ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    return files


def manifest(groups, precedents, fichas_needed, card_fichas, provisional_ids, files):
    by_norm = collections.defaultdict(list)
    for rels in groups.values():
        for r in rels:
            by_norm[T.parse_target_id(r['target_id'])['namespace']].append(r)
    norms = {}
    for n, rels in sorted(by_norm.items()):
        pids = sorted({r['precedent_id'] for r in rels})
        norms[n] = dict(relations=len(rels), targets_with_j=len({r['target_id'] for r in rels}), query_keys=len({query_key(r['target_id']) for r in rels}),
                        distinct_precedents=len(pids), fichas=len({JT.ficha(p) for p in pids}),
                        tipos=dict(sorted(collections.Counter(precedents[p]['tipo'] for p in pids).items())),
                        tribunais=dict(sorted(collections.Counter(precedents[p]['tribunal'] for p in pids).items())),
                        provisionals=sorted(p for p in pids if p in set(provisional_ids)))
    shared = collections.defaultdict(set)
    for rels in groups.values():
        for r in rels:
            shared[JT.ficha(r['precedent_id'])].add(T.parse_target_id(r['target_id'])['namespace'])
    keys = list(groups)
    return dict(schema_version=1, kind='MULTINORM_JURIS_MANIFEST', layer=LAYER, norms=norms,
                totals=dict(relations=sum(v['relations'] for v in norms.values()), query_keys=len(keys),
                            DUPLICATE_QUERY_KEYS=len(keys) - len(set(keys)), fichas_referenced=len(fichas_needed),
                            fichas_new=len([f for f in fichas_needed if f not in card_fichas])),
                fichas_shared_across_norms=sorted(f for f, ns in shared.items() if len(ns) > 1),
                files={k: hashlib.sha256(v).hexdigest() for k, v in sorted(files.items())})


# ---------- CF fixture: J2I_FROZEN_315_198 (visible LEXV1 relations + legacy precedent records) ----------
J2I_SD = ROOT / 'JURISPRUDENCE_AUDIT/J2H_CANDIDATE_B_OVER_A/candidate/SD'
CARD = ROOT / 'JURISPRUDENCE_AUDIT/J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json'


def card_fichas():
    return {k.split('/')[-1] for k in json.loads(CARD.read_text(encoding='utf-8'))['entries'] if k.startswith(CONTENT + '/')}


def legacy_records():
    rows = [l.split('|') for l in (J2I_SD / '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX').read_text(encoding='utf-8').split('\n')[1:] if l]
    out = {}
    for r in rows:
        meta = dict(tipo=r[1], tribunal=r[2], numero=r[3], status=r[4], titulo=r[5], fonte=r[7])
        if r[6] in out and out[r[6]] != meta:
            raise PackagerError(f'INCONSISTENT_LEGACY_RECORD {r[6]}')
        out[r[6]] = meta
    return out


def cf_fixture():
    sys.path.insert(0, str(ROOT / 'JURISPRUDENCE_AUDIT'))
    import build_j2_batch as G
    vis = G.j2i_baseline()
    rels = [dict(norm=r[0].split(':')[0], target_id=r[0], precedent_id=r[5], origin='J2I_FROZEN_315_198', ref_label=r[6]) for r in vis]
    return rels, legacy_records()


def provisional_ids():
    reg = json.loads((ROOT / 'JURISPRUDENCE_AUDIT/J2_PROVISIONAL_REGISTRY.json').read_text(encoding='utf-8'))
    return [i['source_id'] for i in reg['items']]


def known_targets():
    """Real target indexes of the project: CF88/ADCT (J2I CF88_TARGETS.IDX) + CC2002 (CC2002_TARGET_INDEX.json)."""
    cf = {l.split('|', 1)[0] for l in (J2I_SD / '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')}
    cc = {t['target_id'] for t in json.loads((ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json')
                                             .read_text(encoding='utf-8'))['targets']}
    return cf | cc
