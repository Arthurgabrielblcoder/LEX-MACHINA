"""CONTEXT_CITATION_GUARD corpus audit (host only; read-only).

Replays every physical line of the 72 device texts through the CONTEXTO parser port (context_parser_port.apply_line = the firmware
aplicarLinhaContextoJuridico) twice: before the guard (CITATION_GUARD=False) and after it (True). The state is carried line to line
exactly as the reader does, so a false trigger is also counted by the lines it would mislabel until the next real heading.

Usage: python context_citation_audit.py [out.json]
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
sys.path.insert(0, str(HERE))
import article_index_corpus as C  # noqa: E402
import build_article_search_index as AI  # noqa: E402

sys.path.insert(0, str(DI.parent / 'LEGAL_TARGET_ID'))
import structure_parser as SP  # noqa: E402
import context_parser_port as P  # noqa: E402

CORPUS = DI / 'backups/sd_20260929T163407Z/data'            # host copy of the card (approved full-corpus deploy)
OVERRIDES = {                                                # what the device actually opens for these norms
    'MARIA2006': DI / 'staging_maria2006_source_repair/SD/15-LEI MARIA DA PENHA/Lei Maria da Penha.txt',
    'CF88': DI / 'staging_sd_v1_batch04_run3_candidate/SD/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt',
}
TERMINAL = ('.', ';', ':', ')', '!', '?')
# Oracles (approved, read-only): the 72 ARTICLE_SEARCH indexes (full-corpus + MARIA2006 repair) and the CF88 TEXT_MAP (structural
# records of the runtime text that ACTIVE_TARGET resolves through).
INDEXES = DI / 'staging_maria2006_source_repair/_host/full_corpus/SD/99_LEX_V1/10_TARGETS'
CF_TEXT_MAP = DI / 'staging_sd_v1_batch04_run3_candidate/SD/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX'


def documents():
    out = []
    for d in C.discover(CORPUS):
        p = Path(OVERRIDES.get(d['norma'], d['path'] or ''))
        if p.is_file():
            out.append((d['norma'], p))
    return out


def classify(line):
    """Parser branch that reads the line (same order as aplicarLinhaContextoJuridico): ART / PAR / UNICO / ALI / INC."""
    s = line.decode('utf-8', 'replace').lstrip(' 	 ')
    low = s.lower()
    if low.startswith('art'):
        return 'ART'
    if s.startswith('§'):
        return 'PAR'
    if low.startswith(('paragrafo', 'parágrafo')):
        return 'UNICO'
    if len(s) > 1 and 'a' <= s[0] <= 'z' and s[1] == ')':
        return 'ALI'
    return 'INC'


def replay(raw, guard):
    P.CITATION_GUARD = guard
    try:
        c = dict(artigo='', paragrafo='', inciso='', alinea='')
        states, applied = [], []
        for line in raw.split(b'\n'):
            prev = dict(c)
            ok = P.apply_line(c, line.rstrip(b'\r')[:511])
            applied.append((ok, prev, dict(c)))
            states.append(dict(c))
        return states, applied
    finally:
        P.CITATION_GUARD = True


def oracle_offsets(norma, raw):
    """Line-start offsets the approved structure registers for this text: indexed article headings (+ CF88 TEXT_MAP records)."""
    out = set()
    idx = INDEXES / f'{norma}_ARTICLE_SEARCH.IDX'
    if idx.is_file():
        out |= {r[3] for r in AI.ArticleIndex(idx.read_bytes(), raw).recs}
    if norma == 'CF88' and CF_TEXT_MAP.is_file():
        out |= {int(l.split('|')[0]) for l in CF_TEXT_MAP.read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')}
    return out


def audit_text(norma, raw):
    lines = raw.split(b'\n')
    oracle = oracle_offsets(norma, raw)
    offsets, pos = [], 0
    for line in lines:
        offsets.append(pos)
        pos += len(line) + 1
    s0, a0 = replay(raw, False)
    s1, a1 = replay(raw, True)
    eliminated, added, prev_text = [], [], ''
    counts = collections.Counter()
    for n, line in enumerate(lines):
        text = line.decode('utf-8', 'replace').strip()
        if a0[n][0] and not a1[n][0]:
            kind = classify(line)
            counts[kind] += 1
            eliminated.append(dict(norma=norma, line=n + 1, offset=offsets[n], kind=kind, text=text[:90],
                                   oracle_structural=offsets[n] in oracle, previous_tail=prev_text[-40:],
                                   previous_open=bool(prev_text) and not prev_text.endswith(TERMINAL)))
        elif a1[n][0] and not a0[n][0]:
            added.append(dict(norma=norma, line=n + 1, text=text[:90]))
        if text:
            prev_text = text
    structural = collections.Counter()
    residual, prev_text = [], ''
    for n in range(len(lines)):
        text = lines[n].decode('utf-8', 'replace').strip()
        if a1[n][0]:
            kind = classify(lines[n])
            structural[kind] += 1
            # Still accepted but citation-shaped (never fixed here: reported as AMBIGUOUS): a lower-case 'art.' line, or a heading
            # line whose previous line leaves the sentence open with a citation tail word (structure_parser.CITATION_TAIL).
            tail = prev_text.rstrip(' ,').rsplit(' ', 1)[-1]
            if offsets[n] not in oracle and ((kind == 'ART' and text[:1] == 'a') or
                                              (kind in ('ART', 'PAR', 'UNICO') and tail in SP.CITATION_TAIL)):
                residual.append(dict(norma=norma, line=n + 1, kind=kind, text=text[:90], previous_tail=prev_text[-40:]))
        if text:
            prev_text = text
    relabeled = sum(1 for x, y in zip(s0, s1) if x != y)
    oracle_lost = [n for n in range(len(lines)) if offsets[n] in oracle and a0[n][0] and not a1[n][0]]
    return dict(eliminated=eliminated, added=added, residual=residual, oracle_records=len(oracle), oracle_lost=len(oracle_lost), eliminated_by_kind=dict(counts), structural_after=dict(structural),
                lines=len(lines), relabeled_lines=relabeled)


def run():
    norms, eliminated, added, residual = {}, [], [], []
    total = collections.Counter()
    preserved = collections.Counter()
    relabeled = 0
    oracle_records = oracle_lost = 0
    for norma, path in documents():
        r = audit_text(norma, path.read_bytes())
        norms[norma] = dict(lines=r['lines'], eliminated=r['eliminated_by_kind'], structural_after=r['structural_after'],
                            relabeled_lines=r['relabeled_lines'])
        eliminated += r['eliminated']
        added += r['added']
        residual += r['residual']
        total.update(r['eliminated_by_kind'])
        preserved.update(r['structural_after'])
        relabeled += r['relabeled_lines']
        oracle_records += r['oracle_records']
        oracle_lost += r['oracle_lost']
    return dict(norms=len(norms), eliminated_total=sum(total.values()), eliminated_by_kind=dict(sorted(total.items())),
                structural_preserved_by_kind=dict(sorted(preserved.items())), added_total=len(added),
                eliminated_previous_line_closed=[e for e in eliminated if not e['previous_open']],
                oracle_records=oracle_records, oracle_structural_lost=oracle_lost,
                residual_ambiguous_total=len(residual),
                residual_ambiguous_by_kind=dict(collections.Counter(x['kind'] for x in residual)),
                relabeled_lines=relabeled, per_norm=norms, residual=residual, eliminated=eliminated, added=added)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    result = run()
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('per_norm', 'eliminated', 'added', 'residual')}, ensure_ascii=False, indent=1))
