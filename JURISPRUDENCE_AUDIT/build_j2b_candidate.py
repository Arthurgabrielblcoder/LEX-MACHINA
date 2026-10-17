"""J2B: HOST-ONLY SD candidate = current physical card (J1.4 installed, J1.5 11/11) + RUN8 (5 ADI links, J2A BATCH01 ratified) + the legacy
jurisprudence records/fichas the current firmware needs to list and open them. No firmware change.

  /99_LEX_V1      OFFICIAL staging generator (build_sd_staging, same profile as the physical baseline) with RUN8 bytes; CF88_TARGETS may differ
                  from the generator ONLY in position R ([4], not read by the firmware). LEXV1.VER / LEX_DEVICE_MANIFEST regenerated.
  /99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX  card bytes + 5 rows APPENDED (existing bytes/offsets unchanged)
  /99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX      card bytes + 5 rows APPENDED (sum of quantities == records: PSRAM cache stays valid)
  /99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_ADI_*.TXT            3 NEW fichas (UTF-8, LF, same layout as the current fichas)
  everything else on the card: unchanged (99_JURISPRUDENCIA_V2/MANIFESTO.json is the J4.6 pack manifest, not read by the firmware: untouched).
Proof first: the J1.4 package builder, re-run at its pinned commit, must reproduce the physical card (J1_5_PHYSICAL_DEPLOY/sd_manifest_post_full.json);
the legacy base bytes come from the protected J4.6 archive and must equal the card manifest.
Outputs: DEVICE_INTEGRATION/staging_sd_v1_juris_j2b_candidate/ (gitignored) and JURISPRUDENCE_AUDIT/J2B_CANDIDATE_HOST_ONLY/ (changed + added files,
rollback = physical bytes; added files roll back by deletion; manifest). Never writes to a removable volume.
Usage: python build_j2b_candidate.py --commit <sha> [--runs N]
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DI = ROOT / 'DEVICE_INTEGRATION'
sys.path.insert(0, str(DI / 'tools'))
sys.path.insert(0, str(ROOT / 'REFERENCE_COVERAGE_AUDIT'))
sys.path.insert(0, str(HERE))
import build_sd_staging as S  # noqa: E402
import build_j1_4_candidate as P  # noqa: E402

PROFILE = P.PROFILE
J14_COMMIT = '7786bbc50a5f33fcf7eec01ce0de170b2d02a4f6'   # commit pinned by the installed J1.4 package
RUN8_DEV = ROOT / 'LEGAL_TARGET_ID/derived/export_test/run8_juris_j2b_candidate/device_ready'
ADDITIONS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADI_ADDITIONS_J2B.json'
PHYSICAL = HERE / 'J1_5_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
LEGACY = Path('C:/LMA/p545e/20260928/LEX_MACHINA_JURIS_CF_J4_6/SD_JURIS_J4_TESTE')   # protected archive (read only)
IDX = '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX'
LOOKUP = '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX'
CONTENT = '99_JURISPRUDENCIA_V2/03_CONTEUDO'
OUT = DI / 'staging_sd_v1_juris_j2b_candidate'
TMP = DI / '_tmp_juris_j2b_rebuild'
TMP_BASE = DI / '_tmp_juris_j2b_physical_reproduction'
PKG = HERE / 'J2B_CANDIDATE_HOST_ONLY'
PACKAGE = 'JURIS_J2B'
MANIFEST_NAME = 'J2B_PACKAGE_MANIFEST.json'
RUN_NAMES = ('REF_LOOKUP.IDX', 'REF_PAYLOAD.IDX', 'CF88_TARGETS.IDX')
ENGINE_VERSION = dict(tag='cf-reference-engine-run8-juris-j2b', run='run8', status='RUN8_JURIS_J2B_CANDIDATE_HOST_ONLY',
                      derived_from='run7 (J1.4 installed, J1.5 11/11) + 5 ADI links (J2A BATCH01 ratified; ADI 7047/7064 joint record)')
R_POS = 4
EXPECTED_CHANGED = ('99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX', '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX',
                    '99_LEX_V1/00_SYS/LEXV1.VER', '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json', '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX',
                    '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX', '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tree(d):
    return {p.relative_to(d).as_posix(): sha(p) for p in sorted(Path(d).rglob('*')) if p.is_file()}


def physical():
    return {k: v['sha256'] for k, v in json.loads(PHYSICAL.read_text(encoding='utf-8'))['entries'].items()}


def ficha_name(identificador):            # mirror of arquivoDetalheJurisCF
    return identificador.replace(':', '_').replace('/', '_') + '.TXT'


def legacy_files():
    """Card legacy bytes (archive == card manifest) + appended ADI rows/lookups + new fichas. Returns {rel: bytes}."""
    card = physical()
    base = {rel: (LEGACY / rel).read_bytes() for rel in (IDX, LOOKUP)}
    for rel, b in base.items():
        if hashlib.sha256(b).hexdigest() != card[rel]:
            raise SystemExit(f'LEGACY_ARCHIVE_NOT_CARD {rel}')
    doc = json.loads(ADDITIONS.read_text(encoding='utf-8'))
    idx, lookup = base[IDX], base[LOOKUP]
    if not idx.endswith(b'\n') or not lookup.endswith(b'\n') or b'\r' in idx or b'\r' in lookup:
        raise SystemExit('LEGACY_INDEX_SHAPE')
    keys = {l.split(b'|', 1)[0] for l in idx.split(b'\n') if l}
    looks = {tuple(l.split(b'|')[:5]) for l in lookup.split(b'\n') if l and not l.startswith(b'#')}
    out_idx, out_lookup = bytearray(idx), bytearray(lookup)
    for r in doc['records']:
        row = r['legacy_idx_row'].encode('utf-8')
        k = row.split(b'|', 1)[0]
        lk = tuple(x.encode('utf-8') for x in r['legacy_lookup'])
        if k in keys or lk in looks or b'\r' in row or b'\n' in row:
            raise SystemExit(f'LEGACY_KEY_OR_LOOKUP_EXISTS {k.decode()}')
        offset = len(out_idx)
        out_idx += row + b'\n'
        out_lookup += b'|'.join(lk + (str(offset).encode(), b'1')) + b'\n'
        keys.add(k)
        looks.add(lk)
    files = {IDX: bytes(out_idx), LOOKUP: bytes(out_lookup)}
    for ident, text in sorted(doc['fichas'].items()):
        rel = f'{CONTENT}/{ficha_name(ident)}'
        if rel in card:
            raise SystemExit(f'FICHA_ALREADY_ON_CARD {rel}')
        files[rel] = text.encode('utf-8')
    return files


def build(out, commit):
    run8_targets = (RUN8_DEV / 'CF88_TARGETS.IDX').read_bytes()
    original = S.build_targets
    record = {}

    def targets_with_run8_bytes(sd, idx, status, entenda_lookup, ref_lookup):
        stats = original(sd, idx, status, entenda_lookup, ref_lookup)
        p = sd / '10_TARGETS/CF88_TARGETS.IDX'
        gen, cand = p.read_bytes().decode('utf-8').split('\n'), run8_targets.decode('utf-8').split('\n')
        if len(gen) != len(cand):
            raise SystemExit('TARGETS_SHAPE_DIFFERS')
        r_only = []
        for g, c in zip(gen, cand):
            if g == c:
                continue
            fg, fc = g.split('|'), c.split('|')
            if g.startswith('#') or fg[:3] != fc[:3] or fg[3][:R_POS] != fc[3][:R_POS] or fg[3][R_POS + 1:] != fc[3][R_POS + 1:]:
                raise SystemExit(f'TARGETS_DIFFER_BEYOND_R {fg[0]}')
            r_only.append(fg[0])
        p.write_bytes(run8_targets)
        record['targets_r_only_divergence_vs_generator'] = r_only
        return stats

    S.build_targets = targets_with_run8_bytes
    try:
        man = S.build(out, ref_dir=RUN8_DEV, require_committed_refs=True, reference_engine_version=ENGINE_VERSION, profile=PROFILE,
                      build_commit=commit)
    finally:
        S.build_targets = original
    rel_dir = Path(out) / 'SD/99_RELATIONS_V2/05_INDICES_ESP32_V2'
    rel_dir.mkdir(parents=True)
    for name in ('RELACOES.IDX', 'REL_LOOKUP.IDX', 'EXT_ARTIGOS.IDX'):
        (rel_dir / name).write_bytes((RUN8_DEV / name).read_bytes())
    for rel, b in legacy_files().items():
        p = Path(out) / 'SD' / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
    return man, record


def physical_reproduced():
    try:
        P.build(TMP_BASE, J14_COMMIT)
        t, card = tree(TMP_BASE / 'SD'), physical()
        return all(card.get(k) == v for k, v in t.items()), t
    finally:
        shutil.rmtree(TMP_BASE, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--commit', required=True)
    ap.add_argument('--runs', type=int, default=2)
    a = ap.parse_args()
    ok, base_tree = physical_reproduced()
    if not ok:
        raise SystemExit('PHYSICAL_BASELINE_NOT_REPRODUCED')
    man, rec = build(OUT, a.commit)
    trees = [tree(OUT / 'SD')]
    try:
        for _ in range(a.runs - 1):
            build(TMP, a.commit)
            trees.append(tree(TMP / 'SD'))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    if not all(t == trees[0] for t in trees):
        raise SystemExit('STAGING_NOT_DETERMINISTIC')
    card = physical()
    added = tuple(sorted(k for k in trees[0] if k not in card))
    changed = tuple(sorted(k for k in trees[0] if k in card and trees[0][k] != card[k]))
    if changed != EXPECTED_CHANGED:
        raise SystemExit(f'UNEXPECTED_DIFF_VS_PHYSICAL {changed}')
    if set(trees[0]) - set(added) != set(base_tree) | {IDX, LOOKUP} or not all(k.startswith(CONTENT + '/STF_ADI_') for k in added):
        raise SystemExit(f'UNEXPECTED_FILE_SET {added}')
    for name, rel in (('REF_LOOKUP.IDX', '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX'), ('REF_PAYLOAD.IDX', '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'),
                      ('CF88_TARGETS.IDX', '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX')):
        if trees[0][rel] != sha(RUN8_DEV / name):
            raise SystemExit(f'STAGING_NOT_RUN {rel}')
    for rel in (IDX, LOOKUP):                                    # append-only: the card bytes are an exact prefix
        if not (OUT / 'SD' / rel).read_bytes().startswith((LEGACY / rel).read_bytes()):
            raise SystemExit(f'LEGACY_NOT_APPEND_ONLY {rel}')
    m = json.loads((OUT / 'SD/99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json').read_text(encoding='utf-8'))
    man_ok = all(trees[0].get(k) == v['sha256'] for k, v in m['files'].items() if k != '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json')
    if PKG.exists():
        shutil.rmtree(PKG)
    P.build(TMP_BASE, J14_COMMIT)                    # rollback bytes = current physical card (reproduced, checked against the card manifest)
    try:
        for rel in changed + added:
            dst = PKG / 'candidate/SD' / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes((OUT / 'SD' / rel).read_bytes())
        for rel in changed:
            src = LEGACY / rel if rel.startswith('99_JURISPRUDENCIA_V2/') else TMP_BASE / 'SD' / rel
            dst = PKG / 'rollback/SD' / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(Path(src).read_bytes())
    finally:
        shutil.rmtree(TMP_BASE, ignore_errors=True)
    for rel in changed:
        if sha(PKG / 'rollback/SD' / rel) != card[rel]:
            raise SystemExit(f'ROLLBACK_NOT_PHYSICAL {rel}')
    diff = [dict(path='/' + rel, before_sha256=card[rel], before_bytes=(PKG / 'rollback/SD' / rel).stat().st_size, after_sha256=trees[0][rel],
                 after_bytes=(PKG / 'candidate/SD' / rel).stat().st_size) for rel in changed]
    adds = [dict(path='/' + rel, after_sha256=trees[0][rel], after_bytes=(PKG / 'candidate/SD' / rel).stat().st_size, rollback='DELETE')
            for rel in added]
    report = dict(profile=PROFILE, package=PACKAGE, status='HOST_ONLY_CANDIDATE', physical_approved=False, card_touched=False,
                  device_flashed=False, firmware_change='NONE (firmware already classifies TIPO adi: list "ADI <NUMERO>", ficha 03_CONTEUDO)',
                  staging=OUT.relative_to(ROOT).as_posix(), build_id=man['build_id'], git_commit=man['git_commit'], reference_engine=ENGINE_VERSION,
                  physical_baseline_reproduced=True, legacy_base='J4.6 archive bytes == card manifest (JURISPRUDENCIA.IDX, JUR_LOOKUP.IDX)',
                  deterministic_runs=a.runs, byte_identical_rebuild=True, legacy_append_only=True,
                  targets_r_only_divergence_vs_generator=rec['targets_r_only_divergence_vs_generator'], device_manifest_matches_package=man_ok,
                  changed_vs_physical=list(changed), added_vs_physical=list(added), file_diff=diff, file_additions=adds,
                  files=[dict(path='/' + k, sha256=v, same_as_physical=card.get(k) == v) for k, v in trees[0].items()])
    (PKG / MANIFEST_NAME).write_bytes((json.dumps(report, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))
    print(json.dumps({k: v for k, v in report.items() if k not in ('files',)}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
