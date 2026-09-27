"""Gate from human protocol and pre-frozen control floors; no tuning after metrics."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'05_COMPILADOR'))
from proof_compiler_r1 import load, require
from r1d_support import ROOT, write, now, key, integrity
from run_regression_r1d import verify_freeze


def run():
    freeze=verify_freeze()
    r=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D.json')
    sim=load(ROOT/'06_BENCHMARKS/SIMULACAO_GARANTIA_DEPENDENTE_V1.json')
    policy=load(ROOT/'01_SCHEMA/POLITICA_EDITORIAL_REFERENCIAS_V2_V1.json')['gate_protocol']
    overlay=load(ROOT/'03_OBRAS/CURADORIA_EDITORIAL_R1D.json')
    tech=load(ROOT/'06_BENCHMARKS/OITO_LACUNAS_TECNICAS_R1D.json')
    contracts=load(ROOT/'06_BENCHMARKS/CONTRATOS_ADICIONAIS_14_POS_POLITICA.json')
    human=load(ROOT/'06_BENCHMARKS/ADJUDICACAO_HUMANA_R1C_V1.json')
    tests=load(ROOT/'00_CHECKPOINTS/TEST_RESULTS_R1D.json')
    integ=integrity();g=r['groups'];by={key(x):x for x in r['cases']}
    impacted={key(x) for x in sim['cases'] if x['impacto']=='TP_HISTORICO_PARA_READJUDICACAO'}
    unexpected_lost=[x for x in r['lost_admissions'] if x['r1c_metric']=='TP' and key(x) not in impacted]
    new_fp=[x for x in r['cases'] if x['metric']=='FP' and x['r1c_metric']!='FP']
    changed_ds={d['device_id'] for d in overlay['devices']}
    changed_ws={e['work_id'] for e in overlay['evidence_replacements']+overlay['evidence_additions']}
    unexplained=[x for x in r['cases'] if x['r1c_state']!=x['admissibility'] and x['device_id'] not in changed_ds and x['work_id'] not in changed_ws]
    # Adjudications are validated against real proof output, never forcibly applied to state.
    approved=[x for x in human['cases']+contracts['cases'] if x['rotulo_adjudicado_v1']=='APROVAR']
    missing_approved=[x for x in approved if by[key(x)]['admissibility']!='ADMISSIVEL']
    resolved_mismatch=[x for x in tech['cases'] if x['resolution']=='RESOLVIDA' and by[key(x)]['admissibility']!='ADMISSIVEL']
    checks=dict(
        integrity=integ['passed'],tests=tests['passed'],single_regression=r['runs']==1,
        frozen_input=r['input_hash']==freeze['input_hash'],
        no_new_structural_failure=not (unexpected_lost or new_fp or unexplained or missing_approved or resolved_mismatch),
        known_fp_controlled=r['matrix']['FP']<=policy['max_known_fp'],
        four_fp_eliminated=all(by[key(x)]['admissibility']!='ADMISSIVEL' for x in human['fp_confirmados']),
        old_tp_not_artificially_protected=all(by[k]['admissibility']!='ADMISSIVEL' for k in impacted),
        recent25_preserved=g['recent60']['historical_counts']['TP']>=policy['recent25_admissible_min'],
        recent35_controlled=g['recent60']['historical_counts']['FP']<=policy['recent35_max_fp'],
        recent20_negative_preserved=g['recent20']['historical_counts']['TN']>=policy['recent20_negative_min'],
        mechanisms15_preserved=g['mechanisms15']['historical_counts']['TP']>=policy['mechanisms15_admissible_min'],
        mechanisms10_negative_preserved=g['negatives10']['historical_counts']['TN']>=policy['negative_mechanisms10_min'],
        contractual_cases_disposed=len(human['cases'])==12 and len(contracts['cases'])==14 and all(x['rotulo_adjudicado_v1'] in ['APROVAR','REJEITAR','EVIDENCIA_INSUFICIENTE','PENDENTE_HUMANO'] for x in human['cases']+contracts['cases']),
        technical_eight_closed=len(tech['cases'])==8 and all(x['research_closed'] and x['resolution'] in ['RESOLVIDA','EVIDENCIA_INSUFICIENTE'] for x in tech['cases']))
    passed=all(checks.values())
    report=dict(at=now(),status='EXECUCAO_COMPLETA_R1D_AUTORIZADA' if passed else 'R1D_REGRESSION_COMPLETE_GATE_FAILED',passed=passed,
        decision='EXECUCAO_COMPLETA_R1D' if passed else 'BLOQUEAR_EXECUCAO_COMPLETA_R1D',input_hash=r['input_hash'],checks=checks,
        unexpected_tp_losses=unexpected_lost,new_fp=new_fp,unexplained_transitions=unexplained,approved_without_proof=missing_approved,
        technical_resolution_mismatches=resolved_mismatch,matrix=r['matrix'],historical_label_matrix=r['historical_label_matrix'],
        policy_pending_allowed=True,holdout_opened=False)
    write('00_CHECKPOINTS/R1D_GATE_DECISION.json',report)
    print(report['decision']);print(checks)


if __name__=='__main__':run()
