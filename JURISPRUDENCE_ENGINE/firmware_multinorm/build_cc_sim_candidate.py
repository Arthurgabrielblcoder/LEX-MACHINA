"""SPRINT DE ESCALA — Parte H: minimal HOST-ONLY Código Civil jurisprudence candidate for the multinorm firmware SIMULATION.
Relations = pilot candidates with an official source, a linking assessment and no pending human judgment (PORTABILITY_PILOT_ONLY): they are
NOT human-approved and are NEVER deployed (status SIMULATION_ONLY). The J2I CF bytes are kept as an exact prefix (like J2H), CC rows appended.
Writes pilot_cc/SIM_CANDIDATE_CC/.   Usage: python build_cc_sim_candidate.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / 'LEGAL_TARGET_ID'), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import target_id as T  # noqa: E402
import juris_types as JT  # noqa: E402

PILOT = ROOT / 'JURISPRUDENCE_ENGINE/pilot_cc/PORTABILITY_PILOT_CC.json'
J2I_SD = ROOT / 'JURISPRUDENCE_AUDIT/J2H_CANDIDATE_B_OVER_A/candidate/SD/99_JURISPRUDENCIA_V2'
CARD = ROOT / 'JURISPRUDENCE_AUDIT/J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
OUT = ROOT / 'JURISPRUDENCE_ENGINE/pilot_cc/SIM_CANDIDATE_CC'
LINKING = ('PROMOTE_RECOMMENDED', 'REALLOCATE_RECOMMENDED')
STATUS = {'adi': 'merito_julgado', 'repercussao_geral': 'tese_fixada'}
TIPO = {'ADI': 'adi', 'RG': 'repercussao_geral'}


def selected():
    d = json.loads(PILOT.read_text(encoding='utf-8'))
    out = []
    for c in d['candidates']:
        if c['pilot_assessment'] in LINKING and not c['HUMAN_REVIEW_NEEDED'] and c['steps']['OFFICIAL_SOURCE_FOUND']:
            for t in c['proposed_targets']:
                out.append((t, c['precedent'], c['id']))
    return out, d['sources']


def ficha(pid, src):
    _, k, n = pid.split(':')
    head = 'AÇÃO DIRETA DE INCONSTITUCIONALIDADE ' + n if k == 'ADI' else f'TEMA {n} DE REPERCUSSÃO GERAL'
    return '\n'.join([head, 'TRIBUNAL: STF', 'SIMULAÇÃO — NÃO PUBLICADO (piloto de portabilidade do Código Civil)', '',
                      'RESUMO DA FONTE OFICIAL', src['proves'], '', 'FONTE OFICIAL', src['url']]) + '\n'


def build():
    rels, sources = selected()
    lookup0 = (J2I_SD / '05_INDICES_ESP32/JUR_LOOKUP.IDX').read_bytes()
    records0 = (J2I_SD / '05_INDICES_ESP32/JURISPRUDENCIA.IDX').read_bytes()
    if not lookup0.endswith(b'\n') or not records0.endswith(b'\n'):
        raise SystemExit('J2I_INDEX_WITHOUT_TRAILING_NEWLINE')
    card = {k.split('/')[-1] for k in json.loads(CARD.read_text(encoding='utf-8'))['entries'] if k.startswith('99_JURISPRUDENCIA_V2/03_CONTEUDO/')}
    by_target = {}
    for t, pid, cid in rels:
        by_target.setdefault(t, []).append((pid, cid))
    rec, look, new_fichas, rows_meta = bytearray(records0), bytearray(lookup0), {}, []
    for t in sorted(by_target):
        norma, art, par, inc, ali = T.to_pipe_fields(t).split('|')
        off = len(rec)
        for pid, cid in by_target[t]:
            _, k, n = pid.split(':')
            tipo = TIPO[k]
            tail = ':'.join([norma, art, par.upper() if par else '-', inc or '-', ali or '-'])
            src_id = ('A' + n) if k == 'ADI' else ('T' + n)
            url = sources[src_id]['url']
            line = f'{pid}:{tail}|{tipo}|STF|{n}|{STATUS[tipo]}|{JT.label(tipo, "STF", n)}|{pid}|{url}\n'
            rec += line.encode('utf-8')
            fname = JT.ficha(pid).split('/')[-1] if hasattr(JT, 'ficha') else pid.replace(':', '_') + '.TXT'
            if fname not in card:
                new_fichas[fname] = ficha(pid, sources[src_id])
            rows_meta.append(dict(target_id=t, precedent=pid, pilot_candidate=cid, label=JT.label(tipo, 'STF', n), ficha=fname,
                                  ficha_already_on_card=fname in card))
        look += f'{norma}|{art}|{par}|{inc}|{ali}|{off}|{len(by_target[t])}\n'.encode('utf-8')
    files = {'05_INDICES_ESP32/JUR_LOOKUP.IDX': bytes(look), '05_INDICES_ESP32/JURISPRUDENCIA.IDX': bytes(rec)}
    files.update({f'03_CONTEUDO/{k}': v.encode('utf-8') for k, v in sorted(new_fichas.items())})
    man = dict(schema_version=1, kind='SIM_CANDIDATE', norm='CC2002', status='SIMULATION_ONLY', human_approved=False, deployable=False,
               base='J2I_FROZEN_315_198 (J2H_CANDIDATE_B_OVER_A) — JUR_LOOKUP/JURISPRUDENCIA bytes kept as exact prefix',
               base_sha256={'JUR_LOOKUP.IDX': hashlib.sha256(lookup0).hexdigest(), 'JURISPRUDENCIA.IDX': hashlib.sha256(records0).hexdigest()},
               selection='pilot candidates: linking assessment + OFFICIAL_SOURCE_FOUND + HUMAN_REVIEW_NEEDED = false',
               relations=rows_meta, cc_lookups=len(by_target), cc_records=len(rows_meta),
               files={k: hashlib.sha256(v).hexdigest() for k, v in sorted(files.items())},
               fichas_reused_from_card=sorted({r['ficha'] for r in rows_meta if r['ficha_already_on_card']}))
    files['SIM_MANIFEST.json'] = (json.dumps(man, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    return files


def main():
    files = build()
    if '--check' in sys.argv:
        ok = all((OUT / k).is_file() and (OUT / k).read_bytes().replace(b'\r\n', b'\n') == v.replace(b'\r\n', b'\n') for k, v in files.items())
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    for k, v in files.items():
        (OUT / k).parent.mkdir(parents=True, exist_ok=True)
        (OUT / k).write_bytes(v)
    m = json.loads(files['SIM_MANIFEST.json'])
    print(m['cc_lookups'], m['cc_records'], [(r['target_id'], r['label'], r['ficha'], r['ficha_already_on_card']) for r in m['relations']])


if __name__ == '__main__':
    main()
