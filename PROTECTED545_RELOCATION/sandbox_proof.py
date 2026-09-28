"""P545A sandbox proof: simulate protected545 relocation OUTSIDE the repository.

Copies (never moves) the original proof and all 545 protected members into an external sandbox, then inside the sandbox:
  BEFORE  derived verifier -> 545 ORIGINAL_PATH_PRESENT; legacy protected545 check -> PASS
  MOVE    relocates representative candidate directories (REFERENCIAS json, JURIS IDX, firmware) to a sandbox archive
  AFTER   derived verifier -> VALID_RELOCATION for moved members; legacy check -> FAIL (path identity lost, as expected)
  GEN2    second relocation of one directory (lineage A->B->C); ROLLBACK of another (lineage A->B->A)
  NEG     explicit fail-closed scenarios, each restored afterwards
Usage: python sandbox_proof.py <sandbox_dir> <summary_json>
"""
import copy
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import relocation_ledger as rl  # noqa: E402
import verify_relocation as vr  # noqa: E402
import materialize_legacy_view as mlv  # noqa: E402

PROOF = 'LEX_MACHINA_REFERENCIAS_V2/00_CHECKPOINTS/INTEGRITY_BEFORE.json'
MOVE_DIRS = ['LEX_MACHINA_REFERENCIAS_CF_J5', 'LEX_MACHINA_JURIS_CF_J2', 'firmware/LEX_MACHINA_v7.11.0_JURIS_CF_PILOTO']


def inventory(base):
    rows = []
    for dp, _, fn in os.walk(base):
        for x in fn:
            p = Path(dp) / x
            rows.append((p.relative_to(base).as_posix(), vr.file_sha256(p), p.stat().st_size))
    rows.sort(key=lambda r: r[0].encode('utf-8'))
    h = hashlib.sha256()
    for r, s, n in rows:
        h.update(r.encode('utf-8') + b'\0' + s.encode() + b'\0' + str(n).encode() + b'\n')
    return dict(file_count=len(rows), size_bytes=sum(r[2] for r in rows), inventory_sha256=h.hexdigest())


def legacy_protected_check(repo_root, entries):
    """Same expression as r1d_support.integrity() for protected545 (file_hash(ROOT.parent/path) != sha256)."""
    try:
        changed = [e['path'] for e in entries if vr.file_sha256(repo_root / e['path']) != e['sha256']]
        return dict(result='PASS' if not changed else 'FAIL', changed=len(changed))
    except FileNotFoundError as exc:
        return dict(result='FAIL', error='FileNotFoundError', detail=Path(exc.filename).name)


def main(sandbox, summary_path):
    sandbox = Path(sandbox)
    if sandbox.exists():
        raise SystemExit('sandbox already exists: refusing to reuse ' + str(sandbox))
    srepo, sarch = sandbox / 'repo', sandbox / 'archive'
    proof_sha = vr.file_sha256(REPO / PROOF)
    entries = vr.load_json(REPO / PROOF)['files']
    (srepo / PROOF).parent.mkdir(parents=True)
    shutil.copy2(REPO / PROOF, srepo / PROOF)
    for e in entries:
        dst = srepo / e['path']
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / e['path'], dst)
    sarch.mkdir()
    bind = {'REPO_ROOT': str(srepo), 'P545_ARCHIVE': str(sarch)}
    S = dict(sandbox=str(sandbox), original_proof=dict(path=PROOF, sha256=proof_sha, unchanged_in_repo=None),
             copied_members=len(entries), steps={}, negative_tests=[])

    def run(led=None, head=None):
        return vr.verify(PROOF, bind, led, proof_sha, head)

    def brief(res):
        return dict(result=res['result'], counts=res['counts'], ledger_errors=res['ledger_errors'][:5])

    S['steps']['before'] = dict(derived=brief(run()), legacy=legacy_protected_check(srepo, entries))
    led = rl.new_ledger('p545a-sandbox', PROOF, proof_sha, ['P545_ARCHIVE'])
    moved = {}
    for d in MOVE_DIRS:
        pre = inventory(srepo / d)
        (sarch / d).parent.mkdir(parents=True, exist_ok=True)
        os.rename(srepo / d, sarch / d)
        post = inventory(sarch / d)
        assert pre == post, d
        batch = dict(batch_id='sandbox-gen1:' + d, directory_from=dict(root_id='REPO_ROOT', relative_path=d),
                     directory_to=dict(root_id='P545_ARCHIVE', relative_path=d), directory_inventory_sha256=post['inventory_sha256'])
        members = [e for e in entries if e['path'].startswith(d + '/')]
        for e in members:
            rel = e['path'][len(d) + 1:]
            rl.append_event(led, 'RELOCATE', e, dict(root_id='REPO_ROOT', relative_path=e['path']),
                            dict(root_id='P545_ARCHIVE', relative_path=d + '/' + rel), 'P545A sandbox relocation', 'sandbox', batch)
        moved[d] = dict(members=len(members), pre=pre, post=post, byte_identity=pre == post)
    S['moved_directories'] = moved
    after = run(led, led['head']['event_hash'])
    S['steps']['after_move'] = dict(derived=brief(after), legacy=legacy_protected_check(srepo, entries))
    # generation 2 (A->B->C) for JURIS_CF_J2 and ROLLBACK (A->B->A) for CF_J5
    g2 = 'LEX_MACHINA_JURIS_CF_J2'
    (sarch / 'gen2').mkdir()
    os.rename(sarch / g2, sarch / 'gen2' / g2)
    for e in entries:
        if e['path'].startswith(g2 + '/'):
            rl.append_event(led, 'RELOCATE', e, dict(root_id='P545_ARCHIVE', relative_path=e['path']),
                            dict(root_id='P545_ARCHIVE', relative_path='gen2/' + e['path']), 'P545A sandbox generation 2', 'sandbox')
    rb = 'LEX_MACHINA_REFERENCIAS_CF_J5'
    os.rename(sarch / rb, srepo / rb)
    for e in entries:
        if e['path'].startswith(rb + '/'):
            rl.append_event(led, 'ROLLBACK', e, dict(root_id='P545_ARCHIVE', relative_path=e['path']),
                            dict(root_id='REPO_ROOT', relative_path=e['path']), 'P545A sandbox rollback', 'sandbox')
    final = run(led, led['head']['event_hash'])
    lin = next(r for r in final['occurrences'] if r['original_path'].startswith(g2 + '/'))
    rbk = next(r for r in final['occurrences'] if r['original_path'].startswith(rb + '/'))
    S['steps']['after_gen2_and_rollback'] = dict(derived=brief(final),
                                                 lineage_example=dict(original=lin['original_path'], status=lin['status'],
                                                                      chain=[x['from_location']['relative_path'] + ' -> ' + x['to_location']['relative_path'] for x in lin['lineage']]),
                                                 rollback_example=dict(original=rbk['original_path'], status=rbk['status'], events=len(rbk['lineage'])),
                                                 ledger_events=len(led['events']), ledger_head=led['head'])
    rl.dump(led, sandbox / 'P545_RELOCATION_LEDGER.sandbox.json')
    good = copy.deepcopy(led)
    anchor = good['head']['event_hash']
    fw = next(e for e in entries if e['path'].startswith('firmware/LEX_MACHINA_v7.11.0') and e['bytes'] > 0)
    fw_dst = sarch / fw['path']
    j2 = next(e for e in entries if e['path'].startswith(g2 + '/'))

    def neg(name, expect, fn):
        res, detail = fn()
        bad = [r for r in res['occurrences'] if r['status'] not in vr.OK]
        hit = [r for r in bad if r['status'] == expect or expect in r['problems']]
        rec = hit[0] if hit else (bad[0] if bad else None)
        ok = res['result'] == 'FAIL' and (any(expect in e for e in res['ledger_errors']) or bool(hit))
        S['negative_tests'].append(dict(test=name, expected=expect, result=res['result'], failed_explicitly=ok,
                                        observed=(rec['status'], rec['problems'][:2]) if rec else res['ledger_errors'][:2], detail=detail))
        post = run(copy.deepcopy(good), anchor)
        assert post['result'] == 'PASS', ('state not restored after', name, post['counts'])

    def t_missing():
        tmp = fw_dst.with_name(fw_dst.name + '.hidden')
        os.rename(fw_dst, tmp)
        try:
            return run(copy.deepcopy(good), anchor), 'destino renomeado temporariamente'
        finally:
            os.rename(tmp, fw_dst)

    def t_bytes(mutate, label):
        def f():
            orig = fw_dst.read_bytes()
            fw_dst.write_bytes(mutate(orig))
            try:
                return run(copy.deepcopy(good), anchor), label
            finally:
                fw_dst.write_bytes(orig)
        return f

    def t_no_event():
        l2 = rl.new_ledger('p545a-sandbox-neg', PROOF, proof_sha, ['P545_ARCHIVE'])
        for ev in good['events']:
            if ev['occurrence_id'] != rl.occurrence_id(fw):
                e = next(x for x in entries if rl.occurrence_id(x) == ev['occurrence_id'])
                rl.append_event(l2, ev['event_type'], e, ev['from_location'], ev['to_location'], ev['reason'], ev['source_manifest'], ev['batch'])
        return run(l2, l2['head']['event_hash']), 'ledger reconstruido sem a occurrence do firmware'

    def t_two_dest():
        l2 = copy.deepcopy(good)
        extra = sarch / 'dup' / fw['path']
        extra.parent.mkdir(parents=True)
        shutil.copy2(fw_dst, extra)
        rl.append_event(l2, 'RELOCATE', fw, dict(root_id='REPO_ROOT', relative_path=fw['path']),
                        dict(root_id='P545_ARCHIVE', relative_path='dup/' + fw['path']), 'neg', 'neg')
        try:
            return run(l2, l2['head']['event_hash']), 'segundo destino a partir do path original'
        finally:
            shutil.rmtree(sarch / 'dup')

    def t_cycle():
        l2 = copy.deepcopy(good)
        rl.append_event(l2, 'RELOCATE', fw, dict(root_id='P545_ARCHIVE', relative_path=fw['path']),
                        dict(root_id='REPO_ROOT', relative_path=fw['path']), 'neg', 'neg')
        return run(l2, l2['head']['event_hash']), 'RELOCATE de volta ao original (nao ROLLBACK)'

    def t_wrong_path():
        l2 = copy.deepcopy(good)
        rl.append_event(l2, 'RELOCATE', fw, dict(root_id='P545_ARCHIVE', relative_path='nao/existe/' + Path(fw['path']).name),
                        dict(root_id='P545_ARCHIVE', relative_path='x/' + Path(fw['path']).name), 'neg', 'neg')
        return run(l2, l2['head']['event_hash']), 'from_location diferente da localizacao corrente'

    def t_wrong_occ():
        l2 = rl.new_ledger('p545a-sandbox-neg', PROOF, proof_sha, ['P545_ARCHIVE'])
        for ev in good['events']:
            e = copy.deepcopy(next(x for x in entries if rl.occurrence_id(x) == ev['occurrence_id']))
            if ev['occurrence_id'] == rl.occurrence_id(fw):
                e['sha256'] = j2['sha256']
                e['bytes'] = j2['bytes']
                new = rl.append_event(l2, ev['event_type'], e, ev['from_location'], ev['to_location'], ev['reason'], ev['source_manifest'], ev['batch'])
                new['occurrence_id'] = ev['occurrence_id']
                new['event_hash'] = rl.event_hash(new)
                l2['head'] = dict(count=len(l2['events']), event_hash=new['event_hash'])
            else:
                rl.append_event(l2, ev['event_type'], e, ev['from_location'], ev['to_location'], ev['reason'], ev['source_manifest'], ev['batch'])
        return run(l2, l2['head']['event_hash']), 'evento com occurrence_id do firmware e dados originais de outra occurrence (cadeia valida)'

    def t_casefold():
        l2 = copy.deepcopy(good)
        other = next(e for e in entries if e['path'].startswith('LEX_MACHINA_REFERENCIAS_TEMAS_LOTE45_V1/'))
        target = fw['path'].upper()
        rl.append_event(l2, 'RELOCATE', other, dict(root_id='REPO_ROOT', relative_path=other['path']),
                        dict(root_id='P545_ARCHIVE', relative_path=target), 'neg', 'neg')
        return run(l2, l2['head']['event_hash']), 'duas occurrences no mesmo destino por casefold'

    def t_tamper():
        l2 = copy.deepcopy(good)
        l2['events'][3]['to_location']['relative_path'] = 'adulterado/' + l2['events'][3]['to_location']['relative_path']
        return run(l2, anchor), 'to_location de um evento editado sem recalcular a cadeia'

    def t_truncate():
        l2 = copy.deepcopy(good)
        l2['events'].pop()
        l2['head'] = dict(count=len(l2['events']), event_hash=l2['events'][-1]['event_hash'])
        return run(l2, anchor), 'ultimo evento removido e head reescrito; ancora externa detecta'

    neg('1_destino_faltando', 'MISSING', t_missing)
    neg('2_hash_alterado', 'SHA256_MISMATCH', t_bytes(lambda b: bytes([b[0] ^ 1]) + b[1:], 'um byte alterado'))
    neg('3_tamanho_alterado', 'SIZE_MISMATCH', t_bytes(lambda b: b + b'\n', 'um byte acrescentado'))
    neg('4_ledger_sem_occurrence', 'MISSING', t_no_event)
    neg('5_dois_destinos', 'AMBIGUOUS_RELOCATION', t_two_dest)
    neg('6_ciclo', 'CYCLE', t_cycle)
    neg('7_path_errado', 'BROKEN_LINEAGE', t_wrong_path)
    neg('8_occurrence_errada', 'WRONG_OCCURRENCE', t_wrong_occ)
    neg('9_colisao_casefold', 'LOCATION_COLLISION_CASEFOLD_NFC', t_casefold)
    neg('10_ledger_adulterado', 'LEDGER_CORRUPT', t_tamper)
    neg('11_ledger_truncado', 'LEDGER_TRUNCATED_OR_CORRUPT', t_truncate)
    S['final_state'] = brief(run(copy.deepcopy(good), anchor))
    view = sandbox / 'legacy_view'
    mat = mlv.materialize(PROOF, bind, copy.deepcopy(good), view, anchor)
    S['steps']['legacy_view'] = dict(materialize=mat, legacy_on_view=legacy_protected_check(view, entries),
                                     legacy_on_live_relocated_repo=legacy_protected_check(srepo, entries))
    S['original_proof']['unchanged_in_repo'] = vr.file_sha256(REPO / PROOF) == proof_sha
    S['all_negative_failed_explicitly'] = all(t['failed_explicitly'] for t in S['negative_tests'])
    S['verdict'] = 'PASS' if (S['steps']['before']['derived']['result'] == 'PASS' and S['steps']['after_move']['derived']['result'] == 'PASS'
                              and S['steps']['after_move']['legacy']['result'] == 'FAIL'
                              and S['steps']['after_gen2_and_rollback']['derived']['result'] == 'PASS'
                              and S['steps']['legacy_view']['legacy_on_view']['result'] == 'PASS'
                              and all(m['byte_identity'] for m in moved.values()) and S['all_negative_failed_explicitly']
                              and S['original_proof']['unchanged_in_repo']) else 'FAIL'
    Path(summary_path).write_bytes(json.dumps(S, ensure_ascii=False, indent=1).encode('utf-8') + b'\n')
    print(json.dumps(dict(verdict=S['verdict'], steps={k: v['derived'] for k, v in S['steps'].items() if 'derived' in v},
                          legacy_before=S['steps']['before']['legacy'], legacy_after=S['steps']['after_move']['legacy'], legacy_view=S['steps']['legacy_view'],
                          negatives=[(t['test'], t['failed_explicitly'], t['observed']) for t in S['negative_tests']]), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
