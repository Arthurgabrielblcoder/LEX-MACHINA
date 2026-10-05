"""ENTENDA-T1 scale pipeline: triage of a pending production batch into queues A-E and the four review packets.

Read-only on the batch content (never rewrites text, status or version; AUTO_APPROVE_* must stay false). Writes:
  <P>_TRIAGE.json                 queue per target, detectors, risk reasons, external resolution, metrics
  <P>_COMPACT_CLEAN_REVIEW.md     queues A/B: one compact card per item
  <P>_QUICK_REVIEW.md             queue C: only the problem excerpt, minimal context, detector, reason and a safe correction proposal
  <P>_FULL_HUMAN_REVIEW.md        queue D: full T1 package (Lei Seca, five sections, external layer, risk reasons, vigency, detectors)
  <P>_HARD_FAIL_REPORT.md         queue E (explicit 0 when empty)
  MICRO_ADJUSTMENTS_LOG.json      automatic micro-adjustments (applied only if T1_PIPELINE_CONFIG MICROAUTO_APPLY) and eligible proposals
<P> is derived from the batch id (ENTENDA_CF_PRODUCTION_BATCH_06 -> BATCH06).
Usage: python t1_batch_packets.py <batch_dir>
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entenda_engine as E  # noqa: E402
import t1_triage as T  # noqa: E402
import t1_validator_v2 as V  # noqa: E402

SAFE_FIX = dict(T.QUICK_ACTION, **{
    'LONG_SENTENCE': 'dividir a frase em duas ou mais, sem alterar o conteudo juridico',
    'DUPLICATION': 'diferenciar a redacao entre as duas explicacoes (manter o conteudo de cada dispositivo)',
    'LAW_DEPENDENCY_OMITTED': 'mencionar, em uma oracao, a dependencia de lei apontada pela Lei Seca',
    'ABSOLUTE_CLAIM': 'trocar o termo absoluto por formulacao fiel ao texto, ou confirmar que o texto o autoriza',
    'EXCEPTION_NOT_IN_TEXT': 'retirar a excecao ou apontar o trecho da Lei Seca que a preve',
    'EXTRAPOLATION_NUMBER': 'retirar o numero ou apontar sua origem na Lei Seca',
    'EXAMPLE_NUMBER': 'confirmar que o numero do exemplo e hipotetico ou vem do texto',
    'TRANSITION_IN_CORE': 'mover a mencao a emenda/transicao para ATENCAO ou camada externa',
    'MODALITY_SHIFT': 'restaurar a modalidade do texto (faculdade x dever)',
})
SECTIONS = (('o_que_diz', 'O QUE DIZ'), ('o_que_significa', 'O QUE SIGNIFICA'), ('exemplo_pratico', 'EXEMPLO PRÁTICO'), ('atencao', 'ATENÇÃO'))


def prefix(batch_id):
    m = re.search(r'BATCH_(\d+)$', batch_id)
    return f'BATCH{m.group(1)}' if m else 'BATCH'


def _sub_block(spec, t):
    art = ':'.join(t.split(':')[:2])
    return next((k for k, v in (spec.get('sub_blocks') or {}).items() if art in v), '—')


def _ext(x):
    return ', '.join(x['external_dependency'] or []) or 'nenhuma'


def _notes(r):
    return '; '.join(r['external_layer_notes']) or 'nenhuma'


def _warnings(x, chk_row):
    out = sorted(set(x['lint']))
    out += [f"{f['code']}({'resolvido' if f['resolution'] else 'ABERTO'})" for f in chk_row['findings']]
    return ', '.join(out) or 'nenhum'


def compact(rows, act, chk, spec):
    L = [f"# {prefix(spec['batch_id'])} — REVISÃO COMPACTA (filas A e B)", '',
         f"Lote `{spec['batch_id']}` · {spec['as_of_date']} · nenhum item aprovado (AUTO_APPROVE_LOW/MEDIUM = OFF). "
         'T1 completo só sob pedido.', '']
    for q, label in (('A_CLEAN_LOW', 'A — CLEAN_LOW'), ('B_CLEAN_MEDIUM', 'B — CLEAN_MEDIUM')):
        xs = [x for x in rows if x['queue'] == q]
        L += [f'## {label} ({len(xs)})', ''] + (['- nenhum item nesta fila', ''] if not xs else [])
        for x in xs:
            r, c = act[x['target_id']], act[x['target_id']]['content']
            L += [f"### `{x['target_id']}` — {x['title']}", '',
                  f"- Risco: {x['risk']} ({'; '.join(chk[x['target_id']]['risk_reasons'])})",
                  f"- Ponto jurídico: {T._first_sentence(c['o_que_diz'])}",
                  f"- Interpretação principal: {T._first_sentence(c['o_que_significa'])}",
                  f"- ATENÇÃO: {c['atencao'] or '—'}",
                  f"- Dependência externa: {_ext(x)} · camada externa: {_notes(r)}",
                  f"- Warnings: {_warnings(x, chk[x['target_id']])}",
                  f"- Motivo da fila: {x['reason']}", '', '- [ ] APROVAR   - [ ] AJUSTAR   - [ ] MANDAR PARA D', '']
    return '\n'.join(L) + '\n'


def quick(rows, act, chk, spec):
    xs = [x for x in rows if x['queue'] == 'C_QUICK_REVIEW']
    L = [f"# {prefix(spec['batch_id'])} — REVISÃO RÁPIDA (fila C)", '',
         f"Lote `{spec['batch_id']}` · {len(xs)} itens · só o trecho com problema; nenhuma correção foi aplicada.", '']
    if not xs:
        L += ['- nenhum item nesta fila']
    for x in xs:
        r = act[x['target_id']]
        L += [f"## `{x['target_id']}` — {x['title']} · risco {x['risk']}", '']
        seen = set()
        for d in x['detectors']:
            if d['severity'] != 'REVIEW_REQUIRED':
                continue
            if d['code'] == 'EDITORIAL_CHECK_UNRESOLVED':
                ed = next((f for f in chk[x['target_id']]['findings'] if not f['resolution'] and f['code'] == d['match']), None)
                code, section, excerpt = d['match'], (ed or {}).get('section', d['section']), (ed or {}).get('detail', d['sentence'] or '')
            else:
                code, section, excerpt = d['code'], d['section'], d['sentence'] or ''
            if (code, section, excerpt) in seen:
                continue
            seen.add((code, section, excerpt))
            text = r['content'].get(section) if section in r['content'] else ''
            if text and code == 'LONG_SENTENCE':  # editorial_checks stores only the first 80 chars: show the whole sentence
                excerpt = next((s_ for s_ in T._disp_sentences(text) if s_.startswith(excerpt.strip()[:60])), excerpt)
            before, after = T._sent_ctx(text or '', excerpt) if text else ('', '')
            L += [f"- **Trecho:** \"{excerpt}\"",
                  f"- **Contexto mínimo:** {section}{': … ' + T._cut(before, 140) if before else ''}{' ⟦trecho⟧ ' + T._cut(after, 140) if after else ''}",
                  f"- **Detector:** {code} ({d['code']})",
                  f"- **Motivo:** {x['reason']}",
                  f"- **Proposta de correção segura:** {SAFE_FIX.get(code, 'revisar o trecho')}", '']
        L += ['- [ ] ACEITAR PROPOSTA   - [ ] AJUSTAR   - [ ] MANDAR PARA D', '']
    return '\n'.join(L) + '\n'


def full(rows, act, chk, spec, plan, ctx):
    xs = [x for x in rows if x['queue'] == 'D_FULL_HUMAN_REVIEW']
    L = [f"# {prefix(spec['batch_id'])} — REVISÃO HUMANA COMPLETA (fila D)", '',
         f"Lote `{spec['batch_id']}` · {len(xs)} itens · nenhum aprovado. Ordenado por sub-bloco e dispositivo.", '', '## Índice', '']
    xs = sorted(xs, key=lambda x: (_sub_block(spec, x['target_id']), E.T.sort_key(x['target_id']) if hasattr(E.T, 'sort_key') else x['target_id']))
    for i, x in enumerate(xs, 1):
        L.append(f"{i}. [{_sub_block(spec, x['target_id'])}] `{x['target_id']}` — {x['title']} ({x['risk']})")
    L += ['']
    for i, x in enumerate(xs, 1):
        t, r = x['target_id'], act[x['target_id']]
        item = T._full_package_item(i, r, ctx, x)
        rules = sorted({re.split(r':', s_, 1)[0] for s_ in chk[t]['risk_reasons']})
        extra = [f"- Sub-bloco {_sub_block(spec, t)} · gatilhos HIGH: {', '.join(rules)}"
                 + (f" · vigência: {'; '.join(plan[t])}" if plan.get(t) else '')
                 + f" · checks: {_warnings(x, chk[t])}"]
        if x.get('external_resolution'):
            extra.append(f"- Resolver externo: {x['external_resolution']['status']} via {x['external_resolution']['via']}")
        L += item[:4] + extra + item[4:]
    return '\n'.join(L) + '\n'


def hard(rows, spec):
    xs = [x for x in rows if x['queue'] == 'E_HARD_FAIL']
    L = [f"# {prefix(spec['batch_id'])} — HARD FAIL (fila E)", '', f'Total: **{len(xs)}**', '']
    L += [f"- `{x['target_id']}` — {x['reason']}" for x in xs] or ['- 0 itens com HARD_FAIL (validator v2 e contrato de bloqueio do engine).']
    return '\n'.join(L) + '\n'


def micro_auto(rows, act, cfg):
    """Automatic micro-adjustments: eligible findings are logged; applied only when MICROAUTO_APPLY is true (default false)."""
    log = []
    for x in rows:
        for d in x['detectors']:
            if d['severity'] == 'EDITORIAL_AUTO_FIX_ELIGIBLE':
                log.append(dict(target_id=x['target_id'], code=d['code'], section=d['section'], match=d['match'],
                                applied=False, reason='MICROAUTO_APPLY=false: proposta registrada, nao aplicada'))
    return dict(policy='micro-ajuste nunca altera sentido juridico; aplicacao automatica so com MICROAUTO_APPLY=true',
                microauto_apply=bool(cfg.get('MICROAUTO_APPLY')), applied=sum(1 for e in log if e['applied']), eligible=len(log), entries=log)


def run(batch_dir):
    bd = Path(batch_dir)
    ctx = E.NormContext('CF88')
    cfg = V.load_json(V.CONFIG)
    spec = V.load_json(bd / 'BATCH_SPEC.json')
    doc, act = T.triage(bd, ctx)
    chk = {r['target_id']: r for r in V.load_json(bd / 'EDITORIAL_CHECKS.json')['rows']}
    plan_file = next(iter(sorted(bd.glob('BATCH*_TARGET_PLAN.json'))), None)
    plan = V.load_json(plan_file).get('vigency_by_target', {}) if plan_file else {}
    rows = doc['rows']
    for x in rows:  # route reason: a HIGH item without detector findings is in D by the risk rule, not by an alert
        if x['queue'] == 'D_FULL_HUMAN_REVIEW' and x['risk'] == 'HIGH' and x['reason'].startswith('sem alerta'):
            x['reason'] = 'risco HIGH (escalonamento automatico t1_risk); sem alerta juridico/editorial do validator v2'
    p = prefix(spec['batch_id'])
    files = {f'{p}_COMPACT_CLEAN_REVIEW.md': compact(rows, act, chk, spec), f'{p}_QUICK_REVIEW.md': quick(rows, act, chk, spec),
             f'{p}_FULL_HUMAN_REVIEW.md': full(rows, act, chk, spec, plan, ctx), f'{p}_HARD_FAIL_REPORT.md': hard(rows, spec)}
    _, _, old_model = T.render(doc, act, ctx)
    draft_chars = sum(len(act[x['target_id']]['content'][k] or '') for x in rows for k in E.REQUIRED_TEXT + ('atencao',)) + \
        sum(len(g['termo']) + len(g['explicacao']) for x in rows for g in act[x['target_id']]['content']['palavras_dificeis'])
    presented = sum(len(v) for v in files.values())
    micro = micro_auto(rows, act, cfg)
    doc['metrics'] = dict(total_draft_chars=draft_chars, old_model_full_package_chars=old_model, presented_chars=presented,
                          presented_by_file={k: len(v) for k, v in files.items()},
                          reduction_pct=round(100 * (1 - presented / old_model), 1) if old_model else None)
    doc['micro_adjustments'] = dict(applied=micro['applied'], eligible=micro['eligible'], microauto_apply=micro['microauto_apply'])
    doc['by_risk_all'] = {k: {q: sum(1 for x in rows if x['queue'] == q and x['risk'] == k) for q in T.QUEUES} for k in ('LOW', 'MEDIUM', 'HIGH')}
    doc['human_approved_t1_granted'] = 0
    for name, text in files.items():
        (bd / name).write_bytes(text.encode('utf-8'))
    (bd / 'MICRO_ADJUSTMENTS_LOG.json').write_bytes((json.dumps(micro, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    (bd / f'{p}_TRIAGE.json').write_bytes((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    return doc


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    d = run(sys.argv[1])
    print(json.dumps(dict(counts=d['counts'], by_risk=d['by_risk_all'], metrics=d['metrics'], micro=d['micro_adjustments']), ensure_ascii=False, indent=1))
