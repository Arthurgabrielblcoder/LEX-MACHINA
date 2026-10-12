"""C2 prototype — fail-closed validator for the future CORRELATA additions overlay (LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json).

PROTOTYPE ONLY: it is not wired into reference_engine.py, the RUN3 export, REF_LOOKUP/REF_PAYLOAD, the card or the firmware. It proves the
C2 rules on a handful of fixtures:
  - the legacy catalog stays immutable; new relations enter only through additions with review_status HUMAN_APPROVED_CORRELATA_V1;
  - target must exist and be CURRENT/STRUCTURAL in the engine; an ADCT target whose engine status is UNKNOWN_VALIDITY is accepted only
    when the device runtime confirms it (legal_status CURRENT, present in TARGETS and reachable in TEXT_MAP) — UNKNOWN is never opened
    generically;
  - destination_route MAIN_CORPUS for norms of the main collection (never duplicated as EXT_NORMAS) and EXT_NORMAS for external norms;
  - destination articles must exist in the destination article index; an empty list needs the explicit OPEN_NORM fallback;
  - VACATIO_LEGIS needs effective_from + vacatio_policy; TRANSITIONAL needs revalidate_on; PARTIAL_EFFECTS/JUDICIAL_RESTRICTIONS need a
    complete judicial_status with a short notice.
Any error stops the build (OverlayError) — no partial overlay.
"""
import json
import re
import sys
from pathlib import Path

C2 = Path(__file__).resolve().parents[1]
AUDIT = C2.parent
ROOT = AUDIT.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import target_id as T  # noqa: E402

APPROVED = 'HUMAN_APPROVED_CORRELATA_V1'
ROUTES = ('MAIN_CORPUS', 'EXT_NORMAS')
RELATION_TYPES = ('REGULAMENTA', 'COMPLEMENTA', 'IMPLEMENTA', 'PROCEDIMENTO', 'CONDIÇÃO_OU_EXCEÇÃO', 'ORGANIZA_INSTITUIÇÃO')
TEMPORAL = ('IN_FORCE', 'VACATIO_LEGIS', 'PARTIAL_EFFECTS', 'TRANSITIONAL', 'REVOKED', 'UNCERTAIN')
VACATIO_POLICIES = ('DO_NOT_PUBLISH_AS_CURRENT',)
JUDICIAL_STATUSES = ('STF_PARTIAL_UNCONSTITUTIONALITY', 'STF_INTERPRETATION_CONFORME', 'STF_SUSPENDED_INJUNCTION', 'STF_PARTIAL_EFFECTS',
                     'PENDING_JUDICIAL_REVALIDATION')
JUDICIAL_REQUIRED = ('status', 'cases', 'decided_on', 'notice_short', 'checked_until')
NOTICE_MAX = 80
FIELDS = ('relation_id', 'target_id', 'destination_norm_id', 'destination_route', 'destination_articles', 'relation_type', 'legal_basis',
          'scope', 'flags', 'temporal_status', 'effective_from', 'early_application_possible', 'revalidate_on', 'vacatio_policy',
          'judicial_status', 'review_status', 'reviewer', 'decision_id', 'provenance')
REQUIRED_NON_EMPTY = ('relation_id', 'target_id', 'destination_norm_id', 'destination_route', 'relation_type', 'legal_basis', 'temporal_status',
                      'review_status', 'reviewer', 'decision_id', 'provenance')
ENGINE_OK = ('CURRENT', 'STRUCTURAL')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


class OverlayError(Exception):
    def __init__(self, code, ref):
        super().__init__(f'{code}: {ref}')
        self.code, self.ref = code, ref


def load_context(registry_path=C2 / 'fixtures/destination_registry.json'):
    """Read-only context: engine target status, device runtime tables (C0 evidence pin) and the destination registry."""
    status = json.loads((ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS.json').read_text(encoding='utf-8'))['targets']
    dev = json.loads((AUDIT / 'inputs/CORRELATA_EVIDENCE_PIN.json').read_text(encoding='utf-8'))['device_tables']
    reg = {n['norm_id']: n for n in json.loads(Path(registry_path).read_text(encoding='utf-8'))['norms']}
    return dict(engine=status, runtime=dev['targets'], text_map=set(dev['text_map_targets']), registry=reg)


def _check_target(r, ctx):
    tid = r['target_id']
    if not T.validate_target_id(tid)[0] or tid not in ctx['engine']:
        raise OverlayError('TARGET_NOT_FOUND', tid)
    eng = ctx['engine'][tid]['status']
    rt = ctx['runtime'].get(tid)
    if eng == 'HISTORICAL_ONLY' or (rt and rt['legal_status'] != 'CURRENT'):
        raise OverlayError('TARGET_HISTORICAL_OR_REVOKED', tid)
    if eng in ENGINE_OK:
        return 'ENGINE_' + eng
    if eng == 'UNKNOWN_VALIDITY' and tid.startswith('ADCT:'):
        if rt and rt['legal_status'] == 'CURRENT' and tid in ctx['text_map']:
            return 'ADCT_RUNTIME_CONFIRMED'
        raise OverlayError('ADCT_NOT_CONFIRMED_BY_RUNTIME', tid)
    raise OverlayError('TARGET_STATUS_NOT_ALLOWED', f'{tid} ({eng})')


def _check_destination(r, ctx):
    n = ctx['registry'].get(r['destination_norm_id'])
    route = r['destination_route']
    if route not in ROUTES:
        raise OverlayError('ROUTE_INVALID', f"{r['relation_id']} ({route})")
    if not n:
        raise OverlayError('DESTINATION_NORM_NOT_FOUND', r['destination_norm_id'])
    if route == 'MAIN_CORPUS' and n['route'] != 'MAIN_CORPUS':
        raise OverlayError('MAIN_CORPUS_UNRESOLVABLE', r['destination_norm_id'])
    if route == 'EXT_NORMAS' and n['route'] == 'MAIN_CORPUS':
        raise OverlayError('MAIN_CORPUS_NORM_DUPLICATED_AS_EXT', r['destination_norm_id'])
    arts = r['destination_articles']
    if not arts and 'OPEN_NORM_FALLBACK' not in r['flags']:
        raise OverlayError('DESTINATION_ARTICLES_EMPTY_WITHOUT_FALLBACK', r['relation_id'])
    for a in arts:
        if a not in n['article_index']['articles']:
            raise OverlayError('DESTINATION_ARTICLE_INVALID', f"{r['destination_norm_id']} art. {a}")
    return n


def _check_temporal(r):
    t = r['temporal_status']
    if t not in TEMPORAL:
        raise OverlayError('TEMPORAL_STATUS_INVALID', r['relation_id'])
    if t in ('REVOKED', 'UNCERTAIN'):
        raise OverlayError('TEMPORAL_STATUS_NOT_PUBLISHABLE', f"{r['relation_id']} ({t})")
    if t == 'VACATIO_LEGIS':
        if r['vacatio_policy'] not in VACATIO_POLICIES or not DATE.match(r['effective_from'] or ''):
            raise OverlayError('VACATIO_WITHOUT_POLICY', r['relation_id'])
    if t == 'TRANSITIONAL' and not r['revalidate_on']:
        raise OverlayError('TRANSITIONAL_WITHOUT_REVALIDATION', r['relation_id'])
    if t == 'PARTIAL_EFFECTS' or 'JUDICIAL_RESTRICTIONS' in r['flags']:
        j = r['judicial_status'] or {}
        if (j.get('status') not in JUDICIAL_STATUSES or any(not j.get(k) for k in JUDICIAL_REQUIRED)
                or not DATE.match(j['decided_on']) or len(j['notice_short']) > NOTICE_MAX or 'JUDICIAL_RESTRICTIONS' not in r['flags']):
            raise OverlayError('JUDICIAL_RESTRICTIONS_INCOMPLETE', r['relation_id'])


def validate(records, ctx, as_of):
    """Validate every record (fail closed) and return the device decision of each one; nothing is written anywhere."""
    out, seen = [], set()
    for r in records:
        missing = [f for f in FIELDS if f not in r] + [f for f in REQUIRED_NON_EMPTY if r.get(f) in (None, '')]
        if missing:
            raise OverlayError('MISSING_FIELD', f"{r.get('relation_id')}: {missing[0]}")
        if r['review_status'] != APPROVED:
            raise OverlayError('NOT_APPROVED', r['relation_id'])
        if r['relation_type'] not in RELATION_TYPES:
            raise OverlayError('RELATION_TYPE_INVALID', r['relation_id'])
        tgt = _check_target(r, ctx)
        n = _check_destination(r, ctx)
        _check_temporal(r)
        key = (r['target_id'], r['destination_norm_id'])
        if key in seen or r['relation_id'] in {o['relation_id'] for o in out}:
            raise OverlayError('DUPLICATE', r['relation_id'])
        seen.add(key)
        if r['temporal_status'] == 'VACATIO_LEGIS' and as_of < r['effective_from']:
            device = 'HIDDEN_UNTIL_EFFECTIVE'
        elif not n['on_card']:
            device = 'BLOCKED_INGESTION_REQUIRED'
        elif r['judicial_status']:
            device = 'PUBLISH_WITH_JUDICIAL_NOTICE'
        else:
            device = 'PUBLISH'
        out.append(dict(relation_id=r['relation_id'], target_id=r['target_id'], target_check=tgt, destination_route=r['destination_route'],
                        destination_norm_id=r['destination_norm_id'], destination_articles=r['destination_articles'], device=device,
                        notice=(r['judicial_status'] or {}).get('notice_short'), revalidate_on=r['revalidate_on']))
    return out


def validate_file(path, ctx, as_of):
    return validate(json.loads(Path(path).read_text(encoding='utf-8'))['records'], ctx, as_of)


if __name__ == '__main__':
    ctx = load_context()
    for res in validate_file(C2 / 'fixtures/correlata_additions_fixture.json', ctx, sys.argv[1] if len(sys.argv) > 1 else '2026-10-11'):
        print(json.dumps(res, ensure_ascii=False))
