"""Generic, deterministic builder of an ENTENDA macro batch (a range of articles split into sub-blocks), from versioned content only.

Reusable for the next CF ranges and other norms. The batch directory holds the editorial inputs:
  MACRO_SPEC.json                    norm, batch id, packet prefix, sub-blocks {X: {start, end}}, sub_blocks_built, caps, prior corpora,
                                     canonical structural source (vigency annotations)
  drafts/<P>_<X>_DRAFTS.json         per sub-block: article_notes {article: what the overview covers} + explanations (T1 drafts)
  drafts/<P>_<X>_CRITIC_LOG.json     per sub-block: corrections made by the critic pass (before/after, reason)
  EDITORIAL_INPUT.json               fact rules, technical terms and editor resolutions of editorial_checks
  RELATIONS_PIN.json                 Relations Engine evidence pinned for the batch (sources may be empty)
Generated (byte-identical across builds): BATCH_SPEC.json, BATCH_<NN>_DRAFTS.json, BATCH<NN>_TARGET_PLAN.json, EDITORIAL_REVIEW_INPUT.json,
corpus, index/, SELECTION_REPORT.json, JURISPRUDENCE_LINK_RECOMMENDATIONS.json, review sheet, EDITORIAL_CHECKS.json, risk triage sheet,
<P>_TRIAGE.json, <P>_COMPACT_AB_REVIEW.md, <P>_QUICK_C_REVIEW.md, <P>_FULL_D_REVIEW.md, <P>_HARD_FAIL_REPORT.md,
<P>_D_ESCALATION_DIAGNOSTIC.md (only above 40% D; the D package is still produced), <P>_HUMAN_REVIEW_PRIORITY.md, MICRO_ADJUSTMENTS_LOG.json,
<P>_SCALE_REPORT.md, <P>_<X>_CHECKPOINT.json per built sub-block, <P>_MANIFEST.json.
Nothing is approved: every new explanation is PENDING_HUMAN_REVIEW; AUTO_APPROVE_* and MICROAUTO_APPLY stay OFF.
Usage:
  python build_entenda_macro_batch.py derived/production_batch_07_macro [--determinism 3]
"""
import hashlib
import json
import re
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import editorial_checks as EC  # noqa: E402
import entenda_engine as E  # noqa: E402
import entenda_vigency_plan as VP  # noqa: E402
import production_batch as PB  # noqa: E402
import t1_batch_packets as BP  # noqa: E402
import t1_risk as R  # noqa: E402
import t1_validator_v2 as V  # noqa: E402
import t1_validator_v3 as V3  # noqa: E402

KIND_PT = {'PARAGRAFO': 'paragrafo', 'PARAGRAFO_UNICO': 'paragrafo unico', 'INCISO': 'inciso', 'ALINEA': 'alinea', 'ITEM': 'item', 'CAPUT': 'caput'}
QUEUE_ORDER = ('E_HARD_FAIL', 'D_FULL_HUMAN_REVIEW', 'C_QUICK_REVIEW', 'B_CLEAN_MEDIUM', 'A_CLEAN_LOW')
RISK_ORDER = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
CX_ORDER = {'EXTERNAL': 0, 'STRUCTURED': 1, 'SIMPLE': 2}


JUDICIAL_REVIEW_RE = re.compile(r'\bVide\s+(ADIN|ADI|ADC|ADPF|ADO)\b[^;)]*', re.I)


class MacroBuildError(RuntimeError):
    pass


class MacroContext(BP.Context):
    """Macro-layer risk rule on top of t1_risk.assess (shared module untouched, Batch06 hashes preserved):
    JUDICIAL_REVIEW_ANNOTATED -- a target in the scope of the explanation carries a "Vide ADI/ADIN/ADC/ADPF/ADO" vigency annotation, i.e.
    the official text itself points to constitutional review of that wording; the literal reading may not be the current one, so the
    explanation is LEGAL_RISK HIGH and goes to full human review with the external evidence status of the decision."""

    def assess(self, r, findings):
        a, cx = super().assess(r, findings)
        hits = sorted({f"{t.split(':', 1)[1]}: {m.group(0).strip()}" for t in R.scope_targets(r, self.ctx)
                       for ann in self.vigency.get(t, []) for m in [JUDICIAL_REVIEW_RE.search(ann)] if m})
        if not hits:
            return a, cx
        reason = 'JUDICIAL_REVIEW_ANNOTATED: ' + '; '.join(hits[:3]) + (f' (+{len(hits) - 3})' if len(hits) > 3 else '')
        a = dict(a)
        if a['level'] != 'HIGH':
            a['secondary'] = list(a['reasons']) if a['level'] == 'MEDIUM' else []
            a['rules'], a['reasons'] = [], []
        a['level'] = 'HIGH'
        a['rules'] = list(a['rules']) + ['JUDICIAL_REVIEW_ANNOTATED']
        a['reasons'] = list(a['reasons']) + [reason]
        return a, cx


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_lf(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def _json(p, doc):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_bytes((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))


def _load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def _n(x):
    return f'{x:,}'.replace(',', '.')


class Names:
    def __init__(self, ms):
        self.p = ms['packet_prefix']
        self.nn = re.search(r'(\d+)$', ms['batch_id']).group(1)
        self.drafts = f'BATCH_{self.nn}_DRAFTS.json'
        self.plan = f'BATCH{self.nn}_TARGET_PLAN.json'
        self.corpus = f"{ms['norma_id']}_MACRO_{self.nn}.entenda.jsonl"
        self.sheet = f'REVIEW_{self.p}.md'
        self.triage_sheet = f'REVIEW_{self.p}_RISK_TRIAGE.md'
        self.triage = f'{self.p}_TRIAGE.json'
        self.packets = dict(compact=f'{self.p}_COMPACT_AB_REVIEW.md', quick=f'{self.p}_QUICK_C_REVIEW.md', full=f'{self.p}_FULL_D_REVIEW.md',
                            hard=f'{self.p}_HARD_FAIL_REPORT.md', diagnostic=f'{self.p}_D_ESCALATION_DIAGNOSTIC.md')
        self.priority = f'{self.p}_HUMAN_REVIEW_PRIORITY.md'
        self.report = f'{self.p}_SCALE_REPORT.md'
        self.manifest = f'{self.p}_MANIFEST.json'


def article_targets(ctx, norma, start, end):
    """Article targets numbered start..end, with lettered articles (76, 103-A, 103-B ...), in structural order."""
    out = []
    for n in range(start, end + 1):
        for suf in [''] + [f'-{x}' for x in 'ABCDEFGHIJ']:
            a = f'{norma}:ART.{n}{suf}'
            if ctx.exists(a):
                out.append(a)
    return sorted(out, key=lambda t: ctx.order[t])


def sub_block_of(ms, ctx, art):
    n = int(re.match(r'.*:ART\.(\d+)', art).group(1))
    return next(k for k, v in ms['sub_blocks'].items() if v['start'] <= n <= v['end'])


def assemble(bd, ms, ctx, nm):
    """Merges the built sub-blocks into the generated drafts, spec and vigency plan."""
    built = ms['sub_blocks_built']
    arts, notes, expl, authoring = [], {}, [], None
    for x in built:
        sb = ms['sub_blocks'][x]
        arts += article_targets(ctx, ms['norma_id'], sb['start'], sb['end'])
        d = _load(bd / 'drafts' / f"{nm.p}_{x}_DRAFTS.json")
        notes.update(d['article_notes'])
        expl += d['explanations']
    main = [r for r in E.load_corpus(HERE / 'corpus' / f"{ms['norma_id']}.entenda.jsonl") if r['status'] == 'ACTIVE']
    in_scope = lambda t: any(t == a or t.startswith(a + ':') for a in arts)  # noqa: E731
    reused = {r['target_id']: f"Explicacao aprovada anteriormente (HUMAN_APPROVED_T1, {r['explanation_id']}); reutilizada sem alteracao."
              for r in main if in_scope(r['target_id'])}
    own = {e['target_id'] for e in expl} | set(reused)
    covered = {c for e in expl for c in e.get('covered_targets', [])}
    missing_overview = [a for a in arts if a not in own and ctx.effective_status(a) == 'CURRENT']
    if missing_overview:
        raise MacroBuildError(f'ARTICLE_WITHOUT_OVERVIEW {missing_overview}')
    no_sep = {}
    for a in arts:
        for t in ctx.subtree(a):
            if t in own or t in covered or ctx.effective_status(t) != 'CURRENT' or ctx.kind(t) in ('CAPUT', 'ARTIGO'):
                continue
            note = notes.get(a)
            if not note:
                raise MacroBuildError(f'ARTICLE_NOTE_MISSING {a}')
            no_sep[t] = f"{KIND_PT.get(ctx.kind(t), ctx.kind(t).lower())} sem explicacao propria: {note}"
    drafts = dict(norma_id=ms['norma_id'], batch_id=ms['batch_id'], template_version=ms['template_version'], prompt_version=ms['prompt_version'],
                  review_status='PENDING_HUMAN_REVIEW', authoring=ms['authoring'], explanations=expl)
    _json(bd / nm.drafts, drafts)
    sub_blocks = {k: [a for a in arts if sub_block_of(ms, ctx, a) == k] for k in built}
    spec = dict(norma_id=ms['norma_id'], batch_id=ms['batch_id'], report_schema=2, as_of_date=ms['as_of_date'], scope=arts,
                sub_blocks=sub_blocks, drafts=nm.drafts, reference_export=ms.get('reference_export'), batch_corpus=nm.corpus, index_dir='index',
                review_sheet=nm.sheet, prior_corpora=ms['prior_corpora'], soft_target=ms['soft_target'], hard_cap=ms['hard_cap'],
                soft_target_justification=ms.get('soft_target_justification'), reused=dict(sorted(reused.items())),
                no_separate_reasons=dict(sorted(no_sep.items(), key=lambda kv: ctx.order[kv[0]])),
                jurisprudence_recommendations=[r for x in built for r in _load(bd / 'drafts' / f"{nm.p}_{x}_DRAFTS.json").get('jurisprudence_recommendations', [])],
                packet_prefix=nm.p)
    if not spec['reference_export']:
        spec.pop('reference_export')
    _json(bd / 'BATCH_SPEC.json', spec)
    targets = [t for a in arts for t in ctx.subtree(a) if ctx.effective_status(t) == 'CURRENT']
    vig, stats = VP.vigency_map(ctx, targets, ROOT / ms['canonical_structural_source'])
    _json(bd / nm.plan, dict(schema_version=1, batch_id=ms['batch_id'], norma_id=ms['norma_id'], as_of=ms['as_of_date'], scope=arts,
                             canonical_structural_source=ms['canonical_structural_source'], method='entenda_vigency_plan.vigency_map',
                             stats=stats, sub_blocks=sub_blocks, vigency_by_target=vig, reused_pilots=sorted(reused),
                             status='DRAFT_AND_TRIAGE (sem aprovacao humana nesta missao)'))
    return spec


def _retitle(text, nm):
    return re.sub(r'^# BATCH\d+ ', f'# {nm.p} ', text, count=1)


def priority(doc, c, nm):
    rows = sorted(doc['rows'], key=lambda x: (QUEUE_ORDER.index(x['queue']), RISK_ORDER[x['legal_risk']], CX_ORDER[x['verification_complexity']],
                                              c.ctx.order[x['target_id']]))
    L = [f"# {nm.p} — PRIORIDADE DA REVISÃO HUMANA", '',
         f"Lote `{doc['batch_id']}` · {len(rows)} explicações novas, todas `PENDING_HUMAN_REVIEW`. Ordem: fila (E, D, C, B, A), risco jurídico, "
         'complexidade de verificação e posição no texto. Ler de cima para baixo; o pacote de cada fila traz o detalhe.', '',
         '| # | Fila | Risco | Complexidade | Target | Título | Motivo principal |', '|---|---|---|---|---|---|---|']
    for i, x in enumerate(rows, 1):
        why = (x['legal_rules'] and ', '.join(x['legal_rules'])) or BP._cut(x['reason'], 90)
        L.append(f"| {i} | {x['queue'][0]} | {x['legal_risk']} | {x['verification_complexity']} | `{x['target_id']}` | {x['title']} | {why} |")
    return '\n'.join(L) + '\n'


def slice_stats(doc, sel, spec, articles):
    """Counts for a set of articles (a sub-block checkpoint)."""
    inart = lambda t: any(t == a or t.startswith(a + ':') for a in articles)  # noqa: E731
    rows = [x for x in doc['rows'] if inart(x['target_id'])]
    srows = [r for r in sel['selection'] if inart(r['target_id'])]
    cur = [r for r in srows if r['status'] == 'CURRENT']
    return dict(articles=len(articles), targets_evaluated=len(srows), targets_current=len(cur),
                select=sum(1 for r in cur if r['classification'] in PB.SELECTED), skip=sum(1 for r in cur if r['classification'] == 'NO_SEPARATE_EXPLANATION'),
                excluded=dict(Counter(r['classification'] for r in srows if r['classification'].startswith('EXCLUDED'))),
                new_explanations=len(rows), reused=sum(1 for r in cur if r.get('explanation_source') == 'PILOT_T1_APPROVED'),
                roles=dict(sorted(Counter(x['role'] for x in rows).items())),
                legal_risk={k: sum(1 for x in rows if x['legal_risk'] == k) for k in ('LOW', 'MEDIUM', 'HIGH')},
                verification_complexity={k: sum(1 for x in rows if x['verification_complexity'] == k) for k in ('SIMPLE', 'STRUCTURED', 'EXTERNAL')},
                queues={q: sum(1 for x in rows if x['queue'] == q) for q in BP.QUEUES},
                jurisprudence=dict(sorted(Counter(x['jurisprudence'] for x in rows).items())))


def checks(c, doc):
    """Structural checks of the build: engine contract (already enforced by production_batch), Lei Seca divergence, hard fails, status."""
    rec = list(c.records.values())
    div = [r['target_id'] for r in rec if r['source']['source_text_snapshot'] != c.ctx.snapshot(r['target_id'], r['granularity'].get('covered_targets', []))]
    hard = [x['target_id'] for x in doc['rows'] if x['queue'] == 'E_HARD_FAIL']
    approved_new = [r['target_id'] for r in rec if r['review_status'] != 'PENDING_HUMAN_REVIEW']
    stale = [s for s in E.stale_report(rec, c.ctx) if s['state'] != 'FRESH']
    ok = not (div or hard or approved_new or stale)
    return dict(engine_contract='PASS (production_batch.validate_corpus)', lei_seca_divergence=div, hard_fail=hard, new_not_pending=approved_new,
                stale=[s['target_id'] for s in stale], status='PASS' if ok else 'FAIL')


def build(bd):
    bd = Path(bd).resolve()
    ms = _load(bd / 'MACRO_SPEC.json')
    nm = Names(ms)
    ctx = E.NormContext(ms['norma_id'])
    assemble(bd, ms, ctx, nm)
    for n in (nm.corpus, 'index/ENTENDA_BUILD_MANIFEST.json', 'index/ENTENDA_LOOKUP.IDX', 'index/ENTENDA_PAYLOAD.DAT'):
        (bd / n).unlink(missing_ok=True)   # none of the macro explanations was human-reviewed: the corpus is regenerated from the drafts
    sel = PB.run(bd)
    catalog, known, registry = V.load_catalog(), V.load_json(V.KNOWN), V3.load_registry()
    c = MacroContext(bd, ctx, catalog, known, registry, _load(bd / 'RELATIONS_PIN.json'))
    inp = _load(bd / 'EDITORIAL_INPUT.json')
    inp.update(schema_version=1, batch_id=ms['batch_id'], triage_sheet=nm.triage_sheet,
               risk_criteria=dict(classifier='ENTENDA_ENGINE/t1_risk.py::assess + complexity (validator v3)',
                                  LEGAL_RISK='HIGH: ' + '; '.join(R.LEGAL_HIGH) + '; JUDICIAL_REVIEW_ANNOTATED (camada macro: anotacao Vide ADI/ADIN/ADC/ADPF/ADO no escopo)', level='o campo level e o LEGAL_RISK'),
               risk=BP.risk_input(c))
    _json(bd / 'EDITORIAL_REVIEW_INPUT.json', dict(sorted(inp.items())))
    EC.run(bd)
    doc = BP.triage(c)
    files, full_generated = BP.packets(doc, c)
    out = {}
    for k, v in files.items():
        key = next(n for n, suffix in (('compact', '_COMPACT_CLEAN_REVIEW.md'), ('quick', '_QUICK_REVIEW.md'), ('full', '_FULL_HUMAN_REVIEW.md'),
                                       ('hard', '_HARD_FAIL_REPORT.md'), ('diagnostic', '_D_ESCALATION_DIAGNOSTIC.md')) if k.endswith(suffix))
        out[nm.packets[key]] = _retitle(v, nm)
    if not full_generated:                                     # macro batches always produce the D package; the diagnostic is added
        out[nm.packets['full']] = _retitle(BP.full(doc, c), nm)
    for n in nm.packets.values():
        if n not in out:
            (bd / n).unlink(missing_ok=True)
    out[nm.priority] = priority(doc, c, nm)
    doc['metrics'] = BP.metrics(doc, c, out)
    doc['d_ratio'] = round(doc['counts']['D_FULL_HUMAN_REVIEW'] / len(doc['rows']), 3) if doc['rows'] else 0
    doc['d_escalation_diagnostic'] = nm.packets['diagnostic'] in out
    micro = BP.micro_auto(doc, c.cfg)
    doc['micro_adjustments'] = dict(applied=micro['applied'], eligible=micro['eligible'], microauto_apply=micro['microauto_apply'])
    doc['human_approved_t1_granted'] = 0
    doc['validator_limits'] = V3.LIMITS
    critic = {x: _load(bd / 'drafts' / f"{nm.p}_{x}_CRITIC_LOG.json") for x in ms['sub_blocks_built'] if (bd / 'drafts' / f"{nm.p}_{x}_CRITIC_LOG.json").is_file()}
    doc['critic'] = {x: dict(corrections=len(v['corrections']), by_category=dict(sorted(Counter(e['category'] for e in v['corrections']).items())))
                     for x, v in critic.items()}
    doc['checks'] = checks(c, doc)
    for name, text in out.items():
        (bd / name).write_bytes(text.encode('utf-8'))
    _json(bd / 'MICRO_ADJUSTMENTS_LOG.json', micro)
    spec = _load(bd / 'BATCH_SPEC.json')
    for x in ms['sub_blocks']:
        cp = bd / f'{nm.p}_{x}_CHECKPOINT.json'
        if x not in ms['sub_blocks_built']:
            cp.unlink(missing_ok=True)
            continue
        st = slice_stats(doc, sel, spec, spec['sub_blocks'][x])
        _json(cp, dict(schema_version=1, batch_id=ms['batch_id'], sub_block=f"{ms['sub_blocks'][x]['name']}",
                       articles_range=f"{ms['sub_blocks'][x]['start']}-{ms['sub_blocks'][x]['end']}", stats=st,
                       critic=doc['critic'].get(x, dict(corrections=0, by_category={})),
                       checks=dict(doc['checks'], scope='lote acumulado ate este sub-bloco'),
                       determinism='ver DETERMINISM_EVIDENCE.json (builds completos comparados byte a byte)',
                       human_approved_t1_granted=0, status=doc['checks']['status']))
    _json(bd / nm.triage, doc)
    (bd / nm.report).write_bytes(report(doc, sel, c, ms, nm).encode('utf-8'))
    manifest(bd, ms, nm, doc, sel)
    if doc['checks']['status'] != 'PASS':
        raise MacroBuildError(json.dumps(doc['checks'], ensure_ascii=False))
    return doc


def report(doc, sel, c, ms, nm):
    s, m = sel['summary'], doc['metrics']
    rows = doc['rows']
    L = [f"# {ms['batch_id']} — relatório de escala", '',
         f"Data de referência: {ms['as_of_date']} · gerado por `ENTENDA_ENGINE/build_entenda_macro_batch.py` (determinístico, só conteúdo versionado) · "
         '**0 HUMAN_APPROVED_T1 novos**: todas as explicações novas estão `PENDING_HUMAN_REVIEW`; AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF.', '',
         f"Sub-blocos construídos: {', '.join(ms['sub_blocks'][x]['name'] + ' (arts. ' + str(ms['sub_blocks'][x]['start']) + '–' + str(ms['sub_blocks'][x]['end']) + ')' for x in ms['sub_blocks_built'])}.", '',
         '## Seleção', '', '| | |', '|---|---|',
         f"| Artigos | {len(doc_spec(c)['scope'])} |",
         f"| Targets analisados | {s['targets_evaluated']} ({s['targets_current']} vigentes; excluídos: "
         + ', '.join(f'{k} {v}' for k, v in sorted(s['by_classification'].items()) if k.startswith('EXCLUDED')) + ') |',
         f"| SELECT | {s['selected']} = {s['new_explanations']} novas + {s['reused_from_pilot']} reutilizada(s) já aprovada(s) |",
         f"| SKIP | {s['by_classification'].get('NO_SEPARATE_EXPLANATION', 0)} (todos com motivo e explicação que os cobre) |",
         f"| Papéis das novas | {', '.join(f'{k} {v}' for k, v in sorted(Counter(x['role'] for x in rows).items()))} |", '',
         '## Por sub-bloco', '', '| Sub-bloco | Artigos | Vigentes | SELECT | SKIP | Novas | LOW/MED/HIGH | A/B/C/D/E | Correções do critic |',
         '|---|---|---|---|---|---|---|---|---|']
    spec = doc_spec(c)
    for x in ms['sub_blocks_built']:
        st = slice_stats(doc, sel, spec, spec['sub_blocks'][x])
        q = st['queues']
        L.append(f"| {ms['sub_blocks'][x]['name']} | {st['articles']} | {st['targets_current']} | {st['select']} | {st['skip']} | {st['new_explanations']} | "
                 f"{st['legal_risk']['LOW']}/{st['legal_risk']['MEDIUM']}/{st['legal_risk']['HIGH']} | "
                 f"{q['A_CLEAN_LOW']}/{q['B_CLEAN_MEDIUM']}/{q['C_QUICK_REVIEW']}/{q['D_FULL_HUMAN_REVIEW']}/{q['E_HARD_FAIL']} | "
                 f"{doc['critic'].get(x, {}).get('corrections', 0)} |")
    L += ['', '## Dois eixos e filas', '', '| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |', '|---|---|---|---|---|']
    for a, b in zip(('LOW', 'MEDIUM', 'HIGH'), ('SIMPLE', 'STRUCTURED', 'EXTERNAL')):
        L.append(f"| {a} | {doc['legal_risk_counts'].get(a, 0)} | | {b} | {doc['complexity_counts'].get(b, 0)} |")
    L += ['', '| Fila | Itens |', '|---|---|'] + [f"| {q} | {doc['counts'][q]} |" for q in BP.QUEUES]
    L += ['', f"D = {doc['d_ratio'] * 100:.1f}% das novas" + (' — acima de 40%: ver diagnóstico de escalonamento.' if doc['d_escalation_diagnostic'] else '.'),
          f"Jurisprudência: {', '.join(f'{k} {v}' for k, v in sorted(doc['jurisprudence_counts'].items()))}.", '',
          '## Motivos dos D', ''] + [f"- {k}: {v}" for k, v in doc['d_reasons'].items()]
    L += ['', '## Achados REVIEW_REQUIRED', ''] + ([f"- {k}: {v}" for k, v in doc['finding_counts'].items()] or ['- nenhum'])
    L += ['', '## Dependências externas', '']
    ext = [x for x in rows if x['external_dependency'] and any(not d.startswith('JURISPRUD') for d in x['external_dependency'])]
    L += [f"- `{x['target_id']}`: {', '.join(x['external_dependency'])}" + (f" · resolver {x['external_resolution']['status']}" if x.get('external_resolution') else '')
          for x in ext] or ['- nenhuma além da camada de jurisprudência']
    L += ['', '## Volume para o humano', '', '| Métrica | Caracteres |', '|---|---|',
          f"| Rascunhos (5 seções + glossário) | {_n(m['total_draft_chars'])} |",
          f"| Modelo antigo (pacote completo de todos os itens) | {_n(m['old_model_full_package_chars'])} |",
          f"| **Apresentado ao humano (pacotes + prioridade)** | **{_n(m['presented_chars'])}** |"]
    L += [f"| — {k} | {_n(v)} |" for k, v in m['presented_by_file'].items()]
    L += [f"| Redução vs. modelo antigo | {_n(m['reduction_abs'])} ({m['reduction_pct']}%) |", '',
          '## Checks estruturais', '', f"- {doc['checks']['status']}: contrato do motor, Lei Seca idêntica ao runtime em todos os registros, "
          f"0 HARD_FAIL, 0 aprovado novo, 0 STALE.", '',
          '## Limites do validador', ''] + [f'- {x}' for x in V3.LIMITS]
    return '\n'.join(L) + '\n'


def doc_spec(c):
    return c.spec


def manifest(bd, ms, nm, doc, sel):
    inputs = ['MACRO_SPEC.json', 'EDITORIAL_INPUT.json', 'RELATIONS_PIN.json'] + sorted(str(p.relative_to(bd)) for p in (bd / 'drafts').glob('*.json'))
    generated = sorted(str(p.relative_to(bd)) for p in bd.rglob('*') if p.is_file() and str(p.relative_to(bd)) not in inputs
                       and p.name not in (nm.manifest, 'DETERMINISM_EVIDENCE.json'))
    _json(bd / nm.manifest, dict(
        schema_version=1, batch_id=ms['batch_id'], as_of=ms['as_of_date'], status='CANDIDATE: 0 HUMAN_APPROVED_T1; nada aprovado',
        builder='ENTENDA_ENGINE/build_entenda_macro_batch.py', validator=doc['validator'], sub_blocks_built=ms['sub_blocks_built'],
        selection=dict(targets_evaluated=sel['summary']['targets_evaluated'], current=sel['summary']['targets_current'], selected=sel['summary']['selected'],
                       new=sel['summary']['new_explanations'], reused=sel['summary']['reused_from_pilot'],
                       skip=sel['summary']['by_classification'].get('NO_SEPARATE_EXPLANATION', 0)),
        queues=doc['counts'], legal_risk=doc['legal_risk_counts'], verification_complexity=doc['complexity_counts'], metrics=doc['metrics'],
        code_sha256_lf={p: sha_lf(HERE / p) for p in ('build_entenda_macro_batch.py', 'entenda_vigency_plan.py', 't1_batch_packets.py', 't1_risk.py',
                                                      't1_validator_v3.py', 't1_validator_v2.py', 't1_triage.py', 'editorial_checks.py',
                                                      'production_batch.py', 'entenda_engine.py')},
        inputs={p: sha(bd / p) for p in inputs}, files={p: sha(bd / p) for p in generated}))


def determinism(bd, n=3):
    bd = Path(bd).resolve()
    ms = _load(bd / 'MACRO_SPEC.json')
    nm = Names(ms)
    inputs = ['MACRO_SPEC.json', 'EDITORIAL_INPUT.json', 'RELATIONS_PIN.json']
    runs = []
    with tempfile.TemporaryDirectory(prefix='macro_det_') as tmp:
        for i in range(n):
            td = Path(tmp) / f'run{i}' / bd.name
            (td / 'drafts').mkdir(parents=True)
            for f in inputs:
                shutil.copy(bd / f, td / f)
            for f in (bd / 'drafts').glob('*.json'):
                shutil.copy(f, td / 'drafts' / f.name)
            build(td)
            runs.append({str(p.relative_to(td)): sha(p) for p in td.rglob('*') if p.is_file()})
    inplace = {str(p.relative_to(bd)): sha(p) for p in bd.rglob('*') if p.is_file() and p.name != 'DETERMINISM_EVIDENCE.json'}
    differing = sorted({f for r in runs for f in set(r) | set(inplace) if r.get(f) != inplace.get(f)})
    ev = dict(schema_version=1, batch_id=ms['batch_id'], runs=n, byte_identical=not differing, differing_files=differing, files=len(inplace),
              sha256=dict(sorted(inplace.items())), sub_blocks_built=ms['sub_blocks_built'],
              procedure=f'{n} builds completos em copias temporarias das entradas versionadas, comparados entre si e com o build no lugar')
    _json(bd / 'DETERMINISM_EVIDENCE.json', ev)
    return ev


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    target = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else HERE / 'derived/production_batch_07_macro'
    d = build(target)
    out = dict(counts=d['counts'], legal_risk=d['legal_risk_counts'], complexity=d['complexity_counts'], d_reasons=d['d_reasons'],
               findings=d['finding_counts'], metrics={k: v for k, v in d['metrics'].items() if k != 'presented_by_file'}, checks=d['checks']['status'])
    if '--determinism' in sys.argv:
        ev = determinism(target, int(sys.argv[sys.argv.index('--determinism') + 1]))
        out['determinism'] = dict(runs=ev['runs'], byte_identical=ev['byte_identical'], differing=ev['differing_files'])
    print(json.dumps(out, ensure_ascii=False, indent=1))
