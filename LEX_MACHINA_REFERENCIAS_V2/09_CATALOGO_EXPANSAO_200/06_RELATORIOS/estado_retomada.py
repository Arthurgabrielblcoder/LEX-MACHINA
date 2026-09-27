"""Read-only inventory of the 200 candidates at resume time (after the Codex run).

Never edits existing mission files; writes only 06_RELATORIOS/ESTADO_RETOMADA.json.
Progress is derived from the checkpoint and from the content of the lot files,
not from the names of BUSCA_XXX.json files.
"""
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(out_name='ESTADO_RETOMADA.json', snapshot_at=None):
    candidates = load(ROOT / '00_ENTRADA/CANDIDATAS_200.json')
    checkpoints = load(ROOT / '06_RELATORIOS/CHECKPOINT_LOTES.json')
    # Later, logged revisions (REVISOES_POS_CHECKPOINT.json) legitimately change some closed-lot files.
    rev_path = ROOT / '06_RELATORIOS/REVISOES_POS_CHECKPOINT.json'
    revised = {h['path']: h['sha256_depois'] for h in load(rev_path)['hashes']} if rev_path.exists() else {}
    closed = {}
    hash_problems = []
    for c in checkpoints:
        ok = True
        for h in c['hashes']:
            p = ROOT / h['path']
            if p.exists() and h['path'] in revised and sha(p) == revised[h['path']]:
                continue
            if not p.exists() or sha(p) != h['sha256']:
                ok = False
                hash_problems.append(h['path'])
        closed[c['lote']] = ok
    triage, identity = {}, {}
    for p in sorted((ROOT / '02_TRIAGEM').glob('LOTE_*.json')):
        for e in load(p):
            triage[e['number']] = (e, p.name)
    for p in sorted((ROOT / '01_IDENTIDADE').glob('LOTE_*.json')):
        for e in load(p):
            identity[e['number']] = p.name
    records = []
    for c in candidates:
        n, wid = c['number'], c['work_id']
        batch = (n - 1) // 25 + 1
        files = []
        for rel in [f'03_FONTES/{wid}.json', f'03_FONTES/BUSCA_{n}.json', f'03_FONTES/STEAM_{n:03}.json', f'04_DOSSIERS/{wid}.json']:
            if (ROOT / rel).exists():
                files.append(rel)
        e, lotfile = triage.get(n, (None, None))
        if lotfile:
            files.append(f'02_TRIAGEM/{lotfile}')
        if n in identity:
            files.append(f'01_IDENTIDADE/{identity[n]}')
        status = e['status_triagem'] if e else None
        # identity
        if n in identity and e and e.get('ano') and e.get('criador_principal'):
            identity_status = 'CONFIRMADA'
        elif n in identity:
            identity_status = 'REGISTRADA_INCOMPLETA'
        else:
            identity_status = 'PENDENTE'
        # source
        src_path = ROOT / f'03_FONTES/{wid}.json'
        srcs = load(src_path) if src_path.exists() else []
        if srcs and all(s.get('url') and s.get('tier') for s in srcs):
            source_status = 'FONTE_SELECIONADA_TIER_' + '/'.join(sorted({s['tier'] for s in srcs}))
        elif (ROOT / f'03_FONTES/BUSCA_{n}.json').exists():
            source_status = 'BUSCA_BRUTA_SEM_FONTE_SELECIONADA'
        elif (ROOT / f'03_FONTES/STEAM_{n:03}.json').exists():
            source_status = 'COLETA_STEAM_SEM_SELECAO'
        else:
            source_status = 'AUSENTE'
        # evidence
        dossier = ROOT / f'04_DOSSIERS/{wid}.json'
        if dossier.exists():
            cards = load(dossier).get('evidencias', [])
            valid = [x for x in cards if x.get('not_targeted_to_device') is True and x.get('source', {}).get('url')]
            evidence_status = f'EVIDENCE_CARDS_{len(valid)}' if valid and len(valid) == len(cards) else 'EVIDENCE_CARD_INVALIDO'
        elif status and (status.startswith('REJEITADA') or status == 'FONTE_EM_REVISAO'):
            evidence_status = 'NAO_APLICAVEL_' + status
        else:
            evidence_status = 'AUSENTE'
        completed = bool(e) and closed.get(batch, False)
        records.append(dict(
            candidate_number=n, candidate_id=c['candidate_id'], work_id=wid, titulo=c['titulo_informado'], tipo=c['tipo'],
            identity_status=identity_status, source_status=source_status, evidence_status=evidence_status,
            triage_status=status, batch=batch, batch_checkpoint_closed=batch in closed, completed=completed,
            files_found=files, needs_resume=not completed))
    summary = dict(
        snapshot_at=snapshot_at,
        total=len(records),
        checkpoint_lotes_fechados=sorted(closed),
        checkpoint_hash_problems=hash_problems,
        completed=sum(r['completed'] for r in records),
        needs_resume=sum(r['needs_resume'] for r in records),
        partial_with_raw_search=[r['candidate_number'] for r in records if r['needs_resume'] and r['source_status'] == 'BUSCA_BRUTA_SEM_FONTE_SELECIONADA'],
        first_unprocessed=next((r['candidate_number'] for r in records if r['needs_resume']), None),
        first_without_any_file=next((r['candidate_number'] for r in records if not r['files_found']), None))
    out = dict(summary=summary, candidates=records)
    p = ROOT / '06_RELATORIOS' / out_name
    p.write_bytes((json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main(*sys.argv[1:])
