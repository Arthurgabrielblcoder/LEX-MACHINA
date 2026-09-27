"""Versioned data loader. Same immutable interpreter and contracts as R1B."""
from canonical_input_r1b import load_canonical as load_r1b, ROOT
from prepare_r1c_data import assemble, invariants
from proof_compiler_r1 import load, require, file_hash

def load_canonical():
    desc=load(ROOT/'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1C.json')
    base=load_r1b()
    require(base.hash==desc['base_input_hash'],'R1B changed')
    require(file_hash(ROOT/desc['overlay'])==desc['overlay_sha256'],'R1C overlay changed')
    inp=assemble(base,load(ROOT/desc['overlay']))
    invariants(base,inp)
    require(inp.hash==desc['canonical_input_hash'],'R1C input changed')
    return inp
