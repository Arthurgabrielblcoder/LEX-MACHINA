"""CORRELATA overlay for the Reference Engine (C3A, RUN4_CANDIDATE_HOST_ONLY). Generic and data-driven: no norm, target or law is named here.

Two overlays over the immutable legacy catalog (the CORRELATA links that reference_engine.build_links() produces):
  * corrections  (CF88_CORRELATA_EXCLUSIONS_CANDIDATE.json): one record per legacy link (reference_id) with an action
        EXCLUDE            MATERIAL_MISMATCH_EXCLUDED            link leaves the visible export (REMOVE, REPLACE, RETARGET)
        SUPPRESS_HOLD      REVIEW_HOLD_SUPPRESSED                human decision is HOLD: not published, decision preserved, restorable
        SUPPRESS_TEMPORAL  TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE   legally kept, hidden until `until` (vacatio legis)
        ROUTE_FIX          ROUTE_FIXED                           same link (no duplicate), corrected route in the RELACOES candidate
        KEEP               LEGACY_KEPT                           unchanged; recorded so that every visible legacy link has a decision
  * additions    (CF88_CORRELATA_ADDITIONS.json and the legal register): human-approved relations, review_status HUMAN_APPROVED_CORRELATA_V1.

LEGAL_APPROVED IS NOT DEVICE_READY. validate_record() decides whether a relation is legally representable (fail closed); device_blockers()
decides, separately, whether the current card + firmware could show it without new ingestion and without a new firmware route.
Every error raises OverlayError: no partial overlay is ever produced.
"""
import hashlib
import json
import re
from pathlib import Path

import reference_engine as E
import target_id as T

APPROVED = 'HUMAN_APPROVED_CORRELATA_V1'
ROUTES = ('EXT_NORMAS', 'MAIN_CORPUS')
RESOLUTIONS = ('ON_CARD', 'MAIN_CORPUS', 'INGESTION_REQUIRED')
FALLBACKS = ('OPEN_NORM_START',)
RELATION_TYPES = ('REGULAMENTA', 'COMPLEMENTA', 'IMPLEMENTA', 'PROCEDIMENTO', 'CONDIÇÃO_OU_EXCEÇÃO', 'ORGANIZA_INSTITUIÇÃO')
# legacy decisions (KEEP/RETARGET/REPLACE review) never classified the relation type: allowed only when every decision is a legacy one
LEGACY_RELATION_TYPE = 'NAO_CLASSIFICADA_REVISAO_LEGADA'
TEMPORAL = ('IN_FORCE', 'VACATIO_LEGIS', 'PARTIAL_EFFECTS', 'TRANSITIONAL', 'REVOKED', 'UNCERTAIN')
TEMPORAL_PUBLISHABLE = ('IN_FORCE', 'VACATIO_LEGIS', 'PARTIAL_EFFECTS', 'TRANSITIONAL')
VACATIO_POLICIES = ('DO_NOT_PUBLISH_AS_CURRENT',)
JUDICIAL_STATUSES = ('STF_PARTIAL_UNCONSTITUTIONALITY', 'STF_INTERPRETATION_CONFORME', 'STF_SUSPENDED_INJUNCTION', 'STF_PARTIAL_EFFECTS',
                     'PENDING_JUDICIAL_REVALIDATION')
JUDICIAL_REQUIRED = ('status', 'cases', 'decided_on', 'notice_short', 'checked_until')
NOTICE_MAX = 80
ENGINE_OK = ('CURRENT', 'STRUCTURAL')
RUNTIME_OK = ('CURRENT', 'STRUCTURAL')
FIELDS = ('relation_id', 'target_id', 'destination_norm_id', 'destination_norm_key', 'destination_route', 'destination_resolution',
          'destination_articles', 'fallback', 'relation_type', 'legal_basis', 'scope', 'flags', 'temporal_status', 'effective_from',
          'early_application_possible', 'revalidate_on', 'temporal_note', 'vacatio_policy', 'judicial_status', 'review_status', 'reviewer',
          'decision_ids', 'provenance', 'supersedes')
NON_EMPTY = ('relation_id', 'target_id', 'destination_norm_id', 'destination_norm_key', 'destination_route', 'destination_resolution',
             'relation_type', 'legal_basis', 'temporal_status', 'review_status', 'reviewer', 'decision_ids', 'provenance')
ACTIONS = {'KEEP': 'LEGACY_KEPT', 'EXCLUDE': 'MATERIAL_MISMATCH_EXCLUDED', 'SUPPRESS_HOLD': 'REVIEW_HOLD_SUPPRESSED',
           'SUPPRESS_TEMPORAL': 'TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE', 'ROUTE_FIX': 'ROUTE_FIXED'}
# device capability of the CURRENT firmware (data, not norm-specific): routes it can open and relation origins verified on the card
DEVICE_ROUTES_SUPPORTED = ('EXT_NORMAS',)
DEVICE_JUDICIAL_NOTICE_SUPPORTED = False
FIRMWARE_CACHE = dict(lookup_rows=64, norms=32)
DEVICE_STATES = ('DEVICE_READY', 'TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE', 'BLOCKED_INGESTION_REQUIRED', 'BLOCKED_DEVICE_ROUTE_MAIN_CORPUS',
                 'BLOCKED_DEVICE_ORIGIN_UNVERIFIED', 'BLOCKED_DEVICE_JUDICIAL_NOTICE_UNSUPPORTED')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
REL_HEADER = ('#LEXMACHINA|RELACOES|2', '#ORIGEM_NORMA|ARTIGO|PARAGRAFO|INCISO|ALINEA|RELACAO_ID|DESTINO_ID|DESTINO_NOME|MODO|ARTIGOS_DESTINO|CAMINHO_TXT')
LOOKUP_HEADER = ('#LEXMACHINA|REL_LOOKUP|2', '#ORIGEM_NORMA|ARTIGO|PARAGRAFO|INCISO|ALINEA|OFFSET|QUANTIDADE')


class OverlayError(ValueError):
    def __init__(self, code, ref=''):
        super().__init__(f'{code}: {ref}')
        self.code, self.ref = code, ref


# ---------------------------------------------------------------- identity / presentation
def presentation_unit(target_id):
    """ART and ART:CAPUT are one presentation unit (the device shows both on the article screen)."""
    return target_id[:-len(':CAPUT')] if target_id.endswith(':CAPUT') else target_id


def identity(target_id, norm_key):
    return (presentation_unit(target_id), norm_key)


def relation_id_for(target_id, destination_norm_id):
    h = hashlib.sha256(f'CORRELATA_ADDITION|{presentation_unit(target_id)}|{destination_norm_id}'.encode('utf-8')).hexdigest()
    return 'REL_' + h[:16].upper()


def origin_of(target_id):
    """RELACOES origin columns of a target (ART and ART:CAPUT share the article origin)."""
    p = T.parse_target_id(presentation_unit(target_id))
    return (p['namespace'], p['article'] or '', p['paragraph'] or '', p['inciso'] or '', p['alinea'] or '')


def target_of_origin(origin):
    ns, art, par, inc, al = origin
    return ':'.join([ns, f'ART.{art}'] + ([f'PAR.{par}'] if par else []) + ([f'INC.{inc}'] if inc else []) + ([f'AL.{al}'] if al else []))


# ---------------------------------------------------------------- context
class Context:
    """Read-only inputs: engine registry (target existence/status), device runtime tables, card relation tables, main-corpus article index."""

    def __init__(self, reg, norma_id, runtime_targets, text_map, card_dir, main_corpus_index, ext_text_index):
        self.reg, self.norma_id = reg, norma_id
        reg.load(norma_id)
        self.runtime, self.text_map = runtime_targets, set(text_map)
        card_dir = Path(card_dir)
        self.ext = {r[0]: dict(name=r[1], path=r[2]) for r in _rows(card_dir / 'EXT_NORMAS.IDX')}
        self.ext_articles = {}
        for r in _rows(card_dir / 'EXT_ARTIGOS.IDX'):
            self.ext_articles.setdefault(r[0], set()).add(r[1])
        self.relacoes = [tuple(r) for r in _rows(card_dir / 'RELACOES.IDX')]
        self.card_lookup = (card_dir / 'REL_LOOKUP.IDX').read_bytes()
        self.card_relacoes = (card_dir / 'RELACOES.IDX').read_bytes()
        self.main = json.loads(Path(main_corpus_index).read_text(encoding='utf-8'))['norms']
        # legal article check uses the norm TEXT; the card's EXT_ARTIGOS (device jump index) may have gaps
        self.ext_text_articles = {k: set(v['articles']) for k, v in json.loads(Path(ext_text_index).read_text(encoding='utf-8'))['norms'].items()}

    def engine_status(self, target_id):
        return self.reg.status(self.norma_id, target_id)


def _rows(p):
    return [l.split('|') for l in Path(p).read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]


# ---------------------------------------------------------------- validation (legal)
def check_target(target_id, ctx, ref):
    """Target must exist and be CURRENT/STRUCTURAL. UNKNOWN_VALIDITY is never accepted generically: only an ADCT target confirmed by the
    device runtime (present, legal status CURRENT/STRUCTURAL, reachable in TEXT_MAP) passes, and only for an approved record."""
    if not T.validate_target_id(target_id)[0] or not ctx.reg.target_exists_for_norm(ctx.norma_id, target_id):
        raise OverlayError('TARGET_NOT_FOUND', f'{ref}: {target_id}')
    eng = ctx.engine_status(target_id)
    rt = ctx.runtime.get(target_id)
    if eng == 'HISTORICAL_ONLY' or (rt and rt['legal_status'] not in RUNTIME_OK):
        raise OverlayError('TARGET_HISTORICAL_OR_REVOKED', f'{ref}: {target_id}')
    if eng in ENGINE_OK:
        return 'ENGINE_' + eng
    if eng == 'UNKNOWN_VALIDITY' and T.parse_target_id(target_id)['namespace'] == 'ADCT':
        if rt and rt['legal_status'] in RUNTIME_OK and presentation_unit(target_id) in ctx.text_map:
            return 'ADCT_RUNTIME_CONFIRMED'
        raise OverlayError('ADCT_NOT_CONFIRMED_BY_RUNTIME', f'{ref}: {target_id}')
    raise OverlayError('TARGET_STATUS_NOT_ALLOWED', f'{ref}: {target_id} ({eng})')


def check_destination(r, ctx):
    route, nid, res = r['destination_route'], r['destination_norm_id'], r['destination_resolution']
    if route not in ROUTES:
        raise OverlayError('ROUTE_INVALID', f"{r['relation_id']} ({route})")
    if res not in RESOLUTIONS:
        raise OverlayError('RESOLUTION_INVALID', r['relation_id'])
    if r['fallback'] not in FALLBACKS:
        raise OverlayError('FALLBACK_INVALID', r['relation_id'])
    if route == 'MAIN_CORPUS':
        if res != 'MAIN_CORPUS' or nid not in ctx.main:
            raise OverlayError('MAIN_CORPUS_UNRESOLVABLE', f"{r['relation_id']}: {nid}")
        index = set(ctx.main[nid]['articles'])
    else:
        if nid in ctx.main:
            raise OverlayError('MAIN_CORPUS_NORM_DUPLICATED_AS_EXT', f"{r['relation_id']}: {nid}")
        on_card = nid in ctx.ext
        if res == 'ON_CARD' and not on_card:
            raise OverlayError('DESTINATION_NORM_NOT_FOUND', f"{r['relation_id']}: {nid}")
        if res == 'INGESTION_REQUIRED' and on_card:
            raise OverlayError('RESOLUTION_STALE_ALREADY_ON_CARD', f"{r['relation_id']}: {nid}")
        if res == 'MAIN_CORPUS':
            raise OverlayError('RESOLUTION_ROUTE_MISMATCH', r['relation_id'])
        index = ctx.ext_text_articles.get(nid, set()) if on_card else None  # None: destination not ingested, articles checked at ingestion
    for a in r['destination_articles']:
        if index is not None and a not in index:
            raise OverlayError('DESTINATION_ARTICLE_INVALID', f'{nid} art. {a}')
    return 'ARTICLES_VERIFIED' if index is not None else 'ARTICLES_DEFERRED_UNTIL_INGESTION'


def check_temporal(r):
    t, rid = r['temporal_status'], r['relation_id']
    if t not in TEMPORAL:
        raise OverlayError('TEMPORAL_STATUS_INVALID', rid)
    if t not in TEMPORAL_PUBLISHABLE:
        raise OverlayError('TEMPORAL_STATUS_NOT_PUBLISHABLE', f'{rid} ({t})')
    if t == 'VACATIO_LEGIS' and (r['vacatio_policy'] not in VACATIO_POLICIES or not DATE.match(r['effective_from'] or '')):
        raise OverlayError('VACATIO_WITHOUT_POLICY', rid)
    if t == 'TRANSITIONAL' and not r['revalidate_on']:
        raise OverlayError('TRANSITIONAL_WITHOUT_REVALIDATION', rid)
    judicial = 'JUDICIAL_RESTRICTIONS' in r['flags']
    if judicial or r['judicial_status']:
        j = r['judicial_status'] or {}
        if (not judicial or j.get('status') not in JUDICIAL_STATUSES or any(not j.get(k) for k in JUDICIAL_REQUIRED)
                or not DATE.match(j['decided_on']) or len(j['notice_short']) > NOTICE_MAX):
            raise OverlayError('JUDICIAL_RESTRICTIONS_INCOMPLETE', rid)
    elif t == 'PARTIAL_EFFECTS' and not (r['temporal_note'] and r['revalidate_on']):
        # non-judicial partial effects (e.g. staggered effects of a statute) must say why and when to revalidate
        raise OverlayError('PARTIAL_EFFECTS_WITHOUT_BASIS', rid)


def validate_record(r, ctx):
    missing = [f for f in FIELDS if f not in r] + [f for f in NON_EMPTY if r.get(f) in (None, '', [])]
    if missing:
        raise OverlayError('MISSING_FIELD', f"{r.get('relation_id')}: {missing[0]}")
    if r['review_status'] != APPROVED:
        raise OverlayError('NOT_APPROVED', r['relation_id'])
    legacy_only = all(d.startswith('LEGACY:') for d in r['decision_ids'])
    if r['relation_type'] not in RELATION_TYPES and not (legacy_only and r['relation_type'] == LEGACY_RELATION_TYPE):
        raise OverlayError('RELATION_TYPE_INVALID', r['relation_id'])
    if r['relation_id'] != relation_id_for(r['target_id'], r['destination_norm_id']):
        raise OverlayError('RELATION_ID_NOT_DETERMINISTIC', r['relation_id'])
    tgt = check_target(r['target_id'], ctx, r['relation_id'])
    art = check_destination(r, ctx)
    check_temporal(r)
    return dict(target_check=tgt, article_check=art)


def validate_records(records, ctx, materialized_only=False):
    """All records valid, one relation per legal identity (presentation unit x norm), unique relation ids."""
    out, seen, ids = [], {}, set()
    for r in records:
        chk = validate_record(r, ctx)
        if materialized_only and r['destination_resolution'] != 'ON_CARD':
            raise OverlayError('ADDITION_NOT_RESOLVABLE_ON_CARD', r['relation_id'])
        k = identity(r['target_id'], r['destination_norm_key'])
        if k in seen or r['relation_id'] in ids:
            raise OverlayError('DUPLICATE', f"{r['relation_id']} ({seen.get(k)})")
        seen[k], _ = r['relation_id'], ids.add(r['relation_id'])
        out.append(dict(record=r, **chk))
    return out


# ---------------------------------------------------------------- device classification (separate from legal validity)
def device_blockers(r, ctx, as_of):
    b = []
    if r['temporal_status'] == 'VACATIO_LEGIS' and as_of < r['effective_from']:
        b.append('TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE')
    if r['destination_resolution'] == 'INGESTION_REQUIRED':
        b.append('BLOCKED_INGESTION_REQUIRED')
    if r['destination_route'] not in DEVICE_ROUTES_SUPPORTED:
        b.append('BLOCKED_DEVICE_ROUTE_MAIN_CORPUS')
    if not any(o[0] == origin_of(r['target_id'])[0] for o in ctx.relacoes):
        b.append('BLOCKED_DEVICE_ORIGIN_UNVERIFIED')          # no RELACOES row of this namespace exists on the card yet
    if r['judicial_status'] and not DEVICE_JUDICIAL_NOTICE_SUPPORTED:
        b.append('BLOCKED_DEVICE_JUDICIAL_NOTICE_UNSUPPORTED')
    return b


# ---------------------------------------------------------------- legacy corrections
def validate_corrections(records, legacy_links, ctx):
    """Exactly one record per VISIBLE legacy CORRELATA link (no visible legacy link without a human decision); each record matches one link."""
    by_id = {l['reference_id']: l for l in legacy_links if l['reference_type'] == 'CORRELATA'}
    missing = sorted(k for k, l in by_id.items() if l['visibility'] == 'CURRENT_VISIBLE')
    missing = [k for k in missing if k not in {c.get('reference_id') for c in records}]
    if missing:
        raise OverlayError('LEGACY_LINK_WITHOUT_DECISION', missing[0])
    seen = set()
    for c in records:
        ref = c.get('reference_id')
        if ref in seen:
            raise OverlayError('CORRECTION_DUPLICATE', ref)
        seen.add(ref)
        if c.get('action') not in ACTIONS or c.get('status') != ACTIONS[c['action']]:
            raise OverlayError('CORRECTION_ACTION_INVALID', ref)
        if not c.get('decision_id') or not c.get('provenance'):
            raise OverlayError('CORRECTION_WITHOUT_DECISION', ref)
        l = by_id.get(ref)
        if not l or l['target_id'] != c['target_id'] or l['source_id'] != c['source_id'] or l['payload']['relacao_id'] != c['relation_id']:
            raise OverlayError('CORRECTION_LINK_NOT_FOUND', ref)
        if c['action'] == 'SUPPRESS_TEMPORAL' and not DATE.match(c.get('until') or ''):
            raise OverlayError('TEMPORAL_SUPPRESSION_WITHOUT_DATE', ref)
        if c['action'] == 'ROUTE_FIX':
            rf = c.get('route_fix') or {}
            if not rf.get('articles') or any(a not in ctx.ext_text_articles.get(c['source_id'], set()) for a in rf['articles']):
                raise OverlayError('ROUTE_FIX_ARTICLE_INVALID', ref)
    return records


def correction_effect(c, as_of):
    """Visible effect of a correction on the device export at `as_of`."""
    if c['action'] in ('EXCLUDE', 'SUPPRESS_HOLD'):
        return 'HIDDEN'
    if c['action'] == 'SUPPRESS_TEMPORAL':
        return 'HIDDEN' if as_of < c['until'] else 'VISIBLE'
    return 'VISIBLE'


# ---------------------------------------------------------------- links and card tables
def addition_link(r, ctx):
    status = ctx.engine_status(r['target_id'])
    link = dict(norma_id=ctx.norma_id, target_id=r['target_id'], reference_id=f"CORRELATA:{r['relation_id']}@{r['target_id']}",
                reference_type='CORRELATA', source_id=r['destination_norm_id'], source_reference_id=r['relation_id'],
                provenance=dict(system='CORRELATA_ADDITIONS (RUN4_CANDIDATE_HOST_ONLY)', relacao_id=r['relation_id'], review_status=r['review_status'],
                                decision_ids=r['decision_ids']),
                status=status, visibility=E._visibility(ctx.reg.cfg, status), label=E._clean(r['destination_norm_id']),
                payload=dict(destino=r['destination_norm_id'], relacao_id=r['relation_id']), migration=APPROVED,
                validation_status='VALIDATED', routes=[], duplicate_class='DISTINCT')
    E.validate_link(link, ctx.reg)
    return link


def device_route(dest, articles, ctx):
    """Device jump: only articles present in the card's EXT_ARTIGOS index; otherwise the C2 safe fallback (open the norm at the start)."""
    on_card = [a for a in articles if a in ctx.ext_articles.get(dest, set())]
    gap = [a for a in articles if a not in on_card]
    return ('ABRIR_ARTIGO_INTERNO' if on_card else 'ABRIR_NORMA_SEM_SALTO'), on_card, gap


def relacoes_row(origin, rel, dest, ctx, articles):
    n = ctx.ext[dest]
    mode, arts, _ = device_route(dest, articles, ctx)
    return tuple(origin) + (rel, dest, n['name'], mode, ','.join(arts), n['path'])


def write_relacoes(rows, ctx):
    """RELACOES.IDX + REL_LOOKUP.IDX in the card format: origins in structural order, rows of one origin by destination name."""
    def okey(o):
        return ctx.reg.order(ctx.norma_id, target_of_origin(o))
    groups = {}
    for r in rows:
        groups.setdefault(tuple(r[:5]), []).append(r)
    head = ('\n'.join(REL_HEADER) + '\n').encode('utf-8')
    body, lookup, off = [], [], len(head)
    for o in sorted(groups, key=okey):
        g = sorted(groups[o], key=lambda r: (r[7], r[5]))
        blob = ''.join('|'.join(r) + '\n' for r in g).encode('utf-8')
        lookup.append('|'.join(o) + f'|{off}|{len(g)}')
        body.append(blob)
        off += len(blob)
    rel = head + b''.join(body)
    look = ('\n'.join(LOOKUP_HEADER + tuple(lookup)) + '\n').encode('utf-8')
    return rel, look, dict(lookup_rows=len(lookup), norms=len({r[6] for r in rows}))
