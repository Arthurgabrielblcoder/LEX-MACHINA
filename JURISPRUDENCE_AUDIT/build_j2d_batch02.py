"""J2D — HIGH backlog rebuilt over the CURRENT installed baseline (261, J2C 12/12) minus everything Batch01 resolved, and deterministic
selection of BATCH02 (10). Host-only, read-only, deterministic, no network. The legal review of the 10 (official sources) lives in
J2_HIGH_BACKLOG/j2d_batch02_review.py and is merged here; nothing is materialized.

Reads:   J0_DIAGNOSTIC_AUDIT.json + ENTENDA recommendation files (same J0 rule, via build_j2a_batch01.reconstruct),
         J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json (the 10 resolved recommendations and their (target, precedent) pairs),
         J2B_1_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX (installed bytes, 261 visible).
Priority: the J0 rule (named identifier, recurrence, article without jurisprudence, reference described; HIGH >= 3) recomputed over the
CURRENT pending set (Batch01 removed), so recurrence and article coverage reflect the 261.
Selection (J2D order, lexicographic): 1 explicit identifier, 2 direct constitutional weight, 3 target without jurisprudence, 4 recurrence,
5 practical relevance (article without jurisprudence), 6 low ambiguity, 7 recommendation_id.
Writes:  J2_HIGH_BACKLOG/J2D_BATCH02_DECISIONS.json.   Usage: python build_j2d_batch02.py [--check] [--selection-only]
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_DIR = HERE / 'J2_HIGH_BACKLOG'
OUT = OUT_DIR / 'J2D_BATCH02_DECISIONS.json'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(OUT_DIR))
import build_j2a_batch01 as B  # noqa: E402
import build_j0_diagnostic_audit as J0  # noqa: E402

CURRENT = HERE / 'J2B_1_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'
CURRENT_SHA = '62b06deb45b3c1ec9e2ead4fe577241b78658fc62d67f91516b61841e83456e9'   # installed on the card (J2C, 12/12)
BATCH01 = OUT_DIR / 'J2A_BATCH01_DECISIONS.json'
BATCH_SIZE = 10
J0_IDENT = __import__('re').compile(r'\b(ADI|ADC|ADPF|ADO|RE|ARE|MS|HC|RHC|MI|Rcl|AI|ACO|AP|Inq|Pet)\s*\d[\d.]*|\bTema\s*\d+|'
                                   r'\bS[uú]mula\s+(Vinculante\s+)?\d+|\bSV\s*\d+', __import__('re').I)
SELECTION_RULES = {
    '1_explicit_identifier': '2 = a referência nomeia exatamente um identificador; 1 = identificadores só na nota ou mais de um; 0 = nenhum',
    '2_direct_constitutional_weight': '2 = precedente de efeito geral/vinculante (ADI/ADC/ADO/ADPF, Tema RG, SV); 1 = outras classes do STF / súmula comum',
    '3_target_without_juris': '1 = o target exato não tem jurisprudência visível na base de 261',
    '4_recurrence': '1 = o mesmo identificador aparece em mais de uma recomendação pendente (ou occurrences > 1)',
    '5_practical_relevance': '1 = o artigo não tem nenhuma jurisprudência visível (lacuna)',
    '6_low_ambiguity': '1 = um único identificador e referência descrita (não IDENTIFICACAO_PENDENTE)',
    '7_tiebreak': 'recommendation_id crescente',
}


def current_baseline():
    if B.sha(CURRENT) != CURRENT_SHA:
        raise SystemExit('CURRENT_BASELINE_NOT_INSTALLED_BYTES')
    rows = [l.split('|') for l in CURRENT.read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')]
    vis = [r for r in rows if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
    if (len(vis), len({r[0] for r in vis})) != (261, 160):
        raise SystemExit('CURRENT_BASELINE_NOT_261')
    return vis


def reconstruct():
    original = B.current_baseline
    B.current_baseline = current_baseline                       # J0 categories over the 261 (fail closed if they differ from J0)
    try:
        items, _, j0 = B.reconstruct()
    finally:
        B.current_baseline = original                           # never leak the patch into the J2A builder
    vis = current_baseline()
    vis_targets = {r[0] for r in vis}
    art_with = {':'.join(t.split(':')[:2]) for t in vis_targets}
    b1 = json.loads(BATCH01.read_text(encoding='utf-8'))
    resolved = {d['recommendation_id']: d['decision'] for d in b1['decisions']}
    resolved_pairs = {(d['recommended_by_backlog'], d['precedent']) for d in b1['decisions']}
    pending = [b for b in items if b['category'] == 'NEEDS_EXTERNAL_INGESTION' and b['recommendation_id'] not in resolved]
    covered = {}                                   # notes whose identifiers on the same target were already decided in Batch01
    for b in pending:
        ids = B.ids_in(f"{b['desired_reference']} {b['recommendation_text']}")
        ov = sorted(f'{t}|{p}' for t, p in resolved_pairs if t == b['target_id'] and
                    any(p.split(':')[-1].split('-')[0] in i.replace(' ', '') for i in ids))
        if ov:
            covered[b['recommendation_id']] = dict(target=b['target_id'], resolved_pairs=ov)
    pending = [b for b in pending if b['recommendation_id'] not in covered]
    dup_desired = collections.Counter(J0.norm(b['desired_reference']) for b in pending)
    id_count = collections.Counter(i for b in pending for i in B.ids_in(f"{b['desired_reference']} {b['recommendation_text']}"))
    for b in pending:
        text = f"{b['desired_reference']} {b['recommendation_text'][:300]}"
        named = sorted({m.group(0).strip() for m in J0_IDENT.finditer(text)})   # J0 priority rule, unchanged (no "ADIN")
        art_has = ':'.join(b['target_id'].split(':')[:2]) in art_with
        tgt_has = any(k in vis_targets for k in (b['target_id'], b['target_id'] + ':CAPUT', b['target_id'].removesuffix(':CAPUT')))
        recurrent = b['occurrences'] > 1 or dup_desired[J0.norm(b['desired_reference'])] > 1
        described = bool(b['desired_reference'] and b['desired_reference'] != 'IDENTIFICACAO_PENDENTE')
        score = (1 if named else 0) + (1 if recurrent else 0) + (0 if art_has else 1) + (1 if described else 0)
        b['priority'] = 'HIGH' if score >= 3 else 'MEDIUM' if score == 2 else 'LOW'
        b['priority_reason'] = dict(named_identifier=bool(named), recurrent=recurrent, article_without_juris=not art_has, reference_described=described)
        ref_ids = B.ids_in(b['desired_reference'] if described else '')
        all_ids = B.ids_in(f"{b['desired_reference']} {b['recommendation_text']}")
        b['suggested_identifiers'] = all_ids
        b['suggested_type'] = sorted({i.split(' ')[0] for i in all_ids})
        b['current_baseline_equivalent'] = dict(target_has_juris=tgt_has, article_has_juris=art_has,
                                                target_juris_now=sorted(r[5] for r in vis if r[0] == b['target_id']))
        b['resolved_pair_overlap'] = sorted(f'{t}|{p}' for t, p in resolved_pairs if t == b['target_id'] and
                                            any(p.split(':')[-1].split('-')[0] in i.replace(' ', '') for i in all_ids))
        b['selection_scores'] = {
            '1_explicit_identifier': 2 if len(ref_ids) == 1 else 1 if all_ids else 0,
            '2_direct_constitutional_weight': 2 if all_ids and all(B.GENERAL_EFFECT.match(i) for i in (ref_ids or all_ids)) else 1 if all_ids else 0,
            '3_target_without_juris': 0 if tgt_has else 1,
            '4_recurrence': 1 if b['occurrences'] > 1 or any(id_count[i] > 1 for i in all_ids) else 0,
            '5_practical_relevance': 0 if art_has else 1,
            '6_low_ambiguity': 1 if len(all_ids) == 1 and described else 0}
    return items, pending, resolved, covered, j0


def select(pending):
    high = [b for b in pending if b['priority'] == 'HIGH']
    key = lambda b: tuple(-b['selection_scores'][k] for k in sorted(b['selection_scores'])) + (b['recommendation_id'],)  # noqa: E731
    ranked = sorted(high, key=key)
    return high, ranked, [b['recommendation_id'] for b in ranked[:BATCH_SIZE]]


def build(selection_only=False):
    items, pending, resolved, covered, j0 = reconstruct()
    high, ranked, chosen = select(pending)
    cnt = collections.Counter(b['priority'] for b in pending)
    old = {b['recommendation_id'] for b in json.loads(BATCH01.read_text(encoding='utf-8'))['high_queue']}   # the 42 HIGH of J2A
    recon = dict(BACKLOG_PENDING_J2A=148, RESOLVED_BY_BATCH01=sorted(resolved), COVERED_BY_BATCH01=covered, BACKLOG_PENDING_CURRENT=len(pending),
                 BACKLOG_TARGETS_CURRENT=len({b['target_id'] for b in pending}), HIGH_CURRENT=cnt['HIGH'], MEDIUM_CURRENT=cnt['MEDIUM'],
                 LOW_CURRENT=cnt['LOW'], HIGH_J2A=42,
                 left_high=sorted(r for r in old if r not in resolved and r not in {b['recommendation_id'] for b in high}),
                 entered_high=sorted(b['recommendation_id'] for b in high if b['recommendation_id'] not in old),
                 RESOLVED_BATCH01_REENTERED=sum(1 for b in pending if b['recommendation_id'] in resolved or b['resolved_pair_overlap']))
    for r in recon['left_high']:
        b = next(x for x in pending if x['recommendation_id'] == r)
        recon.setdefault('left_high_reason', {})[r] = dict(target=b['target_id'], now=b['priority'], reason=b['priority_reason'])
    doc = dict(schema_version=1, round='J2D', batch='BATCH02', mode='HOST_ONLY_DECISIONS_NO_MATERIALIZATION', status='AWAITING_USER_RATIFICATION',
               current_baseline=dict(file=CURRENT.relative_to(ROOT).as_posix(), sha256=CURRENT_SHA, JURIS_RELATIONS=261, JURIS_TARGETS=160,
                                     physical='J2C_PHYSICAL_VALIDATION = 12/12 PASS'),
               inputs={f.relative_to(ROOT).as_posix(): B.sha_lf(f) for f in
                       [B.J0_AUDIT, BATCH01] + [ROOT / f'ENTENDA_ENGINE/derived/{b}/JURISPRUDENCE_LINK_RECOMMENDATIONS.json' for b in J0.BATCHES]},
               reconstruction=recon, selection_rules=SELECTION_RULES,
               high_queue=[{k: b[k] for k in ('recommendation_id', 'target_id', 'desired_reference', 'origin', 'occurrences', 'suggested_identifiers',
                                             'suggested_type', 'priority_reason', 'current_baseline_equivalent', 'selection_scores')}
                           | dict(rank=ranked.index(b) + 1, recommendation_text=b['recommendation_text'][:400]) for b in sorted(high, key=lambda b: b['recommendation_id'])],
               selected=chosen, HIGH_REMAINING_AFTER_BATCH=len(high) - len(chosen))
    if not selection_only:
        import j2d_batch02_review as R
        decisions = R.decisions(doc)
        doc.update(sources=R.SOURCES, decisions=decisions, totals=dict(sorted(collections.Counter(d['decision'] for d in decisions).items())))
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    so = '--selection-only' in sys.argv
    b = build(so)
    if so:
        d = json.loads(b)
        print(json.dumps(dict(reconstruction=d['reconstruction'], selected=d['selected']), ensure_ascii=False, indent=1))
        for q in sorted(d['high_queue'], key=lambda q: q['rank']):
            print(q['rank'], q['recommendation_id'], q['target_id'], q['suggested_identifiers'], list(q['selection_scores'].values()),
                  q['current_baseline_equivalent']['target_juris_now'])
    elif '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes() == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    else:
        OUT.write_bytes(b)
        print(OUT.name, hashlib.sha256(b).hexdigest())
