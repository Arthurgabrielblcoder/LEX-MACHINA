"""Freeze real R1B proofs for known-pair identities only; no new full run."""
import json
from canonical_input_r1b import load_canonical, ROOT
from proof_compiler_r1 import load, digest, file_hash
from proof_compiler_v2 import run_pairs


def freeze():
    inp=load_canonical()
    # Only IDs select the development scope. Human outcomes never reach proof evaluation.
    ledger=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json')
    pairs=[dict(device_id=p['device_id'],work_id=p['work_id']) for p in ledger['pairs']]
    rows=run_pairs(inp,pairs)
    proofs=dict(input_hash=inp.hash,scope='398_DEVELOPMENT_PAIRS_ONLY',rows=rows)
    paths=['01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1B.json','01_SCHEMA/COMPLETUDE_FACTUAL_R1B.json',
           '05_COMPILADOR/proof_compiler_r1.py','05_COMPILADOR/proof_compiler_v2.py',
           '05_COMPILADOR/canonical_input_r1b.py','05_COMPILADOR/canonical_input_r1.py',
           '05_COMPILADOR/canonical_input.py','06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json',
           '06_BENCHMARKS/HOLDOUT_V2_BLIND.json']
    freeze=dict(status='EXPANSION_R1B_PROOFS_FROZEN',canonical_input_hash=inp.hash,
                proof_content_hash=digest(proofs),scope=proofs['scope'],pairs=len(rows),
                factual_pass=1,architectural_revision=1,
                hashes=[dict(path=p,sha256=file_hash(ROOT/p)) for p in paths],
                note='Freeze pré-métricas do passe factual; não é cego nem execução final. Gate pendente. Provas R1 e dados originais intactos.')
    return dict(proofs=proofs,freeze=freeze)


if __name__=='__main__':
    print(json.dumps(freeze(),ensure_ascii=False,separators=(',',':')))
