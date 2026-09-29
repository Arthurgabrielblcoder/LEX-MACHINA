"""ENTENDA production batch builder (norm-agnostic): semantic selection report + stamping + deterministic build + review sheet.

Every structural target in the batch scope is evaluated and classified as OVERVIEW / DEVICE / BLOCK / ITEM (own explanation),
NO_SEPARATE_EXPLANATION (covered by an article overview or a block, with the covering explanation named) or EXCLUDED_HISTORICAL.
Explanations already approved in the main corpus are reused (never duplicated); new ones are stamped PENDING_HUMAN_REVIEW.
A final (human-approved) batch declares expected_review_status=HUMAN_APPROVED_T1 and supersedes_corpus: the pending corpus is
the immutable evidence, adjusted explanations get a new editorial_version and the earlier one stays RETIRED.
Jurisprudence is never written into ENTENDA: the batch only emits link recommendations, marking READY_TO_LINK solely when the
record identity is proven in a local curated dataset (otherwise PENDING_EXTERNAL_INGESTION).
Usage: python production_batch.py <batch_dir>   (batch_dir contains BATCH_SPEC.json and the drafts named in it)
"""
import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entenda_engine as E  # noqa: E402

SELECTED = ('OVERVIEW', 'DEVICE', 'BLOCK', 'ITEM')


class BatchError(E.EntendaError):
    pass


def classify(spec, ctx, reused, new):
    """Selection report: one row per evaluated target of the scope."""
    scope = [t for a in spec['scope'] for t in ctx.subtree(a)]
    own = {r['target_id']: (r, 'PILOT_T1_APPROVED') for r in reused}
    own.update({r['target_id']: (r, 'BATCH_NEW') for r in new})
    for tid in own:
        if tid not in scope:
            raise BatchError('BATCH_TARGET_OUT_OF_SCOPE', tid)
    covered = {c: tid for tid, (r, _) in own.items() for c in r['granularity'].get('covered_targets', [])}
    overrides = spec.get('no_separate_reasons', {})
    overview_all = set(spec.get('overview_covers_all_subdivisions', []))
    criteria = {e['target_id']: e.get('selection_criteria', []) for e in spec['_drafts']['explanations']}
    rows = []
    for tid in scope:
        status = ctx.effective_status(tid)
        row = dict(target_id=tid, kind=ctx.kind(tid), status=status)
        if spec.get('report_schema', 1) >= 2:
            row.update(structurally_present=ctx.structurally_present(tid), legal_status=ctx.legal_status(tid),
                       legally_current=ctx.legally_current(tid))
        art = next(a for a in spec['scope'] if tid == a or tid.startswith(a + ':'))
        if status == 'HISTORICAL':
            row.update(classification='EXCLUDED_HISTORICAL', selection_reason='redacao historica: producao CURRENT-only')
        elif status == 'REVOKED':
            row.update(classification='EXCLUDED_REVOKED',
                       selection_reason='estruturalmente presente no texto consolidado, mas legal_status REVOKED: nao recebe ENTENDA vigente')
        elif status != 'CURRENT':
            row.update(classification='EXCLUDED_NOT_CURRENT', selection_reason=f'status {status}: producao CURRENT-only')
        elif tid in own:
            r, src = own[tid]
            row.update(classification=r['granularity']['role'], explanation_id=r['explanation_id'], explanation_source=src,
                       review_status=r['review_status'], selection_criteria=criteria.get(tid, []),
                       selection_reason=r['granularity']['editorial_reason'] if src == 'BATCH_NEW' else spec['reused'][tid])
        else:
            anc = next((a for a in E.T.ancestors(tid) if a in own and own[a][0]['granularity']['role'] != 'OVERVIEW'), None)
            anc_cov = next((a for a in E.T.ancestors(tid) if a in covered), None)
            if tid in covered:
                row.update(covered_by=covered[tid], coverage='BLOCK_COVERED_SIBLING',
                           selection_reason='explicado em bloco com irmaos (covered_targets do bloco)')
            elif anc:
                row.update(covered_by=anc, coverage='BLOCK_SUBDIVISION', selection_reason='subdivisao explicada no bloco do dispositivo-pai')
            elif anc_cov:
                row.update(covered_by=covered[anc_cov], coverage='BLOCK_COVERED_SUBDIVISION',
                           selection_reason='subdivisao de dispositivo coberto por bloco')
            elif tid in overrides:
                row.update(covered_by=art, coverage='ARTICLE_OVERVIEW', selection_reason=overrides[tid])
            elif row['kind'] == 'CAPUT':
                row.update(covered_by=art, coverage='ARTICLE_OVERVIEW',
                           selection_reason='caput explicado na visao geral do artigo (regra T1: caput sem comando distinto da visao geral)')
            elif art in overview_all:
                row.update(covered_by=art, coverage='ARTICLE_OVERVIEW',
                           selection_reason='item curto de lista explicado na visao geral do artigo; explicacao propria repetiria o artigo')
            else:
                raise BatchError('BATCH_TARGET_NOT_CLASSIFIED', tid)
            if row['covered_by'] not in own:
                raise BatchError('BATCH_COVERING_EXPLANATION_MISSING', f"{tid} -> {row['covered_by']}")
            row['classification'] = 'NO_SEPARATE_EXPLANATION'
        rows.append(row)
    return rows


def review_sheet(spec, ctx, new, rows, manifest, decisions=None):
    per = {p['target_id']: p for p in manifest['per_explanation']}
    dec = {d['target_id']: d for d in (decisions or {}).get('decisions', [])}
    warn = {}
    for w in manifest['warnings']:
        warn.setdefault(w['target_id'], []).append(w)
    final = spec.get('expected_review_status', 'PENDING_HUMAN_REVIEW') != 'PENDING_HUMAN_REVIEW'
    lines = [f"# {'FINAL REVIEW SUMMARY' if final else 'REVIEW'} — {spec['batch_id']}", '']
    lines += (['Versão final aprovada pela revisão humana (`HUMAN_APPROVED_T1`). Decisões em `HUMAN_REVIEW_DECISIONS.json`;',
               'as versões anteriores permanecem no corpus como `RETIRED`.', ''] if final else
              ['Explicações novas para revisão humana. Todas estão em `PENDING_HUMAN_REVIEW`.',
               'As explicações reutilizadas de lotes aprovados não são repetidas aqui.', '',
               'Para cada explicação, marque APROVAR, AJUSTAR (indique o trecho) ou REJEITAR.', ''])
    by_art = {}
    for r in new:
        art = next(a for a in spec['scope'] if r['target_id'] == a or r['target_id'].startswith(a + ':'))
        by_art.setdefault(art, []).append(r)
    for art in spec['scope']:
        nsep = [x for x in rows if x['classification'] == 'NO_SEPARATE_EXPLANATION' and (x['target_id'] == art or x['target_id'].startswith(art + ':'))]
        lines += [f'## {art}', '']
        reused = [x for x in rows if x.get('explanation_source') == 'PILOT_T1_APPROVED' and x['target_id'].startswith(art)]
        if reused:
            lines += [f"Reutilizada do piloto (aprovada): `{x['explanation_id']}`." for x in reused] + ['']
        lines += [f'Sem explicação própria: {len(nsep)} dispositivos (ver `SELECTION_REPORT.json`).', '']
        for r in by_art.get(art, []):
            g, c = r['granularity'], r['content']
            lines += [f"### {E.display_title(r)}", '',
                      f"- **TARGET:** `{r['target_id']}` · `{r['explanation_id']}`",
                      f"- **DISPLAY TITLE:** {E.display_title(r)}",
                      f"- **DISPOSITIVO:** {g['target_kind']}",
                      f"- **COVERED TARGETS:** {', '.join('`' + t + '`' for t in g.get('covered_targets', [])) or '—'}",
                      f"- **ROLE:** {g['role']} · {g['semantic_autonomy']} · contexto: {', '.join('`' + t + '`' for t in g['context_targets']) or '—'}",
                      f"- **STATUS:** {r['review_status']} · vigência {E.display_validity(r)} · {per[r['target_id']]['words']} palavras · {per[r['target_id']]['payload_bytes']} bytes · referências {per[r['target_id']]['reference_count']}",
                      f"- **Motivo da seleção:** {g['editorial_reason']}", '',
                      '**O QUE DIZ**', '', c['o_que_diz'], '', '**O QUE SIGNIFICA**', '', c['o_que_significa'].replace('\n', '\n\n'), '',
                      '**EXEMPLO PRÁTICO**', '', c['exemplo_pratico'], '', '**ATENÇÃO**', '', c['atencao'] or '—', '', '**PALAVRAS DIFÍCEIS**', '']
            lines += [f"- *{t['termo']}*: {t['explicacao']}" for t in c['palavras_dificeis']] or ['—']
            lines += ['', '**CAMADA EXTERNA**', ''] + ([f'- {n}' for n in r['external_layer_notes']] or ['—'])
            lines += ['', '**WARNINGS:** ' + ('; '.join(f"{w['code']} ({w['section']}: {w['detail'][:60]})" for w in warn[r['target_id']])
                                              if warn.get(r['target_id']) else '—')]
            if r['target_id'] in dec:
                d = dec[r['target_id']]
                lines += ['', f"**DECISÃO HUMANA:** {d['decision']} — {d['review_reason']}" +
                          (f" (seções: {', '.join(d['changed_sections'])})" if d['changed_sections'] else '')]
            else:
                lines += ['', '- [ ] APROVAR   - [ ] AJUSTAR   - [ ] REJEITAR']
            lines += ['', '---', '']
    return '\n'.join(lines) + '\n'


def _catalog(ctx):
    """Local curated jurisprudence catalog (official thesis text), keyed by tribunal:tipo:numero."""
    p = ctx.ncfg.get('jurisprudence_catalog')
    path = Path(p) if p and Path(p).is_absolute() else (ctx.base / p if p else None)
    if not path or not path.is_file():
        return {}
    code = {'repercussao_geral': 'RG', 'sumula_vinculante': 'SV'}
    out = {}
    for x in json.loads(path.read_text(encoding='utf-8')):
        key = f"{x['tribunal']}:{code.get(x['tipo'], x['tipo'])}:{x['numero']}"
        out.setdefault(key, []).append(x)
    return out


def _catalog_key(target_id):
    """CF88:ART.231:PAR.1 -> CF88:231:1:-:- (vinculo_id suffix of the curated catalog)."""
    parts = target_id.split(':')
    seg = {p.split('.')[0]: p.split('.', 1)[1] for p in parts[1:] if '.' in p}
    return ':'.join([parts[0], seg.get('ART', '-'), seg.get('PAR', '-'),seg.get('INC', '-'), seg.get('AL', '-')])


def _verify_subject(rec, keywords):
    thesis = (rec.get('tese_ou_resumo') or '')
    low = thesis.lower()
    missing = [k for k in keywords if k.lower() not in low]
    return dict(verified=bool(keywords) and bool(thesis) and not missing, keywords=keywords, missing_keywords=missing,
                catalog_record_id=rec.get('vinculo_id'), thesis_excerpt=thesis[:400] or None,
                official_source_sha256=(rec.get('fonte_oficial') or {}).get('sha256_conteudo'),
                official_source_url=(rec.get('fonte_oficial') or {}).get('url'))


def jurisprudence_recommendations_v2(spec, ctx, local):
    """READY_TO_LINK only with local proof of tribunal + tipo + numero + pertinent subject (keywords found in the local official
    thesis text, and the curated link on the same target). Identity without subject proof -> IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION."""
    cat = _catalog(ctx)
    out = []
    for r in spec.get('jurisprudence_recommendations', []):
        ident = r.get('local_identity') or ''
        found = local.get(ident, [])
        # primary_target_id: the curated link lives on the principal device (e.g. art. 231) and this target is a correlated one
        link_target = r.get('primary_target_id') or r['target_id']
        excluded = {x['target_id'] for x in r.get('excluded_local_links', [])}
        on_target = [f for f in found if f['target_id'] == link_target]
        recs = [x for x in cat.get(ident, []) if x.get('vinculo_id', '').startswith(ident + ':')]
        if r.get('primary_target_id'):  # read the thesis from the catalog record of the principal device
            recs = sorted(recs, key=lambda x: x.get('vinculo_id') != f"{ident}:{_catalog_key(link_target)}")
        ver = _verify_subject(recs[0], r.get('subject_keywords', [])) if recs else None
        if r.get('material_mismatch') and ver and ver['verified']:
            raise BatchError('JURIS_MISMATCH_CONTRADICTED', f"{r['target_id']} {ident}: tese local contem o assunto; revisar material_mismatch")
        if found and on_target and ver and ver['verified']:
            status = 'READY_TO_LINK'
        elif r.get('material_mismatch') and recs:
            # identity exists locally, the local thesis was read and it treats another subject: never link to this target
            status = 'MATERIAL_MISMATCH_EXCLUDED'
        elif found or recs:
            status = 'IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION'
        else:
            status = 'PENDING_EXTERNAL_INGESTION'
        item = dict(target_id=r['target_id'], desired_reference=r['desired_reference'], purpose=r['purpose'],
                    local_identity_searched=r.get('local_identity'), local_record_found=bool(found or recs),
                    local_reference_id=(on_target or found)[0]['reference_id'] if found else None,
                    already_linked_to_target=bool(on_target), subject_verification=ver, status=status)
        if r.get('primary_target_id'):
            item.update(primary_target_id=link_target, correlated_target_id=r['target_id'])
        if r.get('excluded_local_links'):
            # overlay only: the original catalog/export is never edited; the wrong local link is recorded and never used
            item['excluded_local_links'] = [dict(x, local_link_present=any(f['target_id'] == x['target_id'] for f in found),
                                                 status='MATERIAL_MISMATCH_EXCLUDED') for x in r['excluded_local_links']]
            if on_target and on_target[0]['target_id'] in excluded:
                raise BatchError('JURIS_EXCLUDED_LINK_USED', f"{r['target_id']} {ident}")
        if r.get('human_supplied'):
            item['human_supplied'] = r['human_supplied']  # informed by the human review; not a local record
        if status == 'MATERIAL_MISMATCH_EXCLUDED':
            item['material_mismatch'] = r['material_mismatch']
            item['note'] = 'Tese local conferida: trata de outro assunto. Vinculo local existente NAO deve ser usado como jurisprudencia pertinente a este target.'
        elif status == 'PENDING_EXTERNAL_INGESTION':
            item['note'] = 'Registro nao existe no acervo local curado; nada foi fabricado. Requer ingestao oficial.'
        elif status != 'READY_TO_LINK':
            item['note'] = 'Identidade encontrada localmente, mas o assunto/tese nao foi comprovado localmente; nao vincular ainda.'
        out.append(item)
    counts = {k: sum(1 for x in out if x['status'] == k) for k in ('READY_TO_LINK', 'IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION', 'PENDING_EXTERNAL_INGESTION',
                                                                  'MATERIAL_MISMATCH_EXCLUDED')}
    extra = dict(material_mismatch_excluded=counts['MATERIAL_MISMATCH_EXCLUDED']) if counts['MATERIAL_MISMATCH_EXCLUDED'] else {}
    return dict(schema_version=2, batch_id=spec['batch_id'], policy='ENTENDA nao incorpora jurisprudencia; READY_TO_LINK exige tribunal, tipo, numero e assunto comprovados localmente',
                local_sources=[ctx.ncfg.get('reference_export'), ctx.ncfg.get('jurisprudence_catalog')], total=len(out),
                ready_to_link=counts['READY_TO_LINK'], identity_found_pending_subject_verification=counts['IDENTITY_FOUND_PENDING_SUBJECT_VERIFICATION'],
                pending_external_ingestion=counts['PENDING_EXTERNAL_INGESTION'], **extra, recommendations=out)


def jurisprudence_recommendations(spec, ctx):
    """Recommendations only (schema 1: identity match). Schema 2 (report_schema >= 2) also requires subject verification."""
    p = ctx.ncfg.get('reference_export')
    doc = json.loads((ctx.base / p).read_text(encoding='utf-8')) if p else {'references': {}}
    local = {}
    for tid, links in doc['references'].items():
        for l in links:
            if l['reference_type'] == 'JURISPRUDENCE':
                local.setdefault(l['source_id'], []).append(dict(target_id=tid, reference_id=l['reference_id'], label=l['label']))
    if spec.get('report_schema', 1) >= 2:
        return jurisprudence_recommendations_v2(spec, ctx, local)
    out = []
    for r in spec.get('jurisprudence_recommendations', []):
        found = local.get(r.get('local_identity') or '', [])
        on_target = [f for f in found if f['target_id'] == r['target_id']]
        out.append(dict(target_id=r['target_id'], desired_reference=r['desired_reference'], purpose=r['purpose'],
                        local_identity_searched=r.get('local_identity'), local_record_found=bool(found),
                        local_reference_id=(on_target or found)[0]['reference_id'] if found else None,
                        **({'local_label': (on_target or found)[0]['label'],
                            'identity_basis': 'tribunal + tipo + numero (source_id do acervo local curado); tema material nao reverificado localmente'}
                           if found else {}),
                        already_linked_to_target=bool(on_target),
                        status='READY_TO_LINK' if found else 'PENDING_EXTERNAL_INGESTION',
                        note=None if found else 'Registro nao existe no acervo local curado; nada foi fabricado. Requer ingestao oficial.'))
    return dict(schema_version=1, batch_id=spec['batch_id'], policy='ENTENDA nao incorpora jurisprudencia; lista de integracao/revisao',
                local_source=p, total=len(out), ready_to_link=sum(1 for x in out if x['status'] == 'READY_TO_LINK'),
                pending_external_ingestion=sum(1 for x in out if x['status'] == 'PENDING_EXTERNAL_INGESTION'), recommendations=out)


def run(batch_dir, config=HERE / 'entenda_config.json'):
    bd = Path(batch_dir)
    spec = json.loads((bd / 'BATCH_SPEC.json').read_text(encoding='utf-8'))
    if spec.get('superseded_by_final'):
        raise BatchError('BATCH_SUPERSEDED', f"{spec['batch_id']}: evidencia congelada; usar {spec['superseded_by_final']}")
    ctx = E.NormContext(spec['norma_id'], config)
    main_corpus = E.load_corpus(ctx.base / ctx.ncfg['corpus'])
    drafts = json.loads((bd / spec['drafts']).read_text(encoding='utf-8'))
    spec['_drafts'] = drafts
    expected = spec.get('expected_review_status', 'PENDING_HUMAN_REVIEW')
    if drafts['review_status'] != expected or any('review_status' in e for e in drafts['explanations']):
        raise BatchError('BATCH_REVIEW_STATUS_MISMATCH', f"{spec['batch_id']}: esperado {expected}")
    decisions = json.loads((bd / spec['decisions']).read_text(encoding='utf-8')) if spec.get('decisions') else None
    if expected != 'PENDING_HUMAN_REVIEW' and not decisions:
        raise BatchError('BATCH_APPROVAL_WITHOUT_DECISIONS', spec['batch_id'])
    in_scope = lambda t: any(t == a or t.startswith(a + ':') for a in spec['scope'])  # noqa: E731
    reused = [r for r in main_corpus if r['status'] == 'ACTIVE' and in_scope(r['target_id'])]
    if sorted(r['target_id'] for r in reused) != sorted(spec['reused']):
        raise BatchError('BATCH_REUSE_MISMATCH', str(sorted(r['target_id'] for r in reused)))
    if any(r['review_status'] != 'HUMAN_APPROVED_T1' for r in reused):
        raise BatchError('BATCH_REUSED_NOT_APPROVED', spec['batch_id'])
    main_keys = {r['explanation_key'] for r in main_corpus}
    for pc in spec.get('prior_corpora', []):
        main_keys |= {r['explanation_key'] for r in E.load_corpus(ctx.base / pc) if r['status'] == 'ACTIVE'}
    for e in drafts['explanations']:
        if E.explanation_key(e['target_id'], e.get('variant', 'BASE')) in main_keys:
            raise BatchError('BATCH_DUPLICATE_TARGET_EXPLANATION', e['target_id'])
        for t in [e['target_id']] + e.get('covered_targets', []):
            if ctx.effective_status(t) != 'CURRENT':
                raise BatchError('BATCH_NOT_CURRENT', t)
    n_new = len(drafts['explanations'])
    if n_new > spec['hard_cap']:
        (bd / 'BATCH_SPLIT_RECOMMENDED.json').write_text(json.dumps(dict(batch_id=spec['batch_id'], new=n_new, hard_cap=spec['hard_cap']),
                                                                    indent=1) + '\n', encoding='utf-8')
        raise BatchError('BATCH_SPLIT_RECOMMENDED', f'{n_new} > {spec["hard_cap"]}')
    corpus_path = bd / spec['batch_corpus']
    # evidence corpus (pending batch) is immutable input for a final batch; otherwise the batch's own corpus keeps its hashes
    existing = E.load_corpus(ctx.base / spec['supersedes_corpus']) if spec.get('supersedes_corpus') else E.load_corpus(corpus_path)
    stamped = E.stamp(drafts, ctx, existing)
    new = [r for r in stamped if r['status'] == 'ACTIVE']
    if any(r['review_status'] != expected for r in new):
        raise BatchError('BATCH_REVIEW_STATUS_MISMATCH', spec['batch_id'])
    combined = reused + new
    E.validate_corpus(reused + stamped, ctx)
    E.write_corpus(stamped, corpus_path, ctx)
    rows = classify(spec, ctx, reused, new)
    files = E.build_entenda_index(ctx, combined, bd / spec['index_dir'])
    manifest = json.loads((bd / spec['index_dir'] / 'ENTENDA_BUILD_MANIFEST.json').read_text(encoding='utf-8'))
    counts = {}
    for r in rows:
        counts[r['classification']] = counts.get(r['classification'], 0) + 1
    per_new = [p for p in manifest['per_explanation'] if p['target_id'] in {r['target_id'] for r in new}]
    art5 = spec.get('focus_article')
    summary = dict(
        targets_evaluated=len(rows), targets_current=sum(1 for r in rows if r['status'] == 'CURRENT'),
        selected=sum(counts.get(k, 0) for k in SELECTED), by_classification=dict(sorted(counts.items())),
        historical_excluded=counts.get('EXCLUDED_HISTORICAL', 0),
        **({'revoked_excluded': counts['EXCLUDED_REVOKED']} if counts.get('EXCLUDED_REVOKED') else {}), reused_from_pilot=len(reused), new_explanations=len(new),
        batch_total_explanations=len(combined), soft_target=spec['soft_target'], hard_cap=spec['hard_cap'],
        soft_target_status='WITHIN' if spec['soft_target'][0] <= len(new) <= spec['soft_target'][1] else 'OUTSIDE_JUSTIFIED',
        soft_target_justification=spec.get('soft_target_justification'),
        new_words_mean=round(statistics.mean(p['words'] for p in per_new)), new_payload_bytes_mean=round(statistics.mean(p['payload_bytes'] for p in per_new)),
        largest=max(manifest['per_explanation'], key=lambda p: p['payload_bytes']),
        files=files, lookup_rows=manifest['lookup_rows'], targets_with_references=sum(1 for p in manifest['per_explanation'] if p['reference_count']),
        warnings=sum(manifest['warning_counts'].values()), warning_counts=manifest['warning_counts'])
    if art5:
        a5 = [r for r in rows if r['target_id'] == art5 or r['target_id'].startswith(art5 + ':')]
        summary['focus_article'] = dict(target=art5, evaluated=len(a5), own_explanations=sum(1 for r in a5 if r['classification'] in SELECTED),
                                        new_explanations=sum(1 for r in a5 if r.get('explanation_source') == 'BATCH_NEW'),
                                        incisos_evaluated=sum(1 for r in a5 if r['kind'] == 'INCISO'),
                                        no_separate=sum(1 for r in a5 if r['classification'] == 'NO_SEPARATE_EXPLANATION'),
                                        by_classification={k: sum(1 for r in a5 if r['classification'] == k) for k in SELECTED + ('NO_SEPARATE_EXPLANATION',)})
    report = dict(schema_version=1, batch_id=spec['batch_id'], norma_id=spec['norma_id'], scope=spec['scope'], policy='ENTENDA-T1 (semantica)',
                  summary=summary, selection=rows)
    summary['retired_versions'] = sum(1 for r in stamped if r['status'] == 'RETIRED')
    summary['review_status_counts'] = {k: sum(1 for r in combined if r['review_status'] == k) for k in sorted({r['review_status'] for r in combined})}
    juris = jurisprudence_recommendations(spec, ctx)
    summary['jurisprudence_recommendations'] = dict(total=juris['total'], ready_to_link=juris['ready_to_link'],
                                                    pending_external_ingestion=juris['pending_external_ingestion'])
    if spec.get('report_schema', 1) >= 2:
        summary['jurisprudence_recommendations']['identity_found_pending_subject_verification'] = juris['identity_found_pending_subject_verification']
        if juris.get('material_mismatch_excluded'):
            summary['jurisprudence_recommendations']['material_mismatch_excluded'] = juris['material_mismatch_excluded']
        summary.update(targets_structurally_present=sum(1 for r in rows if r['structurally_present']),
                       targets_legally_current=sum(1 for r in rows if r['legally_current']),
                       targets_revoked=sum(1 for r in rows if r['legal_status'] == 'REVOKED'))
        temporal = E.temporal_report(combined, spec['as_of_date'])
        summary['temporal_notes'] = dict(as_of=spec['as_of_date'], total=len(temporal),
                                         not_yet_effective=sum(1 for t in temporal if t['state'] == 'NOT_YET_EFFECTIVE'),
                                         review_due=sum(1 for t in temporal if t['review_due']))
        if temporal:
            (bd / 'TEMPORAL_NOTES.json').write_bytes((json.dumps(dict(schema_version=1, batch_id=spec['batch_id'], as_of=spec['as_of_date'],
                                                                      policy='data explicita (nunca o relogio do sistema); updater revisa quando review_after/future_effective_date chegar',
                                                                      notes=temporal), ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    (bd / 'SELECTION_REPORT.json').write_bytes((json.dumps(report, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    (bd / 'JURISPRUDENCE_LINK_RECOMMENDATIONS.json').write_bytes((json.dumps(juris, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    (bd / spec.get('review_sheet', 'REVIEW_BATCH.md')).write_bytes(review_sheet(spec, ctx, new, rows, manifest, decisions).encode('utf-8'))
    return report


if __name__ == '__main__':
    rep = run(sys.argv[1])
    print(json.dumps(rep['summary'], ensure_ascii=False, indent=1))
