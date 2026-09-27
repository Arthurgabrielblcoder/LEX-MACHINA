"""R1D1: one versioned art.205 contract relocation; frozen matcher/ranker."""
import copy
from canonical_input_r1d import load_canonical as load_base
from proof_compiler_r1 import CanonicalInput, load, file_hash, digest, require
from r1d_support import ROOT


def assemble(base, patch):
    require(patch['base_input_hash']==base.hash,'R1D base changed')
    require(patch['device_id']=='CF88:ART.205','Patch outside authorized article')
    data=copy.deepcopy(base.data)
    device=next(d for d in data['devices'] if d['device_id']==patch['device_id'])
    require(digest(device)==patch['before_sha256'],'Article before mismatch')
    device.update(copy.deepcopy(patch['after']))
    require(digest(device)==patch['after_sha256'],'Article after mismatch')
    inp=CanonicalInput(data)
    require(inp.data['works']==base.data['works'],'Work evidence changed')
    require(inp.data['ontology']==base.data['ontology'],'Ontology changed')
    require([d for d in inp.data['devices'] if d['device_id']!='CF88:ART.205']==[d for d in base.data['devices'] if d['device_id']!='CF88:ART.205'],'Other article changed')
    return inp


def load_canonical():
    desc=load(ROOT/'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1D1.json')
    require(file_hash(ROOT/desc['patch'])==desc['patch_sha256'],'Patch changed')
    inp=assemble(load_base(),load(ROOT/desc['patch']))
    require(inp.hash==desc['canonical_input_hash'],'R1D1 input changed')
    return inp
