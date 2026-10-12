"""C3A — derive the CORRELATA overlay inputs from the human decisions (HIGH consolidated + legacy full review). Nothing is decided here.

Writes (RUN4_CANDIDATE_HOST_ONLY; not referenced by engine_config.json nor by the RUN3 build):
  C3A/CF88_CORRELATA_LEGAL_REGISTER_CANDIDATE.json        every approved relation (77 HIGH + legacy retargets/replacements), merged by
                                                          legal identity (presentation unit x norm), with destination resolution
  LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json   the subset materialized now: destination already on the card (ON_CARD)
  LEGAL_TARGET_ID/derived/CF88_CORRELATA_EXCLUSIONS_CANDIDATE.json   one correction per legacy link whose decision is not a plain KEEP
Every record carries decision_ids back to the human decision. Usage: python build_c3a_overlay.py [--check]
"""
import argparse
import json
import re
import sys
from pathlib import Path

C3A = Path(__file__).resolve().parents[1]
AUDIT = C3A.parent
ROOT = AUDIT.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
sys.path.insert(0, str(AUDIT / 'tools'))
import correlata_overlay as O  # noqa: E402
import build_c1b_high_batch01 as B1  # noqa: E402
import build_c1b_high_batch02 as B2  # noqa: E402
import build_c1b_high_batch03 as B3  # noqa: E402
import build_c1b_high_batch04 as B4  # noqa: E402

CONSOLIDATED = AUDIT / 'CF88_CORRELATA_C1B_HIGH_CONSOLIDATED.json'
LEGACY = AUDIT / 'CF88_CORRELATA_LEGACY_FULL_REVIEW.json'
CANDS = AUDIT / 'CF88_CORRELATA_CANDIDATES.json'
OUT_REGISTER = C3A / 'CF88_CORRELATA_LEGAL_REGISTER_CANDIDATE.json'
OUT_ADDITIONS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json'
OUT_CORRECTIONS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_CORRELATA_EXCLUSIONS_CANDIDATE.json'
STATUS = 'RUN4_CANDIDATE_HOST_ONLY'
C2_VACATIO_POLICY = 'DO_NOT_PUBLISH_AS_CURRENT'          # approved in C2 for every VACATIO_LEGIS relation
ART = re.compile(r'(?:\barts?\.\s*|\be\s+(?:art\.\s*)?|,\s*)(\d+(?:-[A-Z])?)(?:º|°)?')
RES = {'EXTERNAL_ALREADY_INGESTED': ('EXT_NORMAS', 'ON_CARD'), 'IN_MAIN_CORPUS': ('MAIN_CORPUS', 'MAIN_CORPUS'),
       'INGESTION_REQUIRED': ('EXT_NORMAS', 'INGESTION_REQUIRED')}


def articles(text):
    out = []
    for a in ART.findall(text or ''):
        if a not in out:
            out.append(a)
    return out


def destination(norm_key, acervo):
    """(route, resolution, destination_norm_id) from the C0 acervo classification of the norm."""
    st, aid = acervo[norm_key]
    route, res = RES[st]
    return route, res, aid if res != 'INGESTION_REQUIRED' else f'PENDING_INGESTION:{norm_key}'


def acervo_map():
    out = {}
    for c in json.loads(CANDS.read_text(encoding='utf-8'))['candidates']:
        if c['acervo_status'] in RES:
            out.setdefault(c['norm_key'], (c['acervo_status'], c['acervo_id']))
    return out


def batch_routes():
    out = {}
    for mod in (B1, B2, B3, B4):
        for d in json.loads(mod.build()[1])['decisions']:
            out[d['candidate_id']] = d
    return out


def record(target, norm_key, norm_name, rel_type, basis, temporal, scope, flags, judicial, decision_ids, provenance, arts, acervo,
           supersedes=(), reviewer=''):
    route, res, nid = destination(norm_key, acervo)
    t = temporal or B3.IN_FORCE
    return dict(relation_id=O.relation_id_for(target, nid), target_id=target, destination_norm_id=nid, destination_norm_key=norm_key,
                destination_norm_name=norm_name, destination_route=route, destination_resolution=res, destination_articles=arts,
                fallback='OPEN_NORM_START', relation_type=rel_type, legal_basis=basis, scope=sorted(scope), flags=sorted(flags),
                temporal_status=t['temporal_status'], effective_from=t.get('effective_from') if t['temporal_status'] == 'VACATIO_LEGIS' else None,
                early_application_possible=t.get('early_application_possible'), revalidate_on=t.get('revalidate_on'), temporal_note=t.get('note'),
                vacatio_policy=C2_VACATIO_POLICY if t['temporal_status'] == 'VACATIO_LEGIS' else None, judicial_status=judicial,
                review_status=O.APPROVED, reviewer=reviewer, decision_ids=list(decision_ids), provenance=list(provenance),
                supersedes=list(supersedes))


def judicial_of(row):
    j = row.get('judicial')
    if not j:
        return None
    return dict(status=j['judicial_status'], cases=j['cases'], decided_on=j['merits_decided_on'], notice_short=j['notice_short'],
                checked_until=j['status_checked_until'], pending=j['embargos_status'], revalidate_on_final_ed=j['REVALIDATE_ON_FINAL_ED'])


def high_records(acervo):
    rows = json.loads(CONSOLIDATED.read_text(encoding='utf-8'))['candidates']
    routes = batch_routes()
    out = []
    for r in rows:
        if r['decision'] not in ('APPROVE', 'ADJUST'):
            continue
        d = routes[r['candidate_id']]
        basis = d.get('relevant_provisions') or r.get('final_analysis') or r['norm_name']
        out.append(record(r['target_final'], r['norm_key'], r['norm_name'], r['relation_type_final'], basis[:300], r['temporal'], r['scope'],
                          r.get('flags', []), judicial_of(r), [r['candidate_id']], [CONSOLIDATED.name], articles(d.get('route')), acervo,
                          reviewer=r.get('decision_source') or r['batch']))
    return out


def legacy_outputs(acervo):
    """Legacy decisions -> corrections (one per legacy link) + new relations (retarget destination, replacements)."""
    doc = json.loads(LEGACY.read_text(encoding='utf-8'))
    recs, corr, noop = [], [], []
    for l in doc['links']:
        dec, ref = l['decision'], l['reference_id']
        did = f"LEGACY:{l['review_round']}:{ref}"
        base = dict(reference_id=ref, target_id=l['target_id'], source_id=l['destination_norm_id'], relation_id=l['relation_id'],
                    decision=dec, decision_id=did, provenance=LEGACY.name)
        t = l.get('temporal') or B3.IN_FORCE
        if dec == 'KEEP':
            if t['temporal_status'] == 'VACATIO_LEGIS':
                corr.append(dict(base, action='SUPPRESS_TEMPORAL', status=O.ACTIONS['SUPPRESS_TEMPORAL'], until=t['effective_from'],
                                 reason='VACATIO_LEGIS: política C2 DO_NOT_PUBLISH_AS_CURRENT'))
            else:
                corr.append(dict(base, action='KEEP', status=O.ACTIONS['KEEP'], reason='KEEP'))
            continue
        if dec == 'KEEP_WITH_ROUTE_FIX':
            corr.append(dict(base, action='ROUTE_FIX', status=O.ACTIONS['ROUTE_FIX'], route_fix=l['route_fix'], reason='rota corrigida, mesmo vínculo'))
            continue
        if dec == 'HOLD':
            corr.append(dict(base, action='SUPPRESS_HOLD', status=O.ACTIONS['SUPPRESS_HOLD'],
                             reason='decisão humana HOLD preservada; não publicado no candidato; restaurável'))
            continue
        if dec == 'RETARGET' and O.presentation_unit(l['retarget_to']) == O.presentation_unit(l['target_id']):
            noop.append(dict(base, effect='PRESENTATION_EQUIVALENT_RETARGET_NOOP', retarget_to=l['retarget_to']))
            corr.append(dict(base, action='KEEP', status=O.ACTIONS['KEEP'], reason='PRESENTATION_EQUIVALENT_RETARGET_NOOP (ART = CAPUT)',
                             retarget_to=l['retarget_to']))
            continue
        corr.append(dict(base, action='EXCLUDE', status=O.ACTIONS['EXCLUDE'], reason=dec))
        if dec == 'RETARGET':
            arts = (l['route_fix'] or {}).get('articles') if isinstance(l['route_fix'], dict) else None
            recs.append(record(l['retarget_to'], l['destination_norm_key'], l['destination_norm_name'], None, l['legal_analysis'][:300], l.get('temporal'),
                               l.get('scope', []), [], None, [did], [LEGACY.name], arts or l['current_route']['articles'], acervo,
                               supersedes=[ref], reviewer=l['review_round']))
        elif dec == 'REPLACE':
            for n in l['replacement_norms']:
                recs.append(record(n['target_id'], n['norm_key'], n['norm_name'], n['relation_type'], l['legal_analysis'][:300], None, [], [], None,
                                   [did], [LEGACY.name], articles(n.get('route')), acervo, supersedes=[ref], reviewer=l['review_round']))
    return recs, corr, noop


def merge(records):
    """One relation per legal identity. Records of the same identity coming from different decisions are collapsed (decision ids united);
    a conflict on relation type, temporal status or destination stops the build."""
    by = {}
    for r in records:
        k = O.identity(r['target_id'], r['destination_norm_key'])
        if k not in by:
            by[k] = r
            continue
        m = by[k]
        if r['relation_type'] and m['relation_type'] and r['relation_type'] != m['relation_type']:
            raise SystemExit(f'DECISION_CONFLICT relation_type {k}')
        if r['temporal_status'] != m['temporal_status'] or r['destination_norm_id'] != m['destination_norm_id']:
            raise SystemExit(f'DECISION_CONFLICT {k}')
        m['relation_type'] = m['relation_type'] or r['relation_type']
        for f in ('decision_ids', 'provenance', 'supersedes'):
            m[f] = sorted(set(m[f]) | set(r[f]))
        m['destination_articles'] = m['destination_articles'] or r['destination_articles']
        m['merged_from_identities'] = m.get('merged_from_identities', 1) + 1
    out = list(by.values())
    for r in out:
        if not r['relation_type']:
            if not all(d.startswith('LEGACY:') for d in r['decision_ids']):
                raise SystemExit(f"RELATION_TYPE_MISSING {r['relation_id']}")
            r['relation_type'] = O.LEGACY_RELATION_TYPE        # not decided by the legacy review; no new legal decision here
    return sorted(out, key=lambda r: (r['target_id'], r['destination_norm_key']))


def jdump(o):
    return (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def build():
    acervo = acervo_map()
    high = high_records(acervo)
    leg, corr, noop = legacy_outputs(acervo)
    reg = merge(high + leg)
    common = dict(schema_version=1, status=STATUS, candidate_only=True, review_status_required=O.APPROVED,
                  principle='LEGAL_APPROVED != DEVICE_READY: estar aqui não significa aparecer no aparelho.')
    register = dict(common, artifact='CF88_CORRELATA_LEGAL_REGISTER_CANDIDATE', sources=[CONSOLIDATED.name, LEGACY.name],
                    counts=dict(high_accepted=len(high), legacy_new_relations=len(leg), merged_relations=len(reg),
                                collapsed_duplicates=len(high) + len(leg) - len(reg)),
                    records=reg, presentation_equivalent_noop=noop)
    adds = [r for r in reg if r['destination_resolution'] == 'ON_CARD']
    additions = dict(common, artifact='CF88_CORRELATA_ADDITIONS', norma_id='CF88', materialization_policy='DESTINATION_ON_CARD_ONLY',
                     policy='Overlay de relações CORRELATA aprovadas por humano. O catálogo legado não é editado. Nesta C3A só entram relações '
                            'cujo destino já está no cartão; as demais ficam no registro jurídico.', records=adds)
    corrections = dict(common, artifact='CF88_CORRELATA_EXCLUSIONS_CANDIDATE', norma_id='CF88', actions=O.ACTIONS,
                       policy='Uma correção por vínculo legado (reference_id). O catálogo canônico e CF88_LINK_EXCLUSIONS.json não são editados. '
                              'REVIEW_HOLD_SUPPRESSED e TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE preservam a decisão e são reversíveis.',
                       records=sorted(corr, key=lambda c: c['reference_id']))
    return jdump(register), jdump(additions), jdump(corrections)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out = build()
    if out != build():
        raise SystemExit('NOT_DETERMINISTIC')
    paths = (OUT_REGISTER, OUT_ADDITIONS, OUT_CORRECTIONS)
    if a.check:
        ok = all(p.read_bytes().replace(b'\r\n', b'\n') == b for p, b in zip(paths, out))
        print('check', 'OK' if ok else 'DIFF')
        sys.exit(0 if ok else 1)
    for p, b in zip(paths, out):
        p.write_bytes(b)
    print(json.dumps(json.loads(out[0])['counts']), len(json.loads(out[1])['records']), len(json.loads(out[2])['records']))


if __name__ == '__main__':
    main()
