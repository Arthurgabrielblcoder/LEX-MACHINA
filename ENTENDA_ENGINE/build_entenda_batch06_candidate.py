"""Deterministic builder of the ENTENDA Batch06 candidate (CF88 arts. 42-75) from versioned content only.

Replaces the temporary b06_* scripts of the checkpoint. Inputs (all in Git):
  derived/production_batch_06/BATCH_SPEC.json, BATCH_06_DRAFTS.json (editorial source), BATCH06_TARGET_PLAN.json (vigency annotations),
  EDITORIAL_REVIEW_INPUT.json (fact rules, technical terms, editor resolutions; its "risk" block is regenerated here),
  BATCH06_RELATIONS_PIN.json (Relations Engine evidence), PRE_RECALIBRATION_MANIFEST.json (checkpoint queues, for the migration report);
  editorial/T1_EXTERNAL_CATALOG.json, T1_KNOWN_RESOLUTIONS.json, T1_PIPELINE_CONFIG.json, T1_SEMANTIC_AMBIGUITY_REGISTRY.json;
  CF88 text: updater/saida (git-ignored) or its byte-exact reconstruction (text_source_reconstruction.py, sha256 verified).
Steps: production_batch (SELECT/SKIP, stamping, index, review sheet) -> risk map (t1_risk.assess/complexity on validator v3) ->
editorial_checks -> triage A-E (t1_batch_packets) -> packets -> scale report -> manifest.
The candidate corpus is regenerated from the drafts on every build (none of its explanations was human-reviewed, so there is no version
chain to keep); nothing is approved: AUTO_APPROVE_* stay OFF and every explanation stays PENDING_HUMAN_REVIEW.
Usage:
  python build_entenda_batch06_candidate.py                      build in place
  python build_entenda_batch06_candidate.py --determinism 3      + 3 builds in temporary copies; writes DETERMINISM_EVIDENCE.json
"""
import hashlib
import json
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import editorial_checks as EC  # noqa: E402
import entenda_engine as E  # noqa: E402
import production_batch as PB  # noqa: E402
import t1_batch_packets as BP  # noqa: E402
import t1_risk as R  # noqa: E402
import t1_validator_v2 as V  # noqa: E402
import t1_validator_v3 as V3  # noqa: E402
import text_source_reconstruction as TSR  # noqa: E402

BD = HERE / 'derived/production_batch_06'
INPUTS = ('BATCH_SPEC.json', 'BATCH_06_DRAFTS.json', 'BATCH06_TARGET_PLAN.json', 'EDITORIAL_REVIEW_INPUT.json', 'BATCH06_RELATIONS_PIN.json',
          'PRE_RECALIBRATION_MANIFEST.json', 'RECALIBRATION_EDITORIAL_LOG.json', 'ROUND_0_EDITORIAL_LOG.json')
GENERATED = ('CF88_BATCH_06.entenda.jsonl', 'index/ENTENDA_BUILD_MANIFEST.json', 'index/ENTENDA_LOOKUP.IDX', 'index/ENTENDA_PAYLOAD.DAT',
             'SELECTION_REPORT.json', 'JURISPRUDENCE_LINK_RECOMMENDATIONS.json', 'REVIEW_BATCH_06.md', 'EDITORIAL_REVIEW_INPUT.json',
             'EDITORIAL_CHECKS.json', 'REVIEW_BATCH_06_RISK_TRIAGE.md', 'BATCH06_TRIAGE.json', 'BATCH06_COMPACT_CLEAN_REVIEW.md',
             'BATCH06_QUICK_REVIEW.md', 'BATCH06_FULL_HUMAN_REVIEW.md', 'BATCH06_D_ESCALATION_DIAGNOSTIC.md', 'BATCH06_HARD_FAIL_REPORT.md',
             'MICRO_ADJUSTMENTS_LOG.json', 'BATCH06_SCALE_REPORT.md', 'BATCH06_MANIFEST.json')
GLOBAL_INPUTS = ('ENTENDA_ENGINE/editorial/T1_EXTERNAL_CATALOG.json', 'ENTENDA_ENGINE/editorial/T1_KNOWN_RESOLUTIONS.json',
                 'ENTENDA_ENGINE/editorial/T1_PIPELINE_CONFIG.json', 'ENTENDA_ENGINE/editorial/T1_SEMANTIC_AMBIGUITY_REGISTRY.json',
                 'ENTENDA_ENGINE/editorial/TEXT_SOURCE_RECONSTRUCTION.json', 'ENTENDA_ENGINE/entenda_config.json',
                 'LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json', 'LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS.json',
                 'updater/fontes_oficiais_senado/CF88/16434817_5beff7a4/normalizado.txt')
CHECKPOINT_PRESENTED = 265430
ORIGIN = {}


def _n(x):
    return f'{x:,}'.replace(',', '.')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_lf(p):
    """Hash of a text input/code file with CRLF folded to LF (stable under core.autocrlf checkouts without an eol rule)."""
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def _json(p, doc):
    Path(p).write_bytes((json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))


def text_source_status(ctx):
    out = {}
    for src in ctx.ncfg['text_sources']:
        if 'CF88' not in src['namespaces']:
            continue  # only the source the batch records are stamped from (ADCT fallback bytes depend on the checkout's eol)
        info = next((v for v in ctx.text_source.values() if v['path'] == src['path']), None)
        present = (ctx.base / src['path']).is_file()
        out[src['path']] = dict(sha256=info['file_sha256'] if info else None, reconstructible_from_git=src['path'] in TSR.recipes())
        ORIGIN[src['path']] = 'ARQUIVO_LOCAL' if present else 'RECONSTRUIDO_DO_GIT (sha256 conferido)'  # not written: environment-dependent
    return out


def batch05_regression(ctx, catalog):
    """Read-only: v2 x v3 on the Batch05 v1 texts that humans sent back (true positives) or approved unchanged (alerts = noise)."""
    import t1_triage as T
    b5 = HERE / 'derived/production_batch_05'
    spec = V.load_json(b5 / 'BATCH_SPEC.json')
    v1 = {r['target_id']: r for r in E.load_corpus(b5 / spec['batch_corpus']) if r['editorial_version'] == 1}
    dec = T._rounds(b5)
    adj = sorted(d['target_id'] for d in dec if d['decision'] != 'APPROVED')
    same = sorted(d['target_id'] for d in dec if d['decision'] == 'APPROVED')
    flag2 = {t: {f['code'] for f in V.validate(v1[t], ctx, catalog, {}) if f['severity'] in ('REVIEW_REQUIRED', 'HARD_FAIL')} for t in adj + same}
    flag3 = {t: {f['code'] for f in V3.validate(v1[t], ctx, catalog, {}) if f['severity'] in ('REVIEW_REQUIRED', 'HARD_FAIL')} for t in adj + same}
    return dict(changes_requested_v1=len(adj), true_positives_v2=sum(1 for t in adj if flag2[t]), true_positives_v3=sum(1 for t in adj if flag3[t]),
                lost_by_v3=[t for t in adj if flag2[t] and not flag3[t]], gained_by_v3=[t for t in adj if flag3[t] and not flag2[t]],
                approved_unchanged_v1=len(same), flagged_v2=sum(1 for t in same if flag2[t]), flagged_v3=sum(1 for t in same if flag3[t]),
                new_codes_on_approved_unchanged=dict(sorted(Counter(c for t in same for c in flag3[t] - flag2[t]).items())))


def build(bd=BD):
    bd = Path(bd)
    for n in ('CF88_BATCH_06.entenda.jsonl', 'index/ENTENDA_BUILD_MANIFEST.json', 'index/ENTENDA_LOOKUP.IDX', 'index/ENTENDA_PAYLOAD.DAT'):
        (bd / n).unlink(missing_ok=True)                     # candidate corpus is regenerated from the drafts (no reviewed version)
    sel = PB.run(bd)
    ctx = E.NormContext('CF88')
    catalog, known, registry = V.load_catalog(), V.load_json(V.KNOWN), V3.load_registry()
    pin = V.load_json(bd / 'BATCH06_RELATIONS_PIN.json')
    pre = V.load_json(bd / 'PRE_RECALIBRATION_MANIFEST.json')
    c = BP.Context(bd, ctx, catalog, known, registry, pin)
    inp = V.load_json(bd / 'EDITORIAL_REVIEW_INPUT.json')
    inp['risk_criteria'] = dict(classifier='ENTENDA_ENGINE/t1_risk.py::assess + complexity (validator v3)',
                                LEGAL_RISK='HIGH: ' + '; '.join(R.LEGAL_HIGH) + '. MEDIUM: jurisprudencia so de contexto, questao interpretativa '
                                'remetida, tema sensivel, dependencia externa nao material. LOW: o restante.',
                                VERIFICATION_COMPLEXITY='EXTERNAL: dependencia/nota externa; STRUCTURED: numero, prazo, quorum, lista, bloco, '
                                'remissao, excecao, lei, emenda; SIMPLE: o restante. Nao altera LEGAL_RISK.',
                                level='o campo level e o LEGAL_RISK')
    inp['risk'] = BP.risk_input(c)
    _json(bd / 'EDITORIAL_REVIEW_INPUT.json', inp)
    EC.run(bd)
    doc = BP.triage(c, pre.get('queues_by_target'))
    files, full_generated = BP.packets(doc, c)
    for n in ('BATCH06_FULL_HUMAN_REVIEW.md', 'BATCH06_D_ESCALATION_DIAGNOSTIC.md'):
        if n not in files:
            (bd / n).unlink(missing_ok=True)
    doc['metrics'] = BP.metrics(doc, c, files)
    doc['metrics']['checkpoint_presented_chars'] = CHECKPOINT_PRESENTED
    doc['d_full_package'] = 'GERADO' if full_generated else 'NAO_GERADO (diagnostico de escalonamento)'
    micro = BP.micro_auto(doc, c.cfg)
    doc['micro_adjustments'] = dict(applied=micro['applied'], eligible=micro['eligible'], microauto_apply=micro['microauto_apply'])
    doc['human_approved_t1_granted'] = 0
    doc['text_source'] = text_source_status(ctx)
    doc['relations_pin'] = dict(file='BATCH06_RELATIONS_PIN.json', coverage=pin['coverage'])
    doc['validator_limits'] = V3.LIMITS
    doc['validator_v3_regression_batch05'] = batch05_regression(ctx, catalog)
    for name, text in files.items():
        (bd / name).write_bytes(text.encode('utf-8'))
    _json(bd / 'MICRO_ADJUSTMENTS_LOG.json', micro)
    _json(bd / 'BATCH06_TRIAGE.json', doc)
    (bd / 'BATCH06_SCALE_REPORT.md').write_bytes(scale_report(doc, sel, c, pre).encode('utf-8'))
    manifest(bd, doc, sel)
    return doc


def scale_report(doc, sel, c, pre):
    s, m, mig = sel['summary'], doc['metrics'], doc.get('migration', {})
    rows = doc['rows']
    sb = {}
    for r in sel['selection']:
        if r['status'] != 'CURRENT':
            continue
        k = BP._sub_block(c.spec, r['target_id'])
        cur = sb.setdefault(k, Counter())
        cur['current'] += 1
        cur['new' if r.get('explanation_source') == 'BATCH_NEW' else 'reused' if r.get('explanation_source') else 'skip'] += 1
    rec = json.loads((c.bd / 'RECALIBRATION_EDITORIAL_LOG.json').read_text(encoding='utf-8'))
    L = [f"# {c.spec['batch_id']} — relatório de escala (recalibração de risco)", '',
         f"Data de referência: {c.spec['as_of_date']} · gerado por `ENTENDA_ENGINE/build_entenda_batch06_candidate.py` (determinístico, só conteúdo "
         'versionado) · **WIP: nenhum ENTENDA do Batch06 aprovado** (0 HUMAN_APPROVED_T1 novos; AUTO_APPROVE_LOW/MEDIUM e MICROAUTO_APPLY OFF).', '',
         '## Seleção', '', '| | |', '|---|---|',
         f"| Targets analisados | {s['targets_evaluated']} ({s['targets_current']} vigentes + {s['historical_excluded']} históricos excluídos) |",
         f"| SELECT | {s['selected']} = {s['new_explanations']} explicações novas + {s['reused_from_pilot']} pilotos reutilizados |",
         f"| SKIP | {s['by_classification'].get('NO_SEPARATE_EXPLANATION', 0)} (todos com motivo e explicação que os cobre) |",
         '| Sub-blocos (vigentes / novas / reutilizadas / SKIP) | ' + ' · '.join(f"{k} {v['current']}/{v['new']}/{v['reused']}/{v['skip']}"
                                                                         for k, v in sorted(sb.items())) + ' |',
         f"| Papéis das novas | {', '.join(f'{k} {v}' for k, v in sorted(Counter(x['role'] for x in rows).items()))} |", '',
         '## Dois eixos', '',
         '- **LEGAL_RISK** — há risco real de interpretação jurídica incorreta?',
         '- **VERIFICATION_COMPLEXITY** — quão difícil é verificar o draft deterministicamente?',
         'Número, percentual, prazo, idade, votos, quórum, BLOCK, lista, artigo longo, remissão simples, dependência de lei e emenda '
         'constitucional elevam só a complexidade.', '',
         '| LEGAL_RISK | Itens | | VERIFICATION_COMPLEXITY | Itens |', '|---|---|---|---|---|']
    for a, b in zip(('LOW', 'MEDIUM', 'HIGH'), ('SIMPLE', 'STRUCTURED', 'EXTERNAL')):
        L.append(f"| {a} | {doc['legal_risk_counts'].get(a, 0)} | | {b} | {doc['complexity_counts'].get(b, 0)} |")
    L += ['', f"Jurisprudência: {', '.join(f'{k} {v}' for k, v in sorted(doc['jurisprudence_counts'].items()))} "
          '(CONTEXT_ONLY não gera D; REQUIRED_FOR_CORRECTNESS é gatilho de D).', '',
          '## Filas', '', '| Fila | Agora | Checkpoint |', '|---|---|---|']
    prev = mig.get('previous_counts', {})
    for q in BP.QUEUES:
        L.append(f"| {q} | {doc['counts'][q]} | {prev.get(q, 0)} |")
    L += ['', f"Risco no checkpoint: {', '.join(f'{k} {v}' for k, v in sorted(mig.get('previous_risk_counts', {}).items()))}.", '',
          f"**Migração dos {mig.get('previous_D', 0)} D antigos:** {mig.get('previous_D_migrated', 0)} saíram de D → "
          + ', '.join(f'{k} {v}' for k, v in sorted(mig.get('previous_D_now', {}).items())) + '.', '',
          '## Motivos dos D restantes', '']
    L += [f"- {k}: {v}" for k, v in doc['d_reasons'].items()]
    L += [''] + [f"- `{x['target_id']}` — {'; '.join(x['legal_reasons']) or x['reason']}" for x in rows if x['queue'] == 'D_FULL_HUMAN_REVIEW']
    L += ['', '## Achados que ainda pedem revisão (REVIEW_REQUIRED)', '']
    L += [f"- {k}: {v}" for k, v in doc['finding_counts'].items()] or ['- nenhum']
    L += ['', '## Falsos positivos corrigidos por regra geral (validator v3)', '']
    L += [f"- {k}: {v} alerta(s) rebaixado(s) para INFO" for k, v in doc['refined_false_positive_counts'].items()] or ['- nenhum']
    L += ['- "incentivo(s)" como substantivo do próprio texto ou como matéria da lei não é teleologia; "todos os"/"só pode" que reproduzem '
          'quórum/condição explícitos não são universalização; "automaticamente" expresso no artigo não é consequência inventada.',
          '- Rótulo truncado do fato externo ("Lei Complementar nº 7") passa a mostrar a identificação inteira; fato só na camada externa '
          'vai para C (o núcleo T1 não depende dele).', '',
          '## Correções editoriais desta rodada (ROUND_0B)', '',
          f"{len(rec['edits'])} edições em {len(rec['targets'])} explicações: " + ', '.join(f'{k} {v}' for k, v in sorted(rec['counts'].items()))
          + ' (antes/depois em `RECALIBRATION_EDITORIAL_LOG.json`).', '',
          '## Volume para o humano', '', '| Métrica | Caracteres |', '|---|---|',
          f"| Rascunhos (5 seções + glossário) | {_n(m['total_draft_chars'])} |",
          f"| Modelo antigo (pacote completo de todos os itens) | {_n(m['old_model_full_package_chars'])} |",
          f"| Checkpoint (pacotes apresentados, D=89) | {_n(m['checkpoint_presented_chars'])} |",
          f"| **Agora (pacotes apresentados)** | **{_n(m['presented_chars'])}** |"]
    L += [f"| — {k} | {_n(v)} |" for k, v in m['presented_by_file'].items()]
    L += [f"| Redução vs. modelo antigo | {_n(m['reduction_abs'])} ({m['reduction_pct']}%) |",
          f"| Redução vs. checkpoint | {_n(m['checkpoint_presented_chars'] - m['presented_chars'])} "
          f"({round(100 * (1 - m['presented_chars'] / m['checkpoint_presented_chars']), 1)}%) |", '',
          f"Pacote D: {doc['d_full_package']} (limite do diagnóstico: {int(BP.D_DIAGNOSTIC_THRESHOLD * 100)}% em D).", '',
          '## Dependências externas', '']
    L += [f"- `{x['target_id']}`: {', '.join(x['external_dependency'])}" + (f" · resolver {x['external_resolution']['status']} via "
                                                                             f"{x['external_resolution']['via']}" if x.get('external_resolution') else '')
          for x in rows if x['external_dependency'] and any(not d.startswith('JURISPRUD') for d in x['external_dependency'])] or ['- nenhuma']
    L += ['', '## Reprodutibilidade', '',
          '- Texto CF/ADCT (sha256 dos bytes lidos, idêntico com arquivo local ou reconstrução do Git): '
          + '; '.join(f"`{k.split('/')[-1]}` {v['sha256'][:16]}…" + (' (reconstruível do Git)' if v['reconstructible_from_git'] else ' (versionado)')
                      for k, v in doc['text_source'].items()) + '.',
          '- Relations Engine: `BATCH06_RELATIONS_PIN.json` (cobertura parcial: só a relação consultada no checkpoint; atualização do pin '
          'para todo o escopo = NOT_RUN_CLOUD_MISSING_LOCAL_DEPENDENCY).',
          '- Determinismo: `python ENTENDA_ENGINE/build_entenda_batch06_candidate.py --determinism 3` (evidência em `DETERMINISM_EVIDENCE.json`).',
          '', '## Regressão do validator v3 contra as decisões humanas do Batch05 (só leitura)', '']
    g = doc['validator_v3_regression_batch05']
    L += [f"- v1 devolvidas pelo humano: {g['changes_requested_v1']} · detectadas v2 {g['true_positives_v2']} · v3 {g['true_positives_v3']} "
          f"(perdidas pelo v3: {', '.join(g['lost_by_v3']) or 'nenhuma'}; ganhas: {', '.join(g['gained_by_v3']) or 'nenhuma'}).",
          f"- v1 aprovadas sem mudança: {g['approved_unchanged_v1']} · com alerta v2 {g['flagged_v2']} · v3 {g['flagged_v3']} (custo em ruído dos "
          f"detectores novos: {', '.join(f'{k} {v}' for k, v in g['new_codes_on_approved_unchanged'].items()) or 'nenhum'}).",
          '', '## Limites do validador', ''] + [f'- {x}' for x in V3.LIMITS]
    return '\n'.join(L) + '\n'


def manifest(bd, doc, sel):
    root = HERE.parent
    files = {n: sha(bd / n) for n in INPUTS + GENERATED if (bd / n).is_file() and n != 'BATCH06_MANIFEST.json'}
    _json(bd / 'BATCH06_MANIFEST.json', dict(
        schema_version=2, batch_id=doc['batch_id'], as_of=doc['as_of'], status='WIP_CANDIDATE: 0 HUMAN_APPROVED_T1; nada aprovado; triagem recalibrada',
        builder='ENTENDA_ENGINE/build_entenda_batch06_candidate.py', validator=doc['validator'],
        selection=dict(targets_evaluated=sel['summary']['targets_evaluated'], current=sel['summary']['targets_current'],
                       selected=sel['summary']['selected'], new=sel['summary']['new_explanations'], reused=sel['summary']['reused_from_pilot'],
                       skip=sel['summary']['by_classification'].get('NO_SEPARATE_EXPLANATION', 0), by_classification=sel['summary']['by_classification']),
        queues=doc['counts'], legal_risk=doc['legal_risk_counts'], verification_complexity=doc['complexity_counts'], metrics=doc['metrics'],
        text_source=doc['text_source'], inputs_global_sha256_lf={p: sha_lf(root / p) for p in GLOBAL_INPUTS},
        code_sha256_lf={p: sha_lf(HERE / p) for p in ('build_entenda_batch06_candidate.py', 't1_batch_packets.py', 't1_risk.py', 't1_validator_v3.py',
                                         't1_validator_v2.py', 't1_triage.py', 't1_external_resolver.py', 'editorial_checks.py', 'production_batch.py',
                                         'entenda_engine.py', 'text_source_reconstruction.py')},
        files=files))


def determinism(n=3):
    """n full builds in temporary copies of the inputs; every generated file must be byte-identical across builds and to the in-place build."""
    runs = []
    with tempfile.TemporaryDirectory(prefix='b06_det_') as tmp:
        for i in range(n):
            td = Path(tmp) / f'run{i}' / 'production_batch_06'
            td.mkdir(parents=True)
            for f in INPUTS:
                shutil.copy(BD / f, td / f)
            shutil.copy(BD / 'EDITORIAL_REVIEW_INPUT.json', td / 'EDITORIAL_REVIEW_INPUT.json')
            build(td)
            runs.append({f: sha(td / f) for f in GENERATED if (td / f).is_file()})
    inplace = {f: sha(BD / f) for f in GENERATED if (BD / f).is_file()}
    differing = sorted({f for r in runs for f in set(r) | set(inplace) if r.get(f) != inplace.get(f)})
    ev = dict(schema_version=2, batch_id='ENTENDA_CF_PRODUCTION_BATCH_06', runs=n, byte_identical=not differing, differing_files=differing,
              files=len(inplace), sha256=dict(sorted(inplace.items())),
              procedure=f'{n} builds completos em copias temporarias das entradas versionadas (build_entenda_batch06_candidate.build), '
                        'comparados entre si e com o build no lugar',
              excluded='BATCH06_MANIFEST.json registra hashes de codigo e entradas, tambem comparado; DETERMINISM_EVIDENCE.json nao se auto-inclui')
    _json(BD / 'DETERMINISM_EVIDENCE.json', ev)
    return ev


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    d = build()
    out = dict(text_source_origin=ORIGIN, counts=d['counts'], legal_risk=d['legal_risk_counts'], complexity=d['verification_complexity'] if 'verification_complexity' in d
               else d['complexity_counts'], migration=d.get('migration'), d_reasons=d['d_reasons'], metrics=d['metrics'])
    if '--determinism' in sys.argv:
        ev = determinism(int(sys.argv[sys.argv.index('--determinism') + 1]))
        out['determinism'] = dict(runs=ev['runs'], byte_identical=ev['byte_identical'], differing=ev['differing_files'])
    print(json.dumps(out, ensure_ascii=False, indent=1))
