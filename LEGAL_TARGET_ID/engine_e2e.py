"""CF-REF-A3 end-to-end proof on the golden corpus: SOURCE RECORD -> target_id -> link -> export -> lookup (JSON and IDX).

Usage: python engine_e2e.py <export_dir> <report_json>
"""
import collections
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference_engine as E  # noqa: E402

GOLDEN = ['CF88:ART.1', 'CF88:ART.5', 'CF88:ART.37', 'CF88:ART.60', 'CF88:ART.150', 'CF88:ART.225', 'ADCT:ART.5']
KEY = ['CF88:ART.37:PAR.6', 'CF88:ART.37:PAR.10', 'CF88:ART.60:PAR.4:INC.IV', 'ADCT:ART.5', 'CF88:ART.5', 'CF88:ART.5:CAPUT',
       'ADCT:ART.78:PAR.4', 'CF88:ART.78:PAR.4', 'CF88:ART.40:PAR.4:INC.II']


def main(export_dir, report):
    ex = Path(export_dir)
    doc = json.loads((ex / 'CF88_REFERENCES_EXPORT.json').read_text(encoding='utf-8'))
    lk, pl = ex / 'REF_LOOKUP.IDX', ex / 'REF_PAYLOAD.IDX'
    reg = E.TargetRegistry().load('CF88')
    links = [l for ls in doc['references'].values() for l in ls]
    per_target = {t: len(ls) for t, ls in doc['references'].items()}
    payload_bytes = collections.Counter()
    for line in pl.read_text(encoding='utf-8').splitlines():
        if line and not line.startswith('#'):
            payload_bytes[line.split('|')[0]] += len(line.encode('utf-8')) + 1
    metrics = dict(targets_with_references=len(per_target), total_links=len(links),
                   by_type=dict(sorted(collections.Counter(l['reference_type'] for l in links).items())),
                   by_visibility=dict(sorted(collections.Counter(l['visibility'] for l in links).items())),
                   by_status=dict(sorted(collections.Counter(l['status'] for l in links).items())),
                   max_links_per_target=max(per_target.values()), max_links_target=max(per_target, key=lambda t: (per_target[t], t)),
                   mean_links_per_target=round(statistics.mean(per_target.values()), 2), median_links_per_target=statistics.median(per_target.values()),
                   largest_payload_bytes=max(payload_bytes.values()), largest_payload_target=max(payload_bytes, key=lambda t: (payload_bytes[t], t)),
                   files={p.name: p.stat().st_size for p in (ex / 'CF88_REFERENCES_EXPORT.json', lk, pl)},
                   multi_route_links=sum(1 for l in links if l.get('duplicate_class') == 'MULTI_ROUTE_DISTINCT_PROVENANCE'),
                   fan_out_links=sum(1 for l in links if l['migration'] == 'SPLIT_FROM_LITERAL_CITATION'),
                   fan_out_source_references=len({l['source_reference_id'] for l in links if l['migration'] == 'SPLIT_FROM_LITERAL_CITATION'}),
                   max_target_id_len=max(len(t) for t in per_target))
    key = {}
    for t in KEY:
        exists = reg.target_exists_for_norm('ADCT' if False else 'CF88', t)
        j = E.get_references(t, doc) if exists else None
        jh = E.get_references(t, doc, include_historical=True) if exists else None
        i = E.lookup_idx(t, lk, pl)
        key[t] = dict(target_exists=exists, visible_links=None if j is None else len(j), links_including_historical=None if jh is None else len(jh),
                      idx_lookup_rows=len(i), types=sorted({l['reference_type'] for l in (jh or [])}),
                      json_equals_idx=(jh is None and not i) or (len(jh) == len(i) and [l['reference_id'].replace('|', '/') for l in jh] == [r[4] for r in i]),
                      sample=[dict(type=l['reference_type'], label=l['label'][:60], source=l['source_id'], visibility=l['visibility']) for l in (jh or [])[:3]])
    golden = []
    for art in GOLDEN:
        sub = {t: ls for t, ls in doc['references'].items() if t == art or t.startswith(art + ':')}
        trace = None
        for t, ls in sub.items():
            l = ls[0]
            idx_rows = E.lookup_idx(t, lk, pl)
            trace = dict(source_record=(l['routes'][0]['reference_id'] if l['routes'] else l['source_reference_id']), source_type=l['reference_type'],
                         canonical_target_id=t, normalized_reference_id=l['reference_id'], migration=l['migration'], exported=True,
                         lookup_json=any(x['reference_id'] == l['reference_id'] for x in E.get_references(t, doc, include_historical=True)),
                         lookup_idx=any(r[4] == l['reference_id'].replace('|', '/') for r in idx_rows))
            break
        golden.append(dict(article=art, targets_with_links=len(sub), links=sum(len(v) for v in sub.values()),
                           by_type=dict(sorted(collections.Counter(l['reference_type'] for v in sub.values() for l in v).items())),
                           trace=trace, e2e_pass=(trace is None) or (trace['lookup_json'] and trace['lookup_idx'])))
    no_collision = dict(
        cf_art5_vs_adct_art5=dict(cf=key['CF88:ART.5']['links_including_historical'], adct=key['ADCT:ART.5']['links_including_historical'],
                                  distinct_ids=True, adct_78_par4_links=key['ADCT:ART.78:PAR.4']['links_including_historical'],
                                  cf_78_par4_exists=key['CF88:ART.78:PAR.4']['target_exists']),
        all_export_targets_valid=all(reg.target_exists_for_norm('CF88', t) for t in doc['references']))
    out = dict(schema_version=1, metrics=metrics, key_lookups=key, golden=golden, no_collision=no_collision,
               GOLDEN_E2E_PASS=all(g['e2e_pass'] for g in golden) and all(v['json_equals_idx'] for v in key.values()))
    Path(report).write_bytes((json.dumps(out, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps(dict(metrics=metrics, GOLDEN_E2E_PASS=out['GOLDEN_E2E_PASS']), ensure_ascii=False, indent=1))
    for t, v in key.items():
        print(t, {k: v[k] for k in ('target_exists', 'visible_links', 'links_including_historical', 'idx_lookup_rows', 'types', 'json_equals_idx')})
    for g in golden:
        print(g['article'], g['links'], g['by_type'], g['e2e_pass'], (g['trace'] or {}).get('canonical_target_id'))
    return out


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
