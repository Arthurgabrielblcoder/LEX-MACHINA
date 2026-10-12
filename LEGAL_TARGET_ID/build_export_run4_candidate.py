"""Reference Engine RUN4_CANDIDATE_HOST_ONLY: RUN3 + CORRELATA overlay (corrections of legacy links + human-approved additions).

NOT a baseline, NOT physical, NOT deployed. RUN3 and every operational file stay untouched: this build only reads them.
  RUN3 links    reference_engine.build_links() (byte-identical to export_test/run3, checked here)
  corrections   derived/CF88_CORRELATA_EXCLUSIONS_CANDIDATE.json   one record per visible legacy CORRELATA link
  additions     derived/CF88_CORRELATA_ADDITIONS.json              materialized now (destination on the card)
  register      every legally approved relation (legal view; includes what cannot reach the device yet)
Two views, never confused (LEGAL_APPROVED != DEVICE_READY):
  legal_view/CF88_CORRELATA_LEGAL_VIEW.json   every decision with its legal state and its device state/blockers
  device_ready/                               what the CURRENT card + firmware could show without new ingestion or new firmware route:
                                              CF88_REFERENCES_EXPORT.json, REF_LOOKUP.IDX, REF_PAYLOAD.IDX, RELACOES.IDX, REL_LOOKUP.IDX
Usage: python build_export_run4_candidate.py [--out DIR]
"""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import reference_engine as E  # noqa: E402
import correlata_overlay as O  # noqa: E402

D = HERE / 'derived'
NORM = 'CF88'
AS_OF = '2026-10-12'
OUT = D / 'export_test/run4_candidate'
RUN3 = D / 'export_test/run3'
ADDITIONS = D / 'CF88_CORRELATA_ADDITIONS.json'
CORRECTIONS = D / 'CF88_CORRELATA_EXCLUSIONS_CANDIDATE.json'
AUDIT = ROOT / 'CORRELATA_COVERAGE_AUDIT'
REGISTER = AUDIT / 'C3A/CF88_CORRELATA_LEGAL_REGISTER_CANDIDATE.json'
PIN = AUDIT / 'inputs/CORRELATA_EVIDENCE_PIN.json'
CARD = AUDIT / 'C3A/inputs/card_relations_v2'
MAIN_INDEX = AUDIT / 'C3A/inputs/main_corpus_article_index.json'
EXT_TEXT_INDEX = AUDIT / 'C3A/inputs/ext_text_article_index.json'
STATUS = 'RUN4_CANDIDATE_HOST_ONLY'
RUN3_FILES = ('CF88_REFERENCES_EXPORT.json', 'REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def context(reg):
    dev = load(PIN)['device_tables']
    return O.Context(reg, NORM, dev['targets'], dev['text_map_targets'], CARD, MAIN_INDEX, EXT_TEXT_INDEX)


def build(out):
    out = Path(out)
    reg = E.TargetRegistry()
    links = E.build_links(NORM, reg)
    work_excl, work_add = E.link_exclusions(NORM, reg), E.work_reference_additions(NORM, reg)
    ctx = context(reg)
    corr = O.validate_corrections(load(CORRECTIONS)['records'], links, ctx)
    adds_doc, reg_doc = load(ADDITIONS), load(REGISTER)
    if adds_doc['review_status_required'] != O.APPROVED or reg_doc['review_status_required'] != O.APPROVED:
        raise O.OverlayError('OVERLAY_POLICY_INVALID', 'review_status_required')
    adds = O.validate_records(adds_doc['records'], ctx, materialized_only=True)
    register = O.validate_records(reg_doc['records'], ctx)
    reg_by_id = {v['record']['relation_id']: v['record'] for v in register}
    for v in adds:                                                  # additions are a faithful subset of the legal register
        if reg_by_id.get(v['record']['relation_id']) != v['record']:
            raise O.OverlayError('ADDITION_NOT_IN_REGISTER', v['record']['relation_id'])

    by_ref = {c['reference_id']: c for c in corr}
    effect = {c['reference_id']: O.correction_effect(c, AS_OF) for c in corr}
    device = [l for l in links if not (l['reference_type'] == 'CORRELATA' and effect.get(l['reference_id']) == 'HIDDEN')]
    kept_identity = {(O.presentation_unit(l['target_id']), l['source_id']): l['reference_id'] for l in device if l['reference_type'] == 'CORRELATA'}
    for v in register:                                              # a new relation never duplicates a legacy link still shown
        r = v['record']
        hit = kept_identity.get((O.presentation_unit(r['target_id']), r['destination_norm_id']))
        if hit:
            raise O.OverlayError('ADDITION_DUPLICATES_EXISTING_LINK', f"{r['relation_id']} = {hit}")
    materialized = {v['record']['relation_id'] for v in adds}
    entries, new_links = [], []
    for v in register:
        r = v['record']
        blockers = O.device_blockers(r, ctx, AS_OF)
        ready = r['relation_id'] in materialized and not blockers
        if ready:
            new_links.append(O.addition_link(r, ctx))
        entries.append(dict(kind='ADDITION', relation_id=r['relation_id'], target_id=r['target_id'], destination_norm_id=r['destination_norm_id'],
                            destination_norm_key=r['destination_norm_key'], destination_route=r['destination_route'],
                            destination_resolution=r['destination_resolution'], destination_articles=r['destination_articles'],
                            fallback=r['fallback'], relation_type=r['relation_type'], temporal_status=r['temporal_status'],
                            effective_from=r['effective_from'], revalidate_on=r['revalidate_on'], judicial_notice=(r['judicial_status'] or {}).get('notice_short'),
                            legal_state='LEGAL_APPROVED', materialized_in_additions=r['relation_id'] in materialized,
                            device_state='DEVICE_READY' if ready else (blockers[0] if blockers else 'NOT_MATERIALIZED_IN_C3A'),
                            device_blockers=blockers, target_check=v['target_check'], article_check=v['article_check'],
                            device_article_gap=O.device_route(r['destination_norm_id'], r['destination_articles'], ctx)[2]
                            if r['destination_resolution'] == 'ON_CARD' else [],
                            decision_ids=r['decision_ids'], supersedes=r['supersedes']))
    for l in links:
        if l['reference_type'] != 'CORRELATA':
            continue
        c = by_ref.get(l['reference_id'])
        if not c:
            state = 'HISTORICAL_HIDDEN_UNCHANGED'
        elif c['action'] in ('KEEP', 'ROUTE_FIX'):
            state = 'DEVICE_READY'
        elif c['action'] == 'SUPPRESS_TEMPORAL':
            state = 'TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE' if effect[l['reference_id']] == 'HIDDEN' else 'DEVICE_READY'
        else:
            state = c['status']
        entries.append(dict(kind='LEGACY', reference_id=l['reference_id'], target_id=l['target_id'], destination_norm_id=l['source_id'],
                            relation_id=l['payload']['relacao_id'], legacy_decision=c['decision'] if c else None, action=c['action'] if c else None,
                            route_fix=c.get('route_fix') if c else None, until=c.get('until') if c else None,
                            device_article_gap=O.device_route(l['source_id'], c['route_fix']['articles'], ctx)[2] if c and c['action'] == 'ROUTE_FIX' else [],
                            legal_state='LEGAL_KEPT' if c and c['action'] in ('KEEP', 'ROUTE_FIX', 'SUPPRESS_TEMPORAL') else
                            ('LEGAL_HOLD' if c and c['action'] == 'SUPPRESS_HOLD' else ('LEGAL_REMOVED' if c else 'HISTORICAL')),
                            device_state=state, decision_id=c['decision_id'] if c else None, note=c.get('reason') if c else None))

    # device-ready export (RUN3 links minus hidden legacy CORRELATA plus ready additions) and the RELACOES candidate
    device_links = device + new_links
    device_links.sort(key=lambda l: (reg.order(NORM, l['target_id']), E.TYPE_ORDER.get(l['reference_type'], 9), l['label'], l['reference_id']))
    card_rows = {(tuple(r[:5]), r[5]): r for r in ctx.relacoes}
    rows = []
    for l in device_links:
        if l['reference_type'] != 'CORRELATA':
            continue
        o, rel = O.origin_of(l['target_id']), l['payload']['relacao_id']
        if l['reference_id'] in by_ref or (o, rel) in card_rows and rel not in materialized:
            row = card_rows.get((o, rel))
            if not row:
                raise O.OverlayError('LEGACY_RELACOES_ROW_NOT_FOUND', l['reference_id'])
            c = by_ref.get(l['reference_id'])
            if c and c['action'] == 'ROUTE_FIX':
                row = O.relacoes_row(o, rel, row[6], ctx, c['route_fix']['articles'])
            rows.append(tuple(row))
        else:
            r = reg_by_id[rel]
            rows.append(O.relacoes_row(o, rel, r['destination_norm_id'], ctx, r['destination_articles']))
    rel_b, look_b, caps = O.write_relacoes(rows, ctx)
    for k, lim in O.FIRMWARE_CACHE.items():
        if caps[k] > lim:
            raise O.OverlayError('FIRMWARE_CACHE_EXCEEDED', f'{k}={caps[k]} > {lim}')
    hidden = [dict(reference_id=c['reference_id'], target_id=c['target_id'], source_id=c['source_id'], status=c['status'], decision_id=c['decision_id'])
              for c in corr if effect[c['reference_id']] == 'HIDDEN']
    dev_dir, legal_dir = out / 'device_ready', out / 'legal_view'
    files = E.export(NORM, device_links, dev_dir, list(work_excl) + hidden, work_add)
    (dev_dir / 'RELACOES.IDX').write_bytes(rel_b)
    (dev_dir / 'REL_LOOKUP.IDX').write_bytes(look_b)

    def cnt(kind, key='device_state'):
        return dict(sorted(collections.Counter(e[key] for e in entries if e['kind'] == kind).items()))
    run3_cor = [l for l in links if l['reference_type'] == 'CORRELATA']
    adds_e = [e for e in entries if e['kind'] == 'ADDITION']
    summary = dict(
        status=STATUS, as_of=AS_OF, principle='LEGAL_APPROVED != DEVICE_READY',
        run3=dict(correlata_total=len(run3_cor), visible=sum(l['visibility'] == 'CURRENT_VISIBLE' for l in run3_cor),
                  hidden_historical=sum(l['visibility'] != 'CURRENT_VISIBLE' for l in run3_cor)),
        legacy_actions=dict(sorted(collections.Counter(c['action'] for c in corr).items())),
        legacy_device_states=cnt('LEGACY'), additions_register=len(adds_e), additions_materialized=len(materialized),
        additions_device_states=cnt('ADDITION'),
        additions_blockers=dict(sorted(collections.Counter(b for e in adds_e for b in e['device_blockers']).items())),
        adct_runtime_confirmed=dict(total=sum(e['target_check'] == 'ADCT_RUNTIME_CONFIRMED' for e in adds_e),
                                    device_ready=sum(e['target_check'] == 'ADCT_RUNTIME_CONFIRMED' and e['device_state'] == 'DEVICE_READY' for e in adds_e)),
        legal_view=dict(entries=len(entries), legal_current_relations=sum(e['legal_state'] in ('LEGAL_APPROVED', 'LEGAL_KEPT') for e in entries)),
        device_ready=dict(correlata_links=sum(l['reference_type'] == 'CORRELATA' for l in device_links),
                          correlata_visible=sum(l['reference_type'] == 'CORRELATA' and l['visibility'] == 'CURRENT_VISIBLE' for l in device_links),
                          correlata_hidden_historical=sum(l['reference_type'] == 'CORRELATA' and l['visibility'] != 'CURRENT_VISIBLE' for l in device_links),
                          new_correlata_links=len(new_links), relacoes_rows=len(rows), firmware_cache=dict(used=caps, limit=O.FIRMWARE_CACHE),
                          non_correlata_links_identical_to_run3=[l for l in device_links if l['reference_type'] != 'CORRELATA'] ==
                          [l for l in links if l['reference_type'] != 'CORRELATA']),
        files={k: v for k, v in files.items()})
    legal_dir.mkdir(parents=True, exist_ok=True)
    legal = dict(schema_version=1, artifact='CF88_CORRELATA_LEGAL_VIEW', status=STATUS, as_of=AS_OF, principle=summary['principle'],
                 summary=summary, entries=entries)
    (legal_dir / 'CF88_CORRELATA_LEGAL_VIEW.json').write_bytes((json.dumps(legal, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    (out / 'RUN4_CANDIDATE_SUMMARY.json').write_bytes((json.dumps(summary, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    sums = sorted((p.relative_to(out).as_posix(), sha(p.read_bytes())) for p in out.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
    (out / 'SHA256SUMS.txt').write_bytes(''.join(f'{h}  {n}\n' for n, h in sums).encode('utf-8'))
    return summary


def run3_reproduced():
    """The RUN3 part is untouched: rebuilding RUN3 from the engine still matches the versioned RUN3 byte by byte."""
    import tempfile
    reg = E.TargetRegistry()
    with tempfile.TemporaryDirectory() as t:
        E.export(NORM, E.build_links(NORM, reg), t, E.link_exclusions(NORM, reg), E.work_reference_additions(NORM, reg))
        return all((Path(t) / f).read_bytes() == (RUN3 / f).read_bytes().replace(b'\r\n', b'\n') for f in RUN3_FILES)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(OUT))
    a = ap.parse_args()
    if not run3_reproduced():
        raise SystemExit('RUN3_NOT_REPRODUCED')
    s = build(a.out)
    print(json.dumps({k: s[k] for k in ('run3', 'legacy_actions', 'legacy_device_states', 'additions_device_states', 'adct_runtime_confirmed',
                                        'legal_view', 'device_ready')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
