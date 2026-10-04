"""Build the derived target index of one norm (inspection artifact; not for the SD yet).

Usage: python build_target_index.py --norma CF88 --source <text file> --output <json> [--end-marker "..."]
The index lists every structural target with parent, kind, source line and a short preview; it does not copy the norm.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import structure_parser as SP  # noqa: E402
import target_id as T  # noqa: E402


def build(norma, source, end_markers=(), article_case_sensitive=False, remission_guard=False, heading_variants=False):
    raw = Path(source).read_bytes()
    text = raw.decode('utf-8-sig')
    targets, anomalies, _ = SP.parse_structure(text, norma, end_markers=end_markers, article_case_sensitive=article_case_sensitive,
                                               remission_guard=remission_guard, heading_variants=heading_variants)
    ids = [t['target_id'] for t in targets]
    dup = len(ids) - len(set(ids))
    ordered = '\n'.join(sorted(ids)).encode('ascii')
    counts = {}
    for t in targets:
        counts[t['kind']] = counts.get(t['kind'], 0) + 1
    by_ns = {}
    for t in targets:
        by_ns.setdefault(t['namespace'], {}).setdefault(t['kind'], 0)
        by_ns[t['namespace']][t['kind']] += 1
    lens = [len(i) for i in ids]
    return dict(schema_version=1, norma_id=norma, grammar='LEGAL_TARGET_ID/target_id.py',
                source=dict(path=str(Path(source)).replace('\\', '/'), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw)),
                total_targets=len(ids), target_id_duplicates=dup, target_index_sha256=hashlib.sha256(ordered).hexdigest(),
                counts_by_kind=dict(sorted(counts.items())), counts_by_namespace={k: dict(sorted(v.items())) for k, v in sorted(by_ns.items())},
                target_id_length=dict(max=max(lens), mean=round(sum(lens) / len(lens), 2)),
                repeated_label_targets=[dict(target_id=t['target_id'], occurrences=t['occurrences']) for t in targets
                                        if t['repeated_label_occurrences'] and t['repeated_label_occurrences'] > 1],
                anomalies=anomalies, targets=targets)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--norma', required=True)
    ap.add_argument('--source', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--end-marker', action='append', default=[])
    ap.add_argument('--article-case-sensitive', action='store_true')
    a = ap.parse_args()
    idx = build(a.norma, a.source, tuple(a.end_marker), a.article_case_sensitive)
    if idx['target_id_duplicates']:
        raise SystemExit('TARGET_ID_DUPLICATES=%d: refusing to write' % idx['target_id_duplicates'])
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    Path(a.output).write_bytes((json.dumps(idx, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in idx.items() if k not in ('targets', 'anomalies', 'repeated_label_targets')}, ensure_ascii=False, indent=1))
    print('repeated_label_targets', len(idx['repeated_label_targets']), 'anomalies', len(idx['anomalies']))


if __name__ == '__main__':
    main()
