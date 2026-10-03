"""REFERENCE COVERAGE TRUTH AUDIT (read-only): real coverage of layer 4 REFERENCIAS = WORK_REFERENCE only.

Sources (never written):
- LEGAL_TARGET_ID/derived/export_test/run2/CF88_REFERENCES_EXPORT.json  current export (430 links; CF88_LINK_EXCLUSIONS applied)
- LEGAL_TARGET_ID/derived/export_test/run1/CF88_REFERENCES_EXPORT.json  physical DEVICE V1 baseline (432 links)
- LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json                 canonical source (score_editorial per route)
- LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json                         structure (articles, kinds)
- DEVICE_INTEGRATION/staging_sd_v1/SD/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX  ACTIVE_TARGET candidates (device semantics)
- LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_69_CANONICO.json  official work registry (69 works)
- LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/07_CATALOGO_CANDIDATO/CATALOGO_EXPANSAO_200.json  candidate catalog (not integrated)

Classifier: only reference_type WORK_REFERENCE with visibility CURRENT_VISIBLE counts (same as lexV1ClassificarDestino -> REFERENCIA).
Usage: python build_reference_coverage_audit.py   (writes the CSV/MD/JSON files next to this script)
"""
import collections
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUN1 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run1/CF88_REFERENCES_EXPORT.json'
RUN2 = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run2/CF88_REFERENCES_EXPORT.json'
CANON = ROOT / 'LEGAL_TARGET_ID/derived/CF88_REFERENCES_CANONICAL.json'
INDEX = ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json'
STATUS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS.json'
TEXT_MAP = ROOT / 'DEVICE_INTEGRATION/staging_sd_v1/SD/99_LEX_V1/10_TARGETS/CF88_TEXT_MAP.IDX'
REGISTRY = ROOT / 'LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_69_CANONICO.json'
CANDIDATES = ROOT / 'LEX_MACHINA_REFERENCIAS_V2/09_CATALOGO_EXPANSAO_200/07_CATALOGO_CANDIDATO/CATALOGO_EXPANSAO_200.json'

BLOCKS = (('Princípios Fundamentais', 1, 4), ('Direitos e Garantias Fundamentais', 5, 17), ('Organização do Estado', 18, 43),
          ('Organização dos Poderes', 44, 135), ('Defesa do Estado e das Instituições Democráticas', 136, 144), ('Tributação e Orçamento', 145, 169),
          ('Ordem Econômica e Financeira', 170, 192), ('Ordem Social', 193, 232), ('Disposições Constitucionais Gerais', 233, 250))
RANGES = [(a, a + 24) for a in range(1, 250, 25)]
AUDIT_ARTICLES = (2, 5, 6, 14, 37, 43, 62, 98, 170, 193, 194, 201, 202, 205, 220, 225, 227)
ARTHUR_ZERO = (37, 43, 62, 98, 193, 201, 202)


def art_of(tid):
    m = re.match(r'^(CF88|ADCT):ART\.([0-9]+)(-[A-Z])?', tid)
    return (m.group(1), int(m.group(2)), m.group(3) or '') if m else None


def art_key(tid):
    a = art_of(tid)
    return f'{a[0]}:ART.{a[1]}{a[2]}' if a else None


def label_art(key):
    ns, rest = key.split(':ART.')
    return ('ADCT art. ' if ns == 'ADCT' else 'Art. ') + rest


def short(tid):
    """CF88:ART.5:INC.XV -> CF88.5.XV (user notation)."""
    parts = tid.split(':')
    out = [parts[0]]
    for p in parts[1:]:
        out.append(p.split('.', 1)[1] if '.' in p and p != 'PAR.UNICO' else ('UNICO' if p == 'PAR.UNICO' else p))
    return '.'.join(out)


def load():
    idx = json.loads(INDEX.read_text(encoding='utf-8'))
    targets = {t['target_id']: t for t in idx['targets']}
    order = {t['target_id']: i for i, t in enumerate(idx['targets'])}
    status = json.loads(STATUS.read_text(encoding='utf-8'))['targets']
    mapped = {l.split('|')[2] for l in TEXT_MAP.read_text(encoding='utf-8').splitlines() if l and l[0] != '#'}
    runs = {}
    for name, p in (('run1', RUN1), ('run2', RUN2)):
        doc = json.loads(p.read_text(encoding='utf-8'))
        runs[name] = dict(doc=doc, links=[l for ls in doc['references'].values() for l in ls])
    scores = collections.defaultdict(list)
    for r in json.loads(CANON.read_text(encoding='utf-8'))['records']:
        if r['source_layer'] == 'V2_RC2_REFERENCES':
            lf = r.get('legal_fields_preserved', {})
            scores[(r['target_id'], r['provenance']['work_id'])].append(lf.get('score_editorial'))
    reg = json.loads(REGISTRY.read_text(encoding='utf-8'))['obras']
    cand = json.loads(CANDIDATES.read_text(encoding='utf-8'))
    return targets, order, status, mapped, runs, scores, reg, cand


def query_keys(tid):
    """Firmware lexV1QueryKeysForActiveTarget: ART.n (article line = visual caput) -> [ART.n, ART.n:CAPUT]; else [tid]."""
    if tid.startswith('CF88:ART.') and ':' not in tid[len('CF88:ART.'):]:
        return [tid, tid + ':CAPUT']
    return [tid]


def main():
    targets, order, status, mapped, runs, scores, reg, cand = load()
    links2 = runs['run2']['links']
    work = [l for l in links2 if l['reference_type'] == 'WORK_REFERENCE' and l['visibility'] == 'CURRENT_VISIBLE']
    by_type = collections.Counter((l['reference_type'], l['visibility']) for l in links2)
    excluded = runs['run2']['doc'].get('excluded_links', [])
    w1 = sorted((l['target_id'], l['source_id']) for l in runs['run1']['links'] if l['reference_type'] == 'WORK_REFERENCE' and l['visibility'] == 'CURRENT_VISIBLE')
    w2 = sorted((l['target_id'], l['source_id']) for l in work)

    # ---- per-link rows
    rows = []
    for l in sorted(work, key=lambda l: (order[l['target_id']], l['label'])):
        sc = [s for s in scores.get((l['target_id'], l['source_id']), []) if s is not None]
        rows.append(dict(ARTICLE=label_art(art_key(l['target_id'])), TARGET_ID=l['target_id'], TARGET_SHORT=short(l['target_id']),
                         TARGET_KIND=targets[l['target_id']]['kind'], REFERENCE_ID=l['source_id'], TITLE=l['label'],
                         MEDIA_TYPE=(l.get('payload') or {}).get('tipo') or '', YEAR=(l.get('payload') or {}).get('ano') or '',
                         SCORE='' if not sc else f'{max(sc):.1f}', VISIBILITY=l['visibility'],
                         CURRENT_STATUS='ACTIVE' if status.get(l['target_id'], {}).get('status') == 'CURRENT' else status.get(l['target_id'], {}).get('status', 'UNKNOWN'),
                         ROUTES=len(l.get('routes', [])), LINK_REFERENCE_ID=l['reference_id']))
    per_target = collections.Counter(r['TARGET_ID'] for r in rows)
    per_article = collections.defaultdict(list)
    for r in rows:
        per_article[art_key(r['TARGET_ID'])].append(r)

    # ---- structure: articles
    arts = [t for t in sorted(targets, key=lambda t: order[t]) if targets[t]['kind'] == 'ARTIGO']
    cf_arts = [a for a in arts if a.startswith('CF88:')]
    adct_arts = [a for a in arts if a.startswith('ADCT:')]
    covered = {a for a in per_article}

    def all_links(tid_prefix):
        return [l for l in links2 if l['target_id'] == tid_prefix or l['target_id'].startswith(tid_prefix + ':')]

    # ---- device expectations (ACTIVE_TARGET + ART<->CAPUT only on the article line)
    dev = []
    for tid in sorted(per_target, key=lambda t: order[t]):
        if tid in mapped:
            disp, eq = tid, 'NO'
        elif tid.endswith(':CAPUT') and tid[:-len(':CAPUT')] in mapped:
            disp, eq = tid[:-len(':CAPUT')], 'YES'
        else:
            disp, eq = '', 'NO'
        dev.append(dict(TARGET_ID=tid, WORK_COUNT=per_target[tid], LAYER4_EXPECTED='YES' if disp else 'NO', ART_CAPUT_EQUIVALENCE=eq,
                        EXPECTED_DISPLAY_TARGET=disp or 'UNREACHABLE (target fora do TEXT_MAP)',
                        DISPLAY_QUERY_KEYS='+'.join(query_keys(disp)) if disp else ''))

    # ---- per article detail audit
    def article_audit(n):
        key = f'CF88:ART.{n}'
        ls = all_links(key)
        w = [l for l in ls if l['reference_type'] == 'WORK_REFERENCE' and l['visibility'] == 'CURRENT_VISIBLE']
        kinds = collections.defaultdict(list)
        for l in w:
            k = targets[l['target_id']]['kind']
            kinds[k].append(f"{short(l['target_id'])}: {l['label']} ({l['source_id']})")
        non = collections.Counter(f"{l['reference_type']}/{l['visibility']}" for l in ls if l not in w)
        excl = [x for x in excluded if x['target_id'] == key or x['target_id'].startswith(key + ':')]
        caput_w = [l for l in w if l['target_id'] in (key, key + ':CAPUT')]
        st = 'ZERO_COVERAGE' if not w else 'COVERED' if caput_w else 'PARTIAL'
        return dict(article=key, work_total=len(w), caput=bool(caput_w), caput_works=[f"{l['label']} ({l['source_id']})" for l in caput_w],
                    incisos=kinds.get('INCISO', []), paragrafos=kinds.get('PARAGRAFO', []) + kinds.get('PARAGRAFO_UNICO', []),
                    alineas=kinds.get('ALINEA', []), status=st, confirmed_gap=not w, non_work_relations=dict(non),
                    excluded_mismatch=[x['reference_id'] for x in excl],
                    work_links=[dict(target=l['target_id'], work=l['source_id'], title=l['label'], media=(l.get('payload') or {}).get('tipo'),
                                     score=next((r['SCORE'] for r in rows if r['TARGET_ID'] == l['target_id'] and r['REFERENCE_ID'] == l['source_id']), ''),
                                     device=next((d for d in dev if d['TARGET_ID'] == l['target_id']), None)) for l in w])

    audits = {n: article_audit(n) for n in sorted(set(AUDIT_ARTICLES))}

    # ---- ranges / blocks / gaps
    def num(a):
        return art_of(a)[1]
    rng = []
    for lo, hi in RANGES:
        ex = [a for a in cf_arts if lo <= num(a) <= hi]
        cov = [a for a in ex if a in covered]
        rng.append(dict(range=f'{lo}–{hi}', existing=len(ex), covered=len(cov), pct=round(100 * len(cov) / len(ex), 1) if ex else 0.0,
                        work_links=sum(len(per_article[a]) for a in cov), articles=[label_art(a) for a in cov]))
    adct_cov = [a for a in adct_arts if a in covered]
    rng.append(dict(range='ADCT', existing=len(adct_arts), covered=len(adct_cov), pct=round(100 * len(adct_cov) / len(adct_arts), 1),
                    work_links=sum(len(per_article[a]) for a in adct_cov), articles=[label_art(a) for a in adct_cov]))
    blocks = []
    for name, lo, hi in BLOCKS:
        ex = [a for a in cf_arts if lo <= num(a) <= hi]
        cov = [a for a in ex if a in covered]
        tg = {r['TARGET_ID'] for a in cov for r in per_article[a]}
        blocks.append(dict(block=name, articles=f'{lo}–{hi}', existing=len(ex), covered=len(cov), targets=len(tg),
                           links=sum(len(per_article[a]) for a in cov), pct=round(100 * len(cov) / len(ex), 1)))
    blocks.append(dict(block='ADCT', articles='ADCT', existing=len(adct_arts), covered=len(adct_cov),
                       targets=len({r['TARGET_ID'] for a in adct_cov for r in per_article[a]}), links=sum(len(per_article[a]) for a in adct_cov),
                       pct=round(100 * len(adct_cov) / len(adct_arts), 1)))
    gaps, run = [], []
    for a in cf_arts + [None]:
        if a is not None and a not in covered:
            run.append(a)
        else:
            if run:
                gaps.append(dict(first=label_art(run[0]), last=label_art(run[-1]), count=len(run)))
            run = []
    gaps.sort(key=lambda g: (-g['count'], g['first']))

    # ---- registry
    used = {l['source_id'] for l in work}
    reg_ids = {o['id'] for o in reg}
    reg_rows = [dict(id=o['id'], titulo=o['titulo'], tipo=o['tipo'], ano=o.get('ano'), used_in_cf=o['id'] in used,
                     cf_links=sum(1 for l in work if l['source_id'] == o['id'])) for o in reg]
    used_outside_registry = sorted(used - reg_ids)

    summary = dict(
        source_current_export=str(RUN2.relative_to(ROOT)), exclusions_applied=[x['reference_id'] for x in excluded],
        run2_total_links=len(links2), run2_by_type_visibility={f'{k[0]}/{k[1]}': v for k, v in sorted(by_type.items())},
        work_reference_links=len(work), work_reference_links_run1=len(w1), work_links_identical_run1_run2=(w1 == w2),
        distinct_targets_with_work=len(per_target), distinct_articles_with_work_cf=len([a for a in covered if a.startswith('CF88:')]),
        adct_targets_with_work=len([t for t in per_target if t.startswith('ADCT:')]), adct_articles_with_work=len(adct_cov),
        cf_articles_existing=len(cf_arts), cf_articles_without_work=len(cf_arts) - len([a for a in covered if a.startswith('CF88:')]),
        cf_article_coverage_pct=round(100 * len([a for a in covered if a.startswith('CF88:')]) / len(cf_arts), 1),
        mean_works_per_target=round(len(work) / len(per_target), 2), max_works_per_target=max(per_target.values()),
        max_works_targets=sorted(t for t, n in per_target.items() if n == max(per_target.values())),
        canonical_rc2_routes=sum(1 for _ in scores for _ in scores[_]), work_links_with_score=sum(1 for r in rows if r['SCORE']),
        work_links_without_score=sum(1 for r in rows if not r['SCORE']),
        device_expectations=dict(layer4_yes=sum(1 for d in dev if d['LAYER4_EXPECTED'] == 'YES'), via_art_caput=sum(1 for d in dev if d['ART_CAPUT_EQUIVALENCE'] == 'YES'),
                                 unreachable=sum(1 for d in dev if d['LAYER4_EXPECTED'] == 'NO')),
        registry=dict(works=len(reg), by_type=dict(collections.Counter(o['tipo'] for o in reg)), used_in_cf=len(used & reg_ids), unused=len(reg_ids - used),
                      used_by_type=dict(collections.Counter(o['tipo'] for o in reg if o['id'] in used)), used_outside_registry=used_outside_registry,
                      used_total_distinct=len(used)),
        candidate_catalog=dict(status=cand['status_catalogo'], works=cand['total_obras'], by_type_status=cand['por_tipo_status']),
        ranges=rng, blocks=blocks, largest_gaps=gaps[:15], article_audits=audits)
    (HERE / 'REFERENCE_COVERAGE_AUDIT_SUMMARY.json').write_bytes((json.dumps(dict(summary, registry_rows=reg_rows), ensure_ascii=False, indent=1) + '\n').encode('utf-8'))

    cols = ['ARTICLE', 'TARGET_ID', 'TARGET_SHORT', 'TARGET_KIND', 'REFERENCE_ID', 'TITLE', 'MEDIA_TYPE', 'YEAR', 'SCORE', 'VISIBILITY', 'CURRENT_STATUS', 'ROUTES', 'LINK_REFERENCE_ID']
    with open(HERE / 'REFERENCE_WORK_COVERAGE_FULL.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    with open(HERE / 'REFERENCE_LAYER4_DEVICE_EXPECTATIONS.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['TARGET_ID', 'WORK_COUNT', 'LAYER4_EXPECTED', 'ART_CAPUT_EQUIVALENCE', 'EXPECTED_DISPLAY_TARGET', 'DISPLAY_QUERY_KEYS'],
                           lineterminator='\n')
        w.writeheader()
        w.writerows(dev)

    # ---- coverage markdown
    M = ['# Cobertura real da camada 4 REFERÊNCIAS (WORK_REFERENCE) — CF88', '',
         f"Fonte: `{summary['source_current_export']}` (export corrigido; exclusões `CF88_LINK_EXCLUSIONS.json` aplicadas). Somente `WORK_REFERENCE` com `CURRENT_VISIBLE`; jurisprudência, correlatas, ocultos e `MATERIAL_MISMATCH_EXCLUDED` não entram.",
         f"Os vínculos de obra do run1 (baseline físico) e do run2 são idênticos: **{summary['work_links_identical_run1_run2']}** (as duas exclusões do run2 são de jurisprudência).", '',
         '## Números', '',
         f"- Vínculos WORK_REFERENCE: **{summary['work_reference_links']}** (de {summary['run2_total_links']} vínculos do run2).",
         f"- Targets canônicos distintos com obra: **{summary['distinct_targets_with_work']}**.",
         f"- Artigos distintos da CF com obra: **{summary['distinct_articles_with_work_cf']}** de {summary['cf_articles_existing']} ({summary['cf_article_coverage_pct']}%).",
         f"- Targets do ADCT com obra: **{summary['adct_targets_with_work']}**.",
         f"- Média de obras por target: **{summary['mean_works_per_target']}**; máximo: **{summary['max_works_per_target']}** ({', '.join(summary['max_works_targets'])}).",
         '- **1 target com obra ≠ 1 artigo coberto**: um artigo com 10 targets com obra conta como 1 artigo coberto. Os dois números são dados separadamente.', '',
         '## Tabela por artigo', '', '| ARTIGO | TARGETS COM OBRA | Nº DE VÍNCULOS | OBRAS |', '|---|---|---|---|']
    for a in sorted(per_article, key=lambda a: order[a] if a in order else 0):
        rs = per_article[a]
        tg = sorted({r['TARGET_ID'] for r in rs}, key=lambda t: order[t])
        M.append(f"| {label_art(a)} | {'<br>'.join(short(t) for t in tg)} | {len(rs)} | {len({r['REFERENCE_ID'] for r in rs})} |")
    M += ['', '## Vínculos (um por linha)', '', '| ARTICLE | TARGET_ID | TARGET_KIND | REFERENCE_ID | TITLE | MEDIA_TYPE | SCORE | VISIBILITY | CURRENT_STATUS |',
          '|---|---|---|---|---|---|---|---|---|']
    M += [f"| {r['ARTICLE']} | `{r['TARGET_SHORT']}` | {r['TARGET_KIND']} | {r['REFERENCE_ID']} | {r['TITLE']} | {r['MEDIA_TYPE']} | {r['SCORE'] or '—'} | {r['VISIBILITY']} | {r['CURRENT_STATUS']} |"
          for r in rows]
    M += ['', '## Cobertura por faixa de artigos', '', '| FAIXA | ARTIGOS EXISTENTES | ARTIGOS COM ALGUMA OBRA | COBERTURA | WORK_REFERENCE LINKS |', '|---|---|---|---|---|']
    M += [f"| {r['range']} | {r['existing']} | {r['covered']} | {r['pct']}% | {r['work_links']} |" for r in rng]
    M += ['', '## Cobertura por grandes blocos', '', '| BLOCO | ARTS. | ARTIGOS | ARTIGOS COM OBRA | TARGETS COM OBRA | VÍNCULOS | COBERTURA |', '|---|---|---|---|---|---|---|']
    M += [f"| {b['block']} | {b['articles']} | {b['existing']} | {b['covered']} | {b['targets']} | {b['links']} | {b['pct']}% |" for b in blocks]
    M += ['', '## Os 15 maiores intervalos consecutivos sem obra', '']
    M += [f"{i}. {g['first']} – {g['last']}: **{g['count']}** artigos consecutivos sem obra" for i, g in enumerate(gaps[:15], 1)]
    M += ['', '## Acervo de obras', '',
          f"- Registry oficial (`CATALOGO_69_CANONICO.json`): **{summary['registry']['works']}** obras ({', '.join(f'{k} {v}' for k, v in sorted(summary['registry']['by_type'].items()))}).",
          f"- Com pelo menos um vínculo na CF: **{summary['registry']['used_in_cf']}**; sem uso na CF: **{summary['registry']['unused']}**.",
          f"- Obras usadas na CF fora do registry de 69: {', '.join(summary['registry']['used_outside_registry']) or 'nenhuma'}.",
          f"- Catálogo de expansão: {summary['candidate_catalog']['works']} obras, status `{summary['candidate_catalog']['status']}` (não integrado; sem vínculos).",
          '- Tipos MÚSICA e OUTROS: 0 no registry.']
    (HERE / 'REFERENCE_WORK_COVERAGE_FULL.md').write_bytes(('\n'.join(M) + '\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in summary.items() if k not in ('ranges', 'blocks', 'largest_gaps', 'article_audits')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
