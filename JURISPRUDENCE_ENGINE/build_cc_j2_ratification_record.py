"""CC-J2 — formal human ratification record (user, chat, 2026-10-18). Immutable over its inputs: the CC-J2 decisions, review, preliminary and
final dossiers, sources and metrics are pinned by sha256 (LF) and are NOT modified; this record is the only place that says HUMAN_APPROVED for
CC-J2. Every human change of target/status versus the original proposal is recorded. Fail closed: approved targets must exist in the CC index,
must not already be physical, and must be among the targets the final dossier put on the table; rejected items must be RED in the final dossier.
Nothing materialized, nothing deployed, no physical package.   Writes CC_J2_RATIFICATION_RECORD.json.
Usage: python build_cc_j2_ratification_record.py [--check]
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import batch_engine as E  # noqa: E402
import juris_types as JT  # noqa: E402

AS_OF = '2026-10-18'                    # device knowledge at ratification time (record stays reproducible)
DEC = HERE / 'CC_J2_DECISIONS.json'
FINAL = HERE / 'CC_J2_RATIFICATION_DOSSIER_FINAL.json'
CC_INDEX = ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json'
PHYSICAL_SD = HERE / 'CC_J1_MATERIALIZATION_CANDIDATE/candidate/SD'
CARD = HERE / 'CC_J1_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
OUT = HERE / 'CC_J2_RATIFICATION_RECORD.json'
PINNED = ['CC_J2_DECISIONS.json', 'CC_J2_REVIEW.md', 'CC_J2_RATIFICATION_DOSSIER.md', 'CC_J2_RATIFICATION_DOSSIER.json',
          'CC_J2_RATIFICATION_DOSSIER_FINAL.md', 'CC_J2_RATIFICATION_DOSSIER_FINAL.json', 'CC_J2_SCALE_METRICS.json', 'CC_J2_SIMULATION_REPORT.md',
          'cc_j2/CC_J2_BACKLOG.json', 'cc_j2_simulation/CC_J2_SIMULATION_MANIFEST.json', 'cc_j2_review.py', 'cc_j2_final_review.py',
          'stj/STJ_SUMULAS_INDEX.json', 'stj/STJ_PRECEDENTES_INDEX.json', 'cc_j2/PLANALTO_CC2002_2026-10-18.json', 'cc_j2/STF_Q1_RECHECK.json',
          'pilot_cc/cc_pilot_evidence.py', 'CC_J1_RATIFICATION_RECORD.json']
RATIFICATION = dict(by='ARTHUR', on='2026-10-18', channel='chat',
                    statement='Ratificação do CC-J2: os 9 GREEN e os 10 YELLOW do dossiê final (targets finais definidos pelo usuário; Tema 1130 '
                              'como definitivo, não provisório); os 11 RED não aprovados. Sem materialização, sem pacote físico, sem deploy.')
# id -> (human state, final targets, editorial flags, note)
H = {
    'CCJ2-02': ('HUMAN_APPROVED', ['CC2002:ART.835'], [], None),
    'CCJ2-04': ('HUMAN_APPROVED', ['CC2002:ART.405'], [], None),
    'CCJ2-05': ('HUMAN_APPROVED', ['CC2002:ART.50'], [], None),
    'CCJ2-07': ('HUMAN_APPROVED', ['CC2002:ART.1829'], [], 'Ficha do Tema 498 já existe (reutilizar).'),
    'CCJ2-14': ('HUMAN_APPROVED', ['CC2002:ART.286'], [], None),
    'CCJ2-16': ('HUMAN_APPROVED', ['CC2002:ART.191'], [], None),
    'CCJ2-17': ('HUMAN_APPROVED', ['CC2002:ART.1829'], [], 'Ficha do Tema 809 já existe (reutilizar).'),
    'CCJ2-23': ('HUMAN_APPROVED', ['CC2002:ART.206:PAR.3:INC.III'], [], None),
    'CCJ2-25': ('HUMAN_APPROVED', ['CC2002:ART.354'], [], None),
    'CCJ2-01': ('HUMAN_APPROVED_MULTI_TARGET', ['CC2002:ART.1208', 'CC2002:ART.1255'], ['ONE_FICHA_TWO_LINKS'],
                'Relações materialmente diferentes: 1.208 = mera detenção; 1.255 = ausência de indenização pelas acessões na ocupação indevida '
                'de bem público. Ambos registrados pela fonte oficial do STJ. Art. 1.219 NÃO acrescentado nesta rodada.'),
    'CCJ2-06': ('HUMAN_APPROVED_HISTORICAL_CONTEXT', ['CC2002:ART.202:PAR.UNICO'], ['HISTORICAL_BUT_RELEVANT', 'CPC/1973',
                                                                                   'IAC_PHYSICAL_LABEL_VALIDATION_REQUIRED'],
                'A tese extrai do art. 202, p.u. a prescrição intercorrente nas causas regidas pelo CPC/1973; a ficha não pode apresentá-la '
                'como regra geral do CPC/2015.'),
    'CCJ2-08': ('HUMAN_APPROVED', ['CC2002:ART.206:PAR.5:INC.I'], [],
                'Somente o 206, § 5º, I; vínculo ao art. 2.028 NÃO criado (a transição já tem cobertura própria).'),
    'CCJ2-09': ('HUMAN_APPROVED_REALLOCATE_SOURCE_ERROR', ['CC2002:ART.943'], ['SOURCE_STRUCTURAL_ERROR_CORRECTED = ART943_INC1 -> ART943'],
                'A fonte oficial traz "ART:00943 INC:00001", mas o art. 943 não tem incisos; a norma material é o art. 943. Anomalia '
                'preservada na proveniência; nenhum target inexistente criado.'),
    'CCJ2-11': ('HUMAN_APPROVED_REALLOCATE', ['CC2002:ART.1238:PAR.UNICO'], [],
                'Não o caput: a tese fixa os 10 anos justamente na hipótese do parágrafo único (obras, utilidade pública, interesse social).'),
    'CCJ2-18': ('HUMAN_APPROVED_EXCEPTION_CONTEXT', ['CC2002:ART.1210:PAR.2'], ['EXCEPTION / INTERPRETATIVE LIMIT'],
                'A alegação de domínio não garante, por si, tutela possessória, mas pode aparecer incidentalmente (ente público). Não é '
                'reprodução literal do dispositivo.'),
    'CCJ2-20': ('HUMAN_APPROVED_WITH_SUPREME_COURT_QUALIFICATION', ['CC2002:ART.1641:INC.II'], ['SUBJECT_TO_TEMA_1236_STF'],
                'Não é duplicata do Tema 1236. Ficha: Súmula 655/STJ (separação obrigatória na união estável; comunicação dos bens com '
                'esforço comum) + Tema 1236/STF (regime afastável por escritura pública). Sem obrigatoriedade absoluta.'),
    'CCJ2-21': ('HUMAN_APPROVED_EXCLUSION_CONTEXT', ['CC2002:ART.354'], ['EXCLUSION_CONTEXT', 'INAPLICABILIDADE À COMPENSAÇÃO TRIBUTÁRIA'],
                'A ficha começa pela inaplicabilidade à compensação tributária; não é interpretação positiva geral do art. 354.'),
    'CCJ2-22': ('HUMAN_APPROVED_CURRENT', ['CC2002:ART.76:PAR.UNICO'], ['PROVISIONAL = NO', 'STJ_SOURCE_STATUS_STALE = YES',
                                                                       'STF_TEMA1432_RESOLVED_CONSTITUTIONAL_RISK = YES'],
                'Alterado pelo usuário em relação ao dossiê (PROVISIONAL → definitivo): o STJ ainda exibe "Acórdão Publicado - RE Pendente", '
                'mas o Tema 1432/STF decidiu "não há repercussão geral" (trânsito em 18/09/2026). Não entra no registro de provisórios.'),
    'CCJ2-29': ('HUMAN_APPROVED', ['CC2002:ART.206:PAR.3:INC.IV'], [],
                'Somente o 206, § 3º, IV; vínculo ao art. 2.028 NÃO criado (já tem jurisprudência transitória no baseline).'),
    'CCJ2-03': ('HUMAN_REJECTED_OR_NOT_APPROVED', [], ['REJECT_NOT_MATERIAL'], None),
    'CCJ2-13': ('HUMAN_REJECTED_OR_NOT_APPROVED', [], ['REJECT_NOT_MATERIAL'], None),
    'CCJ2-28': ('HUMAN_REJECTED_OR_NOT_APPROVED', [], ['REJECT_NOT_MATERIAL'], None),
    'CCJ2-10': ('HUMAN_REJECTED_OR_NOT_APPROVED', [], ['REJECT_SUPERSEDED'], None),
    'CCJ2-12': ('HUMAN_REJECTED_OR_NOT_APPROVED', [], ['REJECT_TEMPORAL_MISMATCH'], None),
    'CCJ2-15': ('HUMAN_REJECTED_OR_NOT_APPROVED', [], ['REJECT_NOT_MATERIAL'], None),
    'CCJ2-19': ('HUMAN_REJECTED_OR_NOT_APPROVED', [], ['REJECT_TEMPORAL_MISMATCH'], None),
    'CCJ2-24': ('HUMAN_REJECTED_OR_NOT_APPROVED', [], ['REJECT_TEMPORAL_MISMATCH'], None),
    'CCJ2-27': ('HUMAN_REJECTED_OR_NOT_APPROVED', [], ['REJECT_TEMPORAL_MISMATCH'], None),
    'CCJ2-30': ('HUMAN_REJECTED_OR_NOT_APPROVED', [], ['REJECT_TEMPORAL_MISMATCH'], None),
    'CCJ2-26': ('HUMAN_REJECTED_OR_NOT_APPROVED', [], ['REJECT_DUPLICATE'], None),
}
REJECT_CODE = {'REJECT_NOT_MATERIAL_RECOMMENDED': 'REJECT_NOT_MATERIAL', 'REJECT_SUPERSEDED_RECOMMENDED': 'REJECT_SUPERSEDED',
               'REJECT_TEMPORAL_MISMATCH_RECOMMENDED': 'REJECT_TEMPORAL_MISMATCH', 'DUPLICATE_RECOMMENDATION': 'REJECT_DUPLICATE'}


def sha_lf(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def build():
    dec = {x['id']: x for x in E.load(DEC)['decisions']}
    fin = {x['id']: x for x in E.load(FINAL)['items']}
    if sorted(H) != sorted(dec) or sorted(fin) != sorted(dec) or len(dec) != 30:
        raise SystemExit('RATIFICATION_DOES_NOT_COVER_THE_30')
    index = {t['target_id'] for t in E.load(CC_INDEX)['targets']}
    _, _, rows = E.physical_layer(PHYSICAL_SD)
    phys = {(r['target_id'], r['precedent_id']) for r in rows if E.namespace_of(r['target_id']) == 'CC2002'}
    cf_rel = sum(1 for r in rows if not r['target_id'].startswith('CC2002:'))
    phys_targets = {t for t, _ in phys}
    card = {k.split('/')[-1] for k in E.load(CARD)['entries'] if k.startswith(E.P.CONTENT + '/')}
    items, approved = [], []
    for i in sorted(dec):
        x, f = dec[i], fin[i]
        state, ts, flags, note = H[i]
        ok = state.startswith('HUMAN_APPROVED')
        if ok:
            if f['group_final'] == 'RED' or not ts:
                raise SystemExit(f'APPROVED_RED_OR_EMPTY {i}')
            for t in ts:
                if t not in index or (t, x['precedent']) in phys or t not in f['targets_final']:
                    raise SystemExit(f'BAD_APPROVED_TARGET {i} {t}')
            approved += [(t, x['precedent']) for t in ts]
        elif f['group_final'] != 'RED' or ts or REJECT_CODE[f['decision_final']] not in flags:
            raise SystemExit(f'BAD_REJECTION {i}')
        provisional = ok and f['decision_final'] == 'PROMOTE_PROVISIONAL_RECOMMENDED' and 'PROVISIONAL = NO' not in flags
        ficha = JT.ficha(x['precedent'])
        items.append(dict(id=i, rank=x['rank'], precedent=x['precedent'], label=x['device_label'], tribunal=x['tribunal'], channel=x['channel'],
                          original_proposal=dict(group=x['group'], decision=x['decision'], targets=x['proposed_targets']),
                          final_dossier=dict(group=f['group_final'], decision=f['decision_final'], targets=f['targets_final'],
                                             recommendation=f['recommendation']),
                          human_state=state, final_targets=ts, targets_added=sorted(set(ts) - set(x['proposed_targets'])),
                          targets_dropped=sorted(set(x['proposed_targets']) - set(ts)), status_changed_from_final_dossier=(
                              'PROVISIONAL → CURRENT' if f['decision_final'] == 'PROMOTE_PROVISIONAL_RECOMMENDED' and not provisional and ok else None),
                          editorial_flags=flags, relation=f['relation'], temporal=f['temporal'], note=note, ficha_note=f.get('ficha_note'),
                          source=x['source'], source_anomaly=f.get('source_anomaly'), reopen=None if ok else f['reopen'], provisional=provisional,
                          ficha=ficha if ok else None, ficha_on_card=(ficha in card) if ok else None,
                          device_status_physical=JT.physical_status(x['klass'], as_of=AS_OF) if ok else None, human_approved=ok, materialized=False))
    appr = sorted(set(approved))
    new_t = sorted({t for t, _ in appr} - phys_targets)
    proj = sorted(phys | set(appr))
    c = collections.Counter('APPROVED' if it['human_approved'] else 'NOT_APPROVED' for it in items)
    doc = dict(schema_version=1, kind='HUMAN_RATIFICATION', batch='CC-J2', norm='CC2002', ratification=RATIFICATION,
               pinned={k: sha_lf(HERE / k) for k in PINNED},
               physical_baseline='MULTINORM_FROZEN_CF315_198_CC29_24 (inalterado)', materialized=False, deployed=False, physical_package=False,
               counts=dict(TOTAL_PROPOSALS=len(items), APPROVED_PROPOSALS=c['APPROVED'], NOT_APPROVED=c['NOT_APPROVED'], PENDING=0,
                           APPROVED_RELATIONS=len(appr), DISTINCT_TARGETS_APPROVED=len({t for t, _ in appr}),
                           TARGETS_ALREADY_IN_CC_J1=len({t for t, _ in appr} & phys_targets), NEW_DISTINCT_TARGETS=len(new_t),
                           DISTINCT_PRECEDENTS_APPROVED=len({p for _, p in appr}),
                           FICHAS_REUSED_FROM_CARD=sorted({it['ficha'] for it in items if it['ficha_on_card']}),
                           NEW_FICHAS_REQUIRED=len({it['ficha'] for it in items if it['human_approved'] and not it['ficha_on_card']}),
                           PROVISIONAL_APPROVED=sum(it['provisional'] for it in items),
                           HUMAN_TARGET_OR_STATUS_CHANGES=sum(1 for it in items if it['human_approved'] and (
                               it['targets_added'] or it['targets_dropped'] or it['status_changed_from_final_dossier']))),
               baselines=dict(CC_PHYSICAL_BASELINE=f'{len(phys)}/{len(phys_targets)}', CF_ADCT_NORMALIZED_RELATIONS=cf_rel,
                              CF_PHYSICAL_BASELINE='315/198 (LEXV1; inalterado)',
                              PROJECTED_AFTER_CC_J2_MATERIALIZATION=f'{len(proj)}/{len({t for t, _ in proj})}',
                              projection_note='projeção, não baseline físico'),
               device=dict(SUMULA_STJ_PHYSICALLY_VALIDATED='YES' if JT.physical_status('SUMULA_STJ', as_of=AS_OF) == 'VALIDATED' else 'NO',
                           SUMULA_STJ_REFERENCE=JT.PHYSICAL_VALIDATION_RECORDS.get('SUMULA_STJ'),
                           IAC_SUPPORTED_ARCHITECTURALLY='YES' if JT.device_status('IAC') != 'NEW_JURIS_TYPE_REQUIRES_DESIGN' else 'NO',
                           IAC_PHYSICALLY_VALIDATED='YES' if JT.physical_status('IAC', as_of=AS_OF) == 'VALIDATED' else 'NO',
                           REPETITIVO_STJ_PHYSICALLY_VALIDATED='YES' if JT.physical_status('REPETITIVO', as_of=AS_OF) == 'VALIDATED' else 'NO',
                           physical_checklist_requirements=['IAC 1 (rótulo IAC) no CC art. 202, p.u.',
                                                            'REPETITIVO STJ n (primeira exibição física do rótulo)']),
               approved_relations=[dict(target_id=t, precedent=p) for t, p in appr], new_targets=new_t,
               not_approved=[it['id'] for it in items if not it['human_approved']], pending=[],
               next_step='CC-J2 MATERIALIZATION PREFLIGHT', items=items)
    return doc


def main():
    doc = build()
    b = (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    print(json.dumps(dict(doc['counts'], **doc['baselines'], **{k: v for k, v in doc['device'].items() if k.isupper()}), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
