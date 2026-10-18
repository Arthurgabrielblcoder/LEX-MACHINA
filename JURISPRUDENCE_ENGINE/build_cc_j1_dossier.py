"""CC-J1 — ratification dossier (GREEN / YELLOW / RED). Read-only over CC_J1_DECISIONS.json: no decision changes, nothing approved,
nothing materialized. GREEN = SAFE_FOR_BLOCK_RATIFICATION (not ratified); YELLOW = REVIEW_INDIVIDUALLY; RED = DO_NOT_RATIFY_NOW.
Writes CC_J1_RATIFICATION_DOSSIER.md + CC_J1_RATIFICATION_DOSSIER.json.   Usage: python build_cc_j1_dossier.py [--check]
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE / 'pilot_cc'), str(ROOT / 'JURISPRUDENCE_AUDIT')]
import cc_pilot_evidence as EV  # noqa: E402
import juris_types as JT  # noqa: E402

DEC = HERE / 'CC_J1_DECISIONS.json'
ANNOT = HERE / 'pilot_cc/PLANALTO_CC2002_ANNOTATIONS.json'
CARD = ROOT / 'JURISPRUDENCE_AUDIT/J2H_PHYSICAL_DEPLOY/sd_manifest_post_full.json'
OUT_MD = HERE / 'CC_J1_RATIFICATION_DOSSIER.md'
OUT_JSON = HERE / 'CC_J1_RATIFICATION_DOSSIER.json'
LINKING = ('PROMOTE_RECOMMENDED', 'PROMOTE_PROVISIONAL_RECOMMENDED', 'REALLOCATE_RECOMMENDED')

# rank -> (group, risk, motive<=2 sentences, yellow: (problem, favor, risk, option B, recommendation) | red: reopen)
C = {
    1: ('GREEN', 'BAIXO', 'Ementa nomeia o art. 20; interpretação conforme vigente, sem redução de texto.', None),
    2: ('YELLOW', 'MÉDIO', 'Julgamento conjunto ADI 6792/7055 em dois targets (186 e 927); exige decidir o registro conjunto.',
        ('Registro conjunto (como ADI 7047/7064 na CF) e dois targets do mesmo acórdão.',
         'Ementa confere interpretação conforme "aos arts. 186 e 927 do Código Civil" (j. 22/05/2024).',
         'Rotular como duas ADIs separadas duplicaria a ficha; o alcance é só a responsabilidade de jornalistas.',
         'registrar só a ADI 6792 (sem a 7055) nos dois targets', 'A — registro conjunto "ADI 6792/7055" em 186 e 927.')),
    3: ('GREEN', 'BAIXO', 'Tese do Tema 498 declara inconstitucional a distinção do art. 1.790; o vínculo é justamente o aviso disso.', None),
    4: ('GREEN', 'BAIXO', 'Tese do Tema 809 (mesma tese, tema próprio) sobre o art. 1.790; registro separado do Tema 498, não duplicata.', None),
    5: ('YELLOW', 'MÉDIO', 'Realocação de 1.727 para 1.723, § 1º, ditada pela tese.',
        ('O extrator associou o art. 1.727 (concubinato); a tese cita a exceção do art. 1.723, § 1º.',
         'Tese: "ressalvada a exceção do artigo 1723, § 1º, do Código Civil, impede o reconhecimento de novo vínculo".',
         'O art. 1.727 também é pertinente (concubinato); escolher só um pode empobrecer a lista.',
         'promover nos dois (1.723, § 1º e 1.727)', 'A — 1.723, § 1º.')),
    6: ('YELLOW', 'MÉDIO', 'Realocação para o inciso II; a Súmula 655/STJ (2022) sobre o mesmo inciso pode ter sido afetada por este tema.',
        ('Alvo desce do caput para o inciso II; interação com a Súmula 655/STJ.',
         'Tese do Tema 1236 (2024): separação obrigatória do art. 1.641, II é norma dispositiva, afastável por convenção.',
         'Baixo para o vínculo; a Súmula 655 (fora do lote) precisará de análise de superação.',
         'manter no artigo (CC2002:ART.1641)', 'A — 1.641, II.')),
    7: ('YELLOW', 'BAIXO', 'Realocação incontroversa para o parágrafo único; amarelo só pela regra de realocação.',
        ('Realocação 927 → 927, p.u.', 'Tese: "O artigo 927, parágrafo único, do Código Civil é compatível com o artigo 7º, XXVIII, da CF".',
         'Mínimo; ficha STF_RG_932 já existe no cartão (compartilhada com a CF).', 'manter no caput do 927', 'A — 927, p.u.')),
    8: ('RED', '—', 'Tema previdenciário; o art. 1.521 é só fundamento (não material).', 'Reabrir só se surgir precedente que interprete os impedimentos do art. 1.521.'),
    9: ('YELLOW', 'MÉDIO', 'Realocação 206 → 206-A; o tema afasta a prescrição intercorrente só na execução de dano ambiental.',
        ('Alvo corrigido para o art. 206-A (o extrator truncou o número).',
         'Tese: "imprescritível a pretensão executória e inaplicável a prescrição intercorrente na execução de reparação de dano ambiental".',
         'Relação é de exceção (o tema afasta o 206-A num campo específico); art. 206-A tem redação de 2022.',
         'não vincular no CC (tema ambiental)', 'A — 206-A, com o alcance ambiental na ficha.')),
    10: ('GREEN', 'BAIXO', 'Mesmo acórdão da ADI 4815, que nomeia o art. 21; segundo target legítimo (não duplicata).', None),
    11: ('YELLOW', 'MÉDIO', 'Referência oficial do STJ, mas genérica: o direito à imagem (art. 20) não é citado pela súmula.',
         ('Arts. 186/927 são base geral da responsabilidade; o dispositivo específico seria o art. 20.',
          'Súmula 403 (Segunda Seção, 28/10/2009): indenização por uso comercial da imagem independe de prova do prejuízo; STJ referencia CC 186 e 927.',
          'Relação verdadeira porém indireta; texto vigente do 186 inalterado (Vide ADI 6792/7055).', 'acrescentar o art. 20 como alvo',
          'A — 186 (e avaliar o art. 20 em lote futuro).')),
    12: ('YELLOW', 'MÉDIO', 'Mesma súmula e mesma ficha do item 11; dever de indenizar sem prova do prejuízo.',
         ('Mesmo caso do 186: base geral, não o dispositivo específico.', 'Mesmo enunciado; STJ referencia o art. 927.',
          'Indireta; texto vigente do 927 inalterado.', 'acrescentar o art. 20 como alvo', 'A — 927 (mesma ficha STJ_SUMULA_403).')),
    13: ('YELLOW', 'MÉDIO', 'Súmula do SFH sobre ineficácia da hipoteca; o art. 1.420 (legitimação para hipotecar) é pertinência indireta.',
         ('Núcleo da súmula é a proteção do adquirente (CDC/boa-fé), não a legitimação do 1.420.',
          'Súmula 308 (30/03/2005): hipoteca entre construtora e agente financeiro não tem eficácia perante adquirentes; STJ referencia o 1.420.',
          'Associação fraca pode confundir o leitor.', 'rejeitar como não material', 'D — manter pendente até decidir o padrão para referências indiretas.')),
    14: ('GREEN', 'BAIXO', 'Súmula excepciona expressamente a prova do erro exigida pelo art. 877.', None),
    15: ('GREEN', 'BAIXO', 'Fiança sem autorização do cônjuge: aplicação direta do art. 1.647, III.', None),
    16: ('RED', '—', 'Súmula sobre cálculo do VPA; a regra de transição do art. 2.028 não é seu objeto.', 'Reabrir só se o STJ revisar a súmula com foco na transição de prazos.'),
    17: ('YELLOW', 'ALTO', 'Realocação para 206, § 3º, IX, mas o regime do seguro obrigatório mudou em 2024 (NEEDS_REVIEW).',
         ('Seguro obrigatório: impacto de mudanças legislativas de 2024 (inclusive o contexto da Lei 15.040/2024).',
          'Súmula 405 (28/10/2009): DPVAT prescreve em três anos; STJ referencia o 206, § 3º, IX (vigente).',
          'Risco de vincular regra possivelmente restrita a fatos antigos.', 'vincular no 2.028', 'D — manter pendente até análise individual.')),
    18: ('YELLOW', 'MÉDIO', 'O enunciado remete ao "prazo do Código Civil" sem dizer qual; o art. 205 é a referência oficial.',
         ('Extensão da súmula: prazo geral (205) ou outro prazo do CC.',
          'Súmula 412 (25/11/2009): repetição de tarifas de água e esgoto segue o prazo do CC; STJ referencia o art. 205.',
          'Se o prazo aplicado for outro, o vínculo induz erro.', 'vincular também no 206', 'A — 205, após conferir o precedente originário.')),
    19: ('RED', '—', 'Penhorabilidade da sede é questão processual; conceito de estabelecimento é pano de fundo.', 'Reabrir se surgir precedente que interprete o art. 1.142.'),
    20: ('YELLOW', 'BAIXO', 'Realocação 186 → 917 (endosso-mandato), também referência oficial do STJ.',
         ('Alvo descoberto genérico (186); núcleo é o endosso-mandato.', 'Súmula 476 (13/06/2012); STJ referencia CC 186, 662 e 917.',
          'Baixo.', 'vincular também no 662 (mandato sem poderes)', 'A — 917.')),
    21: ('YELLOW', 'MÉDIO', 'Realocação 1.231 → 99 (bens públicos); a súmula afasta a presunção do 1.231.',
         ('Escolher entre o fundamento (99) e o dispositivo afastado (1.231).', 'Súmula 496 (08/08/2012); STJ referencia CC 99 e 1.231.',
          'O art. 99 tem incisos; vincular no artigo é genérico.', 'vincular no 1.231', 'A — 99 (artigo).')),
    22: ('YELLOW', 'MÉDIO', 'Súmula tributária que se apoia no conceito de empresário do art. 966; relação indireta.',
         ('Relação conceitual (empresa) num tema tributário.', 'Súmula 499 (13/03/2013); STJ referencia CC 966 (e CF 240, CLT 570/577).',
          'Leitor do CC pode esperar jurisprudência civil.', 'rejeitar como não material', 'A — 966, com ficha explicando o uso tributário.')),
    23: ('GREEN', 'BAIXO', 'Monitória de cheque sem força executiva: prazo quinquenal do art. 206, § 5º, I (vigente).', None),
    24: ('RED', '—', 'Restituição na resolução de compra de imóvel é regra consumerista; art. 122 é lateral.', 'Reabrir se surgir precedente sobre condição potestativa (art. 122).'),
    25: ('YELLOW', 'MÉDIO', 'HISTORICAL_BUT_RELEVANT: o enunciado manda aplicar a transição do art. 2.028 (CC/1916 → CC/2002).',
         ('Regra de transição: útil para fatos anteriores a 2003; precisa distinguir CC/1916 de CC/2002 na ficha.',
          'Súmula 547 (14/10/2015): "observada a regra de transição disciplinada em seu art. 2.028".',
          'Baixo para o vínculo; a ficha deve deixar clara a natureza transitória.', 'vincular também no 206, § 3º, IV e § 5º, I',
          'A — 2.028 (com nota temporal).')),
    26: ('RED', '—', 'Credit scoring: núcleo no CDC e na Lei do Cadastro Positivo; abuso de direito é lateral.', 'Reabrir se o STJ fundamentar no art. 187.'),
    27: ('YELLOW', 'MÉDIO', 'Súmula tributária (IPVA) apoiada na tradição; dois targets possíveis (1.226 e 1.267).',
         ('Relação indireta e escolha entre 1.226 (móveis) e 1.267 (regra geral da tradição).',
          'Súmula 585 (14/12/2016); STJ referencia CC 1.226 e 1.267.', 'Tema tributário no CC.', 'vincular no 1.267', 'A — 1.226.')),
    28: ('RED', '—', 'Responsabilidade objetiva do fornecedor (CDC); o ilícito culposo do art. 186 não é o fundamento.', 'Reabrir só com fundamentação no CC.'),
    29: ('GREEN', 'BAIXO', 'Alimentos avoengos: aplicação direta do art. 1.696 (o 1.698 é alvo adicional possível, não alternativo).', None),
    30: ('YELLOW', 'ALTO', 'Boa-fé (art. 422) vigente, mas a súmula é de seguro e os arts. 765/766 foram revogados pela Lei 15.040/2024.',
         ('Possível impacto da Lei 15.040/2024 (nova disciplina do contrato de seguro).',
          'Súmula 609 (11/04/2018): recusa de cobertura por doença preexistente é ilícita sem exames prévios ou prova de má-fé.',
          'A súmula pode não subsistir integralmente sob a lei nova.', 'rejeitar como superada', 'D — manter pendente até análise individual.')),
}


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def evidence(x, amend):
    if x['tribunal'] == 'STJ':
        date, essence = x['decisao'], x['enunciado']
    else:
        base = 'STF:ADI:6792' if x['precedent'] == 'STF:ADI:6792-7055' else x['precedent']
        f = EV.PRECEDENTS[base]
        date, essence = f"{f['judgment_year']} ({f['status_text']})", f['evidence']
    ts = x['proposed_targets'] or [x['discovered_target']]
    vig = {t: ('REVOGADO' if any(a['kind'].lower().startswith('revogad') for a in amend.get(t, [])) else 'VIGENTE') for t in ts}
    leg = sorted({f"{t}: {a['kind']} pela {a['by']}" for t in ts for a in amend.get(t, [])})
    return dict(official_source=x['source']['url'], source_sha256=x['source']['sha256'], official_reference=x['device_label'],
                original_target=x['discovered_target'], proposed_targets=x['proposed_targets'], essence=essence[:300], precedent_date=date,
                target_validity=vig, legislative_changes=leg)


def build():
    dec, amend = load(DEC), load(ANNOT)['amendments']
    card = {k.split('/')[-1] for k in load(CARD)['entries'] if k.startswith('99_JURISPRUDENCIA_V2/03_CONTEUDO/')}
    items = []
    for x in dec['decisions']:
        g, risk, motive, extra = C[x['rank']]
        if g == 'GREEN' and (x['decision'] not in LINKING or x['decision'] == 'REALLOCATE_RECOMMENDED' or x['temporal'] != 'CURRENT'
                             or x['decision'].startswith('UNRESOLVED') or x['source']['tier'] != 'A'):
            raise SystemExit(f'GREEN_RULE_VIOLATION {x["rank"]}')
        if g != 'RED' and x['decision'] not in LINKING:
            raise SystemExit(f'NON_LINKING_NOT_RED {x["rank"]}')
        it = dict(id=f"CCJ1-{x['rank']:02d}", rank=x['rank'], target=x['discovered_target'], proposed_targets=x['proposed_targets'],
                  precedent=x['precedent'], label=x['device_label'], tribunal=x['tribunal'], channel=x['channel'], temporal=x['temporal'],
                  proposed_decision=x['decision'], risk=risk, group=g, motive=motive, status='AWAITING_USER_RATIFICATION', human_approved=False)
        if g in ('GREEN', 'YELLOW'):
            it['evidence'] = evidence(x, amend)
            if any(v == 'REVOGADO' for v in it['evidence']['target_validity'].values()):
                raise SystemExit(f'REVOKED_TARGET_NOT_RED {x["rank"]}')
        if g == 'YELLOW':
            it['yellow'] = dict(problem=extra[0], favor=extra[1], risk=extra[2], option_b=extra[3], recommendation=extra[4])
        if g == 'RED':
            it['reopen'] = extra
        items.append(it)
    green = [i for i in items if i['group'] == 'GREEN']
    rels = sorted({(t, i['precedent']) for i in green for t in i['proposed_targets']})
    fichas = sorted({JT.ficha(p) for _, p in rels})
    cnt = collections.Counter(i['group'] for i in items)
    doc = dict(schema_version=1, kind='CC_J1_RATIFICATION_DOSSIER', batch='CC-J1', not_ratified=True, HUMAN_APPROVED_NEW=0, CC_RELATIONS_PUBLISHED=0,
               SD_CHANGED='NO', FIRMWARE_CHANGED='NO', decisions_sha256_lf=__import__('hashlib').sha256(DEC.read_bytes().replace(b'\r\n', b'\n')).hexdigest(),
               counts=dict(TOTAL=len(items), GREEN=cnt['GREEN'], YELLOW=cnt['YELLOW'], RED=cnt['RED']),
               RATIFY_GREEN_SET_PROPOSAL=dict(ids=[i['id'] for i in green], executed=False, new_relations=len(rels),
                                              new_targets=len({t for t, _ in rels}), distinct_precedents=len({p for _, p in rels}),
                                              distinct_fichas=len(fichas), fichas_already_on_card=[f for f in fichas if f in card],
                                              relations=[dict(target_id=t, precedent=p) for t, p in rels]),
               items=items)
    return doc


def render(doc):
    c, g = doc['counts'], doc['RATIFY_GREEN_SET_PROPOSAL']
    L = ['# CC-J1 — dossiê de ratificação (verde / amarelo / vermelho)', '', '```',
         f"NÃO RATIFICADO · 30 propostas AWAITING_USER_RATIFICATION · HUMAN_APPROVED_NEW = 0 · nada materializado",
         f"TOTAL = {c['TOTAL']} · GREEN = {c['GREEN']} · YELLOW = {c['YELLOW']} · RED = {c['RED']}", '```', '',
         '**GREEN** = `SAFE_FOR_BLOCK_RATIFICATION` (ainda não ratificado) · **YELLOW** = `REVIEW_INDIVIDUALLY` · **RED** = `DO_NOT_RATIFY_NOW`.', '',
         '## Tabela completa', '', '| # | ID | Target CC | Precedente | Tribunal | Fonte | Temporalidade | Decisão proposta | Risco | Grupo | Motivo curto |',
         '|---|---|---|---|---|---|---|---|---|---|---|']
    for i in doc['items']:
        tgt = i['target'] + (f" → {', '.join(i['proposed_targets'])}" if i['proposed_targets'] and i['proposed_targets'] != [i['target']] else '')
        L.append(f"| {i['rank']} | {i['id']} | {tgt} | {i['label']} | {i['tribunal']} | {'PDF oficial STJ' if i['tribunal'] == 'STJ' else 'STF oficial'} | "
                 f"{i['temporal']} | {i['proposed_decision'].replace('_RECOMMENDED', '')} | {i['risk']} | **{i['group']}** | {i['motive']} |")
    L += ['', '## Resumo para ratificação', '', '```', f"GREEN_COUNT = {c['GREEN']}", f"YELLOW_COUNT = {c['YELLOW']}", f"RED_COUNT = {c['RED']}",
          f"TOTAL = {c['TOTAL']}", '```', '']
    for grp, title in (('GREEN', 'GREEN — candidatos à ratificação em bloco'), ('YELLOW', 'YELLOW — revisar individualmente'), ('RED', 'RED — não ratificar')):
        L += [f'**{title}:** `{[i["id"] for i in doc["items"] if i["group"] == grp]}`', '']
    L += ['## Proposta de ratificação GREEN (NÃO executada)', '', '```', f"RATIFY_GREEN_SET = {g['ids']}", '```', '',
          f"Se executada: **{g['new_relations']} relações novas**, **{g['new_targets']} targets novos**, **{g['distinct_precedents']} precedentes distintos**, "
          f"**{g['distinct_fichas']} fichas distintas** (já no cartão: {len(g['fichas_already_on_card'])}).", '', '## Dossiê YELLOW', '']
    for i in doc['items']:
        if i['group'] != 'YELLOW':
            continue
        y = i['yellow']
        L += [f"**{i['id']} — {i['label']}**  ", f"Target proposto: {', '.join(i['proposed_targets'])}  ", f"Problema: {y['problem']}  ",
              f"Evidência a favor: {y['favor']}  ", f"Risco: {y['risk']}  ",
              f"Opções: A. promover no target proposto · B. {y['option_b']} · C. rejeitar · D. manter pendente  ", f"Recomendação do motor: {y['recommendation']}", '']
    L += ['## RED', '', '| ID | Precedente | Motivo | Para reabrir |', '|---|---|---|---|']
    for i in doc['items']:
        if i['group'] == 'RED':
            L.append(f"| {i['id']} | {i['label']} | {i['motive']} | {i['reopen']} |")
    L += ['', 'Evidências completas (fonte, referência, target original/proposto, trecho, data, vigência, alteração legislativa) em '
          '`CC_J1_RATIFICATION_DOSSIER.json` → `items[].evidence`.']
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
    print(doc['counts'], {k: v for k, v in doc['RATIFY_GREEN_SET_PROPOSAL'].items() if k not in ('relations',)})


if __name__ == '__main__':
    main()
