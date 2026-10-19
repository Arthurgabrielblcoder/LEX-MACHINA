"""CC-J2 — FINAL ratification dossier (host-only; nothing ratified, materialized, deployed or flashed).

Reads the pinned CC-J2 batch (hashes in cc_j2_final_review.PINS; any drift fails), applies the final human review (cc_j2_final_review.FINAL)
with fail-closed rules, re-confirms the GREEN criteria automatically where they are mechanical, projects the CC coverage (never a baseline)
and separates one-time engine cost from recurring batch cost. The preliminary dossier (CC_J2_RATIFICATION_DOSSIER.md/.json) stays as built
by build_cc_j2.py and pinned; the final dossier is CC_J2_RATIFICATION_DOSSIER_FINAL.md/.json.
Usage: python build_cc_j2_final_dossier.py [--check]
"""
import ast
import collections
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import batch_engine as E  # noqa: E402
from cc_j2_final_review import FINAL, NEW_EVIDENCE, PINS  # noqa: E402

DEC = HERE / 'CC_J2_DECISIONS.json'
CC_INDEX = ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json'
PHYSICAL_SD = HERE / 'CC_J1_MATERIALIZATION_CANDIDATE/candidate/SD'
OUT_MD = HERE / 'CC_J2_RATIFICATION_DOSSIER_FINAL.md'
OUT_JSON = HERE / 'CC_J2_RATIFICATION_DOSSIER_FINAL.json'
GROUP_STATE = dict(GREEN='SAFE_FOR_BLOCK_RATIFICATION', YELLOW='INDIVIDUAL_DECISION_REQUIRED', RED='DO_NOT_RATIFY')
# build_cc_j2.py, by function: what recurs in the next batch vs what was one-off for CC-J2 (CC-J1 comparison, reports to move to the engine)
BATCH_ONE_OFF = ('git_sloc', 'ccj1_metrics', 'scale_metrics', 'render_speed', 'CCJ1_TOOLS', 'CCJ2_TOOLS', 'STEP_MAP')
BATCH_TO_ENGINE = ('render_sim', 'render_coverage', 'outputs')


def sha_lf(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def split_sloc(path, one_off, to_engine, commit=None):
    """Code lines of a builder split by top-level definition: one-off, generic (should move to the engine), recurring. With `commit`, the
    builder as frozen at that commit (later missions may extend it; the CC-J2 metric must not drift)."""
    src = (subprocess.run(['git', 'show', f'{commit}:{Path(path).relative_to(ROOT).as_posix()}'], cwd=ROOT, capture_output=True, check=True)
           .stdout.decode('utf-8') if commit else Path(path).read_text(encoding='utf-8'))
    tree = ast.parse(src)
    code_lines = set()
    doc = tree.body[0] if isinstance(tree.body[0], ast.Expr) else None
    skip = set(range(doc.lineno, doc.end_lineno + 1)) if doc else set()
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], 'value', None), ast.Constant):
            skip.update(range(n.body[0].lineno, n.body[0].end_lineno + 1))
    for i, l in enumerate(src.splitlines(), 1):
        if l.strip() and not l.strip().startswith('#') and i not in skip:
            code_lines.add(i)
    cat = collections.Counter()
    owner = {}
    for n in tree.body:
        name = n.name if isinstance(n, ast.FunctionDef) else (n.targets[0].id if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
                                                              else None)
        for i in range(n.lineno, n.end_lineno + 1):
            owner[i] = name
    for i in code_lines:
        nm = owner.get(i)
        cat['ONE_OFF' if nm in one_off else 'GENERIC_TO_MOVE_TO_ENGINE' if nm in to_engine else 'RECURRING'] += 1
    return dict(cat)


def build():
    drift = {k: sha_lf(HERE / k) for k in PINS if sha_lf(HERE / k) != PINS[k]}
    if drift:
        raise SystemExit(f'PINNED_BATCH_DRIFT {sorted(drift)}')
    doc = E.load(DEC)
    decs = {x['id']: x for x in doc['decisions']}
    if sorted(FINAL) != sorted(decs) or len(decs) != 30:
        raise SystemExit('FINAL_REVIEW_DOES_NOT_COVER_THE_30')
    index = {t['target_id'] for t in E.load(CC_INDEX)['targets']}
    _, _, rows = E.physical_layer(PHYSICAL_SD)
    phys = {(r['target_id'], r['precedent_id']) for r in rows if E.namespace_of(r['target_id']) == 'CC2002'}
    items = []
    for i in sorted(decs):
        x, f = decs[i], FINAL[i]
        g, d, ts = f['group'], f['decision'], f['targets']
        for t in ts:
            if t not in index or (t, x['precedent']) in phys:
                raise SystemExit(f'BAD_TARGET {i} {t}')
        auto = {t: x['temporal_auto'].get(t, {}).get('result', 'CURRENT') for t in ts}
        if any(r == 'REVOKED' for r in auto.values()):
            raise SystemExit(f'LINK_TO_REVOKED {i}')
        checks = None
        if g == 'GREEN':
            checks = dict(fonte_oficial=x['source']['tier'] == 'A' and bool(x['source'].get('sha256')),
                          precedente_vigente=x['status_text'] in ('VIGENTE', 'Trânsito em Julgado') or 'Trânsito em Julgado' in x['status_text'],
                          target_existente=all(t in index for t in ts), pertinencia_direta=f['relation'] == 'DIRECT',
                          sem_alerta_temporal=f['temporal'] == 'CURRENT' and all(r == 'CURRENT' for r in auto.values()),
                          sem_duplicacao_cc_j1=not any((t, x['precedent']) in phys for t in ts), sem_superacao=f['superseded'].startswith('não'))
            if d != 'PROMOTE_RECOMMENDED' or not all(checks.values()):
                raise SystemExit(f'GREEN_CRITERIA_FAIL {i} {checks}')
        elif g == 'YELLOW':
            if d not in E.LINKING or not ts or f['reco'] not in ('A', 'B', 'D'):
                raise SystemExit(f'YELLOW_RULE {i}')
        elif g == 'RED':
            if d in E.LINKING or ts or not f.get('reopen'):
                raise SystemExit(f'RED_RULE {i}')
        items.append(dict(id=i, precedent=x['precedent'], label=x['device_label'], device_type=x['device_type'], channel=x['channel'],
                          preliminary=dict(group=x['group'], decision=x['decision'], targets=x['proposed_targets']),
                          group_final=g, state=GROUP_STATE[g], decision_final=d, targets_final=ts, discovered_targets=x['discovered_targets'],
                          temporal=f['temporal'], temporal_auto=auto, confidence=f['confidence'], relation=f['relation'], material=f['material'],
                          evidence=x['evidence'], judgment=x['judgment'], status_text=x['status_text'],
                          source=dict(x['source'], extra=x['source'].get('extra')), risk=f.get('risk'), alternatives=f.get('alts'),
                          recommendation=f.get('reco'), ficha_note=f.get('ficha'), reopen=f.get('reopen'), changed=f.get('changed'),
                          source_anomaly=f.get('source_anomaly'), provisional=f.get('provisional'), green_checks=checks,
                          status='AWAITING_USER_RATIFICATION', human_approved=False))
    g = collections.Counter(it['group_final'] for it in items)
    green = sorted({(t, it['precedent']) for it in items if it['group_final'] == 'GREEN' for t in it['targets_final']})
    fav = sorted({(t, it['precedent']) for it in items if it['group_final'] == 'YELLOW' and it['recommendation'] in ('A', 'B')
                  for t in it['targets_final']})
    pg, pf = sorted(phys | set(green)), sorted(phys | set(green) | set(fav))
    sm = E.load(HERE / 'CC_J2_SCALE_METRICS.json')
    with tempfile.TemporaryDirectory() as d:                        # this builder as frozen with CC-J2 (later pins must not move the metric)
        f = Path(d) / Path(__file__).name
        f.write_bytes(subprocess.run(['git', 'show', 'a8a4d7a:JURISPRUDENCE_ENGINE/' + f.name], cwd=ROOT, capture_output=True, check=True).stdout)
        me = E.sloc(f)[0]
    split = split_sloc(HERE / 'build_cc_j2.py', BATCH_ONE_OFF, BATCH_TO_ENGINE, commit='a8a4d7a')
    scale = dict(ONE_TIME_ENGINE_GENERALIZATION=dict(lines=sm['CC_J2']['code_by_file']['batch_engine.py']['code'], file='batch_engine.py',
                                                     note='custo pago uma vez; não conta como custo recorrente dos próximos lotes'),
                 ONE_TIME_SOURCE_ADAPTER=dict(lines=sm['CC_J2']['code_by_file']['discovery_stj_precedentes.py']['code'], file='discovery_stj_precedentes.py'),
                 CC_J2_BATCH_CONFIG_SPLIT=dict(file='build_cc_j2.py', **split),
                 RECURRING_BATCH_CODE=dict(lines=split.get('RECURRING', 0), what='configuração do lote + canais específicos + build()'),
                 REVIEW_DATA_LINES=dict(cc_j2_review=sm['CC_J2']['code_by_file']['cc_j2_review.py']['review_data'],
                                        cc_j2_final_review=E.sloc(HERE / 'cc_j2_final_review.py', ('PINS', 'NEW_EVIDENCE', 'FINAL', '_A', '_C', '_D'))[1]),
                 FINAL_DOSSIER_CODE_THIS_MISSION=dict(lines=me, file='build_cc_j2_final_dossier.py', kind='nível de lote (não é motor)'),
                 NEW_CORE_ENGINE_CODE_THIS_DOSSIER=0,
                 NEXT_BATCH_TARGET=dict(NEW_CORE_ENGINE_CODE=0, recurring_expected='configuração (norma, canais, temas, exclusões) + tabela de revisão; '
                                        'os renderizadores e o dossiê final genéricos devem ir para o motor antes do próximo lote, uma vez'))
    out = dict(schema_version=1, kind='RATIFICATION_DOSSIER_FINAL', batch='CC-J2', status='AWAITING_USER_RATIFICATION', HUMAN_APPROVED_NEW=0,
               SD_CHANGED='NO', FIRMWARE_CHANGED='NO', baseline='MULTINORM_FROZEN_CF315_198_CC29_24 (CC_J1_FROZEN_29_24)', pins=PINS,
               new_evidence=NEW_EVIDENCE, totals=dict(TOTAL=len(items), GREEN_FINAL=g['GREEN'], YELLOW_FINAL=g['YELLOW'], RED_FINAL=g['RED'],
                                                      SAFE_FOR_BLOCK_RATIFICATION=g['GREEN'], INDIVIDUAL_DECISIONS_REQUIRED=g['YELLOW'],
                                                      DO_NOT_RATIFY=g['RED'],
                                                      GROUP_CHANGES=sum(1 for it in items if it['group_final'] != it['preliminary']['group']),
                                                      PROPOSAL_CHANGES=sum(1 for it in items if it['changed'])),
               projection=dict(CC_PHYSICAL_BASELINE=f"{len(phys)}/{len({t for t, _ in phys})}",
                               PROJECTED_GREEN_RELATIONS=len(pg), PROJECTED_GREEN_TARGETS=len({t for t, _ in pg}),
                               PROJECTED_FULL_RELATIONS=len(pf), PROJECTED_FULL_TARGETS=len({t for t, _ in pf}),
                               green_new_relations=[list(r) for r in green], favorable_yellow_new_relations=[list(r) for r in fav],
                               note='projeção, não baseline; FULL = GREEN_FINAL + YELLOW com recomendação A/B (D fica fora)'),
               provisional_if_ratified=[it['precedent'] for it in items if it['decision_final'] == 'PROMOTE_PROVISIONAL_RECOMMENDED' and
                                        it['group_final'] != 'RED'],
               physical_test_requirements=sorted({it['label'].split(' ')[0] + ' (' + it['device_type'] + ')' for it in items
                                                  if it['group_final'] != 'RED' and it['device_type'] != 'VALIDATED'
                                                  and not it['precedent'].startswith('STJ:SUMULA:')}),
               device_type_note='Súmulas do STJ já foram validadas fisicamente no CC-J1 (36/36); juris_types ainda as marca como não validadas '
                                '(atualizar a tabela fica para fora deste lote fixado). REPETITIVO STJ e IAC nunca foram exibidos no aparelho.',
               scale=scale, items=items)
    return out


def render(o):
    t, p = o['totals'], o['projection']
    by = collections.defaultdict(list)
    for it in o['items']:
        by[it['group_final']].append(it)
    L = ['# CC-J2 — dossiê FINAL de ratificação', '', '```',
         f"TOTAL = {t['TOTAL']} · GREEN_FINAL = {t['GREEN_FINAL']} (SAFE_FOR_BLOCK_RATIFICATION) · YELLOW_FINAL = {t['YELLOW_FINAL']} "
         f"(INDIVIDUAL_DECISION_REQUIRED) · RED_FINAL = {t['RED_FINAL']} (DO_NOT_RATIFY)",
         f"HUMAN_APPROVED_NEW = 0 · SD_CHANGED = NO · FIRMWARE_CHANGED = NO · baseline físico CC = {p['CC_PHYSICAL_BASELINE']}",
         f"PROJECTED_GREEN = {p['PROJECTED_GREEN_RELATIONS']}/{p['PROJECTED_GREEN_TARGETS']} · PROJECTED_FULL = {p['PROJECTED_FULL_RELATIONS']}/"
         f"{p['PROJECTED_FULL_TARGETS']} (projeções, não baseline)", '```', '',
         f"Lote preservado: 30 candidatos, hashes fixados de {len(o['pins'])} arquivos (decisões, revisão, métricas, backlog, simulação, dossiê "
         f"preliminar e fontes oficiais). Mudanças em relação ao dossiê preliminar: {t['GROUP_CHANGES']} de grupo e {t['PROPOSAL_CHANGES']} de proposta, "
         'registradas aqui; `CC_J2_DECISIONS.json` não foi reescrito.', '',
         f"## GREEN FINAL ({t['GREEN_FINAL']}) — SAFE_FOR_BLOCK_RATIFICATION (não ratificado)", '',
         'Os 7 critérios (fonte oficial, precedente vigente, target existente, pertinência direta, sem alerta temporal, sem duplicação com o CC-J1, '
         'sem superação) foram reconferidos em todos.', '', '| ID | Precedente | Alvo | Relação material |', '|---|---|---|---|']
    L += [f"| {it['id']} | {it['label']} | {', '.join(it['targets_final'])} | {it['material']} |" for it in by['GREEN']]
    L += ['', f"## YELLOW FINAL ({t['YELLOW_FINAL']}) — decisão individual", '']
    for it in by['YELLOW']:
        a = it['alternatives']
        L += [f"### {it['id']} — {it['label']}", '', f"- **Target proposto:** {', '.join(it['targets_final'])}" +
              (f" (antes: {', '.join(it['preliminary']['targets'])})" if it['preliminary']['targets'] != it['targets_final'] else ''),
              f"- **Fonte oficial:** {it['source']['url']} (sha256 `{it['source']['sha256'][:12]}…`); {it['judgment']}",
              f"- **Relação material ({it['relation']}):** {it['material']}", f"- **Temporalidade:** {it['temporal']}", f"- **Risco:** {it['risk']}",
              f"- **Alternativas:** A. {a['A']} · B. {a['B']} · C. {a['C']} · D. {a['D']}",
              f"- **Recomendação do motor:** {it['recommendation']} — {it['decision_final'].replace('_RECOMMENDED', '')}"
              + (f"; ficha: {it['ficha_note']}" if it['ficha_note'] else ''), f"- **Minha confiança:** {it['confidence']}"]
        if it['source_anomaly']:
            L.append(f"- **Anomalia da fonte:** {it['source_anomaly']}")
        if it['provisional']:
            L.append(f"- **Provisório:** {it['provisional']['reason']}; gatilho: {it['provisional']['trigger']}; registro: {it['provisional']['registry']}")
        if it['changed']:
            L.append(f"- **Mudança:** {it['changed']}")
        L.append('')
    L += [f"## RED FINAL ({t['RED_FINAL']}) — não ratificar", '', '| ID | Precedente | Categoria | Razão | Reabrir se |', '|---|---|---|---|---|']
    L += [f"| {it['id']} | {it['label']} | {it['decision_final'].replace('_RECOMMENDED', '')}{' (antes ' + it['preliminary']['group'] + ')' if it['changed'] else ''}"
          f" | {it['material']} | {it['reopen']} |" for it in by['RED']]
    s = o['scale']
    L += ['', '## Escala', '', '| Item | Linhas | Natureza |', '|---|---:|---|',
          f"| batch_engine.py | {s['ONE_TIME_ENGINE_GENERALIZATION']['lines']} | ONE_TIME_ENGINE_GENERALIZATION (não recorrente) |",
          f"| discovery_stj_precedentes.py | {s['ONE_TIME_SOURCE_ADAPTER']['lines']} | adapter novo (uma vez por fonte) |",
          f"| build_cc_j2.py, configuração recorrente | {s['CC_J2_BATCH_CONFIG_SPLIT'].get('RECURRING', 0)} | RECURRING_BATCH_CODE |",
          f"| build_cc_j2.py, comparação CC-J1 | {s['CC_J2_BATCH_CONFIG_SPLIT'].get('ONE_OFF', 0)} | só deste lote |",
          f"| build_cc_j2.py, relatórios genéricos | {s['CC_J2_BATCH_CONFIG_SPLIT'].get('GENERIC_TO_MOVE_TO_ENGINE', 0)} | mover para o motor (uma vez) |",
          f"| build_cc_j2_final_dossier.py | {s['FINAL_DOSSIER_CODE_THIS_MISSION']['lines']} | código de lote desta missão (não é motor) |",
          f"| Dados de revisão (preliminar + final) | {sum(s['REVIEW_DATA_LINES'].values())} | julgamento humano, não código |",
          '', 'NEW_CORE_ENGINE_CODE_THIS_DOSSIER = 0. Meta do próximo lote: NEW_CORE_ENGINE_CODE = 0; o custo recorrente esperado é só '
          'configuração e tabela de revisão. Os relatórios genéricos e este gerador de dossiê final devem ir para o motor uma única vez.',
          '', f"Requisitos de teste físico se ratificados: {', '.join(o['physical_test_requirements'])}.",
          f"Entram no registro de provisórios se ratificados: {', '.join(o['provisional_if_ratified'])}.", '',
          'Nada foi ratificado, materializado, implantado ou gravado. A decisão é do usuário.']
    return '\n'.join(L) + '\n'


def main():
    o = build()
    j = (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    md = render(o).encode('utf-8')
    if '--check' in sys.argv:
        ok = all(p.is_file() and p.read_bytes().replace(b'\r\n', b'\n') == v for p, v in ((OUT_JSON, j), (OUT_MD, md)))
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT_JSON.write_bytes(j)
    OUT_MD.write_bytes(md)
    print(json.dumps(dict(o['totals'], **{k: v for k, v in o['projection'].items() if k.isupper()}), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
