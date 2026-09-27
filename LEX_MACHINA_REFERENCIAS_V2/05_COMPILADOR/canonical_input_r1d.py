"""Load the frozen R1D data overlay through the unchanged canonical contract."""
from canonical_input_r1c import load_canonical as load_base
from proof_compiler_r1 import load, file_hash, require
from r1d_support import ROOT, apply_overlay


def load_canonical():
    desc=load(ROOT/'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1D.json')
    base=load_base()
    require(base.hash==desc['base_input_hash'], 'R1C input changed')
    require(file_hash(ROOT/desc['overlay'])==desc['overlay_sha256'], 'R1D overlay changed')
    inp=apply_overlay(base,load(ROOT/desc['overlay']))
    require(inp.hash==desc['canonical_input_hash'], 'R1D input changed')
    return inp
