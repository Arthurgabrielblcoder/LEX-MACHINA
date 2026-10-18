"""PÓS-NOTURNA Parte J — consolidated provisional-jurisprudence registry: the installed J2B item (ADI 7697) + every batch decision carrying a
`revalidation` block (ADI 5017, ADPF 378, Rcl 84738, …), in the SAME mechanism (check_j2b_provisional.py --registry). Deterministic, read-only
over its inputs; the J2B registry stays intact. Nothing here publishes anything: publication_state says where each item is, auto_publish=false.
Usage: python build_j2_provisional_registry.py [--check]
"""
import argparse
import datetime as dt
import glob
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
J2B = HERE / 'J2_HIGH_BACKLOG/J2B_REVALIDATION_REGISTRY.json'
OUT = HERE / 'J2_PROVISIONAL_REGISTRY.json'
# Real procedural state per item (from the official status recorded in the decision / J2B registry; no new research here)
STATE = {'STF:ADI:7697': 'MERIT_PENDING', 'STF:ADI:5017': 'REFERENDUM_PENDING', 'STF:ADPF:378': 'CAUTIONARY_ONLY',
         'STF:RCL:84738': 'LEADING_CASE_PENDING'}
STATES = {'MERIT_PENDING': 'cautelar referendada; mérito pendente', 'REFERENDUM_PENDING': 'cautelar monocrática sem referendo; mérito pendente',
          'CAUTIONARY_ONLY': 'só há decisão cautelar do Plenário; mérito nunca julgado', 'LEADING_CASE_PENDING':
          'decisão de Turma condicionada a tema de repercussão geral ainda pendente', 'SUPERSEDED': 'substituída por decisão posterior'}
# J2J.1 — editorial/physical state, SEPARATE from the legal state above (which stays provisional). Recorded from the committed evidence:
# human ratification (J2B_REPORT.md for Batch01; J2_RATIFICATION_RECORD_03_09.json for Batches 03–09) and the physical validations.
_RAT01 = dict(by='ARTHUR', on='2026-10-16', record='J2_HIGH_BACKLOG/J2B_REPORT.md (J2A_BATCH01_USER_RATIFIED = YES)')
_RAT39 = dict(by='ARTHUR', on='2026-10-17', record='J2_RATIFICATION_RECORD_03_09.json')
_J2C = 'J2C 12/12 PASS (J2_HIGH_BACKLOG/J2C_DEPLOY_REPORT.md)'
_J2G = 'J2G 21/21 PASS (J2G_PHYSICAL_DEPLOY/J2G_PHYSICAL_VALIDATION.json)'
_J2I = 'J2I 32/32 PASS (J2I_PHYSICAL_FLASH/J2I_PHYSICAL_VALIDATION.json)'
PUBLICATION = {'STF:ADI:7697': dict(ratification=_RAT01, installed_by='J2C', validations=[_J2C, _J2G, _J2I]),
               'STF:ADI:5017': dict(ratification=_RAT39, installed_by='J2G', validations=[_J2G, _J2I]),
               'STF:ADPF:378': dict(ratification=_RAT39, installed_by='J2H', validations=[_J2I]),
               'STF:RCL:84738': dict(ratification=_RAT39, installed_by='J2H', validations=[_J2I])}
PHYSICAL_BASELINE = 'J2I_FROZEN_315_198'
ON_TRIGGER = 'Rever o vínculo e a ficha antes de qualquer novo deploy; sem revisão, o item volta a pendente (fail closed).'


def publication(pid):
    """Editorial/physical fields of an item; the legal fields (state, status_processual, revalidation) are not touched here."""
    p = PUBLICATION[pid]
    return dict(legal_nature='PROVISIONAL', editorial_state='HUMAN_APPROVED', ratification=p['ratification'],
                physical_state='PHYSICALLY_APPROVED', installed_by=p['installed_by'], physical_validations=p['validations'],
                physical_baseline=PHYSICAL_BASELINE,
                publication_state=f'PHYSICALLY_APPROVED ({"; ".join(v.split(" (")[0] for v in p["validations"])})')


def deadline(last, days):
    return (dt.date.fromisoformat(last) + dt.timedelta(days=days)).isoformat()


def build():
    items = []
    for x in json.loads(J2B.read_text(encoding='utf-8'))['items']:
        _, klass, num = x['source_id'].split(':')[:3]
        items.append(dict(source_id=x['source_id'], classe=klass, processo=num, targets=x['targets'], state=STATE[x['source_id']],
                          status_processual='; '.join(x['status_processual']), last_known_state=x['last_known_state'],
                          last_verified_on=x['last_verified_on'], max_age_days=x['max_age_days'],
                          deadline=deadline(x['last_verified_on'], x['max_age_days']), trigger=x['trigger'], check=x['check']['url'],
                          origin=dict(file=J2B.relative_to(HERE).as_posix(), recommendations=[]), **publication(x['source_id']),
                          on_trigger=x['on_trigger']))
    for f in sorted(glob.glob(str(HERE / 'J2_*_BACKLOG/J2_BATCH*_DECISIONS.json'))):
        for d in json.loads(Path(f).read_text(encoding='utf-8'))['decisions']:
            rv = d.get('revalidation')
            if not rv:
                continue
            pid = rv.get('applies_to') or d['precedents'][0]['id']
            _, klass, num = pid.split(':')[:3]
            items.append(dict(source_id=pid, classe=klass, processo=num, targets=d['recommended_targets'], state=STATE[pid],
                              status_processual=d['status_processual'], last_known_state=d['status_processual'],
                              last_verified_on=rv['last_verified_on'], max_age_days=rv['max_age_days'],
                              deadline=deadline(rv['last_verified_on'], rv['max_age_days']), trigger=rv['trigger'], check=rv['check'],
                              origin=dict(file=Path(f).relative_to(HERE).as_posix(), recommendations=[d['recommendation_id']]),
                              decision=d['decision'], **publication(pid), on_trigger=ON_TRIGGER))
    doc = dict(schema_version=1, round='J2', kind='PROVISIONAL_REGISTRY', auto_publish=False, states=STATES,
               policy='Itens provisórios de jurisprudência (cautelar, mérito ou referendo pendente, tema-líder pendente). Gate obrigatório antes de '
                      'qualquer ratificação material ou deploy: check_j2b_provisional.py --registry J2_PROVISIONAL_REGISTRY.json --as-of <data>. '
                      'Estado jurídico (state, status_processual, legal_nature, revalidação) é separado do estado editorial/físico '
                      '(editorial_state, physical_state, publication_state): aprovação humana e física NÃO tornam o item definitivo.',
               items=items)
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
    for x in json.loads(b)['items']:
        print(x['source_id'], x['state'], x['deadline'], x['publication_state'])


if __name__ == '__main__':
    main()
