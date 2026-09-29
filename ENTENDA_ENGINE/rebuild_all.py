"""Rebuild every ENTENDA derived index of the CF88 pilot and batches from their committed editorial sources (deterministic).

Pending-batch evidence (a batch superseded by its final version) is never re-stamped: only its index is rebuilt from the frozen corpus.
Usage: python rebuild_all.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entenda_engine as E  # noqa: E402
import production_batch as P  # noqa: E402


def main():
    ctx = E.NormContext('CF88')
    main_corpus = E.load_corpus(HERE / 'corpus/CF88.entenda.jsonl')
    out = {'pilot_t1': E.build_entenda_index(ctx, main_corpus, HERE / 'derived/pilot_t1')}
    for bd in sorted((HERE / 'derived').glob('production_batch_*')):
        spec_p = bd / 'BATCH_SPEC.json'
        if not spec_p.is_file():
            continue
        spec = json.loads(spec_p.read_text(encoding='utf-8'))
        if spec.get('superseded_by_final'):
            scope = spec['scope']
            reused = [r for r in main_corpus if r['status'] == 'ACTIVE' and any(r['target_id'] == a or r['target_id'].startswith(a + ':') for a in scope)]
            out[bd.name] = E.build_entenda_index(ctx, reused + E.load_corpus(bd / spec['batch_corpus']), bd / spec['index_dir'])
        else:
            out[bd.name] = P.run(bd)['summary']['files']
    return out


if __name__ == '__main__':
    print(json.dumps({k: {f: v['sha256'][:16] for f, v in files.items()} for k, files in main().items()}, indent=1))
