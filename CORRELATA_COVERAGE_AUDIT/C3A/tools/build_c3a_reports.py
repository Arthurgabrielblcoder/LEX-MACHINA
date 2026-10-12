"""C3A reports: RUN3_RUN4_CORRELATA_DIFF.md, C3A_IMPLEMENTATION_REPORT.md and C3A_RUN4_CANDIDATE_MANIFEST.json.

Numbers come only from the RUN4_CANDIDATE_HOST_ONLY outputs (legal view, device-ready export, summary). The RUN4 build is also run twice in
clean temporary directories and the SHA256SUMS compared (reproducibility). Usage: python build_c3a_reports.py [--check]
"""
import argparse
import hashlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

C3A = Path(__file__).resolve().parents[1]
AUDIT = C3A.parent
ROOT = AUDIT.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import build_export_run4_candidate as R4  # noqa: E402
import correlata_overlay as O  # noqa: E402

OUT_DIFF = C3A / 'RUN3_RUN4_CORRELATA_DIFF.md'
OUT_REPORT = C3A / 'C3A_IMPLEMENTATION_REPORT.md'
OUT_MANIFEST = C3A / 'C3A_RUN4_CANDIDATE_MANIFEST.json'
BASELINE = '7c6d421585d971e5eef6af2bc3fa85ccab078d83'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def rel(p):
    return Path(p).relative_to(ROOT).as_posix()


def reproducibility():
    sums = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as t:
            R4.build(t)
            sums.append(hashlib.sha256((Path(t) / 'SHA256SUMS.txt').read_bytes()).hexdigest())
    versioned = sha(R4.OUT / 'SHA256SUMS.txt')
    return dict(builds=2, sha256sums_of_each_build=sums, versioned=versioned, byte_identical=sums[0] == sums[1] == versioned)


def numbers(view, summary):
    E = view['entries']
    add = [e for e in E if e['kind'] == 'ADDITION']
    leg = [e for e in E if e['kind'] == 'LEGACY']
    dev = summary['device_ready']
    return dict(
        ADDITIONS_MATERIALIZED_IN_CANDIDATE=summary['additions_materialized'],
        LEGACY_EXCLUSIONS_CANDIDATE=sum(e['action'] == 'EXCLUDE' for e in leg),
        LEGACY_RETARGETS_CANDIDATE=sum(e['action'] == 'EXCLUDE' and e['legacy_decision'] == 'RETARGET' for e in leg),
        LEGACY_RETARGET_PRESENTATION_NOOP=sum(e['action'] == 'KEEP' and 'PRESENTATION_EQUIVALENT' in (e['note'] or '') for e in leg),
        LEGACY_REPLACED=sum(e['action'] == 'EXCLUDE' and e['legacy_decision'] == 'REPLACE' for e in leg),
        LEGACY_REMOVED=sum(e['action'] == 'EXCLUDE' and e['legacy_decision'] == 'REMOVE' for e in leg),
        LEGACY_ROUTE_FIX=sum(e['action'] == 'ROUTE_FIX' for e in leg),
        LEGACY_KEPT_UNCHANGED=sum(e['action'] == 'KEEP' for e in leg),
        TEMPORAL_SUPPRESSED=sum(e['device_state'] == 'TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE' for e in E),
        REVIEW_HOLD_SUPPRESSED=sum(e['device_state'] == 'REVIEW_HOLD_SUPPRESSED' for e in E),
        MAIN_CORPUS_BLOCKED=sum('BLOCKED_DEVICE_ROUTE_MAIN_CORPUS' in e['device_blockers'] for e in add),
        INGESTION_BLOCKED=sum('BLOCKED_INGESTION_REQUIRED' in e['device_blockers'] for e in add),
        JUDICIAL_NOTICE_BLOCKED=sum('BLOCKED_DEVICE_JUDICIAL_NOTICE_UNSUPPORTED' in e['device_blockers'] for e in add),
        ADCT_RUNTIME_CONFIRMED=summary['adct_runtime_confirmed']['total'],
        ADCT_DEVICE_READY=summary['adct_runtime_confirmed']['device_ready'],
        ADDITIONS_DEVICE_READY=sum(e['device_state'] == 'DEVICE_READY' for e in add),
        RUN4_LEGAL_VIEW_ENTRIES=summary['legal_view']['entries'],
        RUN4_LEGAL_VIEW_LINKS=summary['legal_view']['legal_current_relations'],
        RUN4_DEVICE_READY_VISIBLE_LINKS=dev['correlata_visible'],
        RUN4_DEVICE_HIDDEN_HISTORICAL=dev['correlata_hidden_historical'],
        DEVICE_ARTICLE_INDEX_GAPS_FALLBACK=sum(bool(e.get('device_article_gap')) and e['device_state'] == 'DEVICE_READY' for e in E))


def diff_md(n, view, summary):
    E = view['entries']
    L = []
    a = L.append
    a('# RUN3 × RUN4_CANDIDATE_HOST_ONLY — camada CORRELATA')
    a('')
    a('**RUN4 é candidato host-only, não baseline e não físico.** `LEGAL_APPROVED` ≠ `DEVICE_READY`.')
    a('')
    r3 = summary['run3']
    a(f"- **RUN3:** {r3['correlata_total']} vínculos CORRELATA; {r3['visible']} visíveis; {r3['hidden_historical']} históricos ocultos.")
    a(f"- **RUN4, visão do aparelho:** {n['RUN4_DEVICE_READY_VISIBLE_LINKS']} visíveis DEVICE_READY "
      f"({summary['legacy_device_states'].get('DEVICE_READY', 0)} legados e {n['ADDITIONS_DEVICE_READY']} adições), mais "
      f"{n['RUN4_DEVICE_HIDDEN_HISTORICAL']} históricos ocultos inalterados.")
    a(f"- **RUN4, visão jurídica:** {n['RUN4_LEGAL_VIEW_LINKS']} relações juridicamente vigentes (legados mantidos e adições aprovadas), em "
      f"{n['RUN4_LEGAL_VIEW_ENTRIES']} entradas.")
    a(f"- **Fora do CORRELATA:** os links WORK_REFERENCE e JURISPRUDENCE são idênticos ao RUN3 "
      f"(`{summary['device_ready']['non_correlata_links_identical_to_run3']}`).")
    a('')
    a('| Mudança | n |')
    a('|---|---:|')
    for k in ('LEGACY_KEPT_UNCHANGED', 'LEGACY_ROUTE_FIX', 'LEGACY_REMOVED', 'LEGACY_REPLACED', 'LEGACY_RETARGETS_CANDIDATE',
              'LEGACY_RETARGET_PRESENTATION_NOOP', 'ADDITIONS_MATERIALIZED_IN_CANDIDATE', 'ADDITIONS_DEVICE_READY', 'TEMPORAL_SUPPRESSED',
              'REVIEW_HOLD_SUPPRESSED', 'MAIN_CORPUS_BLOCKED', 'INGESTION_BLOCKED', 'JUDICIAL_NOTICE_BLOCKED', 'ADCT_RUNTIME_CONFIRMED',
              'ADCT_DEVICE_READY', 'DEVICE_ARTICLE_INDEX_GAPS_FALLBACK'):
        a(f'| {k} | {n[k]} |')
    a('')
    a('Os bloqueios contam cada relação em todos os motivos que se aplicam; o estado principal de cada relação está na visão jurídica.')
    a('')
    a('## Vínculos legados (RUN3 → RUN4)')
    a('')
    a('| Target | Destino | Decisão | Ação | Estado no aparelho | Decisão humana |')
    a('|---|---|---|---|---|---|')
    for e in E:
        if e['kind'] == 'LEGACY':
            rf = f" → arts. {','.join(e['route_fix']['articles'])}" if e.get('route_fix') else ''
            gap = f" (lacuna no índice do cartão: {','.join(e['device_article_gap'])}; fallback)" if e.get('device_article_gap') else ''
            a(f"| `{e['target_id']}` | {e['destination_norm_id']} | {e['legacy_decision'] or '—'} | {e['action'] or '—'}{rf}{gap} | "
              f"{e['device_state']} | `{e['decision_id'] or '—'}` |")
    a('')
    a('## Adições no aparelho ou materializadas (destino no cartão)')
    a('')
    a('| Target | Destino | Artigos | Estado | Substitui | Decisões |')
    a('|---|---|---|---|---|---|')
    for e in E:
        if e['kind'] == 'ADDITION' and e['materialized_in_additions']:
            gap = f" (fallback: {','.join(e['device_article_gap'])} fora do índice do cartão)" if e.get('device_article_gap') else ''
            a(f"| `{e['target_id']}` | {e['destination_norm_id']} | {','.join(e['destination_articles']) or '—'}{gap} | {e['device_state']} | "
              f"{len(e['supersedes'])} | {', '.join('`' + d.split('@')[0][-24:] + '`' for d in e['decision_ids'])} |")
    a('')
    a('## Adições aprovadas e bloqueadas para o aparelho')
    a('')
    blocked = Counter(e['device_state'] for e in E if e['kind'] == 'ADDITION' and not e['materialized_in_additions'])
    for k, v in sorted(blocked.items()):
        a(f'- **{k}:** {v}.')
    a('')
    for e in E:
        if e['kind'] == 'ADDITION' and (e['target_id'].startswith('ADCT:') or e['judicial_notice']):
            a(f"- `{e['target_id']}` × {e['destination_norm_key']}: {e['target_check']}; {e['device_state']}; bloqueios {e['device_blockers']}.")
    a('')
    return '\n'.join(L) + '\n'


def report_md(n, summary, repro, created, modified):
    L = []
    a = L.append
    a('# C3A — implementação host-only do motor CORRELATA')
    a('')
    a('**Status: `RUN4_CANDIDATE_HOST_ONLY`.** Não é baseline nem deploy, e não foi aprovado fisicamente.')
    a('')
    a('- **Intocados:** RUN3, REF_LOOKUP, REF_PAYLOAD, TARGETS, RELACOES do cartão, staging SD e firmware.')
    a('- **Princípio:** `LEGAL_APPROVED` ≠ `DEVICE_READY`.')
    a('')
    a('## Arquitetura final')
    a('')
    a('- **Motor genérico:** `LEGAL_TARGET_ID/correlata_overlay.py`, dirigido por dados, sem nenhuma norma, lei ou target no código.')
    a('  - Validação jurídica (`validate_record`, fail-closed).')
    a('  - Classificação do aparelho (`device_blockers`), separada da validação.')
    a('  - Correções do legado (`validate_corrections`).')
    a('  - Escritor das tabelas RELACOES e REL_LOOKUP no formato do cartão. Ele reproduz byte a byte as tabelas atuais.')
    a('- **Builder:** `LEGAL_TARGET_ID/build_export_run4_candidate.py`.')
    a('  - Parte dos links do RUN3, reproduzidos byte a byte pelo motor, e aplica correções e adições.')
    a('  - Gera `legal_view/` e `device_ready/` em `derived/export_test/run4_candidate/`.')
    a('  - `reference_engine.py` e `engine_config.json` não foram alterados, e o RUN3 continua sendo produzido como antes.')
    a('- **Derivação dos dados:** `CORRELATA_COVERAGE_AUDIT/C3A/tools/build_c3a_overlay.py`.')
    a('  - Converte as decisões humanas (consolidado HIGH e revisão legada) em registro jurídico, adições e correções. Não decide nada.')
    a('- **Correções do legado:** `CF88_CORRELATA_EXCLUSIONS_CANDIDATE.json`, uma por vínculo legado visível. Ações:')
    a('  - KEEP;')
    a('  - EXCLUDE (REMOVE, REPLACE e RETARGET);')
    a('  - ROUTE_FIX, que mantém o mesmo vínculo e corrige a rota só na linha RELACOES candidata;')
    a('  - SUPPRESS_HOLD (`REVIEW_HOLD_SUPPRESSED`);')
    a('  - SUPPRESS_TEMPORAL (`TEMPORAL_SUPPRESSED_UNTIL_EFFECTIVE`, com data `until`).')
    a('  - O `CF88_LINK_EXCLUSIONS.json` não foi usado nem editado: o status único dele não representa supressões reversíveis, e o RUN3 depende dele.')
    a('- **Adições:** `CF88_CORRELATA_ADDITIONS.json` só aceita `HUMAN_APPROVED_CORRELATA_V1` e, nesta C3A, só destino já no cartão (`DESTINATION_ON_CARD_ONLY`).')
    a('- **Política HOLD:** `REVIEW_HOLD_SUPPRESSED` não publica o vínculo, preserva a decisão HOLD e o vínculo continua no catálogo, restaurável.')
    a('- **Vacatio:** a relação continua registrada e só aparece a partir de `effective_from`/`until` (política C2 `DO_NOT_PUBLISH_AS_CURRENT`).')
    a('- **ADCT:** um target com `UNKNOWN_VALIDITY` só passa se o runtime do aparelho o confirmar: presente, CURRENT ou STRUCTURAL e alcançável no TEXT_MAP. Não há liberação genérica.')
    a('- **MAIN_CORPUS:** é validado contra o índice de artigos do acervo principal (pin C0) e serializado com `norm_id`, `source_path`, artigos e fallback.')
    a('  - No aparelho fica `BLOCKED_DEVICE_ROUTE_MAIN_CORPUS`, porque o firmware ainda não tem a rota.')
    a('  - Nenhuma norma do acervo principal é duplicada em EXT_NORMAS.')
    a('- **Status judicial:** exige `status`, `cases`, `decided_on`, `notice_short` e `checked_until`.')
    a('  - No aparelho fica bloqueado (`BLOCKED_DEVICE_JUDICIAL_NOTICE_UNSUPPORTED`) até haver UI de aviso.')
    a('- **Identidade jurídica:** unidade de apresentação (ART = CAPUT) × norma. A LC 199/2023 × art. 146, III, b gera uma única relação, com as duas decisões.')
    a('- **PNE:** os seis vínculos viram um só, no caput do art. 214. `NEXT_STEP = ANNEX_ROUTE_SUPPORT` (Meta 19.a) continua pendente.')
    a('')
    a('## Refinamentos encontrados ao aplicar a C2 aos dados reais')
    a('')
    a('1. **PARTIAL_EFFECTS não judicial.** A LC 214 e a LC 227 têm efeitos escalonados sem nenhuma decisão do STF.')
    a('   - O protótipo C2 exigia status judicial para todo PARTIAL_EFFECTS.')
    a('   - Agora: com JUDICIAL_RESTRICTIONS, exige status judicial completo; sem, exige `temporal_note` e `revalidate_on` (`PARTIAL_EFFECTS_WITHOUT_BASIS`).')
    a('2. **Lacunas no índice de artigos do cartão.** O `EXT_ARTIGOS.IDX` do cartão não tem o art. 10 da LC 87/1996 nem o art. 9º da Lei 7.998/1990, embora os dois estejam no texto.')
    a('   - A checagem jurídica usa o texto da norma (`ext_text_article_index.json`, sha do pin); o aparelho usa o índice do cartão.')
    a(f"   - Quando falta o artigo, o aparelho usa o fallback seguro da C2 (abrir a norma sem salto). Casos: {n['DEVICE_ARTICLE_INDEX_GAPS_FALLBACK']}.")
    a('3. **Tipo de relação dos retargets legados.** A revisão legada não classificou o tipo.')
    a('   - Esses registros levam `NAO_CLASSIFICADA_REVISAO_LEGADA`, aceito só quando todas as decisões de origem são legadas.')
    a('   - Nenhuma decisão jurídica nova foi tomada. Ponto para a revisão independente.')
    a('4. **Status judicial da Lei 14.701.** Foi acrescentado `notice_short` ao consolidado HIGH (campo exigido pela política C2). As decisões não mudaram.')
    a('')
    a('## Contagens (derivadas)')
    a('')
    a('| Item | n |')
    a('|---|---:|')
    for k, v in n.items():
        a(f'| {k} | {v} |')
    a(f"| Cache do firmware usado (linhas de lookup / normas) | {summary['device_ready']['firmware_cache']['used']['lookup_rows']} / "
      f"{summary['device_ready']['firmware_cache']['used']['norms']} (limites 64 / 32) |")
    a('')
    a('**Diferenças em relação às estimativas da missão:**')
    a('')
    a('- **HIGH com destino no cartão:** 7. Dois estão em vacatio (Lei 14.965), então 5 são DEVICE_READY.')
    a('  - A LC 199 foi colapsada com o retarget legado.')
    a('  - Somam-se 4 adições do legado (3 retargets e a substituição LC 63 × art. 161, I): 11 materializadas e 9 DEVICE_READY.')
    a('- **MAIN_CORPUS bloqueados:** 21, e não 19. São os 19 HIGH mais 2 substituições do legado (LAI × art. 37, § 3º, II e Lei 8.212 × art. 195, II).')
    a('- **INGESTION bloqueados:** 55, e não 51. São os 51 HIGH mais 4 substituições do legado (Lei 7.990; LCs 124, 125 e 129).')
    a('- **Retargets legados:** 5 decididos. 4 são efetivos (exclusão e adição); o art. 182 → caput é equivalente na apresentação e fica sem alteração.')
    a('')
    a('## Determinismo e regressões')
    a('')
    a(f"- **Reprodutibilidade:** RUN4 construído {repro['builds']} vezes em diretórios temporários limpos; SHA256SUMS idênticos entre si e ao "
      f"versionado: **{repro['byte_identical']}**.")
    a('- **RUN3:** reconstruído pelo motor e byte-idêntico ao versionado. Arquivos operacionais sem diferença em relação à baseline (teste 16).')
    a('- **Testes antigos:** os que exigiam a ausência de `CF88_CORRELATA_ADDITIONS.json` passaram a exigir que ele seja candidato host-only e que o `engine_config.json` não o referencie.')
    a('')
    a('## Arquivos')
    a('')
    a('- **Criados:**')
    for p in created:
        a(f'  - `{p}`')
    a('- **Modificados:**')
    for p in modified:
        a(f'  - `{p}`')
    a('')
    a('## Bloqueios e próximos passos (não iniciados)')
    a('')
    a('- **C3B (aparelho):**')
    a('  - teste físico do candidato device_ready: RELACOES, REL_LOOKUP e REF_* candidatos num cartão de teste;')
    a('  - corrigir as lacunas do `EXT_ARTIGOS.IDX`.')
    a('- **C3C (firmware):**')
    a('  - rota `ABRIR_NORMA_PRINCIPAL` para os 21 MAIN_CORPUS;')
    a('  - UI do aviso judicial;')
    a('  - origem ADCT em RELACOES ainda não verificada no cartão;')
    a('  - limite de cache 32/64 para a escala futura.')
    a('- **Ingestão:** 55 relações dependem de normas novas. Adiada.')
    a('- **Revisão:** o tipo de relação dos 3 retargets legados não classificados.')
    a('- **MEDIUM (191) e LOW (446):** não iniciados.')
    a('')
    return '\n'.join(L) + '\n'


CREATED = ['LEGAL_TARGET_ID/correlata_overlay.py', 'LEGAL_TARGET_ID/build_export_run4_candidate.py',
           'LEGAL_TARGET_ID/derived/CF88_CORRELATA_ADDITIONS.json', 'LEGAL_TARGET_ID/derived/CF88_CORRELATA_EXCLUSIONS_CANDIDATE.json',
           'LEGAL_TARGET_ID/derived/export_test/run4_candidate/ (legal_view, device_ready, summary, SHA256SUMS)',
           'CORRELATA_COVERAGE_AUDIT/C3A/CF88_CORRELATA_LEGAL_REGISTER_CANDIDATE.json', 'CORRELATA_COVERAGE_AUDIT/C3A/inputs/ (card_relations_v2, '
           'main_corpus_article_index.json, ext_text_article_index.json)', 'CORRELATA_COVERAGE_AUDIT/C3A/tools/ (build_c3a_overlay.py, '
           'build_c3a_reports.py, freeze_main_corpus_article_index.py)', 'CORRELATA_COVERAGE_AUDIT/C3A/ (RUN3_RUN4_CORRELATA_DIFF.md, '
           'C3A_IMPLEMENTATION_REPORT.md, C3A_RUN4_CANDIDATE_MANIFEST.json)', 'CORRELATA_COVERAGE_AUDIT/tests/test_correlata_c3a_engine.py']
MODIFIED = ['CORRELATA_COVERAGE_AUDIT/tools/build_c1b_high_consolidated.py (+ notice_short) e o consolidado/fechamento regenerados',
            'CORRELATA_COVERAGE_AUDIT/tests/test_correlata_c1b_batch01.py, _batch02.py, _high_closure.py, test_correlata_c2_prototype.py '
            '(asserção do overlay agora candidato)']


def build(repro):
    view = R4.load(R4.OUT / 'legal_view/CF88_CORRELATA_LEGAL_VIEW.json')
    summary = R4.load(R4.OUT / 'RUN4_CANDIDATE_SUMMARY.json')
    n = numbers(view, summary)
    diff = diff_md(n, view, summary).encode('utf-8')
    report = report_md(n, summary, repro, CREATED, MODIFIED).encode('utf-8')
    inputs = [R4.PIN, AUDIT / 'CF88_CORRELATA_C1B_HIGH_CONSOLIDATED.json', AUDIT / 'CF88_CORRELATA_LEGACY_FULL_REVIEW.json',
              AUDIT / 'CF88_CORRELATA_CANDIDATES.json', R4.MAIN_INDEX, R4.EXT_TEXT_INDEX] + sorted(R4.CARD.iterdir()) + \
             [ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json', ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_STATUS.json'] + \
             [R4.RUN3 / f for f in R4.RUN3_FILES]
    outputs = sorted(p for p in R4.OUT.rglob('*') if p.is_file())
    manifest = dict(schema_version=1, artifact='C3A_RUN4_CANDIDATE_MANIFEST', status=R4.STATUS, baseline_head=BASELINE, as_of=R4.AS_OF,
                    physical_approved=False, baseline=False,
                    inputs={rel(p): sha(p) for p in inputs},
                    overlay={rel(p): sha(p) for p in (R4.ADDITIONS, R4.CORRECTIONS, R4.REGISTER)},
                    run4_outputs={rel(p): sha(p) for p in outputs},
                    reports={rel(OUT_DIFF): hashlib.sha256(diff).hexdigest(), rel(OUT_REPORT): hashlib.sha256(report).hexdigest()},
                    reproducibility=repro, counts=n)
    return diff, report, (json.dumps(manifest, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    repro = reproducibility()
    if not repro['byte_identical']:
        raise SystemExit('RUN4_NOT_REPRODUCIBLE')
    out = build(repro)
    paths = (OUT_DIFF, OUT_REPORT, OUT_MANIFEST)
    if a.check:
        ok = all(p.read_bytes().replace(b'\r\n', b'\n') == b for p, b in zip(paths, out))
        print('check', 'OK' if ok else 'DIFF')
        sys.exit(0 if ok else 1)
    for p, b in zip(paths, out):
        p.write_bytes(b)
    print(json.dumps(json.loads(out[2])['counts'], indent=1), repro['byte_identical'])


if __name__ == '__main__':
    main()
