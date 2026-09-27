"""Full 69 x 3461 Cartesian pass through the same frozen canonical interpreter."""
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'05_COMPILADOR'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'06_BENCHMARKS'))
from canonical_input_r1d import load_canonical
from proof_compiler_r1 import load, require, file_hash, digest
from proof_compiler_v2 import iter_exhaustive, rank_select
from r1d_support import ROOT, now, write, key, integrity
from run_regression_r1d import verify_freeze


def run():
    freeze=verify_freeze();gate=load(ROOT/'00_CHECKPOINTS/R1D_GATE_DECISION.json')
    inp=load_canonical()
    require(gate['passed'] and gate['input_hash']==inp.hash==freeze['input_hash'],'Full execution not authorized')
    require(integrity()['passed'],'Integrity failed')
    reg=load(ROOT/'06_BENCHMARKS/REGRESSAO_COMPLETA_EXPANSION_R1D.json')
    known={key(r):r for r in reg['cases']}
    write('00_CHECKPOINTS/R1D_FULL_STARTED.json',dict(at=now(),input_hash=inp.hash,works=69,devices=3461,expected_pairs=69*3461))
    counts=Counter();admitted=[];review=[];parity=[];count=0;retrieved=0;pair_hash=hashlib.sha256()
    output=ROOT/'07_EXECUCAO_COMPLETA/RESULTADO_COMPLETO_R1D.jsonl.gz'
    require(not output.exists(),'Output exists')
    with output.open('xb') as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as out:
            for row in iter_exhaustive(inp):
                count+=1;retrieved+=int(row['retrieved']);counts[row['state']]+=1
                pair_hash.update((row['device_id']+'\t'+row['work_id']+'\n').encode())
                out.write((json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8'))
                if row['state']=='ADMISSIVEL':admitted.append(row)
                elif row['state']=='REVISAO_EDITORIAL':review.append(row)
                if key(row) in known:
                    k=known[key(row)]
                    parity.append(dict(device_id=row['device_id'],work_id=row['work_id'],
                        equal=row['state']==k['admissibility'] and digest(row['proofs'])==k['proof_digest']))
                if count%50000==0:print('Processed',count,flush=True)
    require(count==69*3461 and retrieved==count,'Cartesian coverage failed')
    require(len(parity)==398 and all(r['equal'] for r in parity),'Known-pair full/regression parity failed')
    # Full-file scan validates actual stored integrity/coverage without re-evaluation.
    stored=Counter();seen=set()
    with gzip.open(output,'rt',encoding='utf-8') as src:
        for line in src:
            row=json.loads(line);k=key(row)
            require(k not in seen,'Duplicate full pair');seen.add(k);stored[row['state']]+=1
    require(len(seen)==count and stored==counts,'Stored full result mismatch')
    hist=load(ROOT.parent/'LEX_MACHINA_REFERENCIAS_TESTE_COMPLETO_ALPHA3_V1/RESULTADO_COMPLETO_ALPHA3.json')['candidatos']
    scores={(r['dispositivo_id'],r['obra_id']):r['score_alpha3'] for r in hist}
    ranked=rank_select(inp,admitted,scores)
    selected=[r for r in ranked if r['selected']]
    unscored=[r for r in ranked if r['editorial_score'] is None]
    summary=dict(schema='EXECUCAO_COMPLETA_R1D',at=now(),input_hash=inp.hash,pairs=count,candidates=retrieved,
        candidate_definition='Recuperação exaustiva de todos os pares, não somente os 589 históricos; admissibilidade decidida pelo mesmo interpretador.',
        works=69,devices=3461,states=dict(counts),admissible=len(admitted),review=len(review),
        insufficient=counts['EVIDENCIA_INSUFICIENTE'],incompatible=counts['INCOMPATIVEL'],source_under_review=counts['FONTE_EM_REVISAO'],
        historical_score_pairs=len(scores),admissible_without_historical_score=len(unscored),selected=len(selected),
        new_scores=0,new_thresholds=0,known_pair_parity=dict(total=len(parity),equal=sum(r['equal'] for r in parity)),
        pair_order_sha256=pair_hash.hexdigest(),output_sha256=file_hash(output),output_bytes=output.stat().st_size,
        represented_devices=sum(bool(d['nuclei']) for d in inp.devices.values()),
        caveats=['Execução exaustiva não significa representação completa dos 3461 dispositivos.',
                 'Sem novo score: admissíveis sem score histórico ficam fora da seleção ranqueada existente.',
                 'Não mede precisão global sem novos rótulos independentes; holdout permanece fechado.'])
    write('07_EXECUCAO_COMPLETA/RESUMO_EXECUCAO_COMPLETA_R1D.json',summary)
    write('07_EXECUCAO_COMPLETA/ADMISSIVEIS_R1D.json',dict(input_hash=inp.hash,rows=ranked))
    write('07_EXECUCAO_COMPLETA/REVISAO_EDITORIAL_R1D.json',dict(input_hash=inp.hash,rows=review))
    write('07_EXECUCAO_COMPLETA/SELECAO_R1D.json',dict(input_hash=inp.hash,rows=selected,unscored_count=len(unscored),policy='Ranking congelado: score histórico >= 6, até 3 por dispositivo, diversidade de mídia como desempate.'))
    write('00_CHECKPOINTS/R1D_FULL_PARITY.json',dict(input_hash=inp.hash,total=398,equal=398,cases=parity))
    write('00_CHECKPOINTS/R1D_FULL_COMPLETE.json',summary)
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':run()
