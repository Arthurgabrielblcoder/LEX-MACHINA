"""RATIFICAÇÃO BATCH10 — formal human ratification record (user, chat, 2026-10-18). The Batch10 decision file stays byte-identical (it is
what was reviewed; pinned by sha256 here); this record is the only place that says HUMAN_APPROVED for Batch10. One editorial modification
by the user: ADI 4439 is ratified on TWO targets (CF art. 19, I + art. 210, § 1º). ADI 5081 keeps CF art. 17, § 1º (never § 6º) with explicit
temporal provenance. Normalized relations are counted against the frozen physical baseline J2I_FROZEN_315_198.
Writes J2_RATIFICATION_RECORD_10.json.   Usage: python build_j2_ratification_record_10.py [--check]
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_j2_batch as G  # noqa: E402

OUT = HERE / 'J2_RATIFICATION_RECORD_10.json'
RATIFICATION = dict(by='ARTHUR', on='2026-10-18', channel='chat',
                    statement='O usuário ratifica as 10 decisões do Batch10 com uma modificação editorial: a ADI 4439 é ratificada em dois targets '
                              '(CF art. 19, I e CF art. 210, § 1º), como vínculos legítimos e independentes do mesmo precedente.',
                    exceptions={'J0-BL-093': 'UNRESOLVED_EXTERNAL (Súmula 203/STJ; fonte oficial do STJ bloqueada por anti-robô; sem ficha, sem vínculo)',
                                'J0-BL-118': 'UNRESOLVED_IDENTIFICATION (art. 124; ADPF 289 com mérito pendente; não materializar)'})
# rid -> (ratified decision label, ratified targets, editorial note, temporal provenance or None)
RATIFIED = {
    'J0-BL-050': ('HUMAN_APPROVED_PROMOTE', ['CF88:ART.25:PAR.3'], None, None),
    'J0-BL-092': ('HUMAN_APPROVED_PROMOTE', ['CF88:ART.103-B:PAR.4'], None, None),
    'J0-BL-023': ('HUMAN_APPROVED_REALLOCATE', ['CF88:ART.17:PAR.1'], 'Não criar vínculo no § 6º.',
                  dict(temporal_version='MIXED', judgment_year=2015, wording_at_judgment='§ 1º na redação da EC 52/2006',
                       current_wording='§ 1º na redação da EC 97/2017',
                       note='Julgado em 2015, quando o § 1º tinha a redação da EC 52/2006. O vínculo é mantido pela pertinência material à autonomia e '
                            'à fidelidade partidária ("normas de disciplina e fidelidade partidária", cláusula presente nas duas redações). A decisão '
                            'não interpretou a redação de 2021 (§ 6º, EC 111/2021).',
                       policy='Exceção à regra J1.4/J2B.1 (redação histórica só no nível de artigo), ratificada expressamente pelo usuário para o § 1º.')),
    'J0-BL-027': ('HUMAN_APPROVED_MULTI_TARGET', ['CF88:ART.19:INC.I', 'CF88:ART.210:PAR.1'],
                  'Modificação editorial do usuário: dois vínculos legítimos do mesmo precedente, não aliases. Art. 19, I integra a fundamentação '
                  'constitucional explícita; art. 210, § 1º é interpretado diretamente na ementa e no mérito.', None),
    'J0-BL-131': ('HUMAN_APPROVED_REALLOCATE', ['CF88:ART.151:INC.III'], None, None),
    'J0-BL-125': ('HUMAN_APPROVED_ALREADY_COVERED', [], 'Tema 656 já instalado; nenhum vínculo novo.', None),
    'J0-BL-133': ('HUMAN_APPROVED_ALREADY_COVERED', [], 'Tema 796 já instalado; nenhum vínculo novo.', None),
    'J0-BL-091': ('HUMAN_APPROVED_REJECT_NOT_MATERIAL', [], 'Não materializar.', None),
    'J0-BL-093': ('UNRESOLVED_EXTERNAL', [], 'Não criar ficha nem vínculo.', None),
    'J0-BL-118': ('UNRESOLVED_IDENTIFICATION', [], 'Não materializar enquanto não houver precedente adequado identificado e julgado.', None),
}


def build():
    p = G.batch_file(10)
    raw = p.read_bytes().replace(b'\r\n', b'\n')
    doc10 = json.loads(raw)
    vis = G.j2i_baseline()
    installed_pairs = {(r[0], r[5]) for r in vis}
    installed_targets = {r[0] for r in vis}
    items = []
    for x in doc10['decisions']:
        rid = x['recommendation_id']
        if (x['status'], x['human_approved']) != ('AWAITING_USER_RATIFICATION', False):
            raise SystemExit(f'UNEXPECTED_PROPOSAL_STATE {rid}')
        label, targets, note, temporal = RATIFIED[rid]
        unresolved = x['decision'].startswith('UNRESOLVED')
        if unresolved != (rid in RATIFICATION['exceptions']) or (unresolved and label != x['decision']):
            raise SystemExit(f'EXCEPTION_MISMATCH {rid}')
        modified = sorted(targets) != sorted(x['recommended_targets'])
        if modified and rid != 'J0-BL-027':
            raise SystemExit(f'UNAUTHORIZED_TARGET_CHANGE {rid}')
        items.append(dict(recommendation_id=rid, batch='BATCH10', proposed_decision=x['decision'], ratified_decision=label,
                          proposed_targets=x['recommended_targets'], ratified_targets=targets, editorial_modification=modified,
                          precedents=[q['id'] for q in x['precedents']], creates_device_relations=bool(targets), note=note, temporal_provenance=temporal,
                          ratification_status=label if unresolved else 'HUMAN_APPROVED', human_approved=not unresolved))
    rel = sorted({(t, i['precedents'][0]) for i in items if i['human_approved'] for t in i['ratified_targets']})
    new_rel = [r for r in rel if r not in installed_pairs]
    new_targets = sorted({t for t, _ in new_rel} - installed_targets)
    c = collections.Counter(i['ratified_decision'] for i in items)
    doc = dict(schema_version=1, round='J2', kind='HUMAN_RATIFICATION', batch='BATCH10', ratification=RATIFICATION,
               decision_files_sha256_lf={p.relative_to(HERE).as_posix(): hashlib.sha256(raw).hexdigest()},
               physical_baseline='J2I_FROZEN_315_198', materialized=False, deployed=False,
               BATCH10_RATIFIED_RECOMMENDATIONS=sum(1 for i in items if i['human_approved']),
               BATCH10_NEW_RELATIONS=len(new_rel), BATCH10_NEW_TARGETS=len(new_targets),
               BATCH10_ALREADY_COVERED=c['HUMAN_APPROVED_ALREADY_COVERED'], BATCH10_REJECTED=c['HUMAN_APPROVED_REJECT_NOT_MATERIAL'],
               BATCH10_UNRESOLVED=sum(1 for i in items if not i['human_approved']),
               normalized_relations=[dict(target_id=t, source_id=s) for t, s in new_rel], new_targets=new_targets,
               ratified_by_decision=dict(sorted(c.items())), items=items)
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = build()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    d = json.loads(b)
    print({k: v for k, v in d.items() if k.startswith('BATCH10_')}, d['normalized_relations'])
