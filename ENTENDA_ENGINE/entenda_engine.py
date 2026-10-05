"""ENTENDA engine: derived editorial explanations keyed by canonical target_id (norm-agnostic).

ENTENDA is NOT Lei Seca, NOT jurisprudence, NOT references. It is an editorial layer derived from the official text:
  - the official text is never copied into or replaced by an explanation (only a snapshot/hash is kept for staleness);
  - an explanation is EDITORIAL_OUTPUT_ONLY: it must never feed correlatas, jurisprudence, references or the relations engine;
  - no automatic inheritance: get_explanation(child) never returns the parent's explanation.

Everything norm-specific comes from entenda_config.json (norm -> target index, status, text sources, corpus).
Pipeline:
  drafts (readable JSON, editorial) --stamp--> corpus <NORM>.entenda.jsonl (canonical, one explanation per line,
  with source_text_snapshot + sha256) --build--> ENTENDA_LOOKUP.IDX + ENTENDA_PAYLOAD.DAT (+ manifest), ESP32-style pair.
Usage:
  python entenda_engine.py stamp --norm CF88 --drafts <drafts.json>
  python entenda_engine.py build --norm CF88 <out_dir>
  python entenda_engine.py stale --norm CF88
"""
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / 'LEGAL_TARGET_ID'))
import structure_parser as SP  # noqa: E402
import target_id as T  # noqa: E402

CONTRACT = 'entenda-contract/1'
USAGE_POLICY = 'EDITORIAL_OUTPUT_ONLY'
SECTION_TITLES = (('o_que_diz', 'O QUE DIZ'), ('o_que_significa', 'O QUE SIGNIFICA'), ('exemplo_pratico', 'EXEMPLO PRÁTICO'),
                  ('atencao', 'ATENÇÃO'), ('palavras_dificeis', 'PALAVRAS DIFÍCEIS'))
REQUIRED_TEXT = ('o_que_diz', 'o_que_significa', 'exemplo_pratico')
ROLES = {'ARTIGO': ('OVERVIEW',), 'CAPUT': ('DEVICE', 'BLOCK'), 'PARAGRAFO': ('DEVICE', 'BLOCK'), 'PARAGRAFO_UNICO': ('DEVICE', 'BLOCK'),
         'INCISO': ('ITEM', 'BLOCK'), 'ALINEA': ('ITEM',)}
AUTONOMY = {'ARTIGO': ('AUTONOMOUS',), 'CAPUT': ('AUTONOMOUS', 'DEPENDENT_ON_PARENT'), 'PARAGRAFO': ('AUTONOMOUS', 'DEPENDENT_ON_PARENT'),
            'PARAGRAFO_UNICO': ('AUTONOMOUS', 'DEPENDENT_ON_PARENT'), 'INCISO': ('DEPENDENT_ON_PARENT',), 'ALINEA': ('DEPENDENT_ON_PARENT',)}
VALIDITY = {'CURRENT': 'CURRENT', 'HISTORICAL_ONLY': 'HISTORICAL', 'UNKNOWN_VALIDITY': 'UNKNOWN'}
STATUSES = ('ACTIVE', 'STALE', 'RETIRED')
REVIEW = ('DRAFT', 'PENDING_HUMAN_REVIEW', 'HUMAN_APPROVED_T1', 'CHANGES_REQUESTED', 'APPROVED', 'REJECTED')
EXTERNAL_VERIFICATION = 'CURRENT_OFFICIAL_EXTERNAL_VERIFICATION'
# structural presence and legal status are separate axes: a label kept in the consolidated text only with a revocation
# marker is structurally present but not legally current
REVOKED_TEXT_RE = re.compile(r'^\(?\s*Revogad[oa]', re.I)
LEGAL_STATUS = {'CURRENT': 'CURRENT', 'HISTORICAL_ONLY': 'HISTORICAL_ONLY', 'UNKNOWN_VALIDITY': 'UNKNOWN'}
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
TEMPORAL_REQUIRED = ('note_id', 'text', 'source_type', 'source_id', 'review_after')
TEMPORAL_DATES = ('valid_from', 'valid_until', 'future_effective_date', 'review_after', 'effective_change_date', 'verified_on')
# lint (warnings only; never rewrites content)
ABSOLUTE_RE = re.compile(r'\b(?:sempre|nunca|jamais|(?<!maioria )absolut[oa]s?|absolutamente|em qualquer (?:caso|hip[óo]tese|circunst[âa]ncia)|sem exce[çc][ãa]o|'
                         r'todo e qualquer|incondicional(?:mente)?|automaticamente)\b', re.I)
# real jurisprudential references (checked in the body sections only; CAMADA EXTERNA may contain them)
BODY_JURIS_RE = re.compile(r'\b(?:STF|STJ|TST|TSE|S[úu]mulas?(?:\s+Vinculantes?)?|Temas?\s+(?:n[ºo.]?\s*)?\d+|Repercuss[ãa]o\s+Geral|'
                           r'jurisprud[êe]ncias?|precedentes?)\b', re.I)
REQUIREMENT_RE = re.compile(r'\b(?:precisa|precisar[áa]|deve|dever[áa]|devem|[ée] obrigat[óo]ri[oa]|exige|exigir[áa]|somente se|s[óo] se|desde que)\b', re.I)
ID_RE = re.compile(r'^ENTENDA/(?P<target>[A-Za-z0-9:.\-]+)/(?P<variant>[A-Z][A-Z0-9_]{0,15})/(?P<version>[1-9][0-9]{0,3})$')
SHA_RE = re.compile(r'^[0-9a-f]{64}$')
# case content of courts must not be written inside ENTENDA (it belongs to the JURISPRUDENCE layer)
EXTERNAL_CASE_RE = re.compile(r'\b(?:STF|STJ|TST|TSE|TCU|S[úu]mula|Tema\s+n?º?\s*\d|ADI|ADPF|ADC|ADO|RE\s+n?º?\s*\d|REsp|HC\s+n?º?\s*\d|'
                              r'decidiu|pacificou|entendimento\s+(?:do|dos|da)\s+(?:tribunal|supremo|corte))\b', re.I)
WORD_RE = re.compile(r'[0-9A-Za-zÀ-ÿ]+')
REQUIRED_FIELDS = ('contract_version', 'explanation_id', 'explanation_key', 'target_id', 'norma_id', 'namespace', 'variant', 'editorial_version',
                   'template_version', 'prompt_version', 'granularity', 'validity', 'source', 'content', 'external_layer_notes', 'status',
                   'review_status', 'authoring', 'usage_policy')


class EntendaError(ValueError):
    def __init__(self, code, detail=''):
        super().__init__(f'{code}: {detail}')
        self.code = code


def sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def norm_text(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s)).strip()


def words(s):
    return WORD_RE.findall(s or '')


def explanation_key(target_id, variant='BASE'):
    return f'ENTENDA/{target_id}/{variant}'


def explanation_id(target_id, variant='BASE', version=1):
    return f'{explanation_key(target_id, variant)}/{version}'


def read_source_bytes(base, rel_path):
    """Bytes of a configured text source. A git-ignored source absent from a clean clone is rebuilt byte for byte from versioned
    content (text_source_reconstruction.py, sha256 verified, fail closed); a present file is always read as is."""
    path = Path(base) / rel_path
    if path.is_file() or Path(base) != REPO:
        return path.read_bytes()
    sys.path.insert(0, str(HERE))
    import text_source_reconstruction as TSR
    return TSR.reconstruct(rel_path, base)


class NormContext:
    """One norm: target index, status, current text per target (from configured sources) and structural order."""

    def __init__(self, norma_id, config_path=HERE / 'entenda_config.json', base=REPO):
        self.cfg = json.loads(Path(config_path).read_text(encoding='utf-8'))
        if norma_id not in self.cfg['norms']:
            raise EntendaError('NORM_NOT_CONFIGURED', norma_id)
        self.norma_id, self.base = norma_id, Path(base)
        self.ncfg = self.cfg['norms'][norma_id]
        self.limits = self.cfg['limits']
        idx = json.loads((self.base / self.ncfg['target_index']).read_text(encoding='utf-8'))
        if idx['norma_id'] != norma_id:
            raise EntendaError('INDEX_NORM_MISMATCH', norma_id)
        self.targets = {t['target_id']: t for t in idx['targets']}
        self.order = {t['target_id']: i for i, t in enumerate(idx['targets'])}
        st = self.ncfg.get('target_status')
        self.status = json.loads((self.base / st).read_text(encoding='utf-8'))['targets'] if st else {}
        self.children = {}
        for tid, t in self.targets.items():
            if t['parent_id']:
                self.children.setdefault(t['parent_id'], []).append(tid)
        self.text, self.text_source = {}, {}
        self.reload_text()

    def reload_text(self, overrides=None):
        """Current text of each target, from the configured sources (or from `overrides` {source_path: text} in tests)."""
        self.text, self.text_source = {}, {}
        for src in self.ncfg['text_sources']:
            path = self.base / src['path']
            raw = (overrides or {}).get(src['path'])
            data = raw.encode('utf-8') if raw is not None else read_source_bytes(self.base, src['path'])
            parsed, _, _ = SP.parse_structure(data.decode('utf-8-sig'), self.norma_id, preview_len=10 ** 6)
            info = dict(role=src['role'], path=src['path'], file_sha256=hashlib.sha256(data).hexdigest())
            for t in parsed:
                if t['namespace'] in src['namespaces'] and t['preview']:
                    self.text[t['target_id']] = norm_text(t['preview'])
                    self.text_source[t['target_id']] = info
        return self

    def exists(self, target_id):
        ok, _ = T.validate_target_id(target_id)
        return ok and target_id in self.targets

    def kind(self, target_id):
        return self.targets[target_id]['kind']

    def subtree(self, target_id):
        out, stack = [], [target_id]
        while stack:
            cur = stack.pop()
            out.append(cur)
            stack.extend(self.children.get(cur, []))
        return sorted(out, key=lambda t: self.order[t])

    def context_chain(self, target_id):
        """Structural ancestors below the namespace root, top-down (article first). Declared, never inherited."""
        chain = [a for a in T.ancestors(target_id) if self.targets.get(a, {}).get('kind') not in (None, 'NORMA', 'NAMESPACE')]
        return list(reversed(chain))

    def structurally_present(self, target_id):
        return target_id in self.targets

    def legal_status(self, target_id):
        """CURRENT, REVOKED, HISTORICAL_ONLY or UNKNOWN (independent of structural presence)."""
        if self.status.get(target_id, {}).get('revoked_marker') or REVOKED_TEXT_RE.match(self.text.get(target_id, '')):
            return 'REVOKED'
        s = self.status.get(target_id, {}).get('status') or self.ncfg.get('default_target_status')
        if s in LEGAL_STATUS:
            return LEGAL_STATUS[s]
        below = {self.legal_status(c) for c in self.children.get(target_id, [])}
        for v in ('CURRENT', 'UNKNOWN', 'HISTORICAL_ONLY', 'REVOKED'):
            if v in below:
                return v
        return 'UNKNOWN'

    def legally_current(self, target_id):
        return self.legal_status(target_id) == 'CURRENT'

    def effective_status(self, target_id):
        if self.legal_status(target_id) == 'REVOKED':
            return 'REVOKED'
        s = self.status.get(target_id, {}).get('status') or self.ncfg.get('default_target_status')
        if s in VALIDITY:
            return VALIDITY[s]
        below = {self.effective_status(c) for c in self.children.get(target_id, [])}
        for v in ('CURRENT', 'UNKNOWN', 'HISTORICAL', 'REVOKED'):
            if v in below:
                return v
        return 'UNKNOWN'

    def snapshot(self, target_id, covered=()):
        """Current official text of the target's subtree (+ covered siblings' subtrees), one line per device: target_id TAB text."""
        ids = self.subtree(target_id) + [t for c in covered for t in self.subtree(c)]
        return '\n'.join(f'{t}\t{self.text[t]}' for t in sorted(set(ids), key=lambda t: self.order[t]) if t in self.text)

    def source_info(self, target_id):
        for t in self.subtree(target_id):
            if t in self.text_source:
                return self.text_source[t]
        return None


# ---------------------------------------------------------------- validation

def _ngrams(ws, n):
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def validate_explanation(rec, ctx):
    """Fail closed. Returns True or raises EntendaError(code)."""
    for f in REQUIRED_FIELDS:
        if f not in rec:
            raise EntendaError('ENTENDA_MISSING_FIELD', f)
    if rec['contract_version'] != CONTRACT:
        raise EntendaError('ENTENDA_CONTRACT_MISMATCH', rec['contract_version'])
    if rec['usage_policy'] != USAGE_POLICY:
        raise EntendaError('ENTENDA_USAGE_POLICY', rec['usage_policy'])
    tid = rec['target_id']
    ok, err = T.validate_target_id(tid)
    if not ok:
        raise EntendaError('ENTENDA_INVALID_TARGET_ID', f'{tid}: {err}')
    parsed = T.parse_target_id(tid)
    if rec['norma_id'] != ctx.norma_id or parsed['norma_id'] != ctx.norma_id or parsed['namespace'] != rec['namespace']:
        raise EntendaError('ENTENDA_NORM_MISMATCH', tid)
    if not ctx.exists(tid):
        raise EntendaError('ENTENDA_TARGET_NOT_IN_NORM', tid)
    m = ID_RE.match(rec['explanation_id'])
    if not m or m['target'] != tid or m['variant'] != rec['variant'] or int(m['version']) != rec['editorial_version']:
        raise EntendaError('ENTENDA_BAD_EXPLANATION_ID', rec['explanation_id'])
    if rec['explanation_key'] != explanation_key(tid, rec['variant']):
        raise EntendaError('ENTENDA_BAD_EXPLANATION_KEY', rec['explanation_key'])
    kind = ctx.kind(tid)
    if kind not in ROLES:
        raise EntendaError('ENTENDA_TARGET_NOT_ELIGIBLE', f'{tid} ({kind})')
    g = rec['granularity']
    if g.get('target_kind') != kind or g.get('role') not in ROLES[kind] or g.get('semantic_autonomy') not in AUTONOMY[kind]:
        raise EntendaError('ENTENDA_GRANULARITY_INVALID', f'{tid}: {g.get("target_kind")}/{g.get("role")}/{g.get("semantic_autonomy")}')
    covered = g.get('covered_targets', [])
    if not isinstance(covered, list) or len(set(covered)) != len(covered) or tid in covered:
        raise EntendaError('ENTENDA_COVERED_INVALID', tid)
    for c in covered:
        if not ctx.exists(c) or ctx.targets[c]['parent_id'] != ctx.targets[tid]['parent_id']:
            raise EntendaError('ENTENDA_COVERED_INVALID', f'{tid}: {c} nao e irmao estrutural real')
        if ctx.effective_status(c) != 'CURRENT' and not ctx.ncfg.get('allow_historical', False):
            raise EntendaError('ENTENDA_COVERED_INVALID', f'{tid}: {c} nao e CURRENT')
    if covered and g.get('role') != 'BLOCK':
        raise EntendaError('ENTENDA_COVERED_INVALID', f'{tid}: covered_targets exige role BLOCK')
    if g.get('anchor_target_id', tid) != tid or ('display_targets' in g and g['display_targets'] != display_targets(rec, ctx)):
        raise EntendaError('ENTENDA_DISPLAY_INVALID', tid)
    if 'coverage_type' in g and (g['coverage_type'] != 'BLOCK' or not covered):
        raise EntendaError('ENTENDA_DISPLAY_INVALID', f'{tid}: coverage_type')
    if g.get('role') == 'BLOCK' and not ctx.children.get(tid) and not covered:
        raise EntendaError('ENTENDA_GRANULARITY_INVALID', f'{tid}: BLOCK sem subdivisoes nem covered_targets')
    if not (g.get('editorial_reason') or '').strip():
        raise EntendaError('ENTENDA_GRANULARITY_INVALID', f'{tid}: editorial_reason vazio')
    if g.get('context_targets') != ctx.context_chain(tid):
        raise EntendaError('ENTENDA_CONTEXT_INVALID', f'{tid}: esperado {ctx.context_chain(tid)}')
    v = rec['validity']
    status = ctx.effective_status(tid)
    if v.get('target_status') != status:
        raise EntendaError('ENTENDA_STATUS_MISMATCH', f'{tid}: {v.get("target_status")} != {status}')
    if status == 'REVOKED':
        raise EntendaError('ENTENDA_REVOKED_NOT_ALLOWED', tid)
    if rec.get('temporal') is not None:
        validate_temporal(rec['temporal'], tid)
    if status == 'HISTORICAL' and not ctx.ncfg.get('allow_historical', False):
        raise EntendaError('ENTENDA_HISTORICAL_NOT_ALLOWED', tid)
    if status == 'UNKNOWN' and not (v.get('validity_note') or '').strip():
        raise EntendaError('ENTENDA_UNKNOWN_VALIDITY_NEEDS_NOTE', tid)
    ev = v.get('external_verification')
    if ev is not None:
        if status != 'UNKNOWN' or ev.get('status') != EXTERNAL_VERIFICATION or ev.get('current_in_operational_source') is not False \
                or ev.get('current_official_external') is not True or not ev.get('verified_on') or not ev.get('evidence') \
                or ev.get('content_hash_stored') not in (False,):
            raise EntendaError('ENTENDA_EXTERNAL_VERIFICATION_INVALID', tid)
    s = rec['source']
    h = s.get('source_text_sha256')
    if not h or not SHA_RE.match(h):
        raise EntendaError('ENTENDA_MISSING_SOURCE_HASH', tid)
    if not s.get('source_text_snapshot') or sha256(s['source_text_snapshot']) != h:
        raise EntendaError('ENTENDA_SOURCE_HASH_MISMATCH', tid)
    if sorted(s.get('context_text_sha256', {})) != sorted(g['context_targets']):
        raise EntendaError('ENTENDA_CONTEXT_HASH_MISSING', tid)
    c = rec['content']
    if sorted(c) != sorted(k for k, _ in SECTION_TITLES):
        raise EntendaError('ENTENDA_SECTIONS_INVALID', f'{tid}: {sorted(c)}')
    for k in REQUIRED_TEXT:
        if not isinstance(c[k], str) or not c[k].strip():
            raise EntendaError('ENTENDA_SECTION_EMPTY', f'{tid}: {k}')
    if c['atencao'] is not None and (not isinstance(c['atencao'], str) or not c['atencao'].strip()):
        raise EntendaError('ENTENDA_SECTION_EMPTY', f'{tid}: atencao (usar null quando nao houver ponto de confusao)')
    terms = c['palavras_dificeis']
    if not isinstance(terms, list) or len(terms) > ctx.limits['max_terms'] or \
            any(sorted(t) != ['explicacao', 'termo'] or not t['termo'].strip() or not t['explicacao'].strip() for t in terms):
        raise EntendaError('ENTENDA_TERMS_INVALID', tid)
    content_texts = [c[k] for k in REQUIRED_TEXT] + ([c['atencao']] if c['atencao'] else []) + [t['termo'] + ' ' + t['explicacao'] for t in terms]
    texts = content_texts + list(rec['external_layer_notes'])
    for t in texts:
        if any(line.startswith(('#', '@')) for line in t.split('\n')) or '|' in t:
            raise EntendaError('ENTENDA_RESERVED_CHAR', tid)
    # hard block applies to the body only; external_layer_notes may name the external layer and its references
    body = [c[k] for k in REQUIRED_TEXT] + ([c['atencao']] if c['atencao'] else []) + [t['explicacao'] for t in terms]
    hit = next((EXTERNAL_CASE_RE.search(t) for t in body if EXTERNAL_CASE_RE.search(t)), None)
    if hit:
        raise EntendaError('ENTENDA_EXTERNAL_CASE_CONTENT', f'{tid}: "{hit.group(0)}" pertence a camada JURISPRUDENCIA')
    total = sum(len(words(t)) for t in content_texts)
    lo, hi = ctx.limits['words_overview'] if g['role'] == 'OVERVIEW' else ctx.limits['words_device']
    if not lo <= total <= hi:
        raise EntendaError('ENTENDA_LENGTH_OUT_OF_RANGE', f'{tid}: {total} palavras (faixa {lo}-{hi})')
    n = ctx.limits['max_verbatim_words']
    src = _ngrams([w.lower() for w in words(s['source_text_snapshot'])], n + 1)
    for k in REQUIRED_TEXT:
        if _ngrams([w.lower() for w in words(c[k])], n + 1) & src:
            raise EntendaError('ENTENDA_COPIES_OFFICIAL_TEXT', f'{tid}: {k} repete mais de {n} palavras seguidas do texto oficial')
    if rec['status'] not in STATUSES or rec['review_status'] not in REVIEW:
        raise EntendaError('ENTENDA_STATUS_INVALID', tid)
    return True


def _sentences(text):
    return {' '.join(w.lower() for w in words(s)) for s in re.split(r'(?<=[.;:!?])\s+', text) if len(words(s)) >= 8}


def similarity(a, b):
    wa, wb = {w.lower() for w in words(a) if len(w) > 3}, {w.lower() for w in words(b) if len(w) > 3}
    return round(len(wa & wb) / len(wa | wb), 3) if wa | wb else 0.0


def validate_corpus(records, ctx):
    """Every record valid + unique ids + one ACTIVE per (target, variant) + no repetition along the hierarchy."""
    seen, active = set(), set()
    for r in records:
        validate_explanation(r, ctx)
        if r['explanation_id'] in seen:
            raise EntendaError('ENTENDA_DUPLICATE_EXPLANATION_ID', r['explanation_id'])
        seen.add(r['explanation_id'])
        if r['status'] == 'ACTIVE':
            if r['explanation_key'] in active:
                raise EntendaError('ENTENDA_DUPLICATE_ACTIVE_TARGET', r['explanation_key'])
            active.add(r['explanation_key'])
    by_tid = {r['target_id']: r for r in records if r['status'] == 'ACTIVE'}
    pairs = []
    for tid, r in by_tid.items():
        for anc in r['granularity']['context_targets']:
            if anc in by_tid:
                a = by_tid[anc]
                for k in REQUIRED_TEXT:
                    if _sentences(r['content'][k]) & _sentences(a['content'][k]):
                        raise EntendaError('ENTENDA_REPEATED_ACROSS_HIERARCHY', f'{tid} x {anc}: {k}')
                sim = {k: similarity(r['content'][k], a['content'][k]) for k in REQUIRED_TEXT}
                if max(sim.values()) > ctx.limits['max_section_similarity']:
                    raise EntendaError('ENTENDA_REPEATED_ACROSS_HIERARCHY', f'{tid} x {anc}: {sim}')
                pairs.append(dict(child=tid, parent=anc, similarity=sim))
    covered_by = {}
    for tid, r in by_tid.items():
        for c in r['granularity'].get('covered_targets', []):
            if c in by_tid:
                raise EntendaError('ENTENDA_COVERED_TARGET_HAS_OWN_EXPLANATION', f'{c} (coberto por {tid})')
            if c in covered_by:
                raise EntendaError('ENTENDA_COVERED_TWICE', f'{c}: {covered_by[c]} e {tid}')
            covered_by[c] = tid
    return pairs


# ---------------------------------------------------------------- stale

def validate_temporal(t, tid=''):
    """Generic temporal metadata: legislation published but not yet in force, transitional rules with a future date."""
    if not isinstance(t, dict) or not isinstance(t.get('time_sensitive'), bool) or not isinstance(t.get('notes'), list) or not t['notes']:
        raise EntendaError('ENTENDA_TEMPORAL_INVALID', tid)
    ids = set()
    for n in t['notes']:
        if any(not n.get(k) for k in TEMPORAL_REQUIRED) or n['note_id'] in ids:
            raise EntendaError('ENTENDA_TEMPORAL_INVALID', f'{tid}: {n.get("note_id")}')
        ids.add(n['note_id'])
        for k in TEMPORAL_DATES:
            if n.get(k) is not None and not DATE_RE.match(n[k]):
                raise EntendaError('ENTENDA_TEMPORAL_INVALID', f'{tid}: {k}={n[k]}')
        if n.get('valid_from') and n.get('valid_until') and n['valid_from'] > n['valid_until']:
            raise EntendaError('ENTENDA_TEMPORAL_INVALID', f'{tid}: valid_from > valid_until')
        if '|' in n['text'] or n['text'].startswith(('#', '@')):
            raise EntendaError('ENTENDA_RESERVED_CHAR', tid)
    return True


def temporal_state(note, as_of):
    """State of a temporal note on a given date (ISO). Deterministic: the date is always explicit, never the system clock."""
    if note.get('future_effective_date') and as_of < note['future_effective_date']:
        state = 'NOT_YET_EFFECTIVE'
    elif note.get('valid_until') and as_of > note['valid_until']:
        state = 'EXPIRED'
    else:
        state = 'IN_EFFECT'
    return dict(state=state, review_due=as_of >= note['review_after'])


def temporal_report(corpus, as_of):
    out = []
    for r in corpus:
        if r['status'] != 'ACTIVE' or not r.get('temporal'):
            continue
        for n in r['temporal']['notes']:
            out.append(dict(target_id=r['target_id'], explanation_id=r['explanation_id'], note_id=n['note_id'], as_of=as_of,
                            **temporal_state(n, as_of), note=n))
    return out


def check_stale(target_id, current_text, corpus, variant='BASE', current_context=None):
    """Compare the current official text of a target (subtree snapshot) with the hash the explanation was written on."""
    rec = get_explanation(target_id, corpus, variant)
    if rec is None:
        return dict(target_id=target_id, state='NO_EXPLANATION')
    if not current_text:
        return dict(target_id=target_id, explanation_id=rec['explanation_id'], state='ORPHANED_TARGET')
    cur = sha256(current_text)
    if cur != rec['source']['source_text_sha256']:
        return dict(target_id=target_id, explanation_id=rec['explanation_id'], state='STALE_TEXT_CHANGED',
                    stored=rec['source']['source_text_sha256'], current=cur)
    changed = sorted(k for k, h in rec['source']['context_text_sha256'].items() if current_context is not None and current_context.get(k) != h)
    if changed:
        return dict(target_id=target_id, explanation_id=rec['explanation_id'], state='STALE_CONTEXT_CHANGED', changed_context=changed)
    return dict(target_id=target_id, explanation_id=rec['explanation_id'], state='FRESH')


def context_hashes(ctx, target_id):
    return {c: (sha256(ctx.text[c]) if c in ctx.text else None) for c in ctx.context_chain(target_id)}


def stale_report(corpus, ctx):
    return [check_stale(r['target_id'], ctx.snapshot(r['target_id'], r['granularity'].get('covered_targets', [])) if ctx.exists(r['target_id']) else '',
                        corpus, r['variant'],
                        context_hashes(ctx, r['target_id']) if ctx.exists(r['target_id']) else {})
            for r in corpus if r['status'] == 'ACTIVE']


# ---------------------------------------------------------------- corpus

def load_corpus(path):
    p = Path(path)
    if not p.is_file():
        return []
    return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]


def write_corpus(records, path, ctx):
    records = sorted(records, key=lambda r: (ctx.order[r['target_id']], r['variant'], r['editorial_version']))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n' for r in records).encode('utf-8'))
    return records


def stamp(drafts, ctx, existing=()):
    """Drafts (editorial content) -> canonical records. A record already stamped keeps its original snapshot/hash
    (this is what makes staleness detectable); changing content requires a new editorial_version."""
    old = {r['explanation_id']: r for r in existing}
    d = drafts
    out = []
    new_versions = {}
    for e in d['explanations']:
        tid, variant, ver = e['target_id'], e.get('variant', 'BASE'), e.get('editorial_version', 1)
        if not ctx.exists(tid):
            raise EntendaError('ENTENDA_TARGET_NOT_IN_NORM', tid)
        eid = explanation_id(tid, variant, ver)
        content = {k: e['content'].get(k) for k, _ in SECTION_TITLES}
        prev = old.get(eid)
        if prev and (prev['content'] != content or prev['external_layer_notes'] != e.get('external_layer_notes', [])
                     or prev.get('temporal') != e.get('temporal')):
            raise EntendaError('ENTENDA_CONTENT_CHANGED_WITHOUT_VERSION_BUMP', eid)
        covered = e.get('covered_targets', [])
        if prev:
            source = prev['source']
        else:
            snap = ctx.snapshot(tid, covered)
            if not snap:
                raise EntendaError('ENTENDA_NO_SOURCE_TEXT', tid)
            info = ctx.source_info(tid)
            source = dict(text_source_role=info['role'], text_source_path=info['path'], text_source_file_sha256=info['file_sha256'],
                          snapshot_scope='SUBTREE+COVERED' if covered else 'SUBTREE', source_text_snapshot=snap, source_text_sha256=sha256(snap),
                          context_text_sha256=context_hashes(ctx, tid))
        rec = dict(contract_version=CONTRACT, explanation_id=eid, explanation_key=explanation_key(tid, variant), target_id=tid,
                   norma_id=ctx.norma_id, namespace=T.parse_target_id(tid)['namespace'], variant=variant, editorial_version=ver,
                   template_version=d['template_version'], prompt_version=d['prompt_version'],
                   granularity=dict(target_kind=ctx.kind(tid), role=e['role'], semantic_autonomy=e['semantic_autonomy'],
                                    context_targets=ctx.context_chain(tid), editorial_reason=e['editorial_reason'],
                                    **({'anchor_target_id': tid, 'covered_targets': covered, 'coverage_type': 'BLOCK',
                                        'display_targets': sorted([tid] + covered, key=lambda t: ctx.order[t])} if covered else {}),
                                    **({'display_topic': e['display_topic']} if e.get('display_topic') else {})),
                   validity=dict(target_status=ctx.effective_status(tid), validity_note=e.get('validity_note'),
                                 **({'external_verification': e['external_verification']} if e.get('external_verification') else {})),
                   source=source, content=content, external_layer_notes=e.get('external_layer_notes', []),
                   status='ACTIVE', review_status=e.get('review_status', d['review_status']), authoring=dict(d['authoring']),
                   usage_policy=USAGE_POLICY)
        if e.get('temporal'):
            rec['temporal'] = e['temporal']
        if e.get('human_review') or d.get('human_review'):
            rec['human_review'] = dict(d.get('human_review') or {}, **(e.get('human_review') or {}))
        out.append(rec)
        new_versions[rec['explanation_key']] = max(ver, new_versions.get(rec['explanation_key'], 0))
    # earlier versions superseded by a new editorial_version are kept as evidence (RETIRED), never deleted
    done = {r['explanation_id'] for r in out}
    for r in existing:
        if r['explanation_id'] in done:
            continue
        if new_versions.get(r['explanation_key'], 0) > r['editorial_version']:
            r = dict(r, status='RETIRED', review_status='CHANGES_REQUESTED' if r['review_status'] == 'PENDING_HUMAN_REVIEW' else r['review_status'],
                     superseded_by=explanation_id(r['target_id'], r['variant'], new_versions[r['explanation_key']]))
        out.append(r)
    return out


def get_explanation(target_id, corpus, variant='BASE'):
    """Exact target only (latest ACTIVE/STALE version). Never falls back to the parent: context is declared, not inherited."""
    ok, err = T.validate_target_id(target_id)
    if not ok:
        raise EntendaError('LOOKUP_INVALID_TARGET_ID', f'{target_id}: {err}')
    hits = [r for r in corpus if r['target_id'] == target_id and r['variant'] == variant and r['status'] in ('ACTIVE', 'STALE')]
    return max(hits, key=lambda r: r['editorial_version']) if hits else None


ROMAN_ORDER = re.compile(r'^[IVXLCDM]+')


def _art_label(t):
    n = t['article']
    m = re.match(r'^(\d+)(.*)$', n)
    num = f'{m.group(1)}º{m.group(2)}' if int(m.group(1)) < 10 else n
    return ('ADCT, art. ' if t['namespace'] != t['norma_id'] else 'Art. ') + num


def _last_label(t):
    if t['alinea']:
        return 'alínea', t['alinea']
    if t['inciso']:
        return 'inciso', t['inciso']
    if t['paragraph']:
        if t['paragraph'] == 'UNICO':
            return 'parágrafo único', None
        m = re.match(r'^(\d+)(.*)$', t['paragraph'])
        return '§', (f'{m.group(1)}º{m.group(2)}' if int(m.group(1)) < 10 else t['paragraph'])
    if t['caput']:
        return 'caput', None
    return None, None


def _join(items):
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' e ' + items[-1]


def target_label(target_id):
    """Human label derived from the canonical target_id (e.g. 'Art. 5º, § 4º, inciso IV')."""
    t = T.parse_target_id(target_id)
    if not t['article']:
        return target_id
    parts = [_art_label(t)]
    if t['paragraph']:
        k, v = _last_label(dict(t, inciso=None, alinea=None))
        parts.append(k if v is None else f'{k} {v}')
    if t['inciso']:
        parts.append(f"inciso {t['inciso']}")
    if t['alinea']:
        parts.append(f"alínea \"{t['alinea']}\"")
    if t['caput'] and not (t['paragraph'] or t['inciso']):
        parts.append('caput')
    return ', '.join(parts)


def display_targets(rec, ctx=None):
    g = rec['granularity']
    ids = [rec['target_id']] + list(g.get('covered_targets', []))
    return sorted(ids, key=lambda t: ctx.order[t]) if ctx else g.get('display_targets', ids)


def group_label(ids):
    """'Art. 5º, incisos IV, V, IX e XIV' for siblings of the same kind; otherwise the individual labels joined."""
    if len(ids) == 1:
        return target_label(ids[0])
    ps = [T.parse_target_id(i) for i in ids]
    kinds = {_last_label(p)[0] for p in ps}
    parents = {T.parent_target_id(i) for i in ids}
    if len(kinds) == 1 and len(parents) == 1 and None not in kinds and 'caput' not in kinds and 'parágrafo único' not in kinds:
        kind = kinds.pop()
        vals = [_last_label(p)[1] for p in ps]
        prefix = target_label(parents.pop()).replace(', caput', '')
        noun = {'inciso': 'incisos', 'alínea': 'alíneas', '§': '§§'}[kind]
        vals = [f'"{v}"' for v in vals] if kind == 'alínea' else vals
        return f'{prefix}, {noun} {_join(vals)}'
    return _join([target_label(i) for i in ids])


def display_title(rec):
    """Display title generated from editorial metadata (never hardcoded): label of all displayed targets + optional topic."""
    topic = rec['granularity'].get('display_topic')
    label = group_label(display_targets(rec))
    return f'{label} — {topic}' if topic else label


def resolve_explanation(target_id, corpus, variant='BASE'):
    """Product lookup (ENTENDA button). DIRECT when the target has its own explanation; COVERED_BY_BLOCK when an explanation
    explicitly lists it in covered_targets. Explicit editorial coverage only: never structural inheritance from the parent."""
    rec = get_explanation(target_id, corpus, variant)
    if rec:
        return dict(record=rec, matched_target_id=target_id, anchor_target_id=rec['target_id'], resolution_type='DIRECT',
                    display_title=display_title(rec), display_targets=display_targets(rec))
    hits = [r for r in corpus if r['variant'] == variant and r['status'] in ('ACTIVE', 'STALE')
            and target_id in r['granularity'].get('covered_targets', [])]
    if not hits:
        return None
    rec = max(hits, key=lambda r: r['editorial_version'])
    return dict(record=rec, matched_target_id=target_id, anchor_target_id=rec['target_id'], resolution_type='COVERED_BY_BLOCK',
                display_title=display_title(rec), display_targets=display_targets(rec))


def context_links(target_id, corpus):
    """Context targets of an explanation that have their own explanation (ids only; content is never merged)."""
    rec = get_explanation(target_id, corpus)
    if rec is None:
        return []
    return [c for c in rec['granularity']['context_targets'] if get_explanation(c, corpus)]


# ---------------------------------------------------------------- build (ESP32-style pair)

def _reference_counts(ctx):
    p = ctx.ncfg.get('reference_export')
    if not p or not (ctx.base / p).is_file():
        return {}
    doc = json.loads((ctx.base / p).read_text(encoding='utf-8'))
    return {t: sum(1 for l in ls if l['visibility'] != 'HISTORICAL_HIDDEN_BY_DEFAULT') for t, ls in doc['references'].items()}


def display_validity(rec):
    """UNKNOWN in the operational source but verified current in official external material -> CURRENT_OFFICIAL_EXTERNAL."""
    ev = rec['validity'].get('external_verification')
    return 'CURRENT_OFFICIAL_EXTERNAL' if ev and ev.get('current_official_external') else rec['validity']['target_status']


def lint(rec, ctx, by_tid):
    """Editorial warnings for human review (never blocking, never rewriting)."""
    c, g, out = rec['content'], rec['granularity'], []
    sections = {k: c[k] for k in REQUIRED_TEXT}
    if c['atencao']:
        sections['atencao'] = c['atencao']
    for k, t in sections.items():
        for m in ABSOLUTE_RE.finditer(t):
            out.append(dict(code='ABSOLUTE_CLAIM', section=k, detail=m.group(0)))
        for m in BODY_JURIS_RE.finditer(t):
            out.append(dict(code='JURISPRUDENCE_WORDING_IN_BODY', section=k, detail=m.group(0)))
    near = _ngrams([w.lower() for w in words(rec['source']['source_text_snapshot'])], 8)
    for k in REQUIRED_TEXT:
        hits = _ngrams([w.lower() for w in words(c[k])], 8) & near
        if hits:
            out.append(dict(code='NEAR_COPY_OF_OFFICIAL_TEXT', section=k, detail=' '.join(sorted(hits)[0])))
    for anc in g['context_targets']:
        if anc in by_tid:
            sim = max(similarity(c[k], by_tid[anc]['content'][k]) for k in REQUIRED_TEXT)
            if sim > 0.2:
                out.append(dict(code='PARENT_REPETITION', section='*', detail=f'{anc}: {sim}'))
    for sent in re.split(r'(?<=[.;:!?])\s+', c['exemplo_pratico']):
        if REQUIREMENT_RE.search(sent):
            out.append(dict(code='EXAMPLE_REQUIREMENT_LANGUAGE', section='exemplo_pratico', detail=sent[:140]))
    body = ' '.join(sections.values()).lower()
    snap = rec['source']['source_text_snapshot'].lower()
    for t in c['palavras_dificeis']:
        stems = [w.lower()[:max(4, len(w) - 3)] for w in words(t['termo']) if len(w) > 3] or [t['termo'].lower()]
        if not all(st in body or st in snap for st in stems):
            out.append(dict(code='TERM_NOT_USED', section='palavras_dificeis', detail=t['termo']))
        if len(t['explicacao']) < 25:
            out.append(dict(code='TERM_LOW_UTILITY', section='palavras_dificeis', detail=t['termo']))
    total = sum(len(words(t)) for t in sections.values()) + sum(len(words(t['termo'] + ' ' + t['explicacao'])) for t in c['palavras_dificeis'])
    hi = (ctx.limits['words_overview'] if g['role'] == 'OVERVIEW' else ctx.limits['words_device'])[1]
    if total > 0.85 * hi:
        out.append(dict(code='LONG_EXPLANATION', section='*', detail=f'{total} palavras (limite {hi})'))
    return [dict(target_id=rec['target_id'], explanation_id=rec['explanation_id'], **w) for w in out]


def render_payload(rec, freshness, ref_count):
    g, c = rec['granularity'], rec['content']
    lines = [f"@{rec['explanation_id']}", f"T|{rec['target_id']}", f"K|{g['target_kind']}|{g['role']}|{g['semantic_autonomy']}",
             f"V|{display_validity(rec)}", f"R|{rec['review_status']}", f"F|{freshness}",
             f"H|{rec['source']['source_text_sha256'][:16]}"]
    lines.append(f'D|{display_title(rec)}')
    if g.get('covered_targets'):
        lines.append('X|' + ','.join(display_targets(rec)))
    lines += [f'C|{t}' for t in g['context_targets']]
    lines += [f'B|{t}' for t in g.get('covered_targets', [])]
    if ref_count:
        lines.append(f'N|{ref_count}')
    if rec['validity'].get('validity_note'):
        lines.append(f"W|{rec['validity']['validity_note']}")
    if rec.get('temporal', {}).get('time_sensitive'):
        lines.append(f"Z|TIME_SENSITIVE|{min(n['review_after'] for n in rec['temporal']['notes'])}")
    for key, title in SECTION_TITLES:
        val = c[key]
        if not val:
            continue
        lines.append(f'#{title}')
        lines += [f"{t['termo']}|{t['explicacao']}" for t in val] if key == 'palavras_dificeis' else val.split('\n')
    if rec['external_layer_notes']:
        lines.append('#CAMADAS EXTERNAS')
        lines += rec['external_layer_notes']
    if rec.get('temporal'):
        t = rec['temporal']
        lines.append('#NOTAS TEMPORAIS')
        lines += [f"[{n['note_id']}; revisar após {n['review_after']}] {n['text']}" for n in t['notes']]
    lines.append('@END')
    return ('\n'.join(lines) + '\n').encode('utf-8')


def build_entenda_index(ctx, corpus, out_dir):
    """Validated corpus -> ENTENDA_LOOKUP.IDX (sorted target_id -> byte offset/length) + ENTENDA_PAYLOAD.DAT + manifest."""
    corpus = sorted(corpus, key=lambda r: (ctx.order[r['target_id']], r['variant'], r['editorial_version'], r['status']))
    pairs = validate_corpus(corpus, ctx)
    allowed = set(ctx.ncfg['export_review_statuses'])
    fresh = {s['explanation_id']: s['state'] for s in stale_report(corpus, ctx) if 'explanation_id' in s}
    refs = _reference_counts(ctx)
    rows = [r for r in corpus if r['status'] == 'ACTIVE' and r['review_status'] in allowed]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    head = '#LEXMACHINA|ENTENDA_PAYLOAD|2\n#BLOCO: @ID / T|K|V|R|F|H|D|C|B|N|W / #SECOES / @END\n'.encode('utf-8')
    offset, blobs, lookup, per = len(head), [], [], []
    for r in sorted(rows, key=lambda r: r['target_id']):
        blob = render_payload(r, fresh.get(r['explanation_id'], 'UNKNOWN'), refs.get(r['target_id'], 0))
        if len(blob) > ctx.limits['max_payload_bytes']:
            raise EntendaError('ENTENDA_PAYLOAD_TOO_LARGE', f"{r['target_id']}: {len(blob)}")
        tail = f"{r['explanation_id']}|{display_validity(r)}|{fresh.get(r['explanation_id'], 'UNKNOWN')}|{r['review_status']}"
        lookup.append(f"{r['target_id']}|{offset}|{len(blob)}|{tail}|DIRECT")
        # explicit editorial coverage (covered_targets), never structural inheritance
        lookup += [f"{c}|{offset}|{len(blob)}|{tail}|COVERED_BY_BLOCK" for c in r['granularity'].get('covered_targets', [])]
        per.append(dict(target_id=r['target_id'], explanation_id=r['explanation_id'], role=r['granularity']['role'], payload_bytes=len(blob),
                        words=sum(len(words(r['content'][k])) for k in REQUIRED_TEXT) + len(words(r['content']['atencao'] or '')) +
                        sum(len(words(t['termo'] + ' ' + t['explicacao'])) for t in r['content']['palavras_dificeis']),
                        freshness=fresh.get(r['explanation_id']), reference_count=refs.get(r['target_id'], 0)))
        blobs.append(blob)
        offset += len(blob)
    (out / 'ENTENDA_PAYLOAD.DAT').write_bytes(head + b''.join(blobs))
    lookup.sort(key=lambda l: l.split('|', 1)[0])
    (out / 'ENTENDA_LOOKUP.IDX').write_bytes(('#LEXMACHINA|ENTENDA_LOOKUP|2\n#TARGET_ID|OFFSET|BYTES|EXPLANATION_ID|VALIDITY|FRESHNESS|REVIEW|RESOLUTION\n'
                                              + ''.join(l + '\n' for l in lookup)).encode('utf-8'))
    files = {p.name: dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)
             for p in (out / 'ENTENDA_LOOKUP.IDX', out / 'ENTENDA_PAYLOAD.DAT')}
    by_tid = {r['target_id']: r for r in corpus if r['status'] == 'ACTIVE'}
    warnings = [w for r in sorted(rows, key=lambda r: (ctx.order[r['target_id']], r['explanation_id'])) for w in lint(r, ctx, by_tid)]
    counts = {}
    for w in warnings:
        counts[w['code']] = counts.get(w['code'], 0) + 1
    manifest = dict(schema_version=2, contract_version=CONTRACT, norma_id=ctx.norma_id, usage_policy=USAGE_POLICY,
                    explanations=len(rows), lookup_rows=len(lookup), files=files, hierarchy_pairs=pairs, per_explanation=per,
                    warning_counts=dict(sorted(counts.items())), warnings=warnings)
    (out / 'ENTENDA_BUILD_MANIFEST.json').write_bytes((json.dumps(manifest, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    files['ENTENDA_BUILD_MANIFEST.json'] = dict(sha256=hashlib.sha256((out / 'ENTENDA_BUILD_MANIFEST.json').read_bytes()).hexdigest(),
                                                bytes=(out / 'ENTENDA_BUILD_MANIFEST.json').stat().st_size)
    return files


def parse_payload(blob):
    rec, section, sections, meta = {}, None, {}, {'C': [], 'B': []}
    for line in blob.decode('utf-8').splitlines():
        if line.startswith('@') and line != '@END':
            rec['explanation_id'] = line[1:]
        elif line.startswith('#'):
            section = line[1:]
            sections[section] = []
        elif section is None and '|' in line:
            k, v = line.split('|', 1)
            if k in ('C', 'B'):
                meta[k].append(v)
            else:
                meta[k] = v
        elif section and line != '@END':
            sections[section].append(line)
    rec.update(target_id=meta.get('T'), display_title=meta.get('D'), kind=meta.get('K'), validity=meta.get('V'), review=meta.get('R'), freshness=meta.get('F'),
               context_targets=meta['C'], covered_targets=meta['B'], display_targets_order=meta['X'].split(',') if meta.get('X') else [meta.get('T')] + meta['B'], reference_count=int(meta.get('N', 0)), sections={k: '\n'.join(v) for k, v in sections.items()})
    return rec


def lookup_idx(target_id, lookup_path, payload_path):
    """Firmware-style lookup: binary search in ENTENDA_LOOKUP.IDX, then read BYTES at OFFSET in ENTENDA_PAYLOAD.DAT."""
    rows = [l.split('|') for l in Path(lookup_path).read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
    lo, hi = 0, len(rows) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if rows[mid][0] == target_id:
            with open(payload_path, 'rb') as fh:
                fh.seek(int(rows[mid][1]))
                rec = parse_payload(fh.read(int(rows[mid][2])))
            rec['resolution_type'] = rows[mid][7] if len(rows[mid]) > 7 else 'DIRECT'
            rec['matched_target_id'], rec['anchor_target_id'] = target_id, rec['target_id']
            rec['display_targets'] = rec.pop('display_targets_order')
            return rec
        if rows[mid][0] < target_id:
            lo = mid + 1
        else:
            hi = mid - 1
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=('stamp', 'build', 'stale'))
    ap.add_argument('out_dir', nargs='?')
    ap.add_argument('--norm', required=True)
    ap.add_argument('--drafts')
    ap.add_argument('--config', default=str(HERE / 'entenda_config.json'))
    a = ap.parse_args()
    ctx = NormContext(a.norm, a.config)
    corpus_path = ctx.base / ctx.ncfg['corpus']
    if a.cmd == 'stamp':
        drafts = json.loads(Path(a.drafts).read_text(encoding='utf-8'))
        recs = stamp(drafts, ctx, load_corpus(corpus_path))
        validate_corpus(recs, ctx)
        write_corpus(recs, corpus_path, ctx)
        print(json.dumps(dict(corpus=str(corpus_path), explanations=len(recs)), ensure_ascii=False))
    elif a.cmd == 'build':
        print(json.dumps(build_entenda_index(ctx, load_corpus(corpus_path), a.out_dir), indent=1))
    else:
        print(json.dumps(stale_report(load_corpus(corpus_path), ctx), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
