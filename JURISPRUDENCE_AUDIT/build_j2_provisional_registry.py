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
                          origin=dict(file=J2B.relative_to(HERE).as_posix(), recommendations=[]), publication_state='PHYSICALLY_INSTALLED (J2C)',
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
                              publication_state=f'AWAITING_USER_RATIFICATION ({d["decision"]})',
                              on_trigger='Rever o vínculo e a ficha antes de ratificar ou publicar; sem revisão, não publicar (fail closed).'))
    doc = dict(schema_version=1, round='J2', kind='PROVISIONAL_REGISTRY', auto_publish=False, states=STATES,
               policy='Itens provisórios de jurisprudência (cautelar, mérito ou referendo pendente, tema-líder pendente). Gate obrigatório antes de '
                      'qualquer ratificação material ou deploy: check_j2b_provisional.py --registry J2_PROVISIONAL_REGISTRY.json --as-of <data>.',
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
