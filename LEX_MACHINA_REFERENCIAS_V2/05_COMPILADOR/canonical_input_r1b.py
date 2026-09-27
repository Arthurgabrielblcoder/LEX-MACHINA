"""Factual overlay only. Every current runner/test loads this exact input."""
from canonical_input_r1 import load_canonical as load_r1, ROOT
from proof_compiler_r1 import CanonicalInput, load, require, file_hash


def load_canonical():
    desc=load(ROOT/'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1B.json')
    base=load_r1()
    require(base.hash==desc['base_input_hash'],'R1 input changed')
    require(file_hash(ROOT/desc['overlay'])==desc['overlay_sha256'],'R1B overlay changed')
    overlay=load(ROOT/desc['overlay']); data=base.data
    by_device={d['device_id']:d for d in data['devices']}
    by_work={w['work_id']:w for w in data['works']}
    for d in overlay['devices']:
        old=by_device[d['device_id']]
        require(d['text']==old['text'] and d['source_hash']==old['source_hash'],'source altered')
        by_device[d['device_id']]=d
    for w in overlay['works']:
        require(w['work_id'] in by_work,'new work not allowed')
        by_work[w['work_id']]=w
    data['devices']=[by_device[k] for k in sorted(by_device)]
    data['works']=[by_work[k] for k in sorted(by_work)]
    data['scope']+='__FACTUAL_R1B'
    return CanonicalInput(data)
