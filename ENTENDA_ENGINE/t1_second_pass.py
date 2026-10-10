"""Second pass of an ENTENDA macro batch: risk compression with versioned evidence (generic; macro layer only).

The shared triage modules pinned by the Batch06 manifest (t1_risk, t1_validator_v3, t1_batch_packets, ...) are not edited. This module
refines their output, inside the macro builder, with inputs that live in the batch directory:

  <P>_TRANSITION_EVIDENCE.json  per target with TRANSITION_OR_TEMPORAL: origin, amendments, ADCT articles, temporal marker, rule in force
                                at the reference date, effect in that year, quotes. Every quote is checked against the versioned source
                                (sha256 + text, whitespace folded); nothing temporal comes from memory.
                                RESOLVED_BY_VERSIONED_SOURCE -> the TRANSITION rule stops being HIGH (MEDIUM, TRANSITION_RESOLVED_BY_VERSIONED_SOURCE);
                                ACTIVE_TRANSITION_HIGH       -> HIGH kept, only with an explicit criterion of HIGH_CRITERIA.
  SECOND_PASS_INPUT.json        judicial_review: {target: {classification, reason}} for explanations whose scope carries a "Vide ADI/ADC/..."
                                annotation. CONTEXT_ONLY -> MEDIUM (JUDICIAL_REVIEW_CONTEXT_ONLY); REQUIRED_FOR_CORRECTNESS -> HIGH
                                (JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS); missing classification -> REQUIRED (fail closed).
                                quick_review: [{target_id, section, excerpt, reason, proposal}] -> C (excerpt must occur in the section).
Deterministic rules applied to every record:
  CONTROVERSY_TERM_FROM_LEI_SECA  the interpretive-controversy marker is a word of the Lei Seca itself (e.g. "controversia atual" of art. 103-A,
                                  "outras controversias" of art. 114): not a debate marker, the INTERPRETIVE_CONTROVERSY rule is dropped.
  PARENT_CHILD_LEGAL_CONSISTENCY  an overview saying that a device "tem explicacao propria" must point to a device that has one (C otherwise).
"""
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

RESOLVED, ACTIVE = 'RESOLVED_BY_VERSIONED_SOURCE', 'ACTIVE_TRANSITION_HIGH'
HIGH_CRITERIA = {
    'DATA_DE_IMPLANTACAO_AINDA_MATERIAL': 'data de implantacao ainda material na data de referencia',
    'REGIMES_COEXISTENTES': 'regimes coexistentes',
    'VIGENCIA_PARCIAL': 'vigencia parcial',
    'TRANSICAO_DEPENDENTE_DE_LEI_EXTERNA': 'transicao dependente de lei (complementar) externa',
    'TEXTO_VIGENTE_INSUFICIENTE': 'texto vigente insuficiente para o marco temporal',
    'CONTROVERSIA_JURISPRUDENCIAL_TEMPORAL': 'controversia jurisprudencial temporal',
    'EMENDA_RECENTE_COM_TRANSICAO_PROPRIA': 'emenda recente com regra de transicao propria fora das fontes versionadas',
}
JR_CLASSES = ('CONTEXT_ONLY', 'REQUIRED_FOR_CORRECTNESS')
BODY = ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao')
CONTROVERSY_RE = re.compile(r'(objeto de debate|controv[ée]rs\w*|gera(?:m)? d[úu]vidas|n[ãa]o est[áa] pacificad\w*|ainda (?:se )?discute)', re.I)
ID_PREFIX_RE = re.compile(r'^[A-Z0-9]+:[^\t\n]*\t', re.M)
OWN_RE = re.compile(r'explica[çc][ãa]o pr[óo]pria', re.I)
ROMAN = r'[IVXLC]+(?:-[A-Z])?'
NUM = r'\d+º?(?:-[A-Z])?'


class SecondPassError(RuntimeError):
    pass


def fold(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s)).strip()


def _load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


# ---------------------------------------------------------------- transition evidence

def load_transition_evidence(path, root):
    """{target_id: entry}; fail closed on a source whose sha256 changed, a quote absent from its source or an inconsistent decision."""
    if not Path(path).is_file():
        return {}
    doc = _load(path)
    texts = {}
    for key, s in doc['sources'].items():
        data = (Path(root) / s['path']).read_bytes()
        if hashlib.sha256(data).hexdigest() != s['sha256']:
            raise SecondPassError(f"TRANSITION_SOURCE_SHA_MISMATCH {key}: {s['path']}")
        texts[key] = fold(data.decode('utf-8'))
    out = {}
    for e in doc['targets']:
        tid = e['target_id']
        if tid in out:
            raise SecondPassError(f'TRANSITION_DUPLICATE {tid}')
        if e['resolution'] not in (RESOLVED, ACTIVE):
            raise SecondPassError(f"TRANSITION_RESOLUTION_INVALID {tid}: {e['resolution']}")
        if e['resolution'] == ACTIVE and (not e['high_criteria'] or set(e['high_criteria']) - set(HIGH_CRITERIA)):
            raise SecondPassError(f'TRANSITION_HIGH_WITHOUT_CRITERION {tid}')
        if e['resolution'] == RESOLVED and (e['high_criteria'] or e.get('missing_external_evidence')):
            raise SecondPassError(f'TRANSITION_RESOLVED_WITH_OPEN_ITEMS {tid}')
        if e['resolution'] == RESOLVED and not any(q['source'] != 'CF88_CANONICAL' for q in e['quotes']):
            raise SecondPassError(f'TRANSITION_RESOLVED_WITHOUT_TEMPORAL_SOURCE {tid}')
        if not e['quotes']:
            raise SecondPassError(f'TRANSITION_WITHOUT_QUOTE {tid}')
        for q in e['quotes']:
            if q['source'] not in texts or fold(q['quote']) not in texts[q['source']]:
                raise SecondPassError(f"TRANSITION_QUOTE_NOT_IN_SOURCE {tid}: {q['quote'][:60]}")
        out[tid] = e
    return out


# ---------------------------------------------------------------- input

def load_input(path):
    if not Path(path).is_file():
        return dict(judicial_review={}, quick_review=[])
    doc = _load(path)
    for t, v in doc.get('judicial_review', {}).items():
        if v.get('classification') not in JR_CLASSES or not v.get('reason'):
            raise SecondPassError(f'JUDICIAL_REVIEW_CLASSIFICATION_INVALID {t}')
    doc.setdefault('judicial_review', {})
    doc.setdefault('quick_review', [])
    return doc


def quick_findings(rec, inp):
    out = []
    for q in inp['quick_review']:
        if q['target_id'] != rec['target_id']:
            continue
        sec = q['section']
        text = '\n'.join(rec.get('external_layer_notes') or []) if sec == 'external_layer_notes' else (rec['content'].get(sec) or '')
        if q['excerpt'] not in text:
            raise SecondPassError(f"QUICK_REVIEW_EXCERPT_ABSENT {rec['target_id']} {sec}: {q['excerpt'][:60]}")
        out.append(_finding('SECOND_PASS_QUICK_REVIEW', sec, q['excerpt'], f"{q['reason']} || proposta: {q['proposal']}"))
    return out


def _finding(code, section, match, detail):
    return dict(code=code, severity='REVIEW_REQUIRED', route='QUICK', section=section, match=match, sentence=match, detail=detail)


# ---------------------------------------------------------------- parent/child

def _labels(sentence, art):
    """Devices named in a sentence about "explicacao propria" -> target ids of the article (remissions "121, § 2º" go to that article)."""
    out = []
    s = sentence
    for m in re.finditer(r'(\d+(?:-[A-Z])?),\s*§\s*(' + NUM + ')', s):
        out.append(f"CF88:ART.{m.group(1)}:PAR.{m.group(2).replace('º', '')}")
    s = re.sub(r'\d+(?:-[A-Z])?,\s*§\s*' + NUM, ' ', s)
    if re.search(r'par[áa]grafo [úu]nico', s, re.I):
        out.append(f'{art}:PAR.UNICO')
    for m in re.finditer(r'\bincisos?\s+((?:' + ROMAN + r')(?:\s*(?:,|e|a)\s*(?:' + ROMAN + r'))*)', s):
        out += [f'{art}:INC.{x}' for x in _expand(m.group(1), roman=True)]
    for m in re.finditer(r'§§?\s*((?:' + NUM + r')(?:\s*(?:,|e|a)\s*(?:' + NUM + r'))*)', s):
        out += [f"{art}:PAR.{x}" for x in _expand(m.group(1).replace('º', ''), roman=False)]
    return out


ROMAN_VAL = dict(I=1, V=5, X=10, L=50, C=100)


def _rv(r):
    v = 0
    for a, b in zip(r, r[1:] + ' '):
        v += -ROMAN_VAL[a] if b != ' ' and ROMAN_VAL.get(b, 0) > ROMAN_VAL[a] else ROMAN_VAL[a]
    return v


def _rn(n):
    out = ''
    for v, s in ((100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')):
        while n >= v:
            out, n = out + s, n - v
    return out


def _expand(spec, roman):
    parts = [p.strip() for p in re.split(r'\s*(?:,|\be\b)\s*', spec) if p.strip()]
    out = []
    for p in parts:
        m = re.match(r'(\S+)\s+a\s+(\S+)$', p)
        if m and '-' not in p:
            lo, hi = m.groups()
            if roman:
                out += [_rn(i) for i in range(_rv(lo), _rv(hi) + 1)]
            else:
                out += [str(i) for i in range(int(lo), int(hi) + 1)]
        else:
            out.append(p)
    return out


def parent_child_findings(rec, ctx, owned):
    """owned: devices covered by some explanation of their own (non-overview records of the batch, reused or prior approved ones)."""
    if rec['granularity']['role'] != 'OVERVIEW':
        return []
    art = rec['target_id']
    out = []
    for sec in BODY:
        for sent in re.split(r'(?<=[.])\s+', rec['content'].get(sec) or ''):
            if not OWN_RE.search(sent):
                continue
            for t in _labels(sent, art):
                if t not in ctx.targets:
                    out.append(_finding('PARENT_CHILD_LEGAL_CONSISTENCY', sec, sent, f'{t}: dispositivo inexistente no indice'))
                elif t not in owned:
                    out.append(_finding('PARENT_CHILD_LEGAL_CONSISTENCY', sec, sent,
                                        f"{t.split(':', 1)[1]} nao tem explicacao propria: a visao geral afirma o contrario"))
    return out


# ---------------------------------------------------------------- risk refinement

def controversy_from_lei_seca(rec):
    snap = ID_PREFIX_RE.sub('', rec['source']['source_text_snapshot']).lower()
    words = [m.group(0).lower() for k in BODY for m in CONTROVERSY_RE.finditer(rec['content'].get(k) or '')]
    words += [m.group(0).lower() for n in rec.get('external_layer_notes') or [] for m in CONTROVERSY_RE.finditer(n)]
    return bool(words) and all(w in snap for w in words)


def _split(a):
    """(high [(rule, reason)], medium [(rule, reason)]) from a t1_risk.assess result."""
    pair = lambda s: (s.split(':', 1)[0], s)  # noqa: E731
    if a['level'] == 'HIGH':
        return [pair(s) for s in a['reasons']], [pair(s) for s in a['secondary']]
    if a['level'] == 'MEDIUM':
        return [], [pair(s) for s in a['reasons']]
    return [], []


def _join(a, high, medium, juris=None):
    b = dict(a)
    b['level'] = 'HIGH' if high else 'MEDIUM' if medium else 'LOW'
    reasons = high or medium
    b['rules'] = [r for r, _ in reasons]
    b['reasons'] = [s for _, s in reasons]
    b['secondary'] = [s for _, s in medium] if high else []
    if juris:
        b['jurisprudence'] = juris
    return b


def refine(a, rec, judicial_hits, transition, inp):
    """judicial_hits: "Vide ADI..." annotations in the record's scope (macro layer). Returns the refined assessment."""
    tid = rec['target_id']
    high, medium = _split(a)
    if any(r == 'INTERPRETIVE_CONTROVERSY' for r, _ in high) and controversy_from_lei_seca(rec):
        high = [h for h in high if h[0] != 'INTERPRETIVE_CONTROVERSY']
        medium.append(('CONTROVERSY_TERM_FROM_LEI_SECA', 'CONTROVERSY_TERM_FROM_LEI_SECA: o termo e da propria Lei Seca, nao marca debate'))
    if any(r == 'TRANSITION_OR_TEMPORAL' for r, _ in high):
        e = transition.get(tid)
        if e and e['resolution'] == RESOLVED:
            high = [h for h in high if h[0] != 'TRANSITION_OR_TEMPORAL']
            medium.append(('TRANSITION_RESOLVED_BY_VERSIONED_SOURCE',
                           f"TRANSITION_RESOLVED_BY_VERSIONED_SOURCE: {', '.join(e['adct_articles']) or 'texto vigente'} — {e['temporal_marker']}"))
        elif e:
            high = [h for h in high if h[0] != 'TRANSITION_OR_TEMPORAL']
    e = transition.get(tid)
    if e and e['resolution'] == ACTIVE:   # the evidence decides, not the wording of the draft
        high.append(('TRANSITION_OR_TEMPORAL', f"TRANSITION_OR_TEMPORAL: {' + '.join(e['high_criteria'])} — {e['temporal_marker']}"))
    if judicial_hits:
        base = '; '.join(judicial_hits[:3]) + (f' (+{len(judicial_hits) - 3})' if len(judicial_hits) > 3 else '')
        c = inp['judicial_review'].get(tid)
        if c and c['classification'] == 'CONTEXT_ONLY':
            medium.append(('JUDICIAL_REVIEW_CONTEXT_ONLY', f"JUDICIAL_REVIEW_CONTEXT_ONLY: {base} — {c['reason']}"))
        else:
            why = c['reason'] if c else 'classificacao ausente (fail closed)'
            high.append(('JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS', f'JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS: {base} — {why}'))
    return _join(a, high, medium)


# ---------------------------------------------------------------- packets (second pass format)

JURIS_MARK = re.compile(r'(n[ãa]o deve(?:m)? ser deduzid\w*|n[ãa]o se deve concluir apenas|delimitad[oa]s? pela interpreta[çc][ãa]o|'
                        r'(?:é|são|foi|foram) definid[oa]s? pela interpreta[çc][ãa]o|leitura isolada)', re.I)
DECISIONS = ('APROVAR', 'AJUSTAR', 'VERIFICAR EXTERNAMENTE')


def _cut(s, n):
    s = ' '.join((s or '').split())
    return s if len(s) <= n else s[:n - 1].rstrip() + '…'


def _sentences(text, rx):
    return [s for s in re.split(r'(?<=[.;])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])', text or '') if rx.search(s)]


def _snapshot_lines(r):
    return [ln.split('\t', 1) for ln in r['source']['source_text_snapshot'].split('\n') if '\t' in ln]


def d_item(x, r, c, juris_recs):
    """Everything the human needs to decide one D item."""
    tid = x['target_id']
    body = {k: r['content'].get(k) or '' for k in BODY}
    hits = c.judicial_hits(r)
    ann_devices = {h.split(':', 1)[0] for h in hits}
    ev = c.transition.get(tid)
    depend, local, missing = [], [], []
    rules = set(x['legal_rules'])
    if 'JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS' in rules:
        depend += [f'[{k}] {s}' for k in BODY for s in _sentences(body[k], JURIS_MARK)]
    if 'INTERPRETIVE_CONTROVERSY' in rules:
        depend += [f'[{k}] {s}' for k in BODY for s in _sentences(body[k], CONTROVERSY_RE)]
    if 'JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS' in rules:
        cl = c.second['judicial_review'].get(tid, {})
        depend.append(f"[escopo] {cl.get('reason', 'classificacao ausente (fail closed)')}")
        local += [f'anotação de vigência da fonte canônica: {h}' for h in hits]
        ids = sorted({re.sub(r'^.*?Vide\s+', '', h) for h in hits})
        missing.append(f"decisão do controle de constitucionalidade ({', '.join(ids)}): PENDING_EXTERNAL_INGESTION (nada preenchido de memória)")
    if 'TRANSITION_OR_TEMPORAL' in rules and ev:
        depend.append(f"[transição] regra em 2026: {ev['current_rule_2026']}")
        depend += [f'[{k}] {s}' for k in BODY for s in _sentences(body[k], re.compile(r'transi[çc][ãa]o', re.I))]
        local.append(f"marco temporal: {ev['temporal_marker']} · efeito em 2026: {ev['produces_effect_in_2026']} · critérios HIGH: {', '.join(ev['high_criteria'])}")
        local += [f"{q['source']}: \"{_cut(q['quote'], 220)}\"" for q in ev['quotes']]
        if ev.get('missing_external_evidence'):
            missing.append(ev['missing_external_evidence'])
    for t in [tid] + list(r['granularity'].get('covered_targets', [])):
        if c.vigency.get(t) and not any(JUDICIAL_REVIEW_RE_LOCAL.search(a) for a in c.vigency[t]):
            local.append(f"vigência ({t.split(':', 1)[1]}): {'; '.join(c.vigency[t])}")
    recs = [j for j in juris_recs if j['target_id'] == tid]
    missing += [f"jurisprudência {j['desired_reference']}: {j['status']} — {_cut(j['purpose'], 160)}" for j in recs]
    if rules & {'JURISPRUDENCE_REQUIRED_FOR_CORRECTNESS', 'INTERPRETIVE_CONTROVERSY'} and not recs:
        missing.append('jurisprudência necessária para a correção: sem registro versionado no projeto (PENDING_EXTERNAL_INGESTION; nada preenchido de memória)')
    rev = [d for d in x['detectors'] if d['severity'] == 'REVIEW_REQUIRED']
    missing += [f"{d['code']}: \"{_cut(d['match'], 80)}\" (sem proveniência local)" for d in rev if d['code'].startswith('EXTERNAL_')]
    if missing:
        decision, why = 'VERIFICAR EXTERNAMENTE', 'há evidência externa faltante; a decisão depende dela'
    elif rev:
        decision, why = 'AJUSTAR', 'há alerta de revisão no texto'
    else:
        decision, why = 'APROVAR', 'evidência local completa; conferir a afirmação dependente contra a Lei Seca e a evidência acima'
    snap = _snapshot_lines(r)
    if r['granularity']['role'] == 'OVERVIEW':
        keep = {f'{tid}:CAPUT'} | {f"CF88:{d}" for d in ann_devices} | {tid}
        law = [(t, s) for t, s in snap if t in keep]
        law_note = f'(visão geral: caput e dispositivos ligados ao motivo HIGH; {len(snap)} dispositivos no total, todos no runtime)'
    else:
        law, law_note = snap, ''
    return dict(depend=depend or ['(o motivo HIGH não aponta frase isolada; ver motivo exato)'], local=local or ['—'],
                missing=missing or ['nenhuma'], decision=decision, decision_why=why, law=law, law_note=law_note)


JUDICIAL_REVIEW_RE_LOCAL = re.compile(r'\bVide\s+(ADIN|ADI|ADC|ADPF|ADO)\b', re.I)


def full_d(doc, c, title, juris_recs):
    xs = sorted([x for x in doc['rows'] if x['queue'] == 'D_FULL_HUMAN_REVIEW'], key=lambda x: (x['sub_block'], c.ctx.order[x['target_id']]))
    n = len(doc['rows'])
    L = [f'# {title} — REVISÃO HUMANA COMPLETA (fila D, segundo passe)', '',
         f"Lote `{c.spec['batch_id']}` · {len(xs)} de {n} itens ({100 * len(xs) / n:.1f}%) · nenhum aprovado. Só itens que exigem raciocínio jurídico "
         'profundo: LEGAL_RISK HIGH depois da compressão de risco com evidência versionada. Para cada item: Lei Seca relevante, T1 completo, motivo '
         'exato, afirmação que depende da revisão, evidência local, evidência externa faltante e decisão sugerida.', '', '## Índice', '']
    items = [(x, c.records[x['target_id']], d_item(x, c.records[x['target_id']], c, juris_recs)) for x in xs]
    L += [f"{i}. [{x['sub_block']}] `{x['target_id']}` — {x['title']} · {', '.join(x['legal_rules'])} · sugestão: {it['decision']}"
          for i, (x, r, it) in enumerate(items, 1)]
    L += ['']
    for i, (x, r, it) in enumerate(items, 1):
        cc = r['content']
        L += [f"## {i}. `{x['target_id']}` — {x['title']}", '',
              f"- Sub-bloco {x['sub_block']} · {r['granularity']['role']} · LEGAL_RISK {x['legal_risk']} · complexidade {x['verification_complexity']} · "
              f"jurisprudência {x['jurisprudence']}",
              f"- **Motivo HIGH exato:** {'; '.join(x['legal_reasons'])}"]
        if x['legal_secondary']:
            L.append(f"- Sinais secundários: {'; '.join(_cut(s, 140) for s in x['legal_secondary'])}")
        L += ['', '**Afirmação que depende da revisão humana**', ''] + [f'- {_cut(s, 400)}' for s in it['depend']]
        L += ['', f"**Lei Seca relevante** {it['law_note']}".rstrip(), ''] + [f"- `{t.split(':', 1)[1]}`: {s}" for t, s in it['law']]
        for key, ttl in (('o_que_diz', 'O QUE DIZ'), ('o_que_significa', 'O QUE SIGNIFICA'), ('exemplo_pratico', 'EXEMPLO PRÁTICO'), ('atencao', 'ATENÇÃO')):
            L += ['', f'**{ttl}**', '', (cc[key] or '—').replace('\n', '\n\n')]
        L += ['', '**PALAVRAS DIFÍCEIS**', ''] + [f"- *{g['termo']}*: {g['explicacao']}" for g in cc['palavras_dificeis']]
        L += ['', '**CAMADA EXTERNA**', ''] + ([f'- {n_}' for n_ in r['external_layer_notes']] or ['—'])
        L += ['', '**Evidência local (versionada)**', ''] + [f'- {_cut(s, 300)}' for s in it['local']]
        L += ['', '**Evidência externa faltante**', ''] + [f'- {s}' for s in it['missing']]
        L += ['', f"**Decisão sugerida: {it['decision']}** — {it['decision_why']}", '',
              '- [ ] APROVAR   - [ ] AJUSTAR   - [ ] VERIFICAR EXTERNAMENTE', '', '---', '']
    return '\n'.join(L) + '\n'


def quick_c(doc, c, title, safe_fix):
    xs = [x for x in doc['rows'] if x['queue'] == 'C_QUICK_REVIEW']
    L = [f'# {title} — REVISÃO RÁPIDA (fila C, segundo passe)', '',
         f"Lote `{c.spec['batch_id']}` · {len(xs)} itens · por item: trecho problemático, motivo, contexto mínimo e proposta segura. "
         'Nenhuma proposta foi aplicada.', '']
    if not xs:
        L += ['- nenhum item nesta fila: as correções seguras do segundo passe foram aplicadas e registradas no log editorial; o que exige '
              'interpretação jurídica externa ficou em D.']
    for x in xs:
        r = c.records[x['target_id']]
        L += [f"## `{x['target_id']}` — {x['title']} · risco {x['legal_risk']}", '']
        for d in x['detectors']:
            if d['severity'] != 'REVIEW_REQUIRED':
                continue
            sec = d['section']
            text = '\n'.join(r.get('external_layer_notes') or []) if sec == 'external_layer_notes' else (r['content'].get(sec) or '')
            excerpt = d['sentence'] or d['match'] or ''
            i = text.find(excerpt) if excerpt else -1
            ctx_ = (_cut(text[max(0, i - 120):i], 120) + ' ⟦trecho⟧ ' + _cut(text[i + len(excerpt):i + len(excerpt) + 120], 120)) if i >= 0 else _cut(text, 200)
            reason, _, proposal = (d['detail'] or '').partition(' || proposta: ')
            L += [f'- **Trecho ({sec}):** "{_cut(excerpt, 300)}"', f'- **Motivo:** {d["code"]} — {_cut(reason, 240)}',
                  f'- **Contexto mínimo:** {ctx_}', f"- **Proposta segura:** {proposal or safe_fix.get(d['code'], 'revisar o trecho')}", '']
        L += ['- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D', '']
    return '\n'.join(L) + '\n'


# ---------------------------------------------------------------- second-pass log and report

def editorial_log(bd, p, doc, c, pre):
    """Every change of the second pass: editorial corrections (drafts/<P>_<X>_SECOND_PASS_LOG.json), risk reclassification per target
    (against the pre-second-pass triage snapshot, when versioned), transition decisions and judicial-review classification."""
    corr = []
    for f in sorted((Path(bd) / 'drafts').glob(f'{p}_*_SECOND_PASS_LOG.json')):
        corr += _load(f)['corrections']
    pre_rows = {x['target_id']: x for x in (pre or {}).get('rows', [])}
    moves = []
    for x in doc['rows']:
        o = pre_rows.get(x['target_id'])
        if o and (o['queue'], o['legal_risk'], o['jurisprudence']) != (x['queue'], x['legal_risk'], x['jurisprudence']):
            moves.append(dict(target_id=x['target_id'], queue_before=o['queue'], queue_after=x['queue'], risk_before=o['legal_risk'],
                              risk_after=x['legal_risk'], jurisprudence_before=o['jurisprudence'], jurisprudence_after=x['jurisprudence'],
                              rules_before=o['legal_rules'], rules_after=x['legal_rules'], reasons_after=x['legal_reasons']))
    overviews = [r for r in c.records.values() if r['granularity']['role'] == 'OVERVIEW']
    return dict(schema_version=1, batch_id=c.spec['batch_id'], human_approved_t1_granted=0,
                policy='segundo passe: correcao automatica so quando segura; o que exige interpretacao juridica externa vai para C/D; nada aprovado',
                editorial_corrections=dict(total=len(corr), by_category=dict(sorted(Counter(x['category'] for x in corr).items())),
                                           by_detector=dict(sorted(Counter(x['detector'] for x in corr).items())), entries=corr),
                risk_reclassification=dict(total=len(moves), entries=moves),
                transition=dict(evidence_file=f'{p}_TRANSITION_EVIDENCE.json', targets=len(c.transition),
                                resolved=sorted(t for t, e in c.transition.items() if e['resolution'] == RESOLVED),
                                kept_high=sorted(t for t, e in c.transition.items() if e['resolution'] == ACTIVE)),
                judicial_review=dict(classified=len(c.second['judicial_review']),
                                     by_class=dict(sorted(Counter(v['classification'] for v in c.second['judicial_review'].values()).items())),
                                     entries=c.second['judicial_review']),
                parent_child=dict(overviews_checked=len(overviews),
                                  open_findings=sorted({x['target_id'] for x in doc['rows'] for d in x['detectors']
                                                        if d['code'] == 'PARENT_CHILD_LEGAL_CONSISTENCY'}),
                                  fixed_in_second_pass=sorted({x['target_id'] for x in corr if x['category'] == 'PAI_CONTRADIZ_FILHO'})))


def report_section(doc, pre, log, pre_chars=None):
    L = ['', '## Segundo passe (compressão de risco e saneamento de fonte)', '']
    if pre:
        L += ['| | Antes | Depois |', '|---|---|---|']
        for q in ('A_CLEAN_LOW', 'B_CLEAN_MEDIUM', 'C_QUICK_REVIEW', 'D_FULL_HUMAN_REVIEW', 'E_HARD_FAIL'):
            L.append(f"| {q} | {pre['counts'][q]} | {doc['counts'][q]} |")
        for k in ('LOW', 'MEDIUM', 'HIGH'):
            L.append(f"| LEGAL_RISK {k} | {pre['legal_risk_counts'].get(k, 0)} | {doc['legal_risk_counts'].get(k, 0)} |")
        L.append(f"| D (%) | {100 * pre['counts']['D_FULL_HUMAN_REVIEW'] / len(pre['rows']):.1f}% | {100 * doc['counts']['D_FULL_HUMAN_REVIEW'] / len(doc['rows']):.1f}% |")
        if pre_chars:
            L.append(f"| Caracteres apresentados ao humano | {pre_chars:,} | {doc['metrics']['presented_chars']:,} |".replace(',', '.'))
        L.append('')
    L += [f"- Correções editoriais do segundo passe: {log['editorial_corrections']['total']} "
          f"({', '.join(f'{k} {v}' for k, v in log['editorial_corrections']['by_category'].items())}).",
          f"- Reclassificações de risco/fila: {log['risk_reclassification']['total']}.",
          f"- Transições: {log['transition']['targets']} com evidência versionada; {len(log['transition']['resolved'])} resolvidas pelo Git (MEDIUM); "
          f"{len(log['transition']['kept_high'])} mantidas HIGH com critério explícito.",
          f"- Vide ADI: {log['judicial_review']['classified']} classificados ({', '.join(f'{k} {v}' for k, v in log['judicial_review']['by_class'].items())}).",
          f"- PARENT_CHILD_LEGAL_CONSISTENCY: {log['parent_child']['overviews_checked']} visões gerais verificadas; "
          f"{len(log['parent_child']['open_findings'])} achado(s) em aberto; {len(log['parent_child']['fixed_in_second_pass'])} corrigido(s) no segundo passe."]
    return L
