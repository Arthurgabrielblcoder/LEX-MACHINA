"""J1.4 — overlays of the 4 J1.3 decisions ratified by the user (2026-10-16): exclusion of the 4 links attached to the wrong target and
relocation to the target the official sources indicate. Deterministic.

Writes:
  LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS_J1_4.json   4 records MATERIAL_MISMATCH_EXCLUDED (same schema as CF88_LINK_EXCLUSIONS*.json)
  LEGAL_TARGET_ID/derived/CF88_JURIS_RELOCATIONS_J1_4.json 3 relocated links (same precedent and same link key, new target, temporal note)
The link key (source_reference_id) is kept so the device keeps opening the same thesis in the legacy JURISPRUDENCIA.IDX.
Temas 367/387: KEEP_BOTH (untouched). Backlog of 148 untouched.   Usage: python apply_j1_4_overlays.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEC = HERE / 'J1_3_DECISIONS.json'
OUT_X = ROOT / 'LEGAL_TARGET_ID/derived/CF88_LINK_EXCLUSIONS_J1_4.json'
OUT_R = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_RELOCATIONS_J1_4.json'
RATIFICATION = dict(by='ARTHUR', on='2026-10-16', statement='J1_3_EXTERNAL_DECISIONS_APPROVED = 4/4; TEMAS_367_387 = KEEP_BOTH',
                    directives='SV 17 e Tema 147: retirar do art. 100, § 1º e materializar no § 5º, com proveniência da redação histórica. Tema 594: não '
                               'vincular aos §§ 4º/5º atuais; associar ao art. 40 com nota temporal expressa (redação originária dos §§ 4º e 5º).')
RELOCATIONS = [  # (precedent, source_reference_id, from reference_ids, new target, temporal note)
    ('STF:SV:17', 'STF:SV:17:CF88:100:-:-:-', ['JURISPRUDENCE:STF:SV:17:CF88:100:-:-:-@CF88:ART.100:PAR.1'], 'CF88:ART.100:PAR.5',
     'A SV 17 cita o "período previsto no § 1º do art. 100" na redação anterior à EC 62/2009; esse período está hoje no § 5º (STF, Tema 1037).'),
    ('STF:RG:147', 'STF:RG:147:CF88:100:-:-:-', ['JURISPRUDENCE:STF:RG:147:CF88:100:-:-:-@CF88:ART.100:PAR.1'], 'CF88:ART.100:PAR.5',
     'O Tema 147 trata do § 1º do art. 100 na redação original e na da EC 30/2000; o dispositivo foi transferido para o § 5º pela EC 62/2009 (STF, Tema 1037).'),
    ('STF:RG:594', 'STF:RG:594:CF88:40:-:-:-', ['JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40:PAR.4',
                                                'JURISPRUDENCE:STF:RG:594:CF88:40:-:-:-@CF88:ART.40:PAR.5'], 'CF88:ART.40',
     'O Tema 594 trata dos §§ 4º e 5º do art. 40 na redação originária (anterior à EC 20/1998): paridade de proventos e pensão integral. Os §§ 4º e 5º '
     'atuais têm outro conteúdo; por isso o vínculo é com o art. 40.'),
]


def sha_lf(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def build():
    d = json.loads(DEC.read_text(encoding='utf-8'))
    dec = {x['relation_id']: x for x in d['decisions']}
    if len(dec) != 4 or any(x['decision'] != 'REALLOCATE_RECOMMENDED' for x in dec.values()) or d['redundant']['decision'] != 'KEEP_BOTH':
        raise SystemExit('J1_3_DECISIONS_UNEXPECTED')
    covered = sorted(r for _, _, frm, _, _ in RELOCATIONS for r in frm)
    if covered != sorted(dec):
        raise SystemExit('RELOCATIONS_DO_NOT_COVER_DECISIONS')
    src = d['sources']
    excl = []
    for i, rid in enumerate(sorted(dec), 1):
        x = dec[rid]
        excl.append(dict(
            reference_id=rid, target_id=x['target_id'], source_id=x['precedent'], source_reference_id=rid.split(':', 1)[1].rsplit('@', 1)[0],
            status='MATERIAL_MISMATCH_EXCLUDED', verified_subject=x['basis'], expected_subject=f"{x['target_id']} (conteúdo atual do dispositivo)",
            reason=f"ALVO_HISTORICO_INCORRETO: {x['doubt']}",
            evidence=dict(official_source=src[x['main_source']]['title'], official_source_url=src[x['main_source']]['url'],
                          sources=[dict(id=s, url=src[s]['url'], sha256=src[s].get('dom_text_sha256') or src[s].get('snapshot_sha256')) for s in x['sources']],
                          verified_on='2026-10-16', verified_by='revisão em fontes oficiais (J1.3) ratificada por Arthur em 2026-10-16'),
            relocated_to=x['potential_destination'].split(' ')[0], decided_in=f'J1_3 (J1.3-EXT-{i:02d}), ratificado em J1.4'))
    reloc = []
    for prec, key, frm, target, note in RELOCATIONS:
        reloc.append(dict(relocation_id=f'J1.4-RELOC:{key}@{target}', reference_id=f'JURISPRUDENCE:{key}@{target}', target_id=target, source_id=prec,
                          source_reference_id=key, relocated_from=frm, temporal_note=note, review_status='HUMAN_APPROVED_RELOCATION',
                          decision_refs=[f"{dec[r]['relation_id']}" for r in frm], main_source=dec[frm[0]]['main_source'],
                          sources=[dict(id=s, url=src[s]['url'], sha256=src[s].get('dom_text_sha256') or src[s].get('snapshot_sha256')) for s in dec[frm[0]]['sources']]))
    base = dict(schema_version=1, norma_id='CF88', round='J1.4', ratification=RATIFICATION, decisions_file=DEC.relative_to(ROOT).as_posix(),
                decisions_sha256=sha_lf(DEC))
    x_doc = dict(base, policy='Overlay de exclusão J1.4: vínculos de jurisprudência associados a dispositivo cuja redação atual não corresponde ao que o '
                              'precedente interpreta (redação histórica). Mesmo mecanismo de CF88_LINK_EXCLUSIONS*.json. Fail closed.',
                 total=len(excl), records=excl)
    r_doc = dict(base, policy='Overlay de realocação J1.4: o mesmo precedente e a mesma chave de vínculo, no dispositivo atual indicado pelas fontes oficiais, '
                              'com nota temporal expressa. Aplicado pelo build RUN7 depois das exclusões J1.4. Fail closed.',
                 total=len(reloc), records=reloc)
    return [(p, (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')) for p, doc in ((OUT_X, x_doc), (OUT_R, r_doc))]


if __name__ == '__main__':
    outs = build()
    if '--check' in sys.argv:
        ok = all(p.is_file() and p.read_bytes() == b for p, b in outs)
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    for p, b in outs:
        p.write_bytes(b)
        print(p.name, hashlib.sha256(b).hexdigest(), json.loads(b)['total'])
