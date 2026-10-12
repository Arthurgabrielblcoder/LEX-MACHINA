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

# Final independent HIGH closure review: resolution of the 4 HOLD (batch files keep the decision taken at the time; this layer is final).
STF_P = 'https://portal.stf.jus.br/processos/'
STF_SOURCES = [
    dict(source_id='STF_ADC87_DECISOES', norm='STF, ADC 87 (julgamento conjunto com ADIs 7582, 7583 e 7586), aba Decisões',
         url=STF_P + 'abaDecisoes.asp?incidente=6824155', sha256='385afc97854239dd4976104efa884d6beb0460673abdd7c82c398e71ada39df5', bytes=76207,
         verified_on=B1.VERIFIED_ON),
    dict(source_id='STF_ADC87_ANDAMENTOS', norm='STF, ADC 87, aba Andamentos', url=STF_P + 'abaAndamentos.asp?incidente=6824155',
         sha256='b232dd6628c7c1fd1c206fa5127712b6c7e60ff5cee30322a541a755516d8e94', bytes=3529015, verified_on=B1.VERIFIED_ON),
]
L14701_JUDICIAL = dict(
    judicial_status='STF_PARTIAL_UNCONSTITUTIONALITY', cases=['ADC 87', 'ADI 7582', 'ADI 7583', 'ADI 7586'], merits_decided_on='2025-12-19',
    merits_summary='Procedência parcial (sessão virtual extraordinária de 15 a 18/12/2025, decisão registrada em 19/12/2025): '
                   'inconstitucionais a expressão "na data da promulgação da Constituição Federal" do caput do art. 4º e os §§ 2º, 3º e 4º do '
                   'art. 4º; os §§ 1º e 2º do art. 9º; os arts. 10 e 13; o parágrafo único do art. 20; interpretação conforme nos arts. 5º, 6º, '
                   '14, 18, §§ 1º e 2º, 20, caput, e 22, entre outros.',
    embargos_status='PENDING: segundos embargos de declaração em sessão virtual; pedido de vista do Min. Dias Toffoli em 19/08/2026; '
                    'último andamento oficial em 02/09/2026 (petição); sem julgamento final dos embargos até 2026-10-11.',
    status_checked_until='2026-10-11', REVALIDATE_ON_FINAL_ED=True, CORRELATA_REQUIRES_JUDICIAL_STATUS=True)
L14701_FINAL_T = B3.TS('PARTIAL_EFFECTS', effective_from='2023-10-20', revalidate_on='julgamento final dos embargos de declaração na ADC 87',
                       note='STF, mérito em 2025-12-19: inconstitucionalidade parcial e interpretação conforme; o texto original não está '
                            'integralmente vigente')
FINAL_CLOSURE = {
    'CORRC0-78E258F9B624': dict(
        decision='REJECT', relation_type_final=None, target_final=None, scope=[], temporal=None, judicial=None, sources=[],
        reject_reason='CURRENT_CONSTITUTIONAL_REGIME_NOT_REPRESENTED_BY_LEI_8112',
        analysis='O regime atual do art. 40, § 7º, depois da EC 103/2019, tem regras gerais de pensão para a União e uma regra diferenciada '
                 'para a morte dos servidores do § 4º-B. A Lei 8.112/1990 não deve ser apresentada como regulamentadora atual desse comando. '
                 'A EC 103 não é transformada em CORRELATA infraconstitucional.'),
    'CORRC0-E86B55D28D44': dict(
        decision='ADJUST', relation_type_final='REGULAMENTA', target_final='CF88:ART.231:PAR.1',
        scope=['NON_EXCLUSIVE'], extra_flags=['PARTIAL_EFFECTS', 'JUDICIAL_RESTRICTIONS'], temporal=L14701_FINAL_T, judicial=L14701_JUDICIAL,
        sources=['L14701'],
        analysis='A lei tem relação material direta com a definição e a demarcação das terras tradicionalmente ocupadas (§ 1º). O STF, porém, '
                 'atingiu dispositivos centrais (art. 4º, marco temporal). O vínculo só pode ser exibido com aviso de status judicial; o texto '
                 'original não é tratado como integralmente vigente.'),
    'CORRC0-E0C9C2F5CDBD': dict(
        decision='REJECT', relation_type_final=None, target_final=None, scope=[], temporal=L14701_FINAL_T, judicial=L14701_JUDICIAL, sources=['L14701'],
        reject_reason='CROSS_REFERENCE_ONLY',
        analysis='A remissão ao § 3º não representa disciplina material suficiente do aproveitamento de recursos hídricos e da lavra de '
                 'riquezas minerais em terras indígenas (autorização do Congresso, oitiva das comunidades, participação nos resultados).'),
    'CORRC0-FC57ED913387': dict(
        decision='ADJUST', relation_type_final='COMPLEMENTA', target_final='CF88:ART.231:PAR.6',
        scope=['ESCOPO_PARCIAL', 'NON_EXCLUSIVE'], extra_flags=['PARTIAL_EFFECTS', 'JUDICIAL_RESTRICTIONS', 'DOES_NOT_IMPLEMENT_COMPLEMENTARY_LAW_EXCEPTION'],
        temporal=L14701_FINAL_T, judicial=L14701_JUDICIAL, sources=['L14701'],
        analysis='A lei complementa parcialmente o § 6º (nulidade de atos e efeitos sobre ocupação e domínio). É lei ordinária e não satisfaz '
                 'a exigência de lei complementar para a ressalva do relevante interesse público da União: '
                 'DOES_NOT_IMPLEMENT_COMPLEMENTARY_LAW_EXCEPTION = true.'),
}


def apply_final_closure(rs):
    cands = {c['candidate_id']: c for c in json.loads(B1.CANDS.read_text(encoding='utf-8'))['candidates']}
    for r in rs:
        f = FINAL_CLOSURE.get(r['candidate_id'])
        if not f:
            continue
        assert r['decision'] == 'HOLD', r['candidate_id']
        ok = f['decision'] in ('APPROVE', 'ADJUST')
        t = f['temporal'] or r['temporal']
        dev = cands[r['candidate_id']]['device_status'] if ok else None
        r.update(batch_decision=r['decision'], decision=f['decision'], decision_source='HIGH_FINAL_CLOSURE_REVIEW', target_final=f['target_final'],
                 relation_type_final=f['relation_type_final'], confidence='ALTA' if f['decision'] == 'REJECT' else 'MEDIA', temporal_status=t['temporal_status'],
                 temporal=t, temporal_source='HIGH_FINAL_CLOSURE_REVIEW', scope=sorted(f['scope']), device_route_status=dev,
                 device_flags=[dev] if ok else [], flags=sorted(f.get('extra_flags', [])), reject_reason=f.get('reject_reason'),
                 judicial=f['judicial'], final_analysis=f['analysis'],
                 final_sources=[dict(source_id=k, **B4.SOURCES[k]) for k in f['sources']] + (STF_SOURCES if f['judicial'] else []))
    return rs


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
    rs = apply_final_closure(rs)
    q =json.loads(B1.QUEUE.read_text(encoding='utf-8'))
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
        final_closure_review=dict(source='HIGH_FINAL_CLOSURE_REVIEW', hold_resolved=len(FINAL_CLOSURE),
                                  resolutions={c: f['decision'] for c, f in FINAL_CLOSURE.items()}),
        judicial_restrictions_accepted=sum(1 for r in acc if 'JUDICIAL_RESTRICTIONS' in r.get('flags', [])),
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
    a(f"- **HOLD resolvidos na revisão final ({s['final_closure_review']['hold_resolved']}), fonte `HIGH_FINAL_CLOSURE_REVIEW`:**")
    a('  - art. 40, § 7º × Lei 8.112/1990: REJECT (`CURRENT_CONSTITUTIONAL_REGIME_NOT_REPRESENTED_BY_LEI_8112`);')
    a('  - art. 231, § 1º × Lei 14.701/2023: ADJUST, REGULAMENTA, `PARTIAL_EFFECTS`, `JUDICIAL_RESTRICTIONS`, `NON_EXCLUSIVE`;')
    a('  - art. 231, § 3º × Lei 14.701/2023: REJECT (`CROSS_REFERENCE_ONLY`);')
    a('  - art. 231, § 6º × Lei 14.701/2023: ADJUST, COMPLEMENTA, `ESCOPO_PARCIAL`, `DOES_NOT_IMPLEMENT_COMPLEMENTARY_LAW_EXCEPTION`.')
    a('- **Lei 14.701/2023 no STF** (consulta oficial única, portal do STF, ADC 87): mérito julgado em 2025-12-19 com inconstitucionalidade '
      'parcial (ADC 87; ADIs 7582, 7583 e 7586); segundos embargos pendentes, com vista ao Min. Dias Toffoli desde 19/08/2026. '
      '`judicial_status = STF_PARTIAL_UNCONSTITUTIONALITY`, `REVALIDATE_ON_FINAL_ED = true`.')
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
    a('- Fila HIGH fechada sem HOLD. Arquitetura C2 desenhada em `C2/` (overlay, ADCT, vacatio, status judicial, rota do acervo principal).')
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
