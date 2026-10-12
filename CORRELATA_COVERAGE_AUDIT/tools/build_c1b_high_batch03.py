"""CF88_CORRELATA_C1B_HIGH_REVIEW_BATCH03 — next 30 original HIGH candidates after Batch01/Batch02, structural order.

From this batch on, every candidate records a temporal status of the candidate norm (IN_FORCE, VACATIO_LEGIS, PARTIAL_EFFECTS,
TRANSITIONAL, REVOKED, UNCERTAIN), scope flags and the device route (with TEMPORAL_DEVICE_BLOCK for vacatio legis). The batch machinery
(select/build/report) is shared with Batch04. Decisions taken against the official text (Planalto, sha256 recorded, HTML not
versioned). NOTHING IS APPLIED.

Writes CF88_CORRELATA_C1B_HIGH_BATCH03_{INPUT.json, DECISIONS.json, REPORT.md}. Usage: python build_c1b_high_batch03.py [--check]
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_c1b_high_batch01 as B1  # noqa: E402
import build_c1b_high_batch02 as B2  # noqa: E402

AUDIT, ROOT = B1.AUDIT, B1.ROOT
BASE = dict(branch='cf-correlata-coverage-audit', head='825f4ad6fed7d476c4dc71405451e848e441c798')
TEMPORAL = ('IN_FORCE', 'VACATIO_LEGIS', 'PARTIAL_EFFECTS', 'TRANSITIONAL', 'REVOKED', 'UNCERTAIN')
SCOPES = ('ESCOPO_FEDERAL', 'ESCOPO_FEDERAL_EXECUTIVE', 'ESCOPO_ESTADUAL', 'ESCOPO_MUNICIPAL', 'ESCOPO_SETORIAL', 'ESCOPO_PARCIAL',
          'NON_EXCLUSIVE', 'TRANSITORIA', 'SUBSIDIARIA', 'ESCOPO_MPU', 'ESCOPO_MPDFT')
S = B1.S


def TS(status, effective_from=None, early=None, revalidate_on=None, note=None):
    assert status in TEMPORAL, status
    return dict(temporal_status=status, effective_from=effective_from, early_application_possible=early, revalidate_on=revalidate_on, note=note)


def D3(decision, confidence, relation, sources, provisions, analysis, temporal, route=None, target=None, scope=(), notes=None):
    assert all(s in SCOPES for s in scope), scope
    return dict(decision=decision, confidence=confidence, relation_type_final=relation, sources=sources, provisions=provisions, analysis=analysis,
                temporal=temporal, route=route, target_final=target, scope=list(scope), notes=notes)


def BL(norm, norm_key, target_id, basis, origin, priority, why_not_now):
    return dict(norm=norm, norm_key=norm_key, target_id=target_id, basis=basis, origin=origin, suggested_priority=priority,
                reason_not_decided=why_not_now, status='BACKLOG_NOT_DECIDED')


IN_FORCE = TS('IN_FORCE')
LC214_T = TS('PARTIAL_EFFECTS', effective_from='2025-01-16 (publicação; efeitos escalonados no art. 544)', revalidate_on='2027-01-01',
             note='LC 214/2025, art. 544: vigência na publicação, com produção de efeitos escalonada; transição do IBS/CBS até 2033')
LC227_T = TS('PARTIAL_EFFECTS', effective_from='2026-01-13 (publicação; parte dos dispositivos a partir de 2027-01-01)', revalidate_on='2027-01-01',
             note='LC 227/2026, art. 182')
ICMS_T = TS('IN_FORCE', revalidate_on='2033-01-01', note='ICMS em extinção gradual pela EC 132/2023 (ADCT, arts. 128 e 129)')

SOURCES = {
    'CF88': B1.SOURCES['CF88'],
    'LC214': B2.SOURCES['LC214'], 'LC227': B2.SOURCES['LC227'], 'LC102': B2.SOURCES['LC102'],
    'LC87': S('Lei Complementar nº 87/1996 (ICMS)', 'leis/lcp/lcp87.htm', '47bb22063ba170cd75425fb6a927780f83b8dbef6e047db857d3a113eceac772', 270282),
    'LC190': S('Lei Complementar nº 190/2022', 'leis/lcp/lcp190.htm', '6b1863792fd850cdd6601e6579c97abe344e24a2324ee81551ebaf8ac599543d', 26839),
    'LC201': S('Lei Complementar nº 201/2023', 'leis/lcp/lcp201.htm', 'ec15b7a30e9d0e396b7516c3c68f3ef472e686c39bab6b39e0490238444255c1', 111579),
    'LC24': S('Lei Complementar nº 24/1975', 'leis/lcp/lcp24.htm', '2e521bd4a17ed0be0672ee4e5e5920cf6fec40c4336c84e841cfcef2e386e268', 22058),
    'LC116': S('Lei Complementar nº 116/2003 (ISS)', 'leis/lcp/lcp116.htm', '24533ca41a83bc95eee469003cad07ef3d9675d3242f0b9be44e41c7047c29ce', 104392),
    'LC101': S('Lei Complementar nº 101/2000 (LRF)', 'leis/lcp/lcp101.htm', 'e353e6697c9e7adabfece3f8b4474be459b1c266a72c7b9a2757a0efae2fde7b', 254857),
    'L14436': S('Lei nº 14.436/2022 (LDO 2023)', '_ato2019-2022/2022/lei/l14436.htm', '4b3f4a68bafe46a417fe2df12a6bb2b17c0bd352850f71178f9f5d23b9d3c07b', 685182),
    'LC200': S('Lei Complementar nº 200/2023', 'leis/lcp/lcp200.htm', '62d132404acbf2a483bfe49af137158cf7e9cf4bafafb486f6fb776317f48d32', 98589),
    'LC210': S('Lei Complementar nº 210/2024', 'leis/lcp/lcp210.htm', 'cda0c0c0035f17d6794a82140a62624eea149cb842eb8e0e4c123c797cf52ee8', 50633),
    'L9801': S('Lei nº 9.801/1999', 'leis/l9801.htm', 'de298f9c6dcd6cfad83057dc196e5de5c28e82b26291abfba93572a8f2735e44', 8281),
    'L13874': S('Lei nº 13.874/2019', '_ato2019-2022/2019/lei/l13874.htm', '99cc67a286076f183732bbbaa20be07b6f93e09e20bf33f6da0e4d11b218431f', 160728),
    'LC76': S('Lei Complementar nº 76/1993', 'leis/lcp/lcp76.htm', 'f6b25ddbad94769f54faf78b890424e97c0d37e8e02996fb7a9bdfdf92944227', 27123),
    'LC93': S('Lei Complementar nº 93/1998', 'leis/lcp/lcp93.htm', '591e381ac041cab6d56e2bee9e8bf240e6caa30fcc21d23571e5307c86b98904', 23481),
    'L8212': S('Lei nº 8.212/1991 (compilada)', 'leis/l8212cons.htm', '12c5bda5cffd920da7093757ceb796651f937e0306d341c19348a3d040a09e1d', 771751),
    'LC187': S('Lei Complementar nº 187/2021', 'leis/lcp/lcp187.htm', 'cf47392daa3ed10c87a83961be9cf4ca77104852e4d40aa5ae80a024470effe0', 300608),
}

REVIEW = {
    'CORRC0-ED340FAA29A6': D3('REJECT', 'MEDIA', None, ['LC214', 'CF88'],
                              'Ementa da LC 214: institui o IBS, a CBS e o Imposto Seletivo. A redução e a extinção do ICMS estão no próprio '
                              'ADCT (arts. 128 e 129), não em regras da LC 214 sobre o § 2º do art. 155.',
                              'O § 2º fixa o regime constitucional do ICMS (não cumulatividade, seletividade, alíquotas, DIFAL, lei complementar). '
                              'A LC 214 não disciplina esses atributos. A ligação com o ICMS é de transição e substituição, e a ENTENDA cita os '
                              'arts. 128 e 129 do ADCT. A relação é temática.', LC214_T),
    'CORRC0-FB5381D4D3A5': D3('REJECT', 'ALTA', None, ['LC190', 'LC87'],
                              'Ementa: "Altera a Lei Complementar nº 87 ... para regulamentar a cobrança do ICMS nas operações e prestações '
                              'interestaduais destinadas a consumidor final não contribuinte". Os dispositivos estão incorporados à LC 87 '
                              '(ex.: art. 4º, § 2º; art. 11, § 7º; art. 12, XVI). O art. 3º trata da produção de efeitos.',
                              'É lei alteradora: a disciplina vigente do DIFAL está no texto compilado da LC 87, avaliada neste lote. O conteúdo '
                              'autônomo que sobra é só a regra de produção de efeitos (art. 3º), já exaurida.', IN_FORCE, scope=(),
                              notes='ALTERADORA_INCORPORADA.'),
    'CORRC0-BD6BE3620174': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['LC87', 'LC190'],
                              'LC 87/1996, na redação da LC 190/2022: fato gerador da saída a consumidor final não contribuinte de outro Estado '
                              '(art. 12, XVI) e cálculo e sujeição da diferença de alíquotas (art. 4º, § 2º; art. 11, § 7º).',
                              'O inciso VII atribui ao Estado de destino a diferença entre alíquotas. A LC 87 é a lei complementar de normas '
                              'gerais que viabiliza essa cobrança. A natureza muda de COMPLEMENTA para REGULAMENTA.', ICMS_T,
                              route='art. 4º, § 2º (e art. 11, § 7º)'),
    'CORRC0-EFBBD4456F98': D3('REJECT', 'ALTA', None, ['LC102'],
                              'Ementa: "Altera dispositivos da Lei Complementar nº 87".',
                              'Lei alteradora sem disciplina autônoma vigente: as alterações estão incorporadas à LC 87, a lei-base do inciso XII.',
                              IN_FORCE, notes='ALTERADORA_INCORPORADA.'),
    'CORRC0-0EF4365F1CB4': D3('REJECT', 'ALTA', None, ['LC201'],
                              'Ementa: "Dispõe sobre a compensação devida pela União nos termos dos arts. 3º e 14 da Lei Complementar nº 194, de 2022, '
                              'a dedução das parcelas dos contratos de dívida...".',
                              'O inciso XII lista matérias reservadas à lei complementar do ICMS. A LC 201 trata da compensação financeira '
                              'federativa por perdas de arrecadação, não dessas matérias. A relação é temática.', IN_FORCE),
    'CORRC0-546E42DB4BCA': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['LC24', 'CF88'],
                              'LC 24/1975: "Dispõe sobre os convênios para a concessão de isenções do ICM". O art. 1º diz que isenções são '
                              'concedidas ou revogadas por convênios; o art. 2º trata do quórum e da forma de celebração.',
                              'A LC 24 (recepcionada) é a lei complementar da alínea g: forma como, mediante deliberação dos Estados e do DF, isenções, '
                              'incentivos e benefícios são concedidos e revogados. O target vai para a alínea g, não para o inciso XII inteiro.',
                              ICMS_T, route='arts. 1º e 2º', target='CF88:ART.155:PAR.2:INC.XII:AL.g'),
    'CORRC0-A5A1F929253C': D3('REJECT', 'ALTA', None, ['LC214', 'LC116'],
                              'LC 116/2003: "Dispõe sobre o Imposto Sobre Serviços de Qualquer Natureza". A LC 214 institui IBS, CBS e IS.',
                              'O § 3º reserva à lei complementar alíquotas, exclusões e benefícios do ISS, matéria da LC 116/2003. A LC 214 não '
                              'disciplina o ISS. A extinção do ISS está no ADCT. A relação é temática.', LC214_T,
                              notes='NEW_CANDIDATE_BACKLOG: LC 116/2003 × art. 156, § 3º.'),
    'CORRC0-D2CF3E042053': D3('APPROVE', 'ALTA', 'REGULAMENTA', ['LC214'],
                              'LC 214/2025, Livro I: normas do IBS e da CBS (incidência ampla, não cumulatividade, alíquotas de referência, '
                              'arts. 14 a 19; regime regular e créditos).',
                              'O § 1º fixa os princípios e características do IBS (neutralidade, incidência ampla, não cumulatividade, '
                              'alíquota única por ente). A LC 214 concretiza esse regime.', LC214_T, route='art. 1º (Livro I)',
                              scope=('NON_EXCLUSIVE',)),
    'CORRC0-E3C2F652AB8A': D3('APPROVE', 'ALTA', 'REGULAMENTA', ['LC214', 'LC227'],
                              'LC 214/2025: regime de compensação e créditos; ressarcimento; destino da operação; bens de capital; regimes '
                              'aduaneiros e ZPE; devolução personalizada (Título III, arts. 112 e ss.); obrigações acessórias.',
                              'O § 5º lista nove matérias de lei complementar. A LC 214 cobre os incisos II a VI, VIII e IX. Os incisos I '
                              '(distribuição da arrecadação) e VII (processo administrativo) estão na LC 227/2026.', LC214_T,
                              route='Livro I (art. 112 e ss. para o inciso VIII)', scope=('ESCOPO_PARCIAL', 'NON_EXCLUSIVE')),
    'CORRC0-945D4CF3CD87': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['LC227'],
                              'LC 227/2026, ementa: "dispõe sobre o processo administrativo tributário do IBS e sobre a distribuição do produto da '
                              'arrecadação". Título II, "Do Processo Administrativo Tributário do IBS" (art. 54 e ss.).',
                              'O vínculo materialmente sustentado é com o inciso VII do § 5º (processo administrativo fiscal do imposto). A '
                              'distribuição da arrecadação (inciso I) é vínculo distinto e vai para o backlog. Nada de fan-out para o § 5º inteiro.',
                              LC227_T, route='art. 54', target='CF88:ART.156-A:PAR.5:INC.VII',
                              notes='NEW_CANDIDATE_BACKLOG: LC 227/2026 × art. 156-A, § 5º, I.'),
    'CORRC0-6236AB9C2784': D3('APPROVE', 'ALTA', 'REGULAMENTA', ['LC214'],
                              'LC 214/2025, Título V, "Dos Regimes Específicos do IBS e da CBS": combustíveis (art. 172, incidência única), '
                              'serviços financeiros, imóveis, planos de saúde, cooperativas, hotelaria e turismo, transporte coletivo.',
                              'O § 6º manda a lei complementar dispor sobre regimes específicos para os setores que lista, e o Título V da LC 214 '
                              'é essa disciplina.', LC214_T, route='art. 172 (Título V)'),
    'CORRC0-AE4FC77A0E24': D3('APPROVE', 'ALTA', 'REGULAMENTA', ['LC214'],
                              'LC 214/2025, art. 19: "Qualquer alteração na legislação federal que reduza ou eleve a arrecadação do IBS ou da CBS: '
                              'I - deverá ser compensada pela elevação ou redução, pelo Senado Federal, ... das alíquotas de referência...; II - '
                              'somente entrará em vigor com o início da produção de efeitos do ajuste...". O art. 18 trata das alíquotas de referência.',
                              'O art. 19 reproduz e disciplina o mecanismo do § 9º. A relação é direta.', LC214_T, route='art. 19'),
    'CORRC0-E80CB2DF38CE': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['LC214'],
                              'LC 214/2025, Título III, "Da Devolução Personalizada do IBS e da CBS (Cashback)", arts. 112 e ss. O art. 118 '
                              'fixa os percentuais de devolução, inclusive em energia elétrica e botijão de GLP.',
                              'O § 13 torna obrigatória a devolução na energia elétrica e no GLP para a baixa renda e permite à lei complementar '
                              'definir o cálculo no momento da cobrança. A LC 214 disciplina isso. A natureza muda de COMPLEMENTA para REGULAMENTA.',
                              LC214_T, route='art. 118'),
    'CORRC0-1A40567592C0': D3('REJECT', 'MEDIA', None, ['LC214', 'CF88'],
                              'LC 214/2025, art. 409: institui o Imposto Seletivo. Os percentuais de repartição do art. 159, I, estão no próprio '
                              'texto constitucional.',
                              'O inciso I do art. 159 é regra constitucional de repartição. A LC 214 só institui um dos impostos repartidos, sem '
                              'disciplinar a repartição. O vínculo útil da LC 214 com o IS fica no art. 153, VIII e § 6º.', LC214_T),
    'CORRC0-EFB85C7CCADA': D3('ADJUST', 'MEDIA', 'COMPLEMENTA', ['LC101', 'CF88'],
                              'LRF, art. 1º: normas de finanças públicas voltadas para a responsabilidade na gestão fiscal, "com amparo no '
                              'Capítulo II do Título VI". Disciplina gestão fiscal, limites e transparência.',
                              'O § 9º reserva à lei complementar (I) exercício financeiro e organização das leis orçamentárias, (II) normas de '
                              'gestão financeira e patrimonial e (III) execução equitativa. A LRF cobre parte do inciso II e não esgota o '
                              'parágrafo (Lei 4.320/1964 e LC 210/2024 também atuam). A natureza muda de REGULAMENTA para COMPLEMENTA, com '
                              'escopo parcial.', IN_FORCE, route='art. 1º', scope=('ESCOPO_PARCIAL', 'NON_EXCLUSIVE')),
    'CORRC0-3EAE25BCF28E': D3('REJECT', 'ALTA', None, ['L14436'],
                              'Ementa: "Dispõe sobre as diretrizes para a elaboração e a execução da Lei Orçamentária de 2023".',
                              'Lei de diretrizes de um exercício encerrado, com eficácia exaurida. A nota oficial da ENTENDA se referia ao § 11 '
                              '(fonte desalinhada), e o dever de executar do § 10 é permanente. Lei periódica não é correlata útil.',
                              TS('TRANSITIONAL', note='lei periódica do exercício de 2023; eficácia exaurida')),
    'CORRC0-68DD94F14824': D3('APPROVE', 'ALTA', 'COMPLEMENTA', ['LC200'],
                              'Ementa: "Institui regime fiscal sustentável ... com fundamento no art. 6º da Emenda Constitucional nº 126". O art. '
                              '3º fixa os limites individualizados de despesas primárias.',
                              'O § 18 exclui despesas com precatórios e RPV do "limite individualizado ... estabelecido na lei complementar de que '
                              'trata o art. 6º da EC 126", que é a LC 200/2023. A relação é de complementação recíproca.', IN_FORCE, route='art. 3º'),
    'CORRC0-56E3853E56E6': D3('ADJUST', 'MEDIA', 'COMPLEMENTA', ['LC210'],
                              'LC 210/2024, ementa: proposição e execução de emendas parlamentares na LOA. Capítulo IV, "Das Emendas Individuais" '
                              '(arts. 6º e 7º).',
                              'O § 9º fixa o limite constitucional das emendas individuais (2% da RCL, metade para a saúde). A LC 210 '
                              'disciplina proposição e execução, sem criar o limite. A natureza muda de REGULAMENTA para COMPLEMENTA.', IN_FORCE,
                              route='art. 6º'),
    'CORRC0-FEF94155C26B': D3('APPROVE', 'ALTA', 'REGULAMENTA', ['LC210'],
                              'LC 210/2024, Capítulo V, art. 10: "São consideradas hipóteses de impedimentos de ordem técnica para execução de '
                              'emendas parlamentares, exclusivamente...".',
                              'O § 11 torna obrigatória a execução das emendas individuais "conforme os critérios para a execução equitativa da '
                              'programação definidos na lei complementar". A LC 210 disciplina execução e impedimentos.', IN_FORCE, route='art. 10',
                              scope=('NON_EXCLUSIVE',)),
    'CORRC0-40EDEC92644D': D3('REJECT', 'ALTA', None, ['L14436'],
                              'Lei 14.436/2022: diretrizes da LOA de 2023.',
                              'Lei periódica de exercício encerrado. Não é a lei complementar permanente que o § 11 exige.',
                              TS('TRANSITIONAL', note='lei periódica do exercício de 2023; eficácia exaurida')),
    'CORRC0-FE5F5C013375': D3('APPROVE', 'ALTA', 'REGULAMENTA', ['LC101'],
                              'LRF, art. 23: o percentual de despesa com pessoal que exceder o limite "terá de ser eliminado nos dois '
                              'quadrimestres seguintes ..., adotando-se, entre outras, as providências previstas nos §§ 3º e 4º do art. 169".',
                              'O § 3º manda adotar as providências "durante o prazo fixado na lei complementar referida no caput", e a LRF fixa '
                              'esse prazo e remete expressamente ao § 3º.', IN_FORCE, route='art. 23'),
    'CORRC0-8A985C226863': D3('ADJUST', 'ALTA', 'COMPLEMENTA', ['LC101', 'L9801'],
                              'LRF, art. 23 (prazo e remissão aos §§ 3º e 4º). Lei 9.801/1999, art. 1º: "regula a exoneração de servidor público '
                              'estável com fundamento no § 4º e seguintes do art. 169".',
                              'O § 4º prevê a perda do cargo do estável quando as medidas do § 3º não bastam "para assegurar o cumprimento da '
                              'determinação da lei complementar referida neste artigo". A LRF dá o parâmetro (limites e prazo), mas as normas '
                              'gerais da exoneração estão na Lei 9.801 (§ 7º). A natureza muda de REGULAMENTA para COMPLEMENTA.', IN_FORCE,
                              route='art. 23', scope=('NON_EXCLUSIVE',), notes='NEW_CANDIDATE_BACKLOG: Lei 9.801/1999 × art. 169, §§ 4º e 7º.'),
    'CORRC0-0F1CB8ABDC7C': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['L13874'],
                              'Lei 13.874/2019, art. 3º: direitos de toda pessoa essenciais ao desenvolvimento econômico, "observado o disposto no '
                              'parágrafo único do art. 170", inciso I: atividade de baixo risco sem atos públicos de liberação.',
                              'O parágrafo único assegura o livre exercício de atividade econômica sem autorização, "salvo nos casos previstos em '
                              'lei". A Declaração de Direitos de Liberdade Econômica disciplina exatamente o regime de liberação. A natureza muda '
                              'para REGULAMENTA.', IN_FORCE, route='art. 3º', scope=('NON_EXCLUSIVE',)),
    'CORRC0-31BBEFA99046': D3('ADJUST', 'ALTA', 'PROCEDIMENTO', ['LC76'],
                              'Ementa: "Dispõe sobre o procedimento contraditório especial, de rito sumário, para o processo de desapropriação de '
                              'imóvel rural, por interesse social, para fins de reforma agrária".',
                              'A ementa reproduz o § 3º. A natureza correta é PROCEDIMENTO, não REGULAMENTA genérico.', IN_FORCE, route='art. 1º'),
    'CORRC0-6BFA71365AA0': D3('REJECT', 'ALTA', None, ['LC93'],
                              'Ementa: "Institui o Fundo de Terras e da Reforma Agrária - Banco da Terra".',
                              'O § 3º trata do rito processual da desapropriação. A LC 93 cria um fundo de financiamento fundiário. A relação é '
                              'temática, vinda da página legada da Câmara.', IN_FORCE),
    'CORRC0-E2384C29633B': D3('REJECT', 'ALTA', None, ['L8212'],
                              'Lei 8.212/1991, art. 10: "A Seguridade Social será financiada por toda sociedade, ... nos termos do art. 195". Não '
                              'há regra sobre a inclusão das receitas estaduais e municipais da seguridade nos respectivos orçamentos.',
                              'O § 1º é regra orçamentária federativa. A citação do art. 10 é genérica ao art. 195. A remoção da LC 70 deste '
                              'target (C1A) não deve ser compensada com vínculo temático.', IN_FORCE),
    'CORRC0-410A3EF072CA': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['L8212'],
                              'Lei 8.212/1991, Capítulo XI, "Da Prova de Inexistência de Débito", art. 47: exige CND da empresa "na contratação com o '
                              'Poder Público e no recebimento de benefícios ou incentivo fiscal ou creditício".',
                              'O § 3º veda contratar com o poder público ou receber benefícios à pessoa jurídica em débito "como estabelecido em '
                              'lei". O art. 47 é essa disciplina. A natureza muda de COMPLEMENTA para REGULAMENTA.', IN_FORCE, route='art. 47'),
    'CORRC0-123B2C35009A': D3('REJECT', 'MEDIA', None, ['L8212', 'CF88'],
                              'Lei 8.212/1991: lei ordinária de custeio. A referência legada ao "cap. XI" aponta para a CND (art. 47), não para '
                              'novas fontes.',
                              'O § 4º autoriza outras fontes de custeio obedecido o art. 154, I (lei complementar, competência residual). A Lei '
                              '8.212 não institui fontes residuais. A indicação legada estava desalinhada.', IN_FORCE),
    'CORRC0-47F967871B91': D3('ADJUST', 'ALTA', 'REGULAMENTA', ['LC187'],
                              'Ementa: "Dispõe sobre a certificação das entidades beneficentes e regula os procedimentos referentes à imunidade de '
                              'contribuições à seguridade social de que trata o § 7º do art. 195".',
                              'Remissão expressa: é a lei complementar das exigências do § 7º. A nota "Vide" da compilação não basta; a ementa '
                              'oficial basta. A natureza muda de COMPLEMENTA para REGULAMENTA.', IN_FORCE, route='art. 1º'),
    'CORRC0-80D1B099C1D9': D3('REJECT', 'ALTA', None, ['L8212', 'LC187'],
                              'Lei 8.212/1991, art. 55 (isenção das entidades beneficentes): "(Revogado pela Lei nº 12.101, de 2009)". O regime '
                              'vigente é o da LC 187/2021.',
                              'A disciplina da Lei 8.212 para o § 7º foi revogada, e a correlata vigente é a LC 187/2021, aprovada neste lote. O '
                              'vínculo é histórico.', IN_FORCE, notes='DISPOSITIVO_REVOGADO.'),
}

NEW_CANDIDATE_BACKLOG = [
    BL('Lei Complementar nº 116/2003 (ISS)', 'LC:116/2003', 'CF88:ART.156:PAR.3', 'ementa oficial: dispõe sobre o ISS; o § 3º reserva à LC alíquotas, '
       'exclusões e benefícios do ISS', 'CORRC0-A5A1F929253C', 'MEDIUM', 'norma não estava na fila HIGH original; exige rodada própria'),
    BL('Lei Complementar nº 227/2026', 'LC:227/2026', 'CF88:ART.156-A:PAR.5:INC.I', 'ementa oficial: dispõe sobre a distribuição do produto da '
       'arrecadação do IBS', 'CORRC0-945D4CF3CD87', 'HIGH', 'vínculo distinto do inciso VII; sem fan-out no mesmo candidate_id'),
    BL('Lei nº 9.801/1999', 'LEI:9801/1999', 'CF88:ART.169:PAR.4', 'art. 1º: regula a exoneração do estável "com fundamento no § 4º e seguintes do '
       'art. 169"', 'CORRC0-8A985C226863', 'HIGH', 'norma não estava na fila HIGH original'),
    BL('Lei nº 9.801/1999', 'LEI:9801/1999', 'CF88:ART.169:PAR.7', '§ 7º: "Lei federal disporá sobre as normas gerais" do § 4º; a Lei 9.801 é essa lei',
       'CORRC0-8A985C226863', 'HIGH', 'norma não estava na fila HIGH original'),
]


# ------------------------------------------------------------------ shared batch machinery (also used by Batch04)
def decided_ids():
    ids = set(json.loads(B1.OUT_IN.read_text(encoding='utf-8'))['selection']['candidate_ids'])
    ids |= set(json.loads(B2.OUT_IN.read_text(encoding='utf-8'))['selection']['candidate_ids'])
    return ids


def remaining_pool(extra_decided=()):
    q, pool, _, excluded, cands = B2.select()
    done = decided_ids() | set(extra_decided)
    return q, [x for x in pool if x['candidate_id'] not in done], cands


def build_batch(name, mission, ids, review, sources, backlog, base, selection_note, q, pool_size, remaining_after):
    cands = {c['candidate_id']: c for c in json.loads(B1.CANDS.read_text(encoding='utf-8'))['candidates']}
    if set(ids) != set(review) or len(ids) != len(set(ids)):
        raise SystemExit(f'{name}_DECISION_MISMATCH {sorted(set(ids) ^ set(review))}')
    inp, dec = [], []
    for cid in ids:
        c = cands[cid]
        inp.append(dict(candidate_id=cid, target_id=c['canonical_target_id'], display_target=c['display_target'], norm_key=c['norm_key'],
                        norm_name=c['norm_name'], namespace=c['namespace'], c0_relation_type=c['relation_type'], c0_confidence=c['confidence'],
                        c0_priority=c['review_priority'], c0_signal_families=c['signal_families'], c0_device_status=c['device_status'],
                        c0_flags=c['flags'], c0_engine_overlay_eligible_now=c['engine_overlay_eligible_now'],
                        c0_signals=[dict(family=s['family'], source=s['source'], evidence=s['evidence']) for s in c['signals'][:6]]))
    for i in inp:
        r = review[i['candidate_id']]
        ok = r['decision'] in ('APPROVE', 'ADJUST')
        t = r['temporal']
        dev = i['c0_device_status'] if ok else None
        dev_flags = ([dev] + (['TEMPORAL_DEVICE_BLOCK'] if t['temporal_status'] == 'VACATIO_LEGIS' else [])) if ok else []
        dec.append(dict(candidate_id=i['candidate_id'], target=i['target_id'], display_target=i['display_target'], namespace=i['namespace'],
                        norm_key=i['norm_key'], norm_name=i['norm_name'], c0_signals=i['c0_signal_families'], c0_relation_type=i['c0_relation_type'],
                        legal_decision=r['decision'], confidence=r['confidence'], relation_type_final=r['relation_type_final'],
                        target_final=(r['target_final'] or i['target_id']) if ok else None, route=r['route'],
                        scope=r['scope'], temporal=t, device_route_status=dev, device_flags=dev_flags,
                        ingestion_status=('INGESTION_REQUIRED' if dev == 'INGESTION_REQUIRED' else 'NOT_REQUIRED') if ok else None,
                        engine_overlay_eligible_now=i['c0_engine_overlay_eligible_now'] if ok else None,
                        official_sources=[dict(source_id=k, **sources[k]) for k in r['sources']], relevant_provisions=r['provisions'],
                        legal_analysis=r['analysis'], notes=r['notes'], applied=False))
    cnt = Counter(d['legal_decision'] for d in dec)
    acc = [d for d in dec if d['legal_decision'] in ('APPROVE', 'ADJUST')]
    summary = dict(batch_candidates=len(dec), high_total=len(q['HIGH']), eligible_pool_before=pool_size,
                   high_remaining_after=len(remaining_after), decisions={k: cnt.get(k, 0) for k in B1.DECISIONS},
                   accepted=len(acc),
                   accepted_device_route={k: sum(1 for d in acc if d['device_route_status'] == k)
                                          for k in ('MAIN_CORPUS_ROUTE_REQUIRED', 'INGESTION_REQUIRED', 'DEVICE_RESOLVABLE_NOW')},
                   accepted_temporal=dict(sorted(Counter(d['temporal']['temporal_status'] for d in acc).items())),
                   temporal_device_block=sum(1 for d in acc if 'TEMPORAL_DEVICE_BLOCK' in d['device_flags']),
                   engine_overlay_blocked=sum(1 for d in acc if not d['engine_overlay_eligible_now']),
                   relation_type_changed=sum(1 for d in acc if d['relation_type_final'] != d['c0_relation_type']),
                   target_changed=sum(1 for d in acc if d['target_final'] != d['target']),
                   cf_vs_adct={ns: dict(sorted(Counter(d['legal_decision'] for d in dec if d['namespace'] == ns).items())) for ns in ('CF88', 'ADCT')},
                   new_candidate_backlog=len(backlog))
    common = dict(schema_version=1, mission=mission, baseline=base, applied=False, verified_on=B1.VERIFIED_ON)
    j_in = B1.jdump(dict(common, artifact=f'CF88_CORRELATA_C1B_HIGH_{name}_INPUT',
                         selection=dict(source='CORRELATA_COVERAGE_AUDIT/CF88_CORRELATA_REVIEW_QUEUE.json :: HIGH (fila original)', rule=selection_note,
                                        eligible_pool_before=pool_size, taken=len(ids), candidate_ids=ids,
                                        remaining_after=[x['candidate_id'] for x in remaining_after]),
                         candidates=inp))
    j_dec = B1.jdump(dict(common, artifact=f'CF88_CORRELATA_C1B_HIGH_{name}_DECISIONS', decision_values=list(B1.DECISIONS),
                          relation_types=list(B1.RELATION_TYPES), temporal_values=list(TEMPORAL), scope_values=list(SCOPES),
                          source_policy='Somente Planalto (fonte oficial); HTML identificado por sha256, nao versionado.',
                          summary=summary, decisions=dec, NEW_CANDIDATE_BACKLOG=backlog))
    return j_in, j_dec, report(name, summary, dec, backlog).encode('utf-8')


def report(name, s, dec, backlog):
    L = []
    a = L.append
    a(f'# CF88_CORRELATA_C1B — HIGH {name.title()}')
    a('')
    a('**Revisão jurídica assistida. Nada foi aplicado.** Não houve ADDITIONS, exclusões, RUN4, nem alteração no SD ou no firmware.')
    a('')
    a('## Lote')
    a('')
    a(f"- **Seleção:** fila HIGH original da C0 ({s['high_total']}) menos os já decididos; {s['eligible_pool_before']} elegíveis antes do lote, "
      'em ordem estrutural do Target Index.')
    a(f"- **Tamanho:** entraram {s['batch_candidates']}. HIGH originais restantes depois: **{s['high_remaining_after']}**.")
    a(f"- **Fontes:** só oficiais (Planalto), verificadas em {B1.VERIFIED_ON}, com sha256 de cada página.")
    a('- **Campos obrigatórios:** cada candidato tem `temporal_status`. Decisão jurídica e rota de aparelho ficam separadas.')
    a('')
    a('## Contabilidade')
    a('')
    a('| Decisão | n |')
    a('|---|---:|')
    for k in B1.DECISIONS:
        a(f"| {k} | {s['decisions'][k]} |")
    a(f"| **Total** | **{s['batch_candidates']}** |")
    a('')
    a('| Aceitos (APPROVE + ADJUST): rota de aparelho | n |')
    a('|---|---:|')
    for k, v in s['accepted_device_route'].items():
        a(f'| {k} | {v} |')
    a(f"| TEMPORAL_DEVICE_BLOCK | {s['temporal_device_block']} |")
    a('')
    a(f"- **Situação temporal dos aceitos:** {s['accepted_temporal']}.")
    a(f"- **Overlay:** aceitos em target com status do motor fora de CURRENT/STRUCTURAL (ADCT): {s['engine_overlay_blocked']}.")
    a(f"- **Ajustes:** natureza reclassificada em {s['relation_type_changed']}; target ajustado em {s['target_changed']}.")
    a(f"- **CF × ADCT:** {s['cf_vs_adct']}.")
    a('')
    a('## Decisões')
    a('')
    a('| # | Target | Norma | Decisão | Natureza | Target final | Temporal | Escopo | Aparelho |')
    a('|---:|---|---|---|---|---|---|---|---|')
    for i, d in enumerate(dec, 1):
        tf = '=' if d['target_final'] == d['target'] else (d['target_final'] or '—')
        a(f"| {i} | {d['display_target']} | {d['norm_name']} | **{d['legal_decision']}** | {d['relation_type_final'] or '—'} | {tf} | "
          f"{d['temporal']['temporal_status']} | {', '.join(d['scope']) or '—'} | {', '.join(d['device_flags']) or '—'} |")
    a('')
    for i, d in enumerate(dec, 1):
        t = d['temporal']
        a(f"### {i}. {d['display_target']} × {d['norm_name']}: **{d['legal_decision']}** ({d['confidence']})")
        a('')
        a(f"- **candidate_id:** `{d['candidate_id']}`")
        a(f"- **Target:** `{d['target']}`; target final `{d['target_final']}`; rota {d['route'] or '—'}.")
        a(f"- **Sinais C0:** {', '.join(d['c0_signals'])}; natureza C0 {d['c0_relation_type']}.")
        a(f"- **Temporal:** {t['temporal_status']}" + (f"; vigência {t['effective_from']}" if t['effective_from'] else '')
          + (f"; revalidar em {t['revalidate_on']}" if t['revalidate_on'] else '') + (f". {t['note']}" if t['note'] else '') + '.')
        a('- **Fonte oficial:**')
        for f in d['official_sources']:
            a(f"  - {f['norm']}: {f['url']} ({f['verified_on']}, sha256 `{f['sha256'][:16]}…`)")
        a(f"- **Dispositivos relevantes:** {d['relevant_provisions']}")
        a(f"- **Análise:** {d['legal_analysis']}")
        if d['notes']:
            a(f"- **Observações:** {d['notes']}")
        a('')
    a('## NEW_CANDIDATE_BACKLOG (não decidido; fora da contagem dos 106 HIGH originais)')
    a('')
    for b in backlog:
        a(f"- {b['norm']} × `{b['target_id']}`, prioridade sugerida {b['suggested_priority']}, origem `{b['origin']}`.")
        a(f"  - Fundamento: {b['basis']}.")
        a(f"  - Por que não decidir agora: {b['reason_not_decided']}.")
    a('')
    return '\n'.join(L) + '\n'


OUT_IN = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH03_INPUT.json'
OUT_DEC = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH03_DECISIONS.json'
OUT_MD = AUDIT / 'CF88_CORRELATA_C1B_HIGH_BATCH03_REPORT.md'
LIMIT = 30


def build():
    q, pool, _ = remaining_pool()
    batch = pool[:LIMIT]
    return build_batch('BATCH03', 'CF88_CORRELATA_C1B_HIGH_REVIEW_BATCH03', [x['candidate_id'] for x in batch], REVIEW, SOURCES, NEW_CANDIDATE_BACKLOG,
                       BASE, 'HIGH original - Batch01 - Batch02 - C1A - duplicatas; ordem estrutural; proximos 30', q, len(pool), pool[LIMIT:])


def main(build_fn=None, paths=None):
    build_fn = build_fn or build
    paths = paths or (OUT_IN, OUT_DEC, OUT_MD)
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    out = build_fn()
    if out != build_fn():
        raise SystemExit('NOT_DETERMINISTIC')
    if a.check:
        ok = all(p.read_bytes().replace(b'\r\n', b'\n') == b for p, b in zip(paths, out))
        print('check', 'OK' if ok else 'DIFF')
        sys.exit(0 if ok else 1)
    for p, b in zip(paths, out):
        p.write_bytes(b)
    print(json.dumps(json.loads(out[1])['summary'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
