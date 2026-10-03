"""Reference Engine RUN3 (REFERENCE_EXPANSION_01): RUN2 + the human-approved WORK_REFERENCE overlay. CANDIDATE, never approved here.

  RUN1  export_test/run1  physical DEVICE V1 baseline       (read only; reproduced by the build without exclusions and additions)
  RUN2  export_test/run2  run1 - CF88_LINK_EXCLUSIONS (430)  (read only; reproduced by the build without additions)
  RUN3  export_test/run3  run2 + CF88_WORK_REFERENCE_ADDITIONS

Writes (all deterministic; built twice and compared byte by byte):
  export_test/run3/{CF88_REFERENCES_EXPORT.json, REF_LOOKUP.IDX, REF_PAYLOAD.IDX}
  export_test/run3/device_candidate/lex_ref_detail_data.RUN3_CANDIDATE.h   rich layer-4 data (candidate; baseline header untouched)
  export_test/run3/RUN3_MANIFEST.json, RUN3_SUMMARY.md, SHA256SUMS.txt
  DEVICE_INTEGRATION/staging_sd_v1_run3_candidate/                          SD overlay CANDIDATE on the PC (never a physical card)
Usage: python build_export_run3.py
"""
import collections
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'DEVICE_INTEGRATION/tools'))
import reference_engine as E  # noqa: E402

D = HERE / 'derived'
RUN1, RUN2, RUN3 = D / 'export_test/run1', D / 'export_test/run2', D / 'export_test/run3'
DEV_CAND = RUN3 / 'device_candidate'
HEADER_NAME = 'lex_ref_detail_data.RUN3_CANDIDATE.h'
STAGING = ROOT / 'DEVICE_INTEGRATION/staging_sd_v1_run3_candidate'
STAGING_SD = STAGING / 'SD/99_LEX_V1'
BASE_STAGING_SD = ROOT / 'DEVICE_INTEGRATION/staging_sd_v1/SD/99_LEX_V1'
RUNTIME_INDEX = ROOT / 'DEVICE_INTEGRATION/staging_sd_v1/_host/CF88_RUNTIME_TARGET_INDEX.json'
ADDITIONS = D / 'CF88_WORK_REFERENCE_ADDITIONS.json'
DECISIONS = ROOT / 'REFERENCE_COVERAGE_AUDIT/REFERENCE_EXPANSION_ROUND1_DECISIONS.json'
REGISTRY = ROOT / 'REFERENCE_REGISTRY/WORK_REGISTRY_V2.json'
REGISTRY69 = ROOT / 'LEX_MACHINA_REFERENCIAS_ADAPTADOR_CATALOGO_69_V1/CATALOGO_69_CANONICO.json'
FILES = ('CF88_REFERENCES_EXPORT.json', 'REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX')
EXCLUDED = ('JURISPRUDENCE:STF:RG:113:CF88:25:-:-:-@CF88:ART.25', 'JURISPRUDENCE:STF:RG:756:CF88:31:3:-:-@CF88:ART.31:PAR.3')
ENGINE_VERSION = dict(tag='cf-reference-engine-run3-candidate', run='run3', status='CANDIDATE_UNCOMMITTED_PENDING_REVIEW',
                      derived_from='run2 + CF88_WORK_REFERENCE_ADDITIONS (REFERENCE_EXPANSION_01)')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tree(d):
    d = Path(d)
    return {p.relative_to(d).as_posix(): sha(p) for p in sorted(d.rglob('*')) if p.is_file()}


def rows(p):
    return [l.split('|') for l in Path(p).read_text(encoding='utf-8').splitlines() if l and l[0] != '#']


def export_into(out):
    reg = E.TargetRegistry()
    links = E.build_links('CF88', reg)
    files = E.export('CF88', links, out, E.link_exclusions('CF88', reg), E.work_reference_additions('CF88', reg))
    return links, files


def header_into(out_h):
    subprocess.run([sys.executable, str(ROOT / 'DEVICE_INTEGRATION/tools/build_ref_detail_header.py'), '--payload', str(RUN3 / 'REF_PAYLOAD.IDX'),
                    '--additions', str(ADDITIONS), '--out', str(out_h)], check=True, capture_output=True)


def counts(links):
    c = collections.Counter((l['reference_type'], l['visibility']) for l in links)
    work = [l for l in links if l['reference_type'] == 'WORK_REFERENCE' and l['visibility'] == 'CURRENT_VISIBLE']
    arts = {':'.join(l['target_id'].split(':')[:2]) for l in work}
    return dict(total=len(links), jurisprudence_visible=c[('JURISPRUDENCE', 'CURRENT_VISIBLE')], correlata_visible=c[('CORRELATA', 'CURRENT_VISIBLE')],
                work_reference=len(work), hidden=sum(v for (t, vis), v in c.items() if vis == 'HISTORICAL_HIDDEN_BY_DEFAULT'),
                work_targets=len({l['target_id'] for l in work}), work_articles_cf=len({a for a in arts if a.startswith('CF88:')}),
                work_articles_adct=len({a for a in arts if a.startswith('ADCT:')}),
                work_targets_adct=len({l['target_id'] for l in work if l['target_id'].startswith('ADCT:')}))


def validate_targets(adds):
    """23/23 rule applied to the integrated links: each target exists in the target index, in the CF88_RUNTIME target table and in the
    device TARGETS table as CURRENT, is reachable by an ACTIVE_TARGET line (TEXT_MAP direct, or ART.n line for ART.n:CAPUT) and is not
    a historical-filtered reference target."""
    idx = {t['target_id']: t for t in json.loads((D / 'CF88_TARGET_INDEX.json').read_text(encoding='utf-8'))['targets']}
    st = json.loads((D / 'CF88_TARGET_STATUS.json').read_text(encoding='utf-8'))['targets']
    rt = {t['target_id'] for t in json.loads(RUNTIME_INDEX.read_text(encoding='utf-8'))['targets']}
    tg = {r[0]: r for r in rows(STAGING_SD / '10_TARGETS/CF88_TARGETS.IDX')}
    tm = {r[2] for r in rows(STAGING_SD / '10_TARGETS/CF88_TEXT_MAP.IDX')}
    man = json.loads((STAGING_SD / '00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
    filtered = {x['target_id'] for x in man['layer_validation']['historical_reference_targets_filtered']}
    out = []
    for a in adds:
        t = a['target_id']
        disp = t if t in tm else (t[:-len(':CAPUT')] if t.endswith(':CAPUT') and t[:-len(':CAPUT')] in tm else None)
        chk = dict(target_id=t, work_id=a['work_id'], in_target_index=t in idx, kind=idx.get(t, {}).get('kind'),
                   status=st.get(t, {}).get('status'), in_runtime=t in rt, device_legal_status=tg.get(t, [None] * 3)[2],
                   namespace=t.split(':')[0], display_target=disp, filtered=t in filtered)
        chk['valid'] = bool(chk['in_target_index'] and chk['status'] in E.ADDITION_TARGET_STATUS and chk['in_runtime']
                            and chk['device_legal_status'] == 'CURRENT' and disp and not chk['filtered'])
        out.append(chk)
    return out


def main():
    for d in (RUN1, RUN2):
        if not all((d / f).is_file() for f in FILES):
            raise SystemExit(f'MISSING_RUN {d}')
    before = {d.name: tree(d) for d in (RUN1, RUN2)}
    reg = E.TargetRegistry()
    # RUN2 must still be exactly the build without the additions overlay (and RUN1 without exclusions + additions)
    with tempfile.TemporaryDirectory() as t:
        r2 = E.without_additions(reg, 'CF88')
        E.export('CF88', E.build_links('CF88', r2), Path(t) / 'r2', E.link_exclusions('CF88', r2))
        E.export('CF88', E.build_links('CF88', E._without(reg, 'CF88', 'link_exclusions', 'work_reference_additions', 'work_registry')), Path(t) / 'r1')
        repro = {'run1': tree(Path(t) / 'r1') == before['run1'], 'run2': tree(Path(t) / 'r2') == before['run2']}
    if not all(repro.values()):
        raise SystemExit(f'PREVIOUS_RUN_NOT_REPRODUCED {repro}')

    if RUN3.exists():
        shutil.rmtree(RUN3)
    links, files = export_into(RUN3)
    DEV_CAND.mkdir(parents=True)
    header_into(DEV_CAND / HEADER_NAME)
    import build_sd_staging as S  # noqa: E402
    S.build(STAGING, ref_dir=RUN3, require_committed_refs=False, reference_engine_version=ENGINE_VERSION)

    # second, independent build of everything -> BYTE_IDENTICAL
    with tempfile.TemporaryDirectory() as t:
        _, files_b = export_into(Path(t) / 'run3')
        header_into(Path(t) / HEADER_NAME)
        tmp_staging = ROOT / 'DEVICE_INTEGRATION' / '_tmp_run3_rebuild'
        try:
            S.build(tmp_staging, ref_dir=RUN3, require_committed_refs=False, reference_engine_version=ENGINE_VERSION)
            identical = dict(export=files == files_b and tree(Path(t) / 'run3') == {k: v for k, v in tree(RUN3).items() if '/' not in k},
                             header=sha(Path(t) / HEADER_NAME) == sha(DEV_CAND / HEADER_NAME),
                             staging=tree(tmp_staging) == tree(STAGING))
        finally:
            shutil.rmtree(tmp_staging, ignore_errors=True)
    if not all(identical.values()):
        raise SystemExit(f'RUN3_NOT_DETERMINISTIC {identical}')

    after = {d.name: tree(d) for d in (RUN1, RUN2)}
    links2 = [l for ls in json.loads((RUN2 / FILES[0]).read_text(encoding='utf-8'))['references'].values() for l in ls]
    l2 = {l['reference_id']: l for l in links2}
    l3 = {l['reference_id']: l for l in links}
    adds = json.loads(ADDITIONS.read_text(encoding='utf-8'))['records']
    new_ids = sorted(set(l3) - set(l2))
    expected_new = sorted(f"WORK_REFERENCE:{a['work_id']}@{a['target_id']}" for a in adds)
    tchecks = validate_targets(adds)
    c2, c3 = counts(links2), counts(links)
    hdr = (DEV_CAND / HEADER_NAME).read_text(encoding='utf-8')
    base_hdr = (ROOT / 'firmware/LEX_MACHINA_DEVICE_V1_CANDIDATE/lex_ref_detail_data.h').read_text(encoding='utf-8')
    base_entries = [b for b in base_hdr.split('\n  {')[1:]]
    checks = dict(
        run1_preserved=before['run1'] == after['run1'], run2_preserved=before['run2'] == after['run2'], run1_run2_reproduced=all(repro.values()),
        byte_identical=identical, only_additions_added=new_ids == expected_new, nothing_removed=not (set(l2) - set(l3)),
        no_existing_link_changed=all(l2[k] == l3[k] for k in l2), additions_valid_targets=f"{sum(c['valid'] for c in tchecks)}/{len(tchecks)}",
        exclusions_absent=[x for x in EXCLUDED if x in l3] == [], exclusions_listed=sorted(x['reference_id'] for x in
                                                                                       json.loads((RUN3 / FILES[0]).read_text(encoding='utf-8'))['excluded_links']) == sorted(EXCLUDED),
        header_keeps_baseline_entries=all(('  {' + b.split('\n};')[0]) in hdr for b in base_entries),
        header_entries=hdr.count('\n  {"'), header_new_entries=sum(f'{{"{a["target_id"]}|{a["work_id"]}"' in hdr for a in adds),
        staging_entenda_unchanged=all(sha(STAGING_SD / '30_ENTENDA' / n) == sha(BASE_STAGING_SD / '30_ENTENDA' / n) for n in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT')),
        staging_runtime_text_unchanged=sha(STAGING_SD / '05_TEXT/CF88_RUNTIME.txt') == sha(BASE_STAGING_SD / '05_TEXT/CF88_RUNTIME.txt'),
        staging_text_map_unchanged=sha(STAGING_SD / '10_TARGETS/CF88_TEXT_MAP.IDX') == sha(BASE_STAGING_SD / '10_TARGETS/CF88_TEXT_MAP.IDX'),
        staging_refs_equal_run3={n: sha(STAGING_SD / '20_REFERENCES' / n) == sha(RUN3 / n) for n in ('REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX')})
    if not (checks['run1_preserved'] and checks['run2_preserved'] and checks['only_additions_added'] and checks['nothing_removed']
            and checks['no_existing_link_changed'] and all(c['valid'] for c in tchecks) and checks['exclusions_absent']
            and checks['exclusions_listed'] and checks['header_keeps_baseline_entries'] and checks['header_new_entries'] == len(adds)
            and checks['staging_entenda_unchanged'] and checks['staging_runtime_text_unchanged'] and checks['staging_text_map_unchanged']
            and all(checks['staging_refs_equal_run3'].values())):
        raise SystemExit(f'RUN3_CHECK_FAILED {json.dumps(checks, indent=1)}')
    tg_base = {r[0]: r[3] for r in rows(BASE_STAGING_SD / '10_TARGETS/CF88_TARGETS.IDX')}
    tg3 = {r[0]: r[3] for r in rows(STAGING_SD / '10_TARGETS/CF88_TARGETS.IDX')}
    flag_changes = [dict(target_id=t, baseline_run1=tg_base[t], run3=tg3[t]) for t in sorted(tg3) if tg3[t] != tg_base.get(t)]
    reg2 = json.loads(REGISTRY.read_text(encoding='utf-8'))
    manifest = dict(
        schema_version=1, run='run3', status=ENGINE_VERSION['status'], derived_from=ENGINE_VERSION['derived_from'], norma_id='CF88',
        inputs={p.relative_to(ROOT).as_posix(): sha(p) for p in (D / 'CF88_REFERENCES_CANONICAL.json', D / 'CF88_TARGET_INDEX.json', D / 'CF88_TARGET_STATUS.json',
                                                                  D / 'CF88_QUARANTINE_RESOLUTION.json', D / 'CF88_LINK_EXCLUSIONS.json', ADDITIONS, REGISTRY,
                                                                  REGISTRY69, DECISIONS, HERE / 'engine_config.json', HERE / 'reference_engine.py')},
        outputs={**{f'run3/{k}': v for k, v in tree(RUN3).items() if k not in ('RUN3_MANIFEST.json', 'RUN3_SUMMARY.md', 'SHA256SUMS.txt')}},
        device_staging_candidate=dict(path=STAGING.relative_to(ROOT).as_posix(), files=json.loads((STAGING_SD / '00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))['files'],
                                      build_id=json.loads((STAGING_SD / '00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))['build_id'],
                                      targets_flag_changes_vs_baseline=flag_changes,
                                      note='Inclui o ENTENDA aprovado do baseline (Batches 01-03 + pilotos). NAO inclui Batch04. NAO copiado para /99_LEX_V1 fisico.'),
        previous_runs=dict(run1=dict(files=before['run1'], preserved=checks['run1_preserved']), run2=dict(files=before['run2'], preserved=checks['run2_preserved'])),
        counts=dict(run2=c2, run3=c3, added_links=len(new_ids), registry_before=reg2['total_before'], registry_after=reg2['total'], promoted_works=reg2['promoted']),
        added_links=new_ids, target_validation=tchecks, checks=checks,
        not_done=['firmware nao alterado', 'header do baseline nao substituido', 'nada copiado para SD fisico', 'sem flash', 'sem merge com Batch04',
                  'sem commit/tag/push'])
    (RUN3 / 'RUN3_MANIFEST.json').write_bytes((json.dumps(manifest, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    M = ['# Reference Engine RUN3 (CANDIDATO — pendente de revisão)', '',
         f"Derivado de: {ENGINE_VERSION['derived_from']}. RUN1 e RUN2 preservados byte a byte e reproduzidos pelo engine "
         f"(run1 sem exclusões/adições; run2 sem adições): {checks['run1_preserved'] and checks['run2_preserved'] and checks['run1_run2_reproduced']}.", '',
         '| | RUN2 | RUN3 |', '|---|---|---|']
    for k, lab in (('total', 'Relações totais'), ('jurisprudence_visible', 'Jurisprudências visíveis'), ('correlata_visible', 'Correlatas visíveis'),
                   ('work_reference', 'WORK_REFERENCE'), ('hidden', 'Hidden (HISTORICAL_HIDDEN_BY_DEFAULT)'), ('work_targets', 'Targets com obra'),
                   ('work_articles_cf', 'Artigos distintos da CF com obra'), ('work_articles_adct', 'Artigos do ADCT com obra'),
                   ('work_targets_adct', 'Targets do ADCT com obra')):
        M.append(f'| {lab} | {c2[k]} | {c3[k]} |')
    M += ['', f"- Novos vínculos: **{len(new_ids)}** (todos WORK_REFERENCE do overlay; nenhum vínculo removido ou alterado).",
          f"- Targets validados: **{checks['additions_valid_targets']}** (índice, CF88_RUNTIME, TARGETS CURRENT, alcançável por ACTIVE_TARGET, não filtrado).",
          f"- Tema 113 × CF88.25 e Tema 756 × CF88.31.3: ausentes (listados só em `excluded_links`): {checks['exclusions_absent']}.",
          f"- Determinismo (export, header candidato, staging DEVICE): {identical}.",
          f"- Registry oficial: {reg2['total_before']} → {reg2['total']} obras (promovidas: {', '.join(reg2['promoted'])}).",
          f"- Header rico candidato: `{(DEV_CAND / HEADER_NAME).relative_to(ROOT).as_posix()}` ({checks['header_entries']} fichas; "
          f"{checks['header_new_entries']} novas; as 101 do baseline mantidas). O header do firmware NÃO foi alterado.",
          f"- Staging DEVICE candidato: `{STAGING.relative_to(ROOT).as_posix()}` (flags de {len(flag_changes)} targets mudam; ENTENDA, texto e TEXT_MAP idênticos ao baseline).",
          '', '## Vínculos adicionados', '']
    M += [f'- `{x}`' for x in new_ids]
    M += ['', '## Não feito nesta missão', ''] + [f'- {x}' for x in manifest['not_done']]
    (RUN3 / 'RUN3_SUMMARY.md').write_bytes(('\n'.join(M) + '\n').encode('utf-8'))
    sums = tree(RUN3)
    sums.pop('SHA256SUMS.txt', None)
    (RUN3 / 'SHA256SUMS.txt').write_bytes(''.join(f'{v}  {k}\n' for k, v in sorted(sums.items())).encode('utf-8'))
    print(json.dumps(dict(counts=manifest['counts'], checks=checks, flag_changes=len(flag_changes)), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
