"""Only assembly path for unit tests, regression, samples and full execution."""
from pathlib import Path
from proof_compiler_r1 import CanonicalInput, load, file_hash, require
from prepare_expansion import device_shell

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def load_canonical():
    manifest = load(ROOT/'01_SCHEMA/CANONICAL_EVALUATION_INPUT_V2.json')
    parts = {}
    for item in manifest['parts']:
        p = ROOT/item['path']
        require(file_hash(p)==item['sha256'], 'canonical part hash mismatch: '+item['path'])
        parts[item['path']] = load(p)
    source = manifest['constitutional_source']
    require(file_hash(REPO/source['path'])==source['sha256'], 'constitutional snapshot changed')
    cf = load(REPO/source['path'])['dispositivos']
    cf_by_id = {d['chave_dispositivo']:d for d in cf}
    devices = {}; works = []
    for path, data in parts.items():
        if path.startswith('02_DISPOSITIVOS/'):
            for d in data['devices']:
                require(d['device_id'] not in devices, 'duplicate across parts')
                require(d['text']==cf_by_id[d['device_id']]['texto'], 'source text changed')
                require(d['source_hash']==source['sha256'], 'device source identity')
                devices[d['device_id']] = d
        elif path.startswith('03_OBRAS/'): works.extend(data['works'])
    require(len(devices)==manifest['priority_count'], 'priority count')
    require(len(works)==manifest['work_count'], 'work count')
    for did, row in cf_by_id.items():
        if did not in devices:
            d = device_shell(row, cf_by_id, source['sha256'])
            d['annotation_status'] = 'NAO_REPRESENTADO_FORA_PRIORIDADE'
            devices[did] = d
    data = dict(schema_version=manifest['schema_version'], scope=manifest['scope'],
                source_policy=manifest['source_policy'], devices=[devices[k] for k in sorted(devices)],
                works=sorted(works,key=lambda w:w['work_id']), ontology=parts['04_CONCEITOS/CONCEITOS_V2.json'])
    return CanonicalInput(data)
