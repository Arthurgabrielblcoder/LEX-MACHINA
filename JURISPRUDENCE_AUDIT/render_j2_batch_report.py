"""J2 — deterministic Markdown report for a batch decision file (Batches 07+), rendered from J2_BATCHNN_DECISIONS.json only.
Usage: python render_j2_batch_report.py --batch N --level MEDIUM|LOW|HIGH [--check]
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_j2_batch as G  # noqa: E402

SHORT = {'PROMOTE_RECOMMENDED': 'PROMOTE', 'PROMOTE_PROVISIONAL_RECOMMENDED': 'PROMOTE_PROVISIONAL', 'REALLOCATE_RECOMMENDED': 'REALLOCATE',
         'REJECT_FALSE_POSITIVE_RECOMMENDED': 'REJECT_FALSE_POSITIVE', 'REJECT_TEMPORAL_MISMATCH_RECOMMENDED': 'REJECT_TEMPORAL',
         'REJECT_NOT_MATERIAL_RECOMMENDED': 'REJECT_NOT_MATERIAL'}


def t(x):
    return x.split(':', 1)[1].replace('ART.', 'art. ').replace(':PAR.UNICO', ', p.u.').replace(':PAR.', ', § ').replace(':INC.', ', ').replace(':CAPUT', ' caput') \
        if x.startswith('CF88:') else x.replace(':ART.', ' art. ').replace(':PAR.', ', § ').replace(':INC.', ', ')


def render(n, level):
    d = json.loads((G.LEVEL_DIR[level] / f'J2_BATCH{n:02d}_DECISIONS.json').read_text(encoding='utf-8'))
    rc = d['reconstruction']
    L = [f'# JURISPRUDÊNCIA — CF: Batch{n:02d} ({level}; propostas aguardando ratificação)', '', '```',
         f'BATCH = {n:02d} · NÍVEL = {level} · HOST-ONLY · NADA MATERIALIZADO · STATUS = AWAITING_USER_RATIFICATION (human_approved = false)',
         f'DECISÕES = {G.LEVEL_DIR[level].name}/J2_BATCH{n:02d}_DECISIONS.json · fila: pendentes {rc["BACKLOG_PENDING_CURRENT"]} · HIGH {rc["HIGH_CURRENT"]} · '
         f'MEDIUM {rc["MEDIUM_CURRENT"]} · LOW {rc["LOW_CURRENT"]} · restantes no nível após o lote: {d["LEVEL_REMAINING_AFTER_BATCH"]}',
         '```', '', '| # | Target (backlog) | Precedentes | Proposta | Alvo proposto | Tipos no aparelho | Razão |', '|---|---|---|---|---|---|---|']
    for i, x in enumerate(d['decisions'], 1):
        prec = '; '.join(p['id'].replace('STF:', '').replace(':', ' ') + (' (provisório)' if p.get('provisional') else '') for p in x['precedents'])
        dev = ', '.join(f'{k}: {"ok" if v == "VALIDATED" else "novo"}' for k, v in x['device_type_status'].items())
        L.append(f"| {i} | {t(x['recommended_by_backlog'])} | {prec} | **{SHORT.get(x['decision'], x['decision'])}** | "
                 f"{', '.join(t(a) for a in x['recommended_targets']) or '—'} | {dev} | {x['reason']} |")
    L += ['', '```', ' · '.join(f'{k} = {v}' for k, v in d['totals'].items()), '```', '', '## Fontes', '', '| Id | Página | Captura |', '|---|---|---|']
    for k, s in sorted(d['sources'].items()):
        h = s.get('dom_text_sha256') or s.get('snapshot_sha256') or ''
        L.append(f"| {k} | {s['title']} | `{h[:8]}…` ({s.get('accessed_on', '')}{', reuso ' + s['reused_from'] if s.get('reused_from') else ''}) |")
    L += ['', 'Detectores da Fase D: os alertas (namespace, temporal, status) estão em `decisions[].auditor_flags`. Cada alerta foi conferido com a '
          'evidência oficial antes da decisão.', '']
    return '\n'.join(L)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', type=int, required=True)
    ap.add_argument('--level', required=True)
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out = G.LEVEL_DIR[a.level] / f'J2_BATCH{a.batch:02d}_REVIEW.md'
    text = render(a.batch, a.level)
    if a.check:
        ok = out.is_file() and out.read_text(encoding='utf-8').replace('\r\n', '\n') == text
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    out.write_text(text, encoding='utf-8', newline='\n')
    print(out.name)
