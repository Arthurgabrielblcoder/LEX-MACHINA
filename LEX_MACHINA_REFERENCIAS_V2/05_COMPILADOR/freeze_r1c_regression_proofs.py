"""One proof pass over development identities, after the representation freeze."""
import json
from canonical_input_r1c import load_canonical, ROOT
from proof_compiler_r1 import load, digest, file_hash, require
from proof_compiler_v2 import run_pairs

def freeze():
    require(not (ROOT/'06_BENCHMARKS/PROVAS_EXPANSAO_R1C.json').exists(),'R1C proofs already persisted; do not repeat')
    before=load(ROOT/'00_CHECKPOINTS/R1C_REPRESENTATIONS_FROZEN.json')
    for item in before['hashes']:
        require(file_hash(ROOT/item['path'])==item['sha256'],'representation freeze changed')
    inp=load_canonical()
    require(inp.hash==before['canonical_input_hash'],'input not frozen')
    ledger=load(ROOT/'06_BENCHMARKS/HUMAN_LABELS_MASTER_V2.json')
    pairs=[dict(device_id=p['device_id'],work_id=p['work_id']) for p in ledger['pairs']]
    rows=run_pairs(inp,pairs)
    proofs=dict(input_hash=inp.hash,scope='398_DEVELOPMENT_PAIRS_ONLY',rows=rows)
    record=dict(status='R1C_PROOFS_FROZEN',canonical_input_hash=inp.hash,proof_content_hash=digest(proofs),scope=proofs['scope'],pairs=len(rows),hashes=before['hashes'],representations_manifest_sha256=file_hash(ROOT/'00_CHECKPOINTS/R1C_REPRESENTATIONS_FROZEN.json'),note='Uma passagem real. Rótulos não chegam ao compilador. Não é holdout cego nem execução completa.')
    return dict(proofs=proofs,freeze=record)

if __name__=='__main__':print(json.dumps(freeze(),ensure_ascii=False,separators=(',',':')))
