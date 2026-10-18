"""CC-J1 — MATERIALIZATION PREFLIGHT: the ratified CC-J1 decisions -> an immutable host-only deploy candidate (never written to a card).

Authority: CC_J1_RATIFICATION_RECORD.json (its pinned hashes are re-verified). Relations are recomputed from the record's final targets and
must reconcile exactly with its approved_relations. Package = generic packager over CF88 + ADCT (J2I fixture, semantics 315/198) + CC2002.
The candidate ADDS files only (normalized layer + new fichas); no existing card file is modified, so a future rollback of the CC is "delete
the added files" and the J2I baseline (legacy indexes, LEXV1, CF88_TARGETS.IDX, device manifest) stays byte-identical.
Writes CC_J1_MATERIALIZATION_CANDIDATE/ (candidate/SD/... + host/*.json).   Usage: python build_cc_j1_materialization.py [--check]
"""
import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / 'pilot_cc'), str(HERE / 'firmware_multinorm'), str(ROOT / 'JURISPRUDENCE_AUDIT'), str(ROOT / 'LEGAL_TARGET_ID')]
import generic_packager as P  # noqa: E402
import cc_pilot_evidence as EV  # noqa: E402
import multinorm_sim as S  # noqa: E402
import juris_types as JT  # noqa: E402
import target_id as T  # noqa: E402

REC = HERE / 'CC_J1_RATIFICATION_RECORD.json'
DEC = HERE / 'CC_J1_DECISIONS.json'
DOSSIER = HERE / 'CC_J1_RATIFICATION_DOSSIER.json'
STJ = HERE / 'stj/STJ_SUMULAS_INDEX.json'
ANNOT = HERE / 'pilot_cc/PLANALTO_CC2002_ANNOTATIONS.json'
CC_INDEX = ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json'
MULTINORM_BUILD = HERE / 'firmware_multinorm/MULTINORM_PROTOTYPE_BUILD.json'
OUT = HERE / 'CC_J1_MATERIALIZATION_CANDIDATE'
CC_FILE = '/2- CÓDIGO CIVIL/codigo_civil_ lei10.406 2002.txt'
CF_FILE = '/1- CONSTITUIÇÃO FEDERAL/cf.txt'
TEMA = 'https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num={}'
FLAG_POS = dict(E=0, C=1, J=2, W=3, R=4, X=5)                # same 6-flag schema as CF88_TARGETS.IDX
LOOKUP_ENTRY_BYTES = 68                                       # sizeof(LookupJurisCFCache) in the multinorm prototype (norma[16])
CACHE_ENTRIES_MAX = 4096                                      # MAX_JUR_LOOKUPS_SEGURANCA
EXPECTED = dict(approved=22, pending=['CCJ1-09', 'CCJ1-30'], not_approved=['CCJ1-08', 'CCJ1-16', 'CCJ1-19', 'CCJ1-24', 'CCJ1-26', 'CCJ1-28'])
# legal-context notes for the fichas — taken only from ratified evidence/notes (no new content)
FICHA_NOTES = {
    'STF:ADI:6792-7055': 'Interpretação conforme aos arts. 186 e 927 no contexto da responsabilidade civil da imprensa: o jornalista ou o veículo só '
                         'responde em caso de dolo ou culpa grave.',
    'STF:RG:498': 'O art. 1.790 foi declarado inconstitucional; aplica-se o regime do art. 1.829 tanto no casamento quanto na união estável.',
    'STF:RG:809': 'O art. 1.790 foi declarado inconstitucional; aplica-se o regime do art. 1.829 tanto no casamento quanto na união estável.',
    'STF:RG:1236': 'Trânsito em julgado em 10/04/2024.',
    'STJ:SUMULA:405': 'Entendimento específico sobre a prescrição da cobrança do seguro DPVAT. O regime do seguro obrigatório mudou depois; a '
                      'orientação deve ser revalidada se a súmula for cancelada ou se o STJ alterar a orientação.',
    'STJ:SUMULA:496': 'Contexto: terrenos de marinha e propriedade da União.',
    'STJ:SUMULA:499': 'Assunto principal tributário (contribuições ao Sesc e ao Senac); o art. 966 entra como conceito de empresário usado pelo STJ.',
    'STJ:SUMULA:547': 'Contexto temporal: transição do Código Civil de 1916 para o de 2002 (art. 2.028).',
    'STJ:SUMULA:585': 'Contexto: alienação de veículo, IPVA e transferência da propriedade móvel pela tradição.',
}
TEMPORAL_CONTEXT = {'STJ:SUMULA:547': 'CC1916_TO_CC2002', 'STJ:SUMULA:405': 'DPVAT_LEGISLATIVE_CONTEXT'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_lf(p):
    return sha(Path(p).read_bytes().replace(b'\r\n', b'\n'))


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def fail(code):
    raise SystemExit(f'PREFLIGHT_STOP {code}')


def authority():
    rec = load(REC)
    pins = rec['pinned']
    if (pins['cc_j1_decisions_sha256_lf'], pins['dossier_sha256_lf'], pins['stj_index_sha256_lf']) != (sha_lf(DEC), sha_lf(DOSSIER), sha_lf(STJ)):
        fail('RATIFICATION_PINS_CHANGED')
    items = rec['items']
    appr = [i for i in items if i['human_approved']]
    pend = sorted(i['id'] for i in items if i['human_state'].startswith('PENDING'))
    nota = sorted(i['id'] for i in items if i['human_state'] == 'HUMAN_REJECTED_OR_NOT_APPROVED')
    if (len(items), len(appr), pend, nota) != (30, EXPECTED['approved'], EXPECTED['pending'], EXPECTED['not_approved']):
        fail('RATIFICATION_COUNTS')
    rels = sorted({(t, i['precedent']) for i in appr for t in i['final_targets']})
    if rels != sorted((r['target_id'], r['precedent']) for r in rec['approved_relations']):
        fail('RELATIONS_DO_NOT_RECONCILE')
    c = rec['counts']
    if (len(rels), len({t for t, _ in rels}), len({p for _, p in rels})) != (c['NORMALIZED_RELATIONS_APPROVED'], c['DISTINCT_CC_TARGETS_APPROVED'],
                                                                        c['DISTINCT_PRECEDENTS_APPROVED']):
        fail('COUNTS_DO_NOT_RECONCILE')
    excluded = {i['precedent'] for i in items if not i['human_approved']} - {p for _, p in rels}
    return rec, appr, rels, pend, nota, excluded


def target_checks(rels):
    idx = {t['target_id']: t for t in load(CC_INDEX)['targets']}
    amend = load(ANNOT)['amendments']
    out = []
    for t in sorted({t for t, _ in rels}):
        p = T.parse_target_id(t)
        rev = [a for a in amend.get(t, []) if a['kind'].lower().startswith('revogad')]
        out.append(dict(target=t, namespace=p['namespace'], article=p['article'], paragraph=p['paragraph'], inciso=p['inciso'], alinea=p['alinea'],
                        kind=p['kind'], exists=t in idx, structure_ok=t in idx and idx[t]['kind'] == p['kind'],
                        amendment_info_available=t in amend, vigente=t in amend and not rev))
    return out


def target_order(t):
    p = T.parse_target_id(t)
    return (int(p['article'].split('-')[0]), p['article'], p['paragraph'] or '', p['inciso'] or '')


def human_target(t):
    """'CC2002:ART.206:PAR.3:INC.IV' -> 'art. 206, § 3º, IV'; numbers >= 1000 with the official thousands dot (art. 2.028)."""
    p = T.parse_target_id(t)
    a = p['article']
    n = a.split('-')[0]
    r = 'art. ' + (f'{n[:-3]}.{n[-3:]}' if len(n) > 3 else n) + a[len(n):]
    if p['paragraph']:
        r += ', parágrafo único' if p['paragraph'] == 'UNICO' else f", § {p['paragraph']}º"
    if p['inciso']:
        r += ', ' + p['inciso']
    if p['alinea']:
        r += ', ' + p['alinea'] + ')'
    return r


def records_and_fichas(rels, appr, card):
    stj = {f"STJ:SUMULA:{e['number']}": e for e in load(STJ)['entries']}
    cf_rels, cf_prec = P.cf_fixture()
    targets_of = collections.defaultdict(list)
    for t, p in rels:
        targets_of[p].append(t)
    prec, fichas = {}, {}
    for pid in sorted(targets_of):
        trib, klass, num = pid.split(':')
        tlist = '; '.join(human_target(t) for t in sorted(targets_of[pid], key=target_order))
        note = FICHA_NOTES.get(pid)
        if pid in cf_prec:                                          # already on the card (Tema 932, CF): reuse record and physical ficha
            prec[pid] = cf_prec[pid]
            continue
        if trib == 'STJ':
            e = stj[pid]
            prec[pid] = dict(tipo='sumula', tribunal='STJ', numero=num, status='vigente', titulo=f'Súmula {num} STJ', fonte=load(STJ)['source']['url'])
            body = [f'SÚMULA {num} DO STJ', 'TRIBUNAL: STJ', f'STATUS: {"vigente" if e["status"] == "VIGENTE" else e["status"].lower()}',
                    f'ÓRGÃO JULGADOR: {e["orgao"]}', '', 'ENUNCIADO', e['enunciado'], '', 'JULGAMENTO', f'{e["data_decisao"]}; {e["fonte"]}.', '',
                    'CÓDIGO CIVIL', tlist, '']
        else:
            base = 'STF:ADI:6792' if pid == 'STF:ADI:6792-7055' else pid
            f = EV.PRECEDENTS[base]
            src = EV.SOURCES[f['sources'][0]]
            numero = num.replace('-', '/')
            if klass == 'RG':
                head, titulo, tipo, status, fonte = f'TEMA {numero} DE REPERCUSSÃO GERAL', f'Tema de Repercussão Geral {numero}', 'repercussao_geral', \
                    'tese_fixada', TEMA.format(num)
            elif '-' in num:
                head, titulo, tipo, status, fonte = 'AÇÕES DIRETAS DE INCONSTITUCIONALIDADE 6792 E 7055', f'ADI {numero} (julgamento conjunto)', 'adi', \
                    'merito_julgado', src['url']
            else:
                head, titulo, tipo, status, fonte = f'AÇÃO DIRETA DE INCONSTITUCIONALIDADE {numero}', f'ADI {numero}', 'adi', 'merito_julgado', src['url']
            prec[pid] = dict(tipo=tipo, tribunal='STF', numero=numero, status=status, titulo=titulo, fonte=fonte)
            stat = f"tese fixada; {f['status_text'].replace(' - em ', ' em ').replace(' - ', ' em ').lower()}" if klass == 'RG' else 'mérito julgado'
            body = [head, 'TRIBUNAL: STF', f'STATUS: {stat}', f'PROCESSO: {JT.label(tipo, "STF", numero)}', '']
            if '-' in num:
                body += ['JULGAMENTO CONJUNTO', 'ADI 6792 e ADI 7055, julgadas em conjunto pelo Plenário (22/05/2024).', '']
            body += ['RESUMO DA FONTE OFICIAL', src['proves'], '', 'TRECHO OFICIAL', f['evidence'], '', 'CÓDIGO CIVIL', tlist, '']
        if note:
            body += ['NOTA', note, '']
        body += ['FONTE OFICIAL', prec[pid]['fonte']]
        fichas[JT.ficha(pid)] = '\n'.join(body) + '\n'
    return cf_rels, cf_prec, prec, fichas


def flags_projection(cc_targets):
    """Host-side projection of the 6-flag schema for CC2002 (no CC flag index exists on the card; the multinorm firmware decides by lookup)."""
    idx = sorted(t['target_id'] for t in load(CC_INDEX)['targets'] if t['kind'] != 'NORMA')
    before = {t: '------' for t in idx}
    after = dict(before)
    for t in cc_targets:
        f = list(after[t])
        f[FLAG_POS['J']] = 'J'
        after[t] = ''.join(f)
    changes = collections.Counter(k for t in idx for k, i in FLAG_POS.items() if before[t][i] != after[t][i])
    return before, after, dict(changes)


def build():
    rec, appr, rels, pend, nota, excluded = authority()
    card = P.card_fichas()
    tchk = target_checks(rels)
    if not all(x['exists'] and x['structure_ok'] and x['vigente'] for x in tchk):
        fail(f'TARGET_CHECK {[x["target"] for x in tchk if not (x["exists"] and x["structure_ok"] and x["vigente"])]}')
    cf_rels, cf_prec, cc_prec, new_fichas = records_and_fichas(rels, appr, card)
    cc_rels = [dict(norm='CC2002', target_id=t, precedent_id=p, origin='CC-J1 HUMAN_APPROVED') for t, p in rels]
    files = P.package(cf_rels + cc_rels, {**cf_prec, **cc_prec}, card, new_fichas=new_fichas, provisional_ids=P.provisional_ids(),
                      known_targets=P.known_targets())
    lm = json.loads(files[P.LAYER + '/MULTINORM_MANIFEST.json'])
    look = files[P.LAYER + '/JUR_LOOKUP.IDX']
    recs = files[P.LAYER + '/JURISPRUDENCIA.IDX']
    build_id = sha(look + recs)[:16]
    ver = '\n'.join([
        '#LEXMACHINA|JURIS_NORMALIZED_LAYER|1', f'BUILD_ID|{build_id}', f'LAYER|{P.LAYER}', 'CF_BASELINE|J2I_FROZEN_315_198',
        f'CC_J1_RATIFICATION_SHA256|{sha_lf(REC)}',
        *[f'NORM|{n}|{v["relations"]}|{v["targets_with_j"]}' for n, v in sorted(lm['norms'].items())]]) + '\n'
    files[P.LAYER + '/LAYER.VER'] = ver.encode('utf-8')
    cand = {f'candidate/SD/{k}': v for k, v in files.items()}
    # ---- checks over the produced bytes ----
    pkg = S.Package(look, recs, card | {k.split('/')[-1] for k in files if k.startswith(P.CONTENT)})
    by_key = collections.defaultdict(set)
    for t, p in rels:
        by_key[P.query_key(t)].add(JT.ficha(p))
    e2e, visible, labels = [], 0, collections.Counter()
    for t in sorted({t for t, _ in rels}):
        norma, art, par, inc, ali = P.query_key(t).split('|')
        st = S.carregar(pkg, CC_FILE, art, par, inc, ali)
        got = {x['arquivo'] for x in st['relations']}
        ok = st['branch'] == 'MULTINORMA' and got == by_key[P.query_key(t)]
        for i in range(len(st['relations'])):
            o = S.open_and_back(pkg, st, i)
            ok = ok and o['opened'] and 'OUTRO' not in o['title'] and S.carregar(pkg, CC_FILE, art, par, inc, ali)['relations'] == st['relations']
        ok = ok and S.carregar(pkg, CC_FILE, art, par, inc, ali) == st
        visible += sum(1 for p in {p for tt, p in rels if tt == t} if JT.ficha(p) in got)
        labels.update(x['label'].split(' ')[0] + '/' + x['tribunal'] for x in st['relations'])
        e2e.append(dict(target=t, pass_=ok, list=[x['label'] for x in st['relations']]))
    cf_only = P.package(cf_rels, cf_prec, card)
    cf_pkg = S.Package(cf_only[P.LAYER + '/JUR_LOOKUP.IDX'], cf_only[P.LAYER + '/JURISPRUDENCIA.IDX'], card)
    cf_keys = [l.split('|')[:5] for l in cf_only[P.LAYER + '/JUR_LOOKUP.IDX'].decode('utf-8').split('\n')[1:] if l and l.startswith('CF88|')]
    cf_reg = all(S.carregar(pkg, CF_FILE, *k[1:])['relations'] == S.carregar(cf_pkg, CF_FILE, *k[1:])['relations'] for k in cf_keys)
    keys = [tuple(l.split('|')[:5]) for l in look.decode('utf-8').split('\n')[1:] if l]
    rec_lines = [l for l in recs.decode('utf-8').split('\n')[1:] if l]
    cc_lines = [l for l in rec_lines if ':CC2002:' in l]
    lost = len(rels) - sum(1 for l in cc_lines)
    leaked = sorted(p for p in excluded if any(l.split('|')[6] == p for l in cc_lines))
    before, after, fchanges = flags_projection({t for t, _ in rels})
    multinorm = load(MULTINORM_BUILD)
    psram = len(keys) * LOOKUP_ENTRY_BYTES + len(recs) + 1
    new_f = sorted(k.split('/')[-1] for k in files if k.startswith(P.CONTENT))
    reused = sorted(JT.ficha(p) for p in {p for _, p in rels} if JT.ficha(p) in card)
    n = lm['norms']
    checks = dict(
        CCJ1_RATIFICATION_RECORD_VALID='PASS', APPROVED_PROPOSALS=len(appr), PENDING_PROPOSALS=len(pend), NOT_APPROVED_PROPOSALS=len(nota),
        APPROVED_RELATIONS=len(rels), APPROVED_TARGETS=len({t for t, _ in rels}), APPROVED_PRECEDENTS=len({p for _, p in rels}),
        PENDING_MATERIALIZED=sum(1 for p in leaked if p in ('STF:RG:1194', 'STJ:SUMULA:609')), REJECTED_MATERIALIZED=len(leaked),
        INVALID_TARGETS=sum(1 for x in tchk if not x['structure_ok']), MISSING_TARGETS=sum(1 for x in tchk if not x['exists']),
        TOTAL_FICHAS=len({JT.ficha(p) for _, p in rels}), NEW_FICHAS=len(new_f), SHARED_FICHAS=len(reused),
        SHARED_FICHA_TEMA932='REUSED' if 'STF_RG_932.TXT' in reused and 'STF_RG_932.TXT' not in new_f else 'NOT_REUSED',
        DUPLICATED_SHARED_FICHAS=len(set(new_f) & card), FICHA_ID_COLLISIONS=len(new_f) - len({f.upper() for f in new_f}),
        DUPLICATE_QUERY_KEYS=len(keys) - len(set(keys)), LOOKUP_LOST_RELATIONS=lost,
        CF88_RELATIONS=n['CF88']['relations'], CF88_TARGETS=n['CF88']['targets_with_j'], ADCT_RELATIONS=n['ADCT']['relations'],
        ADCT_TARGETS=n['ADCT']['targets_with_j'], CF_BASELINE=f"{n['CF88']['relations'] + n['ADCT']['relations']}/{n['CF88']['targets_with_j'] + n['ADCT']['targets_with_j']}",
        CC2002_RELATIONS=n['CC2002']['relations'], CC2002_TARGETS=n['CC2002']['targets_with_j'], CC2002_PRECEDENTS=n['CC2002']['distinct_precedents'],
        CC2002_FICHAS=n['CC2002']['fichas'], CC2002_NEW_FICHAS=len(new_f),
        CC_TARGETS_E2E=f"{sum(1 for x in e2e if x['pass_'])}/{len(e2e)}", CC_RELATIONS_VISIBLE=f'{visible}/{len(rels)}', CF_REGRESSION='PASS' if cf_reg else 'FAIL',
        UNKNOWN_TYPE_LABELS=sum(v for k, v in labels.items() if k.startswith('OUTRO')), LABELS_SEEN=dict(sorted(labels.items())),
        NON_J_FLAG_CHANGES=sum(v for k, v in fchanges.items() if k != 'J'), J_FLAG_CHANGES=fchanges.get('J', 0),
        CACHE_ENTRIES_USED=len(keys), CACHE_ENTRIES_MAX=CACHE_ENTRIES_MAX, PSRAM_ESTIMATED=psram,
        EXISTING_CARD_FILES_MODIFIED=0, SD_CHANGED='NO', FIRMWARE_FLASHED='NO')
    diff = dict(CF_ADCT=dict(semantic_change='NONE', relations=checks['CF_BASELINE'], legacy_files_touched=[]),
                CC2002=dict(relations_added=checks['CC2002_RELATIONS'], targets_with_j_added=checks['CC2002_TARGETS'], new_fichas=len(new_f),
                            reused_fichas=reused), files_added=sorted(k for k in cand), files_modified=[], files_removed=[])
    diff['UNEXPECTED_DIFFS'] = int(bool(diff['files_modified'] or diff['files_removed']
                                        or checks['CF_BASELINE'] != '315/198' or checks['CC2002_RELATIONS'] != len(rels)))
    rollback = dict(scope='remover SOMENTE a camada CC; o baseline CF J2I continua intacto', executed=False,
                    remove_files=sorted(k.replace('candidate/SD/', '') for k in cand),
                    restore_files=[], restore_flags='nenhuma no cartão (flags J do CC são projeção host; CF88_TARGETS.IDX não é alterado)',
                    previous_manifest='J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json (1190 arquivos) — conferir o cartão contra ele após a remoção',
                    firmware='independente dos dados: sem a camada 06_NORMALIZADO o firmware multinorma usa os índices legados; para voltar ao '
                             'firmware J2I, gravar o app 1371e69a… (rollback documentado no freeze J2I)')
    cand['host/PREFLIGHT_RESULT.json'] = (json.dumps(dict(checks=checks, targets=tchk, e2e=e2e, excluded_precedents=sorted(excluded),
                                                          pending=pend, not_approved=nota,
                                                          firmware_multinorm=dict(program_delta=multinorm['delta']['program_bytes'],
                                                                                  ram_delta=multinorm['delta']['static_ram_bytes'],
                                                                                  app0_free=multinorm['builds']['multinorm']['app_partition_free'])),
                                                     ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    cand['host/DIFF_REPORT.json'] = (json.dumps(diff, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    cand['host/ROLLBACK_PLAN.json'] = (json.dumps(rollback, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    cand['host/CC2002_J_FLAGS.json'] = (json.dumps(dict(schema='E,C,J,W,R,X (projeção host; não há índice de flags do CC no cartão)',
                                                        changed={t: [before[t], after[t]] for t in sorted(after) if before[t] != after[t]},
                                                        flag_changes=fchanges), ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    sha_manifest = dict(schema_version=1, kind='CC_J1_MATERIALIZATION_CANDIDATE', build_id=build_id, status='HOST_ONLY_DEPLOY_CANDIDATE',
                        deployed=False, authority=dict(ratification_record=REC.name, sha256_lf=sha_lf(REC)),
                        files={k: dict(bytes=len(v), sha256=sha(v)) for k, v in sorted(cand.items())},
                        card_files_reused={'99_JURISPRUDENCIA_V2/03_CONTEUDO/STF_RG_932.TXT': '7bd339337d38caefb5505c8933b395df9a6d129195e9b02060e40f196a10e4d5'})
    cand['SHA256_MANIFEST.json'] = (json.dumps(sha_manifest, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    return cand


def main():
    cand = build()
    if '--check' in sys.argv:
        ok = all((OUT / k).is_file() and (OUT / k).read_bytes() == v for k, v in cand.items())
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    for k, v in cand.items():
        (OUT / k).parent.mkdir(parents=True, exist_ok=True)
        (OUT / k).write_bytes(v)
    r = json.loads(cand['host/PREFLIGHT_RESULT.json'])['checks']
    print(json.dumps(r, ensure_ascii=False, indent=1))
    print('MANIFEST_SHA256', sha(cand['SHA256_MANIFEST.json']))


if __name__ == '__main__':
    main()
