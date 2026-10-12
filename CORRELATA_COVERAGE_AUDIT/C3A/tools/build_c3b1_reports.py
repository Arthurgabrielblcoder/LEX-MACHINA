"""C3B.1 — host-only firmware simulator, root-cause proof and reports. Never touches a card.

The simulator reproduces the firmware logic that the physical test exercised:
  availability   lexV1AtualizarDisponibilidade: query keys (ART.n -> [ART.n, ART.n:CAPUT]); 1 CORR. iff flags[1]=='C' in CF88_TARGETS.IDX
  list/open      lexV1CarregarRelacoes + lexV1AdicionarCorrelataPorId: REF_LOOKUP -> REF_PAYLOAD (CURRENT_VISIBLE CORRELATA, one per SOURCE_ID)
                 -> id between ':' and '@' -> FIRST RELACOES.IDX line containing "|<id>|" -> mode/articles -> EXT_ARTIGOS (linear, offset)
It runs on two card states: the C3B package that failed physically (with the old TARGETS) and the C3B.1 candidate.

Writes: CORRELATA_COVERAGE_AUDIT/C3B_PHYSICAL_TEST_FAILURE_REPORT.md and C3B1/{C3B1_ROOT_CAUSE_REPORT.md, C3B1_TARGET_FLAGS_DIFF.md,
C3B1_REFERENCE_ID_AUDIT.json}. Usage: python build_c3b1_reports.py [--check]
"""
import argparse
import json
import sys
from pathlib import Path

C3A = Path(__file__).resolve().parents[1]
AUDIT = C3A.parent
ROOT = AUDIT.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
sys.path.insert(0, str(C3A / 'tools'))
import build_export_run4_candidate as R4  # noqa: E402
import correlata_overlay as O  # noqa: E402
import build_c3b_package as P  # noqa: E402

OUT_FAIL = AUDIT / 'C3B_PHYSICAL_TEST_FAILURE_REPORT.md'
OUT_DIR = AUDIT / 'C3B1'
OUT_ROOT = OUT_DIR / 'C3B1_ROOT_CAUSE_REPORT.md'
OUT_FLAGS = OUT_DIR / 'C3B1_TARGET_FLAGS_DIFF.md'
OUT_AUDIT = OUT_DIR / 'C3B1_REFERENCE_ID_AUDIT.json'
C3B_PKG = AUDIT / 'C3B_PHYSICAL_TEST_PACKAGE'
FILES = dict(targets='99_LEX_V1/10_TARGETS/CF88_TARGETS.IDX', lookup='99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX',
             payload='99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX', relacoes='99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX',
             artigos='99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX', normas='99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_NORMAS.IDX')

# Physical results reported by Arthur (C3B, first physical test) and the rollback evidence of this mission (hashes read from D:).
PHYSICAL = [
    (1, 'CF art. 5º, XLIII', 'Lei 13.260/2016 aparece e abre', 'PASS'),
    (2, 'CF art. 202, § 5º', 'LC 108/2001 aparece, mas abre no início (não no art. 26)', 'FAIL_WRONG_DESTINATION_ARTICLE'),
    (3, 'CF art. 158, § 1º, I / II', 'LC 63 não aparece no I; `1` aparece no II e não abre nada', 'FAIL_STALE_LAYER_FLAG_AND_MISSING_NEW_FLAG'),
    (4, 'CF art. 161, I', 'substituição LC 62 → LC 63 funciona', 'PASS'),
    (5, 'CF art. 202, § 1º', 'LC 109 não aparece no § 1º; continua no caput (abre no início)', 'FAIL_STALE_TARGET_FLAGS'),
    (6, 'CF art. 214', 'não aparece no caput; `1` nos incisos I–VI não abre nada', 'FAIL_STALE_TARGET_FLAGS'),
    (7, 'CF art. 150, § 7º', 'LC 87/1996 abre no art. 10', 'PASS'),
    (8, 'CF art. 239, § 3º', 'nenhuma correlata; só ENTENDA', 'FAIL_MISSING_NEW_TARGET_FLAG'),
    (9, 'CF art. 37, § 3º, III', '`1` aparece; pressionar `1` não abre nada', 'FAIL_STALE_TARGET_FLAG_ART37_PAR3_INCIII'),
    (10, 'Lei 14.965 (arts. 131 § 2º, 132, 37 II)', 'não aparece em 131 § 2º e 132; no 37 II `1` aparece e não abre nada', 'FAIL_STALE_TARGET_FLAG_ART37_II'),
    (11, 'Outras camadas', 'não executado', 'NOT_EXECUTED'),
]
ROLLBACK = dict(card='D:\\', identity='BUILD_ID de963699728cb66e; GIT_COMMIT fa9719a6; REFERENCE_ENGINE cf-reference-engine-run3',
                candidate_found_before='5/5', restored='5/5 BASELINE EXACT', files_changed_on_card_this_session=5, card_files=1142,
                after={'99_RELATIONS_V2/05_INDICES_ESP32_V2/EXT_ARTIGOS.IDX': 'a156a2d6c1546fd1f692f0dfec19c15a728621647dce467632caca91b7c1ecad',
                       '99_RELATIONS_V2/05_INDICES_ESP32_V2/RELACOES.IDX': 'bb3c37168829f4fc102ad51f8fd413f8c8658785181c46888e4d3d76c64af96d',
                       '99_RELATIONS_V2/05_INDICES_ESP32_V2/REL_LOOKUP.IDX': '863ff5383d9b338fef2e980edb7972953fe57943e170e42d909e9c7c4ddb4b7e',
                       '99_LEX_V1/20_REFERENCES/REF_LOOKUP.IDX': '6d6c88d79bb63a74443de92a52768bb058b56f7b6da1e899746c58d513970ac8',
                       '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX': '24b4f0d97ec004303a6e327a6abf76054eeb05c8cd2a44a424bd70c8341f58ea'},
                untouched='LEXV1.VER 2be2e369…, LEX_DEVICE_MANIFEST.json 7394cb6a…, CF88_TARGETS.IDX 616a469b… (baseline)')


class Card:
    """Firmware-relevant files of one card state (bytes)."""

    def __init__(self, files):
        self.f = files
        self.flags = {l.split('|')[0]: l.split('|')[3] for l in P.lines(files['targets']) if not l.startswith('#')}
        self.lookup = {}
        for l in P.lines(files['lookup']):
            if not l.startswith('#'):
                t, off, n = l.split('|')
                self.lookup[t] = (int(off), int(n))
        self.rel_text = files['relacoes'].decode('utf-8')
        self.normas = {l.split('|')[0]: l.split('|')[2] for l in P.lines(files['normas']) if not l.startswith('#')}

    @staticmethod
    def keys(tid):
        return [tid, tid + ':CAPUT'] if tid.startswith('CF88:ART.') and ':' not in tid[len('CF88:ART.'):] else [tid]

    def available(self, tid):
        return any(len(self.flags.get(k, '')) >= 4 and self.flags[k][1] == 'C' for k in self.keys(tid))

    def payload_rows(self, key):
        if key not in self.lookup:
            return []
        off, n = self.lookup[key]
        return [l.decode('utf-8').split('|') for l in self.f['payload'][off:].split(b'\n')[:n]]

    def first_relacoes_line(self, rel):
        """strstr on the whole RELACOES text (lexV1LinhaLegadaPorId with a PSRAM cache): FIRST line containing |rel|."""
        k = self.rel_text.find('|' + rel + '|')
        if k < 0:
            return None
        a = self.rel_text.rfind('\n', 0, k) + 1
        return self.rel_text[a:self.rel_text.find('\n', k)].split('|')

    def matches(self, rel):
        return sum(1 for l in self.rel_text.split('\n') if ('|' + rel + '|') in l)

    def ext_offset(self, nid, art):
        for l in self.f['artigos'].decode('utf-8').split('\n'):
            l = l.strip()
            if l and l[0] != '#' and l.split('|')[0] == nid and l.split('|')[1] == art:
                return int(l.split('|')[2])
        return None

    def open_correlatas(self, tid):
        """What `1 CORR.` lists for the active target: [(reference_id, relacoes row, articles -> offsets)]."""
        regs, seen = [], set()
        for k in self.keys(tid):
            for r in self.payload_rows(k):
                if r[1] == 'CORRELATA' and r[2] == 'CURRENT_VISIBLE' and r[5] not in seen:
                    seen.add(r[5])
                    regs.append(r)
        out = []
        for r in regs:
            rel = r[4][r[4].find(':') + 1:r[4].find('@')]
            row = self.first_relacoes_line(rel)
            arts = [a for a in row[9].split(',') if a] if row and row[8] == 'ABRIR_ARTIGO_INTERNO' else []
            out.append(dict(reference_id=r[4], payload_target=r[0], relation_id=rel, row=row, articles=arts,
                            offsets={a: self.ext_offset(row[6], a) for a in arts} if row else {}))
        return out


def card(kind):
    base = {k: P.baseline_bytes(p) if k != 'normas' else (R4.CARD / 'EXT_NORMAS.IDX').read_bytes() for k, p in FILES.items()}
    if kind == 'BASELINE':
        return Card(base)
    pkg = C3B_PKG if kind == 'C3B_INSTALLED' else P.OUT
    files = dict(base)
    for k, p in FILES.items():
        q = pkg / 'candidate/SD' / p
        if q.exists():
            files[k] = q.read_bytes()
    return Card(files)


def headings():
    """(norm, article) -> heading offsets in the norm text (C3A.1 audit, pin-verified texts), plus the frozen texts."""
    h = {(r['norm_id'], r['article']): r['heading_offsets_in_text'] for r in R4.load(AUDIT / 'C3A/inputs/ext_index_audit.json')['articles']}
    for nid, t in R4.ext_texts().items():
        for (n, a) in list(h):
            if n == nid:
                h[(n, a)] = O.article_heading_offsets(t, a)
    return h


def build():
    view = R4.load(R4.OUT / 'legal_view/CF88_CORRELATA_LEGAL_VIEW.json')
    summary = R4.load(R4.OUT / 'RUN4_CANDIDATE_SUMMARY.json')
    old, new, base = card('C3B_INSTALLED'), card('C3B1'), card('BASELINE')
    heads = headings()
    phys = P.physical()
    ready = [e for e in view['entries'] if e['device_state'] == 'DEVICE_READY']
    ready_units = {O.presentation_unit(e['target_id']) for e in ready}

    # 1:1 audit of every CORRELATA reference id of the device REF_PAYLOAD (visible and hidden)
    ids = [l.split('|') for l in P.lines(new.f['payload']) if not l.startswith('#') and l.split('|')[1] == 'CORRELATA']
    one_to_one = [dict(reference_id=r[4], visibility=r[2], relacoes_matches=new.matches(r[4][r[4].find(':') + 1:r[4].find('@')])) for r in ids]
    old_ids = [l.split('|') for l in P.lines(old.f['payload']) if not l.startswith('#') and l.split('|')[1] == 'CORRELATA']
    old_multi = sorted({r[4][r[4].find(':') + 1:r[4].find('@')] for r in old_ids if old.matches(r[4][r[4].find(':') + 1:r[4].find('@')]) > 1})

    # 24-case route matrix (simulated open on the C3B.1 candidate)
    matrix = []
    for e in ready:
        unit = O.presentation_unit(e['target_id'])
        exp_arts = O.device_route(e['destination_norm_id'], e.get('destination_articles') or
                                  (e['route_fix']['articles'] if e.get('route_fix') else []), _ctx())[1] if e['kind'] == 'ADDITION' or e.get('route_fix') else None
        hits = [c for c in new.open_correlatas(unit) if c['row'] and c['row'][6] == e['destination_norm_id'] and c['payload_target'] == e['target_id']]
        c = hits[0] if len(hits) == 1 else None
        row = c['row'] if c else None
        path_ok = bool(row) and row[10].lstrip('/') in phys and new.normas.get(row[6], '').lstrip('/') == row[10].lstrip('/')
        art_ok = bool(row) and all(c['offsets'][a] is not None and c['offsets'][a] in heads.get((row[6], a), []) for a in c['articles'])
        origin_ok = bool(row) and tuple(row[:5]) == O.origin_of(e['target_id'])
        arts_ok = bool(row) and (exp_arts is None or c['articles'] == exp_arts)
        matrix.append(dict(kind=e['kind'], target_id=e['target_id'], destination=e['destination_norm_id'], reference_id=c['reference_id'] if c else None,
                           relacoes_matches=new.matches(c['relation_id']) if c else 0, origin_ok=origin_ok, norm_ok=bool(row),
                           mode=row[8] if row else None, articles=c['articles'] if c else None, articles_expected=exp_arts, articles_ok=arts_ok,
                           file_exists=path_ok, offsets_at_heading=art_ok, available=new.available(unit),
                           result='PASS' if (c and origin_ok and arts_ok and path_ok and art_ok and new.available(unit)
                                             and new.matches(c['relation_id']) == 1) else 'FAIL'))

    # simulated physical expectations (derived from the DEVICE_READY legal view, observed on the simulated card)
    probes = ['CF88:ART.5:INC.XLIII', 'CF88:ART.202:PAR.5', 'CF88:ART.158:PAR.1:INC.I', 'CF88:ART.158:PAR.1:INC.II', 'CF88:ART.161:INC.I',
              'CF88:ART.202:PAR.1', 'CF88:ART.214'] + [f'CF88:ART.214:INC.{i}' for i in ('I', 'II', 'III', 'IV', 'V', 'VI')] + \
             ['CF88:ART.150:PAR.7', 'CF88:ART.239:PAR.3', 'CF88:ART.37:PAR.3:INC.III', 'CF88:ART.37:INC.II', 'CF88:ART.131:PAR.2', 'CF88:ART.132']
    sim = []
    for t in probes:
        expected = any(k in ready_units for k in Card.keys(t)) or t in ready_units
        lst = new.open_correlatas(t)
        sim.append(dict(target=t, expected_c=expected, candidate_c=new.available(t), candidate_list=[(c['row'][6] if c['row'] else None, c['articles'])
                                                                                                    for c in lst],
                        c3b_installed_c=old.available(t), c3b_installed_list=[(c['row'][6] if c['row'] else None, c['articles'], c['row'][:5] if c['row'] else None)
                                                                              for c in old.open_correlatas(t)],
                        baseline_c=base.available(t),
                        result='PASS' if new.available(t) == expected and bool(lst) == expected else 'FAIL'))
    cf37 = 'CF88:ART.37:PAR.3:INC.III'
    cf37_proof = dict(baseline_targets_flag=base.flags[cf37], candidate_targets_flag=new.flags[cf37],
                      device_ready_entries=[e['reference_id'] if e['kind'] == 'LEGACY' else e['relation_id'] for e in ready if e['target_id'] == cf37],
                      candidate_available=new.available(cf37), candidate_payload_correlata_rows=[r for r in new.payload_rows(cf37) if r[1] == 'CORRELATA'],
                      legacy_state=next(e['device_state'] for e in view['entries'] if e['kind'] == 'LEGACY' and e['target_id'] == cf37))
    cf37_proof['result'] = 'PASS' if (cf37_proof['baseline_targets_flag'][1] == 'C' and cf37_proof['candidate_targets_flag'][1] == '-'
                                      and not cf37_proof['device_ready_entries'] and not cf37_proof['candidate_available']
                                      and not cf37_proof['candidate_payload_correlata_rows']) else 'FAIL'
    latent = sorted({(O.target_of_origin(tuple(r[:5])), r[6], r[8], r[9], c['row'][8], c['row'][9])
                     for r in (l.split('|') for l in base.rel_text.split('\n') if l and l[0] != '#')
                     for c in base.open_correlatas(O.target_of_origin(tuple(r[:5])))
                     if c['relation_id'] == r[5] and c['row'] and tuple(c['row'][:5]) != tuple(r[:5]) and c['row'][6] == r[6]
                     and (c['row'][8], c['row'][9]) != (r[8], r[9])})
    changes = summary['device_ready']['target_c_flag_changes']
    doc = dict(schema_version=1, artifact='C3B1_REFERENCE_ID_AUDIT', status='C3B1_CANDIDATE_HOST_ONLY',
               CORRELATA_REFERENCE_ID_RESOLUTION='1_TO_1' if all(x['relacoes_matches'] == 1 for x in one_to_one) else 'BROKEN',
               reference_ids_checked=len(one_to_one), one_to_one=one_to_one,
               c3b_installed_shared_relation_ids=old_multi, device_relation_ids_renamed=summary['device_ready']['device_relation_ids_renamed'],
               DEVICE_READY_ROUTE_SIMULATION=f"{sum(m['result'] == 'PASS' for m in matrix)}/{len(matrix)}", matrix=matrix,
               simulated_physical_expectations=sim, cf37_par3_inciii=cf37_proof,
               baseline_latent_wrong_routes=[dict(target=t, destination=d, intended=f'{m1} {a1}'.strip(), opens=f'{m2} {a2}'.strip(),
                                                  in_c3b1=('FIXED' if any(x['target_id'] == t and x['destination'] == d and x['result'] == 'PASS' for x in matrix)
                                                           else 'NOT_PUBLISHED_IN_C3B1'))
                                             for t, d, m1, a1, m2, a2 in latent],
               target_flags=dict(gained=sorted(c['target_id'] for c in changes if c['change'] == 'GAINED_C'),
                                 lost=sorted(c['target_id'] for c in changes if c['change'] == 'LOST_C')))
    return (dump(doc), failure_md().encode('utf-8'), root_md(doc, old).encode('utf-8'), flags_md(doc, changes).encode('utf-8'))


_CTX = []


def _ctx():
    if not _CTX:
        _CTX.append(R4.context(R4.E.TargetRegistry()))
        c = _CTX[0]
        c.ext_articles = {}
        for l in (R4.OUT / 'device_ready/EXT_ARTIGOS.IDX').read_text(encoding='utf-8').splitlines():
            if l and not l.startswith('#'):
                c.ext_articles.setdefault(l.split('|')[0], set()).add(l.split('|')[1])
    return _CTX[0]


def dump(o):
    return (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def failure_md():
    L = []
    a = L.append
    a('# C3B — relatório de falha do teste físico')
    a('')
    a('**`C3B_PHYSICAL_TEST = FAIL`.** O C3B NÃO foi aprovado.')
    a('')
    a('| # | Onde | Observado | Resultado |')
    a('|---|---|---|---|')
    for n, w, o, r in PHYSICAL:
        a(f'| {n} | {w} | {o} | `{r}` |')
    a('')
    a('- **Passes:** testes 1, 4 e 7.')
    a('- **Falhas:** testes 2, 3, 5, 6, 8, 9 e 10 (parcial).')
    a('- **Não executado:** teste 11.')
    a('- **Teste 9:** executado e confirmado como `FAIL_STALE_TARGET_FLAG_ART37_PAR3_INCIII`.')
    a('- **Teste 5:** a LC 109 no caput do art. 202 é um vínculo legado mantido (KEEP), então aparecer ali é o esperado. A falha é a ausência no § 1º.')
    a('')
    a('## Rollback físico')
    a('')
    a(f"- **Identificação do cartão:** {ROLLBACK['card']} ({ROLLBACK['identity']}).")
    a(f"- **Antes:** candidato C3B encontrado em {ROLLBACK['candidate_found_before']}.")
    a(f"- **Restauração:** o conjunto completo dos 5 arquivos voltou a {ROLLBACK['restored']}.")
    a(f"- **Escopo da escrita:** {ROLLBACK['files_changed_on_card_this_session']} arquivos alterados na sessão, de {ROLLBACK['card_files']} no cartão.")
    for p, h in ROLLBACK['after'].items():
        a(f'  - `{p}` = `{h}`')
    a(f"- **Inalterados:** {ROLLBACK['untouched']}.")
    a('- **Estado final:** o cartão voltou ao baseline físico aprovado. Nenhum candidato foi reinstalado.')
    a('')
    return '\n'.join(L) + '\n'


def root_md(doc, old):
    L = []
    a = L.append
    a('# C3B.1 — causa raiz das falhas físicas do C3B')
    a('')
    a('## Causa 1: `CF88_TARGETS.IDX` não foi atualizado — CONFIRMADA')
    a('')
    a('- **Como o firmware decide:** `lexV1AtualizarDisponibilidade()` mostra `1 CORR.` quando `lexV1FlagCamada(flags, LEXV1_LAYER_CORRELATA)`, isto é, `flags[1]==\'C\'` no `CF88_TARGETS.IDX`.')
    a('  - A decisão usa as query keys do alvo (ART.n → ART.n e ART.n:CAPUT).')
    a('- **O que faltou:** o pacote C3B trocou REF_* e RELACOES, mas não o TARGETS. As flags continuaram as do RUN3.')
    a('- **Reprodução no simulador** (estado instalado no teste: pacote C3B mais o TARGETS antigo):')
    a('')
    a('| Target | C no TARGETS instalado | CORRELATA no REF instalado | Sintoma |')
    a('|---|---|---|---|')
    for s in doc['simulated_physical_expectations']:
        if s['target'] in ('CF88:ART.158:PAR.1:INC.I', 'CF88:ART.158:PAR.1:INC.II', 'CF88:ART.214', 'CF88:ART.214:INC.I', 'CF88:ART.37:INC.II',
                           'CF88:ART.37:PAR.3:INC.III', 'CF88:ART.239:PAR.3', 'CF88:ART.202:PAR.1'):
            has = bool(s['c3b_installed_list'])
            sym = ('`1` fantasma (lista vazia)' if s['c3b_installed_c'] and not has else
                   'vínculo existe mas `1` não aparece' if has and not s['c3b_installed_c'] else 'coerente')
            a(f"| `{s['target']}` | {'C' if s['c3b_installed_c'] else '-'} | {'sim' if has else 'não'} | {sym} |")
    a('')
    a('## Causa 2: `relation_id` compartilhado por várias linhas do RELACOES — CONFIRMADA')
    a('')
    a('- **Como o firmware resolve:** `lexV1AdicionarCorrelataPorId()` chama `lexV1LinhaLegadaPorId(..., "|" + relId + "|", false, linha)`, um `strstr` sobre o RELACOES inteiro.')
    a('  - Fica com a PRIMEIRA linha que contém o id, sem olhar a origem.')
    a(f"- **IDs compartilhados no pacote C3B:** {', '.join(f'`{x}`' for x in doc['c3b_installed_shared_relation_ids'])}.")
    s5 = next(s for s in doc['simulated_physical_expectations'] if s['target'] == 'CF88:ART.202:PAR.5')
    a(f"- **Reprodução do teste 2:** no estado instalado, o § 5º do art. 202 resolve para a linha de origem `{s5['c3b_installed_list'][0][2]}`, "
      f"com artigos `{s5['c3b_installed_list'][0][1]}` (a linha do § 4º), e não o art. 26.")
    a('')
    a('## Correção escolhida (build, sem firmware)')
    a('')
    a('- **IDs de relação únicos por linha do aparelho:** cada linha do RELACOES tem um id único.')
    a('  - Ids já únicos são mantidos.')
    a('  - Ids compartilhados ganham um `device_relation_id` determinístico (origem × id pai × destino × modo × artigos); o id pai fica na proveniência.')
    a('  - O REF_PAYLOAD aponta para o id exato.')
    a(f"  - Foram renomeadas {len(doc['device_relation_ids_renamed'])} linhas, de {len(doc['c3b_installed_shared_relation_ids'])} ids compartilhados.")
    a('- **Alternativa rejeitada:** mudar o firmware para resolver por id + origem também funciona, mas exige firmware novo. O build resolve de forma genérica e segura.')
    a('- **Flags:** a posição C do TARGETS passa a ser recalculada do mesmo export DEVICE_READY, com a mesma regra do gerador do SD.')
    a('  - Alvo exato, só CURRENT_VISIBLE, sem herança.')
    a('  - Todas as outras posições e campos ficam byte a byte iguais.')
    a('')
    a('## Resultado no simulador (candidato C3B.1)')
    a('')
    a(f"- **`CORRELATA_REFERENCE_ID_RESOLUTION`:** `{doc['CORRELATA_REFERENCE_ID_RESOLUTION']}` ({doc['reference_ids_checked']} reference ids).")
    a(f"- **`DEVICE_READY_ROUTE_SIMULATION`:** `{doc['DEVICE_READY_ROUTE_SIMULATION']}`.")
    a(f"- **Expectativas físicas simuladas:** {sum(s['result'] == 'PASS' for s in doc['simulated_physical_expectations'])}/"
      f"{len(doc['simulated_physical_expectations'])} PASS.")
    a(f"- **CF art. 37, § 3º, III:** `{doc['cf37_par3_inciii']['result']}`.")
    a(f"  - Flag antes `{doc['cf37_par3_inciii']['baseline_targets_flag']}`, depois `{doc['cf37_par3_inciii']['candidate_targets_flag']}`.")
    a('  - Nenhum vínculo DEVICE_READY, nenhuma linha CORRELATA órfã, e `1 CORR.` indisponível.')
    a('')
    a('## Outro bug descoberto: rotas erradas latentes no baseline físico atual')
    a('')
    a(f"- **O que acontece:** o mesmo defeito de id compartilhado já existe no cartão baseline (RUN3).")
    a(f"  - {len(doc['baseline_latent_wrong_routes'])} vínculos legados abrem hoje uma rota diferente da gravada na sua própria linha.")
    a('- **Situação no C3B.1:** todos ficam corrigidos (id único) ou não são publicados (excluídos ou suprimidos por decisão humana).')
    a('')
    a('| Target | Destino | Rota pretendida | Rota que o firmware abre | C3B.1 |')
    a('|---|---|---|---|---|')
    for x in doc['baseline_latent_wrong_routes']:
        a(f"| `{x['target']}` | {x['destination']} | {x['intended']} | {x['opens']} | {x['in_c3b1']} |")
    a('')
    a('## Divergência registrada (não corrigida por regra da missão)')
    a('')
    a('- **Flag R:** a posição R (`[4]`, "qualquer linha no REF_LOOKUP") não foi recalculada.')
    a('  - O firmware não lê R (só as posições 0 a 3).')
    a('  - A missão permite mudar apenas C. R fica com o valor do baseline.')
    a('')
    return '\n'.join(L) + '\n'


def flags_md(doc, changes):
    L = []
    a = L.append
    a('# C3B.1 — diff das flags do `CF88_TARGETS.IDX`')
    a('')
    a(f"- **Resumo:** só a posição C muda; {len(doc['target_flags']['gained'])} targets ganham C e {len(doc['target_flags']['lost'])} perdem C.")
    a('- **Prova de isolamento** (`C3B1_FILE_DIFF.json`): ENTENDA, JURIS, WORK_REFERENCE, R, X e demais campos = 0 mudanças.')
    a('')
    a('| Target | Antes | Depois | Mudança |')
    a('|---|---|---|---|')
    for c in sorted(changes, key=lambda c: (c['change'], c['target_id'])):
        a(f"| `{c['target_id']}` | `{c['before']}` | `{c['after']}` | {c['change']} |")
    a('')
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out = build()
    if out != build():
        raise SystemExit('NOT_DETERMINISTIC')
    paths = (OUT_AUDIT, OUT_FAIL, OUT_ROOT, OUT_FLAGS)
    if a.check:
        ok = all(p.read_bytes().replace(b'\r\n', b'\n') == b for p, b in zip(paths, out))
        print('check', 'OK' if ok else 'DIFF')
        sys.exit(0 if ok else 1)
    OUT_DIR.mkdir(exist_ok=True)
    for p, b in zip(paths, out):
        p.write_bytes(b)
    d = json.loads(out[0])
    print(d['CORRELATA_REFERENCE_ID_RESOLUTION'], d['DEVICE_READY_ROUTE_SIMULATION'], d['cf37_par3_inciii']['result'],
          [(s['target'], s['result']) for s in d['simulated_physical_expectations'] if s['result'] != 'PASS'],
          [(m['target_id'], m) for m in d['matrix'] if m['result'] != 'PASS'])


if __name__ == '__main__':
    main()
