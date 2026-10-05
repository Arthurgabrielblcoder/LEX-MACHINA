"""Deterministic builder of an ENTENDA macro batch configurable by norm, segment (namespace), structural range/list and sub-blocks.

Generalizes build_entenda_macro_batch.py (Macro07, CF88 article ranges) without changing it: that module and the shared engine modules
are hash-pinned by the Macro07/Batch06 manifests, so this module imports and reuses them. What is new:
  * sub-blocks name their segment: {"namespace": "ADCT", "start": 1, "end": 30} or {"namespace": "CF88", "articles": [...]};
  * the batch may declare a text profile (MACRO_SPEC.entenda_config, e.g. profiles/CF88_OFFICIAL_RUNTIME: ADCT read from the official
    runtime; see entenda_text_profile.py); every context of the build uses it;
  * article decisions (MACRO08-style TEMPORAL_INPUT): an article may be skipped as a whole (SKIP_EXHAUSTED_TRANSITION,
    SKIP_APPROVED_PILOT_LEGACY_MODEL ...) with a reason; it is kept, with all its targets, in <P>_SKIP_REGISTER.json;
  * temporal layer (editorial, auxiliary; the global legal status is not reclassified): OPERATIVE_CURRENT, OPERATIVE_TRANSITION,
    EFFECT_EXHAUSTED, REVOKED, HISTORICAL_ONLY, FUTURE_TRIGGER, PARTIALLY_OPERATIVE, EXTERNAL_STATUS_REQUIRED, each with provenance;
    written to <P>_<SEGMENT>_TEMPORAL_MAP.json and <P>_TRANSITION_EVIDENCE.json (source hashes and amendment annotations added here);
  * risk calibration on top of t1_risk.assess (shared module untouched):
      - JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS vs JUDICIAL_REVIEW_CONTEXT_ONLY: a "Vide ADI/ADIN/ADC/ADPF/ADO" annotation in scope is
        HIGH only when the editor did not classify it as CONTEXT_ONLY (with reason); unclassified = REQUIRED (conservative);
      - TRANSITION_OR_TEMPORAL alone does not make HIGH when the temporal situation is resolved by versioned evidence (classes
        OPERATIVE_CURRENT, OPERATIVE_TRANSITION, EFFECT_EXHAUSTED, HISTORICAL_ONLY): the record is classified by the remaining risk;
      - TEMPORAL_STATUS_UNRESOLVED (HIGH): the explanation covers a FUTURE_TRIGGER, PARTIALLY_OPERATIVE or EXTERNAL_STATUS_REQUIRED rule;
  * DATES_AND_YEARS_PARITY (QUICK): a year or calendar date in the body (or in the example, unless marked illustrative) that is not in
    the Lei Seca grounding of the record nor in the batch reference date;
  * source sanity before generation (<P>_SOURCE_ANOMALIES.md/.json): CURRENT target without text, glued sibling label, repeated label,
    structural gaps in the numbering, empty snapshot;
  * per-segment accounting (CORPO / ADCT / TOTAL) in the scale report.
Nothing is approved: every new explanation is PENDING_HUMAN_REVIEW; AUTO_APPROVE_* and MICROAUTO_APPLY stay OFF.
Usage: python build_entenda_macro_segment.py derived/production_batch_08_macro [--determinism 3]
"""
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
import build_entenda_macro_batch as M  # noqa: E402
import editorial_checks as EC  # noqa: E402
import entenda_engine as E  # noqa: E402
import entenda_vigency_plan as VP  # noqa: E402
import production_batch as PB  # noqa: E402
import t1_batch_packets as BP  # noqa: E402
import t1_risk as R  # noqa: E402
import t1_validator_v2 as V  # noqa: E402
import t1_validator_v3 as V3  # noqa: E402

TEMPORAL_CLASSES = ('OPERATIVE_CURRENT', 'OPERATIVE_TRANSITION', 'EFFECT_EXHAUSTED', 'REVOKED', 'HISTORICAL_ONLY', 'FUTURE_TRIGGER',
                    'PARTIALLY_OPERATIVE', 'EXTERNAL_STATUS_REQUIRED')
RESOLVED_CLASSES = ('OPERATIVE_CURRENT', 'OPERATIVE_TRANSITION', 'EFFECT_EXHAUSTED', 'HISTORICAL_ONLY')
UNRESOLVED_CLASSES = ('FUTURE_TRIGGER', 'PARTIALLY_OPERATIVE', 'EXTERNAL_STATUS_REQUIRED')
SKIP_CODES = ('SKIP_EXHAUSTED_TRANSITION', 'SKIP_HISTORICAL_NO_CURRENT_VALUE', 'SKIP_APPROVED_PILOT_LEGACY_MODEL')
JR_CLASSES = ('JUDICIAL_REVIEW_CONTEXT_ONLY', 'JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS')
MONTHS = ('janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro')
DATE_RE = re.compile(r'\b(\d{1,2})º?\s+de\s+(' + '|'.join(MONTHS) + r')(?:\s+de\s+(\d{4}))?', re.I)
YEAR_RE = re.compile(r'(?<![\d.,/§º-])((?:18|19|20)\d{2})(?![\d.,]\d)')
ILLUSTRATIVE_RE = re.compile(r'ilustrativ|hipot[ée]tic', re.I)
SEGMENT_OF = {'CF88': 'CORPO', 'ADCT': 'ADCT'}
KIND_PT = M.KIND_PT


class SegmentBuildError(RuntimeError):
    pass


_json, _load, _n, sha, sha_lf = M._json, M._load, M._n, M.sha, M.sha_lf


def config_path(ms):
    return ROOT / ms['entenda_config'] if ms.get('entenda_config') else HERE / 'entenda_config.json'


def article_of(t):
    return ':'.join(t.split(':')[:2])


def article_targets(ctx, sb):
    """Article targets of a sub-block: explicit list, or numbered start..end with lettered articles, in structural order."""
    ns = sb.get('namespace')
    if sb.get('articles'):
        out = [a for a in sb['articles'] if ctx.exists(a)]
        if len(out) != len(sb['articles']):
            raise SegmentBuildError(f"SUB_BLOCK_ARTICLE_NOT_IN_INDEX {sorted(set(sb['articles']) - set(out))}")
    else:
        out = [f'{ns}:ART.{n}{s}' for n in range(sb['start'], sb['end'] + 1) for s in [''] + [f'-{x}' for x in 'ABCDEFGHIJ']]
        out = [a for a in out if ctx.exists(a)]
    return sorted(out, key=lambda t: ctx.order[t])


def all_articles(ms, ctx, built_only=True):
    return {x: article_targets(ctx, ms['sub_blocks'][x]) for x in (ms['sub_blocks_built'] if built_only else ms['sub_blocks'])}


def temporal_input(bd):
    p = bd / 'TEMPORAL_INPUT.json'
    return _load(p) if p.is_file() else dict(articles={}, explanations={})


def skipped(tin, arts):
    out = {}
    for a in arts:
        d = tin['articles'].get(a)
        if d and d.get('decision', 'SELECT') != 'SELECT':
            if d['decision'] not in SKIP_CODES or not (d.get('reason') or '').strip():
                raise SegmentBuildError(f'SKIP_WITHOUT_VALID_CODE_OR_REASON {a}')
            out[a] = d
    return out


# ---------------------------------------------------------------- assemble (segment-aware twin of M.assemble)

def assemble(bd, ms, ctx, nm, tin):
    built = ms['sub_blocks_built']
    by_block = all_articles(ms, ctx)
    arts_all = [a for x in built for a in by_block[x]]
    skips = skipped(tin, arts_all)
    arts = [a for a in arts_all if a not in skips]
    notes, expl = {}, []
    for x in built:
        d = _load(bd / 'drafts' / f'{nm.p}_{x}_DRAFTS.json')
        notes.update(d['article_notes'])
        expl += d['explanations']
    for e in expl:
        if article_of(e['target_id']) in skips:
            raise SegmentBuildError(f"EXPLANATION_IN_SKIPPED_ARTICLE {e['target_id']}")
    main = [r for r in E.load_corpus(ROOT / ctx.ncfg['corpus']) if r['status'] == 'ACTIVE']
    in_scope = lambda t: any(t == a or t.startswith(a + ':') for a in arts)  # noqa: E731
    reused = {r['target_id']: f"Explicacao aprovada anteriormente (HUMAN_APPROVED_T1, {r['explanation_id']}); reutilizada sem alteracao."
              for r in main if in_scope(r['target_id'])}
    own = {e['target_id'] for e in expl} | set(reused)
    covered = {c for e in expl for c in e.get('covered_targets', [])}
    missing = [a for a in arts if a not in own and ctx.effective_status(a) == 'CURRENT']
    if missing:
        raise SegmentBuildError(f'ARTICLE_WITHOUT_OVERVIEW {missing}')
    no_sep = {}
    for a in arts:
        for t in ctx.subtree(a):
            if t in own or t in covered or ctx.effective_status(t) != 'CURRENT' or ctx.kind(t) in ('CAPUT', 'ARTIGO'):
                continue
            if not notes.get(a):
                raise SegmentBuildError(f'ARTICLE_NOTE_MISSING {a}')
            no_sep[t] = f"{KIND_PT.get(ctx.kind(t), ctx.kind(t).lower())} sem explicacao propria: {notes[a]}"
    drafts = dict(norma_id=ms['norma_id'], batch_id=ms['batch_id'], template_version=ms['template_version'], prompt_version=ms['prompt_version'],
                  review_status='PENDING_HUMAN_REVIEW', authoring=ms['authoring'], explanations=expl)
    _json(bd / nm.drafts, drafts)
    targets = [t for a in arts for t in ctx.subtree(a) if ctx.effective_status(t) == 'CURRENT']
    vig, stats = VP.vigency_map(ctx, targets, ROOT / ms['canonical_structural_source'])
    juris = [r for x in built for r in _load(bd / 'drafts' / f'{nm.p}_{x}_DRAFTS.json').get('jurisprudence_recommendations', [])]
    juris += M.derived_jurisprudence_recommendations(ctx, expl, vig, {(r['target_id'], r['desired_reference']) for r in juris})
    sub_blocks = {x: [a for a in by_block[x] if a not in skips] for x in built}
    spec = dict(norma_id=ms['norma_id'], batch_id=ms['batch_id'], report_schema=2, as_of_date=ms['as_of_date'], scope=arts,
                sub_blocks=sub_blocks, drafts=nm.drafts, reference_export=ms.get('reference_export'), batch_corpus=nm.corpus, index_dir='index',
                review_sheet=nm.sheet, prior_corpora=ms['prior_corpora'], soft_target=ms['soft_target'], hard_cap=ms['hard_cap'],
                soft_target_justification=ms.get('soft_target_justification'), reused=dict(sorted(reused.items())),
                no_separate_reasons=dict(sorted(no_sep.items(), key=lambda kv: ctx.order[kv[0]])), jurisprudence_recommendations=juris,
                packet_prefix=nm.p, entenda_config=ms.get('entenda_config'))
    if not spec['reference_export']:
        spec.pop('reference_export')
    _json(bd / 'BATCH_SPEC.json', spec)
    _json(bd / nm.plan, dict(schema_version=1, batch_id=ms['batch_id'], norma_id=ms['norma_id'], as_of=ms['as_of_date'], scope=arts,
                             skipped_articles=sorted(skips, key=lambda a: ctx.order[a]), canonical_structural_source=ms['canonical_structural_source'],
                             entenda_config=ms.get('entenda_config'), method='entenda_vigency_plan.vigency_map', stats=stats, sub_blocks=sub_blocks,
                             vigency_by_target=vig, reused_pilots=sorted(reused),
                             status='DRAFT_AND_TRIAGE (sem aprovacao humana nesta missao)'))
    return spec, skips, vig


# ---------------------------------------------------------------- temporal layer

def temporal_class_of(tin, tid, ctx):
    e = tin['explanations'].get(tid, {})
    if e.get('temporal_class'):
        return e['temporal_class']
    a = tin['articles'].get(article_of(tid), {})
    return a.get('class')


def temporal_map(ms, ctx, tin, segment, vig):
    """Per-article auxiliary layer of a segment, with provenance (input) + source evidence (computed)."""
    rows = []
    for x in ms['sub_blocks']:
        sb = ms['sub_blocks'][x]
        if SEGMENT_OF.get(sb['namespace'], sb['namespace']) != segment:
            continue
        for a in article_targets(ctx, sb):
            st = ctx.effective_status(a)
            cap = ctx.text.get(a + ':CAPUT', '')
            d = tin['articles'].get(a, {})
            cls = 'REVOKED' if st == 'REVOKED' or (st == 'HISTORICAL' and E.REVOKED_TEXT_RE.match(cap)) else d.get('class')
            if st == 'HISTORICAL' and cls != 'REVOKED':
                cls = 'HISTORICAL_ONLY'
            if cls is not None and cls not in TEMPORAL_CLASSES:
                raise SegmentBuildError(f'TEMPORAL_CLASS_INVALID {a} {cls}')
            sub = [t for t in ctx.subtree(a) if t != a]
            ann = sorted({x_ for t in [a] + sub for x_ in vig.get(t, [])})
            rows.append(dict(article=a, sub_block=x, legal_status=st, temporal_class=cls,
                             classification_basis='STATUS_DO_RUNTIME (marca de revogacao)' if cls == 'REVOKED' else
                             ('FONTE_ESTRUTURAL_LEGADA (rotulo ausente do runtime)' if cls == 'HISTORICAL_ONLY' and st == 'HISTORICAL' else
                              ('EDITORIAL_COM_PROVENIENCIA' if cls else 'NAO_CLASSIFICADO')),
                             decision=('EXCLUDED_' + st) if st in ('REVOKED', 'HISTORICAL') else d.get('decision', 'SELECT' if cls else None),
                             reason=d.get('reason'), markers=d.get('markers', []), situation_as_of=d.get('situation_2026'),
                             produces_effects=d.get('produces_effects'), provenance=d.get('provenance', []),
                             targets=len(sub), targets_current=sum(1 for t in sub if ctx.effective_status(t) == 'CURRENT'),
                             targets_revoked=sum(1 for t in sub if ctx.effective_status(t) == 'REVOKED'),
                             targets_historical=sum(1 for t in sub if ctx.effective_status(t) == 'HISTORICAL'),
                             caput_sha256=E.sha256(cap) if cap else None, source_annotations=ann[:6]))
    counts = dict(sorted(Counter(r['temporal_class'] or 'NAO_CLASSIFICADO' for r in rows).items()))
    return dict(schema_version=1, batch_id=ms['batch_id'], segment=segment, as_of=ms['as_of_date'],
                taxonomy=dict(OPERATIVE_CURRENT='A: regra (transitoria ou nao) operante e clara em 2026', OPERATIVE_TRANSITION='A: regra transitoria em curso, com marco determinavel pelo texto',
                              EFFECT_EXHAUSTED='B: efeitos temporais ja produzidos/encerrados', PARTIALLY_OPERATIVE='C: parte vigente, parte exaurida ou revogada',
                              FUTURE_TRIGGER='D: depende de data/marco futuro (efeitos graduais ou posteriores a data de referencia)',
                              EXTERNAL_STATUS_REQUIRED='E/F: aplicacao atual depende de legislacao externa ou de jurisprudencia nao versionada',
                              HISTORICAL_ONLY='G: puramente historica', REVOKED='revogado na compilacao monovigente oficial'),
                policy='camada editorial auxiliar do ENTENDA; nao reclassifica o status juridico global (TARGET_STATUS). So C/D/E/F tendem a HIGH.',
                counts=counts, articles=rows)


def transition_evidence(ms, ctx, c, tin, vig, runtime_sha):
    out = []
    for t, r in sorted(c.records.items(), key=lambda kv: ctx.order[kv[0]]):
        e = tin['explanations'].get(t, {}).get('transition')
        cls = temporal_class_of(tin, t, ctx)
        if not (e or cls in (UNRESOLVED_CLASSES + RESOLVED_CLASSES) and t.startswith('ADCT:') or r.get('temporal')):
            continue
        a = tin['articles'].get(article_of(t), {})
        scope = R.scope_targets(r, ctx)
        ann = sorted({x for s in scope for x in vig.get(s, [])})
        ecs = sorted({n for x in ann for n in V3.EC_NUM.findall(x)}, key=int)
        e = e or {}
        out.append(dict(target_id=t, namespace=t.split(':')[0], temporal_class=cls, resolved_deterministically=cls in RESOLVED_CLASSES,
                        norma=e.get('norma', 'Constituicao Federal (ADCT)' if t.startswith('ADCT:') else 'Constituicao Federal'),
                        ec=e.get('ec') or a.get('ec') or ([f'EC {n}' for n in ecs] or None), article=e.get('artigo') or t,
                        marker=e.get('marco') or a.get('markers'), situation_as_of=e.get('situacao_2026') or a.get('situation_2026'),
                        produces_effects=e.get('produz_efeitos', a.get('produces_effects')), as_of=ms['as_of_date'],
                        source_text_sha256=r['source']['source_text_sha256'], text_source_path=r['source']['text_source_path'],
                        text_source_file_sha256=r['source']['text_source_file_sha256'], runtime_sha256=runtime_sha,
                        source_annotations=ann[:8], provenance=(e.get('provenance') or []) + a.get('provenance', []),
                        temporal_notes=[n['note_id'] for n in (r.get('temporal') or {}).get('notes', [])]))
    return dict(schema_version=1, batch_id=ms['batch_id'], as_of=ms['as_of_date'],
                policy='prova temporal de cada explicacao com componente temporal: norma, EC, artigo, marco, situacao na data de referencia, '
                       'se produz efeitos, hash da fonte e proveniencia. Nada vem de memoria: so texto versionado e anotacoes da fonte canonica.',
                total=len(out), resolved=sum(1 for x in out if x['resolved_deterministically']),
                unresolved=sum(1 for x in out if not x['resolved_deterministically']), entries=out)


# ---------------------------------------------------------------- risk calibration + dates parity

def _dates(text):
    out = set()
    for m in DATE_RE.finditer(text or ''):
        out.add(('d', int(m.group(1)), m.group(2).lower(), m.group(3)))
    for m in YEAR_RE.finditer(DATE_RE.sub(lambda m: ' ', text or '')):
        out.add(('y', m.group(1)))
    return out


def dates_findings(rec, ground, extra_years=(), extra_dates=()):
    """DATES_AND_YEARS_PARITY: calendar dates/years of the body must be in the grounding (snapshot + article + cited devices) or be the
    batch reference date; in the example, a date/year not in the text is allowed only in a sentence marked as illustrative."""
    g = _dates(ground)
    gy = {x[1] for x in g if x[0] == 'y'} | {x[3] for x in g if x[0] == 'd' and x[3]} | set(extra_years)
    gd = {(x[1], x[2]) for x in g if x[0] == 'd'} | set(extra_dates)
    out = []
    for sec in ('o_que_diz', 'o_que_significa', 'atencao', 'exemplo_pratico'):
        for s in V3.sentences(rec['content'].get(sec) or ''):
            miss = []
            for x in _dates(s):
                if x[0] == 'y' and x[1] not in gy:
                    miss.append(x[1])
                elif x[0] == 'd' and ((x[1], x[2]) not in gd or (x[3] and x[3] not in gy)):
                    miss.append(f'{x[1]} de {x[2]}' + (f' de {x[3]}' if x[3] else ''))
            if not miss:
                continue
            if sec == 'exemplo_pratico' and ILLUSTRATIVE_RE.search(s):
                out.append(V3._f('EXAMPLE_DATE_ILLUSTRATIVE', 'INFO', None, sec, ', '.join(sorted(miss)), s, 'data/ano marcado como ilustrativo'))
            else:
                out.append(V3._f('DATE_OR_YEAR_NOT_IN_TEXT', 'REVIEW_REQUIRED', 'QUICK', sec, ', '.join(sorted(miss)), s,
                                 'data ou ano ausente da Lei Seca do registro, do artigo e dos dispositivos citados (DATES_AND_YEARS_PARITY)'))
    return out


CITE_RE = re.compile(r'\barts?\.\s*(\d{1,3}(?:-[A-Z])?(?:\s*(?:,|e|a)\s*\d{1,3}(?:-[A-Z])?)*)', re.I)


def namespace_cited(rec, ctx, sentence=None):
    """Articles cited in the body (or in one sentence), resolved by namespace: a sentence that names the ADCT ("do ADCT", "deste Ato")
    cites ADCT articles; a sentence naming neither, inside a section that names the ADCT, may cite either (both are grounded); in an
    ADCT record a bare citation may be either; "arts. 124 a 127" is a range. The shared v2 resolver reads every citation as CF88
    (hash-pinned; not changed)."""
    out = []
    own_ns = rec['target_id'].split(':')[0]
    adct_re = re.compile(r'\bADCT\b|deste Ato|Disposições Constitucionais Transitórias')
    cf_re = re.compile(r'Constitui[çc][ãa]o')
    sections = [sentence] if sentence is not None else [rec['content'].get(k) or '' for k in ('o_que_diz', 'o_que_significa', 'exemplo_pratico', 'atencao')]
    for text in sections:
        sec_adct = bool(adct_re.search(text))
        for s in V3.sentences(text):
            adct, cf = bool(adct_re.search(s)), bool(cf_re.search(s))
            for m in CITE_RE.finditer(s):
                nums = re.findall(r'\d{1,3}(?:-[A-Z])?', m.group(1))
                if re.search(r'\d\s*a\s*\d', m.group(1)) and len(nums) == 2 and nums[0].isdigit() and nums[1].isdigit():
                    nums = [str(n) for n in range(int(nums[0]), int(nums[1]) + 1)]
                if adct and not cf:
                    spaces = ['ADCT']
                elif cf and not adct:
                    spaces = ['CF88']
                elif adct or sec_adct or own_ns == 'ADCT':
                    spaces = ['ADCT', 'CF88']
                else:
                    spaces = ['CF88']
                for ns in spaces:
                    for n in nums:
                        a = f'{ns}:ART.{n}'
                        if ctx.exists(a) and a not in out:
                            out.append(a)
    return out


def extended_grounding(rec, ctx):
    arts = namespace_cited(rec, ctx)
    return V3.grounding(rec, ctx) + '\n' + '\n'.join(ctx.text.get(t, '') for a in arts for t in ctx.subtree(a))


def refine_numbers(findings, rec, ground, ctx=None):
    """Re-check against the namespace-aware grounding (findings are kept, re-coded, with the reason):
    NUMBER_NOT_IN_TEXT whose quantities are in a cited device of the other namespace -> INFO NUMBER_GROUNDED_IN_CITED_DEVICE;
    EXTERNAL_NORMATIVE_CONTENT_CLAIM / EXTERNAL_FACT_NEEDS_PROVENANCE on an ADCT citation ("art. 125 do ADCT"): the ADCT is part of the
    versioned official runtime, so when every ADCT article cited in the sentence exists in the profile and the sentence's quantities,
    dates and years are in the grounding -> INFO ADCT_REFERENCE_GROUNDED_IN_RUNTIME."""
    gq = V3.quantities(ground)
    gd = _dates(ground)
    gy = {x[1] for x in gd if x[0] == 'y'} | {x[3] for x in gd if x[0] == 'd' and x[3]}
    gdm = {(x[1], x[2]) for x in gd if x[0] == 'd'}
    out = []
    for f in findings:
        if f['code'] == 'NUMBER_NOT_IN_TEXT' and f['severity'] == 'REVIEW_REQUIRED':
            qs = {q[:2] for q in V3.quantities(f['sentence'], units=True)}
            if qs and all(q in gq for q in qs):
                f = dict(f, code='NUMBER_GROUNDED_IN_CITED_DEVICE', severity='INFO', route=None,
                         detail='quantidade presente em dispositivo citado de outro namespace (ADCT/CF), resolvido pela camada macro 08')
        elif ctx is not None and f['code'] in ('EXTERNAL_NORMATIVE_CONTENT_CLAIM', 'EXTERNAL_FACT_NEEDS_PROVENANCE') and f['severity'] == 'REVIEW_REQUIRED' \
                and re.search(r'ADCT|Ato das Disposições', f['match'] or '') and not re.search(r'\bLei\b|Código|Regimento|Decreto', f['match'] or ''):
            s = f['sentence']
            cited = [a for a in namespace_cited(rec, ctx, s) if a.startswith('ADCT:')]
            qs = {q[:2] for q in V3.quantities(s, units=True)}
            ds = _dates(s)
            dates_ok = all((x[1] in gy) if x[0] == 'y' else ((x[1], x[2]) in gdm and (not x[3] or x[3] in gy)) for x in ds)
            if cited and all(q in gq for q in qs) and dates_ok:
                f = dict(f, code='ADCT_REFERENCE_GROUNDED_IN_RUNTIME', severity='INFO', route=None,
                         detail=f"remissao ao ADCT versionado no runtime oficial ({', '.join(cited)}); numeros e datas da frase presentes na fundamentacao")
        out.append(f)
    return out


class SegmentContext(M.MacroContext):
    """Macro-08 calibration (see module docstring). tin: TEMPORAL_INPUT.json."""

    def __init__(self, *a, tin=None, as_of_year=None, as_of_date=None, **k):
        super().__init__(*a, **k)
        self.tin = tin or dict(articles={}, explanations={})
        self.as_of_year = as_of_year
        self.as_of_dates = ()
        if as_of_date:
            y, mth, d = as_of_date.split('-')
            self.as_of_year, self.as_of_dates = y, ((int(d), MONTHS[int(mth) - 1]),)

    def validate(self, r, lint_rows=(), editorial_rows=()):
        ground = extended_grounding(r, self.ctx)
        fs = refine_numbers(super().validate(r, lint_rows, editorial_rows), r, ground, self.ctx)
        return fs + dates_findings(r, ground, extra_years=(self.as_of_year,) if self.as_of_year else (), extra_dates=self.as_of_dates)

    def assess(self, r, findings):
        a, cx = BP.Context.assess(self, r, findings)
        a = dict(a, rules=list(a['rules']), reasons=list(a['reasons']), secondary=list(a.get('secondary', [])))
        tid = r['target_id']
        info = self.tin['explanations'].get(tid, {})
        hits = sorted({f"{t.split(':', 1)[1]}: {m.group(0).strip()}" for t in R.scope_targets(r, self.ctx)
                       for ann in self.vigency.get(t, []) for m in [M.JUDICIAL_REVIEW_RE.search(ann)] if m})
        jr = (info.get('judicial_review') or {})
        if hits and jr.get('classification') not in (None,) + JR_CLASSES:
            raise SegmentBuildError(f'JUDICIAL_REVIEW_CLASS_INVALID {tid}')
        cls = temporal_class_of(self.tin, tid, self.ctx)
        high = [(x, y) for x, y in zip(a['rules'], a['reasons'])] if a['level'] == 'HIGH' else []
        medium = [] if a['level'] == 'HIGH' else ([(x, y) for x, y in zip(a['rules'], a['reasons'])] if a['level'] == 'MEDIUM' else [])
        sec_medium = [s for s in a['secondary']] if a['level'] == 'HIGH' else []
        if hits:
            short = '; '.join(hits[:3]) + (f' (+{len(hits) - 3})' if len(hits) > 3 else '')
            if jr.get('classification') == 'JUDICIAL_REVIEW_CONTEXT_ONLY':
                medium.append(('JUDICIAL_REVIEW_CONTEXT_ONLY', f"{short} -- {jr.get('reason', '')}"[:300]))
            else:
                high.append(('JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS', short + (f" -- {jr['reason']}" if jr.get('reason') else ' -- nao classificado pelo editor (conservador)')))
        if cls in UNRESOLVED_CLASSES:
            high.append(('TEMPORAL_STATUS_UNRESOLVED', f'{cls}: ' + (self.tin['articles'].get(article_of(tid), {}).get('situation_2026') or '')[:200]))
        trans = [h for h in high if h[0] == 'TRANSITION_OR_TEMPORAL']
        if trans and cls in RESOLVED_CLASSES:
            high = [h for h in high if h[0] != 'TRANSITION_OR_TEMPORAL']
            medium.append(('TRANSITION_RESOLVED_BY_VERSIONED_EVIDENCE', f'{cls} (MACRO08_TRANSITION_EVIDENCE)'))
        if high:
            sec = [f'{x}: {y}' for x, y in medium] + [s for s in sec_medium if s.split(':', 1)[0] not in {m[0] for m in medium}]
            return dict(a, level='HIGH', rules=[x for x, _ in high], reasons=[f'{x}: {y}' for x, y in high], secondary=sec), cx
        rest = medium + [(s.split(':', 1)[0], s.split(':', 1)[1].strip()) for s in sec_medium if s.split(':', 1)[0] not in {m[0] for m in medium}]
        lowonly = [m for m in rest if m[0] in ('TRANSITION_RESOLVED_BY_VERSIONED_EVIDENCE',)]
        if rest and len(lowonly) < len(rest):
            return dict(a, level='MEDIUM', rules=[x for x, _ in rest], reasons=[f'{x}: {y}' for x, y in rest], secondary=[]), cx
        if lowonly:
            return dict(a, level='LOW', rules=[], reasons=['risco restante baixo apos resolucao temporal por evidencia versionada'],
                        secondary=[f'{x}: {y}' for x, y in lowonly]), cx
        return a, cx


# ---------------------------------------------------------------- source sanity (before generation)

ROMAN = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
GLUED_RE = re.compile(r'(?<=[.;:])\s*(§\s?\d{1,3}º?(?:-[A-Z])?\s+[A-ZÁÉÍÓÚ]|[IVXL]{1,6}\s[-–]\s[a-zà-ú]|[a-z]\)\s[a-zà-ú])')


def _roman(s):
    v = 0
    for i, ch in enumerate(s):
        x = ROMAN[ch]
        v += -x if i + 1 < len(s) and ROMAN[s[i + 1]] > x else x
    return v


def _seqnum(t):
    last = t.split(':')[-1]
    lab = last.split('.', 1)[1] if '.' in last else ''
    base, _, suf = lab.partition('-')
    if suf:
        return None
    if base.isdigit():
        return int(base)
    if re.fullmatch(r'[IVXLCDM]+', base):
        return _roman(base)
    if re.fullmatch(r'[a-z]', base):
        return ord(base) - 96
    return None


def source_sanity(ctx, arts):
    """Pre-generation checks on the structure and text the explanations will be written on. Never corrects anything."""
    rows = []
    for a in arts:
        sub = ctx.subtree(a)
        for t in sub:
            k, st = ctx.kind(t), ctx.effective_status(t)
            if k in ('ARTIGO',):
                continue
            txt = ctx.text.get(t, '')
            if st == 'CURRENT' and not txt:
                rows.append(dict(target_id=t, code='CURRENT_WITHOUT_TEXT', severity='BLOCKING_FOR_TARGET', detail='target CURRENT sem texto no runtime/fonte'))
            m = GLUED_RE.search(txt)
            if st == 'CURRENT' and m:
                rows.append(dict(target_id=t, code='POSSIBLE_GLUED_SIBLING_LABEL', severity='REVIEW', detail=txt[max(0, m.start() - 40):m.end() + 40]))
            rep = ctx.targets[t].get('repeated_label_occurrences')
            if rep and rep > 1 and st == 'CURRENT':
                if ctx.targets[t].get('profile_origin') == 'OFFICIAL_RUNTIME':
                    rows.append(dict(target_id=t, code='REPEATED_LABEL', severity='REVIEW',
                                     detail=f'{rep} ocorrencias do rotulo na compilacao monovigente; texto da ultima ocorrencia (line_start)'))
                else:   # legacy multi-version index: the repetition is the wording history of cf.txt, the text comes from the monovigente source
                    rows.append(dict(target_id=t, code='LEGACY_MULTIVERSION_LABEL', severity='INFO',
                                     detail=f'{rep} redacoes no indice estrutural legado (cf.txt multivigente); texto lido da fonte monovigente'))
        kids = {}
        for t in sub:
            if t != a and ctx.targets[t]['parent_id']:
                kids.setdefault((ctx.targets[t]['parent_id'], ctx.kind(t)), []).append(t)
        for (parent, kind), ts in kids.items():
            if kind not in ('PARAGRAFO', 'INCISO', 'ALINEA'):
                continue
            nums = [n for n in (_seqnum(t) for t in ts) if n is not None]
            gaps = sorted(set(range(1, max(nums) + 1)) - set(nums)) if nums else []
            if gaps:
                rows.append(dict(target_id=parent, code='NUMBERING_GAP', severity='REVIEW',
                                 detail=f'{kind.lower()}: faltam {gaps[:10]} na sequencia (pode ser renumeracao/revogacao oficial)'))
            if len(nums) != len(set(nums)):
                rows.append(dict(target_id=parent, code='DUPLICATED_LABEL', severity='BLOCKING_FOR_TARGET', detail=f'{kind.lower()} duplicado'))
    return rows


# ---------------------------------------------------------------- build

def build(bd):
    bd = Path(bd).resolve()
    ms = _load(bd / 'MACRO_SPEC.json')
    nm = M.Names(ms)
    cfgp = config_path(ms)
    ctx = E.NormContext(ms['norma_id'], cfgp)
    tin = temporal_input(bd)
    spec, skips, vig_scope = assemble(bd, ms, ctx, nm, tin)
    for n in (nm.corpus, 'index/ENTENDA_BUILD_MANIFEST.json', 'index/ENTENDA_LOOKUP.IDX', 'index/ENTENDA_PAYLOAD.DAT'):
        (bd / n).unlink(missing_ok=True)
    sel = PB.run(bd, cfgp)
    catalog, known, registry = V.load_catalog(), V.load_json(V.KNOWN), V3.load_registry()
    c = SegmentContext(bd, ctx, catalog, known, registry, _load(bd / 'RELATIONS_PIN.json'), tin=tin, as_of_date=ms['as_of_date'])
    inp = _load(bd / 'EDITORIAL_INPUT.json')
    inp.update(schema_version=1, batch_id=ms['batch_id'], triage_sheet=nm.triage_sheet,
               risk_criteria=dict(classifier='ENTENDA_ENGINE/t1_risk.py::assess + complexity (validator v3) + build_entenda_macro_segment.SegmentContext',
                                  LEGAL_RISK='HIGH: ' + '; '.join(R.LEGAL_HIGH) + '; JUDICIAL_REVIEW_REQUIRED_FOR_CORRECTNESS; TEMPORAL_STATUS_UNRESOLVED '
                                  '(camada macro 08; TRANSITION_OR_TEMPORAL resolvido por evidencia versionada nao gera HIGH sozinho)',
                                  level='o campo level e o LEGAL_RISK'),
               risk=BP.risk_input(c))
    _json(bd / 'EDITORIAL_REVIEW_INPUT.json', dict(sorted(inp.items())))
    EC.run(bd)
    doc = BP.triage(c)
    out = render_packets(doc, c, nm)
    doc['metrics'] = BP.metrics(doc, c, out)
    doc['d_ratio'] = round(doc['counts']['D_FULL_HUMAN_REVIEW'] / len(doc['rows']), 3) if doc['rows'] else 0
    doc['d_escalation_diagnostic'] = nm.packets['diagnostic'] in out
    micro = BP.micro_auto(doc, c.cfg)
    doc['micro_adjustments'] = dict(applied=micro['applied'], eligible=micro['eligible'], microauto_apply=micro['microauto_apply'])
    doc['human_approved_t1_granted'] = 0
    doc['validator_limits'] = V3.LIMITS + ['DATES_AND_YEARS_PARITY compara datas/anos por presenca na fundamentacao (Lei Seca do registro, artigo e '
                                           'dispositivos citados) e a data de referencia do lote; nao verifica calculos de prazo.']
    critic = {x: _load(bd / 'drafts' / f'{nm.p}_{x}_CRITIC_LOG.json') for x in ms['sub_blocks_built'] if (bd / 'drafts' / f'{nm.p}_{x}_CRITIC_LOG.json').is_file()}
    doc['critic'] = {x: dict(corrections=len(v['corrections']), by_category=dict(sorted(Counter(e['category'] for e in v['corrections']).items())))
                     for x, v in critic.items()}
    doc['checks'] = M.checks(c, doc)
    doc['segments'] = {s: segment_of_rows(doc, s) for s in ('CORPO', 'ADCT')}
    for name, text in out.items():
        (bd / name).write_bytes(text.encode('utf-8'))
    _json(bd / 'MICRO_ADJUSTMENTS_LOG.json', micro)
    # temporal layer, transition evidence, skip register, source sanity, structural audit
    full_vig = full_vigency(ms, ctx)
    prov = json.loads((ROOT / ctx.cfg['norms'][ms['norma_id']]['target_index']).read_text(encoding='utf-8')).get('sources', {})
    runtime_sha = prov.get('runtime_sha256')
    tmaps = {s: temporal_map(ms, ctx, tin, s, full_vig) for s in ('ADCT',) if any(v['namespace'] == 'ADCT' for v in ms['sub_blocks'].values())}
    for s, d in tmaps.items():
        _json(bd / f'{nm.p}_{s}_TEMPORAL_MAP.json', d)
    _json(bd / f'{nm.p}_TRANSITION_EVIDENCE.json', transition_evidence(ms, ctx, c, tin, vig_scope, runtime_sha))
    _json(bd / f'{nm.p}_SKIP_REGISTER.json', skip_register(ms, ctx, skips, tin))
    anomalies = source_sanity(ctx, [a for v in all_articles(ms, ctx, built_only=False).values() for a in v])
    write_anomalies(bd, nm, ms, anomalies, _load(bd / 'SOURCE_ANOMALIES_INPUT.json') if (bd / 'SOURCE_ANOMALIES_INPUT.json').is_file() else {})
    spec = _load(bd / 'BATCH_SPEC.json')
    for x in ms['sub_blocks']:
        cp = bd / f'{nm.p}_{x}_CHECKPOINT.json'
        if x not in ms['sub_blocks_built']:
            cp.unlink(missing_ok=True)
            continue
        st = M.slice_stats(doc, sel, spec, spec['sub_blocks'][x])
        sb = ms['sub_blocks'][x]
        st['skipped_articles'] = sorted((a for a in skips if a in article_targets(ctx, sb)), key=lambda a: ctx.order[a])
        _json(cp, dict(schema_version=1, batch_id=ms['batch_id'], sub_block=sb['name'], namespace=sb['namespace'],
                       articles_range=f"{sb['namespace']} {sb.get('start')}-{sb.get('end')}" if not sb.get('articles') else sb['articles'], stats=st,
                       critic=doc['critic'].get(x, dict(corrections=0, by_category={})), checks=dict(doc['checks'], scope='lote acumulado ate este sub-bloco'),
                       determinism='ver DETERMINISM_EVIDENCE.json (builds completos comparados byte a byte)', human_approved_t1_granted=0,
                       status=doc['checks']['status']))
    _json(bd / nm.triage, doc)
    (bd / nm.report).write_bytes(report(doc, sel, c, ms, nm, skips, tmaps).encode('utf-8'))
    doc['backlog'] = M.backlog(bd, ms, ctx, nm)
    _json(bd / nm.triage, doc)
    manifest(bd, ms, nm, doc, sel)
    if doc['checks']['status'] != 'PASS':
        raise SegmentBuildError(json.dumps(doc['checks'], ensure_ascii=False))
    return doc


def render_packets(doc, c, nm):
    files, full_generated = BP.packets(doc, c)
    out = {}
    for k, v in files.items():
        key = next(n for n, suffix in (('compact', '_COMPACT_CLEAN_REVIEW.md'), ('quick', '_QUICK_REVIEW.md'), ('full', '_FULL_HUMAN_REVIEW.md'),
                                       ('hard', '_HARD_FAIL_REPORT.md'), ('diagnostic', '_D_ESCALATION_DIAGNOSTIC.md')) if k.endswith(suffix))
        out[nm.packets[key]] = M._retitle(v, nm)
    if not full_generated:
        out[nm.packets['full']] = M._retitle(BP.full(doc, c), nm)
    out[nm.priority] = M.priority(doc, c, nm)
    return out


def segment_of_rows(doc, seg):
    rows = [x for x in doc['rows'] if SEGMENT_OF.get(x['target_id'].split(':')[0]) == seg]
    return dict(new_explanations=len(rows), roles=dict(sorted(Counter(x['role'] for x in rows).items())),
                queues={q: sum(1 for x in rows if x['queue'] == q) for q in BP.QUEUES},
                legal_risk={k: sum(1 for x in rows if x['legal_risk'] == k) for k in ('LOW', 'MEDIUM', 'HIGH')},
                verification_complexity={k: sum(1 for x in rows if x['verification_complexity'] == k) for k in ('SIMPLE', 'STRUCTURED', 'EXTERNAL')},
                jurisprudence=dict(sorted(Counter(x['jurisprudence'] for x in rows).items())))


def full_vigency(ms, ctx):
    arts = [a for v in all_articles(ms, ctx, built_only=False).values() for a in v]
    targets = [t for a in arts for t in ctx.subtree(a) if ctx.text.get(t)]
    vig, _ = VP.vigency_map(ctx, targets, ROOT / ms['canonical_structural_source'])
    return vig


def skip_register(ms, ctx, skips, tin):
    rows = []
    for a in sorted(skips, key=lambda x: ctx.order[x]):
        d = skips[a]
        rows.append(dict(article=a, decision=d['decision'], temporal_class=d.get('class'), reason=d['reason'],
                         situation_as_of=d.get('situation_2026'), provenance=d.get('provenance', []),
                         targets=[dict(target_id=t, kind=ctx.kind(t), status=ctx.effective_status(t)) for t in ctx.subtree(a)]))
    return dict(schema_version=1, batch_id=ms['batch_id'], as_of=ms['as_of_date'],
                policy='artigos avaliados e nao explicados (SKIP de artigo inteiro), sempre com motivo; seus targets constam aqui, nao no SELECTION_REPORT',
                articles=len(rows), targets=sum(len(r['targets']) for r in rows),
                by_decision=dict(sorted(Counter(r['decision'] for r in rows).items())), rows=rows)


def write_anomalies(bd, nm, ms, rows, inp):
    diag = inp.get('diagnoses', {})
    doc = dict(schema_version=1, batch_id=ms['batch_id'], policy='sanity estrutural executado ANTES da geracao; nada foi corrigido por redacao manual',
               counts=dict(sorted(Counter(r['code'] for r in rows).items())), rows=[dict(r, diagnosis=diag.get(f"{r['target_id']}|{r['code']}")) for r in rows],
               registered=inp.get('registered', []))
    _json(bd / f'{nm.p}_SOURCE_ANOMALIES.json', doc)
    L = [f'# {nm.p} — ANOMALIAS DA FONTE (sanity antes da geração)', '', doc['policy'] + '.', '',
         'Escopo: todos os artigos do macrolote (corpo permanente e ADCT), inclusive sub-blocos ainda não gerados. Fonte: config do lote '
         f"(`{ms.get('entenda_config') or 'ENTENDA_ENGINE/entenda_config.json'}`).", '',
         '## Contagem', ''] + [f'- {k}: {v}' for k, v in doc['counts'].items()] + ['', '## Anomalias registradas (diagnóstico)', '']
    for r in inp.get('registered', []):
        L += [f"### {r['id']} — `{r['target']}` ({r['kind']})", '', r['detail'], '', f"- Diagnóstico: {r['diagnosis']}", f"- Tratamento: {r['handling']}", '']
    L += ['## Achados automáticos', '', '| Target | Código | Severidade | Detalhe | Diagnóstico |', '|---|---|---|---|---|']
    L += [f"| `{r['target_id']}` | {r['code']} | {r['severity']} | {r['detail'][:140].replace('|', '/')} | {(r['diagnosis'] or '—')[:200]} |" for r in doc['rows']] or ['| — | — | — | — | — |']
    (bd / f'{nm.p}_SOURCE_ANOMALIES.md').write_bytes(('\n'.join(L) + '\n').encode('utf-8'))


# ---------------------------------------------------------------- report / manifest

def report(doc, sel, c, ms, nm, skips, tmaps):
    s, m = sel['summary'], doc['metrics']
    rows = doc['rows']
    spec = c.spec
    L = [f"# {ms['batch_id']} — relatório de escala", '',
         f"Data de referência: {ms['as_of_date']} · gerado por `ENTENDA_ENGINE/build_entenda_macro_segment.py` (determinístico, só conteúdo versionado) · "
         '**0 HUMAN_APPROVED_T1 novos**: todas as explicações novas estão `PENDING_HUMAN_REVIEW`; AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF.', '',
         f"Config de texto: `{ms.get('entenda_config')}`.", '',
         f"Sub-blocos construídos: {', '.join(ms['sub_blocks'][x]['name'] for x in ms['sub_blocks_built'])}.", '',
         '## Seleção (lote inteiro)', '', '| | |', '|---|---|',
         f"| Artigos no escopo | {len(spec['scope'])} explicados/avaliados no SELECTION_REPORT + {len(skips)} SKIP de artigo inteiro (SKIP_REGISTER) |",
         f"| Targets analisados | {s['targets_evaluated']} ({s['targets_current']} vigentes; excluídos: "
         + ', '.join(f'{k} {v}' for k, v in sorted(s['by_classification'].items()) if k.startswith('EXCLUDED')) + ') |',
         f"| SELECT | {s['selected']} = {s['new_explanations']} novas + {s['reused_from_pilot']} reutilizada(s) já aprovada(s) |",
         f"| SKIP | {s['by_classification'].get('NO_SEPARATE_EXPLANATION', 0)} dispositivos (com motivo) + {len(skips)} artigos inteiros |", '',
         '## Por sub-bloco', '', '| Sub-bloco | Segmento | Artigos | SKIP art. | Vigentes | SELECT | SKIP | Novas | LOW/MED/HIGH | A/B/C/D/E | Correções do critic |',
         '|---|---|---|---|---|---|---|---|---|---|---|']
    for x in ms['sub_blocks_built']:
        st = M.slice_stats(doc, sel, spec, spec['sub_blocks'][x])
        q = st['queues']
        sb = ms['sub_blocks'][x]
        nsk = sum(1 for a in skips if a in article_targets(c.ctx, sb))
        L.append(f"| {sb['name']} | {SEGMENT_OF.get(sb['namespace'])} | {st['articles']} | {nsk} | {st['targets_current']} | {st['select']} | {st['skip']} | "
                 f"{st['new_explanations']} | {st['legal_risk']['LOW']}/{st['legal_risk']['MEDIUM']}/{st['legal_risk']['HIGH']} | "
                 f"{q['A_CLEAN_LOW']}/{q['B_CLEAN_MEDIUM']}/{q['C_QUICK_REVIEW']}/{q['D_FULL_HUMAN_REVIEW']}/{q['E_HARD_FAIL']} | "
                 f"{doc['critic'].get(x, {}).get('corrections', 0)} |")
    L += ['', '## Por segmento', '', '| Segmento | Novas | LOW/MED/HIGH | SIMPLE/STRUCT/EXT | A/B/C/D/E |', '|---|---|---|---|---|']
    for seg, d in doc['segments'].items():
        q = d['queues']
        L.append(f"| {seg} | {d['new_explanations']} | {d['legal_risk']['LOW']}/{d['legal_risk']['MEDIUM']}/{d['legal_risk']['HIGH']} | "
                 f"{d['verification_complexity']['SIMPLE']}/{d['verification_complexity']['STRUCTURED']}/{d['verification_complexity']['EXTERNAL']} | "
                 f"{q['A_CLEAN_LOW']}/{q['B_CLEAN_MEDIUM']}/{q['C_QUICK_REVIEW']}/{q['D_FULL_HUMAN_REVIEW']}/{q['E_HARD_FAIL']} |")
    for seg, tm in tmaps.items():
        L += ['', f'## Mapa temporal ({seg})', '', '| Classe | Artigos |', '|---|---|'] + [f'| {k} | {v} |' for k, v in tm['counts'].items()]
    L += ['', '## Dois eixos e filas (lote)', '', '| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |', '|---|---|---|---|---|']
    for a, b in zip(('LOW', 'MEDIUM', 'HIGH'), ('SIMPLE', 'STRUCTURED', 'EXTERNAL')):
        L.append(f"| {a} | {doc['legal_risk_counts'].get(a, 0)} | | {b} | {doc['complexity_counts'].get(b, 0)} |")
    L += ['', '| Fila | Itens |', '|---|---|'] + [f"| {q} | {doc['counts'][q]} |" for q in BP.QUEUES]
    L += ['', f"D = {doc['d_ratio'] * 100:.1f}% das novas.", f"Jurisprudência: {', '.join(f'{k} {v}' for k, v in sorted(doc['jurisprudence_counts'].items()))}.", '',
          '## Motivos dos D', ''] + [f"- {k}: {v}" for k, v in doc['d_reasons'].items()]
    L += ['', '## Achados REVIEW_REQUIRED', ''] + ([f"- {k}: {v}" for k, v in doc['finding_counts'].items()] or ['- nenhum'])
    L += ['', '## Volume para o humano', '', '| Métrica | Caracteres |', '|---|---|',
          f"| Rascunhos (5 seções + glossário) | {_n(m['total_draft_chars'])} |",
          f"| Modelo antigo (pacote completo de todos os itens) | {_n(m['old_model_full_package_chars'])} |",
          f"| **Apresentado ao humano (pacotes + prioridade)** | **{_n(m['presented_chars'])}** |"]
    L += [f"| — {k} | {_n(v)} |" for k, v in m['presented_by_file'].items()]
    L += [f"| Redução vs. modelo antigo | {_n(m['reduction_abs'])} ({m['reduction_pct']}%) |", '',
          '## Checks estruturais', '', f"- {doc['checks']['status']}: contrato do motor, Lei Seca idêntica ao texto do perfil em todos os registros, "
          f"0 HARD_FAIL, 0 aprovado novo, 0 STALE.", '', '## Limites do validador', ''] + [f'- {x}' for x in doc['validator_limits']]
    return '\n'.join(L) + '\n'


CODE = ('build_entenda_macro_segment.py', 'build_entenda_macro_batch.py', 'entenda_text_profile.py', 'entenda_vigency_plan.py', 't1_batch_packets.py',
        't1_risk.py', 't1_validator_v3.py', 't1_validator_v2.py', 't1_triage.py', 'editorial_checks.py', 'production_batch.py', 'entenda_engine.py',
        'macro_critic_pass.py')
INPUTS = ('MACRO_SPEC.json', 'EDITORIAL_INPUT.json', 'RELATIONS_PIN.json', 'BACKLOG_INPUT.json', 'TEMPORAL_INPUT.json', 'SOURCE_ANOMALIES_INPUT.json')


def manifest(bd, ms, nm, doc, sel):
    inputs = [p for p in INPUTS if (bd / p).is_file()] + sorted(str(p.relative_to(bd)) for p in (bd / 'drafts').rglob('*.json'))
    generated = sorted(str(p.relative_to(bd)) for p in bd.rglob('*') if p.is_file() and str(p.relative_to(bd)) not in inputs
                       and p.name not in (nm.manifest, 'DETERMINISM_EVIDENCE.json') and not p.name.startswith(f'{nm.p}_D_DIAGNOSTIC')
                       and not p.name.startswith(f'{nm.p}_ADCT_STRUCTURAL_AUDIT'))
    prof = config_path(ms).parent / 'PROFILE_MANIFEST.json'
    _json(bd / nm.manifest, dict(
        schema_version=1, batch_id=ms['batch_id'], as_of=ms['as_of_date'], status='CANDIDATE: 0 HUMAN_APPROVED_T1; nada aprovado',
        builder='ENTENDA_ENGINE/build_entenda_macro_segment.py', entenda_config=ms.get('entenda_config'),
        text_profile_manifest_sha256=sha(prof) if prof.is_file() else None, validator=doc['validator'], sub_blocks_built=ms['sub_blocks_built'],
        selection=dict(targets_evaluated=sel['summary']['targets_evaluated'], current=sel['summary']['targets_current'], selected=sel['summary']['selected'],
                       new=sel['summary']['new_explanations'], reused=sel['summary']['reused_from_pilot'],
                       skip=sel['summary']['by_classification'].get('NO_SEPARATE_EXPLANATION', 0)),
        queues=doc['counts'], legal_risk=doc['legal_risk_counts'], verification_complexity=doc['complexity_counts'], segments=doc['segments'],
        metrics=doc['metrics'], code_sha256_lf={p: sha_lf(HERE / p) for p in CODE},
        inputs={p: sha(bd / p) for p in inputs}, files={p: sha(bd / p) for p in generated}))


def copy_inputs(bd, td):
    shutil.copytree(bd / 'drafts', td / 'drafts')
    for f in INPUTS:
        if (bd / f).is_file():
            shutil.copy(bd / f, td / f)


def determinism(bd, n=3):
    bd = Path(bd).resolve()
    ms = _load(bd / 'MACRO_SPEC.json')
    skip = lambda p: p.name == 'DETERMINISM_EVIDENCE.json' or p.name.startswith(('MACRO08_D_DIAGNOSTIC', 'MACRO08_ADCT_STRUCTURAL_AUDIT'))  # noqa: E731
    runs = []
    with tempfile.TemporaryDirectory(prefix='macro_seg_det_') as tmp:
        for i in range(n):
            td = Path(tmp) / f'run{i}' / bd.name
            copy_inputs(bd, td)
            build(td)
            runs.append({str(p.relative_to(td)): sha(p) for p in td.rglob('*') if p.is_file()})
    inplace = {str(p.relative_to(bd)): sha(p) for p in bd.rglob('*') if p.is_file() and not skip(p)}
    differing = sorted({f for r in runs for f in set(r) | set(inplace) if r.get(f) != inplace.get(f)})
    ev = dict(schema_version=1, batch_id=ms['batch_id'], runs=n, byte_identical=not differing, differing_files=differing, files=len(inplace),
              sha256=dict(sorted(inplace.items())), sub_blocks_built=ms['sub_blocks_built'],
              procedure=f'{n} builds completos em copias temporarias das entradas versionadas, comparados entre si e com o build no lugar '
                        '(fora da comparacao: documentos consolidados escritos a mao, MACRO08_D_DIAGNOSTIC e MACRO08_ADCT_STRUCTURAL_AUDIT)')
    _json(bd / 'DETERMINISM_EVIDENCE.json', ev)
    return ev


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    target = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else HERE / 'derived/production_batch_08_macro'
    d = build(target)
    out = dict(counts=d['counts'], legal_risk=d['legal_risk_counts'], complexity=d['complexity_counts'], d_reasons=d['d_reasons'],
               findings=d['finding_counts'], segments=d['segments'], metrics={k: v for k, v in d['metrics'].items() if k != 'presented_by_file'},
               checks=d['checks']['status'])
    if '--determinism' in sys.argv:
        ev = determinism(target, int(sys.argv[sys.argv.index('--determinism') + 1]))
        out['determinism'] = dict(runs=ev['runs'], byte_identical=ev['byte_identical'], differing=ev['differing_files'])
    print(json.dumps(out, ensure_ascii=False, indent=1))
