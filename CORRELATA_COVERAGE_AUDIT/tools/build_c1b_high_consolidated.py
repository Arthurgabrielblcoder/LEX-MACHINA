"""CF88_CORRELATA_C1B — consolidation of the 106 original HIGH candidates (Batch01..Batch04) and HIGH closure report.

Every original HIGH candidate_id of the C0 queue appears exactly once, with batch, decision, final target, final relation type, confidence,
temporal status, scope and device route. Batch01/Batch02 predate the mandatory temporal rule: their temporal status comes from the explicit
per-norm mapping below (sources already verified in those batches), marked temporal_source=CONSOLIDATED_MAPPING. New-candidate backlogs are
listed apart and never counted among the 106. Editorial/legal closure only: NOTHING IS APPLIED.

Writes CF88_CORRELATA_C1B_HIGH_CONSOLIDATED.json and CF88_CORRELATA_C1B_HIGH_CLOSURE_REPORT.md. Usage: python build_c1b_high_consolidated.py [--check]
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_c1b_high_batch01 as B1  # noqa: E402
import build_c1b_high_batch02 as B2  # noqa: E402
import build_c1b_high_batch03 as B3  # noqa: E402
import build_c1b_high_batch04 as B4  # noqa: E402

AUDIT = B1.AUDIT
OUT_JSON = AUDIT / 'CF88_CORRELATA_C1B_HIGH_CONSOLIDATED.json'
OUT_MD = AUDIT / 'CF88_CORRELATA_C1B_HIGH_CLOSURE_REPORT.md'
ROUTES = ('MAIN_CORPUS_ROUTE_REQUIRED', 'INGESTION_REQUIRED', 'DEVICE_RESOLVABLE_NOW')

# temporal status of the Batch01/Batch02 norms (default IN_FORCE); every entry was read in the official text of its batch
EARLY_TEMPORAL = {
    'LEI:9717/1998': B3.TS('TRANSITIONAL', revalidate_on='nova LC do art. 40, § 22', note='EC 103/2019, art. 9º'),
    'LC:214/2025': B3.LC214_T, 'LC:227/2026': B3.LC227_T,
    'MP:1317/2025': B3.TS('REVOKED', note='medida provisória convertida na Lei 15.352/2026'),
    'LC:83/1995': B3.TS('REVOKED', note='alterava a LC 69/1991, revogada pela LC 97/1999 (efeito exaurido)'),
    'LEI:15484/2026': B3.TS('IN_FORCE', effective_from='2026-09-03', note='art. 7º: vigência 30 dias após a publicação (DOU 04/08/2026)'),
}
BATCH01_SUGGESTIONS = [   # suggestions that Batch01 recorded only in notes, made explicit here (not decided)
    B3.BL('Lei nº 8.429/1992 (LIA), art. 23', 'LEI:8429/1992', 'CF88:ART.37:PAR.5', 'art. 23 da LIA: prescrição das ações de improbidade',
          'CORRC0-D961094C030C', 'MEDIUM', 'sugestão do Batch01, fora da fila HIGH original'),
    B3.BL('Lei nº 13.303/2016', 'LEI:13303/2016', 'CF88:ART.173:PAR.1:INC.III', 'estatuto das estatais: regime de licitação do art. 173, § 1º, III',
          'CORRC0-9C3FB3B95B9B', 'MEDIUM', 'sugestão do Batch01'),
    B3.BL('Lei nº 7.783/1989', 'LEI:7783/1989', 'CF88:ART.9', 'art. 1º reproduz e disciplina o caput do art. 9º', 'CORRC0-142570A4C40E', 'MEDIUM',
          'sugestão do Batch01; não herdar do § 2º'),
    B3.BL('Lei nº 7.783/1989', 'LEI:7783/1989', 'CF88:ART.9:PAR.1', 'arts. 10 a 13: atividades essenciais e necessidades inadiáveis', 'CORRC0-142570A4C40E',
          'HIGH', 'sugestão do Batch01; não herdar do § 2º'),
]


def _flags(text):
    return set(re.findall(r'\b[A-Z]{2,}(?:_[A-Z0-9]+)+\b', text or ''))


def rows():
    out = []
    d1 = json.loads(B1.build()[1])
    for d in d1['decisions']:
        sc = d.get('scope') or {}
        scope = sorted(_flags(d['notes']) | set(sc.get('flags', [])) | ({'ESCOPO_FEDERAL_EXECUTIVE'} if sc.get('scope') == 'FEDERAL_EXECUTIVE' else set()))
        t = EARLY_TEMPORAL.get(d['norm_key'], B3.IN_FORCE)
        out.append(_row('BATCH01', d, scope, t, 'CONSOLIDATED_MAPPING'))
    d2 = json.loads(B2.build()[1])
    for d in d2['decisions']:
        t = d.get('temporal') or EARLY_TEMPORAL.get(d['norm_key'], B3.IN_FORCE)
        t = dict(B3.TS(t['temporal_status']), **{k: v for k, v in t.items() if k in ('effective_from', 'early_application_possible', 'revalidate_on', 'note')}) \
            if 'temporal_status' in t else t
        out.append(_row('BATCH02', d, sorted(set(d['scope_flags'])), t, 'BATCH02_INDEPENDENT_REVIEW' if d.get('temporal') else 'CONSOLIDATED_MAPPING'))
    for name, mod in (('BATCH03', B3), ('BATCH04', B4)):
        for d in json.loads(mod.build()[1])['decisions']:
            out.append(_row(name, d, sorted(d['scope']), d['temporal'], name))
    return out, d1, d2


def _row(batch, d, scope, temporal, tsrc):
    ok = d['legal_decision'] in ('APPROVE', 'ADJUST')
    dev = d['device_route_status'] if ok else None
    block = ok and temporal['temporal_status'] == 'VACATIO_LEGIS'
    return dict(batch=batch, candidate_id=d['candidate_id'], target_original=d['target'], namespace=d['target'].split(':')[0], norm_key=d['norm_key'],
                norm_name=d['norm_name'], decision=d['legal_decision'], target_final=d['target_final'], relation_type_final=d['relation_type_final'],
                confidence=d['confidence'], temporal_status=temporal['temporal_status'], temporal=temporal, temporal_source=tsrc, scope=scope,
                device_route_status=dev, device_flags=([dev] + (['TEMPORAL_DEVICE_BLOCK'] if block else [])) if ok else [])


def build():
    rs, d1, d2 = rows()
    q = json.loads(B1.QUEUE.read_text(encoding='utf-8'))
    original = [x['candidate_id'] for x in q['HIGH']]
    ids = [r['candidate_id'] for r in rs]
    if sorted(ids) != sorted(original) or len(ids) != len(set(ids)):
        raise SystemExit(f'HIGH_CONSOLIDATION_MISMATCH missing={sorted(set(original) - set(ids))} extra={sorted(set(ids) - set(original))}')
    order = {c: i for i, c in enumerate(original)}
    idx = {t['target_id']: i for i, t in enumerate(json.loads((B1.ROOT / 'LEGAL_TARGET_ID/derived/CF88_TARGET_INDEX.json').read_text(encoding='utf-8'))['targets'])}
    rs.sort(key=lambda r: (idx.get(r['target_original'], 10 ** 6), r['norm_key'], order[r['candidate_id']]))
    acc = [r for r in rs if r['decision'] in ('APPROVE', 'ADJUST')]
    cnt = Counter(r['decision'] for r in rs)

    def by_ns(f):
        return {ns: sum(1 for r in rs if r['namespace'] == ns and f(r)) for ns in ('CF88', 'ADCT')}
    backlog = []
    seen = set()
    for b in ([dict(b, origin=None, basis=b['reason'], reason_not_decided='sugestão da revisão independente do Batch01', suggested_priority='MEDIUM',
                    status='BACKLOG_NOT_DECIDED') for b in d1['independent_review']['new_candidate_backlog']]
              + BATCH01_SUGGESTIONS + [dict(b, basis=b.get('reason', ''), reason_not_decided='sugestão do Batch02', status='BACKLOG_NOT_DECIDED')
                                       for b in d2['NEW_CANDIDATE_BACKLOG']]
              + B3.NEW_CANDIDATE_BACKLOG + B4.NEW_CANDIDATE_BACKLOG):
        k = (b['norm_key'], b['target_id'])
        if k in seen:
            continue
        seen.add(k)
        backlog.append(dict(norm=b['norm'], norm_key=b['norm_key'], target_id=b['target_id'], basis=b.get('basis'), origin=b.get('origin'),
                            suggested_priority=b['suggested_priority'], reason_not_decided=b.get('reason_not_decided'), status='BACKLOG_NOT_DECIDED'))
    summary = dict(
        HIGH_ORIGINAL_TOTAL=len(original), HIGH_ORIGINAL_REVIEWED=len(rs), HIGH_ORIGINAL_REMAINING=len(original) - len(rs),
        per_batch={b: sum(1 for r in rs if r['batch'] == b) for b in ('BATCH01', 'BATCH02', 'BATCH03', 'BATCH04')},
        decisions={k: cnt.get(k, 0) for k in B1.DECISIONS}, accepted=len(acc),
        accepted_device_route={k: sum(1 for r in acc if r['device_route_status'] == k) for k in ROUTES},
        temporal_device_block=sum(1 for r in acc if 'TEMPORAL_DEVICE_BLOCK' in r['device_flags']),
        vacatio_legis_accepted=sum(1 for r in acc if r['temporal_status'] == 'VACATIO_LEGIS'),
        transitional_accepted=sum(1 for r in acc if r['temporal_status'] == 'TRANSITIONAL'),
        accepted_temporal=dict(sorted(Counter(r['temporal_status'] for r in acc).items())),
        cf_vs_adct=dict(total=by_ns(lambda r: True), accepted=by_ns(lambda r: r['decision'] in ('APPROVE', 'ADJUST')),
                        reject=by_ns(lambda r: r['decision'] == 'REJECT'), hold=by_ns(lambda r: r['decision'] == 'HOLD'),
                        needs_source=by_ns(lambda r: r['decision'] == 'NEEDS_SOURCE')),
        new_candidate_backlog_total=len(backlog),
        new_candidate_backlog_by_priority=dict(sorted(Counter(b['suggested_priority'] for b in backlog).items())))
    doc = dict(schema_version=1, artifact='CF88_CORRELATA_C1B_HIGH_CONSOLIDATED', applied=False, verified_on=B1.VERIFIED_ON,
               baseline=dict(B3.BASE), policy='Fechamento editorial/jurídico da fila HIGH original. Nada aplicado ao Reference Engine.',
               summary=summary, candidates=rs, NEW_CANDIDATE_BACKLOG=backlog)
    return B1.jdump(doc), report(summary, rs, backlog).encode('utf-8')


def report(s, rs, backlog):
    L = []
    a = L.append
    a('# CF88_CORRELATA_C1B — fechamento da fila HIGH original')
    a('')
    a('**Fechamento editorial e jurídico. Nada foi aplicado.** Não houve ADDITIONS, exclusões, RUN4, nem alteração em TARGETS, RELACOES, SD '
      'ou firmware. MEDIUM e LOW não foram iniciados.')
    a('')
    a('## Resultado')
    a('')
    a(f"- **Revisão:** `HIGH_ORIGINAL_REVIEWED = {s['HIGH_ORIGINAL_REVIEWED']}/{s['HIGH_ORIGINAL_TOTAL']}`, `HIGH_ORIGINAL_REMAINING = {s['HIGH_ORIGINAL_REMAINING']}`.")
    a(f"- **Por lote:** {s['per_batch']}.")
    a('')
    a('| Decisão | n |')
    a('|---|---:|')
    for k, v in s['decisions'].items():
        a(f'| {k} | {v} |')
    a(f"| **Aceitos (APPROVE + ADJUST)** | **{s['accepted']}** |")
    a('')
    a('| Aceitos: rota de aparelho / temporal | n |')
    a('|---|---:|')
    for k, v in s['accepted_device_route'].items():
        a(f'| {k} | {v} |')
    a(f"| TEMPORAL_DEVICE_BLOCK | {s['temporal_device_block']} |")
    a(f"| VACATIO_LEGIS | {s['vacatio_legis_accepted']} |")
    a(f"| TRANSITIONAL | {s['transitional_accepted']} |")
    a('')
    a(f"- **Situação temporal dos aceitos:** {s['accepted_temporal']}.")
    a('')
    a('| CF permanente × ADCT | CF | ADCT |')
    a('|---|---:|---:|')
    for k, v in s['cf_vs_adct'].items():
        a(f"| {k} | {v['CF88']} | {v['ADCT']} |")
    a('')
    a('## Pontos para a revisão independente do fechamento')
    a('')
    a('- **HOLD (4):**')
    a('  - art. 40, § 7º × Lei 8.112/1990 (Batch01);')
    a('  - art. 231, §§ 1º, 3º e 6º × Lei 14.701/2023 (Batch04). A lei está sob controle concentrado no STF (ADC 87; ADIs 7582, 7583 e 7586, '
      'anotadas na página oficial).')
    a('- **Vacatio legis:** Lei 14.965/2024 nos arts. 131, § 2º e 132, aceita com `TEMPORAL_DEVICE_BLOCK` até 2028-01-01.')
    a('  - Dívida `FUTURE_EFFECTIVE_CORRELATA_POLICY_REQUIRED`.')
    a('  - O vínculo atual Lei 14.965 × art. 37, II, já visível no RUN3, tem o mesmo problema; registrado para C2.')
    a('- **ADCT:** os aceitos no ADCT dependem da regra de status do motor (UNKNOWN_VALIDITY) para entrar no overlay futuro.')
    a('- **Reforma tributária:** a LC 214/2025 e a LC 227/2026 estão aprovadas em targets específicos, cada um com fundamento próprio.')
    a('  - LC 214: arts. 146, § 1º; 153, § 6º; 156-A, §§ 1º, 5º, 6º, 9º e 13.')
    a('  - LC 227: arts. 155, § 1º e 156-A, § 5º, VII.')
    a('  - Foram rejeitadas as ligações genéricas: 146, III; 153, § 3º; 155, § 2º; 156, § 3º; 159, I.')
    a('')
    a('## Candidatos (106)')
    a('')
    a('| Lote | Target | Norma | Decisão | Natureza final | Target final | Temporal | Aparelho |')
    a('|---|---|---|---|---|---|---|---|')
    for r in rs:
        tf = '=' if r['target_final'] == r['target_original'] else (r['target_final'] or '—')
        a(f"| {r['batch'][-2:]} | `{r['target_original']}` | {r['norm_name']} | {r['decision']} | {r['relation_type_final'] or '—'} | {tf} | "
          f"{r['temporal_status']} | {', '.join(r['device_flags']) or '—'} |")
    a('')
    a(f"## NEW_CANDIDATE_BACKLOG ({s['new_candidate_backlog_total']}; fora dos 106; não decidido)")
    a('')
    a(f"- **Por prioridade sugerida:** {s['new_candidate_backlog_by_priority']}.")
    a('')
    for b in backlog:
        a(f"- {b['norm']} × `{b['target_id']}` ({b['suggested_priority']}), origem `{b['origin'] or '—'}`")
    a('')
    a('## Próximo passo')
    a('')
    a('- Revisão independente dos Batch03 e Batch04 e do fechamento.')
    a('- Depois, decisão arquitetural (overlay CORRELATA_ADDITIONS, regra do ADCT, política de vacatio e rota do acervo principal).')
    a('- Nada de MEDIUM ou LOW antes disso.')
    a('')
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out = build()
    if out != build():
        raise SystemExit('NOT_DETERMINISTIC')
    paths = (OUT_JSON, OUT_MD)
    if a.check:
        ok = all(p.read_bytes().replace(b'\r\n', b'\n') == b for p, b in zip(paths, out))
        print('check', 'OK' if ok else 'DIFF')
        sys.exit(0 if ok else 1)
    for p, b in zip(paths, out):
        p.write_bytes(b)
    print(json.dumps(json.loads(out[0])['summary'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
