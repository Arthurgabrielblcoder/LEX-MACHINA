"""DEVICE INTEGRATION V1-A3A: write ONLY the /99_LEX_V1 overlay to the physical microSD, fail closed.

Nothing outside <ROOT>/99_LEX_V1.DEPLOYING and <ROOT>/99_LEX_V1 is ever opened for writing. Legacy files are only read ('rb').
Usage:
  python deploy_sd_overlay_a3a.py precheck <ROOT> <OUT_JSON>   read-only: backups, staging, card identity, legacy 1.062/1.062
  python deploy_sd_overlay_a3a.py deploy   <ROOT> <OUT_JSON>   precheck again, copy to temp, verify, rename, verify, legacy re-check
  python deploy_sd_overlay_a3a.py verify   <ROOT> <OUT_JSON>   read-only: final overlay + legacy + simulator on the card vs staging
"""
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DI = HERE.parent
sys.path.insert(0, str(HERE))
import backup_sd_readonly as B  # noqa: E402
import device_lookup_simulator as S  # noqa: E402

BACKUP = DI / 'backups/sd_20260929T163407Z'
FLASH_DUMP = DI / 'backups/esp32/raw_flash_16MB_read1.bin'
STAGING = DI / 'staging_sd_v1/SD'
OVERLAY, TEMP = '99_LEX_V1', '99_LEX_V1.DEPLOYING'
MANIFEST_REL = '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json'
EXPECT = dict(
    head='c1fb3dfd802f546b93834f8bbfba9754267fa632',
    sd_files=1062, sd_bytes=24574047, sd_aggregate='f00e6d562f239b23c033844b879a9afdf2b878980550068e3acc4101bad49b38',
    flash_sha='061849a357d77f571d735a108fc5f4a032d7c12e4f7e3c8f3b34c0f3357d6727',
    runtime_bytes=587133, runtime_sha='7ef82290d30f4af180c5010709a7c11b84655e7ed1d3a4951566d3bb18b2e42a',
    text_map_sha='889f82002e82fb2b7d9165e6ce2a4e0dcb78d311432e268c341f1d0b1e436b96',
    targets_rows=3810, entenda=163,
    cf_legacy=('1- CONSTITUIÇÃO FEDERAL/cf.txt', 429242, 'd8469e18e45e027872f04bc56ba1076bcc6d1bb3295c71173bd5b728b22dca6e'),
)
REQUIRED = ('05_TEXT/CF88_RUNTIME.txt', '10_TARGETS/CF88_TEXT_MAP.IDX', '10_TARGETS/CF88_TARGETS.IDX', '30_ENTENDA/ENTENDA_LOOKUP.IDX',
            '30_ENTENDA/ENTENDA_PAYLOAD.DAT', '20_REFERENCES/REF_LOOKUP.IDX', '20_REFERENCES/REF_PAYLOAD.IDX',
            '00_SYS/LEX_DEVICE_MANIFEST.json', '00_SYS/LEXV1.VER')
QUERIES = ('CF88.5.V', 'CF88.21.XXIV', 'CF88.22.XXIX', 'CF88.24.4', 'CF88.37.6', 'CF88.60.4.IV', 'ADCT.10.II', 'CF88.114.VIII',
           'CF88.25', 'CF88.12.2', 'CF88.1', 'ADCT.78.4', 'CF88.40.4.II', 'CF88.999', 'XYZ')


class Blocked(Exception):
    pass


def need(cond, reason):
    if not cond:
        raise Blocked(reason)


def rel_files(root):
    root = Path(root)
    return {p.relative_to(root).as_posix(): p for p in B.walk(root)}


def check_backups():
    m = json.loads((BACKUP / 'manifest.json').read_text(encoding='utf-8'))
    agg = hashlib.sha256(''.join(f"{f['relative_path']}\t{f['size']}\t{f['sha256']}\n" for f in m['files']).encode('utf-8')).hexdigest()
    need((len(m['files']), sum(f['size'] for f in m['files']), agg, m['aggregate_manifest_sha256'], m['errors']) ==
         (EXPECT['sd_files'], EXPECT['sd_bytes'], EXPECT['sd_aggregate'], EXPECT['sd_aggregate'], []), 'ROLLBACK_NOT_VERIFIED: SD manifest')
    data = BACKUP / 'data'
    need(set(rel_files(data)) == {f['relative_path'] for f in m['files']}, 'ROLLBACK_NOT_VERIFIED: SD backup file set')
    bad = [f['relative_path'] for f in m['files'] if (data / f['relative_path']).stat().st_size != f['size'] or B.sha_file(data / f['relative_path']) != f['sha256']]
    need(not bad, f'ROLLBACK_NOT_VERIFIED: SD backup data {bad[:5]}')
    need(FLASH_DUMP.stat().st_size == 16777216 and B.sha_file(FLASH_DUMP) == EXPECT['flash_sha'], 'ROLLBACK_NOT_VERIFIED: flash dump')
    return m, dict(sd_backup='BACKUP_VERIFIED', sd_backup_files=len(m['files']), sd_backup_bytes=EXPECT['sd_bytes'], sd_aggregate=agg,
                   flash_backup='PHYSICAL_FLASH_BACKUP_VERIFIED', flash_sha256=EXPECT['flash_sha'], FULL_PHYSICAL_ROLLBACK_AVAILABLE=True)


def check_staging():
    sd = STAGING
    files = rel_files(sd)
    for r in REQUIRED:
        need(f'{OVERLAY}/{r}' in files, f'RUNTIME_TEXT_NOT_IN_DEPLOY_PACKAGE' if 'RUNTIME' in r else f'PACKAGE_FILE_MISSING {r}')
    man = json.loads(files[MANIFEST_REL].read_text(encoding='utf-8'))
    declared = dict(man['files'])
    need(set(files) - {MANIFEST_REL} == set(declared), f'MANIFEST_FILESET_MISMATCH {sorted(set(files) ^ set(declared) - {MANIFEST_REL})}')
    pkg = {}
    for rel, p in sorted(files.items()):
        size, sha = p.stat().st_size, B.sha_file(p)
        if rel != MANIFEST_REL:
            need((size, sha) == (declared[rel]['bytes'], declared[rel]['sha256']), f'MANIFEST_HASH_MISMATCH {rel}')
        pkg[rel] = dict(bytes=size, sha256=sha)
    rt = pkg[f'{OVERLAY}/05_TEXT/CF88_RUNTIME.txt']
    need((rt['bytes'], rt['sha256']) == (EXPECT['runtime_bytes'], EXPECT['runtime_sha']), 'RUNTIME_TEXT_NOT_IN_DEPLOY_PACKAGE (hash)')
    need(pkg[f'{OVERLAY}/10_TARGETS/CF88_TEXT_MAP.IDX']['sha256'] == EXPECT['text_map_sha'], 'TEXT_MAP_HASH')
    ver = dict(l.split('|', 1) for l in files[f'{OVERLAY}/00_SYS/LEXV1.VER'].read_text(encoding='utf-8').splitlines() if '|' in l and not l.startswith('#'))
    need(ver['GIT_COMMIT'] == EXPECT['head'] == man['git_commit'], 'BUILD_COMMIT_MISMATCH')
    need((ver['RUNTIME_CF_SHA256'], ver['RUNTIME_CF_BYTES'], ver['RUNTIME_CF_PATH']) ==
         (EXPECT['runtime_sha'], str(EXPECT['runtime_bytes']), '/99_LEX_V1/05_TEXT/CF88_RUNTIME.txt'), 'VER_RUNTIME')
    need(int(ver['ENTENDA_COUNT']) == man['entenda_explanation_count'] == EXPECT['entenda'], 'ENTENDA_COUNT')
    need(int(ver['TARGETS']) == man['targets']['rows'] == EXPECT['targets_rows'], 'TARGET_COUNT')
    need(ver['BUILD_ID'] == man['build_id'], 'BUILD_ID')
    return pkg, dict(package_files=len(pkg), package_bytes=sum(v['bytes'] for v in pkg.values()), build_id=man['build_id'],
                     git_commit=man['git_commit'], manifest_sha256=pkg[MANIFEST_REL]['sha256'], manifest_self_consistent=True,
                     entenda=man['entenda_explanation_count'], targets_rows=man['targets']['rows'])


def check_legacy(root, m, allow_overlay):
    """Every legacy file exactly as in the backup manifest; the only permitted extra top-level entry is the overlay."""
    root = Path(root)
    top = sorted(e.name for e in os.scandir(root))
    extra_top = [n for n in top if n in (OVERLAY, TEMP) or n.startswith(OVERLAY)]
    now = {k: v for k, v in rel_files(root).items() if k.split('/', 1)[0] not in extra_top}
    listed = {f['relative_path']: f for f in m['files']}
    changed = sorted(set(now) ^ set(listed))
    for rel, f in listed.items():
        if rel in now and (now[rel].stat().st_size != f['size'] or B.sha_file(now[rel]) != f['sha256']):
            changed.append(rel)
    cf_rel, cf_size, cf_sha = EXPECT['cf_legacy']
    cf = root / cf_rel
    cf_ok = cf.is_file() and cf.stat().st_size == cf_size and B.sha_file(cf) == cf_sha
    need(allow_overlay or not extra_top, f'EXISTING_OVERLAY_PRESENT {extra_top}')
    return dict(legacy_files=len(now), legacy_bytes=sum(p.stat().st_size for p in now.values()), legacy_changed=len(changed),
                legacy_changed_list=changed[:50], cf_txt_ok=cf_ok, top_level_extra=extra_top)


def identify(root):
    root = Path(root)
    need(root.exists() and B.signature_ok(root), 'SD_NOT_IDENTIFIED (signature)')
    return dict(root=str(root), signature=list(B.SIGNATURE) + ['1- CONSTITUIÇÃO FEDERAL/'])


def verify_overlay(base, pkg):
    files = rel_files(base)
    got = {}
    for rel, p in files.items():
        got[f'{OVERLAY}/{rel}'] = dict(bytes=p.stat().st_size, sha256=B.sha_file(p))
    need(got == pkg, f'OVERLAY_HASH_MISMATCH {sorted(k for k in set(got) | set(pkg) if got.get(k) != pkg.get(k))}')
    return dict(files=len(got), bytes=sum(v['bytes'] for v in got.values()), all_hashes_ok=True)


def simulate(sd):
    dev = S.Device(sd)
    try:
        size, sha = dev.verify_runtime_file()
        out = dict(runtime=dict(bytes=size, sha256=sha, conf=(size, sha) == (EXPECT['runtime_bytes'], EXPECT['runtime_sha'])))
        rt = (Path(sd) / '05_TEXT/CF88_RUNTIME.txt').read_bytes()
        off = rt.index('VIII - a execução, de ofício'.encode('utf-8'))
        out['text_position_114_VIII'] = dev.resolve_text_position(off, size, sha)
        out['text_position_wrong_sha'] = dev.resolve_text_position(off, size, '0' * 64)
        q = {}
        for x in QUERIES:
            r = dev.query(x)
            r.pop('lookup_us', None)
            q[x] = r
        out['queries'] = q
        return out
    finally:
        dev.close()


def precheck(root):
    m, backups = check_backups()
    pkg, staging = check_staging()
    ident = identify(root)
    legacy = check_legacy(root, m, allow_overlay=True)
    need(legacy['legacy_changed'] == 0 and legacy['cf_txt_ok'], 'LEGACY_SD_CHANGED')
    return m, pkg, dict(backups=backups, staging=staging, card=ident, legacy_before=legacy)


def deploy(root):
    m, pkg, res = precheck(root)
    root = Path(root)
    final, temp = root / OVERLAY, root / TEMP
    if res['legacy_before']['top_level_extra']:
        need(res['legacy_before']['top_level_extra'] == [OVERLAY], 'EXISTING_DEVICE_V1_DIFFERS (temp or other overlay entry present)')
        verify_overlay(final, pkg)                     # raises EXISTING_DEVICE_V1_DIFFERS-like mismatch if different
        res['deploy'] = dict(status='ALREADY_DEPLOYED_IDENTICAL')
        return res
    os.mkdir(temp)                                     # fails if it exists
    copied = 0
    for rel in sorted(pkg):
        src = STAGING / rel
        dst = temp / rel.split('/', 1)[1]
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(src, 'rb') as fi, open(dst, 'xb') as fo:
            fo.write(fi.read())
            fo.flush()
            os.fsync(fo.fileno())
        copied += 1
    res['temp_verify'] = verify_overlay(temp, pkg)
    res['simulator_temp'] = simulate(temp)
    need(not final.exists(), 'FINAL_APPEARED_DURING_DEPLOY')
    os.rename(temp, final)                            # single directory-entry rename, never replaces (Windows refuses if dest exists)
    need(final.is_dir() and not temp.exists(), 'RENAME_NOT_CONFIRMED')
    res['final_verify'] = verify_overlay(final, pkg)
    res['legacy_after'] = check_legacy(root, m, allow_overlay=True)
    need(res['legacy_after']['legacy_changed'] == 0 and res['legacy_after']['top_level_extra'] == [OVERLAY], 'LEGACY_SD_CHANGED')
    res['deploy'] = dict(status='DEPLOYED', temp=TEMP, final=OVERLAY, copied_files=copied, copied_bytes=sum(v['bytes'] for v in pkg.values()))
    return res


def verify(root):
    m, pkg, res = precheck(root)
    res['final_verify'] = verify_overlay(Path(root) / OVERLAY, pkg)
    card, local = simulate(Path(root) / OVERLAY), simulate(STAGING / OVERLAY)
    res['simulator_card'] = card
    res['simulator_card_equals_staging'] = card == local
    need(card == local, 'SIMULATOR_CARD_DIFFERS_FROM_STAGING')
    return res


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    cmd, root, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    try:
        res = dict(precheck=lambda r: precheck(r)[2], deploy=deploy, verify=verify)[cmd](root)
        res['result'] = 'OK'
    except Blocked as e:
        res = dict(result='BLOCKED', reason=str(e))
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str) + '\n', encoding='utf-8')
    print(res['result'], res.get('reason', ''))
