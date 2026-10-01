"""CANONICAL LAYERS audit (read-only): layers 1/2/4 by EXACT target vs the legacy per-article sources.

Inputs (never written):
- approved export LEGAL_TARGET_ID/derived/export_test/run1 (CF88_REFERENCES_EXPORT.json, 432 links);
- device overlay staging (byte copy of the SD): REF_LOOKUP.IDX, REF_PAYLOAD.IDX, CF88_TARGETS.IDX, CF88_TEXT_MAP.IDX;
- legacy SD backup: JUR_LOOKUP.IDX / JURISPRUDENCIA.IDX, REL_LOOKUP.IDX / RELACOES.IDX.

Device query mirrored here (firmware lexV1CarregarRelacoesTarget / lexV1CarregarItensRef):
ACTIVE_TARGET -> REF_LOOKUP (exact key) -> REF_PAYLOAD rows of that key -> lexV1ClassificarDestino -> one layer.
No ancestor/descendant expansion: the export has no ARTICLE_WIDE / APPLIES_TO_DESCENDANTS / COVERAGE field.

Usage: python canonical_layer_audit.py [--json OUT]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

DI = Path(__file__).resolve().parents[1]
ROOT = DI.parent
sys.path.insert(0, str(DI / 'tools'))
import device_lookup_simulator as S  # noqa: E402

SD = DI / 'staging_sd_v1/SD/99_LEX_V1'
EXPORT = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run1/CF88_REFERENCES_EXPORT.json'
LEGACY = DI / 'backups/sd_20260929T163407Z/data'
JUR_LOOKUP = LEGACY / '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX'
JUR_IDX = LEGACY / '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX'
REL_LOOKUP = LEGACY / '99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX'
REL_IDX = LEGACY / '99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX'

CORRELATA, JURIS, REFERENCIA, HIDDEN, UNKNOWN = 'CORRELATA', 'JURISPRUDENCIA', 'REFERENCIA', 'HIDDEN', 'UNKNOWN'
LAYERS = (CORRELATA, JURIS, REFERENCIA)
ART5 = ['CF88:ART.5', 'CF88:ART.5:CAPUT', 'CF88:ART.5:INC.IV', 'CF88:ART.5:INC.V', 'CF88:ART.5:INC.VI',
        'CF88:ART.5:INC.VIII', 'CF88:ART.5:INC.IX', 'CF88:ART.5:INC.XIV', 'CF88:ART.5:INC.XV',
        'CF88:ART.5:INC.XVI', 'CF88:ART.5:INC.XVII']


def classify(tipo, vis):                        # mirror of lexV1ClassificarDestino
    if vis != 'CURRENT_VISIBLE':
        return HIDDEN
    return {'CORRELATA': CORRELATA, 'JURISPRUDENCE': JURIS, 'WORK_REFERENCE': REFERENCIA}.get(tipo, UNKNOWN)


def flag(flags, layer):                         # mirror of lexV1FlagCamada
    return len(flags) >= 4 and {CORRELATA: flags[1] == 'C', JURIS: flags[2] == 'J', REFERENCIA: flags[3] == 'W'}[layer]


def rows(path):
    return [l.split('|') for l in path.read_text(encoding='utf-8').splitlines() if l and l[0] != '#']


def expected_groups():
    """export -> {target_id: {layer: set(reference_id)}} (the approved source of truth)."""
    e = json.loads(EXPORT.read_text(encoding='utf-8'))
    g = collections.defaultdict(lambda: collections.defaultdict(set))
    n = 0
    for links in e['references'].values():
        for r in links:
            n += 1
            g[r['target_id']][classify(r['reference_type'], r['visibility'])].add(r['reference_id'])
    return g, n


def device_query(dev, tid):
    """Mirror of the firmware exact-target query: {layer: [rows]} in payload order."""
    out = collections.defaultdict(list)
    for r in dev.references(tid):
        if r[0] != tid:                         # firmware stops at the first row of another key (lexv1KeyCmp)
            break
        out[classify(r[1], r[2])].append(r)
    return out


def query_keys(tid):
    """Mirror of lexV1QueryKeysForActiveTarget: the ONLY equivalence. ACTIVE_TARGET 'CF88:ART.n' comes from the TEXT_MAP
    article line, i.e. the visual caput -> [ART.n, ART.n:CAPUT]. Any other target -> [target] (no ancestor, no descendant)."""
    if tid.startswith('CF88:ART.') and ':' not in tid[len('CF88:ART.'):]:
        return [tid, tid + ':CAPUT']
    return [tid]


def device_query_union(dev, tid):
    """Mirror of the firmware lists: rows of every query key, dedup by (destination_layer, SOURCE_ID).
    Returns ({layer: [rows]}, duplicates)."""
    out, seen, dups = collections.defaultdict(list), set(), 0
    for k in query_keys(tid):
        for layer, rs in device_query(dev, k).items():
            for r in rs:
                if (layer, r[5]) in seen:
                    dups += 1
                    continue
                seen.add((layer, r[5]))
                out[layer].append(r)
    return out, dups


# ---------------- legacy (per-article) sources ----------------
def legacy_lookup(path):
    d = {}
    for p in rows(path):
        if len(p) >= 7:
            d[tuple(p[:5])] = (int(p[5]), int(p[6]))
    return d


def legacy_read(path, off, n):
    data = path.read_bytes()[off:]
    return [l.decode('utf-8').split('|') for l in data.split(b'\n')[:n]]


def legacy_best(lookup, art, par='', inc='', ali=''):
    """Mirror of buscarMelhorLookupJurisCF / buscarMelhorLookupRelationsV2: most specific key, then ARTICLE fallback."""
    tries = []
    if ali:
        tries.append((par, inc, ali))
    if inc:
        tries.append((par, inc, ''))
    if par:
        tries.append((par, '', ''))
    tries.append(('', '', ''))
    for p, i, a in tries:
        k = ('CF88', art, p, i, a)
        if k in lookup and lookup[k][1] > 0:
            return k, lookup[k]
    return None, None


def legacy_juris_list(art, par='', inc=''):
    k, v = legacy_best(legacy_lookup(JUR_LOOKUP), art, par, inc)
    return (k, [p[6] for p in legacy_read(JUR_IDX, *v)]) if k else (None, [])


def legacy_correlata_list(art, par='', inc=''):
    k, v = legacy_best(legacy_lookup(REL_LOOKUP), art, par, inc)
    return (k, [p[6] for p in legacy_read(REL_IDX, *v)]) if k else (None, [])


def parts(tid):
    art = par = inc = ''
    for p in tid.split(':')[1:]:
        if p.startswith('ART.'):
            art = p[4:]
        elif p.startswith('PAR.'):
            par = 'UNICO' if p == 'PAR.UNICO' else p[4:]
        elif p.startswith('INC.'):
            inc = p[4:]
    return art, par, inc


def audit():
    exp, total = expected_groups()
    dev = S.Device(SD)
    try:
        flags = {p[0]: p[3] for p in rows(SD / '10_TARGETS/CF88_TARGETS.IDX')}
        mapped = {p[2] for p in rows(SD / '10_TARGETS/CF88_TEXT_MAP.IDX')}
        mism = {l: [] for l in LAYERS}
        flag_mism = []
        derived = []
        for tid in sorted(set(exp) | {p[0] for p in rows(SD / '20_REFERENCES/REF_PAYLOAD.IDX')}):
            got = device_query(dev, tid)
            for l in LAYERS:
                e = exp[tid][l]
                g = {r[4] for r in got[l]}
                if e != g or len(got[l]) != len(g):
                    mism[l].append({'target': tid, 'expected': sorted(e), 'device': sorted(g)})
                for rid in sorted(e):
                    derived.append({'target_id': tid, 'destination_layer': l, 'reference_id': rid})
                if flag(flags.get(tid, '------'), l) != bool(g):
                    flag_mism.append({'target': tid, 'layer': l, 'flags': flags.get(tid), 'count': len(g)})
        # targets that only exist on an ancestor never appear on a descendant (no inheritance)
        table = []
        for tid in ART5 + ['CF88:ART.37', 'CF88:ART.37:CAPUT', 'CF88:ART.37:PAR.6']:
            got = device_query(dev, tid)
            table.append({'target': tid, 'flags': flags.get(tid), 'in_text_map': tid in mapped,
                          CORRELATA: [(r[5], r[6]) for r in got[CORRELATA]],
                          JURIS: [(r[5], r[6]) for r in got[JURIS]],
                          REFERENCIA: [(r[5], r[6]) for r in got[REFERENCIA]]})
        unreachable = sorted(t for t in exp if t not in mapped)
        # CAPUT equivalence: which ACTIVE_TARGET (TEXT_MAP) reaches each visible link through its query keys
        reach = collections.defaultdict(set)
        for a in mapped:
            for k in query_keys(a):
                reach[k].add(a)
        caput_links = [dict(d, tipo=d['reference_id'].split(':', 1)[0], reached_by=sorted(reach[d['target_id']]))
                       for d in derived if d['target_id'] in unreachable]
        hidden_only = sorted(t for t in unreachable if not any(exp[t][l] for l in LAYERS))
        dups_total, dup_detail = 0, {}
        for a in sorted(mapped):
            if len(query_keys(a)) > 1:
                _, n = device_query_union(dev, a)
                if n:
                    dup_detail[a] = n
                    dups_total += n
        art37 = [p for p in rows(SD / '20_REFERENCES/REF_PAYLOAD.IDX') if p[0].startswith('CF88:ART.37') and
                 classify(p[1], p[2]) == JURIS]
        # legacy: the V1 build cached layers 1/2 PER ARTICLE (lexV1SincronizarRelacoes keyed by "CF88:ART.5")
        legacy = {'LEGACY_JUR_LIST(ART.5)': legacy_juris_list('5'),
                  'LEGACY_CORRELATA_LIST(ART.5)': legacy_correlata_list('5'),
                  'LEGACY_JUR_LIST(ART.5,INC.VIII)': legacy_juris_list('5', inc='VIII'),
                  'LEGACY_CORRELATA_LIST(ART.5,INC.XLIII)': legacy_correlata_list('5', inc='XLIII'),
                  'LEGACY_JUR_LIST(ART.37)': legacy_juris_list('37'),
                  'LEGACY_JUR_LIST(ART.37,PAR.6)': legacy_juris_list('37', par='6')}
        # legacy jurisprudence/correlata detail resolution BY ITEM ID (used to open the item; not an article lookup)
        jur_keys = {p[0] for p in rows(JUR_IDX)}
        rel_ids = {p[5] for p in rows(REL_IDX) if len(p) > 5}
        pay = rows(SD / '20_REFERENCES/REF_PAYLOAD.IDX')
        jur_missing = [p[4] for p in pay if classify(p[1], p[2]) == JURIS and
                       p[4].split('@')[0].split(':', 1)[1] not in jur_keys]
        cor_missing = [p[4] for p in pay if classify(p[1], p[2]) == CORRELATA and
                       p[4].split('@')[0].split(':', 1)[1] not in rel_ids]
        return {
            'total_links': total,
            'per_layer': dict(collections.Counter(d['destination_layer'] for d in derived)),
            'hidden': sum(len(v[HIDDEN]) for v in exp.values()),
            'targets_with_links': len(exp),
            'mismatches': {l: len(v) for l, v in mism.items()},
            'mismatch_detail': mism,
            'flag_mismatches': flag_mism,
            'table': table,
            'art37_juris_by_target': dict(collections.Counter(p[0] for p in art37)),
            'link_targets_not_in_text_map': unreachable,
            'caput_equivalence': {'visible_links': caput_links, 'hidden_only_targets': hidden_only,
                                  'unreachable_after_rule': [c for c in caput_links if not c['reached_by']],
                                  'duplicates': dups_total, 'duplicate_detail': dup_detail},
            'legacy': {k: {'key': v[0], 'items': v[1]} for k, v in legacy.items()},
            'legacy_detail_unresolved': {'jurisprudence': jur_missing, 'correlata': cor_missing},
            'derived': derived,
        }
    finally:
        dev.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json')
    a = ap.parse_args()
    r = audit()
    print(f"links={r['total_links']} per_layer={r['per_layer']} hidden={r['hidden']} targets={r['targets_with_links']}")
    print('mismatches', r['mismatches'], 'flag_mismatches', len(r['flag_mismatches']))
    print('TARGET | FLAGS | CORRELATAS | JURISPRUDENCIA | REFERENCIAS')
    for t in r['table']:
        f = lambda xs: ', '.join(lbl for _, lbl in xs) or '-'  # noqa: E731
        print(f"{t['target']} | {t['flags']} | {f(t[CORRELATA])} | {f(t[JURIS])} | {f(t[REFERENCIA])}")
    print('art37 juris by target', r['art37_juris_by_target'])
    for k, v in r['legacy'].items():
        print(k, v['key'], v['items'])
    print('link targets not in TEXT_MAP', len(r['link_targets_not_in_text_map']), r['link_targets_not_in_text_map'])
    ce = r['caput_equivalence']
    print('caput links', len(ce['visible_links']), 'targets', len({c['target_id'] for c in ce['visible_links']}),
          'hidden-only targets', ce['hidden_only_targets'], 'unreachable after rule', len(ce['unreachable_after_rule']),
          'duplicates', ce['duplicates'])
    for c in ce['visible_links']:
        print(' ', c['target_id'], c['reference_id'], c['tipo'], c['destination_layer'], '<-', c['reached_by'])
    print('legacy detail unresolved', {k: len(v) for k, v in r['legacy_detail_unresolved'].items()})
    if a.json:
        Path(a.json).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
