"""Golden corpus (human-inspectable): for selected articles show lei-seca targets and the canonical references attached.

Usage: python build_golden_corpus.py <output.json>
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARTICLES = ['CF88:ART.1', 'CF88:ART.5', 'CF88:ART.37', 'CF88:ART.60', 'CF88:ART.150', 'CF88:ART.225', 'ADCT:ART.5']
KEY_TARGETS = ['CF88:ART.37:CAPUT', 'CF88:ART.37:PAR.6', 'CF88:ART.37:PAR.10', 'CF88:ART.37:INC.XXI', 'CF88:ART.60:PAR.4:INC.IV', 'ADCT:ART.5:PAR.1']


def main(out):
    idx = json.loads((HERE / 'derived/CF88_TARGET_INDEX.json').read_text(encoding='utf-8'))
    st = json.loads((HERE / 'derived/CF88_TARGET_STATUS.json').read_text(encoding='utf-8'))['targets']
    cat = json.loads((HERE / 'derived/CF88_REFERENCES_CANONICAL.json').read_text(encoding='utf-8'))['records']
    q = json.loads((HERE / 'derived/CF88_REFERENCES_QUARANTINE.json').read_text(encoding='utf-8'))['records']
    tg = {t['target_id']: t for t in idx['targets']}
    corpus = []
    for art in ARTICLES:
        sub = [t for k, t in tg.items() if k == art or k.startswith(art + ':')]
        kinds = collections.Counter(t['kind'] for t in sub)
        refs = [r for r in cat if r['target_id'] == art or r['target_id'].startswith(art + ':')]
        quar = [x for x in q if (x['record_original']['original_device_key'] or '').replace('|', ':').startswith(art.replace(':ART.', ':').split(':')[0])
                and any(c == art or c.startswith(art + ':') for c in x.get('candidate_targets') or [])]
        show = [r for r in refs if r['reference_type'] in ('WORK_REFERENCE', 'CORRELATA_INDEX_ENTRY', 'JURISPRUDENCE_LINK')]
        corpus.append(dict(
            article=art, parent=tg[art]['parent_id'], article_status=st[art]['status'],
            caput=dict(target_id=art + ':CAPUT', status=st[art + ':CAPUT']['status'], preview=tg[art + ':CAPUT']['preview']),
            lei_seca_targets=dict(total=len(sub), by_kind=dict(sorted(kinds.items())),
                                  examples=[dict(target_id=t['target_id'], parent_id=t['parent_id'], kind=t['kind'], status=st[t['target_id']]['status'],
                                                 preview=(t['preview'] or '')[:90]) for t in sub if t['kind'] not in ('ARTIGO', 'CAPUT')][:8]),
            references=dict(total=len(refs), by_type=dict(sorted(collections.Counter(r['reference_type'] for r in refs).items())),
                            by_migration=dict(sorted(collections.Counter(r['migration_status'] for r in refs).items())),
                            items=[dict(reference_id=r['reference_id'], target_id=r['target_id'], type=r['reference_type'], label=r['label'],
                                        provenance=r['provenance'].get('system'), migration=r['migration_status'], reason=r['migration_reason'],
                                        target_status=r['target_status']) for r in show][:15]),
            quarantined_touching=len(quar)))
    key = {k: dict(exists=k in tg, parent=tg[k]['parent_id'], kind=tg[k]['kind'], status=st[k]['status'], preview=(tg[k]['preview'] or '')[:90],
                   references=len([r for r in cat if r['target_id'] == k])) for k in KEY_TARGETS}
    doc = dict(schema_version=1, purpose='Bateria permanente humana da CF antes de generalizar para outras normas', articles=corpus, key_targets=key)
    Path(out).write_bytes((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    for c in corpus:
        print(c['article'], c['article_status'], c['lei_seca_targets']['by_kind'], c['references']['by_type'], c['references']['by_migration'])
    return doc


if __name__ == '__main__':
    main(sys.argv[1])
