"""PREVIOUS_REFERENCE_CLAIM_CORRECTION.md from REFERENCE_COVERAGE_AUDIT_SUMMARY.json + run2 (read-only).

The earlier caput-equivalence report listed 32 links on 17 `:CAPUT` targets as "25 WORK_REFERENCE, 6 JURISPRUDENCE, 1 CORRELATA";
reading that list as "17 articles with works" is wrong. This document classifies each of the 17 articles.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUN2 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run2/CF88_REFERENCES_EXPORT.json'
S = json.loads((HERE / 'REFERENCE_COVERAGE_AUDIT_SUMMARY.json').read_text(encoding='utf-8'))
doc = json.loads(RUN2.read_text(encoding='utf-8'))
links = [l for ls in doc['references'].values() for l in ls]
ARTS = (2, 5, 6, 14, 37, 43, 62, 98, 170, 193, 194, 201, 202, 205, 220, 225, 227)
ZERO = (37, 43, 62, 98, 193, 201, 202)
TYPES = {'JURISPRUDENCE': 'JURISPRUDÊNCIA', 'CORRELATA': 'CORRELATA'}

M = ['# Correção da afirmação anterior sobre REFERÊNCIAS (camada 4 = WORK_REFERENCE)', '',
     'A lista anterior de 17 artigos vinha do relatório da equivalência ART ↔ CAPUT: **32 vínculos em 17 targets `:CAPUT`**, dos quais apenas',
     '**25 eram WORK_REFERENCE**; 6 eram JURISPRUDÊNCIA e 1 era CORRELATA. Ler essa lista como “17 artigos com obra” misturou tipos de vínculo.',
     'Este documento fixa a verdade canônica com o export corrigido (run2) e o classificador atual (somente `WORK_REFERENCE` `CURRENT_VISIBLE` vai para o botão 4).', '',
     '| ARTIGO | CLASSIFICAÇÃO | WORK_REFERENCE NO CAPUT | O QUE HAVIA NO CAPUT (NÃO-OBRA) | OBRAS NO ARTIGO INTEIRO |', '|---|---|---|---|---|']
detail = []
for n in ARTS:
    a = S['article_audits'][str(n)]
    key = f'CF88:ART.{n}'
    caput_non = [f"{TYPES.get(l['reference_type'], l['reference_type'])}: {l['label']} ({l['source_id']})" for l in links
                 if l['target_id'] in (key, key + ':CAPUT') and l['reference_type'] != 'WORK_REFERENCE' and l['visibility'] == 'CURRENT_VISIBLE']
    cls = 'CONFIRMED_WORK_REFERENCE' if a['caput'] else 'MISCLASSIFIED_NON_WORK_RELATION'
    M.append(f"| Art. {n} | **{cls}** | {'; '.join(a['caput_works']) or '—'} | {'; '.join(caput_non) or '—'} | {a['work_total']} |")
    lines = [f'### Art. {n}', '',
             f"1. Existe WORK_REFERENCE? **{'SIM' if a['work_total'] else 'NÃO'}** ({a['work_total']} no artigo inteiro).",
             '2. Target exato, obra e score:' if a['work_links'] else '2. Target exato: —']
    for w in a['work_links']:
        d = w['device'] or {}
        lines.append(f"   - `{w['target']}` — {w['title']} ({w['work']}, {w['media']}) — score {w['score'] or 'ausente'} — "
                     f"botão 4 no DEVICE atual: **{d.get('LAYER4_EXPECTED', '—')}** (exibido em `{d.get('EXPECTED_DISPLAY_TARGET', '—')}`"
                     f"{', via ART↔CAPUT' if d.get('ART_CAPUT_EQUIVALENCE') == 'YES' else ''})")
    non = a['non_work_relations']
    lines.append(f"3. Existe apenas JURISPRUDÊNCIA/CORRELATA em vez de obra? **{'SIM' if not a['work_total'] and non else 'NÃO'}**"
                 + (f" — vínculos não-obra no artigo: {', '.join(f'{k} {v}' for k, v in non.items())}" if non else ''))
    if n in ZERO:
        lines += ['', f"**Auditoria do artigo inteiro (verificação física de Arthur):**",
                  f"- WORK_REFERENCE NO CAPUT = {'YES' if a['caput'] else 'NO'}",
                  f"- WORK_REFERENCE EM QUALQUER INCISO = {', '.join(a['incisos']) or 'nenhum'}",
                  f"- WORK_REFERENCE EM QUALQUER PARÁGRAFO = {', '.join(a['paragrafos']) or 'nenhum'}",
                  f"- WORK_REFERENCE EM QUALQUER ALÍNEA = {', '.join(a['alineas']) or 'nenhuma'}",
                  f"- TOTAL WORK_REFERENCE = {a['work_total']}",
                  f"- STATUS = **{a['status']}**" + (' · **CONFIRMED_REFERENCE_GAP**' if a['confirmed_gap'] else '')]
        if n == 193:
            lines += ['- **Divergência com o teste físico:** os dados têm 3 obras em `CF88:ART.193:CAPUT`, alcançáveis pela linha do art. 193 '
                      '(ACTIVE_TARGET `CF88:ART.193`, chaves `ART.193 + ART.193:CAPUT`). Hipótese a confirmar no aparelho: o CONTEXTO é escolhido '
                      'pela linha central do viewport; o art. 193 é curto e, após a busca, a linha central costuma cair no parágrafo único ou no '
                      'art. 194. O botão 4 só aparece quando o rodapé mostra `CONTEXTO: ART. 193` (sem `PAR.`). Reteste físico recomendado; '
                      'não é lacuna de dados.']
    detail += lines + ['']
M += ['', '**Resumo:** CONFIRMED_WORK_REFERENCE = arts. ' + ', '.join(str(n) for n in ARTS if S['article_audits'][str(n)]['caput']) +
      '; MISCLASSIFIED_NON_WORK_RELATION = arts. ' + ', '.join(str(n) for n in ARTS if not S['article_audits'][str(n)]['caput']) + '.', '',
      'Nos MISCLASSIFIED, o vínculo do caput era jurisprudência ou correlata: ele aparece em 2 JURIS. ou 1 CORR., nunca em 4 REF. '
      'Nesses 6 artigos não existe nenhuma obra em todo o artigo (CONFIRMED_REFERENCE_GAP).', '', '## Auditoria individual (17 artigos)', ''] + detail
(HERE / 'PREVIOUS_REFERENCE_CLAIM_CORRECTION.md').write_bytes(('\n'.join(M) + '\n').encode('utf-8'))
print('ok')
