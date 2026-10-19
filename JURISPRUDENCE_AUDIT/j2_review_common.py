"""J2 — common validator for batch review modules (Batches 03+). Each review module provides SOURCES and REVIEW (one entry per selected
recommendation) and calls make_decisions(doc, REVIEW, SOURCES). Every decision is a PROPOSAL (AWAITING_USER_RATIFICATION); this module
never marks anything human-approved. The Fase D detectors run over the stored official excerpt and are recorded next to the decision.
"""
import re

import j2_auditors as AUD
import juris_types as JT

DECISIONS = ('PROMOTE_RECOMMENDED', 'PROMOTE_PROVISIONAL_RECOMMENDED', 'REALLOCATE_RECOMMENDED', 'REJECT_FALSE_POSITIVE_RECOMMENDED',
             'REJECT_TEMPORAL_MISMATCH_RECOMMENDED', 'REJECT_NOT_MATERIAL_RECOMMENDED', 'ALREADY_COVERED', 'DUPLICATE_RECOMMENDATION',
             'UNRESOLVED_EXTERNAL', 'UNRESOLVED_IDENTIFICATION')
TEMPORAL = ('CURRENT', 'HISTORICAL', 'MIXED', 'NOT_APPLICABLE')
# Frozen table used by Batches 03–10 (their decision files are pinned by hash). Batch11+ asks juris_types.device_status (single source).
LEGACY_DEVICE_TYPES = {'RG': 'VALIDATED', 'SV': 'VALIDATED', 'ADI': 'VALIDATED', 'HC': 'FIRMWARE_PROTOTYPE_ONLY',
                'SUMULA': 'FIRMWARE_LABEL_EXISTS_NOT_PHYSICALLY_VALIDATED', 'ADC': 'FIRMWARE_LABEL_EXISTS_NOT_PHYSICALLY_VALIDATED',
                'ADPF': 'FIRMWARE_LABEL_EXISTS_NOT_PHYSICALLY_VALIDATED'}
FIELDS = ('precedents', 'namespace', 'namespace_evidence', 'temporal_version', 'temporal_note', 'target_check', 'recommended_targets',
          'decision', 'confidence', 'status_processual', 'sources', 'evidence_excerpt', 'reason')
LEGACY_DEVICE_TABLE_LAST_BATCH = 10


def device_status(doc, klass):
    n = int(re.sub(r'\D', '', doc['batch']))
    if n <= LEGACY_DEVICE_TABLE_LAST_BATCH:
        return LEGACY_DEVICE_TYPES.get(klass, 'NEW_JURIS_TYPE_REQUIRES_DESIGN')
    return JT.physical_status(klass)


PROMOTING = ('PROMOTE_RECOMMENDED', 'PROMOTE_PROVISIONAL_RECOMMENDED', 'REALLOCATE_RECOMMENDED')


def make_decisions(doc, REVIEW, SOURCES):
    if sorted(REVIEW) != sorted(doc['selected']):
        raise SystemExit('REVIEW_DOES_NOT_MATCH_SELECTION')
    q = {x['recommendation_id']: x for x in doc['queue']}
    out = []
    for rid in doc['selected']:
        r = REVIEW[rid]
        missing = [f for f in FIELDS if f not in r]
        if missing or r['decision'] not in DECISIONS or r['temporal_version'] not in TEMPORAL or any(s not in SOURCES for s in r['sources']):
            raise SystemExit(f'INCOMPLETE_REVIEW {rid} {missing}')
        for p in r['precedents']:
            if not all(k in p for k in ('id', 'court', 'klass', 'number', 'judgment', 'publication')):
                raise SystemExit(f'INCOMPLETE_PRECEDENT {rid}')
        if r['decision'] in PROMOTING:
            article_only = all(len(t.split(':')) == 2 for t in r['recommended_targets'])
            historical_ok = r['temporal_version'] in ('HISTORICAL', 'MIXED') and article_only and len(r['temporal_note']) > 20
            # J1.4/J2B.1 policy: a precedent on a historical wording may only be linked at article level, with an explicit temporal note
            if not r['recommended_targets'] or r['namespace'] not in ('CF88', 'ADCT') or not (r['temporal_version'] == 'CURRENT' or historical_ok):
                raise SystemExit(f'PROMOTION_WITHOUT_TARGET_NAMESPACE_OR_CURRENT_TEXT {rid}')
            if any(not t.startswith('ADCT:' if r['namespace'] == 'ADCT' else 'CF88:') for t in r['recommended_targets']):
                raise SystemExit(f'TARGET_NAMESPACE_MISMATCH {rid}')
        if r['decision'] == 'PROMOTE_PROVISIONAL_RECOMMENDED' and not r.get('revalidation'):
            raise SystemExit(f'PROVISIONAL_WITHOUT_REVALIDATION {rid}')
        types = sorted({p['klass'] for p in r['precedents']})
        device = {t: device_status(doc, t) for t in types}
        out.append(dict(recommendation_id=rid, rank=q[rid]['rank'], recommended_by_backlog=q[rid]['target_id'],
                        original_recommendation=q[rid]['desired_reference'], suggested_identifiers=q[rid]['suggested_identifiers'], **r,
                        NAMESPACE_CHECK='PASS' if r['namespace'] in ('CF88', 'ADCT') else 'FAIL', TEMPORAL_CHECK='DONE',
                        OFFICIAL_SOURCE_REVIEWED=all(SOURCES[s]['tier'] == 'A' for s in r['sources']) and not r['decision'].startswith('UNRESOLVED'),
                        device_type_status=device,
                        NEW_JURIS_TYPE_REQUIRES_DESIGN='YES' if any(v != 'VALIDATED' for v in device.values()) else 'NO',
                        auditor_flags=AUD.review_flags(q[rid]['recommendation_text'], r['evidence_excerpt']),
                        status='AWAITING_USER_RATIFICATION', human_approved=False))
    return out
