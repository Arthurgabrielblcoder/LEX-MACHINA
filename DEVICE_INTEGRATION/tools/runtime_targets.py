"""CF88_RUNTIME -> canonical target index + legacy-vs-runtime diff classification (DEVICE INTEGRATION V1-A2B).

The runtime text is produced by updater/exportar_cf88_runtime.py from the locked official sources only. The target index is
built with the approved parser (LEGAL_TARGET_ID/structure_parser.py, same grammar), in strict mode (article_case_sensitive):
hyperlinked cross-references that became their own lines in the official HTML are not article/namespace headers.

Diff classes (legacy index on the old cf.txt -> runtime index):
  EXPECTED_REMOVAL_HISTORICAL  legacy HISTORICAL_ONLY/REVOKED, or text absent from the official monovigente compilation,
                               or text now belonging to another article (relocated by later amendments)
  EXPECTED_RUNTIME_CHANGE      same text in the same article under another id (official renumbering), or a device the
                               legacy parse never indexed but whose text exists in the legacy source
  UNEXPECTED_MISSING           CURRENT legacy target whose text is still in the runtime but has no target  -> BLOCK
  UNEXPECTED_NEW               runtime target with no evidence in the legacy source                         -> BLOCK
  PARSER_ERROR                 non-CURRENT legacy target whose text is in the runtime without a target      -> BLOCK
Human-reviewed exceptions (with evidence) live in DEVICE_INTEGRATION/runtime/TARGET_DIFF_REVIEWED.json.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
ROOT = DI.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
sys.path.insert(0, str(ROOT / 'updater'))
import build_target_index as BTI  # noqa: E402
import exportar_cf88_runtime as XR  # noqa: E402

LEGACY_INDEX = ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json'
REVIEWED = DI / 'runtime/TARGET_DIFF_REVIEWED.json'
END_MARKERS = ('Brasília, 5 de outubro de 1988.',)
REVOKED_RE = re.compile(r'^\(?\s*(Revogad[oa]|Suprimid[oa])', re.I)
BLOCKING = ('UNEXPECTED_MISSING', 'UNEXPECTED_NEW', 'PARSER_ERROR')


class RuntimeTargetsError(RuntimeError):
    pass


def build_runtime_index(runtime_path):
    idx = BTI.build('CF88', runtime_path, END_MARKERS, article_case_sensitive=True)
    if idx['target_id_duplicates']:
        raise RuntimeTargetsError('RUNTIME_TARGET_ID_DUPLICATES')
    bad = [a for a in idx['anomalies'] if a['code'] != 'CLOSING_MARKER']
    if bad:
        raise RuntimeTargetsError(f'RUNTIME_PARSER_ANOMALIES {bad[:5]}')
    return idx


def runtime_status(idx):
    """Legal status from the official monovigente runtime itself: '(Revogado)'/'(Suprimido)' -> REVOKED, else CURRENT."""
    by = {t['target_id']: t for t in idx['targets']}
    out = {}
    for t in idx['targets']:
        text = t['preview'] or (by.get(t['target_id'] + ':CAPUT') or {}).get('preview') or ''
        out[t['target_id']] = 'REVOKED' if REVOKED_RE.match(text) else 'CURRENT'
    return out


def _n(s):
    s = re.sub(r'\((?:Reda|Inclu|Vide|Revog|Acrescid|Renumer)[^)]*\)', '', s or '')
    return re.sub(r'\s+', ' ', s).strip().lower()


def classify(legacy_idx, runtime_idx, runtime_text, legacy_status, reviewed=None):
    reviewed = reviewed or {}
    new = {t['target_id']: t for t in runtime_idx['targets']}
    old = {t['target_id']: t for t in legacy_idx['targets']}
    by_prefix = {}
    for t in runtime_idx['targets']:
        if t['preview']:
            by_prefix.setdefault(_n(t['preview'])[:60], []).append(t['target_id'])
    rt = _n(runtime_text)
    legacy_text = _n((ROOT / legacy_idx['source']['path']).read_bytes().decode('utf-8-sig'))
    rstatus = runtime_status(runtime_idx)
    rows = []
    for tid, t in old.items():
        if tid in new:
            continue
        st = legacy_status(tid)
        p = _n(t['preview'])[:60]
        if tid in reviewed:
            cls, ev = reviewed[tid]['classification'], reviewed[tid]['evidence']
        elif st in ('HISTORICAL_ONLY', 'REVOKED'):
            cls, ev = 'EXPECTED_REMOVAL_HISTORICAL', f'legacy status {st}'
        elif rstatus.get(':'.join(tid.split(':')[:2])) == 'REVOKED':
            cls, ev = 'EXPECTED_REMOVAL_HISTORICAL', f"artigo {':'.join(tid.split(':')[:2])} revogado na compilacao monovigente"
        elif p and p in by_prefix:
            same = [x for x in by_prefix[p] if x.split(':')[:2] == tid.split(':')[:2]]
            cls = 'EXPECTED_RUNTIME_CHANGE' if same else 'EXPECTED_REMOVAL_HISTORICAL'
            ev = f'texto no runtime em {(same or by_prefix[p])[:2]}'
        elif not p:
            cls, ev = ('EXPECTED_REMOVAL_HISTORICAL', 'dispositivo estrutural sem texto proprio, ausente no runtime')
        elif p not in rt:
            cls, ev = 'EXPECTED_REMOVAL_HISTORICAL', 'texto ausente da compilacao monovigente oficial'
        else:
            cls = 'UNEXPECTED_MISSING' if st == 'CURRENT' else 'PARSER_ERROR'
            ev = 'texto presente no runtime sem target'
        rows.append(dict(target_id=tid, change='REMOVED', legacy_status=st, classification=cls, evidence=ev))
    for tid, t in new.items():
        if tid in old:
            continue
        p = _n(t['preview'])[:60]
        if tid in reviewed:
            cls, ev = reviewed[tid]['classification'], reviewed[tid]['evidence']
        elif p and p in legacy_text:
            cls, ev = 'EXPECTED_RUNTIME_CHANGE', 'texto existe na fonte legada, que nao o indexava'
        else:
            cls, ev = 'UNEXPECTED_NEW', 'sem evidencia na fonte legada'
        rows.append(dict(target_id=tid, change='ADDED', legacy_status=None, classification=cls, evidence=ev))
    rows.sort(key=lambda r: (r['change'], r['target_id']))
    counts = {}
    for r in rows:
        counts[f"{r['change']}:{r['classification']}"] = counts.get(f"{r['change']}:{r['classification']}", 0) + 1
    return rows, dict(sorted(counts.items()))


def load_reviewed():
    if not REVIEWED.is_file():
        return {}
    return {r['target_id']: r for r in json.loads(REVIEWED.read_text(encoding='utf-8'))['reviewed']}
