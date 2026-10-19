"""CC-J2 — physical microSD deploy, DATA ONLY (no flash). MIXED_TRANSACTIONAL_DEPLOY over the immutable CC_J2_MATERIALIZATION_CANDIDATE:
  ADDITIVE_FILES              the new fichas: created on paths that do not exist (temporary .ccj2.tmp, exclusive create, fsync, readback,
                              os.replace onto a NON-existing target, readback)
  AGGREGATE_REPLACEMENT_FILES the 4 files of 99_JURISPRUDENCIA_V2/06_NORMALIZADO (aggregate indexes read at fixed paths by the multinorm
                              firmware): staged as <name>.ccj2.tmp in the SAME directory, all 4 verified, then os.replace one by one (never
                              delete-then-copy), JUR_LOOKUP.IDX last; any failure restores all 4 from the PRE backup and deletes the new fichas.
Rollback = restore exactly the 4 PRE files (byte-exact backup) + delete exactly the created fichas; nothing else is touched.

  python deploy_cc_j2_sd.py pre D:       signature, WHOLE card == CC-J1 post-deploy manifest (1213 files), CF/ADCT 315/198 and CC 29/24
                                         recounted from the card bytes, CC-J2 links absent, candidate hashes, collisions, byte-exact backup
  python deploy_cc_j2_sd.py copy D:      phase 5 (fichas) -> phase 6 (staging of the 4 indexes) -> phase 7 (commit), transactional
  python deploy_cc_j2_sd.py verify D:    readback, POST diff vs PRE, recount + multinorm simulation on the card bytes; ANY failed gate
                                         triggers the rollback automatically
  python deploy_cc_j2_sd.py rollback D:  explicit rollback to CC_J1_FROZEN_29_24
Evidence: JURISPRUDENCE_ENGINE/CC_J2_PHYSICAL_DEPLOY/. Backups (gitignored): DEVICE_INTEGRATION/backups/cc_j2_physical_deploy/.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / 'firmware_multinorm'), str(ROOT / 'JURISPRUDENCE_AUDIT'), str(ROOT / 'LEGAL_TARGET_ID')]
import batch_engine as E  # noqa: E402
import generic_packager as P  # noqa: E402
import juris_types as JT  # noqa: E402
import multinorm_sim as S  # noqa: E402
from deploy_cc_j1_sd import IGNORED_ROOTS, CHUNK, CC_FILE, CF_FILE, TEMA932, TEMA932_SHA, root_for, recount_lexv1  # noqa: E402,F401

CAND = HERE / 'CC_J2_MATERIALIZATION_CANDIDATE'
REC = HERE / 'CC_J2_RATIFICATION_RECORD.json'
BASELINE = HERE / 'CC_J1_PHYSICAL_DEPLOY/sd_manifest_post_full.json'          # card after CC-J1 (1213 files) = MULTINORM_FROZEN_CF315_198_CC29_24
CCJ1_VALID = HERE / 'CC_J1_PHYSICAL_DEPLOY/CC_J1_PHYSICAL_VALIDATION.json'
FW_VALIDATION = HERE / 'firmware_multinorm/PHYSICAL_FLASH/MULTINORM_PHYSICAL_VALIDATION.json'
EV = HERE / 'CC_J2_PHYSICAL_DEPLOY'
BK = ROOT / 'DEVICE_INTEGRATION/backups/cc_j2_physical_deploy'
LAYER = '99_JURISPRUDENCIA_V2/06_NORMALIZADO'
TMP = '.ccj2.tmp'
FROZEN_PREFIXES = {'CORRELATAS': ('99_RELATIONS_V1/', '99_RELATIONS_V2/'), 'LEXV1 (ENTENDA/REFERENCIAS/TARGETS/TEXTO)': ('99_LEX_V1/',),
                   'JURIS_LEGADO': ('99_JURISPRUDENCIA_V2/05_INDICES_ESP32/',), 'FICHAS_EXISTENTES': ('99_JURISPRUDENCIA_V2/03_CONTEUDO/',),
                   'LEI_SECA (pastas das normas)': ('1-', '2-', '3-', '4-', '5-', '6-', '7-', '8-', '9-')}
SHARED = {'CC2002:ART.206:PAR.5:INC.I': ['STJ:SUMULA:503', 'STJ:SUMULA:547', 'STJ:REPETITIVO:639'],
          'CC2002:ART.206:PAR.3:INC.IV': ['STJ:SUMULA:547', 'STJ:REPETITIVO:610'], 'CC2002:ART.1641:INC.II': ['STF:RG:1236', 'STJ:SUMULA:655'],
          'CC2002:ART.1829': ['STF:RG:498', 'STF:RG:809']}


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
    print(json.dumps(value, ensure_ascii=False)[:2500])


def load(name):
    return json.loads((EV / name).read_text(encoding='utf-8'))


def candidate_plan() -> dict:
    m = json.loads((CAND / 'SHA256_MANIFEST.json').read_text(encoding='utf-8'))
    disk = {os.path.relpath(os.path.join(a, f), CAND).replace(os.sep, '/') for a, _, fs in os.walk(CAND) for f in fs}
    if disk != set(m['files']) | {'SHA256_MANIFEST.json'}:
        stop('candidato com arquivos extras ou ausentes')
    for k, v in m['files'].items():
        if rec_of(CAND / k) != dict(bytes=v['bytes'], sha256=v['sha256']):
            stop('hash do candidato diverge: ' + k)
    c = json.loads((CAND / 'host/PREFLIGHT_RESULT.json').read_text(encoding='utf-8'))['checks']
    want = dict(APPROVED_RELATIONS=20, DISTINCT_TARGETS_TOUCHED=18, NEW_TARGETS=15, NEW_FICHAS=17, REUSED_FICHAS=2, REJECTED_MATERIALIZED=0,
                INVALID_TARGETS=0, CC2002='49/39', DUPLICATE_QUERY_KEYS=0, LOOKUP_LOST_RELATIONS=0, CCJ1_REGRESSION=0, CF_REGRESSION=0)
    if any(c[k] != v for k, v in want.items()):
        stop('preflight do candidato não confere: ' + json.dumps({k: c[k] for k in want}))
    d = json.loads((CAND / 'host/DEPLOY_PLAN.json').read_text(encoding='utf-8'))
    files = {k.replace('candidate/SD/', ''): dict(bytes=v['bytes'], sha256=v['sha256']) for k, v in m['files'].items() if k.startswith('candidate/SD/')}
    add, rep = sorted(d['files_to_add']), sorted(d['files_to_replace'])
    if set(add) | set(rep) != set(files) or set(add) & set(rep) or any(not k.startswith(LAYER + '/') for k in rep) or \
            any(not k.startswith('99_JURISPRUDENCIA_V2/03_CONTEUDO/') for k in add):
        stop('plano de deploy inconsistente com o manifesto')
    return dict(manifest_sha256=hashlib.sha256((CAND / 'SHA256_MANIFEST.json').read_bytes()).hexdigest(), build_id=m['build_id'], files=files,
                add=add, replace=rep, before=d['card_files_before'], checks=c)


def layer_rows(look: bytes, recs: bytes):
    """Physical relations of a normalized layer: (target_id, precedent_id) per namespace (same parser as the engine's baseline reader)."""
    out = collections.defaultdict(list)
    for line in recs.decode('utf-8').split('\n')[1:]:
        if line:
            f = line.split('|')
            out[E.namespace_of(E.tail_to_target(f[0][len(f[6]) + 1:]))].append((E.tail_to_target(f[0][len(f[6]) + 1:]), f[6]))
    return out


# ------------------------------------------------------------------ PRE
def pre(drive: str):
    if json.loads(FW_VALIDATION.read_text(encoding='utf-8'))['MULTINORM_FIRMWARE_PHYSICAL_VALIDATION'] != '25/25 PASS':
        stop('firmware multinorma não aprovado fisicamente')
    if json.loads(CCJ1_VALID.read_text(encoding='utf-8'))['PHYSICAL_VALIDATION'] != '36/36 PASS':
        stop('CC-J1 não aprovado fisicamente')
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
    layer = layer_rows((root / LAYER / 'JUR_LOOKUP.IDX').read_bytes(), (root / LAYER / 'JURISPRUDENCIA.IDX').read_bytes())
    cc = layer['CC2002']
    ccj1 = {(r['target_id'], r['precedent']) for r in json.loads((HERE / 'CC_J1_RATIFICATION_RECORD.json').read_text(encoding='utf-8'))['approved_relations']}
    ccj2 = {(r['target_id'], r['precedent']) for r in json.loads(REC.read_text(encoding='utf-8'))['approved_relations']}
    before_ok = {k: man.get(k) == dict(bytes=v['bytes'], sha256=v['sha256']) for k, v in plan['before'].items()}
    collisions = {}
    for rel in plan['add']:
        p = root / rel
        if p.exists():
            collisions[rel] = 'IDENTICAL' if rec_of(p) == plan['files'][rel] else 'DIFFERENT'
        if p.with_name(p.name + TMP).exists():
            collisions[rel + TMP] = 'TEMP_EXISTS'
    for rel in plan['replace']:
        if (root / rel).with_name(Path(rel).name + TMP).exists():
            collisions[rel + TMP] = 'TEMP_EXISTS'
    # byte-exact backup of the 4 files that will be replaced
    backup = {}
    for rel in plan['replace']:
        dst = BK / 'pre_layer' / Path(rel).name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, dst)
        backup[rel] = dict(backup=(str(dst.relative_to(ROOT)) if dst.is_relative_to(ROOT) else str(dst)).replace(os.sep, '/'), **rec_of(dst), card=man.get(rel),
                           exact=rec_of(dst) == man.get(rel))
    rec = dict(SD_DRIVE=drive, card_files=len(man), baseline_files=len(base), diffs=diffs,
               SD_PRE_BASELINE_MATCH='PASS' if not any(diffs.values()) else 'FAIL',
               CF_ADCT_LEXV1=f'{n_rel}/{n_tgt}', CC2002_ON_CARD=f"{len(cc)}/{len({t for t, _ in cc})}",
               CCJ1_RELATIONS_ON_CARD=f"{len(set(cc) & ccj1)}/{len(ccj1)}", CCJ2_RELATIONS_ALREADY_ON_CARD=len(set(cc) & ccj2),
               normalized_by_namespace={k: len(v) for k, v in sorted(layer.items())},
               tema932=dict(path=TEMA932, physical=man.get(TEMA932), TEMA932_PHYSICAL_HASH_MATCH='YES' if man.get(TEMA932, {}).get('sha256') == TEMA932_SHA else 'NO'),
               candidate=dict(manifest_sha256=plan['manifest_sha256'], build_id=plan['build_id'], additive_files=len(plan['add']),
                              aggregate_replacement_files=len(plan['replace']), CCJ2_CANDIDATE='PASS'),
               REPLACEMENT_TARGETS_MATCH_CANDIDATE_BEFORE='PASS' if all(before_ok.values()) else 'FAIL', replacement_before=before_ok,
               UNEXPECTED_FICHA_COLLISIONS=len(collisions), collisions=collisions, backup=backup,
               BACKUP_EXACT='PASS' if all(b['exact'] for b in backup.values()) else 'FAIL',
               planned_add=plan['add'], planned_replace=plan['replace'])
    ok = (rec['SD_PRE_BASELINE_MATCH'] == 'PASS' and rec['CF_ADCT_LEXV1'] == '315/198' and rec['CC2002_ON_CARD'] == '29/24'
          and rec['CCJ1_RELATIONS_ON_CARD'] == '29/29' and rec['CCJ2_RELATIONS_ALREADY_ON_CARD'] == 0 and rec['tema932']['TEMA932_PHYSICAL_HASH_MATCH'] == 'YES'
          and rec['REPLACEMENT_TARGETS_MATCH_CANDIDATE_BEFORE'] == 'PASS' and not collisions and rec['BACKUP_EXACT'] == 'PASS')
    rec['ROLLBACK_TO_CCJ1_29_24_READY'] = 'YES' if ok else 'NO'
    rec['result'] = 'PRE_OK' if ok else 'PRE_FAIL'
    dump('physical_pre.json', rec)
    dump('rollback_plan.json', dict(executed=False, target='CC_J1_FROZEN_29_24', restore={k: dict(from_=v['backup'], sha256=v['sha256'], bytes=v['bytes'])
                                                                                        for k, v in backup.items()},
                                    delete=plan['add'], touch_nothing_else=True, verify_against='CC_J1_PHYSICAL_DEPLOY/sd_manifest_post_full.json (1213 arquivos)'))
    if not ok:
        stop('PRE falhou: ' + json.dumps({k: rec[k] for k in ('SD_PRE_BASELINE_MATCH', 'CF_ADCT_LEXV1', 'CC2002_ON_CARD', 'CCJ2_RELATIONS_ALREADY_ON_CARD',
                                                             'UNEXPECTED_FICHA_COLLISIONS', 'BACKUP_EXACT')}))


# ------------------------------------------------------------------ COPY (transactional)
def write_tmp(src: Path, tmp: Path, r: dict):
    with src.open('rb') as fi, tmp.open('xb') as fo:
        for b in iter(lambda: fi.read(CHUNK), b''):
            fo.write(b)
        fo.flush()
        os.fsync(fo.fileno())
    if rec_of(tmp) != r:
        raise IOError('readback do temporário diverge: ' + tmp.name)


def restore_layer(root: Path, backup: dict):
    out = {}
    for rel, b in backup.items():
        dst = root / rel
        tmp = dst.with_name(dst.name + '.ccj2.restore')
        if tmp.exists():
            tmp.unlink()
        write_tmp(ROOT / b['backup'], tmp, dict(bytes=b['bytes'], sha256=b['sha256']))
        os.replace(tmp, dst)
        out[rel] = rec_of(dst) == dict(bytes=b['bytes'], sha256=b['sha256'])
    return out


def delete_created(root: Path, created: list):
    gone = []
    for rel in created:
        p = root / rel
        if p.exists():
            p.unlink()
            gone.append(rel)
    return gone


def copy(drive: str):
    root = root_for(drive)
    pre_rec = load('physical_pre.json')
    if pre_rec.get('result') != 'PRE_OK':
        stop('PRE não concluído')
    if (EV / 'copy_log.json').exists():
        stop('cópia já registrada; não repetir')
    plan = candidate_plan()
    if plan['manifest_sha256'] != pre_rec['candidate']['manifest_sha256']:
        stop('candidato mudou desde o PRE')
    log = dict(phase5_created=[], phase6_staged=[], phase7_replaced=[], aborted=None, restored=None, deleted=None)
    # ---- phase 5: additive fichas
    try:
        for rel in plan['add']:
            dst = root / rel
            tmp = dst.with_name(dst.name + TMP)
            if dst.exists() or tmp.exists():
                raise IOError('destino ou temporário já existe: ' + rel)
            write_tmp(CAND / 'candidate/SD' / rel, tmp, plan['files'][rel])
            if dst.exists():
                raise IOError('destino surgiu durante a escrita: ' + rel)
            os.replace(tmp, dst)
            if rec_of(dst) != plan['files'][rel]:
                raise IOError('readback final diverge: ' + rel)
            log['phase5_created'].append(rel)
        log['NEW_FICHAS_READBACK'] = 'EXACT' if all(rec_of(root / r) == plan['files'][r] for r in plan['add']) else 'FAIL'
        if log['NEW_FICHAS_READBACK'] != 'EXACT':
            raise IOError('readback das fichas')
    except Exception as e:                                                       # noqa: BLE001
        log.update(aborted=f'fase 5: {e}', deleted=delete_created(root, log['phase5_created']))
        for rel in plan['add']:
            t = (root / rel).with_name(Path(rel).name + TMP)
            if t.exists():
                t.unlink()
        dump('copy_log.json', log)
        stop('fase 5 falhou; fichas removidas')
    # ---- phase 6: staging of the 4 aggregate files in the same directory
    try:
        for rel in plan['replace']:
            dst = root / rel
            tmp = dst.with_name(dst.name + TMP)
            if tmp.exists():
                raise IOError('temporário já existe: ' + rel)
            write_tmp(CAND / 'candidate/SD' / rel, tmp, plan['files'][rel])
            log['phase6_staged'].append(rel)
        if not all(rec_of((root / r).with_name(Path(r).name + TMP)) == plan['files'][r] for r in plan['replace']):
            raise IOError('staging diverge')
        log['NORMALIZED_STAGING'] = 'PASS'
    except Exception as e:                                                       # noqa: BLE001
        for rel in plan['replace']:
            t = (root / rel).with_name(Path(rel).name + TMP)
            if t.exists():
                t.unlink()
        log.update(aborted=f'fase 6: {e}', deleted=delete_created(root, log['phase5_created']))
        dump('copy_log.json', log)
        stop('fase 6 falhou; temporários e fichas removidos; nenhum arquivo antigo substituído')
    # ---- phase 7: commit (os.replace), JUR_LOOKUP.IDX last; any failure restores the 4 PRE files
    order = sorted(plan['replace'], key=lambda k: (k.endswith('JUR_LOOKUP.IDX'), k))
    try:
        for rel in order:
            dst = root / rel
            os.replace(dst.with_name(dst.name + TMP), dst)
            if rec_of(dst) != plan['files'][rel]:
                raise IOError('readback após replace diverge: ' + rel)
            log['phase7_replaced'].append(rel)
        log['NORMALIZED_READBACK'] = 'EXACT' if all(rec_of(root / r) == plan['files'][r] for r in plan['replace']) else 'FAIL'
        if log['NORMALIZED_READBACK'] != 'EXACT':
            raise IOError('readback dos índices')
    except Exception as e:                                                       # noqa: BLE001
        log.update(aborted=f'fase 7: {e}', restored=restore_layer(root, pre_rec['backup']), deleted=delete_created(root, log['phase5_created']))
        for rel in plan['replace']:
            t = (root / rel).with_name(Path(rel).name + TMP)
            if t.exists():
                t.unlink()
        dump('copy_log.json', log)
        stop('fase 7 falhou; os 4 arquivos PRE foram restaurados e as fichas removidas')
    log.update(order_phase7=order, created_count=len(log['phase5_created']), replaced_count=len(log['phase7_replaced']), deleted=[])
    dump('copy_log.json', log)


# ------------------------------------------------------------------ VERIFY
def verify(drive: str):
    root = root_for(drive)
    plan = candidate_plan()
    pre_rec = load('physical_pre.json')
    pre_man = json.loads((BK / 'sd_manifest_pre_full.json').read_text(encoding='utf-8'))['entries']
    post = card_manifest(root)
    added = sorted(set(post) - set(pre_man))
    changed = sorted(k for k in pre_man if k in post and post[k] != pre_man[k])
    removed = sorted(set(pre_man) - set(post))
    deployed_ok = all(post.get(k) == v for k, v in plan['files'].items())
    unexpected = sorted((set(added) - set(plan['add'])) | (set(changed) - set(plan['replace'])) | set(removed))
    frozen = {name: sorted(k for k in changed + removed + added if k.startswith(pref) and k not in plan['files']) for name, pref in FROZEN_PREFIXES.items()}
    # ---- recount + simulation on the CARD bytes
    vis, n_rel, n_tgt = recount_lexv1(root)
    look, recs = (root / LAYER / 'JUR_LOOKUP.IDX').read_bytes(), (root / LAYER / 'JURISPRUDENCIA.IDX').read_bytes()
    fichas = {p.name for p in (root / P.CONTENT).iterdir()}
    pkg = S.Package(look, recs, fichas)
    bk = {Path(k).name: ROOT / v['backup'] for k, v in pre_rec['backup'].items()}
    pkg0 = S.Package(bk['JUR_LOOKUP.IDX'].read_bytes(), bk['JURISPRUDENCIA.IDX'].read_bytes(), fichas)
    layer = layer_rows(look, recs)
    cc = layer['CC2002']
    keys = [l[:5] for l in pkg.lookups]
    ccj1 = sorted((r['target_id'], r['precedent']) for r in json.loads((HERE / 'CC_J1_RATIFICATION_RECORD.json').read_text(encoding='utf-8'))['approved_relations'])
    rrec = json.loads(REC.read_text(encoding='utf-8'))
    ccj2 = sorted((r['target_id'], r['precedent']) for r in rrec['approved_relations'])
    want = collections.defaultdict(list)
    for t, p in cc:
        want[t].append(JT.ficha(p))

    def visit(t):
        _, art, par, inc, ali = P.query_key(t).split('|')
        st = S.carregar(pkg, CC_FILE, art, par, inc, ali)
        ok = st['branch'] == 'MULTINORMA' and [x['arquivo'] for x in st['relations']] == want[t]
        for i, x in enumerate(st['relations']):
            f = root / P.CONTENT / x['arquivo']
            head = f.read_text(encoding='utf-8').split('\n')[:4] if f.is_file() else []
            ok = ok and f.is_file() and x['numero'].split('/')[0] in '\n'.join(head) and x['tribunal'] in '\n'.join(head) and 'OUTRO' not in x['label']
            ok = ok and S.open_and_back(pkg, st, i)['opened'] and S.carregar(pkg, CC_FILE, art, par, inc, ali)['relations'] == st['relations']
        return st, ok
    res2, res1, labels = {}, {}, collections.Counter()
    for t in sorted({t for t, _ in ccj2}):
        st, ok = visit(t)
        res2[t] = dict(ok=ok, labels=[x['label'] for x in st['relations']])
        labels.update(x['label'] for x in st['relations'])
    for t in sorted({t for t, _ in ccj1}):
        st, ok = visit(t)
        res1[t] = dict(ok=ok and all(JT.ficha(p) in [x['arquivo'] for x in st['relations']] for tt, p in ccj1 if tt == t),
                       labels=[x['label'] for x in st['relations']])
    present = set(cc)
    shared = {t: [x['arquivo'] for x in visit(t)[0]['relations']][:len(exp)] == [JT.ficha(p) for p in exp] or
             sorted([x['arquivo'] for x in visit(t)[0]['relations']]) == sorted(JT.ficha(p) for p in exp) for t, exp in SHARED.items()}
    txt = lambda n: (root / P.CONTENT / n).read_text(encoding='utf-8')  # noqa: E731
    critical = dict(
        SUMULA642_ART943=('CC2002:ART.943', 'STJ:SUMULA:642') in present and not any(t.startswith('CC2002:ART.943:') for t, _ in cc),
        TEMA1130_ART76_PU=('CC2002:ART.76:PAR.UNICO', 'STJ:REPETITIVO:1130') in present and 'Tema 1432' in txt('STJ_REPETITIVO_1130.TXT')
        and 'provisional' not in [l.split('|')[4] for l in recs.decode('utf-8').split('\n') if l.startswith('STJ:REPETITIVO:1130:')][0],
        IAC1_ART202_PU=('CC2002:ART.202:PAR.UNICO', 'STJ:IAC:1') in present and 'CPC/1973' in txt('STJ_IAC_1.TXT'),
        TEMA381_EXCLUSION=('CC2002:ART.354', 'STJ:REPETITIVO:381') in present and 'EXCLUSION_CONTEXT' in txt('STJ_REPETITIVO_381.TXT'),
        SUMULA637_EXCEPTION=('CC2002:ART.1210:PAR.2', 'STJ:SUMULA:637') in present and 'EXCEÇÃO' in txt('STJ_SUMULA_637.TXT'),
        SUMULA655_TEMA1236=('CC2002:ART.1641:INC.II', 'STJ:SUMULA:655') in present and 'Tema 1236' in txt('STJ_SUMULA_655.TXT'))
    reused = all(post.get(f'{P.CONTENT}/{n}') == pre_man.get(f'{P.CONTENT}/{n}') for n in ('STF_RG_498.TXT', 'STF_RG_809.TXT')) and \
        sorted(x['arquivo'] for x in visit('CC2002:ART.1829')[0]['relations']) == ['STF_RG_498.TXT', 'STF_RG_809.TXT']
    rejected = [(t, i['precedent']) for i in rrec['items'] if not i['human_approved'] for t in i['original_proposal']['targets']]
    rejected_present = sum(1 for k in rejected if k in present)
    cf_keys = [l[:5] for l in pkg0.lookups if l[0] != 'CC2002']
    cf_changed = [k for k in cf_keys if pkg.exact(*k) is None or pkg.rows(*pkg.exact(*k)) != pkg0.rows(*pkg0.exact(*k))]
    cf_lost = []
    for r in vis:
        norma, art, par, inc, ali = P.query_key(r[0]).split('|')
        hit = pkg.exact(norma, art, par, inc, ali)
        if not hit or JT.ficha(r[5]) not in {S.relation(l, '')['arquivo'] for l in pkg.rows(*hit)}:
            cf_lost.append(r[0] + '|' + r[5])
    art62 = [x['label'] for x in S.carregar(pkg, CF_FILE, '62')['relations']]
    t932 = ([x['caminho'] for x in S.carregar(pkg, CC_FILE, '927', par='unico')['relations'] if x['numero'] == '932'],
            [x['caminho'] for x in S.carregar(pkg, CF_FILE, '7', inc='XXVIII')['relations'] if x['numero'] == '932'])
    n_cc_t = len({t for t, _ in cc})
    lab = {re.sub(r'\d+(/\d+)?', 'n', l) for l in labels}
    out = dict(SD_DRIVE=drive, DEPLOY_MODE='MIXED_TRANSACTIONAL', DEPLOYED_HASHES='EXACT' if deployed_ok else 'FAIL',
               NEW_FICHAS_READBACK='EXACT' if all(post.get(k) == plan['files'][k] for k in plan['add']) else 'FAIL',
               NORMALIZED_READBACK='EXACT' if all(post.get(k) == plan['files'][k] for k in plan['replace']) else 'FAIL',
               added=added, changed=changed, removed=removed, UNEXPECTED_CHANGED_FILES=len(unexpected), unexpected=unexpected,
               card_files_post=len(post), FROZEN_LAYER_CHANGES=sum(len(v) for v in frozen.values()), frozen=frozen,
               CF_ADCT_LEXV1=f'{n_rel}/{n_tgt}', CC2002=f'{len(cc)}/{n_cc_t}', TOTAL=f'{n_rel + len(cc)}/{n_tgt + n_cc_t}',
               normalized_by_namespace={k: len(v) for k, v in sorted(layer.items())}, DUPLICATE_QUERY_KEYS=len(keys) - len(set(keys)),
               CCJ1_RELATIONS=f'{len(set(ccj1) & present)}/{len(ccj1)}', CCJ2_RELATIONS=f'{len(set(ccj2) & present)}/{len(ccj2)}',
               CCJ2_TARGETS_VISIBLE=f"{sum(v['ok'] for v in res2.values())}/{len(res2)}",
               CCJ1_TARGETS=f"{sum(v['ok'] for v in res1.values())}/{len(res1)}",
               SHARED_TARGETS={k: 'PASS' if v else 'FAIL' for k, v in shared.items()}, CRITICAL={k: 'PASS' if v else 'FAIL' for k, v in critical.items()},
               LABELS=sorted(lab), OUTRO_LABELS=sum(1 for l in labels if l.startswith('OUTRO')),
               IAC_LABEL='PASS' if 'IAC 1' in labels else 'FAIL',
               REPETITIVO_STJ_LABEL='PASS' if sum(1 for l in labels if l.startswith('REPETITIVO STJ ')) == sum(1 for _, p in ccj2 if ':REPETITIVO:' in p) else 'FAIL',
               SHARED_FICHAS='PASS' if reused else 'FAIL', REJECTED_RELATIONS_PRESENT=rejected_present,
               CF_RELATIONS=f'{len(vis) - len(cf_lost)}/{len(vis)}', CF_TARGETS=f"{len({r[0] for r in vis if r[0] + '|' + r[5] not in cf_lost})}/{n_tgt}",
               CF_KEYS_CHANGED=len(cf_changed), ART62=art62,
               TEMA932_CROSS_NORM='PASS' if t932[0] == t932[1] == ['/99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_932.TXT'] else 'FAIL',
               CACHE_ENTRIES=len(keys), cases_ccj2=res2, cases_ccj1=res1)
    out['CF_REGRESSION'] = 'PASS' if (not cf_lost and not cf_changed and out['CF_ADCT_LEXV1'] == '315/198' and art62 == ['RG TEMA 33', 'RG TEMA 1196']) else 'FAIL'
    out['CCJ1_REGRESSION'] = 'PASS' if (out['CCJ1_RELATIONS'] == '29/29' and out['CCJ1_TARGETS'] == '24/24') else 'FAIL'
    gates = (out['DEPLOYED_HASHES'] == 'EXACT' and not unexpected and out['FROZEN_LAYER_CHANGES'] == 0 and out['CC2002'] == '49/39'
             and out['TOTAL'] == '364/237' and out['CCJ2_RELATIONS'] == '20/20' and out['CCJ2_TARGETS_VISIBLE'] == '18/18' and out['DUPLICATE_QUERY_KEYS'] == 0
             and all(v == 'PASS' for v in out['SHARED_TARGETS'].values()) and all(v == 'PASS' for v in out['CRITICAL'].values())
             and out['IAC_LABEL'] == out['REPETITIVO_STJ_LABEL'] == out['SHARED_FICHAS'] == out['TEMA932_CROSS_NORM'] == 'PASS' and out['OUTRO_LABELS'] == 0
             and rejected_present == 0 and out['CF_REGRESSION'] == out['CCJ1_REGRESSION'] == 'PASS')
    out['result'] = 'SD_VALIDATED' if gates else 'SD_VALIDATION_FAIL'
    out['READY_FOR_PHYSICAL_TEST'] = 'YES' if gates else 'NO'
    (BK / 'sd_manifest_post_full.json').write_text(json.dumps(dict(drive=drive, entries=post), ensure_ascii=False, indent=1), encoding='utf-8')
    dump('sd_manifest_post_full.json', dict(drive=drive, file_count=len(post), entries=post))
    dump('physical_validation.json', out)
    if not gates:
        rollback(drive, reason='gate de verificação falhou')
        stop('verificação falhou; rollback executado — NÃO recolocar o cartão no aparelho até nova análise')


def rollback(drive: str, reason='rollback explícito'):
    root = root_for(drive)
    pre_rec = load('physical_pre.json')
    plan = candidate_plan()
    restored = restore_layer(root, pre_rec['backup'])
    deleted = delete_created(root, plan['add'])
    for rel in plan['add'] + plan['replace']:
        t = (root / rel).with_name(Path(rel).name + TMP)
        if t.exists():
            t.unlink()
    pre_man = json.loads((BK / 'sd_manifest_pre_full.json').read_text(encoding='utf-8'))['entries']
    now = card_manifest(root)
    dump('rollback_log.json', dict(reason=reason, restored=restored, deleted=deleted, CARD_EQUALS_PRE='YES' if now == pre_man else 'NO'))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('step', choices=('pre', 'copy', 'verify', 'rollback'))
    ap.add_argument('drive')
    a = ap.parse_args()
    {'pre': pre, 'copy': copy, 'verify': verify, 'rollback': rollback}[a.step](a.drive.rstrip('\\/'))
