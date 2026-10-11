"""CF88_CORRELATA_C1A_CURRENT_LINK_SANITIZATION_REVIEW — decisions on the 19 current CORRELATA links flagged NEEDS_REVIEW by C0.

HUMAN-ASSISTED DECISION RECORD. Nothing is applied: no overlay, no exclusion, no RUN4, no SD/firmware change. The decisions below were
taken item by item against the official text of each destination norm (Planalto, ccivil_03), downloaded on the verification date and
identified by sha256 (the HTML itself is not versioned). The 19 items are read from the C0 queue (CURRENT_LINK_REVIEW, plausibility
NEEDS_REVIEW) and frozen as a snapshot inside the decisions file before any decision.

Writes CORRELATA_COVERAGE_AUDIT/CF88_CORRELATA_C1A_DECISIONS.json and CF88_CORRELATA_C1A_CURRENT_LINK_REVIEW.md (deterministic).
Usage: python build_c1a_review.py [--check]
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
ROOT = AUDIT.parent
sys.path.insert(0, str(ROOT / 'LEGAL_TARGET_ID'))
import target_id as T  # noqa: E402

MISSION = 'CF88_CORRELATA_C1A_CURRENT_LINK_SANITIZATION_REVIEW'
BASE = dict(branch='cf-correlata-coverage-audit', head='a4b9867411db431a84c5be06c35a83639ff8909d',
            physical_origin='device-entenda-810 @ 44ef69ba3957d9c55a6b4b5fe9f9f68fcd77efef', reference_engine='RUN3')
QUEUE = AUDIT / 'CF88_CORRELATA_REVIEW_QUEUE.json'
BASELINE = AUDIT / 'CF88_CORRELATA_CURRENT_BASELINE.json'
OUT_JSON = AUDIT / 'CF88_CORRELATA_C1A_DECISIONS.json'
OUT_MD = AUDIT / 'CF88_CORRELATA_C1A_CURRENT_LINK_REVIEW.md'
VERIFIED_ON = '2026-10-11'
DECISIONS = ('KEEP', 'KEEP_WITH_ROUTE_FIX', 'RETARGET', 'REPLACE', 'REMOVE', 'HOLD')
P = 'https://www.planalto.gov.br/ccivil_03/'

# Official sources consulted (Planalto). sha256/bytes of the HTML as downloaded on VERIFIED_ON.
SOURCES = {
    'CF88': dict(norm='Constituição Federal (texto compilado, com redações anteriores)', url=P + 'constituicao/constituicao.htm',
                 sha256='d22db6b86fe90c8626e26753adf5b34d127272959b280e7955df0a9eb0b946cf', bytes=1840587),
    'LEI_9984_2000': dict(norm='Lei nº 9.984/2000 (ANA)', url=P + 'leis/l9984.htm',
                          sha256='558ae5d3c1fc8d6c56d3a4119b352428230b6bd2b8077981454aece253e9eae2', bytes=222218),
    'LEI_7990_1989': dict(norm='Lei nº 7.990/1989 (compensação financeira)', url=P + 'leis/l7990.htm',
                          sha256='cf0d4faceb8e9f5b2e1b5d7b5418862ce7c51bcf02fb70a8d58f62aee2ba6e64', bytes=37921),
    'LEI_13460_2017': dict(norm='Lei nº 13.460/2017 (usuário de serviços públicos)', url=P + '_ato2015-2018/2017/lei/l13460.htm',
                           sha256='28d0650407dea4bbc49b141fb5f4d65a5659e8194990b3249ddb45c681569722', bytes=69906),
    'LEI_12527_2011': dict(norm='Lei nº 12.527/2011 (LAI)', url=P + '_ato2011-2014/2011/lei/l12527.htm',
                           sha256='763c95e3090fa0bdf238e64e876f37c927a98563104aad0df1d9cfacf38bdb33', bytes=109489),
    'LC_112_2001': dict(norm='Lei Complementar nº 112/2001 (RIDE Grande Teresina)', url=P + 'leis/lcp/lcp112.htm',
                        sha256='c8103f55daa39ec93f02091d2b67a99ce61de0246d69f87bfdd60f4d19a2b22b', bytes=9886),
    'LC_124_2007': dict(norm='Lei Complementar nº 124/2007 (SUDAM)', url=P + 'leis/lcp/lcp124.htm',
                        sha256='fd48b9a47de04160187e8a6d19663d117e3826b9d6718768976afcebff1e0df1', bytes=48339),
    'LC_125_2007': dict(norm='Lei Complementar nº 125/2007 (SUDENE)', url=P + 'leis/lcp/lcp125.htm',
                        sha256='2460f6e9635a95b49075ae571007dad0ad81f3a0825e5d36afdee34d240bf9f8', bytes=74128),
    'LC_129_2009': dict(norm='Lei Complementar nº 129/2009 (SUDECO)', url=P + 'leis/lcp/lcp129.htm',
                        sha256='138ce8b84a7d156561dbe2111172879cb32fa4afcb373745325069e19511b46d', bytes=83253),
    'LEI_11250_2005': dict(norm='Lei nº 11.250/2005', url=P + '_ato2004-2006/2005/lei/l11250.htm',
                           sha256='cf6fc96bbe7ed7031974c7cfc64294234212526592345953c419d145c73939d0', bytes=12862),
    'LEI_8981_1995': dict(norm='Lei nº 8.981/1995', url=P + 'leis/l8981.htm',
                          sha256='3f6450796771ccde84710641491b7760d51de3d03fb7ba8a128c4ee4be3465c9', bytes=303019),
    'LEI_9393_1996': dict(norm='Lei nº 9.393/1996 (ITR)', url=P + 'leis/l9393.htm',
                          sha256='3e81e78a7d7b56d0f741f84a0df1941af4391b2d67301cf4ae3f4ce19df15814', bytes=54425),
    'LC_87_1996': dict(norm='Lei Complementar nº 87/1996 (ICMS, Lei Kandir)', url=P + 'leis/lcp/lcp87.htm',
                       sha256='47bb22063ba170cd75425fb6a927780f83b8dbef6e047db857d3a113eceac772', bytes=270282),
    'LC_62_1989': dict(norm='Lei Complementar nº 62/1989 (FPE/FPM)', url=P + 'leis/lcp/lcp62.htm',
                       sha256='a0970c8be6abcb36817a4bc72b8402f53524a1d49c7b8a50810e8c2d4fb9c688', bytes=34151),
    'LC_63_1990': dict(norm='Lei Complementar nº 63/1990 (parcelas municipais; valor adicionado)', url=P + 'leis/lcp/lcp63.htm',
                       sha256='da8f7f7a27a50d58ec4e1825bf94991d8b00cd0368c836ec3ad329e28b687120', bytes=27959),
    'LEI_13425_2017': dict(norm='Lei nº 13.425/2017 (prevenção de incêndios)', url=P + '_ato2015-2018/2017/lei/l13425.htm',
                           sha256='f02a9ce52170c0e183ef711fa0c4affefb70e1a0ecb8050b4120130734bb3dca', bytes=52320),
    'LEI_10257_2001': dict(norm='Lei nº 10.257/2001 (Estatuto da Cidade)', url=P + 'leis/leis_2001/l10257.htm',
                           sha256='ef4562c4c1a136f965e7c548199a1cc3b8ab91837278ccc5295d9173e303087b', bytes=123344),
    'LC_70_1991': dict(norm='Lei Complementar nº 70/1991 (COFINS)', url=P + 'leis/lcp/lcp70.htm',
                       sha256='63315c060d197e272f449ae244cde5093ea93c90c1d21eb187fbd287c72b0a88', bytes=22142),
    'LEI_8212_1991': dict(norm='Lei nº 8.212/1991 (custeio da seguridade)', url=P + 'leis/l8212cons.htm',
                          sha256='12c5bda5cffd920da7093757ceb796651f937e0306d341c19348a3d040a09e1d', bytes=771751),
    'LEI_7998_1990': dict(norm='Lei nº 7.998/1990 (seguro-desemprego/abono/FAT)', url=P + 'leis/l7998.htm',
                          sha256='674335b5ec1bf3edd518c27bbbad3838cca9635225dd08967733ae88fcf36558', bytes=118913),
}


def R(rel, tid):
    return f'CORRELATA:{rel}@{tid}'


# One record per current link. 'evidence' = what the official text says (short paraphrase + the decisive provision).
REVIEW = [
    dict(reference_id=R('REL_0628FE08FD9A170F', 'CF88:ART.20:PAR.1'), decision='REPLACE', confidence='MEDIA',
         sources=['LEI_9984_2000', 'LEI_7990_1989'],
         destination_provisions='Lei 9.984/2000: ementa (cria a ANA); art. 28 altera o art. 17 da Lei 9.648/1998 (percentual da compensação '
                                'financeira por recursos hídricos) e o art. 29 altera a Lei 8.001/1990 (rateio). Lei 7.990/1989: ementa '
                                '"Institui ... compensação financeira pelo resultado da exploração de petróleo ou gás natural, de recursos '
                                'hídricos para fins de geração de energia elétrica, de recursos minerais..."; arts. 1º e 2º.',
         analysis='O § 1º assegura, nos termos da lei, participação ou compensação financeira pela exploração de petróleo, gás, recursos '
                  'hídricos e minerais. A Lei 9.984/2000 é a lei da ANA: só os arts. 28 e 29, que alteram outras leis, tocam a '
                  'compensação hídrica, e o salto atual abre a norma sem artigo. A lei que institui e disciplina a compensação do § 1º é '
                  'a Lei 7.990/1989, depois complementada pela Lei 8.001/1990. Manter a Lei 9.984 como correlata do § 1º inteiro dá '
                  'destaque a uma norma de órgão, com conteúdo só reflexo.',
         replacement_norms=[dict(norm_key='LEI:7990/1989', norm_name='Lei nº 7.990/1989', target_id='CF88:ART.20:PAR.1',
                                 relation_type='REGULAMENTA', route='ABRIR_ARTIGO_INTERNO art. 1º (ou norma inteira)',
                                 acervo_status='INGESTION_REQUIRED')],
         note='A Lei 8.001/1990 (percentuais e rateio) e a Lei 12.734/2012, já vinculada (royalties), complementam. A Lei 9.984 sai do target.'),
    dict(reference_id=R('REL_9DFE2FF258879347', 'CF88:ART.37:PAR.3:INC.II'), decision='REPLACE', confidence='ALTA',
         sources=['LEI_13460_2017', 'LEI_12527_2011'],
         destination_provisions='Lei 13.460/2017, art. 1º, § 1º: aplica-se "nos termos do inciso I do § 3º do art. 37"; art. 2º, parágrafo único: '
                                '"O acesso do usuário a informações será regido pelos termos da Lei nº 12.527". Lei 12.527/2011: ementa '
                                'e art. 1º, "acesso a informações previsto no inciso XXXIII do art. 5º, no inciso II do § 3º do art. 37 e no '
                                '§ 2º do art. 216".',
         analysis='O inciso II trata do acesso a registros administrativos e a informações sobre atos de governo. A própria Lei 13.460 '
                  'remete essa matéria à LAI e declara apoio apenas no inciso I. A LAI regulamenta expressamente o inciso II. O vínculo '
                  'atual vem do fan-out da relação do inciso I.',
         replacement_norms=[dict(norm_key='LEI:12527/2011', norm_name='Lei nº 12.527/2011 (LAI)', target_id='CF88:ART.37:PAR.3:INC.II',
                                 relation_type='REGULAMENTA', route='norma principal LAI2011, art. 1º', acervo_status='IN_MAIN_CORPUS')],
         note='A rota de aparelho para norma do acervo principal ainda não existe (MAIN_CORPUS_ROUTE_REQUIRED, C0).'),
    dict(reference_id=R('REL_9DFE2FF258879347', 'CF88:ART.37:PAR.3:INC.III'), decision='HOLD', confidence='BAIXA',
         sources=['LEI_13460_2017'],
         destination_provisions='Lei 13.460/2017, art. 1º, § 1º: fundamento declarado só no inciso I. Art. 2º, V: "manifestações" incluem '
                                'reclamações e denúncias sobre "a conduta de agentes públicos na prestação e fiscalização de tais serviços".',
         analysis='O inciso III trata da disciplina da representação contra exercício negligente ou abusivo de cargo, emprego ou função. A Lei '
                  '13.460 não se declara regulamentadora do inciso III, mas o regime de manifestações e denúncias sobre a conduta de '
                  'agentes cobre parte da matéria, só no âmbito da prestação de serviços. Não localizei em fonte oficial uma norma geral '
                  'apontada como disciplina do inciso III. Sem essa base, nem remover nem manter é seguro.',
         note='Revisão independente: decidir entre REMOVE (fan-out do inciso I) e KEEP parcial (art. 2º, V), e pesquisar a norma geral do inciso III.'),
    dict(reference_id=R('REL_4468A85CBDDD620A', 'CF88:ART.43:PAR.1:INC.I'), decision='REMOVE', confidence='ALTA',
         sources=['LC_112_2001'],
         destination_provisions='LC 112/2001, ementa e art. 1º: autoriza a criação da RIDE da Grande Teresina (Piauí e Maranhão), '
                                '"conforme o previsto no inciso IX do art. 21, no art. 43, e no inciso IV do art. 48".',
         analysis='O inciso I pede a lei complementar das condições gerais de integração de regiões em desenvolvimento. A LC 112 cria uma região '
                  'específica: é aplicação concreta, uma entre várias RIDEs, e não a disciplina geral. Ela não cita o § 1º nem o inciso I. '
                  'O vínculo é estreito e resulta do fan-out para os dois incisos.',
         note='Nenhuma substituta confirmada para o inciso I nesta rodada.'),
    dict(reference_id=R('REL_4468A85CBDDD620A', 'CF88:ART.43:PAR.1:INC.II'), decision='REPLACE', confidence='MEDIA',
         sources=['LC_112_2001', 'LC_124_2007', 'LC_125_2007', 'LC_129_2009'],
         destination_provisions='LC 124/2007: "Institui, na forma do art. 43 da Constituição Federal, a SUDAM; estabelece sua composição...". '
                                'LC 125/2007: idem para a SUDENE ("estabelece sua composição"). LC 129/2009: "Institui, na forma do art. 43 '
                                'da Constituição Federal, a SUDECO, estabelece sua missão institucional, natureza jurídica, objetivos, área '
                                'de atuação, instrumentos de ação".',
         analysis='O inciso II trata da composição dos organismos regionais que executam os planos regionais. As LCs 124, 125 e 129 instituem, '
                  'na forma do art. 43, SUDAM, SUDENE e SUDECO: são exatamente esses organismos. As ementas das LCs 124 e 125 dizem que elas '
                  'estabelecem a composição; a da LC 129 fala em estrutura e natureza. A LC 112 (uma RIDE) '
                  'não fixa composição de organismo executor de plano regional nacional. Substituição confirmada pelas ementas oficiais.',
         replacement_norms=[dict(norm_key=k, norm_name=n, target_id='CF88:ART.43:PAR.1:INC.II', relation_type='ORGANIZA_INSTITUIÇÃO',
                                 route='ementa / art. 1º', acervo_status='INGESTION_REQUIRED')
                            for k, n in (('LC:124/2007', 'Lei Complementar nº 124/2007 (SUDAM)'),
                                         ('LC:125/2007', 'Lei Complementar nº 125/2007 (SUDENE)'),
                                         ('LC:129/2009', 'Lei Complementar nº 129/2009 (SUDECO)'))],
         note='Confiança média: as LCs se apoiam no art. 43 como um todo; a revisão independente pode preferir o vínculo no art. 43 ou no § 1º.'),
    dict(reference_id=R('REL_0920FF60E61E5491', 'CF88:ART.153:PAR.4:INC.II'), decision='REMOVE', confidence='ALTA',
         sources=['LEI_11250_2005', 'LEI_9393_1996'],
         destination_provisions='Lei 11.250/2005, ementa: "Regulamenta o inciso III do § 4º do art. 153"; art. 1º trata dos convênios com os '
                                'Municípios optantes.',
         analysis='O inciso II é a não incidência sobre pequenas glebas. A Lei 11.250 regula só a opção municipal do inciso III, irmão. A '
                  'disciplina das pequenas glebas está no art. 2º da Lei 9.393/1996, que já tem vínculo nesse inciso (fora do escopo C1A, '
                  'avaliado PLAUSIBLE pela C0). É fan-out puro.',
         note='O vínculo da Lei 11.250 no inciso III continua (PLAUSIBLE_STRONG na C0).'),
    dict(reference_id=R('REL_2C57B972486FE4AE', 'CF88:ART.153:PAR.4:INC.II'), decision='REMOVE', confidence='ALTA',
         sources=['LEI_8981_1995'],
         destination_provisions='Lei 8.981/1995: ementa "Altera a legislação tributária federal". Os artigos do salto atual são o art. 90 (prazo '
                                'de pagamento do ITR no art. 14 da Lei 8.847/1994, revogada pela Lei 9.393/1996) e o art. 117 (cláusula '
                                'revogatória).',
         analysis='Nenhum dispositivo da lei trata de pequenas glebas. O art. 90 alterava o prazo de pagamento numa lei de ITR já revogada. O '
                  'vínculo é temático e obsoleto.'),
    dict(reference_id=R('REL_2C57B972486FE4AE', 'CF88:ART.153:PAR.4:INC.III'), decision='REMOVE', confidence='ALTA',
         sources=['LEI_8981_1995'],
         destination_provisions='Idem: arts. 90 e 117. Não há disposição sobre fiscalização ou cobrança do ITR por Municípios optantes. O '
                                'inciso III foi criado pela EC 42/2003, depois da lei.',
         analysis='A lei é anterior ao próprio inciso III, que nasceu com a EC 42/2003, e não tem conteúdo sobre a opção municipal. É falso '
                  'vínculo.'),
    dict(reference_id=R('REL_D152FF761345E231', 'CF88:ART.153:PAR.4:INC.III'), decision='REMOVE', confidence='ALTA',
         sources=['LEI_9393_1996', 'LEI_11250_2005'],
         destination_provisions='Lei 9.393/1996: lei do ITR. O art. 2º regula a imunidade das pequenas glebas, "nos termos do art. 153, § 4º, '
                                'in fine". As menções a "município" são regras de localização do imóvel. Não há regime de opção municipal.',
         analysis='O inciso III, opção dos Municípios para fiscalizar e cobrar, foi criado pela EC 42/2003 e é regulamentado pela Lei '
                  '11.250/2005, que já está vinculada. A Lei 9.393 serve ao inciso II, não ao III. É fan-out entre irmãos.'),
    dict(reference_id=R('REL_FEB2B8ACAD1A48FA', 'CF88:ART.155:PAR.1:INC.III'), decision='REMOVE', confidence='ALTA',
         sources=['LC_87_1996', 'CF88'],
         destination_provisions='LC 87/1996, ementa: "Dispõe sobre o imposto dos Estados ... sobre operações relativas à circulação de '
                                'mercadorias ... (LEI KANDIR)". Não há disposição sobre transmissão causa mortis ou doação.',
         analysis='O § 1º do art. 155 disciplina o imposto do inciso I (ITCMD). O inciso III pede lei complementar para a competência em '
                  'casos com elemento no exterior. A LC 87 é a lei do ICMS (inciso II e § 2º). Não há relação normativa: é erro de '
                  'atribuição. Não confirmei substituta específica para o inciso III nesta rodada.',
         note='A LC 87/1996 continua vinculada ao art. 155, § 2º, XII (fora do escopo C1A).'),
    dict(reference_id=R('REL_B41DCE7A7582235E', 'CF88:ART.161:INC.I'), decision='REPLACE', confidence='ALTA',
         sources=['LC_62_1989', 'LC_63_1990'],
         destination_provisions='LC 62/1989, art. 1º: regula FPE e FPM, "consoante o disposto nos incisos II e III do art. 161". LC 63/1990, '
                                'art. 3º, § 1º: "O valor adicionado corresponderá, para cada Município, ..." (conceito do art. 158, § 1º, I).',
         analysis='O inciso I manda a lei complementar definir valor adicionado para o art. 158, § 1º, I. A LC 62 se declara apoiada só nos '
                  'incisos II e III. A definição de valor adicionado está no art. 3º, § 1º, da LC 63/1990. A LC 62 continua correta '
                  'nos incisos II e III.',
         replacement_norms=[dict(norm_key='LC:63/1990', norm_name='Lei Complementar nº 63/1990', target_id='CF88:ART.161:INC.I',
                                 relation_type='REGULAMENTA', route='ABRIR_ARTIGO_INTERNO art. 3º (EXT_LC63_1990)',
                                 acervo_status='EXTERNAL_ALREADY_INGESTED')],
         note='A LC 63 já está no cartão (EXT_LC63_1990). Substituição sem ingestão: falta só a relação aprovada e a linha RELACOES.'),
    dict(reference_id=R('REL_70C4549A507F6E00', 'CF88:ART.182'), decision='RETARGET', confidence='MEDIA',
         sources=['LEI_13425_2017', 'LEI_10257_2001'],
         destination_provisions='Lei 13.425/2017, art. 1º, I: estabelece diretrizes gerais sobre prevenção e combate a incêndio, "atendendo ao '
                                'disposto no inciso XX do art. 21, no inciso I, in fine, do art. 24, no § 5º, in fine, do art. 144 e no caput '
                                'do art. 182".',
         analysis='A lei declara expressamente apoio no caput do art. 182, que trata de diretrizes gerais da política urbana fixadas em lei, e '
                  'não nos §§ 1º a 4º (plano diretor, desapropriação, parcelamento compulsório). A relação é real, mas setorial. O '
                  'target correto é o caput, não o artigo inteiro. A correlata principal do art. 182 é o Estatuto da Cidade, Lei '
                  '10.257/2001, que "Regulamenta os arts. 182 e 183". Ele já é candidato C0, fora deste escopo, e não deve ser '
                  'confundido com esta revisão.',
         retarget_to='CF88:ART.182:CAPUT', route='ABRIR_ARTIGO_INTERNO art. 1º (inalterado)',
         note='Na tela, ART.182 e ART.182:CAPUT são a mesma linha (única equivalência permitida). O retarget registra a especificidade '
              'no dado.'),
    dict(reference_id=R('REL_EA8171739858C1AC', 'CF88:ART.195:INC.II'), decision='REPLACE', confidence='ALTA',
         sources=['LC_70_1991', 'LEI_8212_1991'],
         destination_provisions='LC 70/1991, art. 1º: institui a contribuição "nos termos do inciso I do art. 195", devida pelas pessoas '
                                'jurídicas e incidente sobre o faturamento (COFINS). Lei 8.212/1991, Capítulo III ("Da Contribuição do '
                                'Segurado"), arts. 20 e 21.',
         analysis='O inciso II é a contribuição do trabalhador e dos demais segurados. A LC 70 trata da contribuição do empregador sobre o '
                  'faturamento (inciso I, b) e se declara apoiada só no inciso I. A contribuição dos segurados é disciplinada pela Lei '
                  '8.212/1991, arts. 20 e seguintes.',
         replacement_norms=[dict(norm_key='LEI:8212/1991', norm_name='Lei nº 8.212/1991', target_id='CF88:ART.195:INC.II',
                                 relation_type='REGULAMENTA', route='norma principal CUSTEIO1991, art. 20', acervo_status='IN_MAIN_CORPUS')],
         note='A LC 70 continua no inciso I (PLAUSIBLE_STRONG).'),
    dict(reference_id=R('REL_EA8171739858C1AC', 'CF88:ART.195:PAR.1'), decision='REMOVE', confidence='ALTA',
         sources=['LC_70_1991'],
         destination_provisions='LC 70/1991: nenhuma disposição sobre receitas de Estados, DF e Municípios nos respectivos orçamentos.',
         analysis='O § 1º é regra orçamentária federativa. A COFINS é tributo federal sobre faturamento, sem relação normativa com o '
                  'parágrafo. É fan-out da relação do inciso I.'),
    dict(reference_id=R('REL_EA8171739858C1AC', 'CF88:ART.195:PAR.2'), decision='REMOVE', confidence='ALTA',
         sources=['LC_70_1991'],
         destination_provisions='LC 70/1991: nenhuma disposição sobre a elaboração integrada da proposta de orçamento da seguridade.',
         analysis='O § 2º trata da proposta orçamentária integrada (saúde, previdência e assistência) e das metas da LDO, matéria '
                  'orçamentária e periódica. A LC 70 não a disciplina. É fan-out.'),
    dict(reference_id=R('REL_294595B0B7254C57', 'CF88:ART.201:INC.I'), decision='REMOVE', confidence='ALTA',
         sources=['LEI_7998_1990', 'CF88'],
         destination_provisions='Lei 7.998/1990, art. 1º: regula o Programa do Seguro-Desemprego e o abono "de que tratam o inciso II do art. 7º, '
                                'o inciso IV do art. 201 e o art. 239" (numeração de 1990).',
         analysis='O inciso I trata de incapacidade temporária ou permanente e idade avançada (Lei 8.213/1991). A Lei 7.998 não trata desses '
                  'eventos. É fan-out temático.'),
    dict(reference_id=R('REL_294595B0B7254C57', 'CF88:ART.201:INC.II'), decision='REMOVE', confidence='ALTA',
         sources=['LEI_7998_1990'],
         destination_provisions='Lei 7.998/1990: nenhuma disposição sobre proteção à maternidade.',
         analysis='O inciso II é a proteção à maternidade (salário-maternidade, Lei 8.213/1991). Não há relação com o seguro-desemprego. É fan-out.'),
    dict(reference_id=R('REL_294595B0B7254C57', 'CF88:ART.201:INC.IV'), decision='REMOVE', confidence='ALTA',
         sources=['LEI_7998_1990', 'CF88'],
         destination_provisions='CF, texto compilado: a redação original do art. 201, IV, era "proteção ao trabalhador em situação de desemprego '
                                'involuntário". Após a EC 20/1998, esse conteúdo está no inciso III, e o IV passou a ser "salário-família '
                                'e auxílio-reclusão para os dependentes dos segurados de baixa renda".',
         analysis='A Lei 7.998 cita o "inciso IV do art. 201" pela numeração anterior à EC 20/1998. No texto vigente o inciso IV trata de '
                  'salário-família e auxílio-reclusão, sem relação com a lei. O conteúdo citado corresponde ao inciso III, que já tem o mesmo '
                  'vínculo (REL_294595B0B7254C57@CF88:ART.201:INC.III). Retargetar duplicaria o vínculo, por isso a decisão é remover.',
         note='O vínculo no inciso III fica (nota positiva da C0: renumeração).'),
    dict(reference_id=R('REL_294595B0B7254C57', 'CF88:ART.201:INC.V'), decision='REMOVE', confidence='ALTA',
         sources=['LEI_7998_1990'],
         destination_provisions='Lei 7.998/1990: nenhuma disposição sobre pensão por morte.',
         analysis='O inciso V é a pensão por morte (Lei 8.213/1991). A Lei 7.998 não a disciplina. É fan-out.'),
]

INDEPENDENT_REVIEW = dict(verdict='APPROVED_WITH_NOTES', decisions_materially_changed='NO', operational_changes=0,
                          scope='normalizacao final C1A: notas juridicas adicionais; nenhuma decisao, contagem ou simulacao alterada')
INDEPENDENT_NOTES = {
    R('REL_0628FE08FD9A170F', 'CF88:ART.20:PAR.1'): dict(
        verdict='APPROVED_WITH_NOTES', NON_EXCLUSIVE_PRIMARY_CORRELATA=True,
        notes=['NON_EXCLUSIVE_PRIMARY_CORRELATA: a Lei 7.990/1989 tem relação direta e primária com a compensação financeira do art. 20, '
               '§ 1º, mas a aprovação não a torna a única legislação correlata do dispositivo.',
               'Não exclui futuros vínculos setoriais aprovados, como a Lei 8.001/1990 e a Lei 12.734/2012, que já está vinculada.']),
    R('REL_4468A85CBDDD620A', 'CF88:ART.43:PAR.1:INC.II'): dict(
        verdict='APPROVED_WITH_NOTES', independent_confidence='ALTA', relation_assessment='IMPLEMENTACAO_MATERIAL_DIRETA',
        notes=['A avaliação jurídica sobe de MEDIA para ALTA. As LCs 124/2007 (SUDAM), 125/2007 (SUDENE) e 129/2009 (SUDECO):',
               'são leis complementares;',
               'são editadas "na forma do art. 43";',
               'instituem os organismos regionais;',
               'disciplinam sua composição e estrutura.',
               'São implementação material direta do comando do § 1º, II. A decisão REPLACE se mantém; o campo `confidence` original '
               'fica preservado como registro histórico.']),
    R('REL_70C4549A507F6E00', 'CF88:ART.182'): dict(
        verdict='APPROVED_WITH_NOTES', PRESENTATION_EQUIVALENT_RETARGET=True, ART_CAPUT_DUPLICATION=False,
        presentation_target_id='CF88:ART.182', canonical_overlay_target_if_required='CF88:ART.182',
        notes=['O RETARGET é técnico e só vale se compatível com a arquitetura. ART.182 e ART.182:CAPUT são a mesma unidade de '
               'apresentação, a única equivalência física permitida.',
               'O retarget não cria segunda unidade de apresentação e não aumenta coverage_count.',
               'Também não deve gerar dois botões nem vínculos duplicados no DEVICE.',
               'Se o overlay futuro exigir o target canônico de apresentação, a decisão vira o equivalente técnico em CF88:ART.182, sem '
               'alteração jurídica.',
               'Nada aplicado agora.']),
}
OUT_OF_SCOPE_NOTE = ('Os itens que a missão lembrou como atenção especial e que NÃO estão entre os 19 NEEDS_REVIEW da C0 não foram '
                     'revisados nem decididos aqui, por regra de escopo:\n'
                     '- art. 214, I a VI × Lei 15.388/2026 (PLAUSIBLE_NOT_VERIFIED);\n'
                     '- art. 161, II e III × LC 62/1989 (PLAUSIBLE_STRONG);\n'
                     '- art. 195, I × LC 70/1991 (PLAUSIBLE_STRONG);\n'
                     '- art. 201, III × Lei 7.998/1990 (nota positiva de renumeração);\n'
                     '- art. 153, § 4º, II × Lei 9.393/1996 e III × Lei 11.250/2005 (PLAUSIBLE);\n'
                     '- art. 155, § 2º, XII × LC 87/1996 (sem inconsistência evidente).\n'
                     'Ficam para C1B.')


def jdump(o):
    return (json.dumps(o, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def load_scope():
    q = json.loads(QUEUE.read_text(encoding='utf-8'))
    base = {b['reference_id']: b for b in json.loads(BASELINE.read_text(encoding='utf-8'))['links']}
    items = [x for x in q['CURRENT_LINK_REVIEW'] if x['plausibility'] == 'NEEDS_REVIEW']
    snap = []
    for x in items:
        b = base[x['reference_id']]
        snap.append(dict(reference_id=x['reference_id'], target_id=b['target_id'], display_target=b['display_target'], relation_id=b['relation_id'],
                         destination_norm_id=b['destination_norm_id'], destination_norm_key=b['destination_norm_key'],
                         destination_norm_name=b['destination_norm_name'], visibility=b['visibility'], relation_mode=b['relation_mode'],
                         relation_dest_articles=b['relation_dest_articles'], c0_plausibility=b['plausibility'],
                         c0_destination_text_citation=b['destination_text_citation'], c0_destination_cites=b['destination_cites'],
                         c0_review_flags=b['review_flags']))
    return q, base, snap


def build():
    q, base, snap = load_scope()
    by_ref = {r['reference_id']: r for r in REVIEW}
    if len(REVIEW) != len(by_ref):
        raise SystemExit('DUPLICATE_DECISION')
    if set(by_ref) != {s['reference_id'] for s in snap}:
        raise SystemExit(f'SCOPE_MISMATCH {sorted(set(by_ref) ^ {s["reference_id"] for s in snap})}')
    visible = [b for b in base.values() if b['visibility'] == 'CURRENT_VISIBLE']
    decisions = []
    for s in snap:
        r = by_ref[s['reference_id']]
        d = dict(reference_id=s['reference_id'], current_target=s['target_id'], display_target=s['display_target'],
                 current_norm=s['destination_norm_name'], current_norm_id=s['destination_norm_id'], current_relation_id=s['relation_id'],
                 current_route=dict(mode=s['relation_mode'], articles=s['relation_dest_articles']),
                 c0_evidence=dict(plausibility=s['c0_plausibility'], destination_text_citation=s['c0_destination_text_citation'],
                                  flags=s['c0_review_flags']),
                 decision=r['decision'], confidence=r['confidence'],
                 official_sources=[dict(source_id=k, **SOURCES[k], verified_on=VERIFIED_ON) for k in r['sources']],
                 destination_provisions=r['destination_provisions'], legal_analysis=r['analysis'],
                 retarget_to=r.get('retarget_to'), replacement_norms=r.get('replacement_norms', []),
                 route_fix=r.get('route') if r['decision'] in ('KEEP_WITH_ROUTE_FIX', 'RETARGET') else None,
                 note=r.get('note'), applied=False,
                 independent_review=INDEPENDENT_NOTES.get(s['reference_id'], dict(verdict='APPROVED', notes=[])))
        decisions.append(d)
    cnt = Counter(d['decision'] for d in decisions)
    # simulation only (never applied)
    removed = {d['reference_id'] for d in decisions if d['decision'] in ('REMOVE', 'REPLACE')}
    after = [b for b in visible if b['reference_id'] not in removed]
    retarget = {d['reference_id']: d['retarget_to'] for d in decisions if d['decision'] == 'RETARGET'}
    tgt_after = {retarget.get(b['reference_id'], b['target_id']) for b in after}
    unit = lambda t: t[:-len(':CAPUT')] if t.endswith(':CAPUT') else t  # noqa: E731
    repl = [(n['target_id'], n['norm_key']) for d in decisions if d['decision'] == 'REPLACE' for n in d['replacement_norms']]
    sim = dict(
        visible_links_now=len(visible), visible_targets_now=len({b['target_id'] for b in visible}),
        visible_links_after_without_replacements=len(after), visible_targets_after_without_replacements=len(tgt_after),
        visible_presentation_units_after_without_replacements=len({unit(t) for t in tgt_after}),
        replacement_links_if_approved_and_ingested=len(repl),
        visible_links_after_with_replacements=len(after) + len(repl),
        visible_targets_after_with_replacements=len(tgt_after | {t for t, _ in repl}),
        targets_losing_every_link_without_replacements=sorted({unit(b['target_id']) for b in visible} - {unit(t) for t in tgt_after}),
        targets_losing_every_link_even_with_replacements=sorted({unit(b['target_id']) for b in visible} - {unit(t) for t in tgt_after}
                                                                - {unit(t) for t, _ in repl}),
        note='SIMULACAO, nao aplicada. Substitutas so contam se aprovadas e com rota de aparelho (LAI e Lei 8.212 = acervo principal; '
             'LC 63 = ja no cartao; Lei 7.990 e LCs 124/125/129 = ingestao). O retarget ART.182 -> ART.182:CAPUT nao muda a contagem.')
    if any(by_ref[d['reference_id']]['decision'] != d['decision'] for d in decisions):
        raise SystemExit('INDEPENDENT_REVIEW_MUST_NOT_CHANGE_DECISIONS')
    doc = dict(schema_version=1, mission=MISSION, baseline=BASE, applied=False, verified_on=VERIFIED_ON,
               independent_review=INDEPENDENT_REVIEW,
               scope=dict(source=f'{QUEUE.relative_to(ROOT).as_posix()} :: CURRENT_LINK_REVIEW (plausibility NEEDS_REVIEW)',
                          total=len(snap), c0_current_link_review_section_total=len(q['CURRENT_LINK_REVIEW']),
                          excluded_from_scope=[x['reference_id'] for x in q['CURRENT_LINK_REVIEW'] if x['plausibility'] != 'NEEDS_REVIEW'],
                          excluded_reason='OBSOLETE_HIDDEN (2 links historicos ocultos; nao visiveis)', out_of_scope_note=OUT_OF_SCOPE_NOTE),
               source_policy='Somente fontes oficiais (Planalto ccivil_03). HTML baixado em verified_on, identificado por sha256; nao versionado.',
               decision_values=list(DECISIONS), counts={k: cnt.get(k, 0) for k in DECISIONS}, simulation=sim,
               snapshot_before_review=snap, decisions=decisions)
    return jdump(doc), report(doc).encode('utf-8')


def report(doc):
    L = []
    a = L.append
    c, s = doc['counts'], doc['simulation']
    a('# CF88_CORRELATA_C1A — revisão dos vínculos CORRELATA atuais (19 NEEDS_REVIEW)')
    a('')
    a('**Registro de decisão humana assistida. Nada foi aplicado.** Não houve overlay, exclusão, RUN4, nem alteração no SD ou no firmware.')
    a('')
    a('## Baseline e escopo')
    a('')
    a(f"- **Branch:** `{BASE['branch']}` @ `{BASE['head']}`; origem física `{BASE['physical_origin']}`; Reference Engine {BASE['reference_engine']}.")
    a(f"- **Estado confirmado nos artefatos C0:** {s['visible_links_now']} CORRELATAs visíveis em {s['visible_targets_now']} targets, de 46 no "
      'export (2 ocultas históricas).')
    a(f"- **Escopo:** {doc['scope']['total']} itens NEEDS_REVIEW da seção CURRENT_LINK_REVIEW, que tem "
      f"{doc['scope']['c0_current_link_review_section_total']} entradas.")
    a('  - As 2 restantes são as ocultas OBSOLETE_HIDDEN (art. 40, § 4º, II e III × LC 144/2014) e não estão no escopo.')
    a('- **Snapshot:** os 19 itens foram congelados em `snapshot_before_review` do JSON antes das decisões.')
    a(f"- **Fontes:** só oficiais (Planalto), verificadas em {VERIFIED_ON}. Cada fonte tem URL e sha256 do HTML baixado.")
    a('')
    a('## Contabilidade')
    a('')
    a('| Decisão | n |')
    a('|---|---:|')
    for k in DECISIONS:
        a(f'| {k} | {c[k]} |')
    a(f"| **Total** | **{sum(c.values())}** |")
    a('')
    a('**Simulação (não aplicada)**')
    a('')
    a('| Medida | Hoje | Após decisões, sem substitutas | Com substitutas aprovadas e com rota |')
    a('|---|---:|---:|---:|')
    a(f"| CORRELATAs visíveis | {s['visible_links_now']} | {s['visible_links_after_without_replacements']} | {s['visible_links_after_with_replacements']} |")
    a(f"| Targets visíveis | {s['visible_targets_now']} | {s['visible_targets_after_without_replacements']} | {s['visible_targets_after_with_replacements']} |")
    a('')
    a(f"- **Targets que ficariam sem nenhuma correlata, sem substitutas ({len(s['targets_losing_every_link_without_replacements'])}):** "
      + ', '.join(f'`{t}`' for t in s['targets_losing_every_link_without_replacements']) + '.')
    a(f"- **Mesmo com as substitutas ({len(s['targets_losing_every_link_even_with_replacements'])}):** "
      + ', '.join(f'`{t}`' for t in s['targets_losing_every_link_even_with_replacements']) + '.')
    a(f"- **Ressalva:** {s['note']}")
    a('')
    a('## Decisões, uma a uma')
    a('')
    for i, d in enumerate(doc['decisions'], 1):
        a(f"### {i}. {d['display_target']} × {d['current_norm']}: **{d['decision']}** (confiança {d['confidence']})")
        a('')
        a(f"- **reference_id:** `{d['reference_id']}`")
        a(f"- **Vínculo atual:** target `{d['current_target']}`, relação `{d['current_relation_id']}`, rota {d['current_route']['mode']} "
          f"{d['current_route']['articles'] or ''}.")
        a(f"- **Evidência C0:** {d['c0_evidence']['plausibility']} / {d['c0_evidence']['destination_text_citation']}.")
        a('- **Fonte oficial:**')
        for f in d['official_sources']:
            a(f"  - {f['norm']}: {f['url']} (verificado {f['verified_on']}, sha256 `{f['sha256'][:16]}…`)")
        a(f"- **Dispositivos relevantes:** {d['destination_provisions']}")
        a(f"- **Análise:** {d['legal_analysis']}")
        if d['retarget_to']:
            a(f"- **Target substituto:** `{d['retarget_to']}`. Rota: {d['route_fix']}.")
        for n in d['replacement_norms']:
            a(f"- **Norma substituta:** {n['norm_name']} (`{n['norm_key']}`) em `{n['target_id']}`, {n['relation_type']}. Rota: {n['route']}. "
              f"Acervo: {n['acervo_status']}.")
        if d['note']:
            a(f"- **Nota:** {d['note']}")
        a('')
    ir = doc['independent_review']
    a('## Revisão jurídica independente final')
    a('')
    a(f"- `INDEPENDENT_LEGAL_REVIEW: {ir['verdict']}`")
    a(f"- `C1A_DECISIONS_MATERIALLY_CHANGED: {ir['decisions_materially_changed']}`")
    a(f"- `OPERATIONAL_CHANGES: {ir['operational_changes']}`")
    a('')
    for d in doc['decisions']:
        notes = d['independent_review']['notes']
        if notes:
            a(f"**{d['display_target']} ({d['decision']}):**")
            a('')
            for n in notes:
                a(f'- {n}')
            for k, v in d['independent_review'].items():
                if k not in ('verdict', 'notes'):
                    a(f'- `{k} = {json.dumps(v, ensure_ascii=False)}`')
            a('')
    a('## Fora do escopo desta rodada')
    a('')
    a(doc['scope']['out_of_scope_note'])
    a('')
    a('## Próximo passo')
    a('')
    a('- **Revisão jurídica independente:** confirmar estas decisões.')
    a('  - Em especial o HOLD do art. 37, § 3º, III e as substituições de confiança média (art. 20, § 1º; art. 43, § 1º, II).')
    a('- **Só depois:** registrar as remoções em `CF88_LINK_EXCLUSIONS.json` e as substituições e o retarget no overlay futuro '
      '`CF88_CORRELATA_ADDITIONS.json`, numa missão de aplicação com RUN4 candidato.')
    a('')
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    j, m = build()
    if (j, m) != build():
        raise SystemExit('C1A_NOT_DETERMINISTIC')
    if a.check:
        ok = OUT_JSON.read_bytes().replace(b'\r\n', b'\n') == j and OUT_MD.read_bytes().replace(b'\r\n', b'\n') == m
        print('check', 'OK' if ok else 'DIFF')
        sys.exit(0 if ok else 1)
    OUT_JSON.write_bytes(j)
    OUT_MD.write_bytes(m)
    d = json.loads(j)
    print(json.dumps(dict(counts=d['counts'], simulation=d['simulation'], json_sha256=hashlib.sha256(j).hexdigest(),
                          md_sha256=hashlib.sha256(m).hexdigest()), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
