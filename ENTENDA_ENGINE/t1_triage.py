"""ENTENDA-T1 A6: regression of validator v2 against the human decisions, and risk triage of pending explanations (queues A-E).

Read-only on the batch content: writes only report files. Never approves (T1_PIPELINE_CONFIG AUTO_APPROVE_* = false).
Usage: python t1_triage.py <batch_dir>
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entenda_engine as E  # noqa: E402
import t1_external_resolver as X  # noqa: E402
import t1_validator_v2 as V  # noqa: E402

ROOT = HERE.parent
QUEUES = ('A_CLEAN_LOW', 'B_CLEAN_MEDIUM', 'C_QUICK_REVIEW', 'D_FULL_HUMAN_REVIEW', 'E_HARD_FAIL')
QUICK_ACTION = {
    'TELEOLOGY_SPECULATIVE': 'retirar a frase de finalidade (o texto nao a declara) ou reduzi-la ao que o dispositivo diz',
    'UNIVERSAL_CLAIM': 'restringir o quantificador ao alcance da Lei Seca (ou confirmar que o texto o autoriza)',
    'AUTOMATIC_CONSEQUENCE': 'retirar a consequencia automatica ou remete-la a legislacao aplicavel',
    'PERMISSION_NOT_IN_TEXT': 'nao converter a ausencia de garantia em permissao; remeter a legislacao aplicavel',
    'QUALIFIER_NOT_IN_TEXT': 'retirar a condicao (subsidiaria/omissao/lacuna) que o dispositivo nao preve',
    'EXAMPLE_INVENTED_REQUIREMENT': 'retirar do exemplo criterios/mecanismos que o texto nao preve',
    'EDITORIAL_CHECK_UNRESOLVED': 'resolver o achado do editorial_checks',
}


def _rounds(bd):
    spec = V.load_json(bd / 'BATCH_SPEC.json')
    out = []
    for ra in spec.get('round_approvals', []):
        out += V.load_json(bd / ra['decisions'])['decisions']
    return out


def _flagged(fs):
    return any(f['severity'] in ('HARD_FAIL', 'REVIEW_REQUIRED') for f in fs)


def _codes(fs, sev=('HARD_FAIL', 'REVIEW_REQUIRED')):
    return sorted({f['code'] for f in fs if f['severity'] in sev})


def regression(bd, ctx=None, catalog=None, known=None):
    """Validator v2 against the human decisions of the rounds (+ pilots and the prior approved corpus)."""
    bd = Path(bd)
    ctx = ctx or E.NormContext('CF88')
    catalog, known = catalog or V.load_catalog(), known if known is not None else V.load_json(V.KNOWN)
    spec = V.load_json(bd / 'BATCH_SPEC.json')
    allr = E.load_corpus(bd / spec['batch_corpus'])
    v1 = {r['target_id']: r for r in allr if r['editorial_version'] == 1}
    act = {r['target_id']: r for r in allr if r['status'] == 'ACTIVE'}
    dec = _rounds(bd)
    adjusted = [d['target_id'] for d in dec if d['decision'] != 'APPROVED']
    same = [d['target_id'] for d in dec if d['decision'] == 'APPROVED']
    run = lambda r, k=known: V.validate(r, ctx, catalog, k)  # noqa: E731
    pattern_codes = {c for c, *_ in V.PATTERN_RULES}
    adj = {t: run(v1[t], {}) for t in adjusted}                    # v1 that received CHANGES_REQUESTED (raw: no known resolutions)
    tp = [t for t, fs in adj.items() if _flagged(fs)]
    general = lambda fs: [f for f in fs if f['severity'] in ('HARD_FAIL', 'REVIEW_REQUIRED')  # noqa: E731
                          and not (f['code'] == 'CATALOG_LINK_MISSING' and 'target catalogado' in f['detail'])]
    tp_pattern = [t for t, fs in adj.items() if set(_codes(fs)) & pattern_codes]
    tp_general = [t for t, fs in adj.items() if general(fs)]
    fn = [t for t in adjusted if t not in tp]
    same_raw = {t: run(v1[t], {}) for t in same}
    same_res = {t: run(v1[t]) for t in same}
    fin_raw = {t: run(act[t], {}) for t in adjusted + same}
    fin_res = {t: run(act[t]) for t in adjusted + same}
    main = [r for r in E.load_corpus(HERE / 'corpus/CF88.entenda.jsonl') if r['status'] == 'ACTIVE']
    prior = main + [r for pc in spec['prior_corpora'] for r in E.load_corpus(ROOT / pc) if r['status'] == 'ACTIVE']
    pri = {r['explanation_id']: run(r, {}) for r in prior}
    pri_tid = {r['explanation_id']: r['target_id'] for r in prior}
    pilots = {t: run(next(r for r in main if r['target_id'] == t), {}) for t in spec['reused']}
    chain = V.version_chain_findings(allr)
    return dict(
        validator=V.VERSION, batch_id=spec['batch_id'],
        changes_requested_v1=dict(total=len(adjusted), true_positives=len(tp), true_positives_pattern_rules=len(tp_pattern),
                                  true_positives_generalizable=len(tp_general), true_positives_catalog_memory_only=len(tp) - len(tp_general),
                                  memory_only_targets=sorted(set(tp) - set(tp_general)), false_negatives=fn,
                                  codes=dict(Counter(c for fs in adj.values() for c in _codes(fs)))),
        approved_unchanged_v1=dict(total=len(same), flagged_raw=sorted(t for t, fs in same_raw.items() if _flagged(fs)),
                                   flagged_after_known=sorted(t for t, fs in same_res.items() if _flagged(fs))),
        approved_final=dict(total=len(fin_raw), flagged_raw=sorted(t for t, fs in fin_raw.items() if _flagged(fs)),
                            flagged_after_known=sorted(t for t, fs in fin_res.items() if _flagged(fs)),
                            hard_fail=sorted(t for t, fs in fin_raw.items() if 'HARD_FAIL' in {f['severity'] for f in fs})),
        pilots=dict(total=len(pilots), hard_fail=sorted(t for t, fs in pilots.items() if any(f['severity'] == 'HARD_FAIL' for f in fs)),
                    flagged_raw=sorted(t for t, fs in pilots.items() if _flagged(fs))),
        prior_approved_corpus=dict(total=len(pri), hard_fail=sorted(k for k, fs in pri.items() if any(f['severity'] == 'HARD_FAIL' for f in fs)),
                                   flagged_raw=sum(1 for fs in pri.values() if _flagged(fs)),
                                   codes=dict(Counter(c for fs in pri.values() for c in _codes(fs)))),
        version_chain=dict(findings=chain),
        detail=dict(changes_requested_v1={t: _codes(fs) for t, fs in adj.items()},
                    approved_final_raw={t: [f"{f['code']}:{f['match']}" for f in fs if f['severity'] == 'REVIEW_REQUIRED']
                                        for t, fs in fin_raw.items() if _flagged(fs)},
                    prior_flagged=[dict(explanation_id=k, target_id=pri_tid[k],
                                        findings=[dict(code=f['code'], match=f['match'], sentence=f['sentence'], detail=f['detail'])
                                                  for f in fs if f['severity'] in ('HARD_FAIL', 'REVIEW_REQUIRED')])
                                   for k, fs in sorted(pri.items()) if _flagged(fs)]))


# ---------------------------------------------------------------- triage of pending

_ABBREV = re.compile(r'(?:\b(?:arts?|inc|incs|al|n|p|ss?)\.|§|nº)$', re.I)


def _disp_sentences(text):
    """Display-only sentence split (does not cut after "art.", "§", "nº"); detectors keep V._sentences."""
    out = []
    for part in re.split(r'(?<=[.!?])\s+|\n', text or ''):
        if out and _ABBREV.search(out[-1]):
            out[-1] += ' ' + part
        elif part.strip():
            out.append(part)
    return out


def _first_sentence(t):
    s = _disp_sentences(t)
    return (s[0] if s else '')[:220]


def triage(bd, ctx=None, catalog=None, known=None):
    bd = Path(bd)
    cfg = V.load_json(V.CONFIG)
    assert cfg['AUTO_APPROVE_LOW'] is False and cfg['AUTO_APPROVE_MEDIUM'] is False, 'auto-approval must stay OFF in this phase'
    ctx = ctx or E.NormContext('CF88')
    catalog, known = catalog or V.load_catalog(), known if known is not None else V.load_json(V.KNOWN)
    spec = V.load_json(bd / 'BATCH_SPEC.json')
    act = {r['target_id']: r for r in E.load_corpus(bd / spec['batch_corpus']) if r['status'] == 'ACTIVE'}
    chk = {r['target_id']: r for r in V.load_json(bd / 'EDITORIAL_CHECKS.json')['rows']}
    man = V.load_json(bd / spec['index_dir'] / 'ENTENDA_BUILD_MANIFEST.json')
    lint = {}
    for w in man['warnings']:
        lint.setdefault(w['target_id'], []).append(w)
    relations = X.RelationsIndex.from_config(cfg)
    rows = []
    for t, r in act.items():
        if r['review_status'] != 'PENDING_HUMAN_REVIEW':
            continue
        fs = V.validate(r, ctx, catalog, known, lint.get(t, []), chk[t]['findings'])
        external = any(f['code'] in X.EXTERNAL_CODES and f['severity'] in ('REVIEW_REQUIRED', 'HARD_FAIL') for f in fs)
        res = X.resolve(r, catalog, relations, V._provenance(r)) if external else None
        q = V.route(fs, chk[t]['risk'])
        ext = sorted({f['detail'].split(' ')[0] for f in fs if f['code'] in ('CATALOG_LINK_MISSING', 'CATALOG_TOPIC_HANDLED', 'CATALOG_CONTRADICTION')}
                     | {f['match'] for f in fs if f['code'].startswith('EXTERNAL_FACT')})
        rev = [f for f in fs if f['severity'] in ('HARD_FAIL', 'REVIEW_REQUIRED')]
        reason = ('; '.join(sorted({f"{f['code']} ({f['match'] or f['detail']})"[:90] for f in rev})) if rev else
                  'sem alerta juridico/editorial relevante (validator v2, editorial_checks resolvidos, lint informativo)')
        rows.append(dict(
            target_id=t, title=E.display_title(r), role=r['granularity']['role'], risk=chk[t]['risk'], queue=q,
            detectors=[dict(code=f['code'], severity=f['severity'], route=f['route'], section=f['section'], match=f['match'], sentence=f['sentence'])
                       for f in fs if f['severity'] in ('HARD_FAIL', 'REVIEW_REQUIRED', 'EDITORIAL_AUTO_FIX_ELIGIBLE')],
            lint=[w['code'] for w in lint.get(t, [])], editorial_checks=[f"{f['code']}:{'RESOLVED' if f['resolution'] else 'OPEN'}" for f in chk[t]['findings']],
            external_dependency=ext or None, reason=reason, show_full_t1=q in ('D_FULL_HUMAN_REVIEW', 'E_HARD_FAIL'),
            review_status=r['review_status'], editorial_version=r['editorial_version'],
            **({'external_resolution': dict(status=res['status'], via=res['via'],
                                            evidence=[{k: v for k, v in e.items() if k in ('norma', 'entry', 'tipo', 'fonte', 'status', 'decisao', 'url', 'source')}
                                                      for e in res['evidence']])} if res else {})))
    rows.sort(key=lambda x: (QUEUES.index(x['queue']), x['target_id']))
    counts = {q: sum(1 for x in rows if x['queue'] == q) for q in QUEUES}
    doc = dict(schema_version=1, triage='T1_PENDING_TRIAGE', validator=V.VERSION, batch_id=spec['batch_id'], as_of=spec['as_of_date'],
               auto_approve=dict(LOW=cfg['AUTO_APPROVE_LOW'], MEDIUM=cfg['AUTO_APPROVE_MEDIUM']),
               policy='somente classificacao; nenhum texto, status ou versao alterado; o detector nao substitui revisao juridica (roteamento de risco)',
               counts=counts, by_risk={k: {q: sum(1 for x in rows if x['queue'] == q and x['risk'] == k) for q in QUEUES} for k in ('LOW', 'MEDIUM')},
               rows=rows)
    return doc, act


def _full_package_item(i, r, ctx, row):
    c, g = r['content'], r['granularity']
    L = [f'## {i}. {E.display_title(r)}', '', f"- `{r['target_id']}` · {g['role']} · risco {row['risk']} · {r['explanation_id']}",
         f"- Motivo do roteamento: {row['reason']}", '', '**Lei Seca**', '']
    L += [f"- `{ln.split(chr(9))[0]}`: {ln.split(chr(9), 1)[1]}" for ln in r['source']['source_text_snapshot'].split('\n')]
    for key, title in (('o_que_diz', 'O QUE DIZ'), ('o_que_significa', 'O QUE SIGNIFICA'), ('exemplo_pratico', 'EXEMPLO PRÁTICO'), ('atencao', 'ATENÇÃO')):
        L += ['', f'**{title}**', '', (c[key] or '—').replace('\n', '\n\n')]
    L += ['', '**PALAVRAS DIFÍCEIS**', ''] + [f"- *{x['termo']}*: {x['explicacao']}" for x in c['palavras_dificeis']]
    L += ['', '**CAMADA EXTERNA**', ''] + ([f'- {n}' for n in r['external_layer_notes']] or ['—'])
    L += ['', '**Alertas do validator v2**', ''] + [f"- {d['severity']} · {d['code']} · {d['section']}: \"{d['match']}\" — {d['sentence']}" for d in row['detectors']]
    L += ['', '- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR', '', '---', '']
    return L


def render(doc, act, ctx):
    rows = doc['rows']
    L = ['# T1 — TRIAGEM DOS PENDENTES (validator v2, padrão A6)', '',
         f"Lote `{doc['batch_id']}` · {doc['as_of']} · `{doc['validator']}`. **Somente classificação**: nenhum texto, status ou versão foi alterado; "
         f"autoaprovação desligada (LOW={doc['auto_approve']['LOW']}, MEDIUM={doc['auto_approve']['MEDIUM']}). Todos seguem `PENDING_HUMAN_REVIEW`.",
         'O detector não substitui revisão jurídica: ele roteia risco.', '',
         '| Fila | LOW | MEDIUM | Total |', '|---|---|---|---|']
    for q in QUEUES:
        L.append(f"| {q} | {doc['by_risk']['LOW'][q]} | {doc['by_risk']['MEDIUM'][q]} | {doc['counts'][q]} |")
    L += ['', '## Manifesto por target', '', '| Target | Risco | Fila | Detectores | Lint / editorial_checks | Dependência externa | Motivo | T1 completo? |',
          '|---|---|---|---|---|---|---|---|']
    for x in rows:
        det = ', '.join(sorted({d['code'] for d in x['detectors']})) or '—'
        L.append(f"| `{x['target_id']}` | {x['risk']} | {x['queue']} | {det} | {', '.join(x['lint']) or '—'} / {', '.join(x['editorial_checks']) or '—'} | "
                 f"{', '.join(x['external_dependency'] or []) or '—'} | {x['reason']} | {'sim' if x['show_full_t1'] else 'não'} |")
    A = [x for x in rows if x['queue'] == 'A_CLEAN_LOW']
    B = [x for x in rows if x['queue'] == 'B_CLEAN_MEDIUM']
    C = [x for x in rows if x['queue'] == 'C_QUICK_REVIEW']
    D = [x for x in rows if x['queue'] == 'D_FULL_HUMAN_REVIEW']
    L += ['', f'## Fila A — CLEAN_LOW ({len(A)}): lista compacta', '', 'T1 completo só sob pedido.', '',
          '| Target | Título | Resumo (1ª frase do O QUE DIZ) | Checks | Por que limpo |', '|---|---|---|---|---|']
    for x in A:
        r = act[x['target_id']]
        L.append(f"| `{x['target_id']}` | {x['title']} | {_first_sentence(r['content']['o_que_diz'])} | {', '.join(x['editorial_checks']) or 'ok'} | {x['reason']} |")
    L += ['', f'## Fila B — CLEAN_MEDIUM ({len(B)}): revisão agregada', '']
    for x in B:
        r = act[x['target_id']]
        L += [f"- **`{x['target_id']}` — {x['title']}**", f"  - Ponto central: {_first_sentence(r['content']['o_que_diz'])}",
              f"  - Dependência externa: {', '.join(x['external_dependency'] or []) or 'nenhuma'} · alertas: {', '.join(x['lint']) or 'nenhum'}",
              f"  - Amostra do núcleo: {_first_sentence(r['content']['o_que_significa'])}"]
    L += ['', f'## Fila C — QUICK_REVIEW ({len(C)}): só o trecho', '']
    for x in C:
        L.append(f"- **`{x['target_id']}` — {x['title']}**")
        seen = set()
        for d in x['detectors']:
            if d['severity'] == 'REVIEW_REQUIRED' and (d['code'], d['section'], d['sentence']) not in seen:
                seen.add((d['code'], d['section'], d['sentence']))
                L.append(f"  - {d['section']}: \"{d['sentence']}\" → {d['code']}: {QUICK_ACTION.get(d['code'], 'revisar o trecho')}")
    L += ['', f'## Fila D — FULL_HUMAN_REVIEW ({len(D)})', '', 'Pacote completo em `T1_QUEUE_D_FULL_REVIEW.md` (padrão das Rodadas HIGH).', '']
    L += [f"- `{x['target_id']}` — {x['reason']}" for x in D]
    E_ = [x for x in rows if x['queue'] == 'E_HARD_FAIL']
    L += ['', f'## Fila E — HARD_FAIL ({len(E_)})', ''] + ([f"- `{x['target_id']}` — {x['reason']}" for x in E_] or ['- nenhum'])
    pkg = ['# T1 — FILA D — REVISÃO HUMANA COMPLETA', '', f"Lote `{doc['batch_id']}` · {len(D)} itens · nenhum aprovado.", '']
    for i, x in enumerate(D, 1):
        pkg += _full_package_item(i, act[x['target_id']], ctx, x)
    full_all = ['# (referência) pacote completo de todos os pendentes', '']
    for i, x in enumerate(rows, 1):
        full_all += _full_package_item(i, act[x['target_id']], ctx, x)
    return '\n'.join(L) + '\n', '\n'.join(pkg) + '\n', len('\n'.join(full_all))


# ---------------------------------------------------------------- human calibration packet (one compact file for queues A-D)

SENSITIVE = re.compile(r'(\bsempre\b|\bnunca\b|\bsomente\b|\bautomaticamente\b|\bteto\b|\bLei (?:nº|Complementar nº)|\blei federal\b|em vigor|'
                       r'\bvigente\b|\btransi[çc][ãa]o\b|jurisprud\w*|\bSupremo\b|\btribuna\w*|\best[áa]o? (?:na|no|em|pendente|regulamentad\w*)\b|'
                       r'\bn[ãa]o est[áa]\b|\bainda n[ãa]o\b)', re.I)
CITE = re.compile(r'\bart\. (\d+(?:-[A-Z])?)(?:, (§ \d+º?|[IVXL]+)\b)?|\binciso ([IVXL]+)\b|(?<![\w,] )§ (\d+)º?(?!\S*-)')
# calibration annotations for the two FULL items (local evidence only; no web research in this mission)
D_NOTES = {
    'CF88:ART.38:INC.III': [
        'Afirmação a calibrar: ATENÇÃO, 2ª frase — "A soma das remunerações continua sujeita ao teto do art. 37, XI."',
        'Catálogo: `STF_TEMAS_377_384` registra que, nas acumulações constitucionalmente autorizadas de cargos, empregos e funções, o teto do '
        'art. 37, XI, é considerado em relação a cada vínculo, e não sobre o somatório (validado nas Rodadas 01, 03A e 03B).',
        'O draft afirma a leitura oposta (soma) como regra, sem remissão à camada externa. Se a combinação cargo + mandato de Vereador do art. 38, '
        'III, se enquadra exatamente na tese dos Temas 377/384 é questão jurídica para a revisão humana: não resolvida aqui.',
        'Proveniência registrada: nenhuma (item pendente). Camada externa: vazia.'],
    'CF88:ART.37:PAR.7': [
        'Afirmação a calibrar: CAMADA EXTERNA — "A lei sobre conflito de interesses no Poder Executivo federal está na camada de leis correlatas."',
        'Lei mencionada: o draft não a identifica (nem número nem data).',
        'O que o runtime sustenta: só que "A lei disporá sobre os requisitos e as restrições" (§ 7º). Não sustenta a existência, o conteúdo nem a '
        'localização de uma lei federal específica.',
        'Fonte local disponível: `updater/saida/18_AGENCIAS_E_ORGAOS_REGULADORES/lei_13848_2019_agencias_reguladoras.txt` (linhas 878–879) cita '
        '"conflito de interesse, nos termos da Lei nº 12.813, de 16 de maio de 2013". Isso indica que a lei existe, mas o corpus local não traz '
        'o texto dela nem sua vigência, e o draft não a nomeia.',
        'Veio só do draft: a afirmação de estado ("está na camada de leis correlatas"), o recorte "Poder Executivo federal" e, no O QUE '
        'SIGNIFICA/EXEMPLO, a quarentena e a proibição de negociar ações como restrições ilustrativas (a ATENÇÃO já diz que a quarentena não '
        'está no texto constitucional).',
        'Proveniência registrada: nenhuma. **EXTERNAL_VERIFICATION_REQUIRED.**'],
}


def _cut(s, n):
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0] + '…'


def _short_checks(ed_rows, lint_rows):
    lc = Counter(w['code'] for w in lint_rows)
    out = [f"{k}×{v}" if v > 1 else k for k, v in sorted(lc.items())]
    out += [f"{e['code']}({'resolvido' if e['resolution'] else 'ABERTO'})" for e in ed_rows]
    return ', '.join(out) or 'nenhum'


def _sent_ctx(text, sentence):
    ss = _disp_sentences(text)
    i = next((k for k, s in enumerate(ss) if sentence[:40] in s), None)
    if i is None:
        return '', ''
    return (ss[i - 1] if i > 0 else ''), (ss[i + 1] if i + 1 < len(ss) else '')


def calibration_hint(f, rec, ed_rows):
    """Validator's own reading of a REVIEW finding, for calibration (deterministic rules; documented in the packet)."""
    m = (f['match'] or '').lower()
    for e in ed_rows:
        if e.get('resolution') and m and m in (e['detail'] or '').lower():
            return 'PROVÁVEL FALSO POSITIVO', f"mesmo termo já justificado no editorial_checks ({e['code']}): {e['resolution'][:110]}"
    if f['code'] == 'PERMISSION_NOT_IN_TEXT':
        return (('PROVÁVEL PROBLEMA', 'permissão inferida sobre garantia/piso (padrão da R03B, § 7º)')
                if re.search(r'garantia|piso|m[íi]nimo', f['sentence'], re.I) else
                ('INDETERMINADO', 'comparação de valores, não necessariamente permissão; confirmar'))
    if f['code'] in ('TELEOLOGY_SPECULATIVE', 'AUTOMATIC_CONSEQUENCE', 'QUALIFIER_NOT_IN_TEXT', 'EXAMPLE_INVENTED_REQUIREMENT') \
            and f['section'] != 'exemplo_pratico':
        return 'PROVÁVEL PROBLEMA', f"mesmo padrão corrigido nas rodadas ({f.get('learned_from', '')[:90]})"
    if f['code'] == 'UNIVERSAL_CLAIM' and f['section'] == 'exemplo_pratico':
        snap = rec['source']['source_text_snapshot'].lower()
        stems = {w.lower()[:5] for w in E.words(f['sentence']) if len(w) >= 6}
        if sum(1 for st in stems if st in snap) >= 2:
            return 'PROVÁVEL FALSO POSITIVO', 'quantificador dentro de exemplo que reproduz situação prevista na Lei Seca'
    return 'INDETERMINADO', 'quantificador/expressão no núcleo; depende da leitura do dispositivo'


def _cites(rec, ctx):
    art = rec['target_id'].split(':')[1]
    out = []
    body = ' '.join(rec['content'][k] or '' for k in V.BODY)
    for m in CITE.finditer(body):
        if m.group(1):
            t = f"CF88:ART.{m.group(1)}" + (f":PAR.{re.sub(r'\D', '', m.group(2))}" if m.group(2) and m.group(2).startswith('§')
                                           else f":INC.{m.group(2)}" if m.group(2) else '')
        elif m.group(3):
            t = f'CF88:{art}:INC.{m.group(3)}'
        else:
            t = f'CF88:{art}:PAR.{m.group(4)}'
        if ctx.exists(t) and t != rec['target_id'] and t not in out and t in ctx.text:
            out.append(t)
    return out


def _warn_lines(row, ed_rows, lint_rows):
    out = [f"lint {w['code']} ({w['section']}: {w['detail'][:70]})" for w in lint_rows]
    out += [f"editorial_checks {e['code']} → {'resolvido: ' + e['resolution'][:90] if e['resolution'] else 'ABERTO'}" for e in ed_rows]
    return out or ['nenhum']


def calibration_packet(doc, act, ctx, chk, lint, catalog, known, plan):
    rows = {x['target_id']: x for x in doc['rows']}
    by_q = {q: [x for x in doc['rows'] if x['queue'] == q] for q in QUEUES}
    L = ['# T1 — CALIBRAÇÃO HUMANA DA TRIAGEM (Batch05, 31 pendentes)', '',
         f"`{doc['validator']}` · {doc['as_of']} · nada alterado: textos, status e versões intactos; autoaprovação OFF (LOW e MEDIUM). "
         'Objetivo: decidir se o roteamento A/B/C/D está correto. Não é aprovação.', '',
         '**Como responder:** por item, `CONFIRMAR` a fila ou `RECLASSIFICAR → <fila>` (com motivo curto). Na fila D, só confirmar se o '
         'roteamento está certo; a correção virá depois.', '',
         '**Classificação do validador na fila C** (regras determinísticas, a calibrar com a sua resposta):',
         '- PROVÁVEL FALSO POSITIVO: o mesmo termo já está justificado no editorial_checks, ou o quantificador está num exemplo que '
         'reproduz a Lei Seca;',
         '- PROVÁVEL PROBLEMA: mesmo padrão já corrigido nas rodadas (finalidade, consequência automática, condição inexistente, permissão '
         'sobre garantia);',
         '- INDETERMINADO: o restante.', '']
    # ---- A
    L += [f"## A — CLEAN_LOW ({len(by_q['A_CLEAN_LOW'])})", '']
    for x in by_q['A_CLEAN_LOW']:
        r, t = act[x['target_id']], x['target_id']
        c = r['content']
        fs = V.validate(r, ctx, catalog, known, lint.get(t, []), chk[t]['findings'])
        info = sorted({f['code'] for f in fs if f['severity'] == 'INFO'})
        L += [f"### `{t}` — {x['title']}", '', f"- risco {x['risk']} · {x['role']} · seleção: {r['granularity']['editorial_reason']}",
              f"- **O QUE DIZ:** {c['o_que_diz']}", f"- **O QUE SIGNIFICA:** {c['o_que_significa'].replace(chr(10), ' / ')}",
              f"- **EXEMPLO:** {c['exemplo_pratico']}", f"- **ATENÇÃO:** {c['atencao'] or '—'}",
              f"- **Camada externa:** {' / '.join(r['external_layer_notes']) or '—'}",
              f"- **Checks:** {_short_checks(chk[t]['findings'], lint.get(t, []))} · **v2:** sem HARD_FAIL/REVIEW (INFO: {', '.join(info) or '—'})",
              '- **Por que A:** LOW, nenhum alerta jurídico/editorial pendente. [ ] CONFIRMAR   [ ] RECLASSIFICAR → ____', '']
    # ---- B
    L += [f"## B — CLEAN_MEDIUM ({len(by_q['B_CLEAN_MEDIUM'])})", '']
    for x in by_q['B_CLEAN_MEDIUM']:
        r, t = act[x['target_id']], x['target_id']
        c = r['content']
        fs = V.validate(r, ctx, catalog, known, lint.get(t, []), chk[t]['findings'])
        info = sorted({f['code'] for f in fs if f['severity'] in ('INFO', 'EDITORIAL_AUTO_FIX_ELIGIBLE')})
        L += [f"**`{t}` — {x['title']}**", '',
              f"- Ponto central: {_cut(_first_sentence(c['o_que_diz']), 170)}",
              f"- Interpretação: {_cut(_first_sentence(c['o_que_significa']), 150)}",
              f"- Exemplo: {_cut(_first_sentence(c['exemplo_pratico']), 100)} · ATENÇÃO: {_cut(_first_sentence(c['atencao'] or '—'), 110)}",
              f"- Dep. externa: {'YES (' + ', '.join(x['external_dependency']) + ')' if x['external_dependency'] else 'NO'}"
              f" · checks: {_short_checks(chk[t]['findings'], lint.get(t, []))} · v2: limpo"]
        for f in fs:
            if f['code'] == 'NEAR_COPY_MICROFIX':
                sug = V.suggest_copy_microfix(c[f['section']], r['source']['source_text_snapshot'], 7)
                L.append(f"- Microajuste proposto (não aplicado): {f['section']}: \"{sug[0]}\" → \"{sug[1]}\"" if sug else
                         f"- Microajuste: NEAR_COPY em {f['section']}, sem proposta automática de palavra funcional")
        flagged = []
        for k, title in (('o_que_diz', 'O QUE DIZ'), ('o_que_significa', 'O QUE SIGNIFICA'), ('exemplo_pratico', 'EXEMPLO'), ('atencao', 'ATENÇÃO')):
            for para in (c[k] or '').split('\n'):
                hits = sorted({m.group(0).lower() for m in SENSITIVE.finditer(para)})
                if hits:
                    flagged.append(f"  - {title} [{', '.join(hits)}]: \"{para}\"")
        if flagged:
            L += ['- Parágrafo(s) com termo sensível:'] + flagged
        L += ['- [ ] CONFIRMAR B   [ ] RECLASSIFICAR → ____', '']
    # ---- C
    L += [f"## C — QUICK_REVIEW ({len(by_q['C_QUICK_REVIEW'])})", '', 'Reclassificar para A/B se o alerta for falso positivo; para D se houver problema jurídico.', '']
    for x in by_q['C_QUICK_REVIEW']:
        r, t = act[x['target_id']], x['target_id']
        fs = V.validate(r, ctx, catalog, known, lint.get(t, []), chk[t]['findings'])
        L += [f"**`{t}` — {x['title']} · {x['risk']}**", '']
        seen = set()
        for f in fs:
            if f['severity'] != 'REVIEW_REQUIRED' or (f['code'], f['sentence']) in seen:
                continue
            seen.add((f['code'], f['sentence']))
            before, after = _sent_ctx(r['content'][f['section']], f['sentence'])
            hint, why = calibration_hint(f, r, chk[t]['findings'])
            L += [f"- **{f['code']}** ({f['section']}, gatilho \"{f['match']}\"): \"**{f['sentence']}**\"",
                  f"  - antes: {('…' + before[-90:]) if before else '—'} · depois: {_cut(after, 90) if after else '—'}",
                  f"  - validador: **{hint}** — {_cut(why, 100)}" + ('' if hint.startswith('PROVÁVEL FALSO') else
                                                                      f" · ação: {_cut(QUICK_ACTION.get(f['code'], 'revisar o trecho'), 70)}")]
        L += [f"- Dep. externa: {', '.join(x['external_dependency']) if x['external_dependency'] else 'nenhuma'} · [ ] CONFIRMAR C   [ ] RECLASSIFICAR → ____", '']
    # ---- D
    L += [f"## D — FULL_HUMAN_REVIEW ({len(by_q['D_FULL_HUMAN_REVIEW'])}): pacote completo", '']
    for x in by_q['D_FULL_HUMAN_REVIEW']:
        r, t = act[x['target_id']], x['target_id']
        c = r['content']
        fs = V.validate(r, ctx, catalog, known, lint.get(t, []), chk[t]['findings'])
        L += [f"### `{t}` — {x['title']} · risco {x['risk']} · {x['role']}", '', '**Lei Seca**', '']
        L += [f"- `{ln.split(chr(9))[0]}`: {ln.split(chr(9), 1)[1]}" for ln in r['source']['source_text_snapshot'].split('\n')]
        cites = _cites(r, ctx)
        if cites:
            L += ['', '**Dispositivos citados pelo draft (runtime)**', ''] + [f"- `{d}`: {ctx.text[d]}" for d in cites]
        hl = {f['sentence'] for f in fs if f['severity'] == 'REVIEW_REQUIRED'}
        for k, title in (('o_que_diz', 'O QUE DIZ'), ('o_que_significa', 'O QUE SIGNIFICA'), ('exemplo_pratico', 'EXEMPLO PRÁTICO'), ('atencao', 'ATENÇÃO')):
            txt = c[k] or '—'
            for ds in _disp_sentences(txt):
                if any(h and h[:40] in ds for h in hl):
                    txt = txt.replace(ds, f'**⟦{ds}⟧**', 1)
            L += ['', f'**{title}**', '', txt.replace('\n', '\n\n')]
        L += ['', '**PALAVRAS DIFÍCEIS**', ''] + [f"- *{y['termo']}*: {y['explicacao']}" for y in c['palavras_dificeis']]
        notes = []
        for n in r['external_layer_notes']:
            notes.append(f'- **⟦{n}⟧**' if any(h and h[:40] in n for h in hl) else f'- {n}')
        L += ['', '**CAMADA EXTERNA**', ''] + (notes or ['—'])
        L += ['', f"**Warnings/checks:** {'; '.join(_warn_lines(x, chk[t]['findings'], lint.get(t, [])))}",
              f"**Validator v2:** " + '; '.join(f"{f['code']} ({f['severity']}{', ' + f['detail'] if f['detail'] else ''})"
                                                for f in fs if f['severity'] in ('REVIEW_REQUIRED', 'HARD_FAIL')),
              f"**Proveniência:** {_provenance_text(r)}",
              f"**Vigência (registro do projeto):** {plan_note(plan, t)}",
              f"**Motivo da fila D:** {x['reason']}",
              f"**Catálogo externo:** {', '.join(x['external_dependency'] or []) or 'nenhuma entrada vinculada'}", '',
              '**Calibração (evidência local):**', ''] + [f'- {n}' for n in D_NOTES.get(t, [])]
        L += ['', '- [ ] CONFIRMAR FULL_HUMAN_REVIEW   - [ ] RECLASSIFICAR → ____', '']
    L += ['## Fora deste pacote', '', '- Acervo anterior aprovado: 45 alertas registrados em `T1_LEGACY_AUDIT_BACKLOG.md` (não bloqueiam o Batch05; nada alterado).']
    return '\n'.join(L) + '\n'


def _provenance_text(r):
    p = V._provenance(r)
    return '; '.join(f"{x['source_type']} — {x['content'][:80]}" for x in p) if p else 'nenhuma registrada (item pendente)'


def plan_note(plan, t):
    art = t.split(':')[1].replace('ART.', 'ART')
    keys = [k for k in plan if k == art or k.startswith(art + '_')]
    return '; '.join(plan[k] for k in keys) or 'nenhuma observação específica registrada'


def legacy_backlog(reg):
    items = reg['detail']['prior_flagged']
    special = {'CF88:ART.7:INC.I', 'CF88:ART.5:INC.LXXI'}
    L = ['# T1_LEGACY_AUDIT_BACKLOG — acervo aprovado anterior (Batches 01–04 + pilotos)', '',
         f"`{reg['validator']}` · {len(items)} explicações aprovadas recebem algum alerta do validador v2. **Backlog de auditoria**: "
         'nenhuma foi alterada, nenhuma bloqueia o Batch05, nenhuma perdeu o status `HUMAN_APPROVED_T1`. Aprovadas antes do A6 '
         '(sem campo de proveniência).', '', '## Prioridade: afirmação sobre estado de lei sem fonte', '']
    for it in items:
        if it['target_id'] in special:
            for f in it['findings']:
                if f['code'] == 'LAW_STATUS_CLAIM':
                    L.append(f"- `{it['target_id']}` ({it['explanation_id']}): \"{f['sentence']}\" → {f['code']}; EXTERNAL_VERIFICATION_REQUIRED")
    L += ['', '## Todos os sinalizados', '', '| Target | Explicação | Alertas |', '|---|---|---|']
    for it in items:
        L.append(f"| `{it['target_id']}` | {it['explanation_id']} | " + '; '.join(f"{f['code']}: \"{f['match']}\"" for f in it['findings']) + ' |')
    return '\n'.join(L) + '\n', len(items)


def run(batch_dir):
    bd = Path(batch_dir)
    ctx = E.NormContext('CF88')
    catalog, known = V.load_catalog(), V.load_json(V.KNOWN)
    doc, act = triage(bd, ctx, catalog, known)
    report, pkg, full_chars = render(doc, act, ctx)
    doc['presentation_volume'] = dict(full_package_all_pending_chars=full_chars, queue_report_chars=len(report), queue_d_package_chars=len(pkg),
                                      reduction_pct=round(100 * (1 - (len(report) + len(pkg)) / full_chars), 1) if doc['rows'] else None)
    reg = regression(bd, ctx, catalog, known)
    spec = V.load_json(bd / 'BATCH_SPEC.json')
    chk = {r['target_id']: r for r in V.load_json(bd / 'EDITORIAL_CHECKS.json')['rows']}
    lint = {}
    for w in V.load_json(bd / spec['index_dir'] / 'ENTENDA_BUILD_MANIFEST.json')['warnings']:
        lint.setdefault(w['target_id'], []).append(w)
    plan = V.load_json(bd / 'BATCH05_TARGET_PLAN.json')['vigency_findings'] if (bd / 'BATCH05_TARGET_PLAN.json').is_file() else {}
    packet = calibration_packet(doc, act, ctx, chk, lint, catalog, known, plan)
    backlog, n_legacy = legacy_backlog(reg)
    doc['human_calibration_packet_generated'] = True
    doc['human_calibration_packet'] = dict(file='T1_PENDING_TRIAGE_HUMAN_CALIBRATION.md', chars=len(packet),
                                           reduction_vs_full_pct=round(100 * (1 - len(packet) / full_chars), 1) if doc['rows'] else None)
    doc['legacy_audit_backlog'] = dict(file='T1_LEGACY_AUDIT_BACKLOG.md', items=n_legacy, blocks_batch05=False)
    (bd / 'T1_PENDING_TRIAGE.json').write_bytes((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    (bd / 'T1_PENDING_TRIAGE_REPORT.md').write_bytes(report.encode('utf-8'))
    (bd / 'T1_QUEUE_D_FULL_REVIEW.md').write_bytes(pkg.encode('utf-8'))
    (bd / 'T1_PENDING_TRIAGE_HUMAN_CALIBRATION.md').write_bytes(packet.encode('utf-8'))
    (bd / 'T1_LEGACY_AUDIT_BACKLOG.md').write_bytes(backlog.encode('utf-8'))
    (bd / 'T1_VALIDATOR_V2_REGRESSION.json').write_bytes((json.dumps(reg, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    return doc, reg


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    d, g = run(sys.argv[1])
    print(json.dumps(dict(counts=d['counts'], volume=d['presentation_volume'],
                          regression={k: v for k, v in g.items() if k not in ('detail',)}), ensure_ascii=False, indent=1))
