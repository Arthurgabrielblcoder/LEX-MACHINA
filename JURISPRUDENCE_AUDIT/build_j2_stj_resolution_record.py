"""RESOLUÇÃO STJ — editorial closure of Súmulas 203 and 403/STJ (user, chat, 2026-10-18). History is preserved (blocked -> official source
found -> resolved); the Batch08 and Batch10 decision files stay byte-identical. CF links are HUMAN_APPROVED; the two CC links of Súmula 403
are forwarded to CC-J1 (normal review, not approved here). Nothing is materialized; ficha texts are drafts for a future package.
Writes J2_STJ_RESOLUTION_RECORD.json.   Usage: python build_j2_stj_resolution_record.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_j2_batch as G  # noqa: E402

OUT = HERE / 'J2_STJ_RESOLUTION_RECORD.json'
RESOLUTIONS = HERE / 'STJ_OFFICIAL_SOURCE_RESOLUTIONS.json'
RATIFICATION = dict(by='ARTHUR', on='2026-10-18', channel='chat',
                    statement='Súmula 203/STJ ratificada em CF art. 105, III (redação vigente; histórico da alteração de 2002 preservado na ficha). '
                              'Súmula 403/STJ ratificada em CF art. 5º, V e CF art. 5º, X (dois vínculos, não duplicatas). Os vínculos da '
                              'Súmula 403 a CC arts. 186 e 927 seguem para revisão normal no CC-J1.')
LINKS = {
    'STJ:SUMULA:203': dict(recommendation_id='J0-BL-093', batch='BATCH10', cf=['CF88:ART.105:INC.III'], cc=[]),
    'STJ:SUMULA:403': dict(recommendation_id='J0-BL-001', batch='BATCH08', cf=['CF88:ART.5:INC.V', 'CF88:ART.5:INC.X'],
                           cc=['CC2002:ART.186', 'CC2002:ART.927']),
}
HISTORY = {
    'STJ:SUMULA:403': [dict(on='2026-10-17', state='UNRESOLVED_EXTERNAL', why='scon.stj.jus.br: desafio anti-robô (Batch08, fonte Y3); não contornado'),
                       dict(on='2026-10-18', state='OFFICIAL_SOURCE_RESOLVED', why='PDF oficial "Súmulas do STJ" publicado na página oficial'),
                       dict(on='2026-10-18', state='HUMAN_APPROVED (CF 5º V e X)', why='ratificação editorial do usuário')],
    'STJ:SUMULA:203': [dict(on='2026-10-18', state='UNRESOLVED_EXTERNAL', why='scon.stj.jus.br: desafio anti-robô (Batch10, fonte K12); não contornado'),
                       dict(on='2026-10-18', state='OFFICIAL_SOURCE_RESOLVED', why='PDF oficial "Súmulas do STJ" publicado na página oficial'),
                       dict(on='2026-10-18', state='HUMAN_APPROVED (CF 105, III)', why='ratificação editorial do usuário')],
}


def ficha(pid, it, src):
    n = it['numero']
    lines = [f'SÚMULA {n} DO STJ', 'TRIBUNAL: STJ', f'STATUS: {"vigente (enunciado alterado)" if it["status_sumula"] == "ALTERADA" else "vigente"}',
             f'ÓRGÃO JULGADOR: {it["orgao_julgador"]}', '', 'ENUNCIADO']
    enun = it['enunciado']
    if it['status_sumula'] == 'ALTERADA':
        cur, _, hist = enun.partition(' A Corte Especial,')
        lines += [cur.strip(), '', 'HISTÓRICO DO ENUNCIADO', ('A Corte Especial,' + hist).strip()]
    else:
        lines += [enun]
    lines += ['', 'JULGAMENTO', f'{it["data_decisao"]}; {it["publicacao"]}.', '', 'FONTE OFICIAL', src['url'], f'(PDF oficial, sha256 {src["pdf_sha256"][:16]}…)']
    return '\n'.join(lines) + '\n'


def build():
    res = json.loads(RESOLUTIONS.read_text(encoding='utf-8'))
    vis = G.j2i_baseline()
    installed_pairs, installed_targets = {(r[0], r[5]) for r in vis}, {r[0] for r in vis}
    items, rels = [], []
    for pid, l in LINKS.items():
        it = res['items'][pid]
        if it['source_status'] != 'OFFICIAL_SOURCE_RESOLVED':
            raise SystemExit(f'SOURCE_NOT_RESOLVED {pid}')
        refs = {t for r in it['referencias_legislativas'] for t in r['targets']}
        if not set(l['cf'] + l['cc']) <= refs:
            raise SystemExit(f'TARGET_NOT_IN_OFFICIAL_REFERENCES {pid}')
        rels += [(t, pid) for t in l['cf']]
        items.append(dict(precedent=pid, recommendation_id=l['recommendation_id'], batch=l['batch'], source_status='OFFICIAL_SOURCE_RESOLVED',
                          history=HISTORY[pid], ratified_cf_targets=l['cf'], ratification_status='HUMAN_APPROVED',
                          cc_targets_forwarded_to_cc_j1=l['cc'], cc_status='FORWARDED_TO_CC_J1 (AWAITING_USER_RATIFICATION)',
                          device_label=f'Súmula {it["numero"]} STJ', ficha_file=pid.replace(':', '_') + '.TXT',
                          ficha_draft=ficha(pid, it, res['source']), official_source=dict(url=res['source']['url'], pdf_sha256=res['source']['pdf_sha256'])))
    new_rel = [r for r in rels if r not in installed_pairs]
    doc = dict(schema_version=1, round='J2', kind='STJ_EDITORIAL_RESOLUTION', ratification=RATIFICATION,
               source_resolutions_file=RESOLUTIONS.name, source_resolutions_sha256_lf=G.B.sha_lf(RESOLUTIONS),
               decision_files_unchanged={p.relative_to(HERE).as_posix(): G.B.sha_lf(p) for p in (G.batch_file(8), G.batch_file(10))},
               materialized=False, deployed=False, NEW_CF_RELATIONS=len(new_rel),
               NEW_CF_TARGETS=len({t for t, _ in new_rel} - installed_targets),
               normalized_relations=[dict(target_id=t, source_id=s) for t, s in new_rel], items=items)
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = build()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    d = json.loads(b)
    print(d['NEW_CF_RELATIONS'], d['NEW_CF_TARGETS'], d['normalized_relations'])
    print(d['items'][0]['ficha_draft'])
