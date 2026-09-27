"""Versioned phase-7 ontology revision, shared by all final runners/tests."""
from canonical_input import load_canonical as load_base, ROOT
from proof_compiler_r1 import load, file_hash, require, CanonicalInput


def load_canonical():
    desc=load(ROOT/'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2_R1.json')
    base=load_base()
    require(base.hash==desc['base_input_hash'],'base input hash changed')
    require(file_hash(ROOT/desc['overlay'])==desc['overlay_sha256'],'revision overlay hash changed')
    overlay=load(ROOT/desc['overlay'])
    data=base.data
    data['ontology']['equivalences'].update(overlay['equivalences'])
    data['ontology']['version']='CONCEPTS_V2_EXPANSION_1_R1'
    data['ontology']['equivalence_provenance']=dict(path=desc['overlay'],sha256=desc['overlay_sha256'])
    data['scope']+='__ONTOLOGY_R1'
    return CanonicalInput(data)
