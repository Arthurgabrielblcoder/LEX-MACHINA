"""J2H: HOST-ONLY package "Candidate B over the physically approved Candidate A" (SD data only; the generic firmware is NOT flashed here).

Why a new package: the J2F Candidate B was built over J2C, appending group A and group B legacy rows interleaved; on a card that already
holds Candidate A, the A legacy bytes would not be a prefix of B. J2H keeps the A card bytes as an EXACT prefix of the legacy indexes and
appends ONLY the group-B rows (J2E HC 232627 + J2F group B), so every A offset is preserved (A_INDEX_PREFIX_IDENTICAL / OLD_OFFSETS_PRESERVED).
Everything else is taken byte for byte from the authoritative ratified J2F packages:
  /99_LEX_V1 (LEXV1.VER, LEX_DEVICE_MANIFEST.json, CF88_TARGETS.IDX, REF_LOOKUP.IDX, REF_PAYLOAD.IDX) = J2_GENERIC_FW_CANDIDATE (RUN11-B, 315/198);
  new fichas = J2_GENERIC_FW_CANDIDATE additions that are not in J2_CURRENT_FW_CANDIDATE (group B only).
Proofs: A package candidate bytes == the physical card after J2G (committed manifest); the J2H legacy indexes contain exactly the same rows /
lookup tuples as the J2F B package (only the order differs); rollback bytes = Candidate A (299/186), never J2C.
Writes J2H_CANDIDATE_B_OVER_A/{candidate,rollback}/SD + J2H_PACKAGE_MANIFEST.json.   Usage: python build_j2h_candidate.py [--check]
"""
import collections
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_j2b_isolation_audit as A  # noqa: E402

PKG_A = HERE / 'J2F_CANDIDATES_HOST_ONLY/J2_CURRENT_FW_CANDIDATE'
PKG_B = HERE / 'J2F_CANDIDATES_HOST_ONLY/J2_GENERIC_FW_CANDIDATE'
A_PHYSICAL = HERE / 'J2G_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
A_VALIDATION = HERE / 'J2G_PHYSICAL_DEPLOY/J2G_PHYSICAL_VALIDATION.json'
ADDITIONS = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2F.json'
OUT = HERE / 'J2H_CANDIDATE_B_OVER_A'
IDX, LOOKUP = A.IDX, A.LOOKUP
LEX = ('99_LEX_V1/00_SYS/LEXV1.VER', '99_LEX_V1/00_SYS/LEX_DEVICE_MANIFEST.json', '99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX',
       '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX', '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def lines(b):
    return [l for l in b.split(b'\n') if l and not l.startswith(b'#')]


def build():
    val = json.loads(A_VALIDATION.read_text(encoding='utf-8'))
    if (val['J2G_PHYSICAL_VALIDATION'], val['CANDIDATE_A_PHYSICAL_APPROVED']) != ('21/21 PASS', 'YES'):
        raise SystemExit('CANDIDATE_A_NOT_PHYSICALLY_APPROVED')
    card_a = {k: v['sha256'] for k, v in json.loads(A_PHYSICAL.read_text(encoding='utf-8'))['entries'].items()}
    ma = json.loads((PKG_A / 'J2F_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
    mb = json.loads((PKG_B / 'J2F_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
    ra = lambda rel: (PKG_A / 'candidate/SD' / rel).read_bytes()  # noqa: E731
    rb = lambda rel: (PKG_B / 'candidate/SD' / rel).read_bytes()  # noqa: E731
    for f in ma['files']:
        if card_a.get(f['path'].lstrip('/')) != f['sha256']:
            raise SystemExit(f'A_PACKAGE_IS_NOT_THE_PHYSICAL_CARD {f["path"]}')
    add = json.loads(ADDITIONS.read_text(encoding='utf-8'))
    b_only = [r for r in add['records'] if r['group'] == 'B']
    idx, lk = bytearray(ra(IDX)), bytearray(ra(LOOKUP))
    a_idx, a_lk = bytes(idx), bytes(lk)
    keys = {l.split(b'|', 1)[0] for l in lines(a_idx)}
    shared = []
    looks = {tuple(l.split(b'|')[:5]) for l in lines(a_lk)}
    for r in b_only:
        row = r['legacy_idx_row'].encode('utf-8')
        k = row.split(b'|', 1)[0]
        tup = tuple(x.encode('utf-8') for x in r['legacy_lookup'])
        if k in keys:
            raise SystemExit(f'LEGACY_KEY_EXISTS {k.decode()}')
        if tup in looks:
            shared.append('|'.join(r['legacy_lookup']))
        off = len(idx)
        idx += row + b'\n'
        lk += b'|'.join(tup + (str(off).encode(), b'1')) + b'\n'
        keys.add(k)
        looks.add(tup)
    idx, lk = bytes(idx), bytes(lk)
    # equivalence with the ratified J2F B package: same rows, same lookup tuples (order differs only)
    same_rows = sorted(lines(idx)) == sorted(lines(rb(IDX)))
    tup_count = lambda b: collections.Counter(tuple(l.split(b'|')[:5]) for l in lines(b))  # noqa: E731
    same_lookup_tuples = tup_count(lk) == tup_count(rb(LOOKUP))
    cache_ok, n_rec, n_sum = A.cache_rules(idx, lk)
    if not (same_rows and same_lookup_tuples and cache_ok and idx.startswith(a_idx) and lk.startswith(a_lk)):
        raise SystemExit('J2H_LEGACY_NOT_EQUIVALENT_TO_B')
    a_add = {f['path'].lstrip('/') for f in ma['file_additions']}
    new_fichas = sorted(f['path'].lstrip('/') for f in mb['file_additions'] if f['path'].lstrip('/') not in a_add)
    expected_fichas = sorted({f"99_JURISPRUDENCIA_V2/03_CONTEUDO/{r['source_id'].replace(':', '_').replace('/', '_')}.TXT"
                              for r in b_only if r.get('new_ficha')})
    if new_fichas != expected_fichas:
        raise SystemExit(f'B_ONLY_FICHAS_MISMATCH {sorted(set(new_fichas) ^ set(expected_fichas))}')
    cand = {IDX: idx, LOOKUP: lk, **{rel: rb(rel) for rel in LEX}, **{rel: rb(rel) for rel in new_fichas}}
    rollback = {rel: ra(rel) for rel in (IDX, LOOKUP) + LEX}
    for rel, b in rollback.items():
        if sha(b) != card_a[rel]:
            raise SystemExit(f'ROLLBACK_IS_NOT_CANDIDATE_A {rel}')
    for rel in new_fichas:
        if rel in card_a:
            raise SystemExit(f'FICHA_ALREADY_ON_A_CARD {rel}')
    tree = dict(card_a)
    tree.update({rel: sha(b) for rel, b in cand.items()})
    rows_b = A.rows(cand['99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'])
    jv = [r for r in rows_b if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
    ver = dict(l.split('|', 1) for l in cand['99_LEX_V1/00_SYS/LEXV1.VER'].decode('utf-8').splitlines() if '|' in l and not l.startswith('#'))
    man = dict(package='J2H_CANDIDATE_B_OVER_A', status='HOST_ONLY_CANDIDATE', base='Candidato A fisicamente aprovado (J2G 21/21 PASS, 299/186)',
               source_packages=dict(A=PKG_A.relative_to(HERE).as_posix(), B=PKG_B.relative_to(HERE).as_posix(), B_build_id=mb['build_id']),
               build_id=ver['BUILD_ID'], git_commit=ver['GIT_COMMIT'], physical_approved=False, card_touched=False, device_flashed=False,
               requires_firmware='GENERIC tribunal/classe (JURIS_TYPE_PROTOTYPE); SAFE_TO_BOOT_WITH_CURRENT_FIRMWARE = NO',
               juris_relations=len(jv), juris_targets=len({r[0] for r in jv}),
               legacy=dict(A_INDEX_PREFIX_IDENTICAL='YES', OLD_OFFSETS_PRESERVED='YES', rows_appended=len(b_only), legacy_records=n_rec,
                           lookup_quantity_sum=n_sum, same_rows_as_j2f_b=same_rows, same_lookup_tuples_as_j2f_b=same_lookup_tuples,
                           lookup_tuples_shared=shared),
               group_b_records=[dict(target=r['target_id'], source=r['source_id'], key=r['source_reference_id'], origin=r['origin']) for r in b_only],
               file_diff=[dict(path='/' + rel, before_sha256=sha(rollback[rel]), before_bytes=len(rollback[rel]), after_sha256=sha(cand[rel]),
                               after_bytes=len(cand[rel])) for rel in (IDX, LOOKUP) + LEX],
               file_additions=[dict(path='/' + rel, after_sha256=sha(cand[rel]), after_bytes=len(cand[rel]), rollback='DELETE') for rel in new_fichas],
               ROLLBACK_TARGET='Candidato A 299/186 (NÃO J2C)', files=[dict(path='/' + k, sha256=v) for k, v in sorted(tree.items())])
    return cand, rollback, man


def write(cand, rollback, man):
    if OUT.exists():
        shutil.rmtree(OUT)
    for base, data in (('candidate/SD', cand), ('rollback/SD', rollback)):
        for rel, b in data.items():
            p = OUT / base / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b)
    (OUT / 'J2H_PACKAGE_MANIFEST.json').write_bytes((json.dumps(man, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))


if __name__ == '__main__':
    cand, rollback, man = build()
    if '--check' in sys.argv:
        ok = (OUT / 'J2H_PACKAGE_MANIFEST.json').read_bytes().replace(b'\r\n', b'\n') == (json.dumps(man, ensure_ascii=False, indent=1) + '\n').encode() \
            and all((OUT / 'candidate/SD' / rel).read_bytes() == b for rel, b in cand.items()) \
            and all((OUT / 'rollback/SD' / rel).read_bytes() == b for rel, b in rollback.items())
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    write(cand, rollback, man)
    print(json.dumps({k: man[k] for k in ('build_id', 'juris_relations', 'juris_targets', 'legacy')}, ensure_ascii=False, indent=1))
    print(len(man['file_diff']), 'replaced;', len(man['file_additions']), 'created')
