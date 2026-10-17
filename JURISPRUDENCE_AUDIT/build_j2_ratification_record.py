"""RATIFICAÇÃO 03–09 — Parte A: formal human ratification record of the consolidated Batches 03, 04, 06, 07, 08 and 09 (the user reviewed
J2_RATIFICATION_DOSSIER.md and ratified everything except J0-BL-001, Súmula 403/STJ, kept UNRESOLVED_EXTERNAL). The batch decision files
stay byte-identical (they are what was reviewed; each is pinned by sha256 here); this record is the only place that says HUMAN_APPROVED.
Classifications are preserved exactly. Writes J2_RATIFICATION_RECORD_03_09.json.   Usage: python build_j2_ratification_record.py [--check]
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_j2_batch as G  # noqa: E402

BATCHES = (3, 4, 6, 7, 8, 9)
OUT = HERE / 'J2_RATIFICATION_RECORD_03_09.json'
RATIFICATION = dict(by='ARTHUR', on='2026-10-17', channel='chat',
                    statement='O usuário revisou o dossiê consolidado e RATIFICA as decisões dos Batches 03, 04, 06, 07, 08 e 09, com uma única '
                              'exceção: BL-001 — Súmula 403/STJ permanece UNRESOLVED_EXTERNAL.',
                    exceptions={'J0-BL-001': 'UNRESOLVED_EXTERNAL (fonte oficial do STJ bloqueada por desafio anti-robô; sem ficha, sem vínculo)'},
                    provisional_only=['STF:ADI:5017', 'STF:ADPF:378', 'STF:RCL:84738'])
LINKING = ('PROMOTE_RECOMMENDED', 'PROMOTE_PROVISIONAL_RECOMMENDED', 'REALLOCATE_RECOMMENDED')


def build():
    items, files = [], {}
    for n in BATCHES:
        p = G.batch_file(n)
        files[p.relative_to(HERE).as_posix()] = hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
        for x in json.loads(p.read_text(encoding='utf-8'))['decisions']:
            if (x['status'], x['human_approved']) != ('AWAITING_USER_RATIFICATION', False):
                raise SystemExit(f'UNEXPECTED_PROPOSAL_STATE {x["recommendation_id"]}')
            rid = x['recommendation_id']
            unresolved = x['decision'].startswith('UNRESOLVED')
            if unresolved != (rid in RATIFICATION['exceptions']):
                raise SystemExit(f'EXCEPTION_MISMATCH {rid}')
            rv = x.get('revalidation')
            items.append(dict(recommendation_id=rid, batch=f'BATCH{n:02d}', decision=x['decision'], creates_device_relations=x['decision'] in LINKING,
                              recommended_targets=x['recommended_targets'], precedents=[q['id'] for q in x['precedents']],
                              ratification_status='UNRESOLVED_EXTERNAL' if unresolved else 'HUMAN_APPROVED', human_approved=not unresolved,
                              provisional=dict(applies_to=rv.get('applies_to') or x['precedents'][0]['id'], trigger=rv['trigger']) if rv else None))
    prov = sorted({i['provisional']['applies_to'] for i in items if i['provisional']})
    if prov != sorted(RATIFICATION['provisional_only']):
        raise SystemExit(f'PROVISIONAL_SET_MISMATCH {prov}')
    c = collections.Counter(i['ratification_status'] for i in items)
    doc = dict(schema_version=1, round='J2', kind='HUMAN_RATIFICATION', ratification=RATIFICATION, decision_files_sha256_lf=files,
               TOTAL_RECOMMENDATIONS=len(items), RATIFIED_DECISIONS=c['HUMAN_APPROVED'], UNRESOLVED_EXTERNAL=c['UNRESOLVED_EXTERNAL'],
               ratified_by_decision=dict(sorted(collections.Counter(i['decision'] for i in items if i['human_approved']).items())),
               linking_decisions_ratified=sum(1 for i in items if i['human_approved'] and i['creates_device_relations']),
               non_linking_decisions_ratified=sum(1 for i in items if i['human_approved'] and not i['creates_device_relations']),
               PROVISIONAL_STATUS_PRESERVED='YES', provisional_items=prov, items=items)
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = build()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    d = json.loads(b)
    print({k: d[k] for k in ('TOTAL_RECOMMENDATIONS', 'RATIFIED_DECISIONS', 'UNRESOLVED_EXTERNAL', 'ratified_by_decision', 'linking_decisions_ratified',
                             'provisional_items')})
