"""PÓS-NOTURNA Partes B/C — ratification dossier + state reconciliation, rendered deterministically from the committed batch decision files
(Batches 03–09), the installed baseline (J2C REF_PAYLOAD) and the ratified Batch02 overlay (J2E). Read-only over inputs; never marks anything
ratified. Writes J2_RATIFICATION_DOSSIER.md and J2_RECONCILIATION.json.
Usage: python render_j2_ratification_dossier.py [--check]
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_j2_batch as G  # noqa: E402
import build_j2d_batch02 as D2  # noqa: E402

BATCHES = (3, 4, 6, 7, 8, 9)
EMPTY = (5,)
ORDER = ('PROMOTE_RECOMMENDED', 'PROMOTE_PROVISIONAL_RECOMMENDED', 'REALLOCATE_RECOMMENDED', 'REJECT_FALSE_POSITIVE_RECOMMENDED',
         'REJECT_TEMPORAL_MISMATCH_RECOMMENDED', 'REJECT_NOT_MATERIAL_RECOMMENDED', 'ALREADY_COVERED', 'DUPLICATE_RECOMMENDATION',
         'UNRESOLVED_EXTERNAL', 'UNRESOLVED_IDENTIFICATION')
TITLE = {'PROMOTE_RECOMMENDED': 'Promoções', 'PROMOTE_PROVISIONAL_RECOMMENDED': 'Promoções provisórias', 'REALLOCATE_RECOMMENDED': 'Realocações',
         'REJECT_FALSE_POSITIVE_RECOMMENDED': 'Rejeições (falso positivo)', 'REJECT_TEMPORAL_MISMATCH_RECOMMENDED': 'Rejeições (descompasso temporal)',
         'REJECT_NOT_MATERIAL_RECOMMENDED': 'Rejeições (não material)', 'ALREADY_COVERED': 'Já cobertas', 'DUPLICATE_RECOMMENDATION': 'Duplicatas',
         'UNRESOLVED_EXTERNAL': 'Não resolvidas (fonte externa)', 'UNRESOLVED_IDENTIFICATION': 'Não resolvidas (identificação)'}
PROMOTING = ('PROMOTE_RECOMMENDED', 'PROMOTE_PROVISIONAL_RECOMMENDED', 'REALLOCATE_RECOMMENDED')
COURT_KLASS = {'SUMULA_TSE': ('TSE', 'SUMULA'), 'SUMULA_STJ': ('STJ', 'SUMULA')}


def label(p):
    court, klass = COURT_KLASS.get(p['klass'], (p['court'], p['klass']))
    if klass == 'RG':
        return f"Tema {p['number']}"
    if klass == 'SUMULA':
        return f"Súmula {p['number']}" + ('' if court == 'STF' else f' {court}')
    return f"{klass.title() if klass in ('INQ', 'PET', 'RCL') else klass} {p['number']}"


def tipo(p):
    court, klass = COURT_KLASS.get(p['klass'], (p['court'], p['klass']))
    return f'{court}/{klass}'


ABBR = ('art', 'arts', 'n', 'nº', 'inc', 'incs', 'Min', 'Rel', 'p', 'al', 'c', 'cf', 'Lei', 'EC', 'ss')


def first_sentence(t):
    for m in re.finditer(r'\. (?=[A-ZÀ-Ú"(])', t):
        prev = re.search(r'([\wº]+)$', t[:m.start()])
        if not prev or prev.group(1) not in ABBR:
            return t[:m.start() + 1]
    return t


def cell(s):
    return str(s).replace('|', '/').replace('\n', ' ')


def load(n):
    p = G.batch_file(n)
    return p, json.loads(p.read_text(encoding='utf-8'))


def relations(x):
    return [(t, p['id']) for t in x['recommended_targets'] for p in x['precedents']] if x['decision'] in PROMOTING else []


def render():
    rows, recon, lines = [], {}, []
    for n in BATCHES:
        p, d = load(n)
        for x in d['decisions']:
            if (x['status'], x['human_approved']) != ('AWAITING_USER_RATIFICATION', False):
                raise SystemExit(f'UNEXPECTED_STATUS {x["recommendation_id"]}')
            rows.append((n, d['level'], p, x))
    installed = ['|'.join(r) for r in D2.current_baseline()]                   # CURRENT_VISIBLE only (fails closed unless 261/160)
    j2e = json.loads(G.J2E.read_text(encoding='utf-8'))['records']
    items, pending, analyzed, covered, prev = G.reconstruct(10)          # counting only: Batch10 is NOT created
    prop_rel = sorted({r for *_, x in rows for r in relations(x)})
    unresolved = [x for *_, x in rows if x['decision'].startswith('UNRESOLVED')]
    recon = dict(
        PHYSICAL_RELATIONS=dict(state='PHYSICALLY_INSTALLED (J2C, CURRENT_VISIBLE)', relations=len(installed),
                                targets=len({l.split('|')[0] for l in installed})),
        RATIFIED_HOST_ONLY_RELATIONS=dict(state='EDITORIALLY_APPROVED_HOST_ONLY (Batch02 → J2E, não instalado)', relations=len(j2e),
                                          variant_A=sum(1 for r in j2e if r.get('variant', 'A') == 'A'),
                                          variant_B_requires_hc_firmware=sum(1 for r in j2e if r.get('variant') == 'B')),
        AWAITING_RATIFICATION_RECOMMENDATIONS=dict(state='UNAPPROVED_RESEARCH_PROPOSAL', batches=[f'BATCH{n:02d}' for n in BATCHES],
                                                   recommendations=len(rows),
                                                   decisions_by_type=dict(sorted(collections.Counter(x['decision'] for *_, x in rows).items())),
                                                   promoting_decisions=sum(1 for *_, x in rows if x['decision'] in PROMOTING),
                                                   proposed_relations_upper_bound=len(prop_rel),
                                                   proposed_targets=len({t for t, _ in prop_rel}),
                                                   proposed_precedents=len({pid for _, pid in prop_rel})),
        UNRESOLVED_RECOMMENDATIONS=dict(count=len(unresolved), ids=[x['recommendation_id'] for x in unresolved]),
        IN_RESEARCH=dict(count=0, note='Batch09 concluído nesta operação; nenhum lote em pesquisa. Batch10 NÃO iniciado.'),
        NOT_RESEARCHED=dict(backlog_pending=len(pending), by_level=dict(sorted(collections.Counter(b['priority'] for b in pending).items())),
                            analyzed_in_batches_01_09=len(analyzed), covered_by_ratified=len(covered)),
        UNRATIFIED_RELATIONS_PUBLISHED=0)
    L = lines.append
    L('# J2 — DOSSIÊ DE RATIFICAÇÃO (Batches 03, 04, 06, 07, 08, 09)')
    L('')
    L('```')
    L('STATUS = AWAITING_USER_RATIFICATION · NADA ESTÁ RATIFICADO NESTE DOSSIÊ · human_approved = false em todas as linhas')
    L(f'Gerado por render_j2_ratification_dossier.py a partir dos JSONs dos lotes · Batch05 = vazio (fechamento HIGH)')
    L('```')
    L('')
    L('**Como ler:**')
    L('')
    L('- **Linha:** cada linha é uma recomendação do backlog J0 (`J0-BL-nnn`), com uma única decisão proposta.')
    L('- **Realocação:** aparece como `ORIGINAL → CORRETO`.')
    L('- **Promoção provisória:** traz natureza, último status e gatilho de revalidação.')
    L('- **Relação:** cada relação é um par *target × precedente*; uma decisão pode gerar várias.')
    L('')
    hdr = '| # | Recommendation ID | Target original | Precedente | Tipo | Target recomendado | Decisão proposta | Status | Razão objetiva |'
    sep = '|---|---|---|---|---|---|---|---|---|'
    for n in BATCHES:
        p, d = load(n)
        L(f'## Batch{n:02d} ({d["level"]}) — `{p.relative_to(HERE).as_posix()}`')
        L('')
        i = 0
        for dec in ORDER:
            xs = [x for x in d['decisions'] if x['decision'] == dec]
            if not xs:
                continue
            L(f'### {TITLE[dec]} ({len(xs)})')
            L('')
            L(hdr)
            L(sep)
            for x in xs:
                i += 1
                orig = x['recommended_by_backlog']
                tgt = ', '.join(x['recommended_targets']) or '—'
                if dec == 'REALLOCATE_RECOMMENDED':
                    tgt = f'{orig} → {tgt}'
                reason = first_sentence(x['reason'])
                if x.get('revalidation'):
                    rv = x['revalidation']
                    reason += (f' **Provisório{" (" + rv["applies_to"] + ")" if rv.get("applies_to") else ""}** — natureza: {x["status_processual"]}; '
                               f'última verificação: {rv["last_verified_on"]}; gatilho: {rv["trigger"]}; prazo: {rv["max_age_days"]} dias.')
                L(f'| {i} | {x["recommendation_id"]} | {orig} | {"; ".join(label(q) for q in x["precedents"])} | '
                  f'{", ".join(sorted({tipo(q) for q in x["precedents"]}))} | {cell(tgt)} | {dec} | AWAITING_USER_RATIFICATION | {cell(reason)} |')
            L('')
    L('## Reconciliação de estados (Parte C)')
    L('')
    L('Recomendações, decisões, relações, precedentes e targets **não** são somados entre si.')
    L('')
    L('| Campo | Estado | Valor |')
    L('|---|---|---|')
    r = recon
    L(f'| PHYSICAL_RELATIONS | {r["PHYSICAL_RELATIONS"]["state"]} | {r["PHYSICAL_RELATIONS"]["relations"]} relações / {r["PHYSICAL_RELATIONS"]["targets"]} targets |')
    h = r['RATIFIED_HOST_ONLY_RELATIONS']
    L(f'| RATIFIED_HOST_ONLY_RELATIONS | {h["state"]} | {h["relations"]} relações (A: {h["variant_A"]}; B, exige firmware HC: '
      f'{h["variant_B_requires_hc_firmware"]}) |')
    a = r['AWAITING_RATIFICATION_RECOMMENDATIONS']
    L(f'| AWAITING_RATIFICATION_RECOMMENDATIONS | {a["state"]} | {a["recommendations"]} recomendações; {a["promoting_decisions"]} decisões que '
      f'vinculam; até {a["proposed_relations_upper_bound"]} relações em {a["proposed_targets"]} targets, com {a["proposed_precedents"]} precedentes distintos |')
    L(f'| UNRESOLVED_RECOMMENDATIONS | não resolvidas | {r["UNRESOLVED_RECOMMENDATIONS"]["count"]} ({", ".join(r["UNRESOLVED_RECOMMENDATIONS"]["ids"]) or "—"}) |')
    L(f'| IN_RESEARCH | em pesquisa | {r["IN_RESEARCH"]["count"]} ({r["IN_RESEARCH"]["note"]}) |')
    nr = r['NOT_RESEARCHED']
    L(f'| NOT_RESEARCHED | não pesquisadas | {nr["backlog_pending"]} pendentes ({", ".join(f"{k} {v}" for k, v in nr["by_level"].items())}) |')
    L('| UNRATIFIED_RELATIONS_PUBLISHED | — | **0** |')
    L('')
    L('**Decisões propostas por tipo (Batches 03–09):**')
    L('')
    L('| Decisão | Quantidade |')
    L('|---|---:|')
    for k in ORDER:
        if k in a['decisions_by_type']:
            L(f'| {k} | {a["decisions_by_type"][k]} |')
    L('')
    L('O limite superior de relações conta todos os pares *target × precedente* das decisões que vinculam. Registros conjuntos, como ADI 3423/3392 '
      'ou ADI 7047/7064, podem reduzir o número final na materialização.')
    md = '\n'.join(lines) + '\n'
    js = json.dumps(dict(schema_version=1, round='J2', kind='RECONCILIATION', **recon,
                         inputs={G.batch_file(n).relative_to(ROOT).as_posix(): None for n in BATCHES}), ensure_ascii=False, indent=1) + '\n'
    return md.encode('utf-8'), js.encode('utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    md, js = render()
    outs = {HERE / 'J2_RATIFICATION_DOSSIER.md': md, HERE / 'J2_RECONCILIATION.json': js}
    if a.check:
        bad = [p.name for p, b in outs.items() if not p.is_file() or p.read_bytes().replace(b'\r\n', b'\n') != b]
        print('UP_TO_DATE' if not bad else f'STALE {bad}')
        sys.exit(1 if bad else 0)
    for p, b in outs.items():
        p.write_bytes(b)
    print(json.loads(js)['AWAITING_RATIFICATION_RECOMMENDATIONS'])


if __name__ == '__main__':
    main()
