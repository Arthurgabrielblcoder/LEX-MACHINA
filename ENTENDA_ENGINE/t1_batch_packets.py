"""ENTENDA-T1 scale pipeline (recalibrated): triage of a pending production batch into queues A-E with two separate axes, and the
human review packets.

  LEGAL_RISK              LOW / MEDIUM / HIGH         t1_risk.assess (interpretive signals + legal-content findings)
  VERIFICATION_COMPLEXITY SIMPLE / STRUCTURED / EXTERNAL  t1_risk.complexity (numbers, lists, remissions, external dependency)
  queue                   t1_validator_v3.route: E hard fail · D legal HIGH or FULL finding · C quick findings · A LOW · B MEDIUM

Read-only on the batch content: never rewrites text, status or version; AUTO_APPROVE_LOW/MEDIUM must stay false; MICROAUTO_APPLY only
logs. If more than D_DIAGNOSTIC_THRESHOLD of the new explanations land in D, the full package is NOT generated: a
<P>_D_ESCALATION_DIAGNOSTIC.md is written instead and the volume must be justified before the full package is produced.
Outputs (P from the batch id, e.g. BATCH06):
  <P>_TRIAGE.json, <P>_COMPACT_CLEAN_REVIEW.md (A/B), <P>_QUICK_REVIEW.md (C), <P>_FULL_HUMAN_REVIEW.md (D) or
  <P>_D_ESCALATION_DIAGNOSTIC.md, <P>_HARD_FAIL_REPORT.md (E), MICRO_ADJUSTMENTS_LOG.json
"""
import json
import re
from collections import Counter
from pathlib import Path

import entenda_engine as E
import t1_external_resolver as X
import t1_risk as R
import t1_triage as T
import t1_validator_v2 as V
import t1_validator_v3 as V3

QUEUES = T.QUEUES
D_DIAGNOSTIC_THRESHOLD = 0.40
SHOWN_INFO = ('EXAMPLE_NUMBER_NOT_IN_TEXT', 'NUMBER_FROM_OTHER_DEVICE', 'HISTORICAL_CLAIM_SUPPORTED', 'SEMANTIC_AMBIGUITY_REGISTERED')
SAFE_FIX = dict(T.QUICK_ACTION, **{
    'NUMBER_NOT_IN_TEXT': 'retirar a quantidade ou substituir pela que esta na Lei Seca (nao calcular totais que o texto nao traz)',
    'RESSALVA_OMITTED_IN_SUMMARY': 'acrescentar a ressalva do dispositivo resumido, em uma oracao (sem interpreta-la)',
    'LIST_ITEM_POSSIBLY_DROPPED': 'incluir o item/elemento sem traco ou declarar que a enumeracao e parcial ("entre elas")',
    'HISTORICAL_CLAIM_UNVERIFIED': 'retirar a afirmacao historica ou conferi-la na fonte historica (cf.txt legado versionado) e registrar proveniencia',
    'CONDITION_NOT_IN_TEXT': 'retirar a condicao que o texto nao preve, ou registrar a fonte (proveniencia) e mandar para D',
    'EXTERNAL_FACT_NEEDS_PROVENANCE': 'manter so a remissao registrada pela fonte; nao afirmar conteudo/estado da norma externa sem proveniencia',
    'EXTERNAL_NORMATIVE_CONTENT_CLAIM': 'retirar o conteudo atribuido a norma externa ou registrar a fonte (proveniencia)',
    'EXCEPTION_OR_RESSALVA_DROPPED': 'confirmar que o trecho nao generaliza a regra contra a ressalva do texto',
    'UNIVERSAL_CLAIM': T.QUICK_ACTION['UNIVERSAL_CLAIM'],
})


def prefix(batch_id):
    m = re.search(r'BATCH_(\d+)$', batch_id)
    return f'BATCH{m.group(1)}' if m else 'BATCH'


def _sub_block(spec, t):
    art = ':'.join(t.split(':')[:2])
    return next((k for k, v in (spec.get('sub_blocks') or {}).items() if art in v), '—')


def _cut(s, n):
    return T._cut(s or '', n)


class Context:
    """Everything the triage needs, built once per run (deterministic)."""

    def __init__(self, bd, ctx, catalog, known, registry, relations_pin):
        self.bd, self.ctx, self.catalog, self.known, self.registry = Path(bd), ctx, catalog, known, registry
        self.spec = V.load_json(self.bd / 'BATCH_SPEC.json')
        self.cfg = V.load_json(V.CONFIG)
        assert self.cfg['AUTO_APPROVE_LOW'] is False and self.cfg['AUTO_APPROVE_MEDIUM'] is False, 'auto-approval must stay OFF'
        plan_file = next(iter(sorted(self.bd.glob('BATCH*_TARGET_PLAN.json'))), None)
        self.plan = V.load_json(plan_file) if plan_file else {}
        self.vigency = self.plan.get('vigency_by_target', {})
        self.vigency_ecs = {n for v in self.vigency.values() for a in v for n in V3.EC_NUM.findall(a)}
        self.relations = X.RelationsIndex(relations_pin.get('sources', []))
        self.pinned = set(self.relations.by_target)
        self.scope_text = ' '.join(ctx.text.get(t, '') for a in self.spec['scope'] for t in ctx.subtree(a))
        self.records = {r['target_id']: r for r in E.load_corpus(self.bd / self.spec['batch_corpus']) if r['status'] == 'ACTIVE'}
        owners = {t: set(V3.scope_devices(r, ctx)) for t, r in self.records.items() if r['granularity']['role'] != 'OVERVIEW'}
        for p in self.spec.get('reused', {}):
            if ctx.kind(p) != 'ARTIGO':
                owners[p] = set(ctx.subtree(p))
        self.owners = owners

    def owned_elsewhere(self, tid):
        return set().union(*[v for k, v in self.owners.items() if k != tid] or [set()])

    def validate(self, r, lint_rows=(), editorial_rows=()):
        return V3.validate(r, self.ctx, self.catalog, self.known, lint_rows, editorial_rows, owned_elsewhere=self.owned_elsewhere(r['target_id']),
                           vigency_ecs=self.vigency_ecs, pinned_targets=self.pinned, registry=self.registry, scope_text=self.scope_text)

    def assess(self, r, findings):
        return R.assess(r, self.ctx, self.vigency, findings, V3.interpretive_signals(r)), R.complexity(r, self.ctx, self.vigency, findings)


def risk_input(c):
    """Risk map for EDITORIAL_REVIEW_INPUT.json (legal risk drives editorial_checks' risk column; complexity is recorded alongside)."""
    out = {}
    for t, r in sorted(c.records.items()):
        a, cx = c.assess(r, c.validate(r))
        out[t] = dict(level=a['level'], rules=a['rules'], reasons=a['reasons'], jurisprudence=a['jurisprudence'],
                      verification_complexity=cx['level'], complexity_reasons=cx['reasons'])
    return out


def triage(c, pre=None):
    """pre: PRE_RECALIBRATION_MANIFEST queues_by_target (old queue/risk) to report the migration."""
    pre = pre or {}
    spec = c.spec
    chk = {r['target_id']: r for r in V.load_json(c.bd / 'EDITORIAL_CHECKS.json')['rows']}
    man = V.load_json(c.bd / spec['index_dir'] / 'ENTENDA_BUILD_MANIFEST.json')
    lint = {}
    for w in man['warnings']:
        lint.setdefault(w['target_id'], []).append(w)
    rows = []
    for t, r in c.records.items():
        if r['review_status'] != 'PENDING_HUMAN_REVIEW':
            continue
        fs = c.validate(r, lint.get(t, []), chk[t]['findings'])
        a, cx = c.assess(r, fs)
        q = V3.route(fs, a['level'])
        external = any(f['code'] in X.EXTERNAL_CODES | {'EXTERNAL_NORMATIVE_CONTENT_CLAIM'} and f['severity'] in ('REVIEW_REQUIRED', 'HARD_FAIL')
                       for f in fs)
        res = X.resolve(r, c.catalog, c.relations, V._provenance(r)) if external else None
        rev = [f for f in fs if f['severity'] in ('HARD_FAIL', 'REVIEW_REQUIRED')]
        if q == 'D_FULL_HUMAN_REVIEW':
            reason = 'LEGAL_RISK HIGH: ' + '; '.join(a['reasons']) if a['level'] == 'HIGH' else \
                'alerta FULL: ' + '; '.join(sorted({f"{f['code']} ({f['match']})" for f in rev if f['route'] == 'FULL'}))
        elif rev:
            reason = '; '.join(sorted({f"{f['code']} ({_cut(f['match'] or f['detail'], 60)})" for f in rev}))
        else:
            reason = f"sem alerta; LEGAL_RISK {a['level']}" + (f" ({', '.join(a['rules'])})" if a['rules'] else '')
        ext = sorted({f['match'] for f in fs if f['code'].startswith('EXTERNAL_') and f['severity'] != 'INFO' and f['match']}
                     | ({'JURISPRUDENCIA (contexto)'} if a['jurisprudence'] == 'CONTEXT_ONLY' else set())
                     | ({'JURISPRUDENCIA (necessaria)'} if a['jurisprudence'] == 'REQUIRED_FOR_CORRECTNESS' else set()))
        old = pre.get(t, {})
        rows.append(dict(
            target_id=t, title=E.display_title(r), role=r['granularity']['role'], sub_block=_sub_block(spec, t),
            legal_risk=a['level'], legal_rules=a['rules'], legal_reasons=a['reasons'], legal_secondary=a['secondary'],
            jurisprudence=a['jurisprudence'], verification_complexity=cx['level'], complexity_reasons=cx['reasons'], queue=q,
            previous=dict(risk=old.get('risk'), queue=old.get('queue')) if old else None,
            detectors=[dict(code=f['code'], severity=f['severity'], route=f['route'], section=f['section'], match=f['match'], sentence=f['sentence'],
                            detail=f['detail']) for f in fs if f['severity'] in ('HARD_FAIL', 'REVIEW_REQUIRED', 'EDITORIAL_AUTO_FIX_ELIGIBLE')],
            info=[dict(code=f['code'], section=f['section'], match=f['match'], detail=f.get('refined_v3') or f['detail'])
                  for f in fs if f['severity'] == 'INFO' and (f['code'] in SHOWN_INFO or f.get('refined_v3'))],
            lint=[w['code'] for w in lint.get(t, [])], editorial_checks=[f"{f['code']}:{'RESOLVED' if f['resolution'] else 'OPEN'}" for f in chk[t]['findings']],
            external_dependency=ext or None, reason=reason, show_full_t1=q in ('D_FULL_HUMAN_REVIEW', 'E_HARD_FAIL'),
            review_status=r['review_status'], editorial_version=r['editorial_version'],
            **({'external_resolution': dict(status=res['status'], via=res['via'],
                                            evidence=[{k: v for k, v in e.items() if k in ('norma', 'entry', 'tipo', 'fonte', 'status', 'decisao', 'url', 'source')}
                                                      for e in res['evidence']])} if res else {})))
    rows.sort(key=lambda x: (QUEUES.index(x['queue']), c.ctx.order[x['target_id']]))
    counts = {q: sum(1 for x in rows if x['queue'] == q) for q in QUEUES}
    by = lambda key, vals: {k: {q: sum(1 for x in rows if x['queue'] == q and x[key] == k) for q in QUEUES} for k in vals}  # noqa: E731
    doc = dict(schema_version=2, triage='T1_PENDING_TRIAGE_RECALIBRATED', validator=V3.VERSION, batch_id=spec['batch_id'], as_of=spec['as_of_date'],
               auto_approve=dict(LOW=c.cfg['AUTO_APPROVE_LOW'], MEDIUM=c.cfg['AUTO_APPROVE_MEDIUM']),
               policy='somente classificacao; nenhum texto, status ou versao alterado; o detector roteia risco e nao substitui revisao juridica',
               axes=dict(LEGAL_RISK='ha risco real de interpretacao juridica incorreta? (t1_risk.assess)',
                         VERIFICATION_COMPLEXITY='quao dificil e verificar o draft deterministicamente? (t1_risk.complexity)'),
               legal_high_rules=R.LEGAL_HIGH, counts=counts,
               legal_risk_counts=dict(Counter(x['legal_risk'] for x in rows)), complexity_counts=dict(Counter(x['verification_complexity'] for x in rows)),
               jurisprudence_counts=dict(Counter(x['jurisprudence'] for x in rows)),
               by_legal_risk=by('legal_risk', ('LOW', 'MEDIUM', 'HIGH')), by_complexity=by('verification_complexity', ('SIMPLE', 'STRUCTURED', 'EXTERNAL')),
               rows=rows)
    if pre:
        old_d = [x for x in rows if (x['previous'] or {}).get('queue') == 'D_FULL_HUMAN_REVIEW']
        doc['migration'] = dict(previous_counts=dict(Counter(x['previous']['queue'] for x in rows if x['previous'])),
                                previous_D=len(old_d), previous_D_now=dict(Counter(x['queue'] for x in old_d)),
                                previous_D_migrated=sum(1 for x in old_d if x['queue'] != 'D_FULL_HUMAN_REVIEW'),
                                previous_risk_counts=dict(Counter(x['previous']['risk'] for x in rows if x['previous'])))
    d_rules = Counter(r_ for x in rows if x['queue'] == 'D_FULL_HUMAN_REVIEW' for r_ in (x['legal_rules'] or ['FULL_FINDING']))
    doc['d_reasons'] = dict(sorted(d_rules.items()))
    doc['finding_counts'] = dict(sorted(Counter(d['code'] for x in rows for d in x['detectors'] if d['severity'] == 'REVIEW_REQUIRED').items()))
    doc['refined_false_positive_counts'] = dict(sorted(Counter(i['code'] for x in rows for i in x['info'] if i['detail'] and i['code'] in
                                                               {'TELEOLOGY_SPECULATIVE', 'UNIVERSAL_CLAIM', 'AUTOMATIC_CONSEQUENCE'}).items()))
    return doc


# ---------------------------------------------------------------- packets

def _warn(x):
    w = [f"{d['code']}({d['section']}: {_cut(d['match'], 50)})" for d in x['detectors'] if d['severity'] == 'EDITORIAL_AUTO_FIX_ELIGIBLE']
    w += [f"{i['code']}({_cut(i['match'], 40)})" for i in x['info'] if i['code'] in SHOWN_INFO]
    w += [f"{e.split(':')[0]}(resolvido)" for e in x['editorial_checks'] if e.endswith('RESOLVED')]
    w += [f"lint {k}" for k in sorted(set(x['lint']) - {'NEAR_COPY_OF_OFFICIAL_TEXT'})]
    return ', '.join(w) or 'nenhum'


def _ext(x, r):
    dep = ', '.join(x['external_dependency'] or []) or 'nenhuma'
    if x.get('external_resolution'):
        dep += f" · resolver: {x['external_resolution']['status']}"
    return dep


def compact(doc, c):
    spec = c.spec
    L = [f"# {prefix(spec['batch_id'])} — REVISÃO COMPACTA (filas A e B)", '',
         f"Lote `{spec['batch_id']}` · {spec['as_of_date']} · nenhum item aprovado (AUTO_APPROVE_LOW/MEDIUM = OFF). Revisão humana obrigatória "
         'em formato compacto; T1 completo só sob pedido. Risco = LEGAL_RISK; complexidade = VERIFICATION_COMPLEXITY.', '']
    for q, label in (('A_CLEAN_LOW', 'A — CLEAN_LOW'), ('B_CLEAN_MEDIUM', 'B — CLEAN_MEDIUM')):
        xs = [x for x in doc['rows'] if x['queue'] == q]
        L += [f'## {label} ({len(xs)})', ''] + (['- nenhum item nesta fila', ''] if not xs else [])
        for x in xs:
            r = c.records[x['target_id']]
            cc = r['content']
            L += [f"### `{x['target_id']}` — {x['title']}", '',
                  f"- Risco: {x['legal_risk']} · complexidade: {x['verification_complexity']}"
                  + (f" · {'; '.join(_cut(s, 90) for s in x['legal_reasons'])}" if x['legal_rules'] else ''),
                  f"- Ponto jurídico: {_cut(T._first_sentence(cc['o_que_diz']), 200)}",
                  f"- Interpretação principal: {_cut(T._first_sentence(cc['o_que_significa']), 170)}",
                  f"- ATENÇÃO: {_cut(T._first_sentence(cc['atencao'] or '—'), 200)}",
                  f"- Dependência externa: {_ext(x, r)}",
                  f"- Warnings: {_warn(x)}",
                  f"- Motivo da fila: {x['reason'] if x['legal_rules'] or x['reason'] != 'sem alerta; LEGAL_RISK LOW' else 'LOW sem alerta'}",
                  '- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D', '']
    return '\n'.join(L) + '\n'


def quick(doc, c):
    xs = [x for x in doc['rows'] if x['queue'] == 'C_QUICK_REVIEW']
    L = [f"# {prefix(c.spec['batch_id'])} — REVISÃO RÁPIDA (fila C)", '',
         f"Lote `{c.spec['batch_id']}` · {len(xs)} itens · só o trecho com problema; nenhuma correção foi aplicada.", '']
    if not xs:
        L += ['- nenhum item nesta fila']
    for x in xs:
        r = c.records[x['target_id']]
        L += [f"## `{x['target_id']}` — {x['title']} · risco {x['legal_risk']} · {x['verification_complexity']}", '']
        seen = set()
        for d in x['detectors']:
            if d['severity'] != 'REVIEW_REQUIRED':
                continue
            if d['code'] == 'EDITORIAL_CHECK_UNRESOLVED':
                code, section, excerpt = d['match'], d['section'], d['detail']
            else:
                code, section, excerpt = d['code'], d['section'], d['sentence'] or ''
            if (code, section, excerpt) in seen:
                continue
            seen.add((code, section, excerpt))
            text = '\n'.join(r.get('external_layer_notes') or []) if section == 'external_layer_notes' else (r['content'].get(section) or '')
            before, after = T._sent_ctx(text, excerpt) if text and excerpt else ('', '')
            ctx_line = section + (': … ' + _cut(before, 120) if before else '') + (' ⟦trecho⟧ ' + _cut(after, 120) if after else '')
            detail = d['detail'] if d['code'] != 'EDITORIAL_CHECK_UNRESOLVED' else f"editorial_checks {code} em aberto"
            L += ([f"- **Trecho:** \"{excerpt}\"", f"- **Contexto mínimo:** {ctx_line}"] if excerpt else
                  [f"- **Lei Seca sem traço na explicação ({section}):** {_cut(detail, 260)}"])
            L += [f"- **Detector:** {code}",
                  f"- **Motivo:** {_cut(detail or x['reason'], 220)}" if excerpt else f"- **Motivo:** enumeração parafraseada sem o item/elemento indicado",
                  f"- **Proposta de correção segura:** {SAFE_FIX.get(code, 'revisar o trecho')}", '']
        L += ['- [ ] ACEITAR PROPOSTA   - [ ] FALSO POSITIVO (manter)   - [ ] MANDAR PARA D', '']
    return '\n'.join(L) + '\n'


def full(doc, c):
    xs = [x for x in doc['rows'] if x['queue'] == 'D_FULL_HUMAN_REVIEW']
    xs = sorted(xs, key=lambda x: (x['sub_block'], c.ctx.order[x['target_id']]))
    L = [f"# {prefix(c.spec['batch_id'])} — REVISÃO HUMANA COMPLETA (fila D)", '',
         f"Lote `{c.spec['batch_id']}` · {len(xs)} itens · nenhum aprovado. Só itens com LEGAL_RISK HIGH ou alerta jurídico FULL. "
         'Ordenado por sub-bloco e dispositivo.', '', '## Índice', '']
    L += [f"{i}. [{x['sub_block']}] `{x['target_id']}` — {x['title']} · {', '.join(x['legal_rules']) or 'FULL'}" for i, x in enumerate(xs, 1)]
    L += ['']
    for i, x in enumerate(xs, 1):
        t, r = x['target_id'], c.records[x['target_id']]
        row = dict(x, risk=x['legal_risk'])
        item = T._full_package_item(i, r, c.ctx, row)
        extra = [f"- Sub-bloco {x['sub_block']} · LEGAL_RISK {x['legal_risk']} · complexidade {x['verification_complexity']} · "
                 f"jurisprudência: {x['jurisprudence']}"]
        extra += [f"- Por que exige raciocínio humano: {'; '.join(x['legal_reasons'])}"]
        if c.vigency.get(t):
            extra.append(f"- Vigência (fonte canônica): {'; '.join(c.vigency[t])}")
        if x.get('external_resolution'):
            extra.append(f"- Resolver externo: {x['external_resolution']['status']} via {x['external_resolution']['via']}")
        cites = V.cited_targets(r, c.ctx)
        if cites:
            extra.append('- Dispositivos citados (runtime): ' + ' · '.join(f"`{d.split(':', 1)[1]}` {_cut(c.ctx.text[d], 160)}" for d in cites[:4]))
        L += item[:4] + extra + item[4:]
    return '\n'.join(L) + '\n'


def diagnostic(doc, c):
    xs = [x for x in doc['rows'] if x['queue'] == 'D_FULL_HUMAN_REVIEW']
    n = len(doc['rows'])
    L = [f"# {prefix(c.spec['batch_id'])} — DIAGNÓSTICO DE ESCALONAMENTO PARA D", '',
         f"{len(xs)} de {n} explicações novas em D ({100 * len(xs) / n:.1f}%), acima do limite de {int(D_DIAGNOSTIC_THRESHOLD * 100)}%. "
         'O pacote completo NÃO foi gerado: o volume precisa ser justificado antes.', '', '## D por motivo', '']
    L += [f"- {k}: {v}" for k, v in doc['d_reasons'].items()]
    L += ['', '## Itens', ''] + [f"- `{x['target_id']}` — {'; '.join(x['legal_reasons']) or x['reason']}" for x in xs]
    return '\n'.join(L) + '\n'


def hard(doc, c):
    xs = [x for x in doc['rows'] if x['queue'] == 'E_HARD_FAIL']
    L = [f"# {prefix(c.spec['batch_id'])} — HARD FAIL (fila E)", '', f'Total: **{len(xs)}**', '']
    L += [f"- `{x['target_id']}` — {x['reason']}" for x in xs] or ['- 0 itens com HARD_FAIL (validator v3 e contrato de bloqueio do engine).']
    return '\n'.join(L) + '\n'


def micro_auto(doc, cfg):
    log = [dict(target_id=x['target_id'], code=d['code'], section=d['section'], match=d['match'], applied=False,
                reason='MICROAUTO_APPLY=false: proposta registrada, nao aplicada')
           for x in doc['rows'] for d in x['detectors'] if d['severity'] == 'EDITORIAL_AUTO_FIX_ELIGIBLE']
    return dict(policy='micro-ajuste nunca altera sentido juridico; aplicacao automatica so com MICROAUTO_APPLY=true',
                microauto_apply=bool(cfg.get('MICROAUTO_APPLY')), applied=0, eligible=len(log), entries=log)


def packets(doc, c):
    """Returns ({file: text}, d_full_generated)."""
    p = prefix(c.spec['batch_id'])
    files = {f'{p}_COMPACT_CLEAN_REVIEW.md': compact(doc, c), f'{p}_QUICK_REVIEW.md': quick(doc, c), f'{p}_HARD_FAIL_REPORT.md': hard(doc, c)}
    n_d = doc['counts']['D_FULL_HUMAN_REVIEW']
    if doc['rows'] and n_d / len(doc['rows']) > D_DIAGNOSTIC_THRESHOLD:
        files[f'{p}_D_ESCALATION_DIAGNOSTIC.md'] = diagnostic(doc, c)
        return files, False
    files[f'{p}_FULL_HUMAN_REVIEW.md'] = full(doc, c)
    return files, True


def metrics(doc, c, files):
    rows = doc['rows']
    act = c.records
    draft_chars = sum(len(act[x['target_id']]['content'][k] or '') for x in rows for k in E.REQUIRED_TEXT + ('atencao',)) + \
        sum(len(g['termo']) + len(g['explicacao']) for x in rows for g in act[x['target_id']]['content']['palavras_dificeis'])
    old_rows = [dict(x, risk=x['legal_risk']) for x in rows]
    full_all = ['# (referência) pacote completo de todos os pendentes', '']
    for i, x in enumerate(old_rows, 1):
        full_all += T._full_package_item(i, act[x['target_id']], c.ctx, x)
    old_model = len('\n'.join(full_all))
    presented = sum(len(v) for v in files.values())
    return dict(total_draft_chars=draft_chars, old_model_full_package_chars=old_model, presented_chars=presented,
                presented_by_file={k: len(v) for k, v in sorted(files.items())},
                reduction_abs=old_model - presented, reduction_pct=round(100 * (1 - presented / old_model), 1) if old_model else None)
