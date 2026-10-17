"""J2A — HIGH backlog: reconstruction against the CURRENT approved baseline (256, J1.5 11/11) and deterministic selection of BATCH01 (10).
Host-only, read-only, deterministic, no network. The legal review of the 10 (official sources) is recorded in J2_HIGH_BACKLOG/j2a_batch01_review.py
and merged here; nothing is materialized.

Reads:   JURISPRUDENCE_AUDIT/J0_DIAGNOSTIC_AUDIT.json (backlog items, J0 order = recommendation_id),
         ENTENDA_ENGINE/derived/<batch>/JURISPRUDENCE_LINK_RECOMMENDATIONS.json (same files and rule as J0, re-run),
         JURISPRUDENCE_AUDIT/J1_4_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX (installed, 256 visible).
Writes:  JURISPRUDENCE_AUDIT/J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json
Selection (Part B order, lexicographic; every criterion is an objective proxy, documented in SELECTION_RULES):
  1 explicit identifier  2 constitutional weight of the precedent type  3 recurrence  4 target specificity  5 low ambiguity
  6 utility (article without jurisprudence)  7 recommendation_id.
Usage: python build_j2a_batch01.py [--check] [--selection-only]
"""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_DIR = HERE / 'J2_HIGH_BACKLOG'
OUT = OUT_DIR / 'J2A_BATCH01_DECISIONS.json'
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(OUT_DIR))
import build_j0_diagnostic_audit as J0  # noqa: E402

J0_AUDIT = HERE / 'J0_DIAGNOSTIC_AUDIT.json'
CURRENT = HERE / 'J1_4_CANDIDATE_HOST_ONLY/candidate/SD/99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'
CURRENT_SHA = 'd07cb0764735a56d9f7eecb915a56ed083d35e662cd47164293e388d048f72e1'   # installed on the card (J1.5, 11/11)
BATCH_SIZE = 10
ID_RE = re.compile(r'\b(ADIN|ADI|ADC|ADPF|ADO|RE|ARE|MS|HC|RHC|MI|Rcl|AI|ACO|AP|Inq|Pet)\s*\d[\d.]*|\bTema\s*\d+|\bS[uú]mula\s+(Vinculante\s+)?\d+|\bSV\s*\d+',
                   re.I)
GENERAL_EFFECT = re.compile(r'^(ADIN|ADI|ADC|ADPF|ADO)\b|^Tema\b|^S[uú]mula\s+Vinculante\b|^SV\b', re.I)
SELECTION_RULES = {
    '1_explicit_identifier': '2 = desired_reference names exactly one identifier; 1 = identifiers only in the note or more than one; 0 = none',
    '2_constitutional_weight': '2 = precedent with general/binding effect (ADI/ADC/ADO/ADPF, Tema RG, SV); 1 = other STF classes / súmula comum',
    '3_recurrence': '1 = the same identifier is recommended in more than one pending recommendation (or occurrences > 1)',
    '4_specificity': '1 = target below article level (caput, parágrafo, inciso, alínea); 0 = whole article',
    '5_low_ambiguity': '1 = exactly one identifier in reference + note and reference is not IDENTIFICACAO_PENDENTE',
    '6_utility': '1 = article without any visible jurisprudence in the current baseline',
    '7_tiebreak': 'recommendation_id ascending',
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_lf(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def norm_id(s):
    s = re.sub(r'\s+', ' ', s.strip())
    s = re.sub(r'(?i)^ADIN\b', 'ADI', s)
    s = re.sub(r'(?i)^S[uú]mula Vinculante', 'SV', s)
    s = re.sub(r'(?i)^S[uú]mula', 'Súmula', s)
    return re.sub(r'(\d)\.(\d)', r'\1\2', s)


def ids_in(text):
    return sorted({norm_id(m.group(0)) for m in ID_RE.finditer(text or '')})


def current_baseline():
    if sha(CURRENT) != CURRENT_SHA:
        raise SystemExit('CURRENT_BASELINE_NOT_INSTALLED_BYTES')
    rows = [l.split('|') for l in CURRENT.read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')]
    vis = [r for r in rows if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
    if (len(vis), len({r[0] for r in vis})) != (256, 156):
        raise SystemExit('CURRENT_BASELINE_NOT_256')
    return vis


def reconstruct():
    """Re-run the J0 backlog rule over the CURRENT baseline (256) and compare with J0 (which used the 277)."""
    j0 = json.loads(J0_AUDIT.read_text(encoding='utf-8'))['backlog']
    vis = current_baseline()
    vis_targets = {r[0] for r in vis}
    art_with = {':'.join(t.split(':')[:2]) for t in vis_targets}
    linked_pairs = {(r[0], r[5]) for r in vis}
    by_source = collections.defaultdict(list)
    for r in vis:
        by_source[r[5]].append(r[0])
    recs = []
    for b in J0.BATCHES:
        for x in J0.load(ROOT / f'ENTENDA_ENGINE/derived/{b}/JURISPRUDENCE_LINK_RECOMMENDATIONS.json')['recommendations']:
            recs.append(dict(x, batch=b))
    groups = collections.OrderedDict()
    for x in recs:
        groups.setdefault((x['target_id'], J0.norm(x.get('desired_reference'))), []).append(x)
    items = []
    for i, ((t, _), xs) in enumerate(groups.items(), 1):
        x = xs[-1]
        src = x.get('local_identity_searched') or ''
        if x['status'] == 'MATERIAL_MISMATCH_EXCLUDED':
            cat = 'EXCLUDED_MATERIAL_DIVERGENCE'
        elif x['status'] == 'READY_TO_LINK' or x.get('already_linked_to_target') or (t, src) in linked_pairs:
            cat = 'ALREADY_LINKED'
        else:
            cat = 'NEEDS_EXTERNAL_INGESTION'
        items.append(dict(recommendation_id=f'J0-BL-{i:03d}', target_id=t, desired_reference=x.get('desired_reference'),
                          recommendation_text=x.get('purpose') or '', origin=sorted({y['batch'] for y in xs}), occurrences=len(xs),
                          local_identity_searched=src or None, category=cat))
    if [(a['target_id'], a['desired_reference'], a['category']) for a in items] != \
            [(b['target_id'], b['desired_reference'], b['category']) for b in j0['items']]:
        raise SystemExit('BACKLOG_DIFFERS_FROM_J0')     # categories are unchanged by J1.1/J1.4 (verified, fail closed)
    pending = [b for b in items if b['category'] == 'NEEDS_EXTERNAL_INGESTION']
    dup_desired = collections.Counter(J0.norm(b['desired_reference']) for b in pending)
    id_count = collections.Counter(i for b in pending for i in ids_in(f"{b['desired_reference']} {b['recommendation_text']}"))
    for b in pending:
        text = f"{b['desired_reference']} {b['recommendation_text'][:300]}"
        named = sorted({m.group(0).strip() for m in re.finditer(   # J0 priority rule, unchanged
            r'\b(ADI|ADC|ADPF|ADO|RE|ARE|MS|HC|RHC|MI|Rcl|AI|ACO|AP|Inq|Pet)\s*\d[\d.]*|\bTema\s*\d+|\bS[uú]mula\s+(Vinculante\s+)?\d+|\bSV\s*\d+',
            text, re.I)})
        art_has = ':'.join(b['target_id'].split(':')[:2]) in art_with
        score = (1 if named else 0) + (1 if b['occurrences'] > 1 or dup_desired[J0.norm(b['desired_reference'])] > 1 else 0) + (0 if art_has else 1) \
            + (1 if b['desired_reference'] and b['desired_reference'] != 'IDENTIFICACAO_PENDENTE' else 0)
        b['priority'] = 'HIGH' if score >= 3 else 'MEDIUM' if score == 2 else 'LOW'
        b['priority_reason'] = dict(named_identifier=bool(named),
                                    recurrent=b['occurrences'] > 1 or dup_desired[J0.norm(b['desired_reference'])] > 1,
                                    article_without_juris=not art_has,
                                    reference_described=bool(b['desired_reference'] and b['desired_reference'] != 'IDENTIFICACAO_PENDENTE'))
        ref_ids = ids_in(b['desired_reference'] if b['desired_reference'] != 'IDENTIFICACAO_PENDENTE' else '')
        all_ids = ids_in(f"{b['desired_reference']} {b['recommendation_text']}")
        b['suggested_identifiers'] = all_ids
        b['suggested_type'] = sorted({re.split(r'\s', i)[0] for i in all_ids})
        local = b['local_identity_searched']
        b['current_baseline_equivalent'] = dict(
            target_has_juris=any(k in vis_targets for k in (b['target_id'], b['target_id'] + ':CAPUT', b['target_id'].removesuffix(':CAPUT'))),
            article_has_juris=art_has, same_local_identity_linked_at=sorted(by_source.get(local, [])) if local else [])
        b['selection_scores'] = {
            '1_explicit_identifier': 2 if len(ref_ids) == 1 else 1 if all_ids else 0,
            '2_constitutional_weight': 2 if all_ids and all(GENERAL_EFFECT.match(i) for i in (ref_ids or all_ids)) else 1 if all_ids else 0,
            '3_recurrence': 1 if b['occurrences'] > 1 or any(id_count[i] > 1 for i in all_ids) else 0,
            '4_specificity': 1 if len(b['target_id'].split(':')) > 2 else 0,
            '5_low_ambiguity': 1 if len(all_ids) == 1 and b['desired_reference'] != 'IDENTIFICACAO_PENDENTE' else 0,
            '6_utility': 0 if art_has else 1}
    return items, pending, j0


def select(pending):
    high = [b for b in pending if b['priority'] == 'HIGH']
    key = lambda b: tuple(-b['selection_scores'][k] for k in sorted(b['selection_scores'])) + (b['recommendation_id'],)  # noqa: E731
    ranked = sorted(high, key=key)
    return high, ranked, [b['recommendation_id'] for b in ranked[:BATCH_SIZE]]


def build(selection_only=False):
    items, pending, j0 = reconstruct()
    high, ranked, chosen = select(pending)
    recon = dict(raw_recommendations=sum(b['occurrences'] for b in items), unique=len(items),
                 by_category=dict(sorted(collections.Counter(b['category'] for b in items).items())),
                 BACKLOG_PENDING=len(pending), BACKLOG_TARGETS=len({b['target_id'] for b in pending}),
                 pending_by_priority=dict(sorted(collections.Counter(b['priority'] for b in pending).items())), HIGH_TOTAL=len(high),
                 equals_J0=dict(pending=len(pending) == j0['by_category']['NEEDS_EXTERNAL_INGESTION'],
                                targets=len({b['target_id'] for b in pending}) == j0['pending_targets'],
                                by_priority=dict(collections.Counter(b['priority'] for b in pending)) == j0['pending_by_priority'],
                                high_set={b['target_id'] + '|' + str(b['desired_reference']) for b in high} ==
                                         {b['target_id'] + '|' + str(b['desired_reference']) for b in j0['items'] if b.get('priority') == 'HIGH'}))
    doc = dict(schema_version=1, round='J2A', batch='BATCH01', mode='HOST_ONLY_DECISIONS_NO_MATERIALIZATION',
               status='AWAITING_USER_RATIFICATION',
               current_baseline=dict(file=CURRENT.relative_to(ROOT).as_posix(), sha256=CURRENT_SHA, JURIS_RELATIONS=256, JURIS_TARGETS=156,
                                     physical='J1_5_PHYSICAL_VALIDATION = 11/11 PASS'),
               inputs={f.relative_to(ROOT).as_posix(): sha_lf(f) for f in
                       [J0_AUDIT] + [ROOT / f'ENTENDA_ENGINE/derived/{b}/JURISPRUDENCE_LINK_RECOMMENDATIONS.json' for b in J0.BATCHES]},
               reconstruction=recon, selection_rules=SELECTION_RULES,
               high_queue=[{k: b[k] for k in ('recommendation_id', 'target_id', 'desired_reference', 'origin', 'occurrences', 'suggested_identifiers',
                                             'suggested_type', 'priority_reason', 'current_baseline_equivalent', 'selection_scores')}
                           | dict(rank=ranked.index(b) + 1, recommendation_text=b['recommendation_text'][:400]) for b in sorted(high, key=lambda b: b['recommendation_id'])],
               selected=chosen, HIGH_REMAINING_AFTER_BATCH=len(high) - len(chosen))
    if not selection_only:
        import j2a_batch01_review as R
        decisions = R.decisions(doc)
        doc.update(sources=R.SOURCES, decisions=decisions,
                   totals=dict(sorted(collections.Counter(d['decision'] for d in decisions).items())))
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    so = '--selection-only' in sys.argv
    b = build(so)
    if so:
        d = json.loads(b)
        print(json.dumps(dict(reconstruction=d['reconstruction'], selected=d['selected']), ensure_ascii=False, indent=1))
        for q in sorted(d['high_queue'], key=lambda q: q['rank']):
            print(q['rank'], q['recommendation_id'], q['target_id'], q['suggested_identifiers'], q['selection_scores'])
    elif '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes() == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    else:
        OUT.write_bytes(b)
        print(OUT.name, hashlib.sha256(b).hexdigest())
