"""CC-J1 — first physical microSD deploy of multinorm jurisprudence. DATA ONLY (no flash). ADDITIVE ONLY: the files of the immutable
CC_J1_MATERIALIZATION_CANDIDATE are CREATED; no existing card file is replaced or deleted (Tema 932 ficha already on the card is reused).
Write path per file: temporary .LEX_NEW (exclusive create) -> fsync -> readback sha -> os.replace onto a NON-existing target -> readback sha.
Rollback = delete exactly the created files (list in the evidence); the card returns to the J2H/J2I manifest.

  python deploy_cc_j1_sd.py pre D:      card signature, WHOLE card == J2H post manifest (1190 files), 315/198 recounted, CC absent,
                                        Tema 932 physical sha, candidate hashes, path collisions; PRE manifest + plan + rollback written
  python deploy_cc_j1_sd.py copy D:     create the 23 card files of the candidate (after PRE_OK)
  python deploy_cc_j1_sd.py verify D:   readback, POST manifest diff (only the planned files added), recount + multinorm simulation on the
                                        card bytes (CC 29/24, CF 315/198, exclusions, fichas, BACK, shared ficha, frozen layers)
Evidence: JURISPRUDENCE_ENGINE/CC_J1_PHYSICAL_DEPLOY/. Backups (gitignored): DEVICE_INTEGRATION/backups/cc_j1_physical_deploy/.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / 'firmware_multinorm'), str(ROOT / 'JURISPRUDENCE_AUDIT'), str(ROOT / 'LEGAL_TARGET_ID')]
import generic_packager as P  # noqa: E402
import multinorm_sim as S  # noqa: E402
import juris_types as JT  # noqa: E402

CAND = HERE / 'CC_J1_MATERIALIZATION_CANDIDATE'
REC = HERE / 'CC_J1_RATIFICATION_RECORD.json'
FW_VALIDATION = HERE / 'firmware_multinorm/PHYSICAL_FLASH/MULTINORM_PHYSICAL_VALIDATION.json'
BASELINE = ROOT / 'JURISPRUDENCE_AUDIT/J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
EV = HERE / 'CC_J1_PHYSICAL_DEPLOY'
BK = ROOT / 'DEVICE_INTEGRATION/backups/cc_j1_physical_deploy'
IGNORED_ROOTS = {'System Volume Information'}
TEMA932 = '99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_932.TXT'
TEMA932_SHA = '7bd339337d38caefb5505c8933b395df9a6d129195e9b02060e40f196a10e4d5'
CHUNK = 1 << 20
CC_FILE = '/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'
CF_FILE = '/1- CONSTITUIÇÃO FEDERAL/cf.txt'
EXCLUDED = {'CCJ1-09': 'STF:RG:1194', 'CCJ1-30': 'STJ:SUMULA:609', 'CCJ1-08': 'STF:RG:526', 'CCJ1-16': 'STJ:SUMULA:371', 'CCJ1-19': 'STJ:SUMULA:451',
            'CCJ1-24': 'STJ:SUMULA:543', 'CCJ1-26': 'STJ:SUMULA:550', 'CCJ1-28': 'STJ:SUMULA:595'}
FROZEN_PREFIXES = {'CORRELATAS': ('99_RELATIONS_V1/', '99_RELATIONS_V2/'), 'LEXV1 (ENTENDA/REFERENCIAS/TARGETS/TEXTO)': ('99_LEX_V1/',),
                   'JURIS_LEGADO': ('99_JURISPRUDENCIA_V2/05_INDICES_ESP32/',), 'FICHAS_EXISTENTES': ('99_JURISPRUDENCIA_V2/03_CONTEUDO/',)}


def stop(m):
    raise SystemExit('PARAR: ' + m)


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(CHUNK), b''):
            h.update(b)
    return h.hexdigest()


def rec_of(p: Path) -> dict:
    return dict(bytes=p.stat().st_size, sha256=sha_file(p))


def card_manifest(root: Path) -> dict:
    out = {}
    for dp, dn, fn in os.walk(root):
        if Path(dp) == root:
            dn[:] = sorted(d for d in dn if d not in IGNORED_ROOTS)
        else:
            dn.sort()
        for n in sorted(fn):
            p = Path(dp) / n
            out[p.relative_to(root).as_posix()] = rec_of(p)
    return dict(sorted(out.items()))


def dump(name, value):
    EV.mkdir(parents=True, exist_ok=True)
    (EV / name).write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(value, ensure_ascii=False)[:3000])


def load(name):
    return json.loads((EV / name).read_text(encoding='utf-8'))


def root_for(drive: str) -> Path:
    root = Path(drive.rstrip('\\/') + os.sep)
    need = [root / '99_LEX_V1' / d for d in ('00_SYS', '05_TEXT', '10_TARGETS', '20_REFERENCES', '30_ENTENDA')] + \
           [root / '99_JURISPRUDENCIA_V2/05_INDICES_ESP32', root / '99_JURISPRUDENCIA_V2/03_CONTEUDO', root / '99_RELATIONS_V2']
    if not all(p.is_dir() for p in need) or not any(p.is_dir() and p.name.startswith('1- CONSTITUI') for p in root.iterdir()) \
            or not (root / '2- CÓDIGO CIVIL').is_dir():
        stop('assinatura do cartão LEX MACHINA incompleta em ' + str(root))
    return root


def candidate_plan() -> dict:
    m = json.loads((CAND / 'SHA256_MANIFEST.json').read_text(encoding='utf-8'))
    disk = {os.path.relpath(os.path.join(a, f), CAND).replace(os.sep, '/') for a, _, fs in os.walk(CAND) for f in fs}
    if disk != set(m['files']) | {'SHA256_MANIFEST.json'}:
        stop('candidato com arquivos extras ou ausentes')
    for k, v in m['files'].items():
        if rec_of(CAND / k) != dict(bytes=v['bytes'], sha256=v['sha256']):
            stop('hash do candidato diverge: ' + k)
    res = json.loads((CAND / 'host/PREFLIGHT_RESULT.json').read_text(encoding='utf-8'))['checks']
    want = dict(APPROVED_RELATIONS=29, APPROVED_TARGETS=24, APPROVED_PRECEDENTS=20, NEW_FICHAS=19, SHARED_FICHAS=1, CF_BASELINE='315/198')
    if any(res[k] != v for k, v in want.items()):
        stop('preflight do candidato não confere: ' + json.dumps({k: res[k] for k in want}))
    files = {k.replace('candidate/SD/', ''): dict(bytes=v['bytes'], sha256=v['sha256']) for k, v in m['files'].items() if k.startswith('candidate/SD/')}
    return dict(manifest_sha256=hashlib.sha256((CAND / 'SHA256_MANIFEST.json').read_bytes()).hexdigest(), build_id=m['build_id'], files=files)


def recount_lexv1(root: Path) -> tuple:
    rows = [l.split('|') for l in (root / '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX').read_bytes().decode('utf-8').split('\n') if l and not l.startswith('#')]
    vis = [r for r in rows if r[1] == 'JURISPRUDENCE' and r[2] == 'CURRENT_VISIBLE']
    return vis, len(vis), len({r[0] for r in vis})


def pre(drive: str):
    if json.loads(FW_VALIDATION.read_text(encoding='utf-8'))['MULTINORM_FIRMWARE_PHYSICAL_VALIDATION'] != '25/25 PASS':
        stop('firmware multinorma não aprovado fisicamente')
    root = root_for(drive)
    plan = candidate_plan()
    base = json.loads(BASELINE.read_text(encoding='utf-8'))['entries']
    BK.mkdir(parents=True, exist_ok=True)
    if (BK / 'sd_manifest_pre_full.json').exists():
        stop('PRE já registrado; não sobrescrever')
    man = card_manifest(root)
    (BK / 'sd_manifest_pre_full.json').write_text(json.dumps(dict(drive=drive, entries=man), ensure_ascii=False, indent=1), encoding='utf-8')
    diffs = dict(changed=sorted(k for k in man if k in base and man[k] != base[k]), added=sorted(set(man) - set(base)), removed=sorted(set(base) - set(man)))
    _, n_rel, n_tgt = recount_lexv1(root)
    look = (root / '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JUR_LOOKUP.IDX').read_bytes().decode('utf-8')
    cc_rows = sum(1 for l in look.split('\n') if l.startswith('CC2002|'))
    t932 = rec_of(root / TEMA932) if (root / TEMA932).is_file() else None
    collisions = {}
    for rel, r in plan['files'].items():
        if (root / rel).exists():
            collisions[rel] = 'IDENTICAL' if rec_of(root / rel) == r else 'DIFFERENT'
        if (root / rel).with_name(Path(rel).name + '.LEX_NEW').exists():
            collisions[rel + '.LEX_NEW'] = 'TEMP_EXISTS'
    rollback = dict(scope='apagar SOMENTE os arquivos criados pelo CC-J1; firmware e arquivos antigos da CF intocados', executed=False,
                    delete_files=sorted(plan['files']), delete_dirs_if_empty=['99_JURISPRUDENCIA_V2/06_NORMALIZADO'],
                    restore_files=[], verify_against='JURISPRUDENCE_AUDIT/J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json (1190 arquivos)')
    rec = dict(SD_DRIVE=drive, card_files=len(man), baseline_files=len(base), diffs=diffs,
               SD_PRE_BASELINE_MATCH='PASS' if not any(diffs.values()) else 'FAIL',
               CF_ADCT_RELATIONS=n_rel, CF_ADCT_TARGETS=n_tgt, CC2002_RELATIONS=cc_rows,
               normalized_layer_present=(root / '99_JURISPRUDENCIA_V2/06_NORMALIZADO').exists(),
               tema932=dict(path=TEMA932, physical=t932, expected_sha256=TEMA932_SHA,
                            TEMA932_PHYSICAL_HASH_MATCH='YES' if t932 and t932['sha256'] == TEMA932_SHA == base.get(TEMA932, {}).get('sha256') else 'NO'),
               candidate=dict(manifest_sha256=plan['manifest_sha256'], build_id=plan['build_id'], files_to_add=len(plan['files']), CCJ1_CANDIDATE_HASHES='PASS'),
               UNEXPECTED_PATH_COLLISIONS=len(collisions), collisions=collisions, tema932_in_add_list=TEMA932 in plan['files'],
               ROLLBACK_TO_CF_ONLY_READY='YES', planned_files=sorted(plan['files']))
    ok = (rec['SD_PRE_BASELINE_MATCH'] == 'PASS' and (n_rel, n_tgt, cc_rows) == (315, 198, 0) and not rec['normalized_layer_present']
          and rec['tema932']['TEMA932_PHYSICAL_HASH_MATCH'] == 'YES' and not collisions and not rec['tema932_in_add_list'])
    if ok:
        rec['tema932']['TEMA932_SHARED_FICHA'] = 'VERIFIED_PHYSICAL_REUSE'
    rec['result'] = 'PRE_OK' if ok else 'PRE_FAIL'
    dump('physical_pre.json', rec)
    dump('rollback_plan.json', rollback)
    if not ok:
        stop('PRE falhou: ' + json.dumps({k: rec[k] for k in ('SD_PRE_BASELINE_MATCH', 'CF_ADCT_RELATIONS', 'CF_ADCT_TARGETS', 'CC2002_RELATIONS',
                                                             'normalized_layer_present', 'UNEXPECTED_PATH_COLLISIONS')}))


def create_one(root: Path, rel: str, r: dict):
    src, dst = CAND / 'candidate/SD' / rel, root / rel
    tmp = dst.with_name(dst.name + '.LEX_NEW')
    if dst.exists() or tmp.exists():
        stop('destino ou temporário já existe: ' + rel)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with src.open('rb') as fi, tmp.open('xb') as fo:
        for b in iter(lambda: fi.read(CHUNK), b''):
            fo.write(b)
        fo.flush()
        os.fsync(fo.fileno())
    if rec_of(tmp) != r:
        stop('readback temporário diverge: ' + rel)
    if dst.exists():
        stop('destino surgiu durante a escrita: ' + rel)
    os.replace(tmp, dst)
    if rec_of(dst) != r:
        stop('readback final diverge: ' + rel)
    print('CREATE', rel, r['bytes'], r['sha256'])


def copy(drive: str):
    root = root_for(drive)
    if load('physical_pre.json').get('result') != 'PRE_OK':
        stop('PRE não concluído')
    if (EV / 'copy_log.json').exists():
        stop('cópia já registrada; não repetir')
    plan = candidate_plan()
    if plan['manifest_sha256'] != load('physical_pre.json')['candidate']['manifest_sha256']:
        stop('candidato mudou desde o PRE')
    order = sorted(plan['files'], key=lambda k: (0 if '03_CONTEUDO' in k else 1, k.endswith('JUR_LOOKUP.IDX'), k))   # fichas first, lookup last
    created = []
    for rel in order:
        create_one(root, rel, plan['files'][rel])
        created.append(rel)
    dump('copy_log.json', dict(created=created, created_count=len(created), replaced=[], deleted=[], order='fichas -> índice/manifesto/versão -> lookup'))


def verify(drive: str):
    root = root_for(drive)
    plan = candidate_plan()
    pre_man = json.loads((BK / 'sd_manifest_pre_full.json').read_text(encoding='utf-8'))['entries']
    post = card_manifest(root)
    added = sorted(set(post) - set(pre_man))
    changed = sorted(k for k in pre_man if k in post and post[k] != pre_man[k])
    removed = sorted(set(pre_man) - set(post))
    deployed_ok = all(post.get(k) == v for k, v in plan['files'].items())
    extras = sorted(set(added) - set(plan['files']))
    frozen = {name: sorted(k for k in changed + removed if k.startswith(pref)) for name, pref in FROZEN_PREFIXES.items()}
    # ---- recount + simulation on the CARD bytes ----
    vis, n_rel, n_tgt = recount_lexv1(root)
    layer = root / P.LAYER
    look, recs = (layer / 'JUR_LOOKUP.IDX').read_bytes(), (layer / 'JURISPRUDENCIA.IDX').read_bytes()
    fichas_on_card = {p.name for p in (root / P.CONTENT).iterdir()}
    pkg = S.Package(look, recs, fichas_on_card)
    keys = [tuple(l.split('|')[:5]) for l in look.decode('utf-8').split('\n')[1:] if l]
    lines = [l.split('|') for l in recs.decode('utf-8').split('\n')[1:] if l]
    by_ns = collections.defaultdict(list)
    for l in lines:
        by_ns[l[0][len(l[6]) + 1:].split(':')[0]].append(l)
    rec = json.loads(REC.read_text(encoding='utf-8'))
    rels = sorted((r['target_id'], r['precedent']) for r in rec['approved_relations'])
    want = collections.defaultdict(set)
    for t, p in rels:
        want[t].add(p)
    cases, fichas_ok, back_ok, visible = {}, 0, 0, 0
    for t in sorted(want):
        _, art, par, inc, ali = P.query_key(t).split('|')
        st = S.carregar(pkg, CC_FILE, art, par, inc, ali)
        got = {x['caminho'].split('/')[-1] for x in st['relations']}
        exp = {JT.ficha(p) for p in want[t]}
        for i, x in enumerate(st['relations']):
            f = root / P.CONTENT / x['arquivo']
            head = f.read_text(encoding='utf-8').split('\n')[:3] if f.is_file() else []
            ok_f = f.is_file() and any(x['numero'].replace('/', ' E ').split(' ')[0] in h for h in head) and x['tribunal'] in '\n'.join(head) \
                and 'OUTRO' not in x['label']
            fichas_ok += ok_f
            back_ok += S.carregar(pkg, CC_FILE, art, par, inc, ali)['relations'] == st['relations']
        visible += len(got & exp)
        cases[t] = dict(branch=st['branch'], labels=[x['label'] for x in st['relations']], ok=got == exp and st['branch'] == 'MULTINORMA')
    cf_rel_lost = []
    for r in vis:
        norma, art, par, inc, ali = P.query_key(r[0]).split('|')
        hit = pkg.exact(norma, art, par, inc, ali)
        files = {S.relation(l, '')['arquivo'] for l in pkg.rows(*hit)} if hit else set()
        if JT.ficha(r[5]) not in files:
            cf_rel_lost.append(r[0] + '|' + r[5])
    art62 = [x['label'] for x in S.carregar(pkg, CF_FILE, '62')['relations']]
    t932_cc = S.carregar(pkg, CC_FILE, '927', par='unico')['relations']
    t932_cf = S.carregar(pkg, CF_FILE, '7', inc='XXVIII')['relations']
    shared = [x['caminho'] for x in t932_cc if x['numero'] == '932'] == [x['caminho'] for x in t932_cf if x['numero'] == '932'] == [
        '/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_932.TXT'] and post.get(TEMA932) == pre_man.get(TEMA932)
    cc_ids = {l[6] for l in by_ns['CC2002']}
    out = dict(SD_DRIVE=drive, DEPLOYED_HASHES='EXACT' if deployed_ok else 'FAIL', added=added, EXTRA_UNEXPECTED_FILES=len(extras), extras=extras,
               EXISTING_FILES_MODIFIED=len(changed), existing_changed=changed, FILES_REMOVED=len(removed), card_files_post=len(post),
               FROZEN_LAYER_CHANGES=sum(len(v) for v in frozen.values()), frozen=frozen,
               CF_ADCT_LEXV1=f'{n_rel}/{n_tgt}',
               normalized_counts={ns: dict(relations=len(v), targets=len({l[0][len(l[6]) + 1:] for l in v}), precedents=len({l[6] for l in v}))
                                  for ns, v in sorted(by_ns.items())},
               DUPLICATE_QUERY_KEYS=len(keys) - len(set(keys)), LOOKUP_LOST_RELATIONS=len(rels) - len(by_ns['CC2002']),
               CC_RELATIONS_VISIBLE=f'{visible}/{len(rels)}', CC_TARGETS_VISIBLE=f"{sum(1 for c in cases.values() if c['ok'])}/{len(cases)}",
               PENDING_PRESENT=sum(1 for k in ('CCJ1-09', 'CCJ1-30') if EXCLUDED[k] in cc_ids),
               REJECTED_PRESENT=sum(1 for k, p in EXCLUDED.items() if k not in ('CCJ1-09', 'CCJ1-30') and p in cc_ids),
               FICHA_OPEN=f'{fichas_ok}/{len(rels)}', BACK_SIMULATION=f'{back_ok}/{len(rels)}',
               CROSS_NORM_SHARED_FICHA='PASS' if shared else 'FAIL',
               CF_RELATIONS=f'{len(vis) - len(cf_rel_lost)}/{len(vis)}', CF_TARGETS=f"{len({r[0] for r in vis if r[0] + '|' + r[5] not in cf_rel_lost})}/{n_tgt}",
               CF_LOST_RELATIONS=len(cf_rel_lost), cf_lost=cf_rel_lost[:10], art62_list=art62, cases=cases)
    out['CF_CHANGED'] = 'NO' if (out['CF_ADCT_LEXV1'] == '315/198' and not out['FROZEN_LAYER_CHANGES']) else 'YES'
    out['CF_REGRESSION'] = 'PASS' if (not cf_rel_lost and out['CF_CHANGED'] == 'NO') else 'FAIL'
    ok = (deployed_ok and not extras and not changed and not removed and out['DUPLICATE_QUERY_KEYS'] == 0 and out['LOOKUP_LOST_RELATIONS'] == 0
          and out['CC_RELATIONS_VISIBLE'] == '29/29' and out['CC_TARGETS_VISIBLE'] == '24/24' and out['PENDING_PRESENT'] == 0 and out['REJECTED_PRESENT'] == 0
          and out['FICHA_OPEN'] == '29/29' and out['BACK_SIMULATION'] == '29/29' and shared and out['CF_REGRESSION'] == 'PASS')
    out['result'] = 'SD_VALIDATED' if ok else 'SD_VALIDATION_FAIL'
    (BK / 'sd_manifest_post_full.json').write_text(json.dumps(dict(drive=drive, entries=post), ensure_ascii=False, indent=1), encoding='utf-8')
    dump('sd_manifest_post_full.json', dict(drive=drive, file_count=len(post), entries=post))
    dump('physical_validation.json', out)
    if not ok:
        stop('validação pós-deploy falhou')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('step', choices=('pre', 'copy', 'verify'))
    ap.add_argument('drive')
    a = ap.parse_args()
    {'pre': pre, 'copy': copy, 'verify': verify}[a.step](a.drive.rstrip('\\/'))
