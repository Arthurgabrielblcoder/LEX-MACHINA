"""CC_J1_SIMULATION_CANDIDATE — host-only SIMULATION package (never deployed): the frozen CF baseline (J2I, 315 relations) + the CC-J1
relations that are PROMOTE/REALLOCATE, have an official source and no temporal block (CURRENT or HISTORICAL_BUT_RELEVANT), packaged by
the GENERIC packager into the normalized layer read by the multinorm firmware prototype. CC relations are NOT human-approved.
Writes cc_j1_simulation/SD/... + CC_J1_SIMULATION_MANIFEST.json.   Usage: python build_cc_j1_simulation.py [--check]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / 'pilot_cc')]
import generic_packager as P  # noqa: E402
import cc_pilot_evidence as EV  # noqa: E402

DEC = HERE / 'CC_J1_DECISIONS.json'
OUT = HERE / 'cc_j1_simulation'
TEMA = 'https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num={}'


def records_and_fichas(dec):
    prec, fichas = {}, {}
    by = {x['precedent']: x for x in dec['decisions']}
    for r in dec['simulation_relations']:
        pid = r['precedent']
        if pid in prec:
            continue
        x = by[pid]
        trib, klass, num = pid.split(':')
        if trib == 'STJ':
            prec[pid] = dict(tipo='sumula', tribunal='STJ', numero=num, status='vigente', titulo=f'Súmula {num} STJ', fonte=x['source']['url'])
            body = ['SÚMULA %s DO STJ' % num, 'TRIBUNAL: STJ', 'SIMULAÇÃO — NÃO PUBLICADO (CC-J1, aguardando ratificação)', f'ÓRGÃO JULGADOR: {x["orgao"]}',
                    '', 'ENUNCIADO', x['enunciado'], '', 'JULGAMENTO', f'{x["decisao"]}; {x["fonte"]}.', '', 'FONTE OFICIAL', x['source']['url']]
        else:
            numero = num.replace('-', '/')
            tipo = 'repercussao_geral' if klass == 'RG' else klass.lower()
            titulo = f'Tema de Repercussão Geral {numero}' if klass == 'RG' else f'{klass} {numero}' + (' (julgamento conjunto)' if '-' in num else '')
            prec[pid] = dict(tipo=tipo, tribunal='STF', numero=numero, status='tese_fixada' if klass == 'RG' else 'merito_julgado', titulo=titulo,
                             fonte=TEMA.format(num) if klass == 'RG' else x['source']['url'])
            base = 'STF:ADI:6792' if pid == 'STF:ADI:6792-7055' else pid
            src = EV.SOURCES[EV.PRECEDENTS[base]['sources'][0]]
            body = [titulo.upper(), 'TRIBUNAL: STF', 'SIMULAÇÃO — NÃO PUBLICADO (CC-J1, aguardando ratificação)', '', 'RESUMO DA FONTE OFICIAL',
                    src['proves'], '', 'TRECHO OFICIAL', EV.PRECEDENTS[base]['evidence'], '', 'FONTE OFICIAL', src['url']]
        fichas[P.JT.ficha(pid)] = '\n'.join(body) + '\n'
    return prec, fichas


def build():
    dec = json.loads(DEC.read_text(encoding='utf-8'))
    cf_rels, cf_prec = P.cf_fixture()
    cc_prec, cc_fichas = records_and_fichas(dec)
    for pid, meta in cc_prec.items():
        if pid in cf_prec:
            cc_prec[pid] = cf_prec[pid]                                    # precedent already on the card (e.g. Tema 932): reuse its record
    cc_rels = [dict(norm='CC2002', target_id=r['target_id'], precedent_id=r['precedent'], origin='CC-J1 (SIMULATION_ONLY)') for r in dec['simulation_relations']]
    files = P.package(cf_rels + cc_rels, {**cf_prec, **cc_prec}, P.card_fichas(), new_fichas=cc_fichas, provisional_ids=P.provisional_ids(),
                      known_targets=P.known_targets())
    m = json.loads(files[P.LAYER + '/MULTINORM_MANIFEST.json'])
    man = dict(schema_version=1, kind='CC_J1_SIMULATION_CANDIDATE', status='SIMULATION_ONLY', deployable=False, cc_human_approved=False,
               cf_base='J2I_FROZEN_315_198 (legacy 05_INDICES_ESP32 untouched; CF via LEXV1 on the device)', layer=P.LAYER,
               counts={n: (v['relations'], v['targets_with_j']) for n, v in m['norms'].items()}, duplicate_query_keys=m['totals']['DUPLICATE_QUERY_KEYS'],
               fichas_new=sorted(k.split('/')[-1] for k in files if k.startswith(P.CONTENT)), fichas_shared_across_norms=m['fichas_shared_across_norms'])
    files['CC_J1_SIMULATION_MANIFEST.json'] = (json.dumps(man, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    return {(f'SD/{k}' if not k.endswith('SIMULATION_MANIFEST.json') else k): v for k, v in files.items()}


def main():
    files = build()
    if '--check' in sys.argv:
        ok = all((OUT / k).is_file() and (OUT / k).read_bytes() == v for k, v in files.items())
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    for k, v in files.items():
        (OUT / k).parent.mkdir(parents=True, exist_ok=True)
        (OUT / k).write_bytes(v)
    print(json.loads(files['CC_J1_SIMULATION_MANIFEST.json']))


if __name__ == '__main__':
    main()
