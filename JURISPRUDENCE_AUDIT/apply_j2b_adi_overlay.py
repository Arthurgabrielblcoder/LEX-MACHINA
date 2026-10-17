"""J2B — ADI record model + overlay of the 6 decisions of J2A BATCH01 ratified by the user (2026-10-16). Deterministic, host-only.

Model (no firmware change: the current firmware already classifies TIPO "adi" -> list label "ADI <NUMERO>", ficha 03_CONTEUDO/<IDENTIFICADOR>.TXT):
  legacy JURISPRUDENCIA.IDX row  ID|TIPO|TRIBUNAL|NUMERO|STATUS|TITULO_CURTO|IDENTIFICADOR|FONTE   (same 8 columns, appended at the END)
  ID           STF:ADI:<n>:CF88:<art>:<par>:<inc>:<al>   (same convention as STF:RG:...; joint judgment: <n> = "7047-7064")
  NUMERO       shown in the list after "ADI ": "4425", "7047/7064", "7697 (CAUTELAR)" (provisional marker visible in the list)
  STATUS       procedural status: combination of cautelar | cautelar_referendada | merito_julgado | merito_pendente
  joint judgment: ONE record, aliases [ADI 7047, ADI 7064], both ratified decisions kept in provenance.
Provisional decisions: revalidation registry (trigger = merit judgment) + check_j2b_provisional.py gate (mandatory before any deploy).

Writes:
  LEGAL_TARGET_ID/derived/CF88_JURIS_ADI_ADDITIONS_J2B.json        5 links (6 ratified decisions; 7047/7064 joint) + legacy rows + fichas
  JURISPRUDENCE_AUDIT/J2_HIGH_BACKLOG/J2B_REVALIDATION_REGISTRY.json provisional items (ADI 7697)
Usage: python apply_j2b_adi_overlay.py [--check]
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEC = HERE / 'J2_HIGH_BACKLOG/J2A_BATCH01_DECISIONS.json'
OUT = ROOT / 'LEGAL_TARGET_ID/derived/CF88_JURIS_ADI_ADDITIONS_J2B.json'
REG = HERE / 'J2_HIGH_BACKLOG/J2B_REVALIDATION_REGISTRY.json'
RATIFICATION = dict(by='ARTHUR', on='2026-10-16', statement='J2A_BATCH01_USER_RATIFIED = YES',
                    decisions={'J0-BL-136': 'PROMOTE_PROVISIONAL', 'J0-BL-137': 'PROMOTE_PROVISIONAL', 'J0-BL-138': 'PROMOTE_PROVISIONAL',
                               'J0-BL-081': 'PROMOTE', 'J0-BL-082': 'PROMOTE', 'J0-BL-084': 'PROMOTE', 'J0-BL-080': 'REJECT_TEMPORAL_MISMATCH',
                               'J0-BL-069': 'REJECT_FALSE_POSITIVE', 'J0-BL-074': 'REJECT_FALSE_POSITIVE', 'J0-BL-135': 'DUPLICATE_DO_NOT_PROMOTE'},
                    directives='ADI 7697: status explícito de cautelar referendada, mérito pendente, gatilho obrigatório de revalidação. ADIs 7047 e 7064: '
                               'as duas ratificadas; representação no aparelho decidida na J2B sem duplicar a ficha. HIGH = 42 é o estado correto.')
STATUS_VALUES = ('cautelar', 'cautelar_referendada', 'merito_julgado', 'merito_pendente')
URL_7697 = 'https://portal.stf.jus.br/processos/detalhe.asp?incidente=6997560'
URL_7064 = 'https://portal.stf.jus.br/processos/detalhe.asp?incidente=6330822'
URL_7047 = 'https://portal.stf.jus.br/processos/detalhe.asp?incidente=6318731'
URL_4425 = 'https://jurisprudencia.stf.jus.br/pages/search?classeNumeroIncidente=%22ADI%204425%22&base=acordaos'

PRECEDENTS = {
    'STF:ADI:7697': dict(numero_lista='7697 (CAUTELAR)', titulo='ADI 7697', aliases=['ADI 7697'], status=['cautelar_referendada', 'merito_pendente'],
                         provisional=True, fonte=URL_7697, sources=['S7', 'P1'],
                         ficha=[
                             'AÇÃO DIRETA DE INCONSTITUCIONALIDADE 7697',
                             'TRIBUNAL: STF',
                             'STATUS: medida cautelar referendada pelo Plenário - mérito pendente',
                             'PROCESSO: ADI 7697 (Rel. Min. Flávio Dino; requerente: PSOL)',
                             '',
                             'DECISÃO PROVISÓRIA',
                             'Esta é uma decisão cautelar, não definitiva. Pode mudar quando o mérito for julgado.',
                             '',
                             'DISPOSITIVOS DA CF ALCANÇADOS',
                             'Art. 165, § 9º, III, e § 10; art. 166, §§ 9º, 9º-A, 10, 11, 12, 13, 14, 16, 17, 18, 19 e 20; art. 166-A.',
                             '',
                             'DECISÃO (RESUMO)',
                             'Em 16/08/2024 o Plenário referendou, por unanimidade, a cautelar que deu interpretação conforme a esses dispositivos, '
                             'com efeitos ex nunc: não é compatível com a Constituição executar emendas ao orçamento que não obedeçam a critérios '
                             'técnicos de eficiência, transparência e rastreabilidade; a impositividade das emendas parlamentares não é absoluta.',
                             'Em 04/12/2024 o Plenário referendou nova decisão: nas transferências especiais ("emendas PIX", art. 166-A), a '
                             'apresentação e a aprovação prévias do plano de trabalho no Transferegov.br são obrigatórias.',
                             '',
                             'VERIFICADO EM',
                             '16/10/2026 (andamento: autos conclusos ao relator em 16/06/2026).',
                             '',
                             'FONTE OFICIAL',
                             URL_7697]),
    'STF:ADI:7047-7064': dict(numero_lista='7047/7064', titulo='ADI 7047/7064 (julgamento conjunto)', aliases=['ADI 7047', 'ADI 7064'],
                              status=['merito_julgado'], provisional=False, fonte=URL_7064, sources=['S5', 'S6', 'S4', 'P1'],
                              joint_judgment=dict(processes=['STF:ADI:7047', 'STF:ADI:7064'], date='2023-11-30',
                                                  ratified_decisions=['J0-BL-081', 'J0-BL-082'],
                                                  model='um registro, dois identificadores (aliases); uma ficha'),
                              ficha=[
                                  'AÇÕES DIRETAS DE INCONSTITUCIONALIDADE 7047 E 7064 (JULGAMENTO CONJUNTO)',
                                  'TRIBUNAL: STF',
                                  'STATUS: mérito julgado',
                                  'PROCESSO: ADI 7047 e ADI 7064 (Rel. Min. Luiz Fux)',
                                  '',
                                  'DECISÃO',
                                  'Em 30/11/2023, em sessão virtual extraordinária, o Plenário converteu o julgamento das cautelares em julgamento de '
                                  'mérito e julgou as duas ações parcialmente procedentes (vencido em parte o Min. André Mendonça).',
                                  '',
                                  'ART. 100 DA CF',
                                  '- Declarado inconstitucional o § 9º do art. 100, na redação da EC 113/2021 (depósito, à conta do juízo, do valor de '
                                  'débitos do credor inscritos em dívida ativa). Segundo a ementa, a nova redação, embora diferente, tem a mesma essência '
                                  'da compensação já declarada inconstitucional nas ADIs 4357 e 4425.',
                                  '- Interpretação conforme ao § 11 do art. 100 (EC 113/2021), para excluir a expressão "com auto aplicabilidade para a União".',
                                  '- Declarado inconstitucional também o art. 101, § 5º, do ADCT (EC 113/2021).',
                                  '',
                                  'SOMENTE NA ADI 7064',
                                  'Art. 107-A do ADCT (teto de precatórios) válido só para 2022; incisos II e III e §§ 3º, 5º e 6º inconstitucionais; '
                                  'inconstitucional o art. 6º da EC 114/2021.',
                                  '',
                                  'ACÓRDÃO',
                                  'ADI 7064: julgamento em 01/12/2023, DJe de 19/12/2023.',
                                  '',
                                  'FONTE OFICIAL',
                                  URL_7064,
                                  URL_7047]),
    'STF:ADI:4425': dict(numero_lista='4425', titulo='ADI 4425', aliases=['ADI 4425'], status=['merito_julgado'], provisional=False, fonte=URL_4425,
                         sources=['S3', 'S4', 'P1'],
                         ficha=[
                             'AÇÃO DIRETA DE INCONSTITUCIONALIDADE 4425',
                             'TRIBUNAL: STF',
                             'STATUS: mérito julgado (com modulação de efeitos)',
                             'PROCESSO: ADI 4425 (Rel. Min. Ayres Britto; redator do acórdão Min. Luiz Fux), julgada com a ADI 4357',
                             '',
                             'DECISÃO (MÉRITO: 14/03/2013; DJe 19/12/2013)',
                             'Pedido julgado procedente em parte contra a EC 62/2009 (regime de precatórios). Sobre o § 12 do art. 100:',
                             '- é inconstitucional atualizar os precatórios pelo índice oficial de remuneração da caderneta de poupança;',
                             '- declaração parcial de inconstitucionalidade, sem redução de texto, da expressão "independentemente de sua natureza": '
                             'nos precatórios tributários valem os mesmos juros de mora dos créditos tributários.',
                             'O acórdão também invalidou a compensação dos §§ 9º e 10 (redação da EC 62/2009), o marco "na data de expedição do '
                             'precatório" do § 2º e o regime especial de pagamento criado pela EC 62/2009.',
                             '',
                             'MODULAÇÃO (QUESTÃO DE ORDEM: 25/03/2015; DJe 04/08/2015)',
                             'A TR foi mantida até 25/03/2015; depois, IPCA-E para os precatórios em geral e, nos tributários, os mesmos critérios '
                             'com que a Fazenda corrige seus créditos.',
                             '',
                             'NOTA',
                             'O § 12 continua no texto compilado com a redação da EC 62/2009. A EC 113/2021 adotou a SELIC como índice único de '
                             'atualização, e o STF admitiu esse índice ao julgar as ADIs 7047 e 7064.',
                             '',
                             'FONTE OFICIAL',
                             URL_4425]),
}
# (target, precedent, legacy key, ratified decision ids)
LINKS = [
    ('CF88:ART.100:PAR.9', 'STF:ADI:7047-7064', 'STF:ADI:7047-7064:CF88:100:9:-:-', ['J0-BL-081', 'J0-BL-082'], ('CF88', '100', '9', '', '')),
    ('CF88:ART.100:PAR.12', 'STF:ADI:4425', 'STF:ADI:4425:CF88:100:12:-:-', ['J0-BL-084'], ('CF88', '100', '12', '', '')),
    ('CF88:ART.166:PAR.9', 'STF:ADI:7697', 'STF:ADI:7697:CF88:166:9:-:-', ['J0-BL-136'], ('CF88', '166', '9', '', '')),
    ('CF88:ART.166:PAR.11', 'STF:ADI:7697', 'STF:ADI:7697:CF88:166:11:-:-', ['J0-BL-137'], ('CF88', '166', '11', '', '')),
    ('CF88:ART.166-A', 'STF:ADI:7697', 'STF:ADI:7697:CF88:166-A:-:-:-', ['J0-BL-138'], ('CF88', '166-A', '', '', '')),
]
REVALIDATION = dict(trigger='JULGAMENTO_DE_MERITO', max_age_days=90, last_verified_on='2026-10-16',
                    last_known_state='MC referendada em 16/08/2024 e referendo de 04/12/2024; autos conclusos ao relator em 16/06/2026; sem mérito',
                    check=dict(url=URL_7697 + ' (abas Andamentos e Decisões)', look_for='Decisão de julgamento de mérito (Procedente / Improcedente / '
                                                                                   'Prejudicada / Não conhecida) ou nova decisão do Plenário'),
                    on_trigger='Rever o vínculo e a ficha antes de qualquer novo deploy; sem revisão, o item volta a pendente (fail closed).')


def sha_lf(p):
    return hashlib.sha256(Path(p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def build():
    d = json.loads(DEC.read_text(encoding='utf-8'))
    dec = {x['recommendation_id']: x for x in d['decisions']}
    if sorted(dec) != sorted(RATIFICATION['decisions']):
        raise SystemExit('RATIFICATION_DOES_NOT_COVER_BATCH01')
    promoted = sorted(r for r, v in RATIFICATION['decisions'].items() if v.startswith('PROMOTE'))
    if sorted(r for *_, rs, _ in LINKS for r in rs) != promoted:
        raise SystemExit('LINKS_DO_NOT_MATCH_RATIFIED_PROMOTIONS')
    records = []
    for target, prec, key, rids, lookup in LINKS:
        p = PRECEDENTS[prec]
        for r in rids:
            x = dec[r]
            if x['recommended_target'] != target or x['decision'] != 'PROMOTE_RECOMMENDED':
                raise SystemExit('RATIFIED_DECISION_MISMATCH ' + r)
            if (prec != 'STF:ADI:7047-7064') and x['precedent'] != prec:
                raise SystemExit('PRECEDENT_MISMATCH ' + r)
        if any(s not in STATUS_VALUES for s in p['status']):
            raise SystemExit('BAD_STATUS ' + prec)
        status = '_'.join(p['status'])
        records.append(dict(
            target_id=target, source_id=prec, source_reference_id=key, label=p['titulo'], aliases=p['aliases'],
            status_processual=p['status'], provisional=p['provisional'], ratified_decisions=rids,
            ratification=[RATIFICATION['decisions'][r] for r in rids], sources=p['sources'],
            joint_judgment=p.get('joint_judgment'),
            legacy_idx_row='|'.join((key, 'adi', 'STF', p['numero_lista'], status, p['titulo'], prec, p['fonte'])),
            legacy_lookup=list(lookup),
            payload=dict(tribunal='STF', tipo='adi', numero=p['numero_lista'], titulo=p['titulo'], fonte=p['fonte'], status_processual=status,
                         aliases=p['aliases'], provisorio=p['provisional'])))
    fichas = {prec: '\n'.join(p['ficha']) + '\n' for prec, p in PRECEDENTS.items()}
    doc = dict(schema_version=1, norma_id='CF88', round='J2B', ratification=RATIFICATION, decisions_file=DEC.relative_to(ROOT).as_posix(),
               decisions_sha256=sha_lf(DEC), model=dict(tipo='adi', status_values=list(STATUS_VALUES), firmware_change='NONE',
                                                        list_label='"ADI " + NUMERO', ficha='03_CONTEUDO/<IDENTIFICADOR com : -> _>.TXT',
                                                        joint_judgment='um registro com aliases; uma ficha; as decisões ratificadas ficam na provenance'),
               total=len(records), records=records, fichas=fichas)
    reg = dict(schema_version=1, round='J2B', policy='Itens provisórios (cautelar / mérito pendente). Gate obrigatório antes de qualquer deploy: '
                                                    'check_j2b_provisional.py --as-of <data>. Fail closed.',
               items=[dict(source_id=prec, targets=[t for t, pr, *_ in LINKS if pr == prec], status_processual=p['status'], **REVALIDATION)
                      for prec, p in PRECEDENTS.items() if p['provisional']])
    enc = lambda o: (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8')  # noqa: E731
    return [(OUT, enc(doc)), (REG, enc(reg))]


if __name__ == '__main__':
    outs = build()
    if '--check' in sys.argv:
        ok = all(p.is_file() and p.read_bytes() == b for p, b in outs)
        print('UP_TO_DATE' if ok else 'STALE')
        sys.exit(0 if ok else 1)
    for p, b in outs:
        p.write_bytes(b)
        print(p.name, hashlib.sha256(b).hexdigest())
