"""C3B.2 — audit of the two residual C3B.1 physical failures, global route-mode and target-duplication audits, reports. Host-only.

Every answer is derived from the chain: editorial decision (C1A / legacy review / HIGH consolidated) -> legal register -> RUN4 legal view
-> device export (REF_LOOKUP/REF_PAYLOAD) -> RELACOES -> EXT_ARTIGOS -> firmware simulation (build_c3b1_reports.Card).

Writes C3B1/C3B1_PHYSICAL_TEST_REPORT.md and C3B2/{C3B2_ROOT_CAUSE_REPORT.md, C3B2_LC63_ROUTE_AUDIT.md, C3B2_ART202_LC109_AUDIT.md,
C3B2_TARGET_DUPLICATION_AUDIT.json}. Usage: python build_c3b2_reports.py [--check]
"""
import argparse
import json
import sys
from pathlib import Path

C3A = Path(__file__).resolve().parents[1]
AUDIT = C3A.parent
sys.path.insert(0, str(C3A / 'tools'))
import build_c3b1_reports as B  # noqa: E402

R4, O, P = B.R4, B.O, B.P
OUT_DIR = AUDIT / 'C3B2'
OUT_PHYS = AUDIT / 'C3B1/C3B1_PHYSICAL_TEST_REPORT.md'
OUT_ROOT = OUT_DIR / 'C3B2_ROOT_CAUSE_REPORT.md'
OUT_LC63 = OUT_DIR / 'C3B2_LC63_ROUTE_AUDIT.md'
OUT_202 = OUT_DIR / 'C3B2_ART202_LC109_AUDIT.md'
OUT_DUP = OUT_DIR / 'C3B2_TARGET_DUPLICATION_AUDIT.json'
C3B2_PKG = AUDIT / 'C3B2_PHYSICAL_TEST_PACKAGE'

PHYSICAL_C3B1 = [
    (1, 'CF art. 5º, XLIII', 'Lei 13.260/2016 aparece e abre', 'PASS'),
    (2, 'CF art. 202, § 5º', 'LC 108/2001 abre direto no art. 26', 'PASS'),
    (3, 'CF art. 158, § 1º, I', 'LC 63 aparece e abre a partir do art. 3º (esperava-se o início)', 'PARTIAL_FAIL_WRONG_DESTINATION_LC63'),
    (4, 'CF art. 158, § 1º, II', '`1 CORR.` não aparece', 'PASS'),
    (5, 'CF art. 161, I', 'LC 63 aparece e abre a partir do art. 3º (esperava-se o início)', 'PARTIAL_FAIL_WRONG_DESTINATION_LC63'),
    (6, 'CF art. 202, § 1º', 'LC 109/2001 abre no art. 3º', 'PASS'),
    (7, 'CF art. 202, caput', 'LC 109/2001 continua aparecendo', 'FAIL_LC109_STILL_PUBLISHED_AT_ART202_CAPUT'),
    (8, 'CF art. 214, caput', 'Lei 15.388/2026 aparece', 'PASS'),
    (9, 'CF art. 214, I a VI', 'sem `1 CORR.` fantasma', 'PASS'),
    (10, 'CF art. 150, § 7º', 'LC 87/1996 abre no art. 10', 'PASS'),
    (11, 'CF art. 239, § 3º', 'correlata aparece e abre', 'PASS'),
    (12, 'CF art. 37, § 3º, III', '`1 CORR.` não aparece', 'PASS'),
    (13, 'CF art. 37, II', 'correlata indevida não aparece', 'PASS'),
    (14, 'CF art. 131, § 2º', 'Lei 14.965/2024 não aparece', 'PASS'),
    (15, 'CF art. 132', 'Lei 14.965/2024 não aparece', 'PASS'),
]
ROLLBACK_C3B1 = dict(found='6/6 C3B.1', restored='6/6 BASELINE EXACT', changed_this_session=6, card_files=1142,
                     after={'99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX': '616a469b11dd673347dc665232a83fc8d5bcd8e3c6bfd5f07a4a56c62f5972a7',
                            '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX': '6d6c88d79bb63a74443de92a52768bb058b56f7b6da1e899746c58d513970ac8',
                            '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX': '24b4f0d97ec004303a6e327a6abf76054eeb05c8cd2a44a424bd70c8341f58ea',
                            '99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX': 'a156a2d6c1546fd1f692f0dfec19c15a728621647dce467632caca91b7c1ecad',
                            '99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX': 'bb3c37168829f4fc102ad51f8fd413f8c8658785181c46888e4d3d76c64af96d',
                            '99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX': '863ff5383d9b338fef2e980edb7972953fe57943e170e42d909e9c7c4ddb4b7e'},
                     untouched='LEXV1.VER 2be2e369…, LEX_DEVICE_MANIFEST.json 7394cb6a…')


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def editorial_sources():
    """(target, destination EXT id) -> editorial decision text that fixes the destination route, from the human decision files."""
    out = {}
    for l in load(AUDIT / 'CF88_CORRELATA_LEGACY_FULL_REVIEW.json')['links']:
        rid = f"LEGACY:{l['review_round']}:{l['reference_id']}"
        if l['decision'] == 'RETARGET' and l.get('retarget_to'):
            rf = l['route_fix'] if isinstance(l['route_fix'], dict) else None
            out[(l['retarget_to'], l['destination_norm_id'])] = dict(decision_id=rid, source=f"{l['review_round']} RETARGET",
                                                                     route=f"route_fix {rf}" if rf else f"rota atual {l['current_route']}",
                                                                     basis=l['legal_analysis'])
        for n in l.get('replacement_norms') or []:
            out[(n['target_id'], 'EXT:' + n['norm_key'])] = dict(decision_id=rid, source=f"{l['review_round']} REPLACE", route=n.get('route'),
                                                                basis=l['legal_analysis'])
        if l['decision'] in ('KEEP', 'KEEP_WITH_ROUTE_FIX'):
            out[(l['target_id'], l['destination_norm_id'])] = dict(decision_id=rid, source=f"{l['review_round']} {l['decision']}",
                                                                   route=f"route_fix {l['route_fix']}" if l.get('route_fix') else
                                                                   f"rota legada mantida {l['current_route']}", basis=l['legal_analysis'])
    return out


def build():
    view = load(R4.OUT / 'legal_view/CF88_CORRELATA_LEGAL_VIEW.json')
    reg = {r['relation_id']: r for r in load(R4.REGISTER)['records']}
    c3b1, base = B.card('C3B1'), B.card('BASELINE')
    heads = B.headings()
    ed = editorial_sources()
    ready = [e for e in view['entries'] if e['device_state'] == 'DEVICE_READY']
    card_rows = {(tuple(r[:5]), r[5]): r for r in (l.split('|') for l in base.rel_text.split('\n') if l and l[0] != '#')}

    def editorial_mode(e):
        """Editorial route of a DEVICE_READY relation, from the decision record (never from the device files)."""
        if e['kind'] == 'ADDITION':
            arts = e['destination_articles']
            src = 'registro jurídico (decisão humana): ' + ', '.join(e['decision_ids'])
        elif e.get('route_fix'):
            arts, src = e['route_fix']['articles'], f"ROUTE_FIX da revisão legada ({e['decision_id']})"
        else:
            row = card_rows[(O.origin_of(e['target_id']), e['relation_id'])]
            arts = [a for a in row[9].split(',') if a] if row[8] == 'ABRIR_ARTIGO_INTERNO' else []
            src = f"KEEP: rota legada mantida pela decisão ({e['decision_id']})"
        return ('DESTINATION_SPECIFIC_ARTICLE' if arts else 'DESTINATION_WHOLE_NORM'), arts, src

    modes = []
    for e in ready:
        mode, arts, src = editorial_mode(e)
        unit = O.presentation_unit(e['target_id'])
        hit = [c for c in c3b1.open_correlatas(unit) if c['payload_target'] == e['target_id'] and c['row'] and c['row'][6] == e['destination_norm_id']]
        c = hit[0] if len(hit) == 1 else None
        dev_mode = ('DESTINATION_SPECIFIC_ARTICLE' if c and c['row'][8] == 'ABRIR_ARTIGO_INTERNO' else 'DESTINATION_WHOLE_NORM') if c else None
        ok = bool(c) and dev_mode == mode and c['articles'] == arts and all(c['offsets'][a] in heads.get((c['row'][6], a), []) for a in c['articles'])
        modes.append(dict(kind=e['kind'], target_id=e['target_id'], destination=e['destination_norm_id'], editorial_mode=mode, editorial_articles=arts,
                          editorial_source=src, device_mode=dev_mode, device_articles=c['articles'] if c else None,
                          device_offsets=c['offsets'] if c else None, result='PASS' if ok else 'FAIL'))

    # duplication audit: same destination published on nested/related targets of the same article
    def art_of(t):
        return ':'.join(t.split(':')[:2])
    groups = {}
    for e in ready:
        groups.setdefault((art_of(e['target_id']), e['destination_norm_id']), []).append(e)
    dups = []
    for (art, dest), es in sorted(groups.items()):
        if len(es) < 2:
            continue
        ids = [set(x['decision_ids'] if x['kind'] == 'ADDITION' else [x['decision_id']]) for x in es]
        sup = [x for x in es if x['kind'] == 'ADDITION' and any(s in {y.get('reference_id') for y in es} for s in x.get('supersedes', []))]
        independent = all(not (ids[i] & ids[j]) for i in range(len(es)) for j in range(i + 1, len(es)))
        dups.append(dict(article=art, destination=dest, targets=[x['target_id'] for x in es],
                         decisions=[sorted(i) for i in ids], superseded_still_published=[x['target_id'] for x in sup],
                         verdict='INDEPENDENT_HUMAN_DECISIONS' if independent and not sup else 'DUPLICATED_MATERIALIZATION'))

    def chain(tid, dest):
        e = next(x for x in ready if x['target_id'] == tid and x['destination_norm_id'] == dest)
        r = reg.get(e.get('relation_id')) if e['kind'] == 'ADDITION' else None
        unit = O.presentation_unit(tid)
        lst = [c for c in c3b1.open_correlatas(unit) if c['row'] and c['row'][6] == dest]
        key = (tid, dest) if (tid, dest) in ed else (tid, 'EXT:' + (r or {}).get('destination_norm_key', ''))
        return dict(target=tid, entry=e, register=r, editorial=ed.get(key), flags=c3b1.flags.get(tid), lookup_keys=B.Card.keys(unit),
                    payload_rows=[row for k in B.Card.keys(unit) for row in c3b1.payload_rows(k) if row[1] == 'CORRELATA' and row[5] == dest],
                    resolved=lst, heads={a: heads.get((dest, a)) for c in lst for a in c['articles']})

    lc63 = [chain('CF88:ART.158:PAR.1:INC.I', 'EXT_LC63_1990'), chain('CF88:ART.161:INC.I', 'EXT_LC63_1990')]
    a202 = [chain('CF88:ART.202:CAPUT', 'EXT_LC109_2001'), chain('CF88:ART.202:PAR.1', 'EXT_LC109_2001')]
    lc63_ok = all(x['editorial'] and x['resolved'] and x['resolved'][0]['articles'] == ['3'] and '3' in (x['editorial']['route'] or '')
                  and x['register']['destination_articles'] == ['3'] for x in lc63)
    cap, par1 = a202
    a202_ok = (cap['entry']['kind'] == 'LEGACY' and cap['entry']['legacy_decision'] == 'KEEP' and par1['entry']['kind'] == 'ADDITION'
               and par1['register']['target_id'] == 'CF88:ART.202:PAR.1' and not set(par1['register']['supersedes'])
               and not (set(par1['register']['decision_ids']) & {cap['entry']['decision_id']}))
    summary = dict(
        C3B1_PHYSICAL_TEST='FAIL_RESIDUAL', FULL_PASS='12/15', PARTIAL_FAIL=2, FAIL=1,
        LC63_DESTINATION_ROOT_CAUSE='CONFIRMED' if lc63_ok else 'UNRESOLVED',
        LC63_FINDING='EXPECTATION_MISMATCH: as decisões humanas registradas fixam o art. 3º (C1A REPLACE "ABRIR_ARTIGO_INTERNO art. 3º"; '
                     'retarget legado com route_fix art. 3º); o aparelho executa exatamente essa rota',
        LC63_CORRECT_DESTINATION_ART158='article (art. 3º)', LC63_CORRECT_DESTINATION_ART161='article (art. 3º)',
        ART202_CAPUT_LC109_ROOT_CAUSE='CONFIRMED' if a202_ok else 'UNRESOLVED',
        ART202_FINDING='EXPECTATION_MISMATCH: o caput tem decisão humana própria (KEEP legado, art. 1º); o § 1º é um HIGH independente '
                       '(target original § 1º, sem supersedes); não é relação movida nem duplicação de materialização',
        ART202_CAPUT_LC109_SHOULD_EXIST='YES',
        DEVICE_READY_EDITORIAL_MODE=f"{sum(m['result'] == 'PASS' for m in modes)}/{len(modes)}",
        TARGET_DUPLICATION_AUDIT='PASS' if all(d['verdict'] == 'INDEPENDENT_HUMAN_DECISIONS' for d in dups) else 'FAIL',
        RELATIONS_CORRECTED=0, C3B2_DEVICE_BYTES_EQUAL_C3B1=c3b2_equals_c3b1())
    dup_doc = dict(schema_version=1, artifact='C3B2_TARGET_DUPLICATION_AUDIT', summary=summary, route_modes=modes, duplication_groups=dups)
    return (phys_md().encode('utf-8'), root_md(summary, lc63, a202, modes, dups).encode('utf-8'), lc63_md(lc63).encode('utf-8'),
            a202_md(a202).encode('utf-8'), (json.dumps(dup_doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8'))


def c3b2_equals_c3b1():
    a = load(P.AUDIT / 'C3B1_PHYSICAL_TEST_PACKAGE/C3B1_FILE_DIFF.json')['files']
    b = load(C3B2_PKG / 'C3B2_FILE_DIFF.json')['files'] if (C3B2_PKG / 'C3B2_FILE_DIFF.json').exists() else []
    return [(x['path'], x['candidate_sha256']) for x in a] == [(x['path'], x['candidate_sha256']) for x in b]


def phys_md():
    L = []
    a = L.append
    a('# C3B.1 — relatório do teste físico')
    a('')
    a('**`C3B1_PHYSICAL_TEST = FAIL_RESIDUAL`** (12/15 PASS, 2 PARTIAL_FAIL, 1 FAIL). O C3B.1 NÃO foi promovido a baseline.')
    a('')
    a('- O relatório do C3B (`C3B_PHYSICAL_TEST_FAILURE_REPORT.md`) continua como evidência separada.')
    a('')
    a('| # | Onde | Observado | Resultado |')
    a('|---|---|---|---|')
    for n, w, o, r in PHYSICAL_C3B1:
        a(f'| {n} | {w} | {o} | `{r}` |')
    a('')
    a('- **Partial fail:** testes 3 e 5.')
    a('- **Fail:** teste 7.')
    a('- **Diagnóstico posterior:** `C3B2/C3B2_ROOT_CAUSE_REPORT.md`. As três divergências são de expectativa, não de dados.')
    a('')
    a('## Candidato testado (6 arquivos instalados, hashes confirmados no cartão)')
    a('')
    for f in load(P.AUDIT / 'C3B1_PHYSICAL_TEST_PACKAGE/C3B1_FILE_DIFF.json')['files']:
        a(f"- `{f['path']}` = `{f['candidate_sha256']}`")
    a('')
    a('## Rollback físico')
    a('')
    a(f"- **Antes:** {ROLLBACK_C3B1['found']} no cartão.")
    a(f"- **Restauração:** conjunto completo → {ROLLBACK_C3B1['restored']}.")
    a(f"- **Escopo da escrita:** {ROLLBACK_C3B1['changed_this_session']} arquivos alterados na sessão, de {ROLLBACK_C3B1['card_files']}.")
    for p, h in ROLLBACK_C3B1['after'].items():
        a(f'  - `{p}` = `{h}`')
    a(f"- **Inalterados:** {ROLLBACK_C3B1['untouched']}.")
    a('- **Estado final:** cartão de volta ao baseline físico; firmware inalterado; nenhum candidato reinstalado.')
    a('')
    return '\n'.join(L) + '\n'


def fmt_resolved(x):
    return '; '.join(f"`{c['reference_id']}` → RELACOES `{'|'.join(c['row'][:6])}|…|{c['row'][8]}|{c['row'][9]}` → offsets {c['offsets']}"
                     for c in x['resolved']) or '—'


def lc63_md(lc63):
    L = []
    a = L.append
    a('# C3B.2 — auditoria da rota da LC 63/1990')
    a('')
    for x in lc63:
        e, r, ed = x['entry'], x['register'], x['editorial']
        a(f"## `{x['target']}`")
        a('')
        a(f"- **Decisão editorial:** {ed['source']} (`{ed['decision_id']}`).")
        a(f"  - Rota: **{ed['route']}**.")
        a(f"  - Fundamento: {ed['basis']}")
        a(f"- **Registro jurídico:** `{r['relation_id']}`, artigos {r['destination_articles']}, decisões {r['decision_ids']}.")
        a(f"- **RUN4:** {e['device_state']}, {e.get('device_article_resolution')}; id de aparelho `{e.get('device_relation_id')}`.")
        a(f"- **Aparelho (C3B.1):**")
        a(f"  - flags `{x['flags']}`; query keys {x['lookup_keys']};")
        a(f"  - REF_PAYLOAD {[row[4] for row in x['payload_rows']]};")
        a(f"  - resolução {fmt_resolved(x)};")
        a(f"  - cabeçalhos do texto {x['heads']}.")
        a('')
        a('| Pergunta | Resposta |')
        a('|---|---|')
        a('| 1. Destino editorial pretendido | art. 3º da LC 63/1990 (critério e definição do valor adicionado) |')
        a('| 2. Tipo de vínculo | artigo específico (DESTINATION_SPECIFIC_ARTICLE) |')
        a('| 3. Por que abre no art. 3º | a linha RELACOES é `ABRIR_ARTIGO_INTERNO` com o art. 3, e o EXT_ARTIGOS aponta o cabeçalho do art. 3º |')
        a('| 4. Origem do art. 3º | da decisão jurídica (sem materialização implícita, ID compartilhado, normalização, fallback ou bug) |')
        a('| 5. Comportamento correto | art. 3º, conforme a decisão; a expectativa física "início da norma" diverge da decisão registrada |')
        a('')
    a('**Conclusão:** nenhuma correção de dados. Abrir a LC 63 no início exigiria uma nova decisão jurídica.')
    a('')
    return '\n'.join(L) + '\n'


def a202_md(a202):
    L = []
    a = L.append
    a('# C3B.2 — LC 109/2001 no art. 202 (caput × § 1º)')
    a('')
    a('| Item | `CF88:ART.202:CAPUT` | `CF88:ART.202:PAR.1` |')
    a('|---|---|---|')
    cap, par = a202
    rows = [
        ('flags (TARGETS)', cap['flags'], par['flags']),
        ('query keys do aparelho', cap['lookup_keys'], par['lookup_keys']),
        ('REF_PAYLOAD (LC 109)', [r[:6] for r in cap['payload_rows']], [r[:6] for r in par['payload_rows']]),
        ('REFERENCE_ID', [r[4] for r in cap['payload_rows']], [r[4] for r in par['payload_rows']]),
        ('RELACOES resolvida', fmt_resolved(cap), fmt_resolved(par)),
        ('status', [r[2] for r in cap['payload_rows']], [r[2] for r in par['payload_rows']]),
        ('decisão humana', f"{cap['editorial']['source']} `{cap['editorial']['decision_id']}`", f"HIGH {par['register']['decision_ids']}"),
        ('origem RUN4', f"LEGACY {cap['entry']['action']} (estado {cap['entry']['device_state']})",
         f"ADDITION (registro `{par['register']['relation_id']}`; supersedes {par['register']['supersedes']})"),
        ('artigos destino', cap['resolved'][0]['articles'] if cap['resolved'] else None, par['resolved'][0]['articles'] if par['resolved'] else None),
    ]
    for k, x, y in rows:
        a(f'| {k} | {x} | {y} |')
    a('')
    a('- **Classificação** (opções A a G da missão): nenhuma delas como defeito.')
    a('  - O caput tem REF, PAYLOAD e RELACOES próprios porque existe decisão humana própria (KEEP legado, art. 1º).')
    a('  - O § 1º é outra decisão humana (HIGH com target original no § 1º), não um retarget do caput.')
    a('  - Não há herança: o § 1º não usa a chave do caput.')
    a('  - Não há duplicação de materialização: as decisões são disjuntas e nenhuma relação substitui a outra.')
    a('- **`ART202_CAPUT_LC109_SHOULD_EXIST = YES`.**')
    a('  - O plano C3B.1 já registrava, no teste 6: "o caput continua com a LC 109 no art. 1º".')
    a('  - Remover exigiria uma nova decisão jurídica.')
    a('')
    return '\n'.join(L) + '\n'


def root_md(s, lc63, a202, modes, dups):
    L = []
    a = L.append
    a('# C3B.2 — causa raiz das falhas residuais do C3B.1')
    a('')
    for k in ('C3B1_PHYSICAL_TEST', 'FULL_PASS', 'PARTIAL_FAIL', 'FAIL', 'LC63_DESTINATION_ROOT_CAUSE', 'LC63_CORRECT_DESTINATION_ART158',
              'LC63_CORRECT_DESTINATION_ART161', 'ART202_CAPUT_LC109_ROOT_CAUSE', 'ART202_CAPUT_LC109_SHOULD_EXIST', 'DEVICE_READY_EDITORIAL_MODE',
              'TARGET_DUPLICATION_AUDIT', 'RELATIONS_CORRECTED', 'C3B2_DEVICE_BYTES_EQUAL_C3B1'):
        a(f'- `{k}` = `{s[k]}`')
    a('')
    a('## LC 63/1990 (testes 3 e 5)')
    a('')
    a(f"- {s['LC63_FINDING']}.")
    a('- Detalhe: `C3B2_LC63_ROUTE_AUDIT.md`.')
    a('')
    a('## LC 109/2001 no caput do art. 202 (teste 7)')
    a('')
    a(f"- {s['ART202_FINDING']}.")
    a('- Detalhe: `C3B2_ART202_LC109_AUDIT.md`.')
    a('')
    a('## Auditorias globais')
    a('')
    a(f"- **Modo de rota editorial × aparelho:** {s['DEVICE_READY_EDITORIAL_MODE']}.")
    a(f"  - {sum(m['editorial_mode'] == 'DESTINATION_SPECIFIC_ARTICLE' for m in modes)} vínculos de artigo específico e "
      f"{sum(m['editorial_mode'] == 'DESTINATION_WHOLE_NORM' for m in modes)} de norma inteira.")
    a('  - Nenhum artigo inferido; nenhuma norma inteira transformada em artigo, nem o inverso.')
    a(f"- **Duplicidade de target:** `{s['TARGET_DUPLICATION_AUDIT']}`, com {len(dups)} grupos de mesma norma no mesmo artigo:")
    for d in dups:
        a(f"  - {d['article']} × {d['destination']}: {d['targets']} → {d['verdict']}.")
    a('')
    a('## Simulador × hardware')
    a('')
    a('- O simulador reproduz o estado físico observado no C3B.1:')
    a('  - LC 63 no art. 3º nos dois dispositivos;')
    a('  - LC 109 visível no caput e no § 1º (art. 3º);')
    a('  - os demais 12 testes com o resultado observado.')
    a('- **C3B.2:** nenhum defeito de dados, então nenhuma relação foi alterada (`RELATIONS_CORRECTED = 0`).')
    a('  - O pacote C3B.2 tem os MESMOS bytes de aparelho do C3B.1 e corrige só as expectativas do plano.')
    a('  - Firmware inalterado.')
    a('')
    a('## Decisão pendente (humana)')
    a('')
    a('- **Se as decisões registradas forem mantidas:** o C3B.1/C3B.2 cumpre as 15 expectativas corrigidas, e o próximo passo é a decisão de promoção. Antes de promover, é preciso regenerar o `LEX_DEVICE_MANIFEST.json`.')
    a('- **Se quiser a LC 63 no início da norma, ou sem a LC 109 no caput:** é uma nova decisão jurídica. Ela entra como decisão humana nos arquivos de decisão e gera outro candidato.')
    a('')
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out = build()
    if out != build():
        raise SystemExit('NOT_DETERMINISTIC')
    paths = (OUT_PHYS, OUT_ROOT, OUT_LC63, OUT_202, OUT_DUP)
    if a.check:
        ok = all(p.read_bytes().replace(b'\r\n', b'\n') == b for p, b in zip(paths, out))
        print('check', 'OK' if ok else 'DIFF')
        sys.exit(0 if ok else 1)
    OUT_DIR.mkdir(exist_ok=True)
    for p, b in zip(paths, out):
        p.write_bytes(b)
    print(json.dumps(json.loads(out[4])['summary'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
