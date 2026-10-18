"""CC-J1 — formal human ratification record (user, chat, 2026-10-18). Immutable over its inputs: CC_J1_DECISIONS.json and the ratification
dossier are pinned by sha256 and are NOT modified; this record is the only place that says HUMAN_APPROVED for CC-J1. Nothing materialized,
nothing deployed, no physical package. Additional targets approved by the user must be official STJ legislative references (fail closed).
Writes CC_J1_RATIFICATION_RECORD.json.   Usage: python build_cc_j1_ratification_record.py [--check]
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / 'JURISPRUDENCE_AUDIT'), str(ROOT / 'LEGAL_TARGET_ID')]
import juris_types as JT  # noqa: E402
import target_id as T  # noqa: E402

DEC = HERE / 'CC_J1_DECISIONS.json'
DOSSIER = HERE / 'CC_J1_RATIFICATION_DOSSIER.json'
STJ = HERE / 'stj/STJ_SUMULAS_INDEX.json'
CC_INDEX = ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json'
OUT = HERE / 'CC_J1_RATIFICATION_RECORD.json'
RATIFICATION = dict(by='ARTHUR', on='2026-10-18', channel='chat',
                    statement='Ratificação do CC-J1: os 8 GREEN; 14 YELLOW (com targets finais definidos pelo usuário); CCJ1-09 e CCJ1-30 pendentes; '
                              'os 6 RED não aprovados. Sem materialização, sem pacote físico, sem deploy.')
APPROVED, PENDING, NOT_APPROVED = 'HUMAN_APPROVED', 'PENDING', 'HUMAN_REJECTED_OR_NOT_APPROVED'
# rank -> (human state, final targets, note)
H = {
    1: ('HUMAN_APPROVED', ['CC2002:ART.20'], None),
    3: ('HUMAN_APPROVED', ['CC2002:ART.1790'], None),
    4: ('HUMAN_APPROVED', ['CC2002:ART.1790'], None),
    10: ('HUMAN_APPROVED', ['CC2002:ART.21'], None),
    14: ('HUMAN_APPROVED', ['CC2002:ART.877'], None),
    15: ('HUMAN_APPROVED', ['CC2002:ART.1647:INC.III'], None),
    23: ('HUMAN_APPROVED', ['CC2002:ART.206:PAR.5:INC.I'], None),
    29: ('HUMAN_APPROVED', ['CC2002:ART.1696'], None),
    2: ('HUMAN_APPROVED_MULTI_TARGET', ['CC2002:ART.186', 'CC2002:ART.927'],
        'Julgamento conjunto ADI 6792/7055 (ficha conjunta); interpretação conforme aos arts. 186 e 927, caput (responsabilidade civil da imprensa).'),
    5: ('HUMAN_APPROVED_REALLOCATE', ['CC2002:ART.1723:PAR.1'], 'Somente o art. 1.723, § 1º (ressalvado pela tese); art. 1.727 não acrescentado.'),
    6: ('HUMAN_APPROVED_REALLOCATE', ['CC2002:ART.1641:INC.II'], 'A tese interpreta o inciso II; Tema 1236 com trânsito em julgado em 10/04/2024.'),
    7: ('HUMAN_APPROVED_REALLOCATE', ['CC2002:ART.927:PAR.UNICO'], 'Parágrafo único (não o caput); ficha STF_RG_932 compartilhada entre CF e CC.'),
    11: ('HUMAN_APPROVED', ['CC2002:ART.186'], 'Referência legislativa oficial do STJ; uma ficha para os dois vínculos da Súmula 403; art. 20 não acrescentado.'),
    12: ('HUMAN_APPROVED', ['CC2002:ART.927'], 'Mesma ficha da CCJ1-11.'),
    13: ('HUMAN_APPROVED', ['CC2002:ART.1420'], 'Referência legislativa oficial do STJ; eficácia da hipoteca perante adquirentes.'),
    17: ('HUMAN_APPROVED_MULTI_TARGET', ['CC2002:ART.206:PAR.3:INC.IX', 'CC2002:ART.2028'],
         'Prescrição da cobrança do DPVAT; preservar o contexto legislativo; revalidar se a súmula for cancelada ou o STJ alterar a orientação. '
         'Não considerada superada pela reforma geral de seguros.'),
    18: ('HUMAN_APPROVED', ['CC2002:ART.205'], 'Prazo geral decenal; art. 206 não acrescentado; eventual art. 2.028 exige evidência própria.'),
    20: ('HUMAN_APPROVED_MULTI_TARGET', ['CC2002:ART.662', 'CC2002:ART.917'],
         'Dispositivos específicos de mandato e endosso-mandato; vínculo genérico ao art. 186 NÃO criado.'),
    21: ('HUMAN_APPROVED_MULTI_TARGET', ['CC2002:ART.99', 'CC2002:ART.1231'], 'Contexto da ficha: terrenos de marinha / propriedade da União.'),
    22: ('HUMAN_APPROVED_CONTEXTUAL', ['CC2002:ART.966'],
         'CONTEXTUAL_APPLICATION: assunto principal tributário (Sesc/Senac); o art. 966 entra como conceito de empresário usado pelo STJ.'),
    25: ('HUMAN_APPROVED_MULTI_TARGET', ['CC2002:ART.2028', 'CC2002:ART.206:PAR.3:INC.IV', 'CC2002:ART.206:PAR.5:INC.I'],
         'TEMPORAL_CONTEXT = CC1916_TO_CC2002.'),
    27: ('HUMAN_APPROVED_MULTI_TARGET', ['CC2002:ART.1226', 'CC2002:ART.1267'], 'Contexto: alienação de veículo / IPVA / transferência da propriedade móvel.'),
    9: ('PENDING_HUMAN_REVIEW', [], 'MATERIAL_EXCEPTION_POSSIBLE: a fonte oficial consultada não ancora a tese no art. 206-A. Reabrir com evidência oficial '
                                    'de pertinência direta ao art. 206-A. Não rejeitado.'),
    30: ('PENDING_TEMPORAL_REVALIDATION', [], 'NO_CC_RELATION_PUBLISHED. Súmula 609 consta na base oficial, mas os arts. 765 e 766 de suas referências foram '
                                             'revogados pela Lei 15.040/2024. Reabrir com: (1) decisão do STJ posterior à vigência da lei aplicando a súmula; '
                                             '(2) eventual cancelamento, revisão ou distinção; (3) correspondência com a nova Lei de Seguros.'),
}


def sha_lf(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def build():
    dec, dos = json.loads(DEC.read_text(encoding='utf-8')), json.loads(DOSSIER.read_text(encoding='utf-8'))
    if dos['decisions_sha256_lf'] != sha_lf(DEC):
        raise SystemExit('DOSSIER_NOT_FOR_THESE_DECISIONS')
    idx = {t['target_id'] for t in json.loads(CC_INDEX.read_text(encoding='utf-8'))['targets']}
    stj = {f"STJ:SUMULA:{e['number']}": e for e in json.loads(STJ.read_text(encoding='utf-8'))['entries']}
    groups = {i['rank']: i for i in dos['items']}
    items = []
    for x in dec['decisions']:
        r = x['rank']
        g = groups[r]['group']
        if r in H:
            state, targets, note = H[r]
        elif g == 'RED':
            state, targets, note = NOT_APPROVED, [], f"{x['decision']} (categoria do dossiê). {groups[r]['reopen']}"
        else:
            raise SystemExit(f'NO_HUMAN_DECISION {r}')
        if g == 'RED' and state != NOT_APPROVED:
            raise SystemExit(f'RED_APPROVED {r}')
        for t in targets:
            T.parse_target_id(t)
            if t not in idx:
                raise SystemExit(f'TARGET_NOT_IN_CC2002_INDEX {t}')
        added = [t for t in targets if t not in x['proposed_targets']]
        if added and x['tribunal'] == 'STJ':                               # extra targets only from the STJ's own legislative references
            refs = {t for ref in stj[x['precedent']]['references'] for t in ref['targets']}
            if not set(added) <= refs:
                raise SystemExit(f'ADDED_TARGET_NOT_OFFICIAL_REFERENCE {r} {added}')
        elif added:
            raise SystemExit(f'ADDED_TARGET_WITHOUT_OFFICIAL_BASIS {r} {added}')
        approved = state.startswith('HUMAN_APPROVED')
        items.append(dict(id=f'CCJ1-{r:02d}', rank=r, precedent=x['precedent'], label=x['device_label'], tribunal=x['tribunal'],
                          dossier_group=g, proposed_decision=x['decision'], proposed_targets=x['proposed_targets'], human_state=state,
                          final_targets=targets, targets_added=added, targets_dropped=[t for t in x['proposed_targets'] if t not in targets],
                          relation_note='CONTEXTUAL_APPLICATION' if state == 'HUMAN_APPROVED_CONTEXTUAL' else None,
                          temporal_context='CC1916_TO_CC2002' if r == 25 else ('DPVAT_LEGISLATIVE_CONTEXT' if r == 17 else None),
                          note=note, human_approved=approved, materialized=False))
    appr = [i for i in items if i['human_approved']]
    rels = sorted({(t, i['precedent']) for i in appr for t in i['final_targets']})
    c = collections.Counter('APPROVED' if i['human_approved'] else ('PENDING' if i['human_state'].startswith('PENDING') else 'NOT_APPROVED') for i in items)
    doc = dict(schema_version=1, kind='HUMAN_RATIFICATION', batch='CC-J1', norm='CC2002', ratification=RATIFICATION,
               pinned=dict(cc_j1_decisions_sha256_lf=sha_lf(DEC), dossier_sha256_lf=sha_lf(DOSSIER), stj_index_sha256_lf=sha_lf(STJ)),
               physical_baseline='J2I_FROZEN_315_198 (inalterado)', materialized=False, deployed=False, physical_package=False,
               counts=dict(TOTAL_PROPOSALS=len(items), PROPOSALS_HUMAN_APPROVED=c['APPROVED'], PROPOSALS_PENDING=c['PENDING'],
                           PROPOSALS_REJECTED=c['NOT_APPROVED'], NORMALIZED_RELATIONS_APPROVED=len(rels),
                           DISTINCT_CC_TARGETS_APPROVED=len({t for t, _ in rels}), DISTINCT_PRECEDENTS_APPROVED=len({p for _, p in rels}),
                           DISTINCT_FICHAS_REQUIRED=len({JT.ficha(p) for _, p in rels}),
                           ADDITIONAL_TARGETS_APPROVED=sum(len(i['targets_added']) for i in items)),
               approved_relations=[dict(target_id=t, precedent=p) for t, p in rels],
               pending=[i['id'] for i in items if i['human_state'].startswith('PENDING')],
               not_approved=[i['id'] for i in items if i['human_state'] == NOT_APPROVED], next_step='CC-J1 MATERIALIZATION PREFLIGHT', items=items)
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = build()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    print(json.dumps(json.loads(b)['counts'], ensure_ascii=False, indent=1))
