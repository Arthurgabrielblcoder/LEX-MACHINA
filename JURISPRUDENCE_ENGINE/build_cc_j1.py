"""CC-J1 — first REAL jurisprudence batch of the Código Civil (CC2002). Host-only; nothing published; every decision AWAITING_USER_RATIFICATION.

Selection (deterministic, 30): 10 from Planalto/STF = the first candidate of each distinct precedent of the portability pilot (ADI 6792/7055
judged together count as one) + the next one; 20 from the official STJ súmulas channel = the two mandatory Súmula 403 links (CC 186, 927)
+ 18 súmulas by round-robin over the STJ's own legal branch, taking per súmula its first pair that is CURRENT, on a dispositivo present in the
CC2002 index, from a vigente súmula (revoked insurance articles, cancelled súmulas and CC/1916-only references are avoided at selection).
Review = the human reading of the official evidence recorded below (REVIEW). Writes CC_J1_DECISIONS.json + CC_J1_REVIEW.md.
Usage: python build_cc_j1.py [--check]
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(HERE / 'pilot_cc'), str(ROOT / 'LEGAL_TARGET_ID'), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import cc_pilot_evidence as EV  # noqa: E402
import juris_types as JT  # noqa: E402
import target_id as T  # noqa: E402

PILOT = HERE / 'pilot_cc/PORTABILITY_PILOT_CC.json'
STJ = HERE / 'stj/STJ_SUMULAS_INDEX.json'
CC_INDEX = ROOT / 'DEVICE_INTEGRATION/staging_article_index_cc/_host/CC2002_TARGET_INDEX.json'
OUT_JSON = HERE / 'CC_J1_DECISIONS.json'
OUT_MD = HERE / 'CC_J1_REVIEW.md'
DECISIONS = ('PROMOTE_RECOMMENDED', 'PROMOTE_PROVISIONAL_RECOMMENDED', 'REALLOCATE_RECOMMENDED', 'REJECT_FALSE_POSITIVE_RECOMMENDED',
             'REJECT_TEMPORAL_MISMATCH_RECOMMENDED', 'REJECT_SUPERSEDED_RECOMMENDED', 'REJECT_NOT_MATERIAL_RECOMMENDED', 'ALREADY_COVERED',
             'DUPLICATE_RECOMMENDATION', 'UNRESOLVED_EXTERNAL', 'UNRESOLVED_IDENTIFICATION')
TEMPORAL = ('CURRENT', 'HISTORICAL_BUT_RELEVANT', 'SUPERSEDED', 'NEEDS_REVIEW', 'WRONG_CODE_VERSION')
LINKING = ('PROMOTE_RECOMMENDED', 'PROMOTE_PROVISIONAL_RECOMMENDED', 'REALLOCATE_RECOMMENDED')
JOINT = {'STF:ADI:6792': 'STF:ADI:6792-7055', 'STF:ADI:7055': 'STF:ADI:6792-7055'}

# (discovered target, precedent) -> (decision, proposed targets, temporal, confidence, human_review, reason)
REVIEW = {
    # ---- Planalto / STF (official evidence: pilot sources; assessment re-read for CC-J1) ----
    ('CC2002:ART.20', 'STF:ADI:4815'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.20'], 'CURRENT', 'HIGH', False,
                                        'Ementa: interpretação conforme aos arts. 20 e 21 do CC (biografias), sem redução de texto.'),
    ('CC2002:ART.21', 'STF:ADI:4815'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.21'], 'CURRENT', 'HIGH', False, 'Mesmo acórdão; art. 21 nomeado na ementa.'),
    ('CC2002:ART.186', 'STF:ADI:6792-7055'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.186', 'CC2002:ART.927'], 'CURRENT', 'HIGH', True,
                                              'ADI 6792 e 7055 julgadas em conjunto (22/05/2024): interpretação conforme aos arts. 186 e 927 '
                                              '(responsabilidade de jornalistas só com dolo ou culpa grave). Um registro conjunto em dois targets; o '
                                              'registro conjunto é decisão humana.'),
    ('CC2002:ART.1790', 'STF:RG:498'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1790'], 'CURRENT', 'HIGH', False,
                                        'Tese: inconstitucional a distinção de regimes sucessórios do art. 1.790 (união homoafetiva).'),
    ('CC2002:ART.1790', 'STF:RG:809'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1790'], 'CURRENT', 'HIGH', False,
                                        'Mesma tese, tema próprio (registro separado do Tema 498).'),
    ('CC2002:ART.1727', 'STF:RG:529'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.1723:PAR.1'], 'CURRENT', 'MEDIUM', True,
                                        'A tese ressalva a exceção do art. 1.723, § 1º; o art. 1.727 aparece só como fundamento.'),
    ('CC2002:ART.1641', 'STF:RG:1236'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.1641:INC.II'], 'CURRENT', 'HIGH', False,
                                         'Tese sobre o inciso II (maiores de 70 anos): norma dispositiva, afastável por convenção.'),
    ('CC2002:ART.927', 'STF:RG:932'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.927:PAR.UNICO'], 'CURRENT', 'HIGH', False,
                                       'Tese nomeia o art. 927, parágrafo único (teoria do risco).'),
    ('CC2002:ART.1521', 'STF:RG:526'): ('REJECT_NOT_MATERIAL_RECOMMENDED', [], 'CURRENT', 'MEDIUM', True,
                                        'Tema previdenciário (pensão a concubina); o art. 1.521 (impedimentos) é só fundamento.'),
    ('CC2002:ART.206', 'STF:RG:1194'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.206-A'], 'CURRENT', 'MEDIUM', True,
                                        'O texto oficial cita o art. 206-A (prescrição intercorrente), afastado na execução de dano ambiental.'),
    # ---- STJ súmulas (official evidence: PDF oficial do STJ, enunciado + referências legislativas do próprio STJ) ----
    ('CC2002:ART.186', 'STJ:SUMULA:403'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.186'], 'CURRENT', 'HIGH', False,
                                           'Dano à imagem com fins comerciais: dano presumido; o art. 186 ("ainda que exclusivamente moral") é '
                                           'referência oficial do STJ. O art. 20 seria alvo adicional possível (não referenciado pelo STJ).'),
    ('CC2002:ART.927', 'STJ:SUMULA:403'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.927'], 'CURRENT', 'HIGH', False,
                                           'Mesma súmula: dever de indenizar independentemente de prova do prejuízo. Mesma ficha do art. 186.'),
    ('CC2002:ART.1420', 'STJ:SUMULA:308'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1420'], 'CURRENT', 'MEDIUM', True,
                                            'Ineficácia da hipoteca da construtora perante adquirentes; art. 1.420 (legitimação para hipotecar) é '
                                            'a referência do STJ; pertinência indireta.'),
    ('CC2002:ART.877', 'STJ:SUMULA:322'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.877'], 'CURRENT', 'HIGH', False,
                                           'Excepciona expressamente a exigência de prova do erro do art. 877 (contas-correntes).'),
    ('CC2002:ART.1647:INC.III', 'STJ:SUMULA:332'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1647:INC.III'], 'CURRENT', 'HIGH', False,
                                                    'Fiança sem outorga do cônjuge: o inciso III exige a autorização.'),
    ('CC2002:ART.2028', 'STJ:SUMULA:371'): ('REJECT_NOT_MATERIAL_RECOMMENDED', [], 'CURRENT', 'HIGH', False,
                                            'A súmula trata do cálculo do VPA; a regra de transição de prazos não é o seu objeto.'),
    ('CC2002:ART.2028', 'STJ:SUMULA:405'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.206:PAR.3:INC.IX'], 'NEEDS_REVIEW', 'MEDIUM', True,
                                            'O prazo trienal do DPVAT é o do art. 206, § 3º, IX (outra referência oficial do STJ); o art. 2.028 é '
                                            'transição. O regime do seguro obrigatório mudou em 2024: revisar a vigência para fatos novos.'),
    ('CC2002:ART.205', 'STJ:SUMULA:412'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.205'], 'CURRENT', 'MEDIUM', True,
                                           'Repetição de tarifas de água e esgoto: "prazo prescricional estabelecido no Código Civil"; a referência '
                                           'oficial é o art. 205 (prazo geral).'),
    ('CC2002:ART.1142', 'STJ:SUMULA:451'): ('REJECT_NOT_MATERIAL_RECOMMENDED', [], 'CURRENT', 'MEDIUM', True,
                                            'Penhorabilidade da sede é questão processual (CPC/LEF); o conceito de estabelecimento é só pano de fundo.'),
    ('CC2002:ART.186', 'STJ:SUMULA:476'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.917'], 'CURRENT', 'HIGH', False,
                                           'O núcleo é o endosso-mandato (art. 917, outra referência oficial); o art. 186 é genérico.'),
    ('CC2002:ART.1231', 'STJ:SUMULA:496'): ('REALLOCATE_RECOMMENDED', ['CC2002:ART.99'], 'CURRENT', 'MEDIUM', True,
                                            'Inoponibilidade do registro à União decorre da natureza de bem público (art. 99, outra referência '
                                            'oficial); a presunção do art. 1.231 é o que a súmula afasta.'),
    ('CC2002:ART.966', 'STJ:SUMULA:499'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.966'], 'CURRENT', 'MEDIUM', True,
                                           'Prestadoras de serviço são empresas: a súmula se apoia no conceito de empresário do art. 966.'),
    ('CC2002:ART.206:PAR.5:INC.I', 'STJ:SUMULA:503'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.206:PAR.5:INC.I'], 'CURRENT', 'HIGH', False,
                                                       'Monitória de cheque sem força executiva: prazo quinquenal do § 5º, I.'),
    ('CC2002:ART.122', 'STJ:SUMULA:543'): ('REJECT_NOT_MATERIAL_RECOMMENDED', [], 'CURRENT', 'MEDIUM', True,
                                           'Restituição na resolução de compra de imóvel é regra consumerista; condição potestativa (art. 122) é '
                                           'fundamento lateral.'),
    ('CC2002:ART.2028', 'STJ:SUMULA:547'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.2028'], 'HISTORICAL_BUT_RELEVANT', 'HIGH', False,
                                            'O enunciado manda observar "a regra de transição disciplinada em seu art. 2.028" (CC/1916 → CC/2002).'),
    ('CC2002:ART.187', 'STJ:SUMULA:550'): ('REJECT_NOT_MATERIAL_RECOMMENDED', [], 'CURRENT', 'MEDIUM', True,
                                           'Credit scoring: núcleo no CDC e na Lei do Cadastro Positivo; abuso de direito (art. 187) é lateral.'),
    ('CC2002:ART.1226', 'STJ:SUMULA:585'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1226'], 'CURRENT', 'MEDIUM', True,
                                            'Alienação do veículo (móvel) pela tradição afasta o IPVA posterior do ex-proprietário; o art. 1.267 é '
                                            'alternativa (também referência oficial).'),
    ('CC2002:ART.186', 'STJ:SUMULA:595'): ('REJECT_NOT_MATERIAL_RECOMMENDED', [], 'CURRENT', 'MEDIUM', True,
                                           'Responsabilidade objetiva da instituição de ensino (CDC); o ilícito culposo do art. 186 não é o fundamento.'),
    ('CC2002:ART.1696', 'STJ:SUMULA:596'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.1696'], 'CURRENT', 'HIGH', False,
                                            'Alimentos avoengos complementares e subsidiários (art. 1.696; o art. 1.698 é a outra referência oficial).'),
    ('CC2002:ART.422', 'STJ:SUMULA:609'): ('PROMOTE_RECOMMENDED', ['CC2002:ART.422'], 'NEEDS_REVIEW', 'MEDIUM', True,
                                           'Boa-fé objetiva (art. 422) segue vigente, mas os arts. 765 e 766 também referenciados foram revogados '
                                           'pela Lei 15.040/2024 (seguros): revisar se a súmula subsiste sob a lei nova.'),
}


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def select():
    pilot, stj = load(PILOT), load(STJ)
    rows = [r for r in pilot['candidates'] if not r['duplicate_of']]
    seen, stf = set(), []
    for r in rows:                                                    # first candidate of each distinct precedent (joint = one)
        pid = JOINT.get(r['precedent'], r['precedent'])
        if pid not in seen and r['pilot_assessment'] != 'DUPLICATE_RECOMMENDATION':
            seen.add(pid)
            stf.append((r['discovered_target'], pid, r['id']))
    for r in rows:                                                    # then the next ones in pilot order until 10
        pid = JOINT.get(r['precedent'], r['precedent'])
        if len(stf) >= 10:
            break
        if (r['discovered_target'], pid) not in {(a, b) for a, b, _ in stf} and r['pilot_assessment'] != 'DUPLICATE_RECOMMENDATION':
            stf.append((r['discovered_target'], pid, r['id']))
    idx = {x['target_id'] for x in load(CC_INDEX)['targets']}
    E = {e['number']: e for e in stj['entries']}
    pairs = pilot['stj_channel']['pairs']
    num = lambda p: int(p['precedent'].split(':')[-1])  # noqa: E731
    mandatory = [p for p in pairs if num(p) == 403]
    ok = [p for p in pairs if p['temporal'] == 'CURRENT' and p['target'] in idx and num(p) != 403 and p['status'] == 'VIGENTE']
    first = {}
    for p in sorted(ok, key=lambda p: (num(p), p['target'])):
        first.setdefault(num(p), p)
    branches = collections.OrderedDict()
    for n, p in sorted(first.items()):
        branches.setdefault(E[n]['branch'], []).append(p)
    rr, i = [], 0
    while len(rr) < 20 - len(mandatory) and any(i < len(v) for v in branches.values()):
        for v in branches.values():
            if i < len(v) and len(rr) < 20 - len(mandatory):
                rr.append(v[i])
        i += 1
    stj_sel = [(p['target'], p['precedent'], 'STJ') for p in sorted(mandatory, key=lambda p: p['target']) + rr]
    return stf, stj_sel, stj, pilot


def build():
    stf, stj_sel, stj, pilot = select()
    E = {f"STJ:SUMULA:{e['number']}": e for e in stj['entries']}
    by_id = {r['id']: r for r in pilot['candidates']}
    out = []
    for i, (t, pid, origin) in enumerate(stf + stj_sel, 1):
        dec, targets, temporal, conf, human, reason = REVIEW[(t, pid)]
        if dec not in DECISIONS or temporal not in TEMPORAL:
            raise SystemExit(f'BAD_REVIEW {t} {pid}')
        for x in targets:
            T.parse_target_id(x)
        if pid.startswith('STJ:'):
            e = E[pid]
            src = dict(id='STJ_PDF', url=stj['source']['url'], sha256=stj['source']['pdf_sha256'], tier='A')
            meta = dict(tribunal='STJ', klass='SUMULA_STJ', number=str(e['number']), status_oficial=e['status'], decisao=e['data_decisao'],
                        orgao=e['orgao'], fonte=e['fonte'], enunciado=e['enunciado'])
            channel = 'STJ_SUMULAS_PDF'
        else:
            base = 'STF:ADI:6792' if pid == 'STF:ADI:6792-7055' else pid
            f = EV.PRECEDENTS[base]
            src = dict(id='+'.join(f['sources']), url=EV.SOURCES[f['sources'][0]]['url'], sha256=EV.SOURCES[f['sources'][0]]['sha256'], tier='A')
            meta = dict(tribunal='STF', klass=pid.split(':')[1], number=pid.split(':')[2].replace('-', '/'), status_oficial=f['status_text'],
                        evidence=f['evidence'])
            channel = 'PLANALTO_VIDE' if by_id[origin]['source'] == 'PLANALTO_VIDE' else 'STF_SEARCH_Q1'
        out.append(dict(rank=i, channel=channel, pilot_candidate=origin if origin != 'STJ' else None, discovered_target=t, precedent=pid, **meta, decision=dec, proposed_targets=targets,
                        temporal=temporal, confidence=conf, HUMAN_REVIEW_REQUIRED=human or conf != 'HIGH' or temporal == 'NEEDS_REVIEW',
                        reason=reason, source=src, device_label=JT.label(JT.KLASS_TO_TIPO[meta['klass']] if meta['klass'] in JT.KLASS_TO_TIPO else
                                                                          meta['klass'].lower(), meta['tribunal'], meta['number']),
                        device_type=JT.device_status(meta['klass']), status='AWAITING_USER_RATIFICATION', human_approved=False))
    c = collections.Counter(x['decision'] for x in out)
    rels = sorted({(t, x['precedent']) for x in out if x['decision'] in LINKING for t in x['proposed_targets']})
    sim = sorted({(t, x['precedent']) for x in out if x['decision'] in LINKING and x['temporal'] in ('CURRENT', 'HISTORICAL_BUT_RELEVANT')
                  for t in x['proposed_targets']})
    doc = dict(schema_version=1, batch='CC-J1', norm='CC2002', mode='HOST_ONLY_DECISIONS_NO_MATERIALIZATION', status='AWAITING_USER_RATIFICATION',
               selection=dict(rule=__doc__.split('Selection')[1].split('Review =')[0].strip(), planalto_stf=len(stf), stj=len(stj_sel)),
               metrics=dict(CC_J1_CANDIDATES=len(out), CC_J1_PROMOTE=c['PROMOTE_RECOMMENDED'] + c['PROMOTE_PROVISIONAL_RECOMMENDED'],
                            CC_J1_REALLOCATE=c['REALLOCATE_RECOMMENDED'], CC_J1_REJECT=sum(v for k, v in c.items() if k.startswith('REJECT')),
                            CC_J1_UNRESOLVED=sum(v for k, v in c.items() if k.startswith('UNRESOLVED')),
                            CC_J1_TEMPORAL_ALERTS=sum(1 for x in out if x['temporal'] in ('NEEDS_REVIEW', 'SUPERSEDED', 'WRONG_CODE_VERSION')),
                            CC_J1_HISTORICAL_BUT_RELEVANT=sum(1 for x in out if x['temporal'] == 'HISTORICAL_BUT_RELEVANT'),
                            CC_J1_HUMAN_REVIEW_REQUIRED=sum(1 for x in out if x['HUMAN_REVIEW_REQUIRED']),
                            CC_J1_RELATIONS_PROPOSED=len(rels), CC_J1_TARGETS_PROPOSED=len({t for t, _ in rels}),
                            CC_J1_SIMULATION_RELATIONS=len(sim), CC_J1_AWAITING_RATIFICATION=len(out),
                            STJ_RELATIONS_DISCOVERABLE_TOTAL=sum(stj['stats']['PAIRS_BY_NORM'].values()),
                            STJ_CC2002_RELATIONS=stj['stats']['PAIRS_BY_NORM'].get('CC2002', 0)),
               totals=dict(sorted(c.items())), proposed_relations=[dict(target_id=t, precedent=p) for t, p in rels],
               simulation_relations=[dict(target_id=t, precedent=p) for t, p in sim], decisions=out)
    return doc


def render(doc):
    m = doc['metrics']
    L = ['# CC-J1 — primeiro lote real do Código Civil (propostas aguardando ratificação)', '',
         '```', f"LOTE = CC-J1 · NORMA = CC2002 · HOST-ONLY · NADA MATERIALIZADO · STATUS = AWAITING_USER_RATIFICATION (human_approved = false)",
         ' · '.join(f'{k} = {v}' for k, v in m.items()), '```', '', '## Seleção', '', doc['selection']['rule'], '',
         '## Decisões', '', '| # | Canal | Target descoberto | Precedente | Tribunal | Temporalidade | Proposta | Alvo proposto | Humano | Razão |',
         '|---|---|---|---|---|---|---|---|---|---|']
    for x in doc['decisions']:
        L.append(f"| {x['rank']} | {x['channel']} | {x['discovered_target']} | {x['device_label']} | {x['tribunal']} | {x['temporal']} | "
                 f"**{x['decision'].replace('_RECOMMENDED', '')}** | {', '.join(x['proposed_targets']) or '—'} | "
                 f"{'sim' if x['HUMAN_REVIEW_REQUIRED'] else 'não'} | {x['reason']} |")
    L += ['', '## Fontes', '', '- STF: fontes do piloto (`pilot_cc/cc_pilot_evidence.py`, sha256 do innerText).',
          f"- STJ: PDF oficial \"Súmulas do STJ\" (sha256 `{load(STJ)['source']['pdf_sha256'][:16]}…`), enunciado e referências legislativas do próprio STJ.",
          '', 'Nenhuma decisão é HUMAN_APPROVED. A ratificação é do usuário.']
    return '\n'.join(L) + '\n'


def main():
    doc = build()
    b = (json.dumps(doc, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    md = render(doc).encode('utf-8')
    if '--check' in sys.argv:
        ok = all(p.is_file() and p.read_bytes().replace(b'\r\n', b'\n') == v for p, v in ((OUT_JSON, b), (OUT_MD, md)))
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    OUT_JSON.write_bytes(b)
    OUT_MD.write_bytes(md)
    print(json.dumps(doc['metrics'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
