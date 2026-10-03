"""DEVICE INTEGRATION V1 - builds the SD OVERLAY CANDIDATE on the PC (never on a physical card).

Read-only inputs (approved artifacts, never modified):
  - ENTENDA final corpora of Batches 01-03 (+ the two pilot explanations reused by Batch 01)  -> unified ENTENDA pair (154)
  - Reference Engine export (LEGAL_TARGET_ID/derived/export_test/run1)                         -> REF pair, byte copy
  - CF88_RUNTIME (updater/exportar_cf88_runtime.py, fontes oficiais travadas CF 579494 + ADCT 604119) -> texto exibido, indice de
    targets (parser aprovado, modo estrito), CF88_TARGETS.IDX e CF88_TEXT_MAP.IDX sobre EXATAMENTE os mesmos bytes
Output: DEVICE_INTEGRATION/staging_sd_v1/ (SD tree under SD/, host-only diagnostics under _host/).
Deterministic: no wall clock; build_date comes from SOURCE_DATE_EPOCH or the HEAD commit time.

Usage: python build_sd_staging.py [--out DIR] [--profile BATCH04_RUN3]

Profiles: default (no profile) = the physically approved staging_sd_v1 (163 ENTENDA, RUN1), reproduced byte for byte.
BATCH04_RUN3 = consolidation candidate: + ENTENDA Batch04 (CF88 arts. 25-36, approved by rounds), REF pair from the approved RUN3
export (byte copy), + the physically validated ARTICLE_SEARCH indexes (CF88 + CC2002, byte copy, hash-checked).
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
ROOT = DI.parent
sys.path.insert(0, str(ROOT / 'ENTENDA_ENGINE'))
sys.path.insert(0, str(HERE))
import entenda_engine as E  # noqa: E402
import runtime_targets as RT  # noqa: E402
import exportar_cf88_runtime as XR  # noqa: E402

SCHEMA = 3
SD_ROOT = '99_LEX_V1'
BATCHES = ('production_batch_01_final', 'production_batch_02_final', 'production_batch_03_final')
REF_DIR = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run1'
EXPECTED_ENTENDA = 163
ENTENDA_SCOPE = 'CF88_ARTS_1_24_PLUS_APPROVED_PILOTS'
RUNTIME_STATUS = 'RUNTIME'
RUNTIME_CF_RESOLUTION = 'CF88_RUNTIME_RESOLVED'
# pilot explanations approved in ENTENDA-CF-A2 outside the sequential batches (explicitly listed; no silent additions)
APPROVED_PILOTS = ('CF88:ART.37', 'CF88:ART.37:PAR.6', 'CF88:ART.37:PAR.10', 'CF88:ART.60', 'CF88:ART.60:PAR.4',
                   'CF88:ART.60:PAR.4:INC.IV', 'CF88:ART.150', 'CF88:ART.225', 'ADCT:ART.10:INC.II')
# most specific kind wins when several targets start on the same physical line
KIND_RANK = {'ALINEA': 0, 'INCISO': 1, 'PARAGRAFO': 2, 'PARAGRAFO_UNICO': 2, 'ARTIGO': 3, 'CAPUT': 4, 'NAMESPACE': 5, 'NORMA': 6}


# BATCH04 + RUN3 consolidation profile (explicit; the default build stays the approved baseline).
ARTICLE_INDEXES = (
    # (source in the repo, sha256 of the physically validated file, text it is bound to: 'RUNTIME' or (bytes, sha256))
    ('DEVICE_INTEGRATION/staging_article_index/SD/99_LEX_V1/10_TARGETS/CF88_ARTICLE_SEARCH.IDX',
     '56e437a0c9cebb113c47f6a7b100ee64363c63207a647eca0456e86d6db27fae', 'RUNTIME'),
    ('DEVICE_INTEGRATION/staging_article_index_cc/SD/99_LEX_V1/10_TARGETS/CC2002_ARTICLE_SEARCH.IDX',
     '674c9971925c29aaca9685fb2d0b9515fe87e4072d644858ea27495c327d3a68',
     (660268, 'ad5ba178613b6181e2d8a61919eda0c6223c68feb6e47bef4ea65bc45c13e6ae')),
)
PROFILES = {
    'BATCH04_RUN3': dict(
        batches=BATCHES + ('production_batch_04',), expected_entenda=None, max_article=36,
        entenda_scope='CF88_ARTS_1_36_PLUS_APPROVED_PILOTS',
        entenda_tags=['entenda-cf-batch01-approved-2026-09-28', 'entenda-cf-batch02-approved-2026-09-28',
                      'entenda-cf-batch03-approved-2026-09-29', 'ENTENDA_CF_PRODUCTION_BATCH_04 (round approvals, uncommitted)'],
        entenda_note='ENTENDA: CF88 arts. 1 a 36 (inclui 29-A) + 9 pilotos aprovados (arts. 37, 37 §6, 37 §10, 60, 60 §4, 60 §4 IV, 150, 225, '
                     'ADCT 10 II); ausencia de linha no lookup = sem ENTENDA aprovado.',
        article_indexes=ARTICLE_INDEXES),
}


class BuildError(RuntimeError):
    pass


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def _guard_out(out):
    """Never write outside DEVICE_INTEGRATION (in particular never to a removable/SD volume)."""
    out = Path(out).resolve()
    if DI.resolve() not in out.parents and out != DI.resolve():
        raise BuildError(f'OUTPUT_OUTSIDE_DEVICE_INTEGRATION: {out}')
    return out


def approved_entenda(ctx, batches=BATCHES, expected=EXPECTED_ENTENDA, max_article=24):
    rows = []
    main = E.load_corpus(ROOT / ctx.ncfg['corpus'])
    for b in batches:
        bd = ROOT / 'ENTENDA_ENGINE/derived' / b
        spec = json.loads((bd / 'BATCH_SPEC.json').read_text(encoding='utf-8'))
        rows += [r for r in main if r['status'] == 'ACTIVE' and r['target_id'] in spec.get('reused', {})]
        rows += [r for r in E.load_corpus(bd / spec['batch_corpus']) if r['status'] == 'ACTIVE']
    batch_tids = {r['target_id'] for r in rows}
    pilots = [r for r in main if r['status'] == 'ACTIVE' and r['target_id'] not in batch_tids]
    if sorted(r['target_id'] for r in pilots) != sorted(APPROVED_PILOTS):
        raise BuildError(f"PILOT_SET_MISMATCH {sorted(r['target_id'] for r in pilots)}")
    rows += pilots
    if any(r['review_status'] != 'HUMAN_APPROVED_T1' or r['status'] != 'ACTIVE' for r in rows):
        raise BuildError('ENTENDA_NOT_APPROVED_IN_PACKAGE')
    tids = [r['target_id'] for r in rows]
    if len(tids) != len(set(tids)):
        raise BuildError('ENTENDA_DUPLICATE_TARGET')
    if expected is not None and len(rows) != expected:
        raise BuildError(f'ENTENDA_COUNT {len(rows)} != {expected}')
    out_of_scope = [t for t in tids if t not in APPROVED_PILOTS and (not t.startswith('CF88:ART.') or not 1 <= int(t.split(':')[1][4:].split('-')[0]) <= max_article)]
    if out_of_scope:
        raise BuildError(f'ENTENDA_OUT_OF_SCOPE {out_of_scope}')
    return rows


def build_entenda(ctx, rows, sd):
    tmp = Path(tempfile.mkdtemp(prefix='lexv1_entenda_'))
    try:
        files = E.build_entenda_index(ctx, rows, tmp)
        d = sd / '30_ENTENDA'
        d.mkdir(parents=True)
        for n in ('ENTENDA_LOOKUP.IDX', 'ENTENDA_PAYLOAD.DAT'):
            shutil.copyfile(tmp / n, d / n)
        return json.loads((tmp / 'ENTENDA_BUILD_MANIFEST.json').read_text(encoding='utf-8')), files
    finally:
        shutil.rmtree(tmp)


def build_references(sd, ref_dir=REF_DIR, require_committed=True):
    """Byte copy of the REF pair. Default: the approved (committed) run1 blobs. A CANDIDATE build (require_committed=False, e.g. RUN3
    for review) records the sha256 of the uncommitted files instead and is never an approved package."""
    d = sd / '20_REFERENCES'
    d.mkdir(parents=True)
    out = {}
    for n in ('REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX'):
        src = Path(ref_dir) / n
        if require_committed:
            committed = git('rev-parse', f'HEAD:{src.relative_to(ROOT).as_posix()}')
            if git('hash-object', str(src)) != committed:
                raise BuildError(f'REFERENCE_ARTIFACT_NOT_APPROVED_BLOB: {n}')
            out[n] = committed
        else:
            out[n] = 'sha256:' + sha(src)
        shutil.copyfile(src, d / n)
    return out


def build_runtime(sd, host, ctx):
    """CF88_RUNTIME.txt (from the locked official sources) + canonical target index built on exactly those bytes."""
    data, prov = XR.build_runtime()
    d = sd / '05_TEXT'
    d.mkdir(parents=True)
    rpath = d / 'CF88_RUNTIME.txt'
    rpath.write_bytes(data)
    idx = RT.build_runtime_index(rpath)
    if idx['source']['sha256'] != prov['sha256'] or idx['source']['bytes'] != prov['bytes']:
        raise BuildError('RUNTIME_INDEX_NOT_BUILT_FROM_RUNTIME_BYTES')
    legacy = json.loads(RT.LEGACY_INDEX.read_text(encoding='utf-8'))
    rows, counts = RT.classify(legacy, idx, data.decode('utf-8'), ctx.legal_status, RT.load_reviewed())
    blocking = [r for r in rows if r['classification'] in RT.BLOCKING]
    if blocking:
        raise BuildError(f'RUNTIME_TARGET_DIFF_BLOCKING {blocking[:5]}')
    idx_out = dict(idx, source=dict(idx['source'], path=f'{SD_ROOT}/05_TEXT/CF88_RUNTIME.txt'))
    (host / 'CF88_RUNTIME_TARGET_INDEX.json').write_bytes((json.dumps(idx_out, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    (host / 'CF88_RUNTIME.provenance.json').write_bytes((json.dumps(prov, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    diff = dict(schema_version=1, legacy_index_sha256=legacy['target_index_sha256'], legacy_targets=legacy['total_targets'],
                runtime_index_sha256=idx['target_index_sha256'], runtime_targets=idx['total_targets'], counts=counts, rows=rows)
    (host / 'TARGET_DIFF_LEGACY_VS_RUNTIME.json').write_bytes((json.dumps(diff, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    return data, prov, idx, diff


def validate_layers_against_runtime(idx, sd):
    """163 ENTENDA (anchors + covered) must resolve; Reference targets absent from the runtime must be historical-only rows."""
    ids = {t['target_id'] for t in idx['targets']}
    ent = [l.split('|') for l in (sd / '30_ENTENDA/ENTENDA_LOOKUP.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
    miss = [r[0] for r in ent if r[0] not in ids]
    if miss:
        raise BuildError(f'ENTENDA_TARGET_NOT_IN_RUNTIME {miss}')
    ref_rows = [l.split('|') for l in (sd / '20_REFERENCES/REF_PAYLOAD.IDX').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]
    ref_targets = sorted({r[0] for r in ref_rows})
    absent = [t for t in ref_targets if t not in ids]
    visible_absent = [t for t in absent if any(r[0] == t and r[2] != 'HISTORICAL_HIDDEN_BY_DEFAULT' for r in ref_rows)]
    if visible_absent:
        raise BuildError(f'VISIBLE_REFERENCE_TARGET_NOT_IN_RUNTIME {visible_absent}')
    # Runtime view (derivada; o export aprovado do Reference Engine continua byte a byte): targets historicos ausentes do runtime
    # nao entram em CF88_TARGETS.IDX nem no TEXT_MAP, logo o aparelho nunca os consulta nem mostra camada para eles.
    filtered = [dict(target_id=t, status='HISTORICAL_REFERENCE_TARGET_FILTERED',
                     rows=sum(1 for r in ref_rows if r[0] == t), visibility='HISTORICAL_HIDDEN_BY_DEFAULT') for t in absent]
    return dict(entenda_lookup_rows=len(ent), entenda_direct=sum(1 for r in ent if r[7] == 'DIRECT'), entenda_resolved=len(ent) - len(miss),
                reference_targets=len(ref_targets), reference_rows=len(ref_rows), reference_targets_resolved=len(ref_targets) - len(absent),
                reference_targets_absent_historical_hidden=absent, historical_reference_targets_filtered=filtered)


def build_targets(sd, idx, status, entenda_lookup, ref_lookup):
    """CF88_TARGETS.IDX: every runtime target (sorted, bytewise) with legal status (from the monovigente runtime) and layer flags."""
    ent, ext = {}, {}
    payload = (entenda_lookup.parent / 'ENTENDA_PAYLOAD.DAT').read_bytes()
    for l in entenda_lookup.read_text(encoding='utf-8').splitlines():
        if l and not l.startswith('#'):
            p = l.split('|')
            ent[p[0]] = p[7]
            blob = payload[int(p[1]):int(p[1]) + int(p[2])]
            ext[p[0]] = b'\n#CAMADAS EXTERNAS\n' in blob or b'\n#NOTAS TEMPORAIS\n' in blob
    refs = {l.split('|')[0] for l in ref_lookup.read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')}
    types = {}
    for l in (ref_lookup.parent / 'REF_PAYLOAD.IDX').read_text(encoding='utf-8').splitlines():
        if l and not l.startswith('#'):
            p = l.split('|')
            if p[2] == 'CURRENT_VISIBLE':
                types.setdefault(p[0], set()).add(p[1])
    lines = []
    for t in sorted(idx['targets'], key=lambda t: t['target_id']):
        tid = t['target_id']
        if t['kind'] in ('NORMA', 'NAMESPACE'):
            continue
        ty = types.get(tid, set())
        flags = (('E' if ent.get(tid) == 'DIRECT' else 'B' if ent.get(tid) == 'COVERED_BY_BLOCK' else '-') + ('C' if 'CORRELATA' in ty else '-')
                 + ('J' if 'JURISPRUDENCE' in ty else '-') + ('W' if 'WORK_REFERENCE' in ty else '-') + ('R' if tid in refs else '-')
                 + ('X' if ext.get(tid) else '-'))
        lines.append(f"{tid}|{t['kind']}|{status[tid]}|{flags}")
    d = sd / '10_TARGETS'
    d.mkdir(parents=True)
    head = ('#LEXMACHINA|TARGETS|3\n'
            f"#TARGET_ID_VERSION|{idx['target_index_sha256']}\n#SOURCE_SHA256|{idx['source']['sha256']}\n"
            '#LEGAL_STATUS_SOURCE|CF88_RUNTIME (Compilacao Monovigente): (Revogado)/(Suprimido) -> REVOKED; demais -> CURRENT\n'
            '#TARGET_ID|KIND|LEGAL_STATUS|FLAGS\n'
            '#FLAGS(6 posicoes): [E=ENTENDA DIRECT|B=ENTENDA COVERED_BY_BLOCK|-][C=CORRELATAS|-][J=JURISPRUDENCIA|-][W=REFERENCIAS DE OBRA|-]'
            '[R=qualquer linha no REF_LOOKUP (inclui historicas ocultas)|-][X=ENTENDA com camada externa ou nota temporal|-]\n')
    (d / 'CF88_TARGETS.IDX').write_bytes((head + ''.join(l + '\n' for l in lines)).encode('utf-8'))
    counts = {}
    for l in lines:
        s = l.split('|')[2]
        counts[s] = counts.get(s, 0) + 1
    return dict(rows=len(lines), legal_status_counts=dict(sorted(counts.items())), source_index_sha256=idx['target_index_sha256'])


def build_text_map(sd, idx, data, prov):
    """CF88_TEXT_MAP.IDX over EXACTLY the runtime bytes: one row per target at its canonical line (line_start)."""
    starts, pos = [0], 0
    for line in data.split(b'\n')[:-1]:
        pos += len(line) + 1
        starts.append(pos)
    best = {}
    for t in idx['targets']:
        ln = t['line_start']
        cur = best.get(ln)
        if cur is None or KIND_RANK[t['kind']] < KIND_RANK[cur['kind']]:
            best[ln] = t
    checks = dict(checked=0, mismatched=[])
    rows = []
    for ln in sorted(best):
        t = best[ln]
        text = data[starts[ln - 1]:].split(b'\n', 1)[0].decode('utf-8').replace('\xa0', ' ').strip()
        want = {'ARTIGO': ('Art',), 'CAPUT': ('Art',), 'PARAGRAFO': ('§',), 'PARAGRAFO_UNICO': ('Par',),
                'INCISO': (t['inciso'] or '#',), 'ALINEA': ((t['alinea'] or '#') + ')',), 'NAMESPACE': (t['target_id'] == 'ADCT' and XR.ADCT_MARKER or '#',)}.get(t['kind'])
        if want:
            checks['checked'] += 1
            if not text.startswith(want):
                checks['mismatched'].append(dict(line=ln, target_id=t['target_id'], text=text[:40]))
        rows.append(f"{starts[ln - 1]:010d}|{ln}|{t['target_id']}")
    if checks['mismatched']:
        raise BuildError(f"TEXT_MAP_LINE_MISMATCH {checks['mismatched'][:5]}")
    adct = next(t for t in idx['targets'] if t['kind'] == 'NAMESPACE' and t['target_id'] == 'ADCT')
    adct_off = starts[adct['line_start'] - 1]
    if adct_off != prov['adct_offset']:
        raise BuildError('ADCT_OFFSET_MISMATCH')
    head = (f"#LEXMACHINA|TEXT_MAP|2\n#TARGET_ID_VERSION|{idx['target_index_sha256']}\n#RUNTIME_STATUS|RUNTIME\n"
            f"#SOURCE_SHA256|{prov['sha256']}\n#SOURCE_BYTES|{prov['bytes']}\n#SOURCE_NAME|CF88_RUNTIME.txt\n"
            f"#NORMALIZATION_VERSION|{prov['normalization_version']}\n#RECORD_COUNT|{len(rows)}\n#NAMESPACE_START_ADCT|{adct_off}\n"
            f"#OFFSET(10 digitos, ordem crescente)|LINHA|TARGET_ID\n")
    (sd / '10_TARGETS' / 'CF88_TEXT_MAP.IDX').write_bytes((head + ''.join(r + '\n' for r in rows)).encode('utf-8'))
    return dict(rows=len(rows), line_checks=checks['checked'], adct_offset=adct_off)


def copy_article_indexes(sd, specs, prov):
    """Byte copy of the physically validated ARTICLE_SEARCH indexes; each one must be the approved file AND bound to its text."""
    out = []
    d = sd / '10_TARGETS'
    for rel, want, bound in specs:
        src = ROOT / rel
        if sha(src) != want:
            raise BuildError(f'ARTICLE_INDEX_NOT_APPROVED {rel}')
        blob = src.read_bytes()
        if blob[:8] != b'LXARTIX1':
            raise BuildError(f'ARTICLE_INDEX_SCHEMA {rel}')
        src_bytes, src_sha = int.from_bytes(blob[20:24], 'little'), blob[24:56].hex()
        if bound == 'RUNTIME':
            bound = (prov['bytes'], prov['sha256'])
        if (src_bytes, src_sha) != tuple(bound):
            raise BuildError(f'ARTICLE_INDEX_TEXT_MISMATCH {rel}')
        shutil.copyfile(src, d / src.name)
        out.append(dict(file=f'/{SD_ROOT}/10_TARGETS/{src.name}', sha256=want, bytes=len(blob),
                        records=int.from_bytes(blob[16:20], 'little'), text_bytes=src_bytes, text_sha256=src_sha))
    return out


def build(out, ref_dir=REF_DIR, require_committed_refs=True, reference_engine_version=None, profile=None, build_commit=None):
    """build_commit pins GIT_COMMIT / build_date / git_tags_at_commit to the commit the package was built on (default HEAD), so an
    approved package stays byte-reproducible after later commits."""
    prof = PROFILES[profile] if profile else None
    out = _guard_out(out)
    if out.exists():
        shutil.rmtree(out)
    sd = out / 'SD' / SD_ROOT
    host = out / '_host'
    sd.mkdir(parents=True)
    host.mkdir(parents=True)
    ctx = E.NormContext('CF88')
    rows = (approved_entenda(ctx, prof['batches'], prof['expected_entenda'], prof['max_article']) if prof else approved_entenda(ctx))
    entenda_scope = prof['entenda_scope'] if prof else ENTENDA_SCOPE
    ent_manifest, _ = build_entenda(ctx, rows, sd)
    ref_blobs = build_references(sd, ref_dir, require_committed_refs)
    data, prov, idx, diff = build_runtime(sd, host, ctx)
    layers = validate_layers_against_runtime(idx, sd)
    tgt = build_targets(sd, idx, RT.runtime_status(idx), sd / '30_ENTENDA/ENTENDA_LOOKUP.IDX', sd / '20_REFERENCES/REF_LOOKUP.IDX')
    tmap = build_text_map(sd, idx, data, prov)
    art_idx = copy_article_indexes(sd, prof['article_indexes'], prov) if prof else None
    head = git('rev-parse', build_commit or 'HEAD')
    epoch = int(os.environ.get('SOURCE_DATE_EPOCH') or git('log', '-1', '--format=%ct', head))
    files = {p.relative_to(out / 'SD').as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(sd.rglob('*')) if p.is_file()}
    build_id = hashlib.sha256(''.join(f'{k}:{v["sha256"]}\n' for k, v in files.items()).encode()).hexdigest()[:16]
    ver = (f'#LEXMACHINA|DEVICE_VERSION|{SCHEMA}\nBUILD_ID|{build_id}\nGIT_COMMIT|{head}\nENTENDA_COUNT|{len(rows)}\n'
           f'ENTENDA_SCOPE|{entenda_scope}\nENTENDA_PILOTS|{len(APPROVED_PILOTS)}\nTARGETS|{tgt["rows"]}\n'
           f'RUNTIME_CF_PATH|/{SD_ROOT}/05_TEXT/CF88_RUNTIME.txt\nRUNTIME_CF_BYTES|{prov["bytes"]}\nRUNTIME_CF_SHA256|{prov["sha256"]}\n'
           f'TEXT_MAP_SOURCE_SHA256|{prov["sha256"]}\nTEXT_MAP_SOURCE_BYTES|{prov["bytes"]}\n'
           f'TEXT_MAP_RUNTIME_STATUS|{RUNTIME_STATUS}\nRUNTIME_CF|{RUNTIME_CF_RESOLUTION}\n'
           f"REFERENCE_ENGINE|{(reference_engine_version or {}).get('tag', 'cf-reference-engine-final-2026-09-28')}\n")
    (sd / '00_SYS').mkdir()
    (sd / '00_SYS' / 'LEXV1.VER').write_bytes(ver.encode('utf-8'))
    files['99_LEX_V1/00_SYS/LEXV1.VER'] = dict(bytes=(sd / '00_SYS/LEXV1.VER').stat().st_size, sha256=sha(sd / '00_SYS/LEXV1.VER'))
    files = dict(sorted(files.items()))
    manifest = dict(
        schema_version=SCHEMA, package_type='SD_OVERLAY_CANDIDATE', build_id=build_id,
        build_date=datetime.fromtimestamp(epoch, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), build_date_source='SOURCE_DATE_EPOCH or HEAD commit time',
        git_commit=head, git_tags_at_commit=git('tag', '--points-at', head).split(),
        legal_corpus_version=dict(runtime_text=f'/{SD_ROOT}/05_TEXT/CF88_RUNTIME.txt', runtime_sha256=prov['sha256'], runtime_bytes=prov['bytes'],
                                  runtime_lines=prov['lines'], normalization_version=prov['normalization_version'], adct_offset=prov['adct_offset'],
                                  sources=prov['sources']),
        target_id_version=dict(grammar='LEGAL_TARGET_ID/target_id.py', parser='LEGAL_TARGET_ID/structure_parser.py (article_case_sensitive=True)',
                               target_index_sha256=idx['target_index_sha256'], targets=idx['total_targets'],
                               legacy_index_sha256=diff['legacy_index_sha256'], legacy_vs_runtime=diff['counts']),
        reference_engine_version=dict(reference_engine_version or dict(tag='cf-reference-engine-final-2026-09-28',
                                                                         commit='9fcab702a9b6467b71949071ba34741e940e366d'), blobs=ref_blobs),
        entenda_version=dict(contract=E.CONTRACT, tags=prof['entenda_tags'] if prof else ['entenda-cf-batch01-approved-2026-09-28', 'entenda-cf-batch02-approved-2026-09-28', 'entenda-cf-batch03-approved-2026-09-29'],
                             review_status='HUMAN_APPROVED_T1', lookup_rows=ent_manifest['lookup_rows']),
        entenda_explanation_count=len(rows), entenda_scope=entenda_scope, entenda_pilots_included=list(APPROVED_PILOTS),
        runtime_cf=dict(status=RUNTIME_CF_RESOLUTION, text_map_runtime_status=RUNTIME_STATUS),
        layer_validation=layers, sd_root=f'/{SD_ROOT}', files=files,
        targets=tgt, text_map=dict(rows=tmap['rows'], line_checks=tmap['line_checks'], bound_to_source_sha256=prov['sha256'], adct_offset=tmap['adct_offset']),
        compatibility_notes=[
            'Overlay novo em /99_LEX_V1: nao altera nem substitui 99_RELATIONS_V2, 99_JURISPRUDENCIA_V2 ou os TXT da Lei Seca do cartao legado.',
            'O firmware v7.12.0 ignora /99_LEX_V1 (nenhum caminho do sketch aponta para ele): copiar o overlay nao muda o comportamento atual.',
            'Todos os indices: UTF-8, LF, linhas pipe-separadas, cabecalho #LEXMACHINA|<TIPO>|<versao>, ordenacao bytewise pelo campo-chave.',
            'CF88_TEXT_MAP.IDX so pode ser usado se RUNTIME_STATUS=RUNTIME e tamanho E sha256 do texto exibido coincidirem com o cabecalho; senao a resolucao de target falha fechada.',
            'O texto exibido pelo runtime V1 e /99_LEX_V1/05_TEXT/CF88_RUNTIME.txt, exatamente os bytes indexados.',
            prof['entenda_note'] if prof else 'ENTENDA: CF88 arts. 1 a 24 + 9 pilotos aprovados (arts. 37, 37 §6, 37 §10, 60, 60 §4, 60 §4 IV, 150, 225, ADCT 10 II); ausencia de linha no lookup = sem ENTENDA aprovado.'])
    if art_idx is not None:
        manifest['profile'] = profile
        manifest['article_search_indexes'] = art_idx
    (sd / '00_SYS' / 'LEX_DEVICE_MANIFEST.json').write_bytes((json.dumps(manifest, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    (host / 'ENTENDA_UNIFIED_BUILD_MANIFEST.json').write_bytes((json.dumps(ent_manifest, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(DI / 'staging_sd_v1'))
    ap.add_argument('--profile', choices=sorted(PROFILES))
    a = ap.parse_args()
    m = build(a.out, profile=a.profile)
    print(json.dumps(dict(build_id=m['build_id'], entenda=m['entenda_explanation_count'], targets=m['targets']['rows'],
                          text_map=m['text_map']['rows'], files={k: v['bytes'] for k, v in m['files'].items()}), indent=1))
