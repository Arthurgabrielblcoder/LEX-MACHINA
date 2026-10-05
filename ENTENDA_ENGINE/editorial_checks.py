"""ENTENDA editorial checks for a production batch (host only; never rewrites content, never changes review_status).

Complements entenda_engine.validate_explanation (blocking contract) and entenda_engine.lint (warnings) with the editorial risk checks
of the batch missions:
  EXTRAPOLATION_NUMBER       a number in the body that is not in the official snapshot (nor a device reference like "art. 201, § 2º")
  EXAMPLE_NUMBER             same, inside EXEMPLO PRATICO (hypothetical figures are allowed, but reviewed)
  EXCEPTION_NOT_IN_TEXT      the body announces an exception ("exceto", "salvo", "ressalva") but the snapshot has no exception marker
  ABSOLUTE_CLAIM             absolute wording (entenda_engine.ABSOLUTE_RE)
  TRANSITION_IN_CORE         O QUE DIZ / O QUE SIGNIFICA mention transition rules or amendments (they belong to ATENCAO / external layer)
  DUPLICATION                two explanations of the batch share a sentence of 8+ words or a section similarity above the T1 limit
  FACT_INCONSISTENCY         batch fact rules (input file): a forbidden statement appears in the same sentence as a trigger
  TECHNICAL_TERM_UNDEFINED   a listed technical term is used in the body but is not in the explanation's PALAVRAS DIFICEIS
  LONG_SENTENCE              a sentence with more than 45 words
  MODALITY_SHIFT             the snapshot is permissive ("podera", "poderao", "facultad") but O QUE DIZ states an obligation
  LAW_DEPENDENCY_OMITTED     the snapshot depends on law ("na forma da lei", "lei complementar", "nos termos da lei") and the body never says so
Each finding must be RESOLVED in the input file (resolution text written by the editor) or the explanation is NOT ready for editorial review.
Usage: python editorial_checks.py <batch_dir>   (reads <batch_dir>/EDITORIAL_REVIEW_INPUT.json; writes EDITORIAL_CHECKS.json and the triage)
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entenda_engine as E  # noqa: E402

BODY = ('o_que_diz', 'o_que_significa', 'atencao')
NUM_RE = re.compile(r'(?<![\w§])(\d+(?:[.,]\d+)?)(?:\s*%)?')
REF_BEFORE_RE = re.compile(r'(?:art\.|arts\.|§|§§|inciso|incisos|nº|n\.º|EC|Emenda Constitucional nº|alínea|Lei|de)\s*[\w.,º\s-]{0,12}$', re.I)
EXCEPTION_BODY_RE = re.compile(r'\b(?:exceto|salvo|ressalva(?:s|da|do|das|dos)?|exce[çc][ãa]o|exce[çc][õo]es)\b', re.I)
EXCEPTION_TEXT_RE = re.compile(r'\b(?:exceto|salvo|ressalvad[oa]s?|ressalva|n[ãa]o se aplicando|vedad[oa]|somente|só|apenas|desde que)\b', re.I)
TRANSITION_RE = re.compile(r'\b(?:transi[çc][ãa]o|Emenda Constitucional|EC\s*\d|reforma da previd[êe]ncia)\b', re.I)
PERMISSIVE_RE = re.compile(r'\b(?:poder[áa]|poder[ãa]o|facultad[oa]|faculta)\b', re.I)
OBLIGATION_RE = re.compile(r'\b(?:é obrigat[óo]ri[oa]|obriga(?:m|tório)?|dever[áa]o?|devem|deve)\b', re.I)
LAW_TEXT_RE = re.compile(r'\b(?:na forma da lei|nos termos da lei|lei complementar|lei espec[íi]fica|definidos em lei|previstos em lei|em lei|da lei|de lei|a lei|lei do respectivo)\b', re.I)
LAW_BODY_RE = re.compile(r'\blei(?:s)?\b', re.I)


def _sentences(text):
    return [s for s in re.split(r'(?<=[.;:!?])\s+|\n', text) if s.strip()]


def _numbers_outside_snapshot(text, snapshot):
    snap = snapshot.replace('.', '')
    out = []
    for m in NUM_RE.finditer(text):
        n = m.group(1).replace('.', '')
        if n in snap or REF_BEFORE_RE.search(text[max(0, m.start() - 30):m.start()]):
            continue
        out.append(m.group(0).strip())
    return out


def check_record(r, rules, terms):
    c, snap = r['content'], r['source']['source_text_snapshot']
    body = {k: c[k] for k in BODY if c.get(k)}
    found = []

    def add(code, section, detail):
        found.append(dict(code=code, section=section, detail=detail))

    for k, t in body.items():
        for n in _numbers_outside_snapshot(t, snap):
            add('EXTRAPOLATION_NUMBER', k, n)
        for m in E.ABSOLUTE_RE.finditer(t):
            add('ABSOLUTE_CLAIM', k, m.group(0))
        for s in _sentences(t):
            if len(E.words(s)) > 45:
                add('LONG_SENTENCE', k, s[:80])
    for n in _numbers_outside_snapshot(c['exemplo_pratico'], snap):
        add('EXAMPLE_NUMBER', 'exemplo_pratico', n)
    core = c['o_que_diz'] + ' ' + c['o_que_significa']
    if EXCEPTION_BODY_RE.search(core) and not EXCEPTION_TEXT_RE.search(snap):
        add('EXCEPTION_NOT_IN_TEXT', 'o_que_diz/o_que_significa', EXCEPTION_BODY_RE.search(core).group(0))
    for k in ('o_que_diz', 'o_que_significa'):
        m = TRANSITION_RE.search(c[k])
        if m:
            add('TRANSITION_IN_CORE', k, m.group(0))
    if PERMISSIVE_RE.search(snap) and not OBLIGATION_RE.search(snap) and OBLIGATION_RE.search(c['o_que_diz']):
        add('MODALITY_SHIFT', 'o_que_diz', OBLIGATION_RE.search(c['o_que_diz']).group(0))
    if LAW_TEXT_RE.search(snap) and not LAW_BODY_RE.search(' '.join(body.values())):
        add('LAW_DEPENDENCY_OMITTED', 'body', LAW_TEXT_RE.search(snap).group(0))
    glossary = ' '.join(t['termo'].lower() for t in c['palavras_dificeis'])
    text = ' '.join(body.values()).lower()
    for term in terms:
        if re.search(r'\b' + re.escape(term.lower()), text) and term.lower()[:6] not in glossary:
            add('TECHNICAL_TERM_UNDEFINED', 'body', term)
    full = ' '.join([c[k] for k in E.REQUIRED_TEXT] + ([c['atencao']] if c['atencao'] else []))
    for rule in rules:
        if rule.get('targets') and r['target_id'] not in rule['targets']:
            continue
        for s in _sentences(full):
            if re.search(rule['if_contains'], s, re.I) and re.search(rule['must_not_contain'], s, re.I):
                add('FACT_INCONSISTENCY', rule['id'], s[:120])
    return found


def duplication(records, limit):
    out = []
    sent = {r['target_id']: {k: E._sentences(r['content'][k]) for k in E.REQUIRED_TEXT} for r in records}
    for i, a in enumerate(records):
        for b in records[i + 1:]:
            for k in E.REQUIRED_TEXT:
                shared = sent[a['target_id']][k] & sent[b['target_id']][k]
                sim = E.similarity(a['content'][k], b['content'][k])
                if shared or sim > limit:
                    out.append(dict(a=a['target_id'], b=b['target_id'], section=k, similarity=sim, shared_sentences=sorted(shared)[:2]))
    return out


def run(batch_dir):
    bd = Path(batch_dir)
    spec = json.loads((bd / 'BATCH_SPEC.json').read_text(encoding='utf-8'))
    inp = json.loads((bd / 'EDITORIAL_REVIEW_INPUT.json').read_text(encoding='utf-8'))
    ctx = E.NormContext(spec['norma_id'])
    new = [r for r in E.load_corpus(bd / spec['batch_corpus']) if r['status'] == 'ACTIVE']
    by = {r['target_id']: r for r in new}
    if sorted(inp['risk']) != sorted(by):
        raise SystemExit(f"RISK_CLASSIFICATION_INCOMPLETE {sorted(set(by) ^ set(inp['risk']))}")
    dup = duplication(new, ctx.limits['max_section_similarity'])
    resolutions = inp.get('resolutions', {})
    rows, unresolved_total = [], 0
    for r in new:
        tid = r['target_id']
        f = check_record(r, inp.get('fact_rules', []), inp.get('technical_terms', []))
        f += [dict(code='DUPLICATION', section=d['section'], detail=f"{d['a']} x {d['b']} sim={d['similarity']}") for d in dup if tid in (d['a'], d['b'])]
        res = resolutions.get(tid, {})
        for x in f:
            key = f"{x['code']}:{x['detail']}"
            x['resolution'] = res.get(key) or res.get(x['code'])
        unresolved = [x for x in f if not x['resolution']]
        unresolved_total += len(unresolved)
        risk = inp['risk'][tid]
        rows.append(dict(target_id=tid, explanation_id=r['explanation_id'], title=E.display_title(r), role=r['granularity']['role'],
                         risk=risk['level'], risk_reasons=risk['reasons'], review_status=r['review_status'],
                         editorial_state='READY_FOR_EDITORIAL_REVIEW' if not unresolved else 'EDITORIAL_FIXES_REQUIRED',
                         findings=f, unresolved=len(unresolved)))
    counts = {k: sum(1 for x in rows if x['risk'] == k) for k in ('LOW', 'MEDIUM', 'HIGH')}
    codes = {}
    for x in rows:
        for f in x['findings']:
            codes[f['code']] = codes.get(f['code'], 0) + 1
    doc = dict(schema_version=1, batch_id=spec['batch_id'], as_of=spec['as_of_date'],
               policy='checagens editoriais (nao reescrevem conteudo); READY_FOR_EDITORIAL_REVIEW != HUMAN_APPROVED_T1; review_status inalterado',
               explanations=len(rows), risk_counts=counts, finding_counts=dict(sorted(codes.items())), unresolved_findings=unresolved_total,
               ready_for_editorial_review=sum(1 for x in rows if x['editorial_state'] == 'READY_FOR_EDITORIAL_REVIEW'),
               human_approved_t1=sum(1 for x in rows if x['review_status'] == 'HUMAN_APPROVED_T1'), duplication_pairs=dup, rows=rows)
    (bd / 'EDITORIAL_CHECKS.json').write_bytes((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    (bd / inp.get('triage_sheet', 'REVIEW_RISK_TRIAGE.md')).write_bytes(triage_md(doc).encode('utf-8'))
    return doc


def triage_md(doc):
    L = [f"# TRIAGEM DE RISCO EDITORIAL — {doc['batch_id']}", '',
         f"Data de referência: {doc['as_of']}. Nenhum texto foi alterado por esta triagem e nenhuma explicação foi aprovada: todas seguem "
         '`PENDING_HUMAN_REVIEW`. `READY_FOR_EDITORIAL_REVIEW` significa apenas que as checagens automáticas foram resolvidas pelo editor e '
         'que a explicação pode ir para a revisão humana.', '',
         f"- Explicações: {doc['explanations']} · risco LOW {doc['risk_counts']['LOW']} · MEDIUM {doc['risk_counts']['MEDIUM']} · "
         f"HIGH {doc['risk_counts']['HIGH']}",
         f"- Prontas para revisão editorial: {doc['ready_for_editorial_review']} · aprovadas (HUMAN_APPROVED_T1): {doc['human_approved_t1']}",
         f"- Achados: {', '.join(f'{k} {v}' for k, v in doc['finding_counts'].items()) or '—'} · não resolvidos: {doc['unresolved_findings']}", '']
    for lvl in ('HIGH', 'MEDIUM', 'LOW'):
        L += [f'## Risco {lvl}', '']
        for x in [r for r in doc['rows'] if r['risk'] == lvl]:
            L += [f"### {x['title']}", '', f"- `{x['target_id']}` · {x['role']} · {x['editorial_state']} · {x['review_status']}",
                  f"- Motivos do risco: {'; '.join(x['risk_reasons'])}"]
            for f in x['findings']:
                L.append(f"- {f['code']} ({f['section']}: {f['detail'][:70]}) → {f['resolution'] or 'NÃO RESOLVIDO'}")
            L.append('')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    d = run(sys.argv[1])
    print(json.dumps({k: v for k, v in d.items() if k not in ('rows', 'duplication_pairs')}, ensure_ascii=False, indent=1))
