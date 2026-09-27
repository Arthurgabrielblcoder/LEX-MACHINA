"""R1D data-only helpers. The proof interpreter and ranking remain frozen."""
import copy
import datetime
from pathlib import Path
from proof_compiler_r1 import load, serialized, file_hash, require, CanonicalInput

ROOT = Path(__file__).resolve().parents[1]
POLICY = 'POLITICA_EDITORIAL_REFERENCIAS_V2_V1'
DATE = '2026-09-26'
HOLDOUT_HASH = 'b71a87a8292ac621a209201e2082935813563f8002f9203430af3b781414adf1'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write(path, value):
    p = ROOT / path
    require(not p.exists(), 'Refusing to overwrite: ' + path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else serialized(value), encoding='utf-8')


def key(row):
    return row['device_id'], row['work_id']


def metric(label, state):
    if label == 'APROVAR':
        return 'TP' if state == 'ADMISSIVEL' else 'FN'
    if label == 'REJEITAR':
        return 'FP' if state == 'ADMISSIVEL' else 'TN'
    return 'NAO_AVALIAVEL'


def integrity():
    before = load(ROOT / '00_CHECKPOINTS/R1D_INTEGRITY_BEFORE.json')
    changed = [r['path'] for r in before['files'] if not (ROOT/r['path']).exists() or file_hash(ROOT/r['path']) != r['sha256']]
    protected = load(ROOT/'00_CHECKPOINTS/INTEGRITY_BEFORE.json')['files']
    external_changed = [r['path'] for r in protected if file_hash(ROOT.parent/r['path']) != r['sha256']]
    holdout = file_hash(ROOT/'06_BENCHMARKS/HOLDOUT_V2_BLIND.json')
    return dict(checked_at=now(), preexisting_v2_checked=len(before['files']), preexisting_v2_changed=changed,
                protected_checked=len(protected), protected_changed=external_changed,
                holdout_sha256=holdout, holdout_content_opened=False,
                passed=not changed and not external_changed and holdout == HOLDOUT_HASH)


def contract(relation, obj, predicates, objects, subjects=(), role='ACTOR', context=(), reason=''):
    return dict(relation=relation, object_reached=obj,
                requires=dict(predicates=list(predicates), objects_all=list(objects), subjects_any=list(subjects),
                              participant_role=role, context_all=list(context)),
                editorial_review=False, scope_policy=reason,
                forbidden_inferences=['ancestral_como_especie', 'tema_como_prova', 'contexto_como_competencia'],
                policy=POLICY)


def dependent_contracts(device, nucleus):
    """OR alternatives encoded in existing contracts; no new matching operation.

    At least one essential contextual anchor must occur in the SAME assertion.
    Subject anchors replace the former generic accused with the narrower subject.
    No unrelated claim in a dossier can supply an anchor.
    """
    family = device['family']
    require(nucleus['role'] == 'GARANTIA_TRANSVERSAL', 'Wrong scope')
    if family == 'GARANTIA_EM_REGIME_FUNCIONAL':
        if device['device_id'].startswith(('CF88:ART.41:', 'CF88:ART.247:')):
            subject = 'SERVIDOR_PUBLICO'
            contexts = ['CARGO_PUBLICO']
        else:
            subject = 'JUIZ'
            contexts = ['CARGO_PUBLICO']
    elif family == 'COMPETENCIA_LEGISLATIVA':
        subject = 'LEGISLADOR'
        contexts = ['UNIAO_ESTADOS_DF']
    else:
        raise ValueError('Unadjudicated transversal family: ' + family)
    out = []
    for old in nucleus['contracts_by_relation']:
        for mode in ['subject'] + contexts:
            c = copy.deepcopy(old)
            c['policy'] = POLICY
            c['anchor_policy'] = 'GARANTIA_DEPENDENTE_EXIGE_ANCORA'
            c['scope_policy'] = 'Regra D: uma âncora essencial do contexto hospedeiro na mesma afirmação. Não prova o regime inteiro.'
            if mode == 'subject':
                c['requires']['subjects_any'] = [subject]
                c['requires']['participant_role'] = 'ACTOR' if family == 'COMPETENCIA_LEGISLATIVA' else 'AFFECTED'
            else:
                c['requires']['context_all'] = sorted(set(c['requires']['context_all'] + [mode]))
            out.append(c)
    return out


def apply_overlay(base, overlay):
    data = copy.deepcopy(base.data)
    ds = {d['device_id']: d for d in data['devices']}
    ws = {w['work_id']: w for w in data['works']}
    for d in overlay['devices']:
        ds[d['device_id']].update(copy.deepcopy(d))
    for e in overlay['evidence_replacements']:
        es = ws[e['work_id']]['evidences']
        idx = next(i for i, old in enumerate(es) if old['evidence_id'] == e['evidence_id'])
        es[idx] = copy.deepcopy(e)
    for e in overlay['evidence_additions']:
        ws[e['work_id']]['evidences'].append(copy.deepcopy(e))
    return CanonicalInput(data)
