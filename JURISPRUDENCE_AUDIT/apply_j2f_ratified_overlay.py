"""J2F — normalization + overlay of the decisions RATIFIED by the user for Batches 03, 04, 06, 07, 08, 09 (J2_RATIFICATION_RECORD_03_09.json),
on top of the ratified Batch02 overlay (J2E). Deterministic, host-only, no network. Writes LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2F.json.

Normalization (Parte E), every count derived from the ratified files:
  * only HUMAN_APPROVED decisions of type PROMOTE / PROMOTE_PROVISIONAL / REALLOCATE create relations; rejections, duplicates and
    ALREADY_COVERED never do; J0-BL-001 (UNRESOLVED_EXTERNAL) creates nothing;
  * one relation = (target, precedent record). A precedent's own `target` (divisão por alvo) overrides the decision targets;
  * same (target, record) from several decisions -> ONE relation (ratified_decisions lists all of them);
  * ratified joint record: ADI 3392 and ADI 3432 use the single record of the ADI 3423 group (decisions BL-102/103/116/117 say so);
  * a pair already on the J2C card or in J2E is never added twice.
Compatibility split (Parte F) per relation: group A = types the CURRENT firmware shows correctly (repercussao_geral, sumula_vinculante,
adi); group B = everything else (needs the generic tribunal/classe firmware). J2E records keep their variant (A; HC 232627 = B).
Provisional (Parte B): ADI 5017, ADPF 378, Rcl 84738 keep provisional status (number suffix, ficha block); the gate must PASS.
Physical baseline (Parte K): J2C card, PHYSICAL_BASELINE = 261/160 (J2_BASELINE_RECONCILIATION.json); 301 is never a relation baseline.
Usage: python apply_j2f_ratified_overlay.py [--check]
"""
import collections
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import apply_j2e_batch02_overlay as J2E  # noqa: E402  (texto_detalhe + archived J4 corpus)
import build_j2_batch as G  # noqa: E402
import check_j2b_provisional as GATE  # noqa: E402
import juris_types as JT  # noqa: E402

RAT = HERE / 'J2_RATIFICATION_RECORD_03_09.json'
RECON = HERE / 'J2_BASELINE_RECONCILIATION.json'
PROV = HERE / 'J2_PROVISIONAL_REGISTRY.json'
J2E_ADD = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2E.json'
CARD = HERE / 'J2B_1_CANDIDATE_HOST_ONLY/candidate/SD'
PHYSICAL = HERE / 'J2C_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
OUT = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADDITIONS_J2F.json'
GATE_AS_OF = '2026-10-17'
PAYLOAD = '99_LEX_V1/20_REFERENCES/REF_PAYLOAD.IDX'
IDX = '99_JURISPRUDENCIA_V2/05_INDICES_ESP32/JURISPRUDENCIA.IDX'
CONTENT = '99_JURISPRUDENCIA_V2/03_CONTEUDO'
LINKING = ('PROMOTE_RECOMMENDED', 'PROMOTE_PROVISIONAL_RECOMMENDED', 'REALLOCATE_RECOMMENDED')
CURRENT_FW_TYPES = ('repercussao_geral', 'sumula_vinculante', 'adi')
# Ratified joint record (Batch06 BL-102/103/116/117: "registro conjunto do grupo da ADI 3423"); group per S1/S2 (official pages)
JOINT = {'STF:ADI:3392': 'STF:ADI:3423-3392-3432-3520', 'STF:ADI:3432': 'STF:ADI:3423-3392-3432-3520'}
JOINT_RECORDS = {'STF:ADI:3423-3392-3432-3520': dict(numero='3423/3392/3432/3520', source='S1', extra_source='S2',
                                                      note='Julgamento conjunto: ADI 3423 (principal), 3392, 3432 e 3520, no mesmo sentido.')}
# Ratified target split written in the decision text but not in the precedent's structured `target` (fail-closed coverage check below)
TARGET_OVERRIDES = {('J0-BL-067', 'STF:ADPF:378'): ['CF88:ART.86:PAR.1:INC.II', 'CF88:ART.52:INC.I']}   # reason: "no § 1º, II do art. 86 e no art. 52, I"
PROV_STATUS = {'MERIT_PENDING': 'cautelar_referendada_merito_pendente', 'REFERENDUM_PENDING': 'cautelar_monocratica_merito_pendente',
               'CAUTIONARY_ONLY': 'cautelar_plenario_merito_pendente', 'LEADING_CASE_PENDING': 'provisoria_tema_rg_pendente'}
# corpus (archived official theses endpoint, J4) × batch excerpt: every non-identical case reviewed; the ficha uses the full corpus thesis
TEXT_REVIEW = {'STF:RG:835': 'idênticos salvo pontuação/espaço final', 'STF:RG:1046': 'trecho do lote resumido; corpus traz a tese integral',
               'STF:RG:184': 'trecho do lote é a descrição do tema (a página não exibe a tese); corpus traz a tese',
               'STF:RG:201': 'trecho do lote é a ementa da ADI 2777 (mesma orientação); corpus traz a tese do tema',
               'STF:RG:1093': 'trecho do lote é a descrição do tema; corpus traz a tese'}
SUFFIX = {'MERIT_PENDING': ' (CAUTELAR)', 'REFERENDUM_PENDING': ' (CAUTELAR)', 'CAUTIONARY_ONLY': ' (CAUTELAR)', 'LEADING_CASE_PENDING': ' (PROVISÓRIA)'}
WHEN = {'MERIT_PENDING': 'o mérito for julgado', 'REFERENDUM_PENDING': 'o Plenário referendar a cautelar ou julgar o mérito',
        'CAUTIONARY_ONLY': 'o mérito for julgado ou a ação for extinta', 'LEADING_CASE_PENDING': 'o tema de repercussão geral for julgado'}
NAME = {'ADI': 'AÇÃO DIRETA DE INCONSTITUCIONALIDADE', 'ADPF': 'ARGUIÇÃO DE DESCUMPRIMENTO DE PRECEITO FUNDAMENTAL', 'MS': 'MANDADO DE SEGURANÇA',
        'AP': 'AÇÃO PENAL', 'AI': 'AGRAVO DE INSTRUMENTO', 'INQ': 'INQUÉRITO', 'RCL': 'RECLAMAÇÃO', 'HC': 'HABEAS CORPUS', 'MI': 'MANDADO DE INJUNÇÃO',
        'PET': 'PETIÇÃO'}
STATUS = {'repercussao_geral': 'tese_fixada', 'sumula_vinculante': 'vigente', 'sumula': 'vigente'}
# Pre-materialization revalidation required by a ratified decision text (BL-013: "Revalidar antes de materializar"), official page, 2026-10-17
REVALIDATED = {'STF:RG:935': dict(url='https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=935', accessed_on='2026-10-17',
                                  method='navegador embutido (innerText)',
                                  dom_text_sha256='53861094bc1714a219ed02b0397387ea1bcb1c1a2bb586a2558bde614defdf2c',
                                  result='Situação: "Acórdão de mérito publicado - Publicado em: 09/12/2025"; sem registro de trânsito em julgado. '
                                         'Decisão de mérito (não provisória): materializável com nota.',
                                  ficha_note='Situação verificada em 17/10/2026 na página oficial do tema: acórdão de mérito publicado em 09/12/2025; '
                                             'a página não registra trânsito em julgado.')}


def sha_lf(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def expand(spec):
    """'CF88:ART.114:INC.I|IV|IX' -> ['CF88:ART.114:INC.I', 'CF88:ART.114:INC.IV', 'CF88:ART.114:INC.IX']."""
    first, *alts = spec.split('|')
    head = first.rsplit('.', 1)[0]
    return [first] + [f'{head}.{a}' for a in alts]


def legacy(target):
    """Logical target -> legacy key suffix and JUR_LOOKUP tuple (ADCT keeps the CF88 prefix, J2E convention; CAPUT = article)."""
    parts = dict(p.split('.', 1) for p in target.split(':')[1:] if '.' in p)
    t = ('CF88', parts['ART'], parts.get('PAR', ''), parts.get('INC', ''), parts.get('ALI', ''))
    return 'CF88:' + ':'.join(x or '-' for x in t[1:]), t


def rows(b):
    return [l.split('|') for l in b.decode('utf-8').split('\n') if l and not l.startswith('#')]


def norm(s):
    s = re.sub(r'Referência Legislativa:.*$', '', s.strip())
    s = re.sub(r'\(art[^)]*\)\s*\.?\s*$', '', s.strip())
    return ' '.join(re.sub(r'[“”"]', '', s).split()).rstrip('. ').lower()


EDITORIAL_WORDS = ('aparelho', 'ficha', 'alvo', 'tipo novo', 'MEDIUM', 'onfiança', 'proposta', 'Proposta', 'backlog', 'recomendação', 'Batch', 'materializ')


def generic_ficha(rec_id, trib, klass, num, d, p, src, provisional, extra_src=None, joint_note=None):
    head = f'SÚMULA {num} DO {trib}' if klass == 'SUMULA' else f'{NAME[klass]} {num}'
    status = provisional['description'] if provisional else (d['status_processual'] if len(d['precedents']) == 1 else 'julgado')
    lines = [head, f'TRIBUNAL: {trib}', f'STATUS: {status}',
             f'PROCESSO: {JT.label(JT.KLASS_TO_TIPO[p["klass"]], trib, num)}' + (f' ({p["rapporteur"]})' if p.get('rapporteur') else ''), '']
    if provisional:
        lines += ['DECISÃO PROVISÓRIA', f'Esta decisão não é definitiva. Pode mudar quando {WHEN[provisional["state"]]}.', '']
    lines += ['JULGAMENTO', f'{p["judgment"]}; {p["publication"]}.', '']
    if joint_note:
        lines += ['JULGAMENTO CONJUNTO', joint_note, '']
    lines += ['RESUMO DA FONTE OFICIAL', src['proves']] + ([extra_src['proves']] if extra_src else []) + ['']
    if len(d['precedents']) == 1 or joint_note:
        lines += ['TRECHO OFICIAL', d['evidence_excerpt'], '']
    notes = []
    if d['temporal_version'] != 'CURRENT':
        notes.append(d['temporal_note'])
    if d['confidence'] != 'HIGH':
        keep = [x for x in re.split(r'(?<=[.!?]) (?=[A-ZÀ-Ú])', d['reason']) if not any(w in x for w in EDITORIAL_WORDS)]
        if keep:
            notes.append(' '.join(keep))
    if notes:
        lines += ['NOTA'] + notes + ['']
    if provisional:
        lines += ['VERIFICADO EM', f'{dt.date.fromisoformat(provisional["last_verified_on"]).strftime("%d/%m/%Y")}.', '']
    lines += ['FONTE OFICIAL', src['url']]
    return '\n'.join(lines) + '\n'


def build():
    rat = json.loads(RAT.read_text(encoding='utf-8'))
    recon = json.loads(RECON.read_text(encoding='utf-8'))
    if recon['PHYSICAL_BASELINE_RECONCILED'] != 'PASS' or (recon['PHYSICAL_BASELINE_RELATIONS'], recon['PHYSICAL_BASELINE_TARGETS']) != (261, 160):
        raise SystemExit('PHYSICAL_BASELINE_NOT_RECONCILED')
    for rel, h in rat['decision_files_sha256_lf'].items():
        if sha_lf(HERE / rel) != h:
            raise SystemExit(f'RATIFIED_FILE_CHANGED {rel}')
    gate = GATE.check(dt.date.fromisoformat(GATE_AS_OF), PROV)
    if not all(g['result'] == 'PASS' for g in gate):
        raise SystemExit('PROVISIONAL_REVALIDATION_GATE_FAIL')
    prov = {x['source_id']: dict(state=x['state'], description=json.loads(PROV.read_text(encoding='utf-8'))['states'][x['state']],
                                 last_verified_on=x['last_verified_on'], trigger=x['trigger'])
            for x in json.loads(PROV.read_text(encoding='utf-8'))['items']}
    card = {k: v['sha256'] for k, v in json.loads(PHYSICAL.read_text(encoding='utf-8'))['entries'].items()}
    for rel in (PAYLOAD, IDX):
        if hashlib.sha256((CARD / rel).read_bytes()).hexdigest() != card[rel]:
            raise SystemExit(f'NOT_J2C_CARD {rel}')
    base_pay = rows((CARD / PAYLOAD).read_bytes())
    base_pairs = {(r[0], r[5]) for r in base_pay if r[1] == 'JURISPRUDENCE'}
    base_rows = {r[0]: '|'.join(r) for r in rows((CARD / IDX).read_bytes())}
    j2e = json.loads(J2E_ADD.read_text(encoding='utf-8'))
    j2e_pairs = {(r['target_id'], r['source_id']) for r in j2e['records']}
    corpus, csha = J2E.corpus()

    approved = [i for i in rat['items'] if i['human_approved']]
    dec, srcs = {}, {}
    for n in sorted({i['batch'] for i in approved}):
        d = json.loads(G.batch_file(int(n[5:])).read_text(encoding='utf-8'))
        srcs[n] = d['sources']
        dec.update({x['recommendation_id']: (n, x) for x in d['decisions']})
    pairs, skipped, covered = collections.OrderedDict(), [], {}
    for i in approved:
        n, d = dec[i['recommendation_id']]
        if d['decision'] != i['decision']:
            raise SystemExit(f'CLASSIFICATION_CHANGED {i["recommendation_id"]}')
        if d['decision'] not in LINKING:
            continue
        for p in d['precedents']:
            targets = TARGET_OVERRIDES.get((i['recommendation_id'], p['id'])) or (expand(p['target']) if p.get('target') else d['recommended_targets'])
            if not set(targets) <= set(d['recommended_targets']):
                raise SystemExit(f'PRECEDENT_TARGET_OUTSIDE_DECISION {i["recommendation_id"]} {p["id"]}')
            rec = JOINT.get(p['id'], p['id'])
            covered.setdefault(i['recommendation_id'], set()).update(targets)
            for t in targets:
                if (t, rec) in base_pairs or (t, rec) in j2e_pairs:
                    skipped.append(dict(target=t, record=rec, recommendation_id=i['recommendation_id'], reason='ALREADY_PRESENT'))
                    continue
                e = pairs.setdefault((t, rec), dict(target_id=t, record=rec, members=[], decisions=[]))
                e['decisions'].append((i['recommendation_id'], n))
                if p['id'] not in e['members']:
                    e['members'].append(p['id'])

    for rid, ts in covered.items():
        if ts != set(dec[rid][1]['recommended_targets']):
            raise SystemExit(f'RATIFIED_TARGET_NOT_COVERED {rid} {sorted(set(dec[rid][1]["recommended_targets"]) - ts)}')
    records, fichas, text_checks = [], {}, []
    on_card = {Path(k).name for k in card if k.startswith(CONTENT + '/')}
    j2e_fichas = set(j2e['fichas'])
    for (t, rec), e in pairs.items():
        rid, n = sorted(e['decisions'])[0]
        d = dec[rid][1]
        p = next(q for q in d['precedents'] if q['id'] in e['members'])
        trib, klass, num = rec.split(':')[:3]
        tipo = JT.KLASS_TO_TIPO[p['klass']]
        jr = JOINT_RECORDS.get(rec)
        numero = jr['numero'] if jr else num
        pv = prov.get(rec)
        numero_idx = numero + (SUFFIX[pv['state']] if pv else '')
        S = srcs[n]
        src = S[jr['source']] if jr else next(S[s] for s in d['sources'] if p['number'] in (S[s].get('identifier') or ''))
        titulo = {'repercussao_geral': f'Tema de Repercussão Geral {num}', 'sumula_vinculante': f'Súmula Vinculante {num}'}.get(
            tipo, JT.label(tipo, trib, numero))
        suffix, lookup = legacy(t)
        key = f'{rec}:{suffix}'
        status = PROV_STATUS[pv['state']] if pv else STATUS.get(tipo) or ('merito_julgado' if tipo == 'adi' else 'julgado')
        row = '|'.join((key, tipo, trib, numero_idx, status, titulo, rec, src['url']))
        if key in base_rows and base_rows[key] != row:
            raise SystemExit(f'LEGACY_KEY_CONFLICT {key}')
        ficha_name = JT.ficha(rec)
        new_ficha = None
        if ficha_name not in on_card and rec not in j2e_fichas:
            new_ficha = rec
            if rec not in fichas:
                if tipo in ('repercussao_geral', 'sumula_vinculante'):
                    doc = dict(corpus[rec])
                    if rec in REVALIDATED:
                        doc['tese_ou_enunciado'] = doc['tese_ou_enunciado'] + '\n\nNOTA\n' + REVALIDATED[rec]['ficha_note']
                    fichas[rec] = J2E.texto_detalhe(doc)
                    ex, kx = norm(d['evidence_excerpt']), norm(corpus[rec]['tese_ou_enunciado'])
                    st = 'EQUAL' if ex == kx else 'BATCH_EXCERPT_IS_PREFIX' if kx.startswith(ex) else 'CORPUS_IS_PREFIX' if ex.startswith(kx) else 'DIFFERENT'
                    if st == 'DIFFERENT' and rec not in TEXT_REVIEW:
                        raise SystemExit(f'UNREVIEWED_TEXT_DIVERGENCE {rec}')
                    text_checks.append(dict(record=rec, comparison=st, review=TEXT_REVIEW.get(rec), ficha_text='corpus J4 (tese integral)'))
                else:
                    fichas[rec] = generic_ficha(rec, trib, klass, numero, d, p, src, pv, S.get(jr['extra_source']) if jr else None,
                                                jr['note'] if jr else None)
        records.append(dict(group='A' if tipo in CURRENT_FW_TYPES else 'B', origin='J2F', target_id=t, source_id=rec, source_reference_id=key,
                            label=titulo, legacy_idx_row=row, legacy_lookup=list(lookup), legacy_row_already_on_card=key in base_rows,
                            new_ficha=new_ficha, ficha=f'{CONTENT}/{ficha_name}', members=e['members'],
                            ratified_decisions=sorted(r for r, _ in e['decisions']), batches=sorted({b for _, b in e['decisions']}),
                            provisional=dict(pv, source_id=rec) if pv else None, temporal_version=d['temporal_version'],
                            sources=[dict(id=s, url=S[s]['url'], sha256=S[s].get('dom_text_sha256') or S[s].get('snapshot_sha256'))
                                     for s in sorted({s for r, b in e['decisions'] for s in dec[r][1]['sources']}) if s in S],
                            device_labels=dict(CURRENT=f"{dict(adi='ADI', repercussao_geral='RG TEMA', sumula_vinculante='SV').get(tipo, 'OUTRO')} {numero_idx}",
                                               GENERIC=JT.label(tipo, trib, numero_idx)),
                            payload=dict(tribunal=trib, tipo=tipo, numero=numero_idx, titulo=titulo, fonte=src['url'], status_processual=status)))
    for r in j2e['records']:
        records.append(dict(r, group=r['variant'], origin='J2E'))
    new = [r for r in records if r['origin'] == 'J2F']
    cnt = lambda g, rs: [r for r in rs if r['group'] in g]  # noqa: E731
    norm_counts = dict(
        RATIFIED_DECISIONS=rat['RATIFIED_DECISIONS'], LINKING_DECISIONS=sum(1 for i in approved if i['decision'] in LINKING),
        PAIRS_BEFORE_DEDUP=sum(len(e['decisions']) for e in pairs.values()) + len(skipped), PAIRS_ALREADY_PRESENT=len(skipped),
        NEW_DEVICE_RELATIONS_CURRENT_FW=len(cnt('A', new)), NEW_DEVICE_RELATIONS_GENERIC_FW=len(new),
        NEW_DEVICE_RELATIONS_GROUP_B_ONLY=len(cnt('B', new)),
        NEW_PRECEDENT_RECORDS=len({r['source_reference_id'] for r in new if not r['legacy_row_already_on_card']}),
        NEW_PRECEDENTS=len({r['source_id'] for r in new}),
        NEW_FICHAS_CURRENT_FW=len({r['new_ficha'] for r in cnt('A', new) if r['new_ficha']}),
        NEW_FICHAS_GENERIC_FW=len({r['new_ficha'] for r in new if r['new_ficha']}))   # NEW_TARGETS_WITH_J: RUN11_SUMMARY.json (needs the J2C target set)
    doc = dict(schema_version=1, norma_id='CF88', round='J2F', physical_baseline=dict(relations=261, targets=160, source=RECON.name),
               ratification=dict(file=RAT.name, sha256=sha_lf(RAT), by=rat['ratification']['by'], on=rat['ratification']['on']),
               includes_j2e=dict(file=J2E_ADD.relative_to(ROOT).as_posix(), sha256=sha_lf(J2E_ADD), records=len(j2e['records'])),
               provisional_gate=dict(as_of=GATE_AS_OF, registry=PROV.name, result='PASS', items=[g['source_id'] for g in gate]),
               revalidated_before_materialization=REVALIDATED, joint_records=JOINT_RECORDS, archive_corpus=dict(sha256=csha),
               corpus_text_checks=text_checks, groups=dict(A='tipos que o firmware atual mostra corretamente: ' + ', '.join(CURRENT_FW_TYPES),
                                                           B='exige o firmware genérico de tribunal/classe'),
               normalization=norm_counts, skipped=skipped, total=len(records), records=records, fichas={**j2e['fichas'], **fichas})
    return (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


if __name__ == '__main__':
    b = build()
    if '--check' in sys.argv:
        ok = OUT.is_file() and OUT.read_bytes().replace(b'\r\n', b'\n') == b
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT.write_bytes(b)
    d = json.loads(b)
    print(json.dumps(d['normalization'], ensure_ascii=False, indent=1))
    print(json.dumps(d['corpus_text_checks'], ensure_ascii=False))
    for r in d['records']:
        if r['origin'] == 'J2F':
            print(r['group'], r['target_id'], r['source_id'], '|', r['device_labels']['CURRENT'], '|', r['device_labels']['GENERIC'], '|', r['new_ficha'])
