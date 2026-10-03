# -*- coding: utf-8 -*-
"""REFERENCE WORK COVERAGE RUN3 (read-only): layer 4 REFERENCIAS (WORK_REFERENCE, CURRENT_VISIBLE) before (RUN2) and after (RUN3).

Sources (never written): export_test/run2 and export_test/run3 (CF88_REFERENCES_EXPORT.json), CF88_REFERENCES_CANONICAL.json (RC2
scores), CF88_WORK_REFERENCE_ADDITIONS.json (approved scores), REFERENCE_EXPANSION_ROUND1_DECISIONS.json, CF88_TARGET_INDEX.json and the
RUN3 device staging candidate (CF88_TEXT_MAP.IDX, same bytes as the baseline map).
Writes: REFERENCE_WORK_COVERAGE_RUN3.md, REFERENCE_WORK_COVERAGE_RUN3.csv.   Usage: python build_reference_coverage_run3.py
"""
import collections
import csv
import json
from pathlib import Path

import build_reference_coverage_audit as A

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUN3 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run3/CF88_REFERENCES_EXPORT.json'
ADDITIONS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_WORK_REFERENCE_ADDITIONS.json'
DECISIONS = HERE / 'REFERENCE_EXPANSION_ROUND1_DECISIONS.json'
TEXT_MAP = ROOT / 'DEVICE_INTEGRATION/staging_sd_v1_run3_candidate/SD/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX'
REQUIRED = (37, 43, 52, 58, 62, 86, 134, 144, 145, 182, 184, 192, 196, 201, 206, 215, 231)


def work_links(path):
    doc = json.loads(Path(path).read_text(encoding='utf-8'))
    return [l for ls in doc['references'].values() for l in ls if l['reference_type'] == 'WORK_REFERENCE' and l['visibility'] == 'CURRENT_VISIBLE'], doc


def numbers(work):
    arts = {A.art_key(l['target_id']) for l in work}
    return dict(links=len(work), targets=len({l['target_id'] for l in work}), cf_articles=len({a for a in arts if a.startswith('CF88:')}),
                adct_articles=len({a for a in arts if a.startswith('ADCT:')}), adct_targets=len({l['target_id'] for l in work if l['target_id'].startswith('ADCT:')}))


def main():
    targets, order, status, _, runs, scores, _, _ = A.load()
    mapped = {l.split('|')[2] for l in TEXT_MAP.read_text(encoding='utf-8').splitlines() if l and l[0] != '#'}
    w2, doc2 = work_links(A.RUN2)
    w3, doc3 = work_links(RUN3)
    adds = {(a['target_id'], a['work_id']): a for a in json.loads(ADDITIONS.read_text(encoding='utf-8'))['records']}
    dec = json.loads(DECISIONS.read_text(encoding='utf-8'))
    k2 = {(l['target_id'], l['source_id']) for l in w2}
    n2, n3 = numbers(w2), numbers(w3)

    def score(l):
        a = adds.get((l['target_id'], l['source_id']))
        if a:
            return f"{a['score_editorial']:.1f}"
        sc = [s for s in scores.get((l['target_id'], l['source_id']), []) if s is not None]
        return f'{max(sc):.1f}' if sc else ''

    def display(t):
        if t in mapped:
            return t
        if t.endswith(':CAPUT') and t[:-len(':CAPUT')] in mapped:
            return t[:-len(':CAPUT')]
        return ''

    rows = []
    for l in sorted(w3, key=lambda l: (order[l['target_id']], l['label'])):
        a = adds.get((l['target_id'], l['source_id']))
        disp = display(l['target_id'])
        rows.append(dict(ARTICLE=A.label_art(A.art_key(l['target_id'])), TARGET_ID=l['target_id'], TARGET_SHORT=A.short(l['target_id']),
                         TARGET_KIND=targets[l['target_id']]['kind'], REFERENCE_ID=l['source_id'], TITLE=l['label'],
                         MEDIA_TYPE=(l.get('payload') or {}).get('tipo') or '', YEAR=(l.get('payload') or {}).get('ano') or '', SCORE=score(l),
                         IN_RUN2='YES' if (l['target_id'], l['source_id']) in k2 else 'NO',
                         ORIGIN='REFERENCE_EXPANSION_01' if a else 'CATALOG_RC2', REVIEW_STATUS=a['review_status'] if a else 'RC2_HUMAN_REVIEWED',
                         DECISION=a['decision'] if a else '', DEVICE_DISPLAY_TARGET=disp, LAYER4_EXPECTED='YES' if disp else 'NO',
                         DISPLAY_QUERY_KEYS='+'.join(A.query_keys(disp)) if disp else '', LINK_REFERENCE_ID=l['reference_id']))
    with open(HERE / 'REFERENCE_WORK_COVERAGE_RUN3.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

    def art_works(work, key):
        return sorted({f"{l['label']} ({A.short(l['target_id'])})" for l in work if A.art_key(l['target_id']) == key})

    req = []
    for key in [f'CF88:ART.{n}' for n in REQUIRED] + ['ADCT:ART.68', 'CF88:ART.7']:
        before, after = art_works(w2, key), art_works(w3, key)
        held = [d for d in dec['decisions'] if d.get('integration') == 'APPROVED_PENDING_WORK_IDENTITY' and A.art_key(d['target_id']) == key]
        new = sorted(set(after) - set(before))
        st = ('REFORÇADO' if before and new else 'NOVA COBERTURA' if new else
              'SEM COBERTURA — aprovado, retido (obra sem identidade)' if held else 'SEM MUDANÇA')
        req.append(dict(article=A.label_art(key), run2=len(before), run3=len(after), new=new, status=st))

    gaps = [dict(t=g['target_id'], reason=g['reason'], run3=art_works(w3, g['target_id'])) for g in dec['confirmed_reference_gaps']]
    rejected = [d for d in dec['decisions'] if d['decision'] == 'REJECT']
    held = [d for d in dec['decisions'] if d.get('integration') == 'APPROVED_PENDING_WORK_IDENTITY']
    new_rows = [r for r in rows if r['IN_RUN2'] == 'NO']

    M = ['# Cobertura da camada 4 REFERÊNCIAS — RUN2 → RUN3', '',
         '`WORK_REFERENCE` com `CURRENT_VISIBLE` apenas (mesmo classificador do firmware). Artigo repetido conta uma vez; target ≠ artigo.',
         f"RUN2: `{A.RUN2.relative_to(ROOT).as_posix()}` · RUN3 (candidato): `{RUN3.relative_to(ROOT).as_posix()}`.", '',
         '## Antes × depois', '', '| MÉTRICA | RUN2 | RUN3 | Δ |', '|---|---|---|---|']
    for k, lab in (('links', 'Vínculos WORK_REFERENCE'), ('targets', 'Targets canônicos com obra'), ('cf_articles', 'Artigos distintos da CF com obra'),
                   ('adct_articles', 'Artigos do ADCT com obra'), ('adct_targets', 'Targets do ADCT com obra')):
        M.append(f'| {lab} | {n2[k]} | {n3[k]} | +{n3[k] - n2[k]} |')
    M += ['', f"- Relações totais do export: {doc2['total_links']} → {doc3['total_links']} (só WORK_REFERENCE mudou; jurisprudência, correlatas e ocultos idênticos).",
          f"- Exclusões do RUN2 mantidas no RUN3: {', '.join('`' + x['reference_id'] + '`' for x in doc3['excluded_links'])}.", '',
          '## Artigos-alvo da expansão', '', '| ARTIGO | OBRAS RUN2 | OBRAS RUN3 | NOVAS | SITUAÇÃO |', '|---|---|---|---|---|']
    M += [f"| {r['article']} | {r['run2']} | {r['run3']} | {'<br>'.join(r['new']) or '—'} | {r['status']} |" for r in req]
    M += ['', '## Lacunas e rejeições deliberadas', '']
    M += [f"- **{A.short(g['t'])}** `CONFIRMED_REFERENCE_GAP` — {g['reason']} Obras no RUN3: {len(g['run3'])}." for g in gaps]
    M += [f"- **{A.short(d['target_id'])}** {d['obra']}: `{d['final_status']}` — {d['reason']}" for d in rejected]
    M += [f"- **{A.short(d['target_id'])}** {d['obra']}: aprovado (score {d['final']['score']}), `APPROVED_PENDING_WORK_IDENTITY` — obra sem ID em nenhum catálogo; fora do RUN3." for d in held]
    M += ['', '## Novos vínculos (21) e expectativa no aparelho', '',
          '| TARGET | OBRA | TIPO | ANO | SCORE | DECISÃO | LINHA DO APARELHO (ACTIVE_TARGET) | CHAVES CONSULTADAS |', '|---|---|---|---|---|---|---|---|']
    M += [f"| `{r['TARGET_SHORT']}` | {r['TITLE']} ({r['REFERENCE_ID']}) | {r['MEDIA_TYPE']} | {r['YEAR']} | {r['SCORE']} | {r['DECISION']} | "
          f"`{r['DEVICE_DISPLAY_TARGET']}` | {r['DISPLAY_QUERY_KEYS']} |" for r in new_rows]
    M += ['', 'Regra ART↔CAPUT preservada: obra em `CF88:ART.n:CAPUT` aparece na linha `CF88:ART.n`; nunca em incisos, parágrafos ou alíneas.', '',
          '## Tabela por artigo (RUN3)', '', '| ARTIGO | TARGETS COM OBRA | VÍNCULOS | NOVOS NO RUN3 |', '|---|---|---|---|']
    per = collections.defaultdict(list)
    for r in rows:
        per[A.art_key(r['TARGET_ID'])].append(r)
    for a in sorted(per, key=lambda a: (a.startswith('ADCT'), order.get(a, 0))):
        rs = per[a]
        M.append(f"| {A.label_art(a)} | {'<br>'.join(sorted({r['TARGET_SHORT'] for r in rs}, key=lambda s: order.get(next(x['TARGET_ID'] for x in rs if x['TARGET_SHORT'] == s), 0)))} "
                 f"| {len(rs)} | {sum(1 for r in rs if r['IN_RUN2'] == 'NO')} |")
    M += ['', f'CSV completo (um vínculo por linha, {len(rows)} linhas): `REFERENCE_WORK_COVERAGE_RUN3.csv`.']
    (HERE / 'REFERENCE_WORK_COVERAGE_RUN3.md').write_bytes(('\n'.join(M) + '\n').encode('utf-8'))
    print(json.dumps(dict(run2=n2, run3=n3, new=len(new_rows), required=[(r['article'], r['status']) for r in req]), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
