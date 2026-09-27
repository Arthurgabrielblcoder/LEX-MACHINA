"""Pre-label proof freeze for EVERY possible pair; emits only compact artifacts."""
import hashlib
import json
from collections import Counter
from canonical_input_r1 import load_canonical, ROOT
from proof_compiler_r1 import digest, file_hash, serialized
from proof_compiler_v2 import iter_exhaustive, VERSION


def freeze():
    inp=load_canonical(); states=Counter(); hasher=hashlib.sha256(); meaningful=[]; count=0
    for row in iter_exhaustive(inp):
        count+=1; states[row['state']]+=1
        hasher.update(serialized(row).encode('utf-8'))
        if row['proofs']: meaningful.append(row)
    stats=dict(logical_timestamp='V2-P07-R1-PROOFS-0011', compiler_version=VERSION,
        canonical_input_hash=inp.hash, proof_stream_sha256=hasher.hexdigest(), possible_pairs=count,
        states=dict(states), proven_pairs=len(meaningful),
        protocol='Revisão única após regressão conhecida; desenvolvimento não cego; baseline pré-rótulos preservada.',
        hashes=[dict(path='05_COMPILADOR/'+p,sha256=file_hash(ROOT/'05_COMPILADOR'/p))
                for p in ('proof_compiler_r1.py','proof_compiler_v2.py','canonical_input.py','canonical_input_r1.py','prepare_expansion.py')])
    return {'00_CHECKPOINTS/EXPANSION_R1_PROOFS_FREEZE.json':serialized(stats),
            '06_BENCHMARKS/PROVAS_EXPANSAO_R1.json':serialized(dict(input_hash=inp.hash,rows=meaningful))}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--artifact');args=p.parse_args();files=freeze()
    print(json.dumps({'files':{args.artifact:files[args.artifact]}} if args.artifact else {'summary':json.loads(files['00_CHECKPOINTS/EXPANSION_R1_PROOFS_FREEZE.json'])},ensure_ascii=False))
