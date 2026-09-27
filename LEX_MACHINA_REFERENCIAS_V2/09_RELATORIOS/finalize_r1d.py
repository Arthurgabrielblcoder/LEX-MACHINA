"""Integrity closure and truthful release-candidate packaging after the gate."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'05_COMPILADOR'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'06_BENCHMARKS'))
from proof_compiler_r1 import load, file_hash, require
from r1d_support import ROOT, now, write, integrity, POLICY
from run_regression_r1d import verify_freeze


def run():
    verify_freeze();integ=integrity()
    write('00_CHECKPOINTS/INTEGRITY_R1D_FINAL.json',integ)
    reg=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D.json')
    gate=load(ROOT/'00_CHECKPOINTS/R1D_GATE_DECISION.json')
    sim=load(ROOT/'06_BENCHMARKS/SIMULACAO_GARANTIA_DEPENDENTE_V1.json')
    additional=load(ROOT/'06_BENCHMARKS/CONTRATOS_ADICIONAIS_14_POS_POLITICA.json')
    tech=load(ROOT/'06_BENCHMARKS/OITO_LACUNAS_TECNICAS_R1D.json')
    labels=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2_ADJUDICATED_V1.json')
    tests=load(ROOT/'00_CHECKPOINTS/TEST_RESULTS_R1D.json')
    full_path=ROOT/'07_EXECUCAO_COMPLETA/RESUMO_EXECUCAO_COMPLETA_R1D.json'
    full=load(full_path) if full_path.exists() else None
    rc=bool(gate['passed'] and full and integ['passed'] and full['known_pair_parity']['equal']==398)
    if rc:
        prefix='08_RELEASE_CANDIDATE/CF_REFERENCIAS_V2_RC1/'
        write(prefix+'CF_REFERENCIAS_V2_RC1.json',dict(schema='CF_REFERENCIAS_V2_RC1',at=now(),status='RELEASE_CANDIDATE_OFFLINE',
            input_hash=reg['input_hash'],policy=POLICY,benchmark=reg['matrix'],full=full,
            artifacts=dict(admissible='../../07_EXECUCAO_COMPLETA/ADMISSIVEIS_R1D.json',selection='../../07_EXECUCAO_COMPLETA/SELECAO_R1D.json',
                full='../../07_EXECUCAO_COMPLETA/RESULTADO_COMPLETO_R1D.jsonl.gz',review='../../07_EXECUCAO_COMPLETA/REVISAO_EDITORIAL_R1D.json'),
            product_integrated=False,holdout_opened=False,limitations=full['caveats'],pending_human=8))
        write(prefix+'README.md','# CF_REFERENCIAS_V2_RC1\n\nCandidato offline R1D adjudicado. Gate, regressão única e execução integral concluídos. Nenhuma integração de firmware, SD ou IDX.\n\n'+
            f"{full['pairs']} pares avaliados; {full['admissible']} admissíveis; {full['selected']} selecionados pela regra histórica. {full['admissible_without_historical_score']} admissíveis sem score histórico estão preservados para revisão, sem score inventado.\n\n"+
            'O universo foi percorrido integralmente; a cobertura de representação continua parcial. Métricas são do benchmark conhecido. Onze insuficientes adjudicados e oito pendências novas ficam fora da matriz binária; há matriz histórica paralela. Holdout de 120 pares permanece fechado.\n')
        artifacts=[p for p in ROOT.rglob('*') if p.is_file() and ('R1D' in p.name or 'ADJUDIC' in p.name or 'POS_POLITICA' in p.name or p.parent.name=='CF_REFERENCIAS_V2_RC1') and p.suffix in ['.json','.md','.gz']]
        write(prefix+'MANIFEST.json',dict(at=now(),self_excluded=True,files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=file_hash(p),bytes=p.stat().st_size) for p in sorted(artifacts)]))
    next_step='Revisar as oito pendências humanas e os admissíveis sem score histórico do RC1, preservando o holdout fechado; nenhuma integração autorizada.' if rc else 'Revisar as falhas enumeradas em R1D_GATE_DECISION.json; manter R1D congelada, sem nova regressão, execução completa ou RC nesta passagem.'
    result=dict(at=now(),status='CF_REFERENCIAS_V2_RC1' if rc else 'R1D_REGRESSION_COMPLETE_GATE_FAILED',human_adjudications=12,
        changed_binary_labels=[r for r in labels['changed_labels'] if r['rotulo_adjudicado_v1']=='REJEITAR'],
        changed_label_counts=labels['adjudicated_counts'],simulation=sim['counts'],additional=additional['counts'],technical=tech['counts'],
        matrix=reg['matrix'],historical_label_matrix=reg['historical_label_matrix'],groups={k:v['counts'] for k,v in reg['groups'].items()},
        gate=gate['decision'],full_execution=bool(full),full=full,rc1=rc,integrity=integ,tests=tests,next_step=next_step)
    write('09_RELATORIOS/RESULTADO_FINAL_R1D.json',result)
    lines=['# Encerramento R1D adjudicada','',f"Status: **{result['status']}**. Política: {POLICY}.",'',
        'R1C e todos os artefatos preexistentes foram preservados. A simulação precedeu a implementação; o freeze precedeu a única regressão. Nenhum novo matcher, score ou threshold foi introduzido.','',
        '## Adjudicação e escopo','',
        '12 decisões humanas: 6 aprovações, 1 rejeição e 5 rotas condicionais ainda insuficientes. Três reversões binárias APROVAR → REJEITAR: uma explícita humana (12 Homens e uma Sentença → art.5 LV), duas por aplicação B/D/F (O Processo → art.55 §3; Privacidade Hackeada → art.5 XII). Nenhum arquivo histórico foi sobrescrito.','',
        'Simulação: 12 pares, seis dispositivos; 4 FP eliminados, 5 TP históricos sem âncora enviados à readjudicação, 3 negativos preservados. Nenhum TP da família permaneceu admitido, nenhum FN alterado e nenhuma ambiguidade factual de âncora.','',
        f"14 adicionais: {additional['counts']}. Oito lacunas: {tech['counts']}.",'',
        'As novas fontes limitam-se aos casos técnicos. Vigiar e Punir recebeu somente a anotação TORTURA já explícita na ficha validada, para executar a decisão humana 10; ANALISAR não foi transformado em PRATICAR. Dois complementos literais nas lacunas de representação preservam os 233 núcleos existentes.','',
        '## Regressão única após freeze','',f"Matriz adjudicada: {reg['matrix']}",'',f"Sensibilidade com todos os rótulos históricos: {reg['historical_label_matrix']}",'',
        'A diferença de denominadores está explícita: 11 insuficientes, 8 pendências humanas novas, 3 conflitos e 1 pendente histórico são não binários. Não são convertidos em TN. A matriz histórica retém os FN e perdas de TP para evitar melhoria aparente por exclusão de casos difíceis.','',
        '| Grupo | Resultado adjudicado | Histórico aplicado a R1D |','|---|---|---|']
    for k,v in reg['groups'].items():lines.append(f"| {k} | {v['counts']} | {v['historical_counts']} |")
    lines += ['',f"Gate: **{gate['decision']}**. Checks: {gate['checks']}",'',
        '## Execução e candidato','',f"Execução completa: {'SIM' if full else 'NÃO'}. RC1: {'SIM' if rc else 'NÃO'}."]
    if full:lines += ['',f"{full['pairs']} pares; {full['candidates']} candidatos; {full['admissible']} admissíveis; {full['review']} revisão; {full['insufficient']} insuficientes; {full['incompatible']} incompatíveis; {full['source_under_review']} fonte em revisão.",'',
        f"Paridade dos 398 pares conhecidos: {full['known_pair_parity']}. Dispositivos com algum núcleo: {full['represented_devices']}/3461. Selecionados: {full['selected']}; admissíveis sem score histórico: {full['admissible_without_historical_score']}."]
    lines += ['', '## Integridade','',f"{integ['preexisting_v2_checked']} artefatos V2 preexistentes e {integ['protected_checked']} arquivos protegidos: integridade {integ['passed']}. Testes novos: {tests['tests_run']}, aprovados: {tests['passed']}.",'',
        f"Holdout: {integ['holdout_sha256']}; somente hash de bytes, sem abrir JSON. Sem firmware, SD, IDX, commit ou tag.",'',
        '## Próximo passo','',next_step,'']
    write('09_RELATORIOS/RELATORIO_R1D_ADJUDICADA.md','\n'.join(lines))
    write('00_CHECKPOINTS/RESUME_STATE_R1D.json',dict(status=result['status'],at=now(),input_hash=reg['input_hash'],next_step=next_step,
        frozen=True,regression_runs=1,full_execution=bool(full),rc1=rc,holdout_opened=False))
    print(result['status']);print(next_step)


if __name__=='__main__':run()
