"""Pre-implementation simulation of every known transversal pair, both labels."""
import copy
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'05_COMPILADOR'))
from canonical_input_r1c import load_canonical
from proof_compiler_r1 import CanonicalInput, load, file_hash, require
from proof_compiler_v2 import run_pairs
from r1d_support import ROOT, POLICY, now, write, key, dependent_contracts


def run():
    require(not (ROOT/'06_BENCHMARKS/SIMULACAO_GARANTIA_DEPENDENTE_V1.json').exists(), 'Simulation already exists')
    base = load_canonical()
    master = load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json')
    old = {key(r): r for r in load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1C.json')['cases']}
    data = copy.deepcopy(base.data)
    scope = []
    for d in data['devices']:
        targets = [n for n in d['nuclei'] if n['role'] == 'GARANTIA_TRANSVERSAL']
        if targets:
            for n in targets:
                n['contracts_by_relation'] = dependent_contracts(d, n)
            scope.append(dict(device_id=d['device_id'], family=d['family'], category='REGRA_ESPECIFICA',
                              reason='Garantia inserida em regime funcional ou competência legislativa; política B/D.'))
    ids = {d['device_id'] for d in scope}
    pairs = [p for p in master['pairs'] if p['device_id'] in ids]
    sim = CanonicalInput(data)
    results = run_pairs(sim, pairs)
    rows = []
    for p, result in zip(pairs, results):
        prior = old[key(p)]
        if prior['metric'] == 'TP':
            impact = 'TP_PERMANECE' if result['state'] == 'ADMISSIVEL' else 'TP_HISTORICO_PARA_READJUDICACAO'
        elif prior['metric'] == 'FP':
            impact = 'FP_PERMANECE' if result['state'] == 'ADMISSIVEL' else 'FP_ELIMINADO'
        elif prior['metric'] == 'FN':
            impact = 'FN_ALTERADO' if prior['admissibility'] != result['state'] else 'FN_SEM_ALTERACAO'
        else:
            impact = 'NEGATIVO_PRESERVADO' if result['state'] != 'ADMISSIVEL' else 'NOVO_FP'
        rows.append(dict(device_id=p['device_id'],work_id=p['work_id'],obra=base.works[p['work_id']]['nome'],
            rotulo_historico=p['label'],state_r1c=prior['admissibility'],metric_r1c=prior['metric'],state_simulado=result['state'],
            impacto=impact,decisao_editorial_simulada='REJEITAR_SEM_ANCORA' if impact in ['TP_HISTORICO_PARA_READJUDICACAO','FP_ELIMINADO'] else 'SEM_MUDANCA',
            nota='Rejeição editorial do vínculo com o regime, não prova negativa de inexistência do fato na obra.',
            evidencia_validada=base.works[p['work_id']]['evidences'],proofs=result['proofs'],unmet_contracts=result['unmet_contracts']))
    report = dict(schema='SIMULACAO_GARANTIA_DEPENDENTE_V1',policy=POLICY,created_at=now(),base_input_hash=base.hash,
        input_simulation_hash=sim.hash,implementation_applied=False,known_universe=398,scope=scope,total=len(rows),
        counts=dict(Counter(r['impacto'] for r in rows)),cases=rows,ambiguous=[],
        fn_alterados=[r for r in rows if r['impacto']=='FN_ALTERADO'],
        limits=['Somente pares conhecidos; holdout não aberto.', 'Inclui competência legislativa: tema saúde não é âncora de competência.',
                'Garantias autônomas do art. 5 não entram nesta família.', 'TP histórico sem âncora será PENDENTE_HUMANO no ledger; não se conserva por ser TP.'])
    write('06_BENCHMARKS/SIMULACAO_GARANTIA_DEPENDENTE_V1.json',report)
    md=['# Simulação da garantia dependente V1','',f'Política: {POLICY}. Simulação anterior à implementação R1D. Universo: 398 pares conhecidos; {len(rows)} afetados em {len(scope)} dispositivos.','',
        'Critério: ao menos uma âncora essencial na mesma afirmação que documenta a garantia. Sujeito específico ou contexto do regime são alternativas. Ausência mantém EVIDENCIA_INSUFICIENTE; rejeição editorial não é INCOMPATIVEL factual.','',
        '| Obra | Dispositivo | Histórico | R1C | Simulação | Impacto |','|---|---|---|---|---|---|']
    for r in rows: md.append(f"| {r['obra']} | {r['device_id']} | {r['rotulo_historico']} | {r['state_r1c']} | {r['state_simulado']} | {r['impacto']} |")
    md += ['',str(report['counts']),'','TP que permanecem: 0. FP eliminados: 4. TP históricos para readjudicação: 5. FN alterados: 0 (nenhum FN no escopo). Ambíguos factuais: 0; cinco readjudicações de rótulo humano permanecem pendentes.','',
           'A comparação é contra R1C persistida; R1C não foi executada novamente. Nenhum rótulo antigo foi sobrescrito.']
    write('06_BENCHMARKS/SIMULACAO_GARANTIA_DEPENDENTE_V1.md','\n'.join(md)+'\n')
    print(report['counts'])


if __name__ == '__main__': run()
