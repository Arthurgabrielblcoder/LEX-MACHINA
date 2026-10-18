"""PORTABILITY PILOT — Código Civil: runs the CF jurisprudence engine (unchanged modules + profile wrappers) over CC candidates and
measures, per candidate and per step, what was automatic and what needed human judgment. Host-only, deterministic, no network.
Nothing is published: every result is PORTABILITY_PILOT_ONLY / PORTABILITY_EVIDENCE.
Usage: python build_pilot_cc.py [--check]
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / 'pilot_cc')]
import norm_profiles as NP  # noqa: E402
import cc_pilot_evidence as EV  # noqa: E402
from norm_profiles import T, AUD  # noqa: E402
import juris_types as JT  # noqa: E402

OUT = HERE / 'pilot_cc' / 'PORTABILITY_PILOT_CC.json'
ANNOT = HERE / 'pilot_cc' / 'PLANALTO_CC2002_ANNOTATIONS.json'
CC_INDEX = ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json'
PROFILE = NP.PROFILES['CC2002']
STEPS = ('AUTO_DISCOVERED', 'AUTO_TARGET_NORMALIZATION', 'AUTO_NAMESPACE_CHECK', 'AUTO_TEMPORAL_CHECK', 'AUTO_STATUS_CHECK', 'AUTO_DUPLICATE_CHECK',
         'OFFICIAL_SOURCE_FOUND')


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def alias_map():
    out = {}
    for pid, f in EV.PRECEDENTS.items():
        for a in f.get('alias', []):
            out[a] = pid
    return out


def discover():
    """Adapter #1 (Planalto 'Vide') + adapter #2 (STF search, rule applied here). Returns raw candidates in discovery order."""
    al = alias_map()
    cands = []
    for a in load(ANNOT)['annotations']:
        raw = f"STF:{a['klass']}:{a['number']}"
        cands.append(dict(source='PLANALTO_VIDE', target=a['target_id'], cited_as=a['annotation'], raw_precedent=raw,
                          precedent=al.get(raw, raw), citation_text=a['annotation']))
    for head, org, _, tema, arts, cite in EV.Q1_ROWS:
        if org != 'Tribunal Pleno' or not tema or head.endswith(' RG') or not arts:
            continue
        for art in arts:
            m = re.match(r'([\d.]+)(?:,\s*§\s*(\d+))?', art)
            target = T.format_target_id('CC2002', m.group(1).replace('.', ''), paragraph=m.group(2))
            cands.append(dict(source='STF_SEARCH_Q1', target=target, cited_as=f'{head} (Tema {tema}): art. {art}',
                              raw_precedent=f"STF:{head.split()[0]}:{head.split()[1]}", precedent=f'STF:RG:{tema}', citation_text=cite))
    return cands


def run():
    idx = {x['target_id'] for x in load(CC_INDEX)['targets']}
    missing = sorted({t for v in EV.ASSESSMENT.values() for t in v[1]} - idx)
    if missing:
        raise SystemExit(f'PROPOSED_TARGET_NOT_IN_CC2002_INDEX {missing}')
    amend = load(ANNOT)['amendments']
    cands, seen, out = discover(), {}, []
    for i, c in enumerate(cands, 1):
        f = EV.PRECEDENTS.get(c['precedent'])
        key = (c['target'], c['precedent'])
        steps = {}
        steps['AUTO_DISCOVERED'] = True
        art = T.parse_target_id(c['target'])['article']
        gran = NP.citation_granularity(PROFILE, c['citation_text'] or '', art) if c['citation_text'] else dict(status='NO_TEXT', targets=[])
        valid = T.validate_target_id(c['target'])[0] and c['target'] in idx
        # normalization is automatic when the target is valid AND no finer/other dispositivo is signalled by the official text
        finer = [t for t in gran.get('targets', []) if t != c['target']]
        num = art[:-3] + '.' + art[-3:] if len(art) > 3 else art              # official texts write 1.641 / 206
        suffix = re.search(r'\b' + re.escape(num) + r'(-[A-Z])\b', (f or {}).get('evidence', ''))
        derived = finer[:1] or ([T.format_target_id('CC2002', art + suffix.group(1))] if suffix else [])
        # automatic = the engine itself fixes the final target (valid, in the CC2002 index) from the official text
        engine_target = (derived or [c['target']])[0]
        final = (EV.ASSESSMENT.get(key) or (None, []))[1]
        steps['AUTO_TARGET_NORMALIZATION'] = valid and engine_target in idx and final in ([], [engine_target])
        ns = NP.namespace_check(PROFILE, (f or {}).get('evidence', ''))
        steps['AUTO_NAMESPACE_CHECK'] = ns['result'] == 'PASS'
        tmp = NP.temporal_check(PROFILE, amend.get(c['target'], []), f['judgment_year']) if f else dict(result='UNKNOWN')
        steps['AUTO_TEMPORAL_CHECK'] = tmp['result'] in ('CURRENT', 'TEMPORAL_ALERT')
        st = AUD.status_signals((f or {}).get('status_text', ''))
        steps['AUTO_STATUS_CHECK'] = bool(st['signals'])
        dup_of = seen.get(key)
        joint = [j for j in (f or {}).get('joint_with', []) if (c['target'], j) in seen]
        steps['AUTO_DUPLICATE_CHECK'] = True                                  # alias + same-pair + joint detection always ran
        steps['OFFICIAL_SOURCE_FOUND'] = bool(f and all(EV.SOURCES[s]['tier'] == 'A' for s in f['sources']))
        dec, targets, human, note = EV.ASSESSMENT.get(key, ('DUPLICATE_RECOMMENDATION', [], False, 'Mesmo par já descoberto (alias Tema ↔ leading case).'))
        if dup_of:
            dec, targets, human, note = 'DUPLICATE_RECOMMENDATION', [], False, f'Duplicata automática de {dup_of} (alias {c["raw_precedent"]} → {c["precedent"]}).'
        seen.setdefault(key, f'C{i:02d}')
        tipo = (f or {}).get('tipo', 'repercussao_geral')
        out.append(dict(id=f'C{i:02d}', source=c['source'], discovered_target=c['target'], cited_as=c['cited_as'], raw_precedent=c['raw_precedent'],
                        precedent=c['precedent'], device_label=JT.label(tipo, 'STF', c['precedent'].split(':')[-1]),
                        steps=steps, citation_parser=gran, namespace=ns, temporal=tmp, status_signals=st,
                        engine_target=engine_target, duplicate_of=dup_of, joint_detected=joint or (f or {}).get('joint_with', []),
                        pilot_assessment=dec, proposed_targets=targets, HUMAN_REVIEW_NEEDED=human or not all(steps.values()),
                        assessment_note=note, decision_status='PORTABILITY_PILOT_ONLY', human_approved=False))
    return out


def metrics(rows):
    step_auto = {s: sum(1 for r in rows if r['steps'][s]) for s in STEPS}
    fully = sum(1 for r in rows if all(r['steps'].values()) and not r['HUMAN_REVIEW_NEEDED'])
    by = collections.Counter(r['pilot_assessment'] for r in rows)
    return dict(CANDIDATES_ANALYZED=len(rows), STEP_AUTOMATION=step_auto,
                FULLY_AUTOMATED_STEPS=sum(step_auto.values()), TOTAL_STEPS=len(rows) * len(STEPS),
                CANDIDATES_FULLY_AUTOMATIC=fully, ITEMS_REQUIRING_HUMAN_JUDGMENT=sum(1 for r in rows if r['HUMAN_REVIEW_NEEDED']),
                ITEMS_BLOCKED_BY_SOURCE_ACCESS=sum(1 for r in rows if not r['steps']['OFFICIAL_SOURCE_FOUND']),
                DISCOVERY_CHANNELS_BLOCKED=['STJ (anti-robô; fonte STJ1)'],
                FALSE_POSITIVES_DETECTED=by['REJECT_NOT_MATERIAL_RECOMMENDED'] + by['REJECT_FALSE_POSITIVE_RECOMMENDED'],
                REALLOCATIONS_DETECTED=by['REALLOCATE_RECOMMENDED'],
                REALLOCATIONS_DETECTED_AUTOMATICALLY=sum(1 for r in rows if r['pilot_assessment'] == 'REALLOCATE_RECOMMENDED'
                                                         and r['proposed_targets'] == [r['engine_target']]),
                ENGINE_TARGET_AGREES_WITH_HUMAN=sum(1 for r in rows if r['proposed_targets'] in ([], [r['engine_target']])),
                DUPLICATES_DETECTED=by['DUPLICATE_RECOMMENDATION'],
                DUPLICATES_DETECTED_AUTOMATICALLY=sum(1 for r in rows if r['duplicate_of']),
                TEMPORAL_ALERTS=sum(1 for r in rows if r['temporal'].get('result') == 'TEMPORAL_ALERT'),
                CF_AUDITOR_FALSE_NAMESPACE_ALERTS=sum(1 for r in rows if r['namespace']['cf_auditor_alert']),
                ASSESSMENTS=dict(sorted(by.items())))


TOOLS = [  # (tool, classification for other norms, used in the pilot as)
    ('LEGAL_TARGET_ID/target_id.py', 'GENERIC_ALREADY', 'REUSED_UNCHANGED'),
    ('LEGAL_TARGET_ID/structure_parser.py + build_target_index.py (CC2002_TARGET_INDEX já existente)', 'GENERIC_ALREADY', 'REUSED_UNCHANGED'),
    ('JURISPRUDENCE_AUDIT/juris_types.py', 'GENERIC_ALREADY', 'REUSED_UNCHANGED'),
    ('JURISPRUDENCE_AUDIT/j2_auditors.status_signals / joint_scope', 'GENERIC_ALREADY', 'REUSED_UNCHANGED'),
    ('JURISPRUDENCE_AUDIT/check_j2b_provisional.py', 'GENERIC_ALREADY', 'NOT_EXERCISED (nenhum provisório no piloto)'),
    ('LEGAL_TARGET_ID/citation_parser.py', 'CF_SPECIFIC_BUT_PARAMETERIZABLE', 'REUSED_AFTER_PARAMETERIZATION'),
    ('JURISPRUDENCE_AUDIT/j2_auditors.namespace_alerts', 'CF_SPECIFIC_BUT_PARAMETERIZABLE', 'REUSED_AFTER_PARAMETERIZATION'),
    ('JURISPRUDENCE_AUDIT/j2_auditors.temporal_alerts', 'CF_SPECIFIC_BUT_PARAMETERIZABLE', 'REUSED_AFTER_PARAMETERIZATION'),
    ('JURISPRUDENCE_AUDIT/j2_review_common.make_decisions', 'BLOCKER_FOR_OTHER_NORMS', 'NOT_REUSED (namespace CF88/ADCT fixo)'),
    ('JURISPRUDENCE_AUDIT/build_j2_batch.py + build_j0/build_j2a (descoberta via ENTENDA)', 'BLOCKER_FOR_OTHER_NORMS', 'REPLACED_BY_NEW_ADAPTERS'),
    ('JURISPRUDENCE_ENGINE/discovery_planalto.py', 'NEW_CODE', 'NEW'),
    ('JURISPRUDENCE_ENGINE/norm_profiles.py', 'NEW_CODE', 'NEW'),
    ('JURISPRUDENCE_ENGINE/build_pilot_cc.py (descoberta STF + orquestração)', 'NEW_CODE', 'NEW'),
]


STJ_INDEX = HERE / 'stj' / 'STJ_SUMULAS_INDEX.json'
BEFORE_SPRINT = dict(steps='133/140', candidates_fully_automatic=9, human_judgment=11, distinct_pairs=18)   # PORTABILITY_PILOT_CC.md (5e7e4f6)
SPRINT_TOOLS = [  # what the scale sprint added, kept apart from the original pilot tool list (no rewriting of the before numbers)
    ('JURISPRUDENCE_ENGINE/discovery_stj_sumulas.py (PDF oficial de súmulas do STJ)', 'NEW_CODE', 'NEW'),
    ('LEGAL_TARGET_ID/target_id.py (alínea sem inciso fora da CF)', 'GENERIC_ALREADY', 'EXTENDED_BACKWARD_COMPATIBLE'),
    ('JURISPRUDENCE_AUDIT/juris_types.device_status (fonte única de tipos)', 'GENERIC_ALREADY', 'EXTENDED_BACKWARD_COMPATIBLE'),
    ('JURISPRUDENCE_ENGINE/firmware_multinorm (protótipo multinorma + simulador)', 'NEW_CODE', 'NEW'),
]


def stj_channel(idx, amend, rows):
    """STJ discovery channel for CC2002 (official súmulas PDF), measured separately from the 20 original candidates."""
    d = load(STJ_INDEX)
    existing = {(r['discovered_target'], r['precedent']) for r in rows}
    existing_targets = {t for r in rows for t in [r['discovered_target']] + r['proposed_targets']}
    pairs, cc16_only = [], 0
    for e in d['entries']:
        if e['status'] in ('CANCELADA', 'REVOGADA'):
            continue
        siglas = {r['sigla'] for r in e['references']}
        if 'CC-16' in siglas and not any(r['catalog_id'] == 'CC2002' for r in e['references']):
            cc16_only += 1
        for r in e['references']:
            if r['catalog_id'] != 'CC2002':
                continue
            year = int(e['data_decisao'][-4:]) if re.search(r'\d{4}$', e['data_decisao']) else None
            for t in r['targets']:
                tmp = NP.temporal_check(PROFILE, amend.get(t, []), year) if year else dict(result='UNKNOWN')
                steps = dict(AUTO_DISCOVERED=True, AUTO_TARGET_NORMALIZATION=t in idx, AUTO_NAMESPACE_CHECK=True,
                             AUTO_TEMPORAL_CHECK=tmp['result'] in ('CURRENT', 'TEMPORAL_ALERT'), AUTO_STATUS_CHECK=bool(e['status']),
                             AUTO_DUPLICATE_CHECK=True, OFFICIAL_SOURCE_FOUND=d['source']['tier'] == 'A')
                pairs.append(dict(target=t, precedent=f"STJ:SUMULA:{e['number']}", status=e['status'], data_decisao=e['data_decisao'],
                                  temporal=tmp['result'], steps=steps, overlaps_pilot_target=t in existing_targets,
                                  duplicate_of_pilot=(t, f"STJ:SUMULA:{e['number']}") in existing,
                                  device_label=JT.label('sumula', 'STJ', str(e['number'])), device_type=JT.device_status('SUMULA_STJ')))
    auto = {s: sum(1 for p in pairs if p['steps'][s]) for s in STEPS}
    return dict(source=d['source'], PAIRS=len(pairs), DISTINCT_SUMULAS=len({p['precedent'] for p in pairs}),
                DISTINCT_TARGETS=len({p['target'] for p in pairs}), STEP_AUTOMATION=auto, AUTOMATED_STEPS=f'{sum(auto.values())}/{len(pairs) * len(STEPS)}',
                TEMPORAL_ALERTS=sum(1 for p in pairs if p['temporal'] == 'TEMPORAL_ALERT'), TARGETS_ON_PILOT_TARGETS=sum(p['overlaps_pilot_target'] for p in pairs),
                HUMAN_PERTINENCE_REVIEW='REQUIRED_FOR_ALL (não avaliado nesta missão: o CC não é expandido além do piloto)',
                SUMULAS_CITING_ONLY_CC1916=cc16_only, pairs=pairs)


def build():
    rows = run()
    m = metrics(rows)
    used = collections.Counter(u.split(' ')[0] for _, _, u in TOOLS)
    m.update(TOOLS_REUSED_WITHOUT_CHANGE=used['REUSED_UNCHANGED'], TOOLS_REUSED_AFTER_PARAMETERIZATION=used['REUSED_AFTER_PARAMETERIZATION'],
             TOOLS_REQUIRING_NEW_CODE=used['NEW'], TOOLS_NOT_REUSABLE=used['NOT_REUSED'] + used['REPLACED_BY_NEW_ADAPTERS'],
             TOOLS_GENERIC_NOT_EXERCISED=used['NOT_EXERCISED'])
    doc = dict(schema_version=1, kind='PORTABILITY_PILOT', norm='CC2002', status='PORTABILITY_EVIDENCE', publishes=False,
               CC_RELATIONS_PUBLISHED=0, CC_FILES_DEPLOYED=0, SD_CHANGED='NO', FIRMWARE_CHANGED='NO',
               profile=dict(norm_id=PROFILE.norm_id, namespaces=list(PROFILE.namespaces), expected_courts=list(PROFILE.expected_courts),
                            discovery_adapters=list(PROFILE.discovery_adapters)),
               corpus=dict(planalto_sha256=load(ANNOT)['source_sha256'], cc2002_target_index_sha256=load(CC_INDEX)['target_index_sha256'],
                           cc2002_targets=load(CC_INDEX)['total_targets'], cc2002_articles=load(CC_INDEX)['counts_by_kind']['ARTIGO']),
               sources=EV.SOURCES, metrics=m, tools=[dict(tool=t, classification=c, pilot_use=u) for t, c, u in TOOLS], candidates=rows)
    if STJ_INDEX.is_file():
        idx = {x['target_id'] for x in load(CC_INDEX)['targets']}
        stj = stj_channel(idx, load(ANNOT)['amendments'], rows)
        reach = len({(r['discovered_target'], r['precedent']) for r in rows if not r['duplicate_of']}) + \
            len({(p['target'], p['precedent']) for p in stj['pairs'] if not p['duplicate_of_pilot']})
        doc['sprint'] = dict(
            before=BEFORE_SPRINT,
            after_same_20=dict(steps=f"{m['FULLY_AUTOMATED_STEPS']}/{m['TOTAL_STEPS']}", candidates_fully_automatic=m['CANDIDATES_FULLY_AUTOMATIC'],
                               human_judgment=m['ITEMS_REQUIRING_HUMAN_JUDGMENT'],
                               distinct_pairs=len({(r['discovered_target'], r['precedent']) for r in rows if not r['duplicate_of']}),
                               note='Mesmos 20 candidatos e mesmas regras: os bloqueadores atacados (firmware, gramática, STJ) não alteram essas etapas.'),
            reachable_distinct_pairs_with_stj=reach,
            tools_added=[dict(tool=t, classification=c, use=u) for t, c, u in SPRINT_TOOLS])
        doc['stj_channel'] = stj
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    b = build()
    if ap.parse_args().check:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    print(json.dumps(json.loads(b)['metrics'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
