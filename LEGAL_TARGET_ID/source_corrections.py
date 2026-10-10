"""Approved source transcription corrections (updater/fontes_oficiais_senado/SOURCE_TEXT_CORRECTIONS.json) applied at parse time.

The registry is the same one the device runtime exporter applies (updater/exportar_cf88_runtime.py::apply_source_corrections). Here it is
applied to the lines handed to structure_parser.parse_structure, so every consumer of the operational text (ENTENDA NormContext, the
target status of LEGAL_TARGET_ID) sees the corrected structure without changing any source file or its sha256.

Fail closed, never generic:
  - only corrections with status APPROVED, reviewed, type SOURCE_TRANSCRIPTION_NORMALIZATION, for the parsed norm;
  - the exact raw line must occur 0 times (text already corrected, or another source) or exactly expected_occurrences times;
    any other count raises SourceCorrectionError;
  - when applied, the corrected body (text after the structural label) must be present in the versioned canonical structural source
    (cross-source verification from Git; whitespace and the spacing before punctuation are normalized, the words are not).
The changed span must be only the leading structural label (changed_span, e.g. "VII I" -> "VIII"); the body is checked identical.
"""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REGISTRY = REPO / 'updater/fontes_oficiais_senado/SOURCE_TEXT_CORRECTIONS.json'
CANONICAL = {'CF88': REPO / 'updater/backup_catalogos/catalogo_mestre_20260913_145217/1- CONSTITUI#U00c7#U00c3O FEDERAL/cf.txt'}
LABEL_RE = re.compile(r'^\s*[IVXLCDM]+(?:-[A-Z])?\s*[-–—]?\s*')


class SourceCorrectionError(RuntimeError):
    pass


def _fold(s):
    s = unicodedata.normalize('NFC', s)
    s = re.sub(r'\s+([,.;:])', r'\1', s)
    return re.sub(r'\s+', ' ', s).strip()


def load(path=REGISTRY):
    return json.loads(Path(path).read_text(encoding='utf-8'))['corrections'] if Path(path).is_file() else []


def _canonical_text(norm_id):
    p = CANONICAL.get(norm_id)
    return _fold(p.read_text(encoding='utf-8')) if p and p.is_file() else None


def apply(lines, norm_id, corrections=None):
    """Returns (lines, applied). `applied` lists the corrections used, with before/after sha256 and the cross-source evidence."""
    lines, applied = list(lines), []
    for c in (load() if corrections is None else corrections):
        if c.get('norm_id') != norm_id:
            continue
        cid = c['correction_id']
        hits = [i for i, l in enumerate(lines) if l.rstrip('\r') == c['exact_raw_text']]
        if not hits:
            continue
        if c.get('status') != 'APPROVED' or not c.get('reviewed') or c.get('correction_type') != 'SOURCE_TRANSCRIPTION_NORMALIZATION':
            raise SourceCorrectionError(f'SOURCE_CORRECTION_NOT_APPROVED {cid}')
        if len(hits) != c['expected_occurrences']:
            raise SourceCorrectionError(f"SOURCE_CORRECTION_OCCURRENCES {cid}: {len(hits)} (esperado {c['expected_occurrences']})")
        span = c.get('changed_span') or {}
        if not span.get('before') or not c['exact_raw_text'].startswith(span['before']) or not c['normalized_text'].startswith(span['after']) \
                or c['exact_raw_text'][len(span['before']):] != c['normalized_text'][len(span['after']):]:
            raise SourceCorrectionError(f'SOURCE_CORRECTION_CHANGES_BODY {cid}: so o rotulo inicial (changed_span) pode mudar')
        body = LABEL_RE.sub('', c['normalized_text'], count=1)
        canon = _canonical_text(norm_id)
        if canon is None or _fold(body) not in canon:
            raise SourceCorrectionError(f'SOURCE_CORRECTION_NOT_CROSS_VERIFIED {cid}: corpo ausente da fonte canonica versionada')
        for i in hits:
            lines[i] = c['normalized_text']
        applied.append(dict(correction_id=cid, target_hint=c.get('target_hint'), occurrences=len(hits),
                            before_sha256=hashlib.sha256(c['exact_raw_text'].encode('utf-8')).hexdigest(),
                            after_sha256=hashlib.sha256(c['normalized_text'].encode('utf-8')).hexdigest(),
                            cross_source=str(CANONICAL[norm_id].relative_to(REPO)).replace('\\', '/')))
    return lines, applied
