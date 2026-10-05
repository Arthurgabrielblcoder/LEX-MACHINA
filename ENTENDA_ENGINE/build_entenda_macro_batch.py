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
import contextlib
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
import t1_second_pass as SP  # noqa: E402
import t1_validator_v2 as V  # noqa: E402
import t1_validator_v3 as V3  # noqa: E402

sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import status_errata as SE  # noqa: E402

KIND_PT = {'PARAGRAFO': 'paragrafo', 'PARAGRAFO_UNICO': 'paragrafo unico', 'INCISO': 'inciso', 'ALINEA': 'alinea', 'ITEM': 'item', 'CAPUT': 'caput'}
QUEUE_ORDER = ('E_HARD_FAIL', 'D_FULL_HUMAN_REVIEW', 'C_QUICK_REVIEW', 'B_CLEAN_MEDIUM', 'A_CLEAN_LOW')
RISK_ORDER = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
CX_ORDER = {'EXTERNAL': 0, 'STRUCTURED': 1, 'SIMPLE': 2}


HISTORY = 'history'   # preserved snapshots of earlier passes (e.g. history/pre_second_pass): versioned, never generated nor compared


class ErrataNormContext(E.NormContext):
    """NormContext with the target status errata of LEGAL_TARGET_ID applied (status_errata.py). The frozen status file, pinned by older
    artifacts (Batch06 manifest, DEVICE exports), is not rewritten; the errata sits next to it as <status>_ERRATA.json and is checked against
    its sha256 (fail closed)."""

    def __init__(self, norma_id, *a, **k):
        super().__init__(norma_id, *a, **k)
        self.status_errata, self.status_errata_file = {}, None
        st = self.ncfg.get('target_status')
        if st:
            base = self.base / st
            errata = base.with_name(base.stem + '_ERRATA.json')
            self.status, self.status_errata = SE.overlay(self.status, base.read_bytes(), errata)
            self.status_errata_file = errata.relative_to(self.base).as_posix() if errata.is_file() else None


def norm_context(norma_id):
    return ErrataNormContext(norma_id)


@contextlib.contextmanager
def errata_contexts():
    """During a macro build every NormContext (also the ones the shared selection and editorial modules create, whose code is pinned by the
    Batch06 manifest and is not edited) carries the status errata."""
    orig = E.NormContext
    E.NormContext = ErrataNormContext
    try:
        yield
    finally:
        E.NormContext = orig


JUDICIAL_REVIEW_RE = re.compile(r'\bVide\s+(ADIN|ADI|ADC|ADPF|ADO)\b[^;)]*', re.I)


class MacroBuildError(RuntimeError):
    pass


class MacroContext(BP.Context):
    """Macro-layer risk rules on top of t1_risk.assess (shared module untouched, Batch06 hashes preserved):
    JUDICIAL_REVIEW_* -- a target in the scope of the explanation carries a "Vide ADI/ADIN/ADC/ADPF/ADO" vigency annotation, i.e. the
    official text itself points to constitutional review of that wording. Second pass (t1_second_pass.py): the explanation is classified
    CONTEXT_ONLY (MEDIUM) or REQUIRED_FOR_CORRECTNESS (HIGH, full human review); without classification it is REQUIRED (fail closed).
    The second pass also applies the versioned transition evidence, the Lei Seca controversy-term rule, the parent/child consistency
    check and the quick-review routing of SECOND_PASS_INPUT.json."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        p = _load(self.bd / 'MACRO_SPEC.json')['packet_prefix']
        self.transition = SP.load_transition_evidence(self.bd / f'{p}_TRANSITION_EVIDENCE.json', ROOT)
        self.second = SP.load_input(self.bd / 'SECOND_PASS_INPUT.json')
        self.owned = set().union(*self.owners.values()) if self.owners else set()
        self.transition_seen, self.judicial_seen = set(), set()

    def validate(self, r, lint_rows=(), editorial_rows=()):
        fs = super().validate(r, lint_rows, editorial_rows)
        return fs + SP.quick_findings(r, self.second) + SP.parent_child_findings(r, self.ctx, self.owned)

    def judicial_hits(self, r):
        return sorted({f"{t.split(':', 1)[1]}: {m.group(0).strip()}" for t in R.scope_targets(r, self.ctx)
                       for ann in self.vigency.get(t, []) for m in [JUDICIAL_REVIEW_RE.search(ann)] if m})

    def assess(self, r, findings):
        a, cx = super().assess(r, findings)
        hits = self.judicial_hits(r)
        if 'TRANSITION_OR_TEMPORAL' in a['rules']:
            self.transition_seen.add(r['target_id'])
        if hits:
            self.judicial_seen.add(r['target_id'])
        return SP.refine(a, r, hits, self.transition, self.second), cx


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
        self.backlog = f'{self.p}_BACKLOG.md'


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


JURIS_NOTE_RE = re.compile(r'JURISPRUD[EÊ]NCIA', re.I)


def derived_jurisprudence_recommendations(ctx, expl, vig, seen):
    """Link recommendations derived from versioned evidence only (nothing filled from memory):
    - CANONICAL_VIGENCY_ANNOTATION: a "Vide ADI/ADIN/ADC/ADPF/ADO n" annotation of the canonical structural source on a target in the scope
      of the explanation -> desired_reference is the annotated identity;
    - DRAFT_EXTERNAL_LAYER_NOTE: the draft says, in its external layer, that the reading depends on case law that the Cloud cannot verify
      (EXTERNAL_VERIFICATION_REQUIRED or "tema da camada JURISPRUDENCIA") -> desired_reference stays IDENTIFICACAO_PENDENTE.
    local_identity is never guessed: the local curated sources decide READY_TO_LINK in production_batch.jurisprudence_recommendations_v2."""
    out = []
    for e in expl:
        tid = e['target_id']
        scope = [tid] + list(e.get('covered_targets', []))
        scope += [t for s0 in list(scope) for t in ctx.subtree(s0) if t != s0]
        idents = sorted({m.group(0).strip() for t in scope for a in vig.get(t, []) for m in [JUDICIAL_REVIEW_RE.search(a)] if m},
                        key=lambda x: (x.split()[1], x))
        for ident in idents:
            ref = ident.replace('Vide ', '', 1)
            if (tid, ref) not in seen:
                seen.add((tid, ref))
                out.append(dict(target_id=tid, desired_reference=ref, local_identity=None, subject_keywords=[],
                                purpose='controle de constitucionalidade anotado na fonte canonica sobre dispositivo do escopo da explicacao '
                                        '(CANONICAL_VIGENCY_ANNOTATION); resultado e alcance: EXTERNAL_VERIFICATION_REQUIRED'))
        notes = [n for n in e.get('external_layer_notes') or [] if JURIS_NOTE_RE.search(n) and not JUDICIAL_REVIEW_RE.search(n)]
        if notes and (tid, 'IDENTIFICACAO_PENDENTE') not in seen:
            seen.add((tid, 'IDENTIFICACAO_PENDENTE'))
            out.append(dict(target_id=tid, desired_reference='IDENTIFICACAO_PENDENTE', local_identity=None, subject_keywords=[],
                            purpose='DRAFT_EXTERNAL_LAYER_NOTE: ' + notes[0][:240]))
    return out


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
    targets = [t for a in arts for t in ctx.subtree(a) if ctx.effective_status(t) == 'CURRENT']
    vig, stats = VP.vigency_map(ctx, targets, ROOT / ms['canonical_structural_source'])
    juris = [r for x in built for r in _load(bd / 'drafts' / f"{nm.p}_{x}_DRAFTS.json").get('jurisprudence_recommendations', [])]
    juris += derived_jurisprudence_recommendations(ctx, expl, vig, {(r['target_id'], r['desired_reference']) for r in juris})
    sub_blocks = {k: [a for a in arts if sub_block_of(ms, ctx, a) == k] for k in built}
    spec = dict(norma_id=ms['norma_id'], batch_id=ms['batch_id'], report_schema=2, as_of_date=ms['as_of_date'], scope=arts,
                sub_blocks=sub_blocks, drafts=nm.drafts, reference_export=ms.get('reference_export'), batch_corpus=nm.corpus, index_dir='index',
                review_sheet=nm.sheet, prior_corpora=ms['prior_corpora'], soft_target=ms['soft_target'], hard_cap=ms['hard_cap'],
                soft_target_justification=ms.get('soft_target_justification'), reused=dict(sorted(reused.items())),
                no_separate_reasons=dict(sorted(no_sep.items(), key=lambda kv: ctx.order[kv[0]])),
                jurisprudence_recommendations=juris,
                packet_prefix=nm.p)
    if not spec['reference_export']:
        spec.pop('reference_export')
    _json(bd / 'BATCH_SPEC.json', spec)
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
    # second pass: every transition signal has versioned evidence, every evidence row is used, every "Vide ADI" scope is classified
    no_evidence = sorted(set(c.transition_seen) - set(c.transition)) if c.transition or c.second['judicial_review'] else []
    unused_evidence = sorted(set(c.transition) - set(c.records))
    unclassified = sorted(t for t in c.judicial_seen if t not in c.second['judicial_review']) if c.second['judicial_review'] else []
    ok = not (div or hard or approved_new or stale or no_evidence or unused_evidence or unclassified)
    return dict(engine_contract='PASS (production_batch.validate_corpus)', lei_seca_divergence=div, hard_fail=hard, new_not_pending=approved_new,
                stale=[s['target_id'] for s in stale], transition_without_evidence=no_evidence, transition_evidence_unused=unused_evidence,
                judicial_review_unclassified=unclassified, status='PASS' if ok else 'FAIL')


def old_content_scan(ctx, ms):
    """JUDICIAL_REVIEW_ANNOTATED applied to the ACTIVE records of the main and prior corpora (approved and pending): only registered."""
    recs = []
    for f in [f"ENTENDA_ENGINE/corpus/{ms['norma_id']}.entenda.jsonl"] + ms['prior_corpora']:
        recs += [(f, r) for r in E.load_corpus(ROOT / f) if r['status'] == 'ACTIVE']
    scope = {}
    for _, r in recs:
        s0 = [r['target_id']] + list(r['granularity'].get('covered_targets', []))
        scope[r['explanation_id']] = s0 + [t for x in s0 for t in ctx.subtree(x) if t != x]
    targets = sorted({t for v in scope.values() for t in v if ctx.exists(t)}, key=lambda t: ctx.order[t])
    vig, _ = VP.vigency_map(ctx, targets, ROOT / ms['canonical_structural_source'])
    hits = []
    for f, r in recs:
        ids = sorted({m.group(0) for t in scope[r['explanation_id']] for a in vig.get(t, []) for m in [JUDICIAL_REVIEW_RE.search(a)] if m})
        if ids:
            hits.append(dict(target_id=r['target_id'], explanation_id=r['explanation_id'], review_status=r['review_status'],
                             corpus=f.split('/')[-1], annotations=ids))
    hits.sort(key=lambda h: ctx.order[h['target_id']])
    return dict(records_checked=len(recs), by_review_status=dict(sorted(Counter(r['review_status'] for _, r in recs).items())), hits=hits)


def backlog(bd, ms, ctx, nm):
    inp = _load(bd / 'BACKLOG_INPUT.json') if (bd / 'BACKLOG_INPUT.json').is_file() else dict(items=[])
    scan = old_content_scan(ctx, ms)
    L = [f"# {nm.p} — BACKLOG (não corrigido nesta missão)", '', inp.get('policy', ''), '',
         '## Regra nova aplicada ao conteúdo antigo', '',
         f"`JUDICIAL_REVIEW_ANNOTATED` (anotação Vide ADI/ADIN/ADC/ADPF/ADO no escopo) aplicada a {scan['records_checked']} registros ACTIVE dos corpora anteriores "
         f"({', '.join(f'{k} {v}' for k, v in scan['by_review_status'].items())}). {len(scan['hits'])} registro(s) caem na regra; pela recalibração do segundo passe cada um precisa ser classificado "
         '`JUDICIAL_REVIEW_CONTEXT_ONLY` (MEDIUM) ou `JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS` (HIGH); sem classificação, a regra é REQUIRED (fail closed). '
         'Nenhum foi alterado nem reclassificado; a revisão fica para missão própria.', '',
         '| Target | Status | Corpus | Anotações |', '|---|---|---|---|']
    L += [f"| `{h['target_id']}` | {h['review_status']} | {h['corpus']} | {', '.join(h['annotations'])} |" for h in scan['hits']] or ['| — | — | — | — |']
    L += ['', '## Itens registrados durante a missão', '', '| ID | Tipo | Alvo | Detalhe | Ação sugerida |', '|---|---|---|---|---|']
    L += [f"| {i['id']} | {i['kind']} | `{i['target']}` | {i['detail']} | {i['action']} |" for i in inp['items']]
    (bd / nm.backlog).write_bytes(('\n'.join(L) + '\n').encode('utf-8'))
    return dict(old_content=dict(records_checked=scan['records_checked'], by_review_status=scan['by_review_status'], hits=len(scan['hits'])),
                items=len(inp['items']))


def build(bd):
    with errata_contexts():
        return _build(bd)


def _build(bd):
    bd = Path(bd).resolve()
    ms = _load(bd / 'MACRO_SPEC.json')
    nm = Names(ms)
    ctx = norm_context(ms['norma_id'])
    assemble(bd, ms, ctx, nm)
    for n in (nm.corpus, 'index/ENTENDA_BUILD_MANIFEST.json', 'index/ENTENDA_LOOKUP.IDX', 'index/ENTENDA_PAYLOAD.DAT'):
        (bd / n).unlink(missing_ok=True)   # none of the macro explanations was human-reviewed: the corpus is regenerated from the drafts
    sel = PB.run(bd)
    catalog, known, registry = V.load_catalog(), V.load_json(V.KNOWN), V3.load_registry()
    c = MacroContext(bd, ctx, catalog, known, registry, _load(bd / 'RELATIONS_PIN.json'))
    inp = _load(bd / 'EDITORIAL_INPUT.json')
    inp.update(schema_version=1, batch_id=ms['batch_id'], triage_sheet=nm.triage_sheet,
               risk_criteria=dict(classifier='ENTENDA_ENGINE/t1_risk.py::assess + complexity (validator v3)',
                                  LEGAL_RISK='HIGH: ' + '; '.join(R.LEGAL_HIGH) + '; JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS (camada macro: anotacao Vide ADI/ADIN/ADC/ADPF/ADO no escopo, classificada no segundo passe; CONTEXT_ONLY = MEDIUM)', level='o campo level e o LEGAL_RISK'),
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
    second = (bd / 'SECOND_PASS_INPUT.json').is_file()
    if second:
        jr = _load(bd / 'JURISPRUDENCE_LINK_RECOMMENDATIONS.json')['recommendations'] if (bd / 'JURISPRUDENCE_LINK_RECOMMENDATIONS.json').is_file() else []
        out[nm.packets['full']] = SP.full_d(doc, c, nm.p, jr)
        out[nm.packets['quick']] = SP.quick_c(doc, c, nm.p, BP.SAFE_FIX)
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
    rep = report(doc, sel, c, ms, nm)
    pre_f = bd / HISTORY / 'pre_second_pass' / f'{nm.p}_TRIAGE_PRE_SECOND_PASS.json'
    diag = bd / f'{nm.p}_D_SECOND_PASS_DIAGNOSTIC.md'
    if second:
        pre = _load(pre_f) if pre_f.is_file() else None
        log = SP.editorial_log(bd, nm.p, doc, c, pre)
        _json(bd / f'{nm.p}_SECOND_PASS_EDITORIAL_LOG.json', log)
        rep += '\n'.join(SP.report_section(doc, pre, log, (pre or {}).get('metrics', {}).get('presented_chars'))) + '\n'
        if doc['d_ratio'] > SECOND_PASS_D_LIMIT:
            diag.write_bytes(d_second_pass_diagnostic(doc, nm).encode('utf-8'))
        else:
            diag.unlink(missing_ok=True)
    (bd / nm.report).write_bytes(rep.encode('utf-8'))
    doc['backlog'] = backlog(bd, ms, ctx, nm)
    _json(bd / nm.triage, doc)
    manifest(bd, ms, nm, doc, sel)
    if doc['checks']['status'] != 'PASS':
        raise MacroBuildError(json.dumps(doc['checks'], ensure_ascii=False))
    return doc


SECOND_PASS_D_LIMIT = 0.2


def d_second_pass_diagnostic(doc, nm):
    xs = [x for x in doc['rows'] if x['queue'] == 'D_FULL_HUMAN_REVIEW']
    L = [f'# {nm.p} — DIAGNÓSTICO DE D APÓS O SEGUNDO PASSE', '',
         f"{len(xs)} de {len(doc['rows'])} itens em D ({100 * doc['d_ratio']:.1f}%), acima de {int(SECOND_PASS_D_LIMIT * 100)}%.", '', '## D por motivo', '']
    L += [f'- {k}: {v}' for k, v in doc['d_reasons'].items()]
    L += ['', '## Itens', ''] + [f"- `{x['target_id']}` — {'; '.join(x['legal_reasons'])}" for x in xs]
    return '\n'.join(L) + '\n'


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
    inputs = root_inputs(bd, ms) + sorted(str(p.relative_to(bd)) for p in (bd / 'drafts').glob('*.json'))
    generated = sorted(str(p.relative_to(bd)) for p in bd.rglob('*') if p.is_file() and str(p.relative_to(bd)) not in inputs
                       and p.name not in (nm.manifest, 'DETERMINISM_EVIDENCE.json') and p.relative_to(bd).parts[0] != HISTORY)
    history = sorted(str(p.relative_to(bd)) for p in (bd / HISTORY).rglob('*') if p.is_file()) if (bd / HISTORY).is_dir() else []
    ctx_errata = _status_errata_input(ms['norma_id'])
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
        inputs={p: sha(bd / p) for p in inputs}, files={p: sha(bd / p) for p in generated},
        **(dict(status_errata=ctx_errata) if ctx_errata else {}), **(dict(history={p: sha(bd / p) for p in history}) if history else {})))


def _status_errata_input(norma_id):
    ctx_cfg = json.loads((HERE / 'entenda_config.json').read_text(encoding='utf-8'))['norms'][norma_id]
    if not ctx_cfg.get('target_status'):
        return {}
    base = ROOT / ctx_cfg['target_status']
    p = base.with_name(base.stem + '_ERRATA.json')
    return {p.relative_to(ROOT).as_posix(): sha(p)} if p.is_file() else {}


def root_inputs(bd, ms):
    """Versioned editorial inputs at the batch root (besides drafts/ and history/)."""
    names = ('MACRO_SPEC.json', 'EDITORIAL_INPUT.json', 'RELATIONS_PIN.json', 'BACKLOG_INPUT.json', 'SECOND_PASS_INPUT.json',
             f"{ms['packet_prefix']}_TRANSITION_EVIDENCE.json")
    return [p for p in names if (Path(bd) / p).is_file()]


def determinism(bd, n=3):
    bd = Path(bd).resolve()
    ms = _load(bd / 'MACRO_SPEC.json')
    nm = Names(ms)
    inputs = root_inputs(bd, ms)
    runs = []
    with tempfile.TemporaryDirectory(prefix='macro_det_') as tmp:
        for i in range(n):
            td = Path(tmp) / f'run{i}' / bd.name
            shutil.copytree(bd / 'drafts', td / 'drafts')   # versioned drafts, critic logs and pass-1 inputs (drafts/pass1)
            for f in inputs:
                shutil.copy(bd / f, td / f)
            if (bd / HISTORY).is_dir():
                shutil.copytree(bd / HISTORY, td / HISTORY)   # versioned snapshots of earlier passes (read, never generated)
            build(td)
            runs.append({str(p.relative_to(td)): sha(p) for p in td.rglob('*') if p.is_file() and p.relative_to(td).parts[0] != HISTORY})
    inplace = {str(p.relative_to(bd)): sha(p) for p in bd.rglob('*') if p.is_file() and p.name != 'DETERMINISM_EVIDENCE.json'
               and p.relative_to(bd).parts[0] != HISTORY}
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
